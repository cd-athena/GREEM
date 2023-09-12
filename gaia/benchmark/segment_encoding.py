import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from codecarbon import track_emissions

from gaia.utils.ffmpeg import create_ffmpeg_encoding_command, prepare_sliced_videos
from gaia.utils.config import EncodingConfig, get_output_directory, Rendition
from gaia.utils.timing import TimingMetadata, measure_time_of_system_cmd, IdleTimeEnergyMeasurement
from gaia.utils.dataframe import(
    get_dataframe_from_csv,
    merge_benchmark_dataframes,
    merge_benchmark_and_monitoring_dataframes
)
from gaia.utils.ntfy import send_ntfy

from gaia.hardware.intel import intel_rapl_workaround

from gaia.utils.benchmark import CLI_PARSER

NTFY_TOPIC: str = 'aws_encoding'


ENCODING_CONFIG_PATHS: list[str] = [
    # 'config_files/encoding_test_1.yaml',
    # 'config_files/encoding_test_2.yaml',
    # 'config_files/default_encoding_config.yaml',
    'config_files/segment_encoding.yaml',
    # 'config_files/encoding_config_h264.yaml',
    # 'config_files/encoding_config_h265.yaml'
]

INPUT_FILE_DIR: str = 'dataset/ref_265'
RESULT_ROOT: str = 'results'
COUNTRY_ISO_CODE: str = 'AUT'

USE_SLICED_VIDEOS: bool = CLI_PARSER.is_sliced_encoding()
# if True, no encoding will be executed
DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = CLI_PARSER.is_cuda_enabled()
INCLUDE_CODE_CARBON: bool = CLI_PARSER.is_code_carbon_enabled()

if USE_CUDA:
    from gaia.monitoring.hardware_monitoring import GpuMonitoring


def prepare_data_directories(
    encoding_config: EncodingConfig,
    result_root: str = RESULT_ROOT,
    video_names: list[str] = list()
) -> list[str]:
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

    def is_file_in_config(file_name: str) -> bool:
        if encoding_config.encode_all_videos:
            return True

        file = file_name.split('.')[0]
        if USE_SLICED_VIDEOS:
            file = file.split('_')[0]
        return file in encoding_config.videos_to_encode

    input_files: list[str] = [file_name for file_name in os.listdir(
        video_dir) if is_file_in_config(file_name)]

    if len(input_files) == 0:
        raise ValueError('no video files to encode')

    return input_files


@track_emissions(
    # offline=True,
    # country_iso_code='AUT',
    measure_power_secs=1,
    output_dir=RESULT_ROOT,
    save_to_file=True,
)
def execute_ffmpeg_encoding(
        cmd: str,
        video_name: str,
        codec: str,
        preset: str,
        rendition: Rendition,
        duration: int,
        timing_metadata: dict[int, dict]
) -> None:
    global gpu_monitoring, emission_tracker

    if USE_CUDA:
        gpu_monitoring.current_video = video_name
        gpu_monitoring.rendition = rendition

    start_time, end_time, elapsed_time = measure_time_of_system_cmd(
        cmd)

    metadata = TimingMetadata(
        start_time, end_time, elapsed_time, video_name, codec, preset, rendition, duration)
    timing_metadata[len(
        timing_metadata)] = metadata.to_dict()


def write_encoding_results_to_csv(timing_metadata: dict[int, dict]):
    timing_df: pd.DataFrame = pd.DataFrame.from_dict(
        timing_metadata, orient='index')
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    result_path = f'{RESULT_ROOT}/encoding_results_{current_time}.csv'
    if INCLUDE_CODE_CARBON:
        emission_df = get_dataframe_from_csv(f'{RESULT_ROOT}/emissions.csv')
        # merge codecarbon and timing_df results
        encoding_results_df = merge_benchmark_dataframes(
            emission_df, timing_df)

        if USE_CUDA:
            # merge encoding results with hardware monitoring and idle dataframes
            monitoring_df = pd.read_csv(
                f'{RESULT_ROOT}/monitoring_stream.csv', index_col=0)
            idle_df = pd.read_csv(
                f'{RESULT_ROOT}/encoding_idle_time.csv', index_col=0)
            merged_df = merge_benchmark_and_monitoring_dataframes(
                encoding_results_df, monitoring_df, idle_df)

            # save to disk
            merged_df.to_csv(result_path)
        else:
            encoding_results_df.to_csv(result_path)
        os.system(f'rm {RESULT_ROOT}/emissions.csv')
    else:
        timing_df.to_csv(result_path)


