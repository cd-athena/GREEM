from os import system
import copy
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import OrderedDict, Type

from attr import asdict
from codecarbon import OfflineEmissionsTracker
from codecarbon.output import EmissionsData
from codecarbon.external.scheduler import PeriodicScheduler
from nvitop import ResourceMetricCollector

import pandas as pd

@dataclass
class NviTopData():
    nvitop_dict: dict[str, float]
    
    # def __init__(self, nvitop_dict: dict[str, float]) -> None:
    #     self._nvitop_dict: OrderedDict[str, float] = OrderedDict(nvitop_dict.items())
        
    @property
    def values(self) -> OrderedDict:
        return OrderedDict(self.nvitop_dict.items())
        
    def update(self, data: dict[str, float]) -> None:
        self.nvitop_dict.update(data)
        

# class MonitoringData(EmissionsData):
#     """Container that contains data fetched from hardware resources.

#     Contains CodeCarbon EmissionsData, but also additional measurements from nvitop.
#     """

#     def __init__(self, other):
#         super(EmissionsData, self).__init__()

#     def __new__(cls, other) -> Type['MonitoringData']:
#         if isinstance(other, EmissionsData):
#             other = copy.copy(other)
#             other.__class__ = MonitoringData
#             return MonitoringData(other)
#         return object.__new__(cls)

#     def as_dict(self) -> OrderedDict:
#         return self.values


@dataclass  # has to be a dataclass instead of BaseModel because
# __post_init__ is required
class BaseMonitoring(ABC):
    measure_power_secs: float = 1
    cuda_enabled: bool = False
    tracker: OfflineEmissionsTracker = None
    country_iso_code: str = 'AUT'
    collected_codecarbon_data: deque[EmissionsData] = field(default_factory=deque)
    collected_nvitop_data: deque = field(default_factory=deque)
    gpu_collector: ResourceMetricCollector = None

    @abstractmethod
    def monitor_process(self, cmd: str):
        pass

    def __post_init__(self):
        if self.tracker is None:
            self.tracker = OfflineEmissionsTracker(
                measure_power_secs=self.measure_power_secs,
                save_to_file=False,
                country_iso_code=self.country_iso_code, 
                log_level='error',
                )
        if self.cuda_enabled:
            self.gpu_collector = ResourceMetricCollector(
                interval=self.measure_power_secs)

        # self.tracker.start()

    def flush_monitoring_data(self, delta: bool = True) -> tuple[EmissionsData, NviTopData]:
        codecarbon_data = self.tracker._prepare_emissions_data(delta=delta)
        if self.cuda_enabled:
            gpu_data = self.gpu_collector.collect()
            # codecarbon_data.__dict__.update(gpu_data)
            self.gpu_collector.clear()
            return codecarbon_data, NviTopData(gpu_data)
        
        return codecarbon_data, NviTopData({})
        # self.collected_data.append(codecarbon_data)
        # return MonitoringData(other=codecarbon_data)``


# @dataclass
# class RegularMonitoring(BaseMonitoring):

#     def monitor_process(self, cmd: str):
#         self.flush_monitoring_data()

#         system(cmd)

#         monitoring_data: MonitoringData = self.flush_monitoring_data()
#         self.collected_data.append(monitoring_data)


@dataclass
class HardwareTracker(BaseMonitoring):
    """Monitoring class that fetches the hardware state with CodeCarbon and nvitop but also keeps intermediate results.
    """
    _scheduler: PeriodicScheduler = None

    def monitor_process(self, cmd: str, project_name: str = 'monitoring'):
        self.flush_monitoring_data(delta=True)
        self.tracker._project_name = project_name
        system(cmd)
        self._fetch_hardware_metrics()

        

    def __post_init__(self) -> None:
        super().__post_init__()
        # self.collected_data = deque()
        self.collected_codecarbon_data = deque()
        self.collected_nvitop_data = deque()
        # if self.cuda_enabled:
            # self.gpu_collector = 
        self._scheduler = PeriodicScheduler(
            function=self._fetch_hardware_metrics,
            interval=self.measure_power_secs
        )
        

    def start(self) -> None:
        """Start the monitoring libraries
        """
        self.tracker.start()
        if self.cuda_enabled:
            self.gpu_collector.start(tag='nvitop')
            
        self._scheduler.start()
    

    def stop(self) -> None:
        """Stop the monitoring libraries
        """
        # self._fetch_hardware_metrics()
        self._scheduler.stop()
        self.tracker.stop()
        if self.cuda_enabled:
            self.gpu_collector.deactivate()

    def clear(self) -> None:
        """Clears the collected data and monitored value
        """
        # self.collected_data.clear()
        self.collected_codecarbon_data.clear()
        self.collected_nvitop_data.clear()
        self.flush_monitoring_data(delta=True)

    def _fetch_hardware_metrics(self) -> None:
        emissions_data, nvitop_data = self.flush_monitoring_data(
            delta=True)
        # self.collected_data.append(monitoring_data)
        self.collected_codecarbon_data.append(emissions_data)
        self.collected_nvitop_data.append(nvitop_data)

    def to_dataframe(self) -> pd.DataFrame:
        collected_data = []

        if len(self.collected_nvitop_data) == len(self.collected_codecarbon_data):
            max_length: int = 0
            for carbon, nvi in zip(self.collected_codecarbon_data, self.collected_nvitop_data):
                carbon_dict = carbon.values
                nvi_dict = nvi.values
                carbon_dict.update(nvi_dict)
                collected_data.append(carbon_dict)
                if len(carbon_dict) > max_length:
                    max_length = len(carbon_dict)
                    
            collected_data = [d for d in collected_data if len(d) == max_length]
                
            
        return pd.DataFrame(collected_data)

