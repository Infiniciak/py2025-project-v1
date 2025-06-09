import numpy as np

from datetime import datetime

from symulacja_czujnikow.base_sensor import BaseSensor
class LightSensor(BaseSensor):
    def __init__(self, sensor_id: str = "light_1",
                 name: str = "Light Sensor",
                 min_value: float = 0.0,
                 max_value: float = 10000.0,
                 unit: str = "lux",
                 frequency: float = 1.0):
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)

    def read_value(self) -> float:
        if not self._is_active:
            raise ValueError("Sensor is not active")

        hour = datetime.now().hour
        if 6 <= hour < 18:
            base_light = np.random.normal(loc=8000, scale=2000)
            variation = 2000 * np.sin(2 * np.pi * (hour - 6) / 12)
        else:
            base_light = np.random.normal(loc=100, scale=50)
            variation = 0

        light = (base_light + variation) * self._calibration_factor
        self._last_value = np.clip(light, self.min_value, self.max_value)
        return self._last_value