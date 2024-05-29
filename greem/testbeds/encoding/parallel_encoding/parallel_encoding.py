from collections import deque
import os
from datetime import datetime
from pathlib import Path
from enum import Enum

import pandas as pd

# from greem.hardware.intel import intel_rapl_workaround
from greem.utility.ffmpeg import create_multi_video_ffmpeg_command
from greem.utility.configuration_classes import EncodingConfig, EncodingConfigDTO

from greem.utility.cli_parser import CLI_PARSER
from greem.utility.monitoring import HardwareTracker

NTFY_TOPIC: str = 'gpu_encoding'

ENCODING_CONFIG_PATHS: list[str] = [
    'config_files/parallel_encoding.yaml',
    # 'config_files/segment_encoding_h265.yaml',
]

INPUT_FILE_DIR: str = '../../dataset/ref_265'
RESULT_ROOT: str = 'results'
COUNTRY_ISO_CODE: str = 'AUT'

USE_SLICED_VIDEOS: bool = CLI_PARSER.is_sliced_encoding()
# if True, no encoding will be executed
DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = CLI_PARSER.is_cuda_enabled()
INCLUDE_CODE_CARBON: bool = CLI_PARSER.is_code_carbon_enabled()
SMALL_TESTBED: bool = True
HOST_NAME: str = os.uname()[1]

CLEANUP: bool = False

IS_BATCH_ENCODING: bool = True


if USE_CUDA:
    from greem.utility.gpu_utils import NvidiaGpuUtils, NvidiaGPUMetadata
    gpu_utils = NvidiaGpuUtils()
    has_nvidia = gpu_utils.has_nvidia_gpu
    GPU_COUNT = gpu_utils.gpu_count if has_nvidia else 0
    GPU_INFO: list[NvidiaGPUMetadata] = gpu_utils.nvidia_metadata.gpu if has_nvidia else []
    del gpu_utils

current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
result_path = f'{RESULT_ROOT}/encoding_results_{current_time}_{HOST_NAME}.csv'
hardware_tracker = HardwareTracker(cuda_enabled=True, measure_power_secs=0.5)


class ParallelMode(Enum):
    ONE_VIDEO_MULTIPLE_REPRESENTATIONS = 1
    MULTIPLE_VIDEOS_ONE_REPRESENTATION = 2
    MULTIPLE_VIDEOS_MULTIPLE_REPRESENTATIONS = 3


monitoring_results: deque = deque()


def prepare_data_directories(
        encoding_config: EncodingConfig,
        result_root: str = RESULT_ROOT,
        video_names=None
) -> list[str]:
    '''Used to generate all directories that are used for the video encoding

    Args:
        encoding_config (EncodingConfig): config class that contains the values that are required to generate the directories.
        result_root (str, optional): _description_. Defaults to RESULT_ROOT.
        video_names (list[str], optional): _description_. Defaults to list().

    Returns:
        list[str]: returns a list of all directories that were created
    '''
    if video_names is None:
        video_names = list()
    data_directories = encoding_config.get_all_result_directories()

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
        return encoding_config.videos_to_encode is not None and file in encoding_config.videos_to_encode

    input_files: list[str] = [file_name for file_name in os.listdir(
        video_dir) if is_file_in_config(file_name)]

    if len(input_files) == 0:
        raise ValueError('no video files to encode')

    return input_files


def get_filtered_sliced_videos(encoding_config: EncodingConfig, input_dir: str) -> list[str]:
    input_files: list[str] = get_video_input_files(
        input_dir, encoding_config)

    return sorted(input_files)


def abbreviate_video_name(video_name: str) -> str:
    video_name_no_ext: str = video_name.replace('.265', '')

    upper_case: str = ''.join(
        [
            f'{c}{video_name_no_ext[video_name_no_ext.find(c) + 1]}'
            for c in video_name_no_ext if c.isupper()
        ])
    numbers: str = ''.join([c for c in video_name_no_ext if c.isnumeric()])
    abbreviate: str = f'{upper_case}_{numbers}'

    return abbreviate


def remove_media_extension(file_name: str) -> str:
    return file_name.removesuffix('.265').removesuffix('.webm').removesuffix('.mp4')


def one_video_multiple_representations_encoding(
    encoding_config: EncodingConfig,
    window_size_start: int,
    window_size_end: int,
    input_files: list[str],
    input_dir: str = INPUT_FILE_DIR
):
    assert window_size_start > 0
    assert window_size_start < window_size_end

    # encoding_dtos: list[EncodingConfigDTO] = encoding_config.get_encoding_dtos()

    for codec in encoding_config.codecs:
        for preset in encoding_config.presets:
            for framerate in encoding_config.framerate:
                for input_file in input_files:
                    input_file_dir = f'{input_dir}/{input_file}'

                    print(codec, preset, framerate,
                          encoding_config.renditions, input_file)
                    print()

        # for idx_offset in range(0, len(encoding_dtos), step_size):
        #     window_idx: int = window_size + idx_offset
        #     if window_idx > len(input_files):
        #         break


