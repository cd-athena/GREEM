import sys
sys.path.append("..")

import os
from pathlib import Path
from utils.ffmpeg import create_ffmpeg_encoding_command
import pandas as pd
from datetime import datetime
from codecarbon import track_emissions

from utils.config import EncodingConfig, get_output_directory, Rendition
from utils.timing import TimingMetadata, measure_time_of_system_cmd, IdleTimeEnergyMeasurement
from utils.dataframe import get_dataframe_from_csv, merge_benchmark_dataframes

from hardware.intel import intel_rapl_workaround

ENCODING_CONFIG_PATHS: list[str] = [
    # 'config_files/encoding_test_1.yaml',
    # 'config_files/encoding_test_2.yaml',
    # 'config_files/default_encoding_config.yaml',
    'config_files/test_encoding_config.yaml',
    # 'config_files/encoding_config_h264.yaml',
    # 'config_files/encoding_config_h265.yaml'
]


if __name__ == '__main__':
    intel_rapl_workaround()
    IdleTimeEnergyMeasurement.measure_idle_energy_consumption(result_path='encoding_idle_time.csv', idle_time_in_seconds=1)

    encoding_configs: list[EncodingConfig] = [EncodingConfig.from_file(
        file_path) for file_path in ENCODING_CONFIG_PATHS]
    timing_metadata: dict[int, dict] = dict()

    # execute_encoding_benchmark()