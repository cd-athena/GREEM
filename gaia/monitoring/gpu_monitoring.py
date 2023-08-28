
from dataclasses import dataclass
from gaia.hardware import nvidia_smi_dataclasses
from codecarbon.external.scheduler import PeriodicScheduler
from time import sleep
from os import system
from codecarbon.core.util import suppress
import pandas as pd


@dataclass
class RunningEncoding:
    file_name: str


class GpuMonitoring:

    def __init__(self, monitoring_file_path: str, monitoring_interval_in_secs: int = 1) -> None:

        self.gpu_metadata_handler = nvidia_smi_dataclasses.NvidiaMetadataHandler.from_smi()
        self.monitoring_interval_in_secs = monitoring_interval_in_secs
        self.scheduler = PeriodicScheduler(
            function=self.monitor_gpu,
            interval=monitoring_interval_in_secs
        )

        self.file_stream = open(
            f'{monitoring_file_path}/monitoring_stream.csv', 'a')
        self.current_video: str = ''

    @suppress(Exception)
    def start(self) -> None:
        # TODO make sure that the entire gpu metadata is written to disk at least once
        # TODO make sure initial energy is read for gpu
        self.start_time = pd.Timestamp('now')
        self.last_measured_time = pd.Timestamp('now')
        self.__write_to_file('start', use_header=True)
        self.scheduler.start()

    def stop(self):
        self.last_measured_time = pd.Timestamp('now')
        self.scheduler.stop()

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
        df.to_csv(self.file_stream, header=use_header)
        self.file_stream.flush()


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
