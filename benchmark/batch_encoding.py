from enum import Enum
from utils import get_video_input_files, prepare_data_directories
from hardware.intel import intel_rapl_workaround
from utils.dataframe import get_dataframe_from_csv, merge_benchmark_dataframes
from utils.timing import TimingMetadata, measure_time_of_system_cmd, IdleTimeEnergyMeasurement
from utils.config import EncodingConfig, get_output_directory, Rendition
from codecarbon import track_emissions
from datetime import datetime
import pandas as pd
from utils.ffmpeg import create_ffmpeg_encoding_command, create_ffmpeg_command_all_renditions
from pathlib import Path
import os
import sys
sys.path.append("..")


class EncodingVariant(Enum):
    SEQUENTIAL = 1
    BATCH = 2


ENCODING_CONFIG_PATHS: list[str] = [
    # 'config_files/encoding_test_1.yaml',
    # 'config_files/encoding_test_2.yaml',
    # 'config_files/default_encoding_config.yaml',
    'config_files/test_encoding_config.yaml',
    # 'config_files/encoding_config_h264.yaml',
    # 'config_files/encoding_config_h265.yaml'
]

INPUT_FILE_DIR: str = 'data'
RESULT_ROOT: str = 'results'
COUNTRY_ISO_CODE: str = 'AUT'

DRY_RUN: bool = False  # if True, no encoding will be executed
INCLUDE_CODE_CARBON: bool = False


def encode(encoding_config: EncodingConfig, input_files: list[str], encoding_variant: EncodingVariant):

    if encoding_variant == EncodingVariant.BATCH:
        encode_batch(encoding_config, input_files)

    elif encoding_variant == EncodingVariant.SEQUENTIAL:
        pass
    else:
        print('WTF??')


def encode_batch(encoding_config: EncodingConfig, input_files: list[str]) -> None:
    for segment_duration in encoding_config.segment_duration:
        for video in input_files:
            for codec in encoding_config.codecs:
                for preset in encoding_config.presets:

                    input_file_path: str = f'{INPUT_FILE_DIR}/{video}'
                    if any([x in video for x in ['.webm', '.mp4']]):
                        video_name = video.removesuffix('.webm').removesuffix('.mp4')

                    output_dir: str = f'{RESULT_ROOT}/{codec}/{video_name}/{segment_duration}s/{preset}'

                    cmd = create_ffmpeg_command_all_renditions(
                        input_file_path,
                        output_dir,
                        encoding_config.renditions,
                        preset,
                        codec,
                        segment_duration,
                        pretty_print=DRY_RUN
                    )

def execute_batch_encoding(
        cmd: str,
        video_name: str,
        codec: str,
        preset: str,
        renditions: list[Rendition],
        duration: int,
        timing_metadata: dict[int, dict]
) -> None:
    start_time, end_time, elapsed_time = measure_time_of_system_cmd(
        cmd)
                    


def execute_encoding_benchmark(encoding_configs: list[EncodingConfig]):
    # TODO, think about a way to combine the benchmarks and use an enum to determine which is used

    for encoding_config in encoding_configs:
        input_files: list[str] = get_video_input_files(
            INPUT_FILE_DIR, encoding_config)

        prepare_data_directories(encoding_config, video_names=input_files)


if __name__ == '__main__':
    intel_rapl_workaround()
    IdleTimeEnergyMeasurement.measure_idle_energy_consumption(
        result_path='encoding_idle_time.csv', idle_time_in_seconds=1)

    configs: list[EncodingConfig] = [EncodingConfig.from_file(
        file_path) for file_path in ENCODING_CONFIG_PATHS]
    timing_metadata: dict[int, dict] = dict()

    execute_encoding_benchmark()
