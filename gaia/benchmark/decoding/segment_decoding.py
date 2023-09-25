import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from codecarbon import track_emissions

from gaia.utils.config import DecodingConfig


from gaia.utils.timing import IdleTimeEnergyMeasurement
from gaia.utils.dataframe import get_dataframe_from_csv

from gaia.utils.ntfy import send_ntfy

from gaia.hardware.intel import intel_rapl_workaround
from gaia.hardware.nvidia_top import NvidiaTop

from gaia.utils.benchmark import CLI_PARSER

NTFY_TOPIC: str = 'decoding'

DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = CLI_PARSER.is_cuda_enabled()
INCLUDE_CODE_CARBON: bool = CLI_PARSER.is_code_carbon_enabled()

def get_input_files(decoding_config: DecodingConfig) -> list[str]:
    input_files: list[str] = list()
    
    # TODO
    
    return input_files


if __name__ == '__main__':
    try:
        send_ntfy(NTFY_TOPIC,
                  f'''start decoding benchmark 
              - CUDA: {USE_CUDA} 
              - DRY_RUN: {DRY_RUN}
              ''')
    except Exception as err:
        print('err', err)
        send_ntfy(
            NTFY_TOPIC, f'Something went wrong during the decoding benchmark, Exception: {err}')

    finally:
        print('done')
        send_ntfy(NTFY_TOPIC, 'finished decoding benchmark')