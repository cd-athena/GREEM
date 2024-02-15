import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from codecarbon import track_emissions

from gaia.utils.ffmpeg import create_ffmpeg_encoding_command
from gaia.utils.configuration_classes import (
    EncodingConfig,
    EncodingConfigDTO,
)

from gaia.utils.timing import IdleTimeEnergyMeasurement
from gaia.utils.dataframe import get_dataframe_from_csv

from gaia.utils.ntfy import send_ntfy

from gaia.hardware.intel import intel_rapl_workaround
from gaia.monitoring.nvidia_top import NvidiaTop

from gaia.utils.cli_parser import CLI_PARSER

NTFY_TOPIC: str = "aws_encoding"


ENCODING_CONFIG_PATHS: list[str] = [
    "config_files/segment_encoding_h264.yaml",
    "config_files/segment_encoding_h265.yaml",
]

INPUT_FILE_DIR: str = "../dataset/ref_265"
RESULT_ROOT: str = "results"
COUNTRY_ISO_CODE: str = "AUT"

USE_SLICED_VIDEOS: bool = CLI_PARSER.is_sliced_encoding()
# if True, no encoding will be executed
DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = True
INCLUDE_CODE_CARBON: bool = CLI_PARSER.is_code_carbon_enabled()


def prepare_data_directories(
    encoding_config: EncodingConfig,
    result_root: str = RESULT_ROOT,
    video_names: list[str] = list(),
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
        dto.get_output_directory(video)
        for dto in encoding_config.get_encoding_dtos()
        for video in video_names
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
        return file in encoding_config.videos_to_encode

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


def start_hardware_monitoring():
    global gpu_monitoring
    if USE_CUDA:
        gpu_monitoring.start()


def stop_hardware_monitoring():
    global gpu_monitoring
    if USE_CUDA:
        gpu_monitoring.stop()


def execute_encoding_benchmark():
    send_ntfy(NTFY_TOPIC, "start sequential encoding process")
    input_dir = INPUT_FILE_DIR

    for en_idx, encoding_config in enumerate(encoding_configs):
        input_files = sorted(
            [file for file in os.listdir(INPUT_FILE_DIR) if file.endswith(".265")]
        )

        # encode for each duration defined in the config file
        prepare_data_directories(
            encoding_config,
            video_names=[file.removesuffix(".265") for file in input_files],
        )
        encoding_dtos: list[EncodingConfigDTO] = encoding_config.get_encoding_dtos()
        duration = 4
        # encode each video found in the input files corresponding to the duration
        for video_idx, video_name in enumerate(input_files):
            for dto_idx, dto in enumerate(encoding_dtos):
                output_dir = f'{RESULT_ROOT}/{dto.get_output_directory(video_name.removesuffix(".265"))}'

                send_ntfy(
                    NTFY_TOPIC,
                    f"""
                    - video sequence {video_name} - ({video_idx + 1}/{len(input_files)})
                    --- config - ({en_idx + 1}/{len(encoding_configs)})
                    --- {dto} - ({dto_idx + 1}/{len(encoding_dtos)})
                    """,
                )
                cmd = (
                    create_ffmpeg_encoding_command(
                        f"{input_dir}/{video_name}",
                        output_dir,
                        dto.rendition,
                        dto.preset,
                        duration,
                        dto.codec,
                        framerate=dto.framerate,
                        use_dash=False,
                        pretty_print=DRY_RUN,
                        cuda_enabled=False,
                        quiet_mode=CLI_PARSER.is_quiet_ffmpeg(),
                    )
                    if not DRY_RUN
                    else "sleep 0.1"
                )

                execute_encoding_cmd(cmd, dto, video_name)

    write_encoding_results_to_csv()


@track_emissions(
    offline=True,
    country_iso_code="AUT",
    log_level="error" if CLI_PARSER.is_quiet_ffmpeg() else "debug",
    measure_power_secs=1,
    output_dir=RESULT_ROOT,
    save_to_file=True,
)
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
        result_df["output_path"] = encoding_dto.get_output_directory(video_name)

        metric_results.append(result_df)

    elif DRY_RUN:
        print(cmd)
    else:
        os.system(cmd)


def write_encoding_results_to_csv():
    global nvidia_top, metric_results

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_path = f"{RESULT_ROOT}/encoding_results_{current_time}.csv"
    if INCLUDE_CODE_CARBON and USE_CUDA:
        emission_df = get_dataframe_from_csv(f"{RESULT_ROOT}/emissions.csv")
        # merge codecarbon and timing_df results

        nvitop_df = NvidiaTop.merge_resource_metric_dfs(
            metric_results, exclude_timestamps=True
        )
        merged_df = pd.concat([emission_df, nvitop_df], axis=1)
        # save to disk
        merged_df.to_csv(result_path)
        os.system(f"rm {RESULT_ROOT}/emissions.csv")


if __name__ == "__main__":
    try:
        send_ntfy(
            NTFY_TOPIC,
            f"""start benchmark 
              - CUDA: {USE_CUDA} 
              - DRY_RUN: {DRY_RUN}
              """,
        )

        Path(RESULT_ROOT).mkdir(parents=True, exist_ok=True)

        gpu_monitoring = None
        if USE_CUDA:
            nvidia_top = NvidiaTop()
            metric_results: list[pd.DataFrame] = list()

        intel_rapl_workaround()
        IdleTimeEnergyMeasurement.measure_idle_energy_consumption(
            result_path=f"{RESULT_ROOT}/encoding_idle_time.csv", idle_time_in_seconds=1
        )

        encoding_configs: list[EncodingConfig] = [
            EncodingConfig.from_file(file_path) for file_path in ENCODING_CONFIG_PATHS
        ]
        timing_metadata: dict[int, dict] = dict()

        execute_encoding_benchmark()

    except Exception as err:
        print("err", err)
        send_ntfy(
            NTFY_TOPIC, f"Something went wrong during the benchmark, Exception: {err}"
        )

    finally:
        print("done")
        send_ntfy(NTFY_TOPIC, "finished benchmark")
