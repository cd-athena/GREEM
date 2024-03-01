from codecarbon import EmissionsTracker
from codecarbon.output import EmissionsData, HTTPOutput
from codecarbon.external.scheduler import PeriodicScheduler
from pydantic import BaseModel
from abc import ABC, abstractmethod
from time import sleep
from os import system
from collections import deque
from dataclasses import dataclass, field

import copy


class MonitoringData(EmissionsData):

    def __init__(self, other):
        super(EmissionsData, self).__init__()

    def __new__(cls, other):
        if isinstance(other, EmissionsData):
            other = copy.copy(other)
            other.__class__ = MonitoringData
            return other
        return object.__new__(cls)


class MonitoringMetadata(BaseModel):
    name: str


@dataclass  # has to be a dataclass instead of BaseModel because of __post_init__ and the tracker
class BaseMonitoring(ABC):
    measure_power_secs: float = 1
    use_cuda: bool = False
    collected_data: deque[MonitoringData] = field(default_factory=deque)
    tracker: EmissionsTracker = None

    @abstractmethod
    def start_monitoring(self, cmd: str):
        pass

    # def get_emissions_tracker(self) -> EmissionsTracker:
    #     return EmissionsTracker(measure_power_secs=self.measure_power_secs, save_to_file=False)
    def __post_init__(self):
        self.tracker = EmissionsTracker(
            measure_power_secs=self.measure_power_secs, save_to_file=False)
        self.tracker.start()


@dataclass
class RegularMonitoring(BaseMonitoring):

    def start_monitoring(self, cmd: str):

        self.tracker._prepare_emissions_data(delta=True)

        if self.use_cuda:
            # TODO
            pass
        else:
            system(cmd)

            monitoring_data: MonitoringData = MonitoringData(self.tracker._prepare_emissions_data(
                delta=True))

            self.collected_data.append(monitoring_data)


@dataclass
class PeriodicMonitoring(BaseMonitoring):

    scheduler: PeriodicScheduler = None

    def start_monitoring(self, cmd: str):
        self.tracker._prepare_emissions_data()

        self.scheduler.start()
        if self.use_cuda:
            # TODO
            pass
        else:
            system(cmd)

        self.scheduler.stop()

    def __post_init__(self):
        super().__post_init__()
        self.scheduler = PeriodicScheduler(
            function=self._fetch_hardware_metrics,
            interval=self.measure_power_secs
        )

    def _fetch_hardware_metrics(self):
        monitoring_data: MonitoringData = MonitoringData(self.tracker._prepare_emissions_data(
            delta=True))

        self.collected_data.append(monitoring_data)
