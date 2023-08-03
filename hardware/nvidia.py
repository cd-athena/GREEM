from pynvml import (
    nvmlInit,
    nvmlDeviceGetCount,
    nvmlDeviceGetMemoryInfo,
    nvmlSystemGetDriverVersion,
    nvmlDeviceGetUtilizationRates,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetComputeRunningProcesses,


)
from dataclasses import dataclass, field


@dataclass
class NvidiaGPU():

    handle: str = field(init=True, default='undefinded')
    version: str = field(init=False, default='undefined')
    memory_total: int = field(init=False, default=0)
    memory_used: int = field(init=False, default=0)
    memory_free: int = field(init=False, default=0)
    memory_reserved: int = field(init=False, default=0)
    memory_utilised: float = field(init=False, default=0)
    gpu_utilised: float = field(init=False, default=0)

    def __post_init__(self):
        self.version = nvmlSystemGetDriverVersion()
        self.update_utilisation()

    def get_current_gpu_utilisation(self) -> float:
        self.update_utilisation()

        return (self.memory_reserved + self.memory_used) / self.memory_total

    def update_utilisation(self):
        memory_info = nvmlDeviceGetMemoryInfo(self.handle, self.version)
        self.memory_total = memory_info.total
        self.memory_free = memory_info.free
        self.memory_used = memory_info.used

        if self.version is not None:
            self.memory_reserved = memory_info.reserved

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
