
import numpy as np

from datetime import datetime
from base_sensor import BaseSensor

class HumiditySensor(BaseSensor):
    def __init__(self, sensor_id: str = "hum_1",
                 name: str = "Humidity Sensor",
                 min_value: float = 20.0,
                 max_value: float = 100.0,
                 unit: str = "%",
                 frequency: float = 1.0):
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)

    def read_value(self) -> float:
        if not self._is_active:
            raise ValueError("Sensor is not active")

        hour = datetime.now().hour
        daily_pattern = 15 * np.sin(2 * np.pi * (hour - 6) / 24)
        humidity = (np.random.normal(loc=60, scale=5) + daily_pattern) * self._calibration_factor
        self._last_value = np.clip(humidity, self.min_value, self.max_value)
        return self._last_value
