from abc import ABC, abstractmethod
from typing import Optional
from functools import wraps
from sh_errors import DevicePowerError, InvalidValueError, DeviceError
import random
import uuid

#POWER CHECK DECORATOR
def check_power(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.power:
            raise DevicePowerError(self.name, func.__name__)
        return func(self, *args, **kwargs)
    return wrapper


#ABSTRACT CLASS
class Device(ABC):
    def __init__(self, name:str, power:bool, did:Optional[int]=None): #did stands for device id
        self.name = name
        self.power = power
        self.id = did
        #self.id = uuid.uuid4().hex


    def turn_on(self):
        self.power = True

    def turn_off(self):
        self.power = False

    def get_state(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.device_type(),
            "power": self.power,
        }

    @abstractmethod
    def device_type(self):
        pass

    @classmethod
    @abstractmethod
    def create_default(cls, index: int):
        pass

    '''def apply_mods(self, mods: dict):
        for attr, value in mods.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise AttributeError(f"{self.device_type()} has no attribute '{attr}'")'''

    def apply_mods(self, mods: dict):
        exclude = {'id', 'did', 'type', 'name'}

        for attr, value in mods.items():
            if attr in exclude:
                continue

            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise AttributeError(f"{self.device_type()} has no attribute '{attr}'")

#DEFAULT CLASSES
class SmartLamp(Device):
    def __init__(self, name:str, power:bool, brightness:int, did:Optional[int]=None):
        super().__init__(name, power, did)
        self.brightness = brightness

    @check_power
    def set_brightness(self, value):
        if not (0 <= value <= 100):
            raise InvalidValueError(self.name, "Brightness", value, "0-100")
        self.brightness = value

    def device_type(self):
        return 'lamp'

    @classmethod
    def create_default(cls, index):
        return cls(
            name = f"Lamp {index}",
            power = False,
            brightness = 50,
            did = None
        )

    def get_state(self):
        data = super().get_state()
        data['brightness'] = self.brightness
        return data

class SmartThermostat(Device):
    MIN_TEMP = 10.0  #minimum temp in the home
    MAX_TEMP = 35.0  #maximum temp in the home

    def __init__(self, name:str, power:bool, temperature: float, did:Optional[int]=None):
        super().__init__(name, power, did)
        self.temperature = temperature

    @check_power
    def set_temperature(self, temperature):
        if not (self.MIN_TEMP <= temperature <= self.MAX_TEMP):
            raise InvalidValueError(
                device_name=self.name,
                param="Temperature",
                value=temperature,
                allowed_range=f"{self.MIN_TEMP} - {self.MAX_TEMP}"
            )
        self.temperature = temperature

    def device_type(self):
        return 'thermostat'

    @classmethod
    def create_default(cls, index: int):
        return cls(
            name = f"Thermostat {index}",
            power = False,
            temperature = 20,
            did = None
        )

    def get_state(self):
        data = super().get_state()
        data['temperature'] = self.temperature
        return data

class SmartSpeaker(Device):
    def __init__(self, name:str, power:bool, volume:int, did:Optional[int]=None):
        super().__init__(name, power, did)
        self.volume = volume


    @check_power
    def set_volume(self, volume):
        if not (0 <= volume <= 100):
            raise InvalidValueError(self.name, "Volume", volume, "0-100")
        self.volume = volume

    def status(self):
        return f'{self.name} is {"ON" if self.power else "OFF"}, {self.volume}'

    def device_type(self):
        return 'speaker'

    @classmethod
    def create_default(cls, index):
        return cls(
            name = f"Speaker {index}",
            power = False,
            volume = 10,
            did = None
        )

    def get_state(self):
        data = super().get_state()
        data['volume'] = self.volume
        return data

class SmartVacuumCleaner(Device):
    def __init__(self, name:str, power:bool, charge:float, charging_station:list, did:Optional[int]=None):
        super().__init__(name, power, did)
        self.charge = charge
        self.charging_station = charging_station
        self.current_location = list(charging_station)


    #WORK IMITATION
    @check_power
    def start_cleaning(self):
        if self.charge < 10:
            raise DeviceError(self.name, "Battery too low to start cleaning! Please dock.")
        consumption = random.randint(15, 30)
        self.charge -= consumption
        if self.charge < 0: self.charge = 0
        self.current_location = [random.randint(1, 10), random.randint(1, 10)]
        print(f"{self.name}: Cleaning done. Battery: {self.charge}%. Location: {self.current_location}")

    def return_to_dock(self):
        print(f"{self.name}: Returning to base {self.charging_station}")
        self.current_location = list(self.charging_station)
        self.charge = 100
        print(f"{self.name}: Recharged to 100%.")

    def set_charge(self, new_charge):
        if not (0 <= new_charge <= 100):
            raise InvalidValueError(self.name, "Charge", new_charge, "0-100")
        self.charge = new_charge


    def set_charging_station(self, location:list):
        self.charging_station = location

    def device_type(self):
        return 'vacuum_cleaner'

    @classmethod
    def create_default(cls, index: int):
        return cls(
            name = f'Vacuum Cleaner {index}',
            power = False,
            charge = 100,
            charging_station = [0,0],
            did = None
        )

    def get_state(self):
        data = super().get_state()
        data['charge'] = self.charge
        data['charging_station'] = self.charging_station
        data['current_location'] = self.current_location
        return data


class SmartAirPurifier(Device):
    def __init__(self, name: str, power: bool, co2_lvl: float, filter_life: int = 100, did:Optional[int]=None):
        super().__init__(name, power, did)
        self.co2_lvl = co2_lvl
        self.filter_life = filter_life

    #WORK IMITATION
    @check_power
    def purify_air(self):
        if self.filter_life <= 0:
            raise DeviceError(self.name, "Filter is dead! Please replace filter.")
        self.co2_lvl -= 50
        if self.co2_lvl < 300: self.co2_lvl = 300
        self.filter_life -= 5
        print(f"{self.name}: Air purified. CO2: {self.co2_lvl}. Filter life: {self.filter_life}%")

    def replace_filter(self):
        self.filter_life = 100
        print(f"{self.name}: Filter replaced. Life: 100%")


    def device_type(self):
        return 'air_purifier'

    @classmethod
    def create_default(cls, index: int):
        return cls(
            name = f'Air Purifier {index}',
            power = False,
            filter_life = 100,
            co2_lvl = 20,
            did = None
        )

    def set_co2_lvl(self, new_lvl):
        if new_lvl < 0:
            raise InvalidValueError(self.name, "CO2 Level", new_lvl, "Positive Number")
        self.co2_lvl = new_lvl

    def get_state(self):
        data = super().get_state()
        data['co2_lvl'] = self.co2_lvl
        data['filter_life'] = self.filter_life
        return data


#SEPARATE ROOM WITH ITS OWN DEVICES
class Room:
    def __init__(self, name: str):
        self.name = name
        self.devices = []

    def add_device(self, device: Device):
        self.devices.append(device)

    def turn_all_on(self):
        for device in self.devices:
            device.turn_on()

    def show_status(self):
        for device in self.devices:
            print(device.get_state())


#CREATING NEW CLASSES
class DeviceFactory:
    registry = {
        "lamp": SmartLamp,
        "speaker": SmartSpeaker,
        "thermostat": SmartThermostat,
        "vacuum": SmartVacuumCleaner,
        "vacuum_cleaner": SmartVacuumCleaner,
        "purifier": SmartAirPurifier,
        "air_purifier": SmartAirPurifier
    }

    @classmethod
    def create(cls, device_type, index, mods=None):
        if device_type not in cls.registry:
            raise ValueError(f"Unknown device type: {device_type}")

        device = cls.registry[device_type].create_default(index)

        if mods:
            device.apply_mods(mods)

        if mods and 'name' in mods:
            device.name = mods['name']
        elif not getattr(device, 'name', None):
            device.name = f"{device_type.capitalize()} {index}"


        return device
