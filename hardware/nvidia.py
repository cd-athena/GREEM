
from types import NoneType
from pynvml import (
    nvmlInit,
    nvmlDeviceGetCount,
    nvmlDeviceGetMemoryInfo,
    nvmlSystemGetDriverVersion,
    nvmlDeviceGetUtilizationRates,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetComputeRunningProcesses,
    smi
)
from dataclasses import dataclass, field

def byte_to_kilobyte(bytes: int) -> int:
    return bytes // 1028

def byte_to_megabyte(bytes: int) -> int:
    return bytes // 1028 // 1028



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
    inforom_version: dict
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

    
@dataclass
class NvidiaGPU():

    handle: str = field(init=True, default='undefinded', repr=False)
    version: str = field(init=False, default='undefined')

    memory_total: int = field(init=False, default=0)
    memory_used: int = field(init=False, default=0)
    memory_free: int = field(init=False, default=0)

    memory_utilised: float = field(init=False, default=0)
    gpu_utilised: float = field(init=False, default=0)

    def __post_init__(self):
        self.version = nvmlSystemGetDriverVersion()
        print(self.version)
        self.update_utilisation()

    def get_current_gpu_utilisation(self) -> float:
        self.update_utilisation()

        return (self.memory_reserved + self.memory_used) / self.memory_total

    def update_utilisation(self):
        memory_info = nvmlDeviceGetMemoryInfo(self.handle)
        self.memory_total = memory_info.total
        self.memory_free = memory_info.free
        self.memory_used = memory_info.used

        util = nvmlDeviceGetUtilizationRates(self.handle)
        self.memory_utilised = util.memory
        self.gpu_utilised = util.gpu


@dataclass
class NvidiaGPUHandler():
    '''Represents the NVIDIA GPUs on the system'''

    gpu_count: int = field(init=False, default=0)
    has_nvidia_gpu: bool = field(init=False)
    nvidia_gpus: list[NvidiaGPU] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.has_nvidia_gpu = self.__has_nvidia_gpu()

        if self.has_nvidia_gpu:
            self.gpu_count = nvmlDeviceGetCount()

            for idx in range(self.gpu_count):
                gpu_handle = nvmlDeviceGetHandleByIndex(idx)
                nvidia_gpu = NvidiaGPU(gpu_handle)
                self.nvidia_gpus.append(nvidia_gpu)

    def __has_nvidia_gpu(self):
        '''Check if the system has an NVIDIA GPU.'''
        try:
            nvmlInit()
            return True
        except:
            return False

    def remove_unused_gpus(self) -> list[str]:

        to_remove: list[str] = list()

        for gpu in self.nvidia_gpus:
            if len(nvmlDeviceGetComputeRunningProcesses(gpu.handle)) == 0:
                to_remove.append(gpu.handle)

        self.nvidia_gpus = [
            gpu for gpu in self.nvidia_gpus if gpu.handle not in to_remove]
        
        return to_remove


if __name__ == '__main__':

    nvsmi = smi.nvidia_smi.getInstance()
  
    results = nvsmi.DeviceQuery()
    print(results)
    gpu_handler = NvidiaGPUHandler()

    # gpu = gpu_handler.nvidia_gpus[0]
    # print(gpu.memory_total, byte_to_megabyte(gpu.memory_total))
    # gpu_handler.remove_unused_gpus()
    # print(gpu_handler)