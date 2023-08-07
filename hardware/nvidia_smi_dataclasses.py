from pynvml import smi
from dataclasses import dataclass
from types import NoneType

@dataclass
class NvidiaMigMode():
    # TODO
    pass

@dataclass
class NvidiaDriverModel():
    # TODO
    pass

@dataclass
class NvidiaGpuOperationMode():
    # TODO
    pass

@dataclass
class NvidiaGpuUtilisation():

    gpu_util: float
    memory_util: float
    encoder_util: float
    decoder_util: float
    unit: str
@dataclass
class NvidiaGPUTemperature():
    # TODO
    pass

@dataclass
class NvidiaGPUPowerReadings():
    # TODO 
    pass

@dataclass
class NvidiaGPUMetadata():

    id: str
    product_name: str
    product_brand: str
    display_mode: str
    display_active: str
    persistence_mode: str
    mig_mode: dict
    accounting_mode: str
    accounting_mode_buffer_size: str
    driver_model: dict
    serial: str
    uuid: str
    minor_number: str
    vbios_version: str
    multigpu_board: str
    board_id: str
    gpu_operation_mode: dict
    pci: dict
    fan_speed: int
    fan_speed_unit: str
    performance_state: str
    clocks_throttle: dict
    fb_memory_usage: dict
    bar1_memory_usage: dict
    compute_mode: str
    utilization: dict
    ecc_mode: dict
    ecc_errors: dict
    retired_pages: dict
    temperature: dict
    power_readings: dict
    # TODO create other dataclasses
    clocks: dict
    applications_clocks: dict
    default_applications_clocks: dict
    max_clocks: dict
    clock_policy: dict
    supported_clocks: list
    processes: str
    accounted_processes: NoneType

@dataclass
class NvidiaDeviceQueryMetadata():

    timestamp: str
    driver_version: str
    count: int
    gpu: list[NvidiaGPUMetadata]