import time
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from subprocess import call


def download_url(args):
    start_time = time.time()
    print(args)
    url, output = args[0], args[1]
    try:
        wget_call = ["wget", url, "-P", output]
        call(wget_call)
        return (url, time.time() - start_time)
    except Exception as e:
        print(f"Exception in {__name__}", e)


def download_parallel(args):
    cpus = cpu_count()
    results = ThreadPool(cpus - 1).imap_unordered(download_url, args)
    for result in results:
        print(result)