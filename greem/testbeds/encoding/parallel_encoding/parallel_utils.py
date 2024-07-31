import subprocess
from enum import Enum
import os
from pathlib import Path

from greem.utility.configuration_classes import EncodingConfig


class ParallelMode(Enum):
    """
    Enumeration representing different modes of parallel video processing.

    Attributes:
        ONE_VIDEO_MULTIPLE_REPRESENTATIONS (int):
            Mode where a single video is processed to produce multiple representations (e.g., different resolutions or bitrates).
        MULTIPLE_VIDEOS_ONE_REPRESENTATION (int):
            Mode where multiple videos are processed, each to produce a single representation.
        MULTIPLE_VIDEOS_MULTIPLE_REPRESENTATIONS (int):
            Mode where multiple videos are processed, each to produce multiple representations.
    """

    ONE_VIDEO_MULTIPLE_REPRESENTATIONS = 1
    MULTIPLE_VIDEOS_ONE_REPRESENTATION = 2
    MULTIPLE_VIDEOS_MULTIPLE_REPRESENTATIONS = 3

    def get_abbr(self) -> str:
        """
        Get the abbreviation for the parallel processing mode.

        Returns:
            str: A short abbreviation for the parallel processing mode.
                'ovmr' for ONE_VIDEO_MULTIPLE_REPRESENTATIONS,
                'mvor' for MULTIPLE_VIDEOS_ONE_REPRESENTATION, and
                'mvmr' for MULTIPLE_VIDEOS_MULTIPLE_REPRESENTATIONS.
        """
        if self == ParallelMode.ONE_VIDEO_MULTIPLE_REPRESENTATIONS:
            return "ovmr"
        if self == ParallelMode.MULTIPLE_VIDEOS_ONE_REPRESENTATION:
            return "mvor"

        return "mvmr"


def get_gpu_count() -> int:
    """
    Returns the number of NVIDIA GPUs installed on the system.

    This function uses the `nvidia-smi` command-line tool to determine the number of GPUs available on the system.
    It counts the lines returned by `nvidia-smi --list-gpus`, where each line corresponds to a GPU.

    Returns:
        int: The number of GPUs detected. If `nvidia-smi` is not available or an error occurs, it returns 0.

    Exceptions:
        - subprocess.CalledProcessError: Handles the case where the `nvidia-smi` command fails.
        - FileNotFoundError: Handles the case where `nvidia-smi` is not found (e.g., NVIDIA drivers or CUDA not installed).
    """
    try:
        output = subprocess.check_output(["nvidia-smi", "--list-gpus"])
        gpu_count = len(output.decode('utf-8').strip().split('\n'))
    except subprocess.CalledProcessError:
        gpu_count = 0
    except FileNotFoundError:
        gpu_count = 0
    return gpu_count

# num_gpus = get_gpu_count()

# def get_gpu_count(use_cuda: bool) -> int:
#     gpu_count: int = 0

#     if use_cuda:
#         from greem.utility.gpu_utils import NvidiaGpuUtils

#         gpu_count = NvidiaGpuUtils().gpu_count

#     return gpu_count


def prepare_data_directories(
    encoding_config: EncodingConfig, result_root: str = "results", video_names=None
) -> list[str]:
    """Used to generate all directories that are used for the video encoding

    Args:
        encoding_config (EncodingConfig): config class that contains the values that are required to generate the directories.
        result_root (str, optional): _description_. Defaults to `results`.
        video_names (list[str], optional): _description_. Defaults to list().

    Returns:
        list[str]: returns a list of all directories that were created
    """
    if video_names is None:
        video_names = []
    data_directories = encoding_config.get_all_result_directories()

    for directory in data_directories:
        directory_path: str = f"{result_root}/{directory}"
        Path(directory_path).mkdir(parents=True, exist_ok=True)

    return data_directories


def get_video_input_files(video_dir: str) -> list[str]:
    input_files: list[str] = os.listdir(video_dir)

    if len(input_files) == 0:
        raise ValueError("no video files to encode")

    return input_files


def video_cleanup(videos: list[str]) -> None:
    """
    Deletes a list of video files from the filesystem, ignoring missing files.

    This function takes a list of file paths (as strings) and removes each corresponding file from the filesystem. 
    It will ignore files that do not exist without raising an exception.

    Args:
        videos (list[str]): A list of paths to video files that need to be deleted.

    Returns:
        None
    """
    for video in videos:
        Path(video).unlink(missing_ok=True)


if __name__ == '__main__':
    num_gpu = get_gpu_count()

    print(f'Available NVIDIA GPUs: {num_gpu}')
