import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from greem.testbeds.encoding.parallel_encoding.parallel_utils import (
    ParallelMode,
    get_gpu_count,
    prepare_data_directories,
)
from greem.utility.cli_parser import CLI_PARSER
from greem.utility.configuration_classes import EncodingConfig, EncodingConfigDTO
from greem.utility.ffmpeg import (
    create_multi_video_ffmpeg_command,
    create_one_video_multiple_representation_command,
)
from greem.utility.monitoring import HardwareTracker
from greem.utility.video_file_utility import (
    abbreviate_video_name,
    remove_media_extension,
)

ENCODING_CONFIG_PATHS: list[str] = [
    "config_files/parallel_encoding_h264.yaml",
    "config_files/parallel_encoding_h265.yaml",
]

# INPUT_FILE_DIR: str = '/home/shared2/athena2/Dataset/Inter4K'
# INPUT_FILE_DIR: str = '../../dataset/Inter4K/60fps/UHD'
INPUT_FILE_DIR: str = "../../dataset/Inter4K/60fps/HEVC"
# INPUT_FILE_DIR: str = '../../dataset/ref_265'
RESULT_ROOT: str = "results"
COUNTRY_ISO_CODE: str = "AUT"

# if True, no encoding will be executed
DRY_RUN: bool = CLI_PARSER.is_dry_run()
USE_CUDA: bool = CLI_PARSER.is_cuda_enabled()
SMALL_TESTBED: bool = True
HOST_NAME: str = os.uname()[1]

TEST_REPETITIONS: int = 3
assert TEST_REPETITIONS > 0, "must be bigger than zero"

GPU_COUNT: int = get_gpu_count()

hardware_tracker = HardwareTracker(cuda_enabled=USE_CUDA, measure_power_secs=0.5)


# Change to encode in a different parallel mode
parallel_mode = ParallelMode.MULTIPLE_VIDEOS_ONE_REPRESENTATION

monitoring_results: list = []


def one_video_multiple_representations_encoding(
    encoding_config: EncodingConfig,
    window_size_start: int,
    window_size_end: int,
    input_files: list[str],
    input_dir: str = INPUT_FILE_DIR,
) -> None:
    assert window_size_start > 0
    assert window_size_start < window_size_end

    # TODO

    # encoding_dtos: list[EncodingConfigDTO] = encoding_config.get_encoding_dtos()

    gpu_count: int = GPU_COUNT if USE_CUDA and GPU_COUNT > 0 else 1

    for codec in encoding_config.codecs:
        for preset in encoding_config.presets:
            for framerate in encoding_config.framerate:
                print(codec, preset, framerate, encoding_config.representations)
                for input_file in input_files:
                    input_file_dir = f"{input_dir}/{input_file}"
                    # TODO
                    cmd = create_one_video_multiple_representation_command(
                        input_file_dir,
                        RESULT_ROOT,
                        encoding_config,
                        USE_CUDA,
                        pretty_print=False,
                    )

                    if not DRY_RUN:
                        hardware_tracker.monitor_process(cmd)
                        # TODO add ovmr monitoring results
                        # _add_ovmr_monitoring_results(encoding_config, inpu)
                        hardware_tracker.clear()

                    else:
                        print(cmd)

            # store_monitoring_results(reset_monitoring_results=True, window_size=winsi)

        # for idx_offset in range(0, len(encoding_dtos), step_size):
        #     window_idx: int = window_size + idx_offset
        #     if window_idx > len(input_files):
        #         break


