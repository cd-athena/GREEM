import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from codecarbon import track_emissions

from greem.hardware.intel import intel_rapl_workaround
from greem.utility.cli_parser import CLI_PARSER
from greem.utility.configuration_classes import DecodingConfig, DecodingConfigDTO
from greem.utility.dataframe import get_dataframe_from_csv
from greem.utility.timing import IdleTimeEnergyMeasurement

# from greem.benchmark.decoding.decoding_utils import get_all_possible_video_files, get_input_files

DECODING_CONFIG_PATHS: list[str] = [
    "config_files/test_decoding_config.yaml",
]

# INPUT_FILE_DIR: str = '../encoding/results'
RESULT_ROOT = "decoding_results"

DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = CLI_PARSER.is_cuda_enabled()
INCLUDE_CODE_CARBON: bool = CLI_PARSER.is_code_carbon_enabled()
IS_QUIET: bool = CLI_PARSER.is_quiet_ffmpeg()

if USE_CUDA:
    from greem.monitoring.nvidia_top import NvidiaTop

CLEANUP_AFTER_DECODE: bool = False

nvidia_top = None

try:
    if USE_CUDA:
        nvidia_top = NvidiaTop()
        metric_results: list[pd.DataFrame] = []

    intel_rapl_workaround()
    IdleTimeEnergyMeasurement.measure_idle_energy_consumption(
        result_path=f"{RESULT_ROOT}/decoding_idle_time.csv", idle_time_in_seconds=1
    )

except Exception as err:
    print("err", err)


def prepare_data_directories(
    decoding_config: DecodingConfig,
    result_root: str = RESULT_ROOT,
    video_names: list[str] = [],
) -> None:
    data_directories = [
        dto.get_output_dir(result_root, video)
        for dto in decoding_config.get_decoding_dtos()
        for video in video_names
    ]

    for directory in data_directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def get_video_name_from_path(video_path: str) -> str:
    path_elems: list[str] = video_path.split("/")
    # TODO find better way than to hardcode the video_name
    return path_elems[4]


def execute_decoding_cmd(
    cmd: str, decoding_dto: DecodingConfigDTO, input_file_path: str
) -> None:
    global metric_results, nvidia_top

    if USE_CUDA:
        # executes the cmd with nvidia monitoring
        result_df = nvidia_top.get_resource_metric_as_dataframe(cmd)
        video_name = get_video_name_from_path(input_file_path)

        rendition = decoding_dto.encoding_representation

        result_df[["encoded_preset", "encoded_codec", "duration"]] = (
            decoding_dto.encoding_preset,
            decoding_dto.encoding_codec,
            "4s",
        )
        result_df[["encoded_bitrate", "encoded_width", "encoded_height"]] = (
            rendition.bitrate,
            rendition.width,
            rendition.height,
        )
        result_df["video_name"] = video_name
        result_df["decoding_scale"] = (
            decoding_dto.scaling_resolution.get_resolution_dir_representation()
        )
        result_df["output_path"] = decoding_dto.get_output_dir(RESULT_ROOT, video_name)

        metric_results.append(result_df)

    elif DRY_RUN:
        print(cmd)
    else:
        os.system(cmd)


def write_decoding_results_to_csv():
    global nvidia_top, metric_results

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_path = f"{RESULT_ROOT}/encoding_results_{current_time}.csv"
    if INCLUDE_CODE_CARBON:
        emission_df = get_dataframe_from_csv(f"{RESULT_ROOT}/emissions.csv")
        # merge codecarbon and timing_df results

        if USE_CUDA:
            nvitop_df = NvidiaTop.merge_resource_metric_dfs(
                metric_results, exclude_timestamps=True
            )
            merged_df = pd.concat([emission_df, nvitop_df], axis=1)
            # save to disk
            merged_df.to_csv(result_path)
            os.system(f"rm {RESULT_ROOT}/emissions.csv")


def start_demuxing(
    input_file_path: str, output_path: str, dto: DecodingConfigDTO
) -> str:
    demuxed_output_path: str = f"{output_path}/demuxed.mp4"
    cuvid_codec: str = get_cuda_decoding_codec(dto)
    demuxing_cmd: str = (
        f"ffmpeg -y {cuvid_codec} -i {input_file_path} {demuxed_output_path}"
    )

    execute_decoding_cmd(demuxing_cmd, dto, input_file_path)

    return demuxed_output_path


