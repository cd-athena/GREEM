from typing import Optional

from codecarbon import OfflineEmissionsTracker
from codecarbon.emissions_tracker import BaseEmissionsTracker
from codecarbon.output import EmissionsData
from codecarbon.external.scheduler import PeriodicScheduler
from pydantic import BaseModel
from abc import ABC, abstractmethod
# from time import sleep
from os import system
from collections import deque
from dataclasses import dataclass, field
from nvitop import ResourceMetricCollector

import copy

# stolen from CodeCarbon EmissionsTracker
_sentinel = object()


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
    tracker: OfflineEmissionsTracker = None
    country_iso_code: str = 'AUT'

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
            self.tracker = OfflineEmissionsTracker(
                measure_power_secs=self.measure_power_secs,
                save_to_file=False,
                country_iso_code=self.country_iso_code)
        if self.cuda_enabled:
            pass

        # self.tracker.start()

    def flush_monitoring_data(self, delta: bool = True) -> MonitoringData:
        codecarbon_data = self.tracker._prepare_emissions_data(delta=delta)
        if self.cuda_enabled:
            # cuda_data =
            pass
        return MonitoringData(codecarbon_data)


@dataclass
class RegularMonitoring(BaseMonitoring):

    def start_monitoring(self, cmd: str):
        self.flush_monitoring_data()

        system(cmd)

        monitoring_data: MonitoringData = self.flush_monitoring_data()
        self.collected_data.append(monitoring_data)


@dataclass
class PeriodicMonitoring(BaseMonitoring):
    _scheduler: PeriodicScheduler = None

    def start_monitoring(self, cmd: str):
        self.flush_monitoring_data()  # start a new monitoring cycle

        self.start()
        system(cmd)
        self.stop()

    def __post_init__(self):
        super().__post_init__()
        self.collected_data = deque()
        self._scheduler = PeriodicScheduler(
            function=self._fetch_hardware_metrics,
            interval=self.measure_power_secs
        )

    def start(self):
        self._scheduler.start()

    def stop(self):
        self._scheduler.stop()

    def _fetch_hardware_metrics(self):
        monitoring_data: MonitoringData = self.flush_monitoring_data()

        self.collected_data.append(monitoring_data)


class MetricTracker(OfflineEmissionsTracker):
    collected_data: deque[MonitoringData] = field(default_factory=deque)
    extended_gpu_metrics: bool = False
    gpu_collector: ResourceMetricCollector = None

    def __init__(
            self,
            *args,
            country_iso_code: Optional[str] = 'AUT',
            extended_gpu_metrics: bool = False,
            measure_power_secs: float = 1,
            region: Optional[str] = _sentinel,
            cloud_provider: Optional[str] = _sentinel,
            cloud_region: Optional[str] = _sentinel,
            country_2letter_iso_code: Optional[str] = _sentinel,
            **kwargs,
    ):
        super(MetricTracker, self).__init__(
            country_iso_code=country_iso_code,
            region=region,
            cloud_provider=cloud_provider,
            cloud_region=cloud_region,
            country_2letter_iso_code=country_2letter_iso_code,
            *args,
            **kwargs,
        )

        self.collected_data = deque()
        self.measure_power_secs = measure_power_secs
        # if GPU support is enabled, initialise the nvitop.ResourceMetricCollector
        self.extended_gpu_metrics = extended_gpu_metrics
        if self.extended_gpu_metrics:
            self.gpu_collector = ResourceMetricCollector()

    def __post_init__(self):
        self._scheduler = PeriodicScheduler(
            function=self._fetch_hardware_metrics,
            interval=self.measure_power_secs
        )

    def flush(self) -> Optional[MonitoringData]:
        codecarbon_data: EmissionsData = self._tracker._prepare_emissions_data(delta=True)
        if self.extended_gpu_metrics:
            gpu_data = self.gpu_collector.collect()
            self.gpu_collector.clear()
            codecarbon_data.__dict__.update(gpu_data)

        return MonitoringData(codecarbon_data)

    def start_monitoring(self, cmd: str, tag: str = ''):
        pass

    def stop_monitoring(self, tag: str = ''):
        pass

    def _fetch_hardware_metrics(self):
        monitoring_data: MonitoringData = self.flush()
        self.collected_data.append(monitoring_data)
