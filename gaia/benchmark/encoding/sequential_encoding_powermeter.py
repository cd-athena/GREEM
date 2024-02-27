import os

from pathlib import Path
from datetime import datetime

import pandas as pd
from codecarbon import track_emissions
from dacite import MissingValueError

from gaia.utils.ffmpeg import create_sequential_encoding_cmd
from gaia.utils.configuration_classes import EncodingConfig, EncodingConfigDTO

from gaia.utils.timing import IdleTimeEnergyMeasurement
from gaia.utils.dataframe import get_dataframe_from_csv

from gaia.hardware.intel import intel_rapl_workaround
from gaia.monitoring.nvidia_top import NvidiaTop

from gaia.utils.cli_parser import CLI_PARSER

NTFY_TOPIC: str = "aws_encoding"

MEASUREMENT_INTERVAL: float = 0.25


ENCODING_CONFIG_PATHS: list[str] = [
    # "config_files/segment_encoding_h264.yaml",
    # "config_files/segment_encoding_h265.yaml",
    'config_files/test_encoding_config.yaml'
]

INPUT_FILE_DIR: str = "../dataset/ref_265"
RESULT_ROOT: str = "results"
COUNTRY_ISO_CODE: str = "AUT"

USE_SLICED_VIDEOS: bool = CLI_PARSER.is_sliced_encoding()
# if True, no encoding will be executed
DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = CLI_PARSER.is_cuda_enabled()
INCLUDE_CODE_CARBON: bool = CLI_PARSER.is_code_carbon_enabled()


def prepare_data_directories(
    encoding_config: EncodingConfig,
    result_root: str = RESULT_ROOT,
) -> list[str]:
    """Used to generate all directories that are used for the video encoding

    Args:
        encoding_config (EncodingConfig): config class that contains the values that are required to generate the directories.
        result_root (str, optional): _description_. Defaults to RESULT_ROOT.
        video_names (list[str], optional): _description_. Defaults to list().

    Returns:
        list[str]: returns a list of all directories that were created
    """
    # data_directories = encoding_config.get_all_result_directories(video_names)

    data_directories = [
        dto.get_output_directory()
        for dto in encoding_config.get_encoding_dtos()
    ]

    for directory in data_directories:
        directory_path: str = f"{result_root}/{directory}"
        Path(directory_path).mkdir(parents=True, exist_ok=True)

    return data_directories


def get_video_input_files(video_dir: str, encoding_config: EncodingConfig) -> list[str]:
    def is_file_in_config(file_name: str) -> bool:
        if encoding_config.encode_all_videos:
            return True

        file = file_name.split(".")[0]
        if USE_SLICED_VIDEOS:
            file = file.split("_")[0]
        return (
            encoding_config.videos_to_encode is not None
            and file in encoding_config.videos_to_encode
        )

    input_files: list[str] = [
        file_name for file_name in os.listdir(video_dir) if is_file_in_config(file_name)
    ]

    if len(input_files) == 0:
        raise ValueError("no video files to encode")

    return input_files


def get_filtered_sliced_videos(
    encoding_config: EncodingConfig, input_dir: str
) -> list[str]:
    input_files: list[str] = get_video_input_files(input_dir, encoding_config)

    return sorted(input_files)