def start_decoding(
    input_file_path: str, output_path: str, dto: DecodingConfigDTO
) -> str:
    decoding_output_path: str = f"{output_path}/decoding.yuv"
    cuvid_codec: str = get_cuda_decoding_codec(dto)
    decoding_cmd: str = (
        f"ffmpeg -y {cuvid_codec} -i {input_file_path} {decoding_output_path}"
    )

    execute_decoding_cmd(decoding_cmd, dto, input_file_path)

    return decoding_output_path


def start_scaling(
    input_file_path: str, output_path: str, dto: DecodingConfigDTO
) -> str:
    decoding_input_file_path: str = f"{output_path}/decoding.yuv"
    scaling_output_path: str = f"{output_path}/scaling.yuv"

    cuda_accel: str = "-hwaccel cuvid -hwaccel_output_format cuda" if USE_CUDA else ""
    scaling_cmd: str = (
        f"ffmpeg {cuda_accel} -f rawvideo -c:v rawvideo -s "
        f"{dto.encoding_representation.get_resolution_dir_representation()} -r 23.98 "
        f"-pix_fmt yuv420p -i {decoding_input_file_path} "
        f"-vf scale={dto.scaling_resolution.get_resolution_dir_representation()} "
        f"-y {scaling_output_path}"
    )

    execute_decoding_cmd(scaling_cmd, dto, input_file_path)

    return scaling_output_path


def get_cuda_decoding_codec(dto: DecodingConfigDTO) -> str:
    if not USE_CUDA:
        return ""
    codec = dto.encoding_codec
    return f"-hwaccel cuda -c:v {codec}_cuvid"


@track_emissions(
    offline=True,
    country_iso_code="AUT",
    log_level="error" if CLI_PARSER.is_quiet_ffmpeg() else "debug",
    measure_power_secs=1,
    output_dir=RESULT_ROOT,
    save_to_file=True,
    project_name="scaling",
)
def execute_decoding_benchmark():
    global CLEANUP_AFTER_DECODE
    decoding_configs: list[DecodingConfig] = [
        DecodingConfig.from_file(file_path) for file_path in DECODING_CONFIG_PATHS
    ]
    all_video_files = get_all_possible_video_files()

    for config in decoding_configs:
        prepare_data_directories(config)
        for dto in config.get_decoding_dtos():
            encoded_input_files: list[str] = get_input_files(dto, all_video_files)
            encoded_input_files = [
                file for file in encoded_input_files if file.endswith("output.mp4")
            ]

            for encoded_file_path in encoded_input_files[:1]:
                video_name = get_video_name_from_path(encoded_file_path)
                output_path: str = dto.get_output_dir(RESULT_ROOT, video_name)
                Path(output_path).mkdir(parents=True, exist_ok=True)

                demux_output_path: str = start_demuxing(
                    encoded_file_path, output_path, dto
                )
                decoding_output_path: str = start_decoding(
                    encoded_file_path, output_path, dto
                )
                scaling_output_path: str = start_scaling(
                    encoded_file_path, output_path, dto
                )

                if CLEANUP_AFTER_DECODE:
                    os.system(
                        f"rm {demux_output_path} {decoding_output_path} {scaling_output_path}"
                    )

    write_decoding_results_to_csv()


if __name__ == "__main__":
    # https://pytorch.org/audio/stable/build.ffmpeg.html

    Path(RESULT_ROOT).mkdir(parents=True, exist_ok=True)

    try:
        if USE_CUDA:
            nvidia_top = NvidiaTop()
            metric_results: list[pd.DataFrame] = []

        intel_rapl_workaround()
        IdleTimeEnergyMeasurement.measure_idle_energy_consumption(
            result_path=f"{RESULT_ROOT}/decoding_idle_time.csv", idle_time_in_seconds=1
        )

        execute_decoding_benchmark()

    except Exception as err:
        print("err", err)

    finally:
        print("finished decoding benchmark")
