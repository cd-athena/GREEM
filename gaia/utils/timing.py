from os import system
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd
from codecarbon import OfflineEmissionsTracker

import time

from gaia.utils.config import Rendition


class IdleTimeEnergyMeasurement():

    @staticmethod
    def measure_idle_energy_consumption(
        idle_time_in_seconds: float = 120,
        result_path: str = 'idle_time.csv',
        country_iso_code: str = 'AUT'
    ) -> pd.Series:
        tracker = OfflineEmissionsTracker(country_iso_code=country_iso_code)
        tracker.start()
        time.sleep(idle_time_in_seconds)
        tracker.stop()

        idle_time_series = pd.Series(
            tracker.final_emissions_data.values,
            index=tracker.final_emissions_data.values.keys()
        )

        idle_time_series['cpu_energy_per_second'] = idle_time_series['cpu_energy'] / \
            idle_time_in_seconds

        if not result_path.endswith('.csv'):
            raise Exception('CSV extension expected')
        idle_time_series.dropna(inplace=True)
        idle_time_series.to_csv(result_path)


@dataclass
class TimingMetadata():
    '''Represents the metadata for the timing of the encoding process'''
    start_time: datetime
    end_time: datetime
    elapsed_time: timedelta
    video_name: str
    codec: str
    preset: str
    rendition: Rendition
    segment_duration: int

    def to_dict(self) -> dict:
        '''Returns the metadata as a Python dictionary'''

        ret_dict: dict = {k: str(v) for k, v in asdict(
            self).items() if k != 'rendition'}
        rend_dict: dict = {
            'bitrate': self.rendition.bitrate,
            'width': self.rendition.width,
            'height': self.rendition.height
        }
        ret_dict.update(rend_dict)

        return ret_dict


def measure_time_of_system_cmd(cmd: str) -> tuple[datetime, datetime, timedelta]:
    start_time: datetime = datetime.now()
    system(cmd)
    end_time: datetime = datetime.now()

    elapsed_time: timedelta = end_time - start_time

    return start_time, end_time, elapsed_time


if __name__ == '__main__':

    # tc = measure_time_of_system_cmd('sleep 0.2')

    # tc = TimingContainer(st, et, elt, 'test_video', 'codec', 'preset', Rendition(1, 2, 3), 1)
    # tc_dict = tc.to_dict()

    # print(tc)
    IdleTimeEnergyMeasurement.measure_idle_energy_consumption(
        idle_time_in_seconds=1)
