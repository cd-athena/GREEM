import cv2
from dataclasses import dataclass, field
from math import ceil
import subprocess
import os


class VideoInfo():

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.video = cv2.VideoCapture(self.file_path)
        self.ffprobe_values: dict = {}

    def _get_ffprobe_values(self):
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            self.file_path,
        ]

    def get_fps(self) -> int:
        return ceil(self.video.get(cv2.CAP_PROP_FPS))

    def get_width(self) -> int:
        return ceil(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))

    def get_height(self) -> int:
        return ceil(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_total_frame_count(self) -> int:
        return ceil(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_total_duration_in_sec(self) -> float:
        return self.get_total_frame_count() / self.get_fps()

    def get_file_size_in_bytes(self) -> int:
        info = os.stat(self.file_path)
        return info.st_size


@dataclass
class VideoDTO():
    path: str
    segment_seconds: int = field(default=4)
    name: str = field(init=False)
    fps: int = field(init=False)
    width: int = field(init=False)
    height: int = field(init=False)
    total_frame_count: int = field(init=False)
    segment_element_size: int = field(init=False)
    name_abbreviation: str = field(init=False)

    def __post_init__(self):
        """
        Sets instance variable values after the `__init__` function is completed
        """
        self.name: str = self.path.split('/')[-1].split('.')[0]

        self.name_abbreviation = ''.join(
            [char for char in self.name if char.isupper()])
        video_analyser = VideoInfo(self.path)
        self.fps: int = video_analyser.get_fps()
        self.width = video_analyser.get_width()
        self.height = video_analyser.get_height()
        self.total_frame_count = video_analyser.get_total_frame_count()

        self.segment_element_size: int = self.fps * self.segment_seconds


if __name__ == '__main__':
    ancient = VideoDTO('AncientThought.webm')
    friend = VideoDTO('UnspokenFriend.webm')

    print(ancient)
    print(friend)

    input_file_name = ancient.path

    test = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format', '-show_streams',
        input_file_name,
    ]

    # print(shlex.split(f'ffprobe -i {input_file_name}'))
    data = subprocess.Popen(test, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True)
    out, err = data.communicate()

    print(out)
    # data = subprocess.run(shlex.split(
    #     f'ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate {input_file_name}'), stdout=subprocess.PIPE)

    # data = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

    # print(f'\n\n\n{data.stdout}')
    # print(len(data.stdout))