def get_filtered_sliced_videos(encoding_config: EncodingConfig, input_dir: str) -> list[str]:
    input_files: list[str] = get_video_input_files(
        input_dir, encoding_config)

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
    global gpu_monitoring, timing_metadata

    send_ntfy(NTFY_TOPIC, 'start sequential encoding process')
    input_dir = INPUT_FILE_DIR

    for en_idx, encoding_config in enumerate(encoding_configs):

        input_files = sorted([file for file in os.listdir(
            INPUT_FILE_DIR) if file.endswith('.265')])

        # encode for each duration defined in the config file
        prepare_data_directories(encoding_config, video_names=[file.removesuffix('.265') for file in input_files])

        duration = 4
        # encode each video found in the input files corresponding to the duration
        for video_idx, video in enumerate(input_files):
            for codec_idx, codec in enumerate(encoding_config.codecs):
                for preset_idx, preset in enumerate(encoding_config.presets):
                    for rendition_idx, rendition in enumerate(encoding_config.renditions):
                        
                        send_ntfy(
                            NTFY_TOPIC, 
                            f'''
                            - video sequence {video} - ({video_idx + 1}/{len(input_files)})
                            --- used codec {codec} - ({codec_idx + 1}/{len(encoding_config.codecs)})
                            --- used preset {preset} - ({preset_idx + 1}/{len(encoding_config.presets)})
                            --- used {rendition} - ({rendition_idx + 1}/{len(encoding_config.renditions)})
                            --- encoding config - ({en_idx + 1}/{len(encoding_configs)})
                            ''')

                        output_dir: str = f'{RESULT_ROOT}/{get_output_directory(codec, video.removesuffix(".265"), duration, preset, rendition)}'

                        cmd = create_ffmpeg_encoding_command(
                            f'{input_dir}/{video}',
                            output_dir, rendition, preset, duration, codec,
                            use_dash=False,
                            pretty_print=DRY_RUN,
                            cuda_enabled=USE_CUDA,
                            quiet_mode=CLI_PARSER.is_quiet_ffmpeg()
                        )

                        if not DRY_RUN:

                            start_hardware_monitoring()

                            execute_ffmpeg_encoding(
                                cmd, video, codec, preset, rendition, duration, timing_metadata)

                            stop_hardware_monitoring()

                        else:
                            print(cmd)
                            execute_ffmpeg_encoding(
                                'sleep 0.01', video, codec, preset, rendition, duration, timing_metadata)

    write_encoding_results_to_csv(timing_metadata)


if __name__ == '__main__':
    try:
        send_ntfy(NTFY_TOPIC,
                  f'''start benchmark 
              - CUDA: {USE_CUDA} 
              - SLICE: {USE_SLICED_VIDEOS}
              - DRY_RUN: {DRY_RUN}
              ''')
        Path(RESULT_ROOT).mkdir(parents=True, exist_ok=True)

        # intel_rapl_workaround()
        IdleTimeEnergyMeasurement.measure_idle_energy_consumption(result_path=f'{RESULT_ROOT}/encoding_idle_time.csv', idle_time_in_seconds=1)

        encoding_configs: list[EncodingConfig] = [EncodingConfig.from_file(
            file_path) for file_path in ENCODING_CONFIG_PATHS]
        timing_metadata: dict[int, dict] = dict()

        gpu_monitoring = None
        if USE_CUDA:
            gpu_monitoring = GpuMonitoring(RESULT_ROOT, 0.5)

        execute_encoding_benchmark()
    except Exception as err:
        print('err', err)
        send_ntfy(
            NTFY_TOPIC, f'Something went wrong during the benchmark, Exception: {err}')

    finally:
        print('done')
        send_ntfy(NTFY_TOPIC, 'finished benchmark')
