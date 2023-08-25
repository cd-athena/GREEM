from os import system
from gpu_monitoring import GpuMonitoring
from time import sleep
import subprocess

from multiprocessing import Pool

def run_command(path):
    command = f'''ffmpeg -y \
                -hwaccel cuda \
                -i opengl-rotating-triangle.mp4 \
                -r 20 \
                -vf scale=2160:-1 \
                {path}'''
    # command = f'''ffmpeg -y \
    #             -hwaccel cuda \
    #             -i opengl-rotating-triangle.mp4 \
    #             -r 20 \
    #             -vf scale=4096:-1 \
    #             opengl-rotating-triangle.gif'''
               
    subprocess.Popen(command, shell=True)



if __name__ == '__main__':
    REPETITIONS: int = 1

    monitoring = GpuMonitoring('.', 1)
    monitoring.start()
    
    # get test video with:
    # wget -O opengl-rotating-triangle.mp4 https://github.com/cirosantilli/media/blob/master/opengl-rotating-triangle.mp4?raw=true
    
    # a way to encode multiple videos at once
    # https://askubuntu.com/questions/853636/can-you-edit-multiple-videos-at-the-same-time-using-ffmpeg

    paths = [f'opengl-rotating-triangle-{idx}.gif' for idx in range(REPETITIONS)]
    pool = Pool()
    pool.map(run_command, paths)
    

    pool.join()
    pool.close()
    monitoring.stop()
    