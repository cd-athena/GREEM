from os import system
import copy
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import OrderedDict
from codecarbon import OfflineEmissionsTracker
from codecarbon.output import EmissionsData
from codecarbon.external.scheduler import PeriodicScheduler
from nvitop import ResourceMetricCollector

import pandas as pd


class MonitoringData(EmissionsData):
    """Container that contains data fetched from hardware resources.

    Contains CodeCarbon EmissionsData, but also additional measurements from nvitop.
    """

    def __init__(self, other):
        super(EmissionsData, self).__init__()

    def __new__(cls, other):
        if isinstance(other, EmissionsData):
            other = copy.copy(other)
            other.__class__ = MonitoringData
            return other
        return object.__new__(cls)

    def as_dict(self) -> OrderedDict:
        return self.values


@dataclass  # has to be a dataclass instead of BaseModel because
# __post_init__ is required
class BaseMonitoring(ABC):
    measure_power_secs: float = 1
    cuda_enabled: bool = False
    tracker: OfflineEmissionsTracker = None
    country_iso_code: str = 'AUT'
    collected_data: deque[MonitoringData] = field(default_factory=deque)
    gpu_collector: ResourceMetricCollector = None

    @abstractmethod
    def monitor_process(self, cmd: str):
        pass

    def __post_init__(self):
        if self.tracker is None:
            self.tracker = OfflineEmissionsTracker(
                measure_power_secs=self.measure_power_secs,
                save_to_file=False,
                country_iso_code=self.country_iso_code)
        if self.cuda_enabled:
            self.gpu_collector = ResourceMetricCollector(
                interval=self.measure_power_secs)

        # self.tracker.start()

    def flush_monitoring_data(self, delta: bool = True) -> MonitoringData:
        codecarbon_data = self.tracker._prepare_emissions_data(delta=delta)
        if self.cuda_enabled:
            gpu_data = self.gpu_collector.collect()
            codecarbon_data.__dict__.update(gpu_data)
            self.gpu_collector.clear()
        return MonitoringData(codecarbon_data)


@dataclass
class RegularMonitoring(BaseMonitoring):

    def monitor_process(self, cmd: str):
        self.flush_monitoring_data()

        system(cmd)

        monitoring_data: MonitoringData = self.flush_monitoring_data()
        self.collected_data.append(monitoring_data)


@dataclass
class HardwareTracker(BaseMonitoring):
    """Monitoring class that fetches the hardware state with CodeCarbon and nvitop but also keeps intermediate results.
    """
    _scheduler: PeriodicScheduler = None

    def monitor_process(self, cmd: str, tag: str = 'monitoring'):

        self.start()
        self.tracker._project_name = tag
        self.flush_monitoring_data(delta=True)

        system(cmd)
        # self.stop()

    def __post_init__(self):
        super().__post_init__()
        self.collected_data = deque()
        self._scheduler = PeriodicScheduler(
            function=self._fetch_hardware_metrics,
            interval=self.measure_power_secs
        )

    def start(self):
        """Start the monitoring libraries
        """
        self.tracker.start()
        self._scheduler.start()
        if self.cuda_enabled:
            self.gpu_collector.activate(tag='')

    def stop(self):
        """Stop the monitoring libraries
        """
        self._fetch_hardware_metrics()
        self._scheduler.stop()
        self.tracker.stop()
        if self.cuda_enabled:
            self.gpu_collector.deactivate(tag='')

    def clear(self) -> None:
        """Clears the collected data and monitored value
        """
        self.collected_data.clear()
        self.flush_monitoring_data(delta=True)

    def _fetch_hardware_metrics(self):
        monitoring_data: MonitoringData = self.flush_monitoring_data(
            delta=True)
        self.collected_data.append(monitoring_data)

    def to_dataframe(self) -> pd.DataFrame:
        collected_data = self.collected_data
        if len(collected_data) == 0:
            return pd.DataFrame()

        # TODO currently only works with CodeCarbon
        return pd.DataFrame(collected_data, columns=collected_data[0].as_dict().keys())
