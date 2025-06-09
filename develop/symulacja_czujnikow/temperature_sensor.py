
import numpy as np

from datetime import datetime

from symulacja_czujnikow.base_sensor import BaseSensor
class TemperatureSensor(BaseSensor):
    def __init__(self, sensor_id: str = "temp_1",
                 name: str = "Temperature Sensor",
                 min_value: float = -20.0,
                 max_value: float = 50.0,
                 unit: str = "°C",
                 frequency: float = 1.0):
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)
        self._trend = 0

    def read_value(self) -> float:
        if not self._is_active:
            raise ValueError("Sensor is not active")

        base_temp = np.random.normal(loc=20, scale=5)
        hour = datetime.now().hour
        daily_variation = 10 * np.sin(2 * np.pi * hour / 24)
        self._trend += np.random.normal(scale=0.1)
        self._trend = np.clip(self._trend, -5, 5)

        temp = (base_temp + daily_variation + self._trend) * self._calibration_factor
        self._last_value = np.clip(temp, self.min_value, self.max_value)
        return self._last_value