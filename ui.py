import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random

class PowerMeterHMI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Power Meter HMI")
        self.geometry("800x600")

        # Initialize power output label
        self.power_output_var = tk.StringVar()
        self.power_output_label = ttk.Label(self, textvariable=self.power_output_var, font=("Helvetica", 24))
        self.power_output_label.pack(pady=20)

        # Initialize the matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.ax.set_title("Power Output Over 24 Hours")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Power (Watts)")
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        self.ax.grid(True)

        # Create canvas to embed matplotlib figure
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize data
        self.times = [datetime.now() - timedelta(hours=i) for i in range(24)]
        self.times.reverse()
        self.power_data = [random.uniform(100, 500) for _ in range(24)]  # Random initial power data

        # Plot initial data
        self.line, = self.ax.plot(self.times, self.power_data, color='blue')
        self.canvas.draw()

        # Start the data update loop
        self.update_data()

    def update_data(self):
        # Simulate new power reading
        new_power_reading = random.uniform(100, 500)  # Replace with actual data source
        current_time = datetime.now()

        # Update power output label
        self.power_output_var.set(f"Power Output: {new_power_reading:.2f} Watts")

        # Append new data and remove the oldest
        self.times.append(current_time)
        self.power_data.append(new_power_reading)
        self.times = self.times[-24:]
        self.power_data = self.power_data[-24:]

        # Update plot
        self.line.set_xdata(self.times)
        self.line.set_ydata(self.power_data)

        # Update x-axis limits to reflect the new time range
        self.ax.set_xlim([self.times[0], self.times[-1]])
        self.ax.set_ylim([min(self.power_data) * 0.9, max(self.power_data) * 1.1])

        # Adjust x-axis formatting for better readability
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        self.figure.autofmt_xdate()  # Auto-format date to avoid overlap

        # Redraw the canvas
        self.canvas.draw()

        # Schedule the next update
        self.after(500, self.update_data)

if __name__ == "__main__":
    app = PowerMeterHMI()
    app.mainloop()
