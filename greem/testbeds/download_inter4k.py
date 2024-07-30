
import os
from pathlib import Path
from subprocess import call
import time
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

all_segments = [
    f'{n + 1}' for n in range(1000)
    # ("AncientThought_s0{}", 0, 36),
    # ("Basketball_s0{}", 0, 1), ("Beauty_s0{}", 0, 0),
    # ("Bosohorus_s0{}", 0, 0), ("BundNightScape_s0{}", 0, 1), ("Bunny_s0{}", 0, 1),
    # ("Busy_City_s0{}", 0, 24), ("CampfireParty_s0{}", 0, 1), ("Characters_s0{}", 0, 1),
    # ("Childs_Play_s0{}", 0, 18), ("CityAlley_s0{}", 0, 1), ("ConstructionField_s0{}", 0, 1),
    # ("Construction_s0{}", 0, 1), ("Crowd_s0{}", 0, 1), ("Dolls_s0{}", 0, 1), ("Eldorado_s0{}", 0, 35),
    # ("FlowerFocus_s0{}", 0, 1), ("FlowerKids_s0{}", 0, 1), ("Flowers_s0{}", 0, 1),
    # ("Fountains_s0{}", 0, 1), ("Fun_on_the_river_s0{}", 0, 28), ("HoneyBee_s0{}", 0, 0),
    # ("Indoor_Soccer_s0{}", 0, 49), ("Jockey_s0{}", 0, 0), ("Lake_s0{}", 0, 1), ("Library_s0{}", 0, 1),
    # ("Lifting_Off_s0{}", 0, 39), ("Maples_s0{}", 0, 1), ("Marathon_s0{}", 0, 1),
    # ("Nature_in_the_city_s0{}", 0, 28), ("Park_s0{}", 0, 1), ("RaceNight_s0{}", 0, 1),
    # ("ReadySetGo_s0{}", 0, 0), ("ResidentialBuilding_s0{}", 0, 1), ("RiverBank_s0{}", 0, 1),
    # ("Runners_s0{}", 0, 1), ("RushHour_s0{}", 0, 1), ("Scarf_s0{}", 0, 0),
    # ("Secounds_That_Count_s0{}", 0, 63), ("Skateboarding_s0{}", 0, 54), ("TallBuildings_s0{}", 0, 1),
    # ("TrafficAndBuilding_s0{}", 0, 1), ("TrafficFlow_s0{}", 0, 1), ("TreeShade_s0{}", 0, 1),
    # ("Unspoken_Friend_s0{}", 0, 50), ("Wood_s0{}", 0, 1), ("YachtRide_s0{}", 0, 0)
]

if __name__ == '__main__':

    # # check the directory path of this file as a reference point
    # cwd: str = os.path.dirname(os.path.realpath(__file__))

    # # check if destination folder exists and create if not
    # inter_4k_directory: str = f'{cwd}/dataset/Inter4K/'
    # destination_directory: str = f'{cwd}/dataset/Inter4K/60fps/HEVC'
    # Path(destination_directory).mkdir(parents=True, exist_ok=True)
    
    # os.system(f'wget --no-check-certificate https://drive.google.com/file/d/1YNdzhk0mxFln9_2MetHF1cJIsoeVCskh -o output.zip')
    
    
    # user_name: str = 'cbauer'

    # # create the rsync command to download the video files onto the system
    # rsync_cmd = f'rsync -arP {user_name}@gpu5.itec.aau.at:/home/shared/athena/GAIA/GREEM/greem/testbeds/dataset/Inter4K/60fps/HEVC {destination_directory}'

    # # download video files
    # print('start download of Inter4K raw HEVC')
    # # os.system(rsync_cmd)


    video_path_list: list[str] = list()
    for j in range(len(all_segments)):
        for file_pattern, idx_start, idx_end in [all_segments[j]]:
            for i in range(idx_start, idx_end + 1):
                in_file_full: str = "https://ftp.itec.aau.at/datasets/video-complexity/1-ref/" + file_pattern.format(
                        f'{i}.265')

                video_path_list.append(in_file_full)

    video_input_outputs: list[tuple[str, str]] = [
        (video, 'dataset/ref_265') for video in video_path_list]


    def download_url(args):
        start_time = time.time()
        print(args)
        url, output = args[0], args[1]
        try:
            wget_call = ['wget', url, '-P', output]
            call(wget_call)
            return (url, time.time() - start_time)
        except Exception as e:
            print(f'Exception in {__name__}', e)


    def download_parallel(args):
        cpus = cpu_count()
        results = ThreadPool(cpus - 1).imap_unordered(download_url, args)
        for result in results:
            print(result)


    download_parallel(video_input_outputs)
