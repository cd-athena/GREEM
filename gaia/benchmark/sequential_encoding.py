import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from codecarbon import track_emissions

from gaia.utils.ffmpeg import create_ffmpeg_encoding_command
from gaia.utils.config import EncodingConfig, get_output_directory, Rendition
from gaia.utils.timing import TimingMetadata, measure_time_of_system_cmd, IdleTimeEnergyMeasurement
from gaia.utils.dataframe import get_dataframe_from_csv, merge_benchmark_dataframes

from gaia.hardware.intel import intel_rapl_workaround

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


def prepare_data_directories(encoding_config: EncodingConfig, result_root: str = RESULT_ROOT, video_names: list[str] = list()) -> list[str]:
    '''Used to generate all directories that are used for the video encoding

    Args:
        encoding_config (EncodingConfig): config class that contains the values that are required to generate the directories.
        result_root (str, optional): _description_. Defaults to RESULT_ROOT.
        video_names (list[str], optional): _description_. Defaults to list().

    Returns:
        list[str]: returns a list of all directories that were created
    '''
    data_directories = encoding_config.get_all_result_directories(video_names)

    for directory in data_directories:
        directory_path: str = f'{result_root}/{directory}'
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    return data_directories


def get_video_input_files(video_dir: str, encoding_config: EncodingConfig) -> list[str]:
    input_files: list[str] = [file_name for file_name in os.listdir(
        video_dir) if encoding_config.encode_all_videos or file_name.split('.')[0] in encoding_config.videos_to_encode]
    
    if len(input_files) == 0:
        raise ValueError('no video files to encode')
    
    return input_files


def execute_ffmpeg_encoding(
        cmd: str,
        video_name: str,
        codec: str,
        preset: str,
        rendition: Rendition,
        duration: int,
        timing_metadata: dict[int, dict]
) -> None:
    start_time, end_time, elapsed_time = measure_time_of_system_cmd(
        cmd)

    metadata = TimingMetadata(
        start_time, end_time, elapsed_time, video_name, codec, preset, rendition, duration)
    timing_metadata[len(
        timing_metadata)] = metadata.to_dict()
    
@track_emissions(
    project_name="Encoding Benchmark",
    country_iso_code=COUNTRY_ISO_CODE,
    output_dir=RESULT_ROOT,
    offline=True,
    
)
def execute_ffmpeg_encoding_code_carbon(
        cmd: str,
        video_name: str,
        codec: str,
        preset: str,
        rendition: Rendition,
        duration: int,
        timing_metadata: dict[int, dict]
) -> None:
    execute_ffmpeg_encoding(
        cmd, video_name, codec, preset, rendition, duration, timing_metadata
    )


def write_encoding_results_to_csv(timing_metadata: dict[int, dict]):
    timing_df: pd.DataFrame = pd.DataFrame.from_dict(
        timing_metadata, orient='index')
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    result_path = f'{RESULT_ROOT}/encoding_results_{current_time}.csv'
    if INCLUDE_CODE_CARBON:
        emission_df = get_dataframe_from_csv(f'{RESULT_ROOT}/emissions.csv')
        merged_df = merge_benchmark_dataframes(emission_df, timing_df)

        merged_df.to_csv(result_path)
        os.system(f'rm {RESULT_ROOT}/emissions.csv')

    else:
        timing_df.to_csv(result_path)


def execute_encoding_benchmark():

    for encoding_config in encoding_configs:

        input_files: list[str] = get_video_input_files(
            INPUT_FILE_DIR, encoding_config)

        prepare_data_directories(encoding_config, video_names=input_files)

        ffmpeg_encoding = execute_ffmpeg_encoding_code_carbon if INCLUDE_CODE_CARBON else execute_ffmpeg_encoding

        for duration in encoding_config.segment_duration:
            for video in input_files:
                for codec in encoding_config.codecs:
                    for preset in encoding_config.presets:
                        for rendition in encoding_config.renditions:

                            output_dir: str = f'{RESULT_ROOT}/{get_output_directory(codec, video, duration, preset, rendition)}'
                            cmd = create_ffmpeg_encoding_command(
                                f'{INPUT_FILE_DIR}/{video}', output_dir, rendition, preset, duration, codec, pretty_print=DRY_RUN)

                            if not DRY_RUN:
                                ffmpeg_encoding(
                                    cmd, video, codec, preset, rendition, duration, timing_metadata)

                            else:
                                print(cmd)
                                ffmpeg_encoding(
                                    'sleep 0.01', video, codec, preset, rendition, duration, timing_metadata)

    write_encoding_results_to_csv(timing_metadata)


if __name__ == '__main__':
    intel_rapl_workaround()
    IdleTimeEnergyMeasurement.measure_idle_energy_consumption(result_path='encoding_idle_time.csv', idle_time_in_seconds=1)

    encoding_configs: list[EncodingConfig] = [EncodingConfig.from_file(
        file_path) for file_path in ENCODING_CONFIG_PATHS]
    timing_metadata: dict[int, dict] = dict()

    execute_encoding_benchmark()