def multiple_video_one_representation_encoding(
    encoding_config: EncodingConfig,
    window_size_start: int,
    window_size_end: int,
    input_files: list[str],
    input_dir: str = INPUT_FILE_DIR
) -> None:

    assert window_size_start > 0
    assert window_size_start < window_size_end

    encoding_dtos: list[EncodingConfigDTO] = encoding_config.get_encoding_dtos(
    )

    for window_size in range(window_size_start, window_size_end):
        if USE_CUDA and GPU_COUNT > 0:
            step_size: int = window_size * GPU_COUNT
        elif IS_BATCH_ENCODING:
            step_size: int = window_size
        else:
            step_size: int = 1
        gpu_count = gpu_count if GPU_COUNT > 0 else 1
        print(f'window_size: {window_size} -- step_size: {step_size}')

        for idx_offset in range(0, len(input_files), step_size):
            window_idx: int = window_size * gpu_count + idx_offset
            if window_idx > len(input_files):
                break

            input_slice = [
                f'{input_dir}/{file_slice}' for file_slice in input_files[idx_offset:window_idx]]

            for dto in encoding_dtos:
                output_directory: str = dto.get_output_directory()

                cmd = create_multi_video_ffmpeg_command(
                    input_slice,
                    [f'{RESULT_ROOT}/{output_directory}']*len(input_slice),
                    dto,
                    cuda_mode=USE_CUDA,
                    gpu_count=gpu_count,
                    quiet_mode=CLI_PARSER.is_quiet_ffmpeg(),
                    pretty_print=DRY_RUN
                )

                execute_encoding_cmd(cmd, dto, input_slice)
                break
            break


def multiple_video_multiple_representations_encoding():
    pass


def store_monitoring_results() -> None:

    if len(monitoring_results) > 0:
        df = pd.concat(monitoring_results)
        df.to_csv(result_path)
    else:
        print('no monitoring results found')


def execute_encoding_benchmark(encoding_configuration: list[EncodingConfig], parallel_mode: ParallelMode):

    input_dir = INPUT_FILE_DIR

    for en_idx, encoding_config in enumerate(encoding_configuration):

        input_files = sorted([file for file in os.listdir(
            INPUT_FILE_DIR) if file.endswith('.265')])

        if SMALL_TESTBED:
            input_files = input_files[:20]

        output_files = [remove_media_extension(
            out_file) for out_file in input_files]

        prepare_data_directories(encoding_config, video_names=output_files)

        if parallel_mode == ParallelMode.MULTIPLE_VIDEOS_ONE_REPRESENTATION:
            multiple_video_one_representation_encoding(
                encoding_config, 2, 8, input_files, input_dir)
        elif parallel_mode == ParallelMode.ONE_VIDEO_MULTIPLE_REPRESENTATIONS:
            # TODO
            # raise NotImplementedError('OVMR not implemented yet')
            one_video_multiple_representations_encoding(
                encoding_config, 2, 4, input_files, input_dir)
        elif parallel_mode == ParallelMode.MULTIPLE_VIDEOS_MULTIPLE_REPRESENTATIONS:
            # TODO
            raise NotImplementedError('MVMR not implemented yet')
            multiple_video_multiple_representations_encoding()

    store_monitoring_results()


def execute_encoding_cmd(
        cmd: str,
        dto: EncodingConfigDTO,
        input_slice: list[str]
) -> None:

    preset, codec, rendition = dto.preset, dto.preset, dto.rendition
    bitrate, width, height = rendition.bitrate, rendition.width, rendition.height

    video_abbr = ','.join([abbreviate_video_name(video.split('/')[-1])
                          for video in input_slice]) + f'{bitrate}k:{width}x{height}'

    if not DRY_RUN:
        hardware_tracker.monitor_process(cmd)
        add_monitoring_results(dto, input_slice)

        hardware_tracker.clear()
    else:
        print(cmd)


def add_monitoring_results(dto: EncodingConfigDTO, input_slice: list[str]):
    preset, codec, rendition = dto.preset, dto.codec, dto.rendition
    bitrate, width, height = rendition.bitrate, rendition.width, rendition.height
    framerate, segment_duration = dto.framerate, dto.segment_duration
    result_df = hardware_tracker.to_dataframe()
    result_df[['preset', 'codec']] = preset, codec
    result_df[['framerate', 'segment_duration']
              ] = framerate, segment_duration
    result_df[['bitrate', 'width', 'height']] = bitrate, width, height
    result_df['video_list'] = ','.join(
        [abbreviate_video_name(video.split('/')[-1]) for video in input_slice])
    result_df['num_videos'] = len(input_slice)

    monitoring_results.append(result_df)
    hardware_tracker.clear()
    store_monitoring_results()


if __name__ == '__main__':

    Path(RESULT_ROOT).mkdir(parents=True, exist_ok=True)

    encoding_configs: list[EncodingConfig] = [EncodingConfig.from_file(
        file_path) for file_path in ENCODING_CONFIG_PATHS]

    hardware_tracker.start()

    execute_encoding_benchmark(
        encoding_configs, ParallelMode.MULTIPLE_VIDEOS_ONE_REPRESENTATION)

    hardware_tracker.stop()
