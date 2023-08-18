from typing import Type, ClassVar
from pynvml import smi
from dataclasses import dataclass, field
from types import NoneType
from dacite import from_dict

DISABLED_KW: str = 'Disabled'
NA_KW: str = 'N/A'

DEFAULT_UPDATE_QUERY_KEY_LIST: list[str] = [
    'uuid',
    'fan.speed',
    'memory.free',
    'memory.used',
    'utilization.gpu',
    'utilization.memory',
    'temperature.gpu',
    'temperature.memory',
    'power.draw',
    'clocks.current.graphics',
    'clocks.current.memory'
]

DEFAULT_UPDATE_QUERY_AS_STRING: str = ', '.join(DEFAULT_UPDATE_QUERY_KEY_LIST)


@dataclass
class MigMode():

    current_mm: str = field(default=DISABLED_KW)
    pending_mm: str = field(default=DISABLED_KW)


@dataclass
class DriverModel():

    current_dm: str = field(default=NA_KW)
    pending_dm: str = field(default=NA_KW)


@dataclass
class GpuOperationMode():

    current_gom: str = field(default=NA_KW)
    pending_gom: str = field(default=NA_KW)


@dataclass
class GpuUtilisation():

    gpu_util: float = field(default=0)
    memory_util: float = field(default=0)
    encoder_util: float = field(default=0)
    decoder_util: float = field(default=0)
    unit: str = field(default='%')


@dataclass
class GpuMemoryUsage():

    total: float = 0
    used: float = 0
    free: float = 0
    unit: str = 'MiB'


@dataclass
class GpuTemperature():

    gpu_temp: float = 0
    gpu_temp_max_threshold: float = 0
    gpu_temp_slow_threshold: float = 0
    unit: str = field(default='C')


@dataclass
class GpuClocks():

    graphics_clock: int = 0
    sm_clock: int = 0
    mem_clock: int = 0
    unit: 'str' = field(default='MHz')


@dataclass
class GPUPowerReadings():

    power_management: str
    power_draw: float
    power_limit: float
    default_power_limit: float
    enforced_power_limit: float
    min_power_limit: float
    max_power_limit: float
    power_state: str = field(default='P8')
    unit: str = field(default='W')


@dataclass
class NvidiaGPUMetadata():

    id: str
    product_name: str
    product_brand: str
    display_mode: str
    display_active: str
    persistence_mode: str
    mig_mode: MigMode
    accounting_mode: str
    accounting_mode_buffer_size: str
    driver_model: DriverModel
    serial: str
    uuid: str
    minor_number: str
    vbios_version: str
    multigpu_board: str
    board_id: str
    gpu_operation_mode: GpuOperationMode
    pci: dict = field(repr=False)
    fan_speed: int
    fan_speed_unit: str
    performance_state: str
    clocks_throttle: dict = field(repr=False)
    fb_memory_usage: GpuMemoryUsage = field(repr=False)
    bar1_memory_usage: dict = field(repr=False)
    compute_mode: str
    utilization: GpuUtilisation
    ecc_mode: dict = field(repr=False)
    ecc_errors: dict = field(repr=False)
    retired_pages: dict = field(repr=False)
    temperature: GpuTemperature
    power_readings: GPUPowerReadings
    clocks: GpuClocks
    applications_clocks: dict = field(repr=False)
    default_applications_clocks: dict = field(repr=False)
    max_clocks: GpuClocks
    clock_policy: dict = field(repr=False)
    supported_clocks: list = field(repr=False)
    accounted_processes: NoneType = field(repr=False)


@dataclass
class NvidiaMetadata():
    """NvidiaMetadata is the main class for retrieving Nvidia GPU information of a system.

    Returns
    -------
    `NvidiaMetadata`

    Raises
    ------
    Exception
        `update_metadata` function can raise an exception if the wrong query parameter is given.
    """

    timestamp: str
    driver_version: str
    count: int
    gpu: list[NvidiaGPUMetadata]
    nvidia_smi_instance: ClassVar[smi.nvidia_smi] = smi.nvidia_smi.getInstance()

    @classmethod
    def from_smi(cls: Type['NvidiaMetadata']) -> Type['NvidiaMetadata']:

        nvdia_smi = cls.nvidia_smi_instance
        data = nvdia_smi.DeviceQuery()

        dqm: NvidiaMetadata = from_dict(
            data_class=NvidiaMetadata, data=data)
        return dqm

    def update_metadata(
            self,
            update_query: list[str] | str = DEFAULT_UPDATE_QUERY_AS_STRING
    ) -> dict:
        if isinstance(update_query, list):
            query: str = ', '.join(update_query)
        elif isinstance(update_query, str):
            query: str = update_query
        else:
            raise Exception('wrong query data type in parameter')

        query_dict: dict = NvidiaMetadata.nvidia_smi_instance.DeviceQuery(
            query)

        for query_result in query_dict['gpu']:
            gpu_metadata = self.get_gpu_per_uuid(query_result['uuid'])
            if gpu_metadata is None:
                # TODO for now we do nothing if the UUID does not correspond to a GPU
                # Probably should even raise an exception
                print(f'GPU not found with UUID {query_result["uuid"]}')
                continue

            gpu_metadata.__dict__.update(query_result)

        return query_dict

    def get_gpu_per_uuid(self, uuid: str) -> NvidiaGPUMetadata | None:
        """Get a GPU instance based on the `uuid` provided as a parameter.

        Parameters
        ----------
        uuid : str
            A `uuid` that represents an identifier for an Nvidia GPU on the system.

        Returns
        -------
        NvidiaGPUMetadata | None
            Either returns an `NvidiaGPUMetadata` class containing the metadata of a GPU that corresponds to the `uuid` 
            or `None` if no GPU was found with the provided `uuid`
        """        
        for gpu_metadata in self.gpu:
            if gpu_metadata.uuid == uuid:
                return gpu_metadata

        return None
