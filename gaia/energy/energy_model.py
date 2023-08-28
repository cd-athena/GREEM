from dataclasses import dataclass, field
import psutil
from enum import Enum


class Location(Enum):
    '''Enum for storing the CO2 impact data of a location.
    
    Attributes
    ----------
    name : str
        The name of the location.

    co2_impact_in_g_per_kwh : float
        The CO2 impact of the location in g per kWh.'''
    GERMANY = 'Germany', 83
    AUSTRIA = 'Austria', 83


@dataclass
class CO2Impact():
    '''Class for storing the CO2 impact data of a location.

    Attributes
    ----------
    name : str
        The name of the location.
    
    co2_impact_in_g_per_kwh : float
        The CO2 impact of the location in g per kWh.

    Methods
    -------
    from_enum(location: Location) -> CO2Impact
        Creates a CO2Impact object from a Location enum.

    get_co2_impact_in_kg() -> float 
        Calculates the CO2 impact of the energy consumption in kg.
    
    '''

    name: str
    co2_impact_in_g_per_kwh: float

    @classmethod
    def from_enum(cls, location: Location):
        '''Creates a CO2Impact object from a Location enum.'''
        return CO2Impact(location.value[0], location.value[1])

    def get_co2_impact_in_kg(
        self,
    ) -> float:
        '''Calculates the CO2 impact of the energy consumption in kg.

        Returns
        -------
        co2_impact : float
            The CO2 impact in kg.
        '''
        return 1000 * self.co2_impact_in_g_per_kwh


@dataclass
class EnergyModel():
    '''Class for calculating the energy consumption of a device.
    
    Attributes
    ----------
    impact_in_kg : float
        The CO2 impact of the energy consumption in kg.
        
    location : Location
        The location of the device.
        
    total_cpu_cores : float
        The total number of CPU cores.
        
    co2_impact : CO2Impact
        The CO2 impact of the location.
        
    Methods
    -------
        get_cpu_energy_consumption(
            duration: float,
            cpu_utilisation: float,
            num_cpu_cores_utilised: float,
            tdp: float
        ) -> float
            
        get_total_energy_consumption(
            device_energy_consumptions: list[float]
        ) -> float

        get_co2_impact(
            total_energy_consumption: float
        ) -> float

        get_total_co2_impact(
            device_energy_consumptions: list[float]
        ) -> float

    '''

    location: Location = field(default=Location.AUSTRIA)
    total_cpu_cores: float = field(init=False)
    co2_impact: CO2Impact = field(init=False)

    def __post_init__(self):
        self.total_cpu_cores = psutil.cpu_count()
        self.co2_impact = CO2Impact.from_enum(self.location)

    def get_cpu_energy_consumption(
            self,
            duration: float,
            cpu_utilisation: float,
            num_cpu_cores_utilised: float,
            tdp: float
    ) -> float:
        '''Calculates the energy consumption of a CPU in kWh.

        Parameters
        ----------
        duration : float 
            The duration of the CPU usage in seconds.

        cpu_utilisation : float
            The CPU utilisation in percent.

        num_cpu_cores_utilised : float
            The number of CPU cores utilised.

        cpu_cores_total : float
            The total number of CPU cores.

        tdp : float
            The TDP of the CPU in Watts.

        Returns
        -------
        energy_cpu : float
            The energy consumption of the CPU in kWh.
        '''

        tdp_used: float = (tdp * num_cpu_cores_utilised /
                           self.total_cpu_cores) * (cpu_utilisation / 100)
        
        tdp_in_kw: float = tdp_used * 0.001
        duration_in_h: float = duration / 3600

        energy_cpu: float = tdp_in_kw * duration_in_h

        return energy_cpu

    def get_total_energy_consumption(
        self,
        device_energy_consumptions: list[float]
    ) -> float:
        '''Calculates the total energy consumption of all given devices in kWh.'''
        return sum(device_energy_consumptions)

    def get_co2_impact(
        self,
        total_energy_consumption: float
    ) -> float:
        '''Calculates the CO2 impact of the total energy consumption in kg.'''
        return total_energy_consumption * self.co2_impact.get_co2_impact_in_kg()

    def get_total_co2_impact(
        self,
        device_energy_consumptions: list[float]
    ) -> float:
        '''Calculates the total CO2 impact of all given devices in kg.'''
        return self.get_co2_impact(self.get_total_energy_consumption(device_energy_consumptions))
