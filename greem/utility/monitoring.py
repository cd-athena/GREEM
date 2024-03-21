from codecarbon import EmissionsTracker
from codecarbon.output import EmissionsData
from codecarbon.external.scheduler import PeriodicScheduler
from pydantic import BaseModel
from abc import ABC, abstractmethod
# from time import sleep
from os import system
from collections import deque
from dataclasses import dataclass, field

import copy

# from greem.utility.cli_parser import CUDA_ENC_FLAG


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


@dataclass  # has to be a dataclass instead of BaseModel because
# __post_init__ is required
class BaseMonitoring(ABC):
    measure_power_secs: float = 1
    cuda_enabled: bool = False
    collected_data: deque[MonitoringData] = field(default_factory=deque)
    tracker: EmissionsTracker = None

    @abstractmethod
    def start_monitoring(self, cmd: str):
        pass

    # @abstractmethod
    # def stop_monitoring(self):
    #     pass

    # def get_emissions_tracker(self) -> EmissionsTracker:
    #     return EmissionsTracker(measure_power_secs=self.measure_power_secs, save_to_file=False)
    def __post_init__(self):
        if self.tracker is None:
            self.tracker = EmissionsTracker(
                measure_power_secs=self.measure_power_secs, save_to_file=False)
        self.tracker.start()


@dataclass
class RegularMonitoring(BaseMonitoring):

    def start_monitoring(self, cmd: str):

        self.tracker._prepare_emissions_data(delta=True)

        if self.cuda_enabled:
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
        if self.cuda_enabled:
            # TODO
            pass
        else:
            system(cmd)

        self.scheduler.stop()

    def __post_init__(self):
        super().__post_init__()
        self.collected_data = []
        self.scheduler = PeriodicScheduler(
            function=self._fetch_hardware_metrics,
            interval=self.measure_power_secs
        )

    def _fetch_hardware_metrics(self):
        monitoring_data: MonitoringData = MonitoringData(self.tracker._prepare_emissions_data(
            delta=True))

        self.collected_data.append(monitoring_data)
