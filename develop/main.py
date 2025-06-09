import tkinter as tk
from typing import List
from datetime import datetime
import threading
import time
from symulacja_czujnikow.temperature_sensor import TemperatureSensor
from symulacja_czujnikow.humidity_sensor import HumiditySensor
from symulacja_czujnikow.pressure_sensor import PressureSensor
from symulacja_czujnikow.light_sensor import LightSensor
from logger.logger import Logger
from komunikacja_sieciowa.siec.client import NetworkClient
from gui.main_window import SensorGUI

class MonitoringSystem:
    def __init__(self):
        self.sensors = self.initialize_sensors()
        self.logger = Logger("logger/config.json")
        self.network_client = NetworkClient(host="127.0.0.1", port=5000)
        self.running = False
        self.sensor_data = {s.sensor_id: [] for s in self.sensors}
        
    def initialize_sensors(self) -> List:
        return [
            TemperatureSensor("temp_1", "Temperatura zewnętrzna", -20, 40),
            HumiditySensor("hum_1", "Wilgotność", 0, 100),
            PressureSensor("press_1", "Ciśnienie atmosferyczne", 950, 1050),
            LightSensor("light_1", "Natężenie światła", 0, 10000)
        ]
    
    def start(self):
        self.root = tk.Tk()
        self.gui = SensorGUI(
            self.root, 
            self.sensors,
            self.start_simulation,
            self.stop_simulation
        )
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def start_simulation(self):
        if not self.running:
            self.running = True
            self.logger.start()
            self.network_client.connect()
            
            self.simulation_thread = threading.Thread(
                target=self.run_simulation,
                daemon=True
            )
            self.simulation_thread.start()
    
    def stop_simulation(self):
        self.running = False
        self.logger.stop()
        self.network_client.close()
    
    def run_simulation(self):
        while self.running:
            current_time = datetime.now()
            
            for sensor in self.sensors:
                try:
                    value = sensor.read_value()

                    self.logger.log_reading(
                        sensor.sensor_id,
                        current_time,
                        value,
                        sensor.unit
                    )
                    

                    data = {
                        "sensor_id": sensor.sensor_id,
                        "value": value,
                        "unit": sensor.unit,
                        "timestamp": current_time.isoformat()
                    }
                    self.network_client.send(data)
                    
                    # Aktualizacja danych dla wykresu
                    self.sensor_data[sensor.sensor_id].append(
                        (current_time, value)
                    )
                    if len(self.sensor_data[sensor.sensor_id]) > 100:
                        self.sensor_data[sensor.sensor_id].pop(0)
                    
                except Exception as e:
                    print(f"Błąd czujnika {sensor.sensor_id}: {str(e)}")

            self.root.after(0, self.update_gui)
            time.sleep(1)
    
    def update_gui(self):
        self.gui.update_sensor_table()
        self.gui.update_plots(self.sensor_data)
    
    def on_close(self):
        self.stop_simulation()
        self.root.destroy()

if __name__ == "__main__":
    system = MonitoringSystem()
    system.start()
