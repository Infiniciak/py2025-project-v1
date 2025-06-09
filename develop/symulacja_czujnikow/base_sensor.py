import abc
from datetime import datetime
from typing import Dict, Any, List, Optional


class BaseSensor(abc.ABC):
    def __init__(self, sensor_id: str, name: str, unit: str,
                 min_value: float, max_value: float, frequency: float = 1.0):
        self.sensor_id = sensor_id
        self.name = name
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.frequency = frequency
        self._is_active = True
        self._last_value: Optional[float] = None
        self._history: List[Dict[str, Any]] = []
        self._calibration_factor = 1.0

    @abc.abstractmethod
    def read_value(self) -> float:
        pass

    def get_reading(self) -> Dict[str, Any]:
        reading = {
            'sensor_id': self.sensor_id,
            'name': self.name,
            'value': self.read_value(),
            'unit': self.unit,
            'timestamp': datetime.now().isoformat()
        }
        self._history.append(reading)
        return reading

    def calibrate(self, calibration_factor: float) -> None:
        self._calibration_factor = calibration_factor

    def get_last_value(self) -> float:
        if self._last_value is None:
            self._last_value = self.read_value()
        return self._last_value * self._calibration_factor

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._history[-limit:]

    def start(self) -> None:
        self._is_active = True

    def stop(self) -> None:
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sensor_id': self.sensor_id,
            'name': self.name,
            'type': self.__class__.__name__,
            'unit': self.unit,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'frequency': self.frequency,
            'is_active': self._is_active,
            'calibration_factor': self._calibration_factor
        }

    @classmethod
    def from_dict(cls, config: Dict[str, Any]):
        sensor = cls(
            sensor_id=config['sensor_id'],
            name=config['name'],
            unit=config['unit'],
            min_value=config['min_value'],
            max_value=config['max_value'],
            frequency=config.get('frequency', 1.0)
        )
        sensor._is_active = config['is_active']
        sensor._calibration_factor = config.get('calibration_factor', 1.0)
        return sensor

    def __str__(self):
        return f"Sensor(id={self.sensor_id}, name={self.name}, unit={self.unit}, active={self._is_active})"
