import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from codecarbon import track_emissions

from gaia.utils.config import DecodingConfig, DecodingConfigDTO


from gaia.utils.timing import IdleTimeEnergyMeasurement
from gaia.utils.dataframe import get_dataframe_from_csv

from gaia.utils.ntfy import send_ntfy

from gaia.hardware.intel import intel_rapl_workaround
from gaia.hardware.nvidia_top import NvidiaTop

from gaia.utils.benchmark import CLI_PARSER

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


def execute_decoding_benchmark():
    decoding_configs: list[DecodingConfig] = [DecodingConfig.from_file(file_path) for file_path in DECODING_CONFIG_PATHS]
    all_video_files = get_all_possible_video_files()
    
    for config in decoding_configs:
        for dto in config.get_decoding_dtos():
            pass
    pass


if __name__ == '__main__':
    decoding_configs: list[DecodingConfig] = [DecodingConfig.from_file(file_path) for file_path in DECODING_CONFIG_PATHS]
    all_video_files = get_all_possible_video_files()
    config = decoding_configs[0]
    
    dto = config.get_decoding_dtos()[0]
    
    # print(all_video_files)
    
    for dto in config.get_decoding_dtos():
        # print(dto.encoding_preset, dto.encoding_codec, dto.encoding_rendition, dto.framerate)
        input_files = get_input_files(dto, all_video_files)
        # print(input_files[:10])
        print(input_files[0])
        print(len(input_files))
        
        # test
        
    # try:
    #     send_ntfy(NTFY_TOPIC,
    #               f'''start decoding benchmark 
    #           - CUDA: {USE_CUDA} 
    #           - DRY_RUN: {DRY_RUN}
    #           ''')
        
    #     Path(RESULT_ROOT).mkdir(parents=True, exist_ok=True)
        
    #     gpu_monitoring = None
    #     if USE_CUDA:
    #         nvidia_top = NvidiaTop()
    #         metric_results: list[pd.DataFrame] = list()
            
    #     intel_rapl_workaround()
    #     IdleTimeEnergyMeasurement.measure_idle_energy_consumption(result_path=f'{RESULT_ROOT}/decoding_idle_time.csv', idle_time_in_seconds=1)

    #     decoding_configs: list[DecodingConfig] = [DecodingConfig.from_file(file_path) for file_path in DECODING_CONFIG_PATHS]
        
    #     execute_decoding_benchmark()


    # except Exception as err:
    #     print('err', err)
    #     send_ntfy(
    #         NTFY_TOPIC, f'Something went wrong during the decoding benchmark, Exception: {err}')

    # finally:
    #     print('done')
    #     send_ntfy(NTFY_TOPIC, 'finished decoding benchmark')