def execute_encoding_benchmark(encoding_configs: list[EncodingConfig]):

    input_dir = INPUT_FILE_DIR
    time_dir = {
        'start': datetime.now().__str__()
    }
    start_time = datetime.now()
    for encoding_config in encoding_configs:
        input_files = sorted(
            [file for file in os.listdir(
                INPUT_FILE_DIR) if file.endswith(".265")][:3]
        )

        # encode for each duration defined in the config file
        prepare_data_directories(encoding_config)

        encoding_dtos: list[EncodingConfigDTO] = encoding_config.get_encoding_dtos(
        )

        max_rep = 6
        video_count = 0

        for rep in range(1, max_rep):
            # encode each video found in the input files corresponding to the duration
            for idx, video_name in enumerate(input_files):
                for dto in encoding_dtos:
                    video_count += 1

                    input_file_path = f'{input_dir}/{video_name}'

                    time_dir[f'{video_name}_start_{rep}'] = datetime.now(
                    ).__str__()

                    encoding_cmd = (
                        create_sequential_encoding_cmd(
                            input_file_path, video_name, RESULT_ROOT, dto, quiet_mode=True)
                        if not DRY_RUN
                        else "sleep 0.1"
                    )

                    execute_encoding_stage(encoding_cmd, dto, video_name)
                    time_dir[f'{video_name}_end_{rep}'] = datetime.now().__str__()

                    print(
                        f'Encoded video ({video_count}/{(max_rep - 1) * len(input_files)})')
                    break

    time_dir['end'] = datetime.now().__str__()

    pd.Series(time_dir).to_csv(f'start_stop_times_{datetime.now()}.csv')
    write_encoding_results_to_csv()


@track_emissions(
    offline=True,
    country_iso_code="AUT",
    log_level="error",
    # log_level="error" if CLI_PARSER.is_quiet_ffmpeg() else "debug",
    measure_power_secs=MEASUREMENT_INTERVAL,
    output_dir=RESULT_ROOT,
    save_to_file=True,
    project_name="encoding_stage",
)  # type: ignore
def execute_encoding_stage(
    cmd: str, encoding_dto: EncodingConfigDTO, video_name: str
) -> None:
    execute_encoding_cmd(cmd, encoding_dto, video_name)


def execute_encoding_cmd(
    cmd: str, encoding_dto: EncodingConfigDTO, video_name: str
) -> None:
    global metric_results, nvidia_top

    if USE_CUDA:
        # executes the cmd with nvidia monitoring
        result_df = nvidia_top.get_resource_metric_as_dataframe(cmd)

        rendition = encoding_dto.rendition

        result_df[["preset", "codec", "duration"]] = (
            encoding_dto.preset,
            encoding_dto.codec,
            encoding_dto.segment_duration,
        )
        result_df[["bitrate", "width", "height"]] = (
            rendition.bitrate,
            rendition.width,
            rendition.height,
        )
        result_df["video_name"] = video_name
        result_df["output_path"] = encoding_dto.get_output_directory()

        metric_results.append(result_df)

    elif DRY_RUN:
        print(cmd)
    else:
        os.system(cmd)


def write_encoding_results_to_csv():
    global nvidia_top, metric_results

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_path = f"{RESULT_ROOT}/encoding_results_{current_time}.csv"
    if INCLUDE_CODE_CARBON:
        emission_df = get_dataframe_from_csv(f"{RESULT_ROOT}/emissions.csv").dropna(
            axis=1, how="all"
        )

        # merge codecarbon and timing_df results
        if USE_CUDA:
            nvitop_df = NvidiaTop.merge_resource_metric_dfs(
                metric_results, exclude_timestamps=True
            ).dropna(axis=1, how="all")
            merged_df = pd.concat([emission_df, nvitop_df], axis=1)

            # save to disk
            merged_df.to_csv(result_path)
            os.system(f"rm {RESULT_ROOT}/emissions.csv")


if __name__ == "__main__":
    try:
        Path(RESULT_ROOT).mkdir(parents=True, exist_ok=True)

        if USE_CUDA:
            nvidia_top = NvidiaTop()

        intel_rapl_workaround()
        IdleTimeEnergyMeasurement.measure_idle_energy_consumption(
            result_path=f"{RESULT_ROOT}/encoding_idle_time.csv", idle_time_in_seconds=1
        )

        encoding_configurations: list[EncodingConfig] = [
            EncodingConfig.from_file(file_path) for file_path in ENCODING_CONFIG_PATHS
        ]

        if len(encoding_configurations) == 0:
            raise MissingValueError("No encoding configuration files provided")

        metric_results: list[pd.DataFrame] = []
        timing_metadata: dict[int, dict] = {}

        execute_encoding_benchmark(encoding_configurations)

    except MissingValueError as err:
        print(err)

    except Exception as err:
        print("err", err)

    finally:
        print("done")
