
from dataclasses import dataclass
from codecarbon.core.util import suppress
from codecarbon.external.scheduler import PeriodicScheduler
from time import sleep
from os import system
import pandas as pd

from gaia.hardware import nvidia_smi_dataclasses
from gaia.utils.configuration_classes import Rendition


@dataclass
class RunningEncoding:
    file_name: str


@dataclass
class BaseMonitoring:
    monitoring_file_path: str
    monitoring_interval_in_secs: float = 1

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


class CpuMonitoring(BaseMonitoring):

    def __init__(self, monitoring_file_path: str, monitoring_interval_in_secs: int):
        super().__init__(monitoring_file_path, monitoring_interval_in_secs)


class GpuMonitoring(BaseMonitoring):
    # https://stackoverflow.com/questions/8223811/a-top-like-utility-for-monitoring-cuda-activity-on-a-gpu

    def __init__(self, monitoring_file_path: str, monitoring_interval_in_secs: float) -> None:
        super().__init__(monitoring_file_path, monitoring_interval_in_secs)

        self.gpu_metadata_handler = nvidia_smi_dataclasses.NvidiaMetadataHandler.from_smi()

        self.scheduler = PeriodicScheduler(
            function=self.monitor_gpu,
            interval=self.monitoring_interval_in_secs
        )

        self.file_stream = open(
            f'{self.monitoring_file_path}/monitoring_stream.csv', 'a')
        self.current_video: str = ''
        self.rendition = Rendition.new()
        self.__write_to_file('start', use_header=True)
        self.gpu_metadata_handler.get_update_metadata()

    @suppress(Exception)
    def start(self) -> None:
        # TODO make sure that the entire gpu metadata is written to disk at least once
        # TODO make sure initial energy is read for gpu
        self.start_time = pd.Timestamp('now')
        self.last_measured_time = pd.Timestamp('now')
        self.scheduler.start()

    def stop(self):
        self.last_measured_time = pd.Timestamp('now')
        self.scheduler.stop()

    def get_utilisation(self) -> tuple[float, float]:

        # metadata = self.gpu_metadata_handler.get_update_metadata()['gpu']

        gpu_util: list[float] = list()
        mem_util: list[float] = list()

        for gpu in self.gpu_metadata_handler.gpu:
            print(gpu)

        # gpu_avg = sum(gpu_util) / len(gpu_util)
        # mem_avg = sum(mem_util) / len(mem_util)

        return 0, 0
        # return gpu_avg, mem_avg

    def monitor_gpu(self):
        last_measurement_time_delta = pd.Timestamp(
            'now') - self.last_measured_time
        self.__write_to_file(self.current_video)
        self.last_measured_time = pd.Timestamp('now')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb) -> None:
        self.stop()

    def __write_to_file(self, video_name: str, use_header: bool = False) -> None:
        df: pd.DataFrame = self.gpu_metadata_handler.get_update_as_pandas_df()
        df['current_video'] = video_name
        df['bitrate'] = self.rendition.bitrate
        df['width'] = self.rendition.width
        df['height'] = self.rendition.height
        df.to_csv(self.file_stream, header=use_header)
        self.file_stream.flush()


class HardwareMonitoring(BaseMonitoring):

    def __init__(self):
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


if __name__ == '__main__':
    REPETITIONS: int = 3

    monitoring = GpuMonitoring('.', 1)
    monitoring.start()

    # get test video with:
    # wget -O opengl-rotating-triangle.mp4 https://github.com/cirosantilli/media/blob/master/opengl-rotating-triangle.mp4?raw=true

    for i in range(REPETITIONS):

        system(
            '''ffmpeg -y \
                -hwaccel cuda \
                -i opengl-rotating-triangle.mp4 \
                -r 20 \
                -vf scale=4096:-1 \
                opengl-rotating-triangle.gif'''
        )
        sleep(1)

    monitoring.stop()
