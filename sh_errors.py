#ABSTRACT CLASS FOR ERRORS
class SmartHomeError(Exception):
    pass

#DEVICE ERRORS
class DeviceError(SmartHomeError):
    def __init__(self, device_name, message):
        self.device_name = device_name
        self.message = f"Device '{device_name}': {message}"
        super().__init__(self.message)

class DevicePowerError(DeviceError):
    def __init__(self, device_name, action):
        super().__init__(device_name, f"Cannot perform '{action}' because device is OFF.")

class InvalidValueError(DeviceError):
    def __init__(self, device_name, param, value, allowed_range):
        msg = f"Invalid value '{value}' for {param}. Allowed: {allowed_range}."
        super().__init__(device_name, msg)

#DB ERRORS
class DatabaseError(SmartHomeError):
    pass