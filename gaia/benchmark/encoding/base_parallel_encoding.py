import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from codecarbon import track_emissions

from gaia.utils.ffmpeg import  create_multi_video_ffmpeg_command, create_simple_multi_video_ffmpeg_command
from gaia.utils.config import EncodingConfig, EncodingConfigDTO, get_output_directory, Rendition
from gaia.utils.timing import TimingMetadata, measure_time_of_system_cmd, IdleTimeEnergyMeasurement
from gaia.utils.dataframe import(
    get_dataframe_from_csv,
    merge_benchmark_dataframes,
    merge_benchmark_and_monitoring_dataframes
)
from gaia.utils.ntfy import send_ntfy


from gaia.utils.benchmark import CLI_PARSER

NTFY_TOPIC: str = 'encoding'


ENCODING_CONFIG_PATHS: list[str] = [
    'config_files/segment_encoding_h264.yaml',
    # 'config_files/segment_encoding_h265.yaml',

]

INPUT_FILE_DIR: str = '../dataset/ref_265'
RESULT_ROOT: str = 'results'
COUNTRY_ISO_CODE: str = 'AUT'

USE_SLICED_VIDEOS: bool = CLI_PARSER.is_sliced_encoding()
# if True, no encoding will be executed
DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = CLI_PARSER.is_cuda_enabled()
INCLUDE_CODE_CARBON: bool = CLI_PARSER.is_code_carbon_enabled()

from gaia.hardware.intel import intel_rapl_workaround
if USE_CUDA:    
    from gaia.hardware.nvidia_top import NvidiaTop

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


def get_filtered_sliced_videos(encoding_config: EncodingConfig, input_dir: str) -> list[str]:
    input_files: list[str] = get_video_input_files(
        input_dir, encoding_config)

    return sorted(input_files)


def remove_media_extension(file_name: str) -> str:
    return file_name.removesuffix('.265').removesuffix('.webm').removesuffix('.mp4')

def execute_encoding_benchmark():
    global timing_metadata, nvidia_top, metric_results

    send_ntfy(NTFY_TOPIC, 'start sequential encoding process')
    input_dir = INPUT_FILE_DIR

    for en_idx, encoding_config in enumerate(encoding_configs):

        input_files = sorted([file for file in os.listdir(
            INPUT_FILE_DIR) if file.endswith('.265')])
        output_files = [remove_media_extension(out_file) for out_file in input_files]

        # encode for each duration defined in the config file
        prepare_data_directories(encoding_config, video_names=output_files)
        
        encoding_dtos: list[EncodingConfigDTO] = encoding_config.get_encoding_dtos()
        
        rendition = encoding_config.renditions[-1]
        
        for window_size in range(1, 6):
            for idx_offset in range(len(input_files)):
                window_idx: int = window_size + idx_offset
                if window_idx > len(input_files):
                    break

                input_slice = [f'{input_dir}/{slice}' for slice in input_files[idx_offset:window_idx]]        
                
                for dto in encoding_dtos:
                          
                        
                    output_dirs: list[str] = [
                            f'{RESULT_ROOT}/{get_output_directory(dto.codec, output, 4, dto.preset, rendition)}' 
                            for output in output_files[:window_size]
                            ]
                        # for rendition_idx, rendition in enumerate(encoding_config.renditions):
                        
                    cmd = create_multi_video_ffmpeg_command(
                        input_slice,
                        output_dirs,
                        dto,
                        cuda_mode=CLI_PARSER.is_cuda_enabled(),
                        quiet_mode=CLI_PARSER.is_quiet_ffmpeg(),
                        pretty_print=True
                    )
                    
                    print(cmd)

                        # execute_encoding_cmd(cmd, preset, codec, rendition, input_slice)

                    # cleanup for next iteration
                    # for out in output_dirs:
                    #     os.system(f'rm {out}/output.mp4')

        # metric_df = nvidia_top.merge_dataframe_results(metric_results)
        # metric_df.to_csv(f'{RESULT_ROOT}/test.csv')
        
        # write_encoding_results_to_csv()
            
@track_emissions(
    offline=True,
    country_iso_code='AUT',
    measure_power_secs=0.5,
    output_dir=RESULT_ROOT,
    save_to_file=True,
)
def execute_encoding_cmd(
    cmd: str,
    preset: str,
    codec: str,
    rendition: Rendition,
    input_slice: list[str]
) -> None:
    global metric_results, nvidia_top
    
    if USE_CUDA:
        result_df = nvidia_top.get_resource_metric_as_dataframe(cmd)
        result_df['preset'] = preset
        result_df['codec'] = codec
        result_df[['bitrate', 'width', 'height']] = rendition.bitrate, rendition.width, rendition.height
        result_df['num_videos'] = len(input_slice)
        
        metric_results.append(result_df)
        
    elif DRY_RUN:
        print(cmd)
    else:
        os.system(cmd)
        
def write_encoding_results_to_csv() -> None:
    global timing_metadata, metric_results
    
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
            monitoring_df = NvidiaTop.merge_resource_metric_dfs(metric_results, exclude_timestamps=True)
            merged_df = pd.concat([emission_df, monitoring_df], axis=1)
            # save to disk
            merged_df.to_csv(result_path)
        else:
            encoding_results_df.to_csv(result_path)
        os.system(f'rm {RESULT_ROOT}/emissions.csv')
    else:
        timing_df.to_csv(result_path)

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
        # IdleTimeEnergyMeasurement.measure_idle_energy_consumption(result_path=f'{RESULT_ROOT}/encoding_idle_time.csv', idle_time_in_seconds=1)

        encoding_configs: list[EncodingConfig] = [EncodingConfig.from_file(
            file_path) for file_path in ENCODING_CONFIG_PATHS]
        timing_metadata: dict[int, dict] = dict()

        gpu_monitoring = None
        if USE_CUDA:
            nvidia_top = NvidiaTop()
            metric_results: list[pd.DataFrame] = list()

        execute_encoding_benchmark()
        
    except Exception as err:
        print('err', err)
        send_ntfy(
            NTFY_TOPIC, f'Something went wrong during the benchmark, Exception: {err}')

    finally:
        send_ntfy(NTFY_TOPIC, 'finished benchmark')
        print('done')
 