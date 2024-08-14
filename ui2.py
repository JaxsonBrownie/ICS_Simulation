import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time

# Function to simulate getting power readings (replace this with actual data acquisition)
def get_power_reading():
    return random.uniform(100, 1000)  # Simulate power readings between 100 and 1000 Watts

class PowerMeterHMI:
    def __init__(self, root):
        self.root = root
        self.root.title("Power Meter HMI")
        self.power_readings = []
        self.max_readings = 24  # Max number of values on the graph

        # Create a label to display the current power output
        self.current_power_label = ttk.Label(root, text="Current Power: 0 Watts", font=("Arial", 14))
        self.current_power_label.pack(pady=10)

        # Create a Matplotlib figure and axis
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')
        self.ax.set_ylim(0, 1100)  # Set y-axis limit
        self.ax.set_title("Power Output (Watts)")
        self.ax.set_ylabel("Power (Watts)")
        self.ax.xaxis.set_visible(False)  # Hide x-axis label

        # Embed the plot in the tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        # Start updating the power readings and graph
        self.update_readings()

    def update_readings(self):
        # Simulate a power reading
        power = get_power_reading()
        self.power_readings.append(power)
        
        # Keep only the last `max_readings` values
        if len(self.power_readings) > self.max_readings:
            self.power_readings.pop(0)
        
        # Update the current power label
        self.current_power_label.config(text=f"Current Power: {power:.2f} Watts")
        
        # Update the graph data
        self.line.set_xdata(range(len(self.power_readings)))
        self.line.set_ydata(self.power_readings)
        self.ax.set_xlim(0, len(self.power_readings) - 1)

        # Redraw the graph
        self.canvas.draw()

        # Schedule the next update after 1 second
        self.root.after(1000, self.update_readings)

if __name__ == "__main__":
    root = tk.Tk()
    app = PowerMeterHMI(root)
    root.mainloop()
