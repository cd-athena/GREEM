"""
This module provides functionality for downloading files from URLs in parallel using
multi-threading. It leverages the `wget` command for downloading and utilizes
Python's multiprocessing capabilities to handle multiple downloads concurrently.
"""

import time
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from subprocess import call


def download_url(args) -> tuple[str, float]:
    """
    Downloads a file from a specified URL to a given output directory using the `wget`
    command and measures the time taken for the download.

    Args:
        args (tuple): A tuple containing two elements:
            - str: The URL of the file to be downloaded.
            - str: The output directory where the file should be saved.

    Returns:
        tuple[str, float]: A tuple containing:
            - str: The URL of the downloaded file.
            - float: The time taken to download the file in seconds. If an exception
            occurs, the time returned will be 0.

    Raises:
        Exception: If any error occurs during the download process, it is caught and
        printed.

    Example:
        download_url(("http://example.com/file.zip", "/path/to/directory"))
    """
    start_time = time.time()
    url: str = args[0]
    output: str = args[1]

    try:
        wget_call = ["wget", url, "-P", output]
        call(wget_call)
        return (url, time.time() - start_time)
    except Exception as e:
        print(f"Exception in {__name__}", e)
        return (url, 0)


def download_parallel(args) -> None:
    """
    Downloads multiple files in parallel using a thread pool, where each thread
    downloads a file from a specified URL. The number of threads is determined by
    the number of available CPU cores minus one.

    Args:
        args (list[tuple]): A list of tuples, where each tuple contains:
            - str: The URL of the file to be downloaded.
            - str: The output directory where the file should be saved.

    Returns:
        None: This function does not return any value. It prints the URL and
        download time for each file once the download is complete.

    Example:
        download_parallel([
            ("http://example.com/file1.zip", "/path/to/directory"),
            ("http://example.com/file2.zip", "/path/to/directory")
        ])
    """
    cpus = cpu_count()
    results = ThreadPool(cpus - 1).imap_unordered(download_url, args)
    for result in results:
        print(result)