def multiple_video_one_representation_encoding(
    encoding_config: EncodingConfig,
    window_size_start: int,
    window_size_end: int,
    input_files: list[str],
    input_dir: str = INPUT_FILE_DIR,
) -> None:
    """
    Encodes multiple video files in batches, applying a single representation
    from the provided encoding configuration. The encoding process is performed
    using the FFmpeg command with support for GPU acceleration.

    Args:
        encoding_config (EncodingConfig): An object containing the configuration
            details for encoding, including the target formats, resolutions, and
            other relevant parameters.
        window_size_start (int): The initial window size (batch size) for processing
            the video files. It determines how many files are processed in each batch.
        window_size_end (int): The final window size (batch size) for processing the
            video files. The function will iterate from `window_size_start` to
            `window_size_end`, increasing the batch size progressively.
        input_files (list[str]): A list of video file names (relative paths) to be
            processed, located in `input_dir`.
        input_dir (str, optional): The directory where the input video files are
            located. Defaults to the globally defined `INPUT_FILE_DIR`.

    Returns:
        None: This function does not return any value. It processes the video files
        and stores the encoded outputs in the specified directories.

    Raises:
        AssertionError: If `window_size_start` is less than or equal to 0, or if
        `window_size_start` is not less than `window_size_end`.

    Notes:
        - The function calculates the batch size for each iteration by multiplying
          the window size by the number of available GPUs. If CUDA is not enabled
          or the GPU count is zero, it defaults to a single GPU.
        - For each batch of video files, the function constructs an FFmpeg command
          to perform the encoding, with optional support for CUDA-based acceleration.
        - If `DRY_RUN` is enabled, the function will print the FFmpeg commands
          instead of executing them.
        - Hardware resource monitoring is integrated during the encoding process,
          and results are stored for further analysis.
        - The function handles batches of files by slicing `input_files` according
          to the calculated window size and processes each batch sequentially.
    """
    assert window_size_start > 0
    assert window_size_start < window_size_end

    encoding_dtos: list[EncodingConfigDTO] = encoding_config.get_encoding_dtos()
    gpu_count = GPU_COUNT if USE_CUDA and GPU_COUNT > 0 else 1

    for window_size in range(window_size_start, window_size_end + 1):
        step_size: int = window_size * gpu_count

        for idx_offset in range(0, len(input_files), step_size):
            window_idx: int = window_size * gpu_count + idx_offset
            if window_idx > len(input_files):
                window_idx = len(input_files)

            input_slice = [
                f"{input_dir}/{file_slice}"
                for file_slice in input_files[idx_offset:window_idx]
            ]

            for dto in encoding_dtos[:1]:
                output_directory: str = f"{RESULT_ROOT}/{dto.get_output_directory()}"

                cmd = create_multi_video_ffmpeg_command(
                    input_slice,
                    [output_directory] * len(input_slice),
                    dto,
                    cuda_mode=USE_CUDA,
                    gpu_count=gpu_count,
                    quiet_mode=CLI_PARSER.is_quiet_ffmpeg(),
                    pretty_print=DRY_RUN,
                )

                if not DRY_RUN:
                    hardware_tracker.monitor_process(cmd)
                    _add_mvor_monitoring_results(dto, input_slice)
                    hardware_tracker.clear()

                else:
                    print(cmd)

        store_monitoring_results(
            reset_monitoring_results=True, window_size=window_size * gpu_count
        )


def reduced_multiple_video_one_representation_encoding(
    encoding_config: EncodingConfig,
    input_files: list[str],
    input_dir: str = INPUT_FILE_DIR,
) -> None:
    encoding_dtos: list[EncodingConfigDTO] = encoding_config.get_encoding_dtos()
    gpu_count = GPU_COUNT if USE_CUDA and GPU_COUNT > 0 else 1

    num_videos_in_parallel: list[int] = [1, 2, 5, 10, 15, 20]

    for window_size in num_videos_in_parallel:
        step_size: int = window_size * gpu_count

        for idx_offset in range(0, len(input_files), step_size):
            window_idx: int = window_size * gpu_count + idx_offset

            # make sure we don't exceed the index of available input videos
            # and still encode the remainder of a run
            if window_idx > len(input_files):
                window_idx = len(input_files)

            input_slice = [
                f"{input_dir}/{file_slice}"
                for file_slice in input_files[idx_offset:window_idx]
            ]

            for dto in encoding_dtos:
                output_directory: str = f"{RESULT_ROOT}/{dto.get_output_directory()}"

                cmd = create_multi_video_ffmpeg_command(
                    input_slice,
                    [output_directory] * len(input_slice),
                    dto,
                    cuda_mode=USE_CUDA,
                    gpu_count=gpu_count,
                    quiet_mode=CLI_PARSER.is_quiet_ffmpeg(),
                    pretty_print=DRY_RUN,
                )

                if not DRY_RUN:
                    hardware_tracker.monitor_process(cmd)
                    _add_mvor_monitoring_results(dto, input_slice)

                else:
                    print(cmd)

        # store results for each num_videos_in_parallel iteration
        store_monitoring_results(
            reset_monitoring_results=True, window_size=window_size * gpu_count
        )


def multiple_video_multiple_representations_encoding() -> None:
    # TODO
    pass


def store_monitoring_results(
    reset_monitoring_results: bool = False, window_size: int = 1
) -> None:
    if len(monitoring_results) > 0:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")

        result_path = f"{RESULT_ROOT}/" + "_".join(
            [
                "encoding_results",
                parallel_mode.get_abbreviation(),
                str(window_size),
                "vids",
                current_time,
                HOST_NAME,
            ]
        )
        df = pd.concat(monitoring_results)
        df.to_parquet(f"{result_path}.parquet", index=True)

        if reset_monitoring_results:
            monitoring_results.clear()
    else:
        print("no monitoring results found")


