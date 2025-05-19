
import numpy as np

from base_sensor import BaseSensor
class PressureSensor(BaseSensor):
    def __init__(self, sensor_id: str = "press_1",
                 name: str = "Pressure Sensor",
                 min_value: float = 950.0,
                 max_value: float = 1050.0,
                 unit: str = "hPa",
                 frequency: float = 1.0):
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)
        self._pressure_trend = 0

    def read_value(self) -> float:
        if not self._is_active:
            raise ValueError("Sensor is not active")

        self._pressure_trend += np.random.normal(scale=0.3)
        self._pressure_trend = np.clip(self._pressure_trend, -5, 5)
        pressure = (np.random.normal(loc=1013, scale=2) + self._pressure_trend) * self._calibration_factor
        self._last_value = np.clip(pressure, self.min_value, self.max_value)
        return self._last_value
