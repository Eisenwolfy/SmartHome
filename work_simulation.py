import random
import time
from datetime import datetime

class Simulator:
    def __init__(self, db, devices):
        self.db = db
        self.devices = devices

    def simulate_step(self):
        for device in self.devices.values():

            state = device.get_state()

            if "temperature" in state:
                device.temperature += random.uniform(-0.3, 0.3)

            if "brightness" in state:
                device.brightness = max(0, min(100, device.brightness + random.randint(-5, 5)))

            if "charge" in state:
                if device.power:
                    device.charge = max(0, device.charge - random.uniform(0.1, 0.5))
                else:
                    device.charge = min(100, device.charge + random.uniform(0.05, 0.2))

            if "co2_lvl" in state:
                device.co2_lvl += random.uniform(-10, 10)

            if "filter_life" in state:
                device.filter_life = max(0, device.filter_life - random.uniform(0.01, 0.05))

            self.db.log_device_state(device)

    def run(self, interval=5):
        while True:
            self.simulate_step()
            print("Simulated:", datetime.now())
            time.sleep(interval)
