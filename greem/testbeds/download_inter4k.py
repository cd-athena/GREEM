import os
from pathlib import Path
from subprocess import call
import time
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool


def download_url(args) -> tuple[str, float]:
    start_time = time.time()
    url, output = args[0], args[1]
    wget_call = ["wget", url, "-P", output]
    call(wget_call)
    return (url, time.time() - start_time)


def download_parallel(args) -> None:
    cpus = cpu_count()
    results = ThreadPool(cpus - 1).imap_unordered(download_url, args)

    for result in results:
        print(result)


if __name__ == "__main__":

    ftp_path: str = "https://ftp.itec.aau.at/datasets/Inter4K_HEVC"

    # check the directory path of this file as a reference point
    cwd: str = os.path.dirname(os.path.realpath(__file__))

    # # check if destination folder exists and create if not
    inter_4k_directory: str = f'{cwd}/dataset/Inter4K/'
    destination_directory: str = f"{cwd}/dataset/Inter4K/60fps/HEVC"
    Path(destination_directory).mkdir(parents=True, exist_ok=True)

    num_of_videos: int = 1000

    assert num_of_videos > 0 and num_of_videos <= 1000, "invalid range of videos"

    ftp_video_segments: list[tuple[str, str]] = [
        (f"{ftp_path}/{n}.265", f"{destination_directory}/")
        for n in range(1, num_of_videos + 1)
    ]

    download_parallel(ftp_video_segments)
