import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from codecarbon import track_emissions

from gaia.utils.config import DecodingConfig, DecodingConfigDTO

from time import time


from gaia.utils.timing import IdleTimeEnergyMeasurement
from gaia.utils.dataframe import get_dataframe_from_csv

from gaia.utils.ntfy import send_ntfy

# from gaia.hardware.intel import intel_rapl_workaround

from gaia.utils.benchmark import CLI_PARSER

# from gaia.benchmark.decoding.decoding_utils_dup import get_all_possible_video_files, get_input_files
from gaia.benchmark.decoding.decoding_utils import get_all_possible_video_files, get_input_files

DECODING_CONFIG_PATHS: list[str] = [
    'config_files/test_decoding_config.yaml',
]

NTFY_TOPIC: str = 'decoding'
# INPUT_FILE_DIR: str = '../encoding/results'
RESULT_ROOT = 'decoding_results'

DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = CLI_PARSER.is_cuda_enabled()
INCLUDE_CODE_CARBON: bool = CLI_PARSER.is_code_carbon_enabled()
IS_QUIET: bool = CLI_PARSER.is_quiet_ffmpeg()

if USE_CUDA:
    from gaia.hardware.nvidia_top import NvidiaTop

def prepare_data_directories(
    decoding_config: DecodingConfig,
    result_root: str = RESULT_ROOT,
    video_names: list[str] = list()
) -> None:
    
    data_directories = [
        dto.get_output_dir(result_root, video)
        for dto in decoding_config.get_decoding_dtos()
        for video in video_names
    ]
    
    for directory in data_directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
def get_video_name_from_path(video_path: str) -> str:
    path_elems: list[str] = video_path.split('/')
    # TODO find better way than to hardcode the video_name
    return path_elems[4]


def start_demuxing(input_file_path: str, output_path: str) -> None:
    demuxed_output_path: str = f'{output_path}/demuxed.mp4'
    demuxing_cmd: str = f'ffmpeg -y -i {input_file_path} {demuxed_output_path}'
    
    if USE_CUDA:
        pass
    else:
        os.system(demuxing_cmd)
        
def start_decoding(input_file_path: str, output_path: str) -> None:
    decoding_output_path: str = f'{output_path}/decoding.yuv'
    decoding_cmd: str = f'ffmpeg -y -i {input_file_path} {decoding_output_path}'
    
    if USE_CUDA:
        pass
    else:
        os.system(decoding_cmd)
        

def start_scaling(output_path: str, dto: DecodingConfigDTO) -> None:
    input_file_path: str = f'{output_path}/decoding.yuv'
    scaling_output_path: str = f'{output_path}/scaling.yuv'
    scaling_cmd: str = f'ffmpeg {IS_QUIET} -f rawvideo -vcodec rawvideo -s ' \
                        f'{dto.encoding_rendition.width}x{dto.encoding_rendition.height} -r 23.98 ' \
                        f'-pix_fmt yuv420p -i {input_file_path} ' \
                        f'-vf scale={dto.scaling_resolution.get_resolution_dir_representation()} ' \
                        f'-y {scaling_output_path}'
    
    if USE_CUDA:
        pass
    else:
        os.system(scaling_cmd)    


def execute_decoding_benchmark():
    decoding_configs: list[DecodingConfig] = [DecodingConfig.from_file(file_path) for file_path in DECODING_CONFIG_PATHS]
    all_video_files = get_all_possible_video_files()
    
    for config in decoding_configs:
        prepare_data_directories(config)
        for dto in config.get_decoding_dtos():
            encoded_input_files: list[str] = get_input_files(dto, all_video_files)
            encoded_input_files = [file for file in encoded_input_files if 'output.mp4' in file]
            
            for encoded_file_path in encoded_input_files:
                
                video_name = get_video_name_from_path(encoded_file_path)
                output_path: str = dto.get_output_dir(RESULT_ROOT, video_name)
                Path(output_path).mkdir(parents=True, exist_ok=True)
                
                start_demuxing(encoded_file_path, output_path)
                start_decoding(encoded_file_path, output_path)
                start_scaling(output_path, dto)
    
    # TODO store benchmark results


if __name__ == '__main__':
        
    try:
        send_ntfy(NTFY_TOPIC,
                  f'''start decoding benchmark 
              - CUDA: {USE_CUDA} 
              - DRY_RUN: {DRY_RUN}
              ''')
    
    # TODO add monitoring
        if USE_CUDA:
            nvidia_top = NvidiaTop()
            metric_results: list[pd.DataFrame] = list()
            
    #     intel_rapl_workaround()
    #     IdleTimeEnergyMeasurement.measure_idle_energy_consumption(result_path=f'{RESULT_ROOT}/decoding_idle_time.csv', idle_time_in_seconds=1)

        execute_decoding_benchmark()


    except Exception as err:
        print('err', err)
        send_ntfy(
            NTFY_TOPIC, 
            f'Something went wrong during the decoding benchmark, Exception: {err}', 
            print_message=True)

    finally:
        send_ntfy(NTFY_TOPIC, 'finished decoding benchmark', print_message=True)
    