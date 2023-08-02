from pynvml import nvmlInit, nvmlDeviceGetCount
from pynvml.smi import nvidia_smi
from dataclasses import dataclass, field


@dataclass
class NvidiaGPU():

    gpu_handle: str
    memory_total: int
    memory_used: int
    memory_free: int


@dataclass
class NvidiaGPUHandler():
    '''Represents an NVIDIA GPUs on the system'''

    gpu_count: int = field(init=False)
    has_nvidia_gpu: bool = field(init=False)
    nvidia_gpus: list[NvidiaGPU] = field(init=False)
    _nvidia_smi: nvidia_smi = field(
        init=False, default_factory=nvidia_smi.getInstance())

    def __post_init__(self):
        self.has_nvidia_gpu = self.has_nvidia_gpu()
        self.gpu_count = self.get_device_count()

    def has_nvidia_gpu(self):
        '''Check if the system has an NVIDIA GPU.'''
        try:
            nvmlInit()
            return True
        except:
            return False

    def get_device_count(self):
        '''Returns the number of available NVIDIA GPUs.'''
        return nvmlDeviceGetCount()
