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


def get_gpu_count(use_cuda: bool) -> int:
    gpu_count: int = 0

    if use_cuda:
        from greem.utility.gpu_utils import NvidiaGpuUtils

        gpu_count = NvidiaGpuUtils().gpu_count

    return gpu_count


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
    for video in videos:
        Path(video).unlink()
