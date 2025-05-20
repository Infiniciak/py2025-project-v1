import pytest
from temperature_sensor import TemperatureSensor
from humidity_sensor import HumiditySensor
from pressure_sensor import PressureSensor

def test_temperature_sensor_initialization():
    sensor = TemperatureSensor()
    assert sensor.name == "Temperature Sensor"
    assert sensor.min_value == -20.0
    assert sensor.max_value == 50.0
    assert sensor.unit == "°C"
    assert sensor.is_active

def test_humidity_sensor_reading():
    sensor = HumiditySensor()
    reading = sensor.read_value()
    assert 20.0 <= reading <= 100.0

def test_pressure_sensor_toggle():
    sensor = PressureSensor()
    assert sensor.is_active
    sensor.stop()
    assert not sensor.is_active
    sensor.start()
    assert sensor.is_active

def test_sensor_reading_when_inactive():
    sensor = TemperatureSensor()
    sensor.stop()
    with pytest.raises(ValueError):
        sensor.read_value()

def test_sensor_reading_within_bounds():
    sensor = PressureSensor(min_value=1000.0, max_value=1020.0)
    for _ in range(100):
        reading = sensor.read_value()
        assert 1000.0 <= reading <= 1020.0