def execute_encoding_benchmark(encoding_configuration: list[EncodingConfig]) -> None:
    input_dir = INPUT_FILE_DIR
    input_files = sorted(
        [
            file
            for file in os.listdir(INPUT_FILE_DIR)
            if file.endswith(".mp4") or file.endswith(".265")
        ]
    )

    assert len(input_files) > 0, "no input files detected"

    for _ in range(TEST_REPETITIONS):
        for _, encoding_config in enumerate(encoding_configuration):
            output_files = [
                remove_media_extension(out_file) for out_file in input_files
            ]

            prepare_data_directories(encoding_config, video_names=output_files)

            if parallel_mode == ParallelMode.MULTIPLE_VIDEOS_ONE_REPRESENTATION:
                if SMALL_TESTBED:
                    reduced_multiple_video_one_representation_encoding(
                        encoding_config, input_files, input_dir
                    )
                else:
                    multiple_video_one_representation_encoding(
                        encoding_config, 1, 20, input_files, input_dir
                    )

            elif parallel_mode == ParallelMode.ONE_VIDEO_MULTIPLE_REPRESENTATIONS:
                one_video_multiple_representations_encoding(
                    encoding_config, 2, 4, input_files, input_dir
                )

            elif parallel_mode == ParallelMode.MULTIPLE_VIDEOS_MULTIPLE_REPRESENTATIONS:
                # TODO
                raise NotImplementedError("MVMR not implemented yet")
                # multiple_video_multiple_representations_encoding()

    store_monitoring_results()


def _add_mvor_monitoring_results(
    dto: EncodingConfigDTO, input_slice: list[str]
) -> None:
    result_df = hardware_tracker.to_dataframe()
    preset, codec, rendition = dto.preset, dto.codec, dto.representation
    result_df[["preset", "codec"]] = preset, codec

    framerate, segment_duration = dto.framerate, dto.segment_duration
    result_df[["framerate", "segment_duration"]] = framerate, segment_duration

    bitrate, width, height = rendition.bitrate, rendition.width, rendition.height
    result_df[["bitrate", "width", "height"]] = bitrate, width, height

    if USE_CUDA and GPU_COUNT > 0:
        result_df["use_gpu"] = True
        result_df["gpu_count"] = GPU_COUNT
        video_list = [
            f'{abbreviate_video_name(video.split("/")[-1])}_gpu:{idx % GPU_COUNT}'
            for idx, video in enumerate(input_slice)
        ]
        for idx in range(len(video_list)):
            idx_mod = idx % GPU_COUNT
            result_df[f"video_list_gpu:{idx_mod}"] = ",".join(
                [
                    video.removesuffix(f"_gpu:{idx_mod}")
                    for video in video_list
                    if f"gpu:{idx_mod}" in video
                ]
            )
    else:
        result_df["video_list"] = ",".join(
            [abbreviate_video_name(video.split("/")[-1]) for video in input_slice]
        )
    result_df["num_videos"] = len(input_slice)

    monitoring_results.append(result_df)
    hardware_tracker.clear()


def _add_ovmr_monitoring_results(
    enc_config: EncodingConfig, input_slice: list[str]
) -> None:
    assert enc_config is not None, "EncodingConfig is None"
    assert (
        len(enc_config.codecs) > 0
    ), "EncodingConfig does not contain any video codecs"
    assert len(input_slice), "list of input slices is empty"

    # base_dto: EncodingConfigDTO =
    result_df = hardware_tracker.to_dataframe()

    result_df[["codec", "preset"]] = enc_config.codecs[0], enc_config.presets[0]

    framerate, segment_duration = (
        enc_config.framerate[0],
        enc_config.segment_duration[0],
    )
    result_df[["framerate", "segment_duration"]] = framerate, segment_duration

    representations: list[str] = [
        r.get_representation_dir_string() for r in enc_config.representations
    ]

    result_df["representations"] = ",".join(representations)

    if USE_CUDA and GPU_COUNT > 0:
        result_df["use_gpu"] = True
        result_df["gpu_count"] = GPU_COUNT
        video_list = [
            f'{abbreviate_video_name(video.split("/")[-1])}_gpu:{idx % GPU_COUNT}'
            for idx, video in enumerate(input_slice)
        ]
        for idx in range(len(video_list)):
            idx_mod = idx % GPU_COUNT
            result_df[f"video_list_gpu:{idx_mod}"] = ",".join(
                [
                    video.removesuffix(f"_gpu:{idx_mod}")
                    for video in video_list
                    if f"gpu:{idx_mod}" in video
                ]
            )
    else:
        result_df["use_gpu"] = False

    monitoring_results.append(result_df)
    hardware_tracker.clear()


if __name__ == "__main__":
    Path(RESULT_ROOT).mkdir(parents=True, exist_ok=True)
    Path(f"{RESULT_ROOT}/tmp").mkdir(parents=True, exist_ok=True)

    encoding_configs: list[EncodingConfig] = [
        EncodingConfig.from_file(file_path) for file_path in ENCODING_CONFIG_PATHS
    ]

    hardware_tracker.start()

    execute_encoding_benchmark(encoding_configs)

    hardware_tracker.stop()
