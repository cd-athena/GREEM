from codecarbon.external.scheduler import PeriodicScheduler
from time import sleep
from codecarbon.core.util import suppress
import pandas as pd
import sys
sys.path.append("..")
from hardware import nvidia_smi_dataclasses
from dataclasses import dataclass

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
        
        self.file_stream = open(f'{monitoring_file_path}/monitoring_stream.csv', 'a')
        
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
        

    def monitor_gpu(self):
        # taken from codecarbon emission tracker
        last_measurement_time_delta = pd.Timestamp('now') - self.last_measured_time
        warning_duration = self.monitoring_interval_in_secs * 3
        # if last_measurement_time_delta > warning_duration:
        #     warn_msg = (
        #         "Background scheduler didn't run for a long period"
        #         + " (%ds), results might be inaccurate"
        #     )
        #     print(warn_msg)

        df: pd.DataFrame = self.gpu_metadata_handler.get_update_as_pandas_df()
        print(f'print df {df}')
        df.to_csv(self.file_stream)
        self.file_stream.flush()
        self.last_measured_time = pd.Timestamp('now')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb) -> None:
        self.stop()


if __name__ == '__main__':
    print('hehehe')
    monitoring = GpuMonitoring('.', 1)
    monitoring.start()
    sleep(5)

    monitoring.stop()
