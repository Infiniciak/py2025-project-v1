import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Callable
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SensorGUI:
    def __init__(self, master, sensors: List, start_callback: Callable, stop_callback: Callable):
        self.master = master
        self.sensors = sensors
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        
        master.title("System Monitoringu Czujników")
        master.geometry("1000x700")
        
        self.create_widgets()
        self.setup_plots()
        
    def create_widgets(self):
        control_frame = ttk.LabelFrame(self.master, text="Sterowanie", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Start", command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop", command=self.stop_simulation).pack(side=tk.LEFT, padx=5)
        
        sensor_frame = ttk.LabelFrame(self.master, text="Czujniki", padding=10)
        sensor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(sensor_frame, columns=('ID', 'Nazwa', 'Wartość', 'Jednostka', 'Status'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nazwa', text='Nazwa')
        self.tree.heading('Wartość', text='Wartość')
        self.tree.heading('Jednostka', text='Jednostka')
        self.tree.heading('Status', text='Status')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        plot_frame = ttk.LabelFrame(self.master, text="Wykresy", padding=10)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.figure = plt.Figure(figsize=(10, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_sensor_table()
        
    def setup_plots(self):
        self.ax.clear()
        self.ax.set_title('Odczyty czujników w czasie')
        self.ax.set_xlabel('Czas')
        self.ax.set_ylabel('Wartość')
        self.ax.grid(True)
        self.canvas.draw()
        
    def update_sensor_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for sensor in self.sensors:
            status = "Aktywny" if sensor.is_active else "Zatrzymany"
            self.tree.insert('', 'end', values=(
                sensor.sensor_id,
                sensor.name,
                f"{sensor.get_last_value():.2f}",
                sensor.unit,
                status
            ))
    
    def update_plots(self, sensor_data: Dict):
        self.ax.clear()
        for sensor_id, values in sensor_data.items():
            timestamps = [v[0] for v in values]
            data_points = [v[1] for v in values]
            self.ax.plot(timestamps, data_points, label=sensor_id)
        
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()
    
    def start_simulation(self):
        try:
            self.start_callback()
            messagebox.showinfo("Sukces", "Symulacja rozpoczęta")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się uruchomić: {str(e)}")
    
    def stop_simulation(self):
        self.stop_callback()
        messagebox.showinfo("Informacja", "Symulacja zatrzymana")
    
    def show_error(self, message: str):
        messagebox.showerror("Błąd", message)
