from os import system
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import OrderedDict

from codecarbon import OfflineEmissionsTracker
from codecarbon.output import EmissionsData
from codecarbon.external.scheduler import PeriodicScheduler
from nvitop import ResourceMetricCollector

import pandas as pd


@dataclass
class NviTopData():
    nvitop_dict: dict[str, float]

    @property
    def values(self) -> OrderedDict:
        return OrderedDict(self.nvitop_dict.items())

    def update(self, data: dict[str, float]) -> None:
        self.nvitop_dict.update(data)


@dataclass  # has to be a dataclass instead of BaseModel because
# __post_init__ is required
class BaseMonitoring(ABC):
    """
    Base class for monitoring environmental and resource metrics.

    Attributes:
        measure_power_secs (float): Interval in seconds for measuring power consumption. Defaults to 1 second.
        cuda_enabled (bool): Flag indicating if CUDA is enabled for GPU monitoring. Defaults to False.
        tracker (OfflineEmissionsTracker): Instance of OfflineEmissionsTracker for tracking emissions.
        country_iso_code (str): ISO code of the country for localization of emissions data. Defaults to 'AUT' (Austria).
        collected_codecarbon_data (list[EmissionsData]): List to store collected emissions data. Defaults to an empty list.
        collected_nvitop_data (list): List to store collected NVITop data. Defaults to an empty list.
        gpu_collector (ResourceMetricCollector): Collector for GPU resource metrics.
    """
    measure_power_secs: float = 1
    cuda_enabled: bool = False
    tracker: OfflineEmissionsTracker = None
    country_iso_code: str = 'AUT'
    collected_codecarbon_data: list[EmissionsData] = field(
        default_factory=list)
    collected_nvitop_data: list = field(default_factory=list)
    gpu_collector: ResourceMetricCollector = None

    @abstractmethod
    def monitor_process(self, cmd: str):
        raise NotImplementedError('Do not use the abstract method!')

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
            self.gpu_collector.clear()
            return codecarbon_data, NviTopData(gpu_data)

        return codecarbon_data, NviTopData({})


@dataclass
class HardwareTracker(BaseMonitoring):
    """Monitoring class that fetches the hardware state 
    with CodeCarbon and nvitop but also keeps intermediate results.
    
    Attributes:
        measure_power_secs (float): Interval in seconds for measuring power consumption. Defaults to 1 second.
        cuda_enabled (bool): Flag indicating if CUDA is enabled for GPU monitoring. Defaults to False.
        tracker (OfflineEmissionsTracker): Instance of OfflineEmissionsTracker for tracking emissions.
        country_iso_code (str): ISO code of the country for localization of emissions data. Defaults to 'AUT' (Austria).
        collected_codecarbon_data (list[EmissionsData]): List to store collected emissions data. Defaults to an empty list.
        collected_nvitop_data (list): List to store collected NVITop data. Defaults to an empty list.
        gpu_collector (ResourceMetricCollector): Collector for GPU resource metrics.
    """
    _scheduler: PeriodicScheduler = None

    def monitor_process(self, cmd: str, project_name: str = 'monitoring') -> None:
        """Monitors a process that is executed in the CLI of the sytem.
        The measurement interval is defined by `measure_power_secs`

        Parameters
        ----------
        cmd : str
            The command executed in the CLI
        project_name : str, optional
            Description of the monitored process, 
            useful if many different processes are monitored in sequence, by default 'monitoring'
        """
        self.flush_monitoring_data(delta=True)
        self.tracker._project_name = project_name
        system(cmd)
        self._fetch_hardware_metrics()

    def __post_init__(self) -> None:
        super().__post_init__()
        self.collected_codecarbon_data = []
        self.collected_nvitop_data = []
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
        self._scheduler.stop()
        self.tracker.stop()
        if self.cuda_enabled:
            self.gpu_collector.deactivate()

    def clear(self) -> None:
        """Clears the collected data and monitored value
        """
        self.collected_codecarbon_data.clear()
        self.collected_nvitop_data.clear()
        self.flush_monitoring_data(delta=True)

    def _fetch_hardware_metrics(self) -> None:
        emissions_data, nvitop_data = self.flush_monitoring_data(
            delta=True)
        self.collected_codecarbon_data.append(emissions_data)
        self.collected_nvitop_data.append(nvitop_data)

    def to_dataframe(self) -> pd.DataFrame:
        """Returns all collected measurements as a `pandas DataFrame`.
        
        If the `cuda_enabled` parameter is set to `True`, this also includes in-depth CUDA measurements based on `nvitop`.

        Returns
        -------
        pd.DataFrame
            The dataframe containing all measurements
        """
        collected_data: list[dict] = []

        if not self.cuda_enabled:
            collected_data = [d.values for d in self.collected_codecarbon_data]

        if self.cuda_enabled and (len(self.collected_nvitop_data) == len(self.collected_codecarbon_data)):
            max_length: int = 0
            for carbon, nvi in zip(self.collected_codecarbon_data, self.collected_nvitop_data):
                carbon_dict = carbon.values
                nvi_dict = nvi.values
                carbon_dict.update(nvi_dict)
                collected_data.append(carbon_dict)

                # used to ensure that faulty dictionaries are not included in dataframe
                if len(carbon_dict) > max_length:
                    max_length = len(carbon_dict)

            collected_data = [
                d for d in collected_data if len(d) == max_length]

        return pd.DataFrame(collected_data)
