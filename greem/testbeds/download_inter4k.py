
import os
from pathlib import Path


if __name__ == '__main__':

    # check the directory path of this file as a reference point
    cwd: str = os.path.dirname(os.path.realpath(__file__))

    # check if destination folder exists and create if not
    destination_directory: str = f'{cwd}/dataset/Inter4K/60fps/HEVC'
    Path(destination_directory).mkdir(parents=True, exist_ok=True)

    # create the rsync command to download the video files onto the system
    rsync_cmd = f'rsync -arP cbauer@gpu5.itec.aau.at:/home/itec/cbauer/GAIATools/greem/testbeds/dataset/Inter4K/60fps/HEVC/ {destination_directory}'

    # download video files
    print('start download of Inter4K raw HEVC')
    os.system(rsync_cmd)
