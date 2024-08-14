import tkinter as tk
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to simulate power meter readings
def simulate_voltage():
    return round(random.uniform(220.0, 240.0), 2)

def simulate_current():
    return round(random.uniform(10.0, 20.0), 2)

def simulate_power(voltage, current):
    return round(voltage * current, 2)

# Function to update the HMI with new readings and plot them
def update_readings():
    voltage = simulate_voltage()
    current = simulate_current()
    power = simulate_power(voltage, current)

    voltage_var.set(f"{voltage} V")
    current_var.set(f"{current} A")
    power_var.set(f"{power} W")

    # Append new data to the lists
    voltage_data.append(voltage)
    current_data.append(current)
    power_data.append(power)

    # Update the plots
    update_plots()

    # Keep the last 20 data points for plotting
    if len(voltage_data) > 20:
        voltage_data.pop(0)
        current_data.pop(0)
        power_data.pop(0)

    # Update the readings every second
    root.after(1000, update_readings)

# Function to update the matplotlib plots
def update_plots():
    # Voltage plot
    ax_voltage.clear()
    ax_voltage.plot(voltage_data, label="Voltage (V)", color="blue")
    ax_voltage.set_title("Voltage Over Time")
    ax_voltage.set_ylabel("Voltage (V)")
    ax_voltage.set_ylim(210, 250)
    ax_voltage.legend()

    # Current plot
    ax_current.clear()
    ax_current.plot(current_data, label="Current (A)", color="green")
    ax_current.set_title("Current Over Time")
    ax_current.set_ylabel("Current (A)")
    ax_current.set_ylim(0, 25)
    ax_current.legend()

    # Power plot
    ax_power.clear()
    ax_power.plot(power_data, label="Power (W)", color="red")
    ax_power.set_title("Power Over Time")
    ax_power.set_ylabel("Power (W)")
    ax_power.set_ylim(0, 5000)
    ax_power.legend()

    # Draw the updated plots on the canvas
    canvas_voltage.draw()
    canvas_current.draw()
    canvas_power.draw()

# Initialize the Tkinter root window
root = tk.Tk()
root.title("Power Meter Monitor")

# Define StringVars to hold the readings
voltage_var = tk.StringVar()
current_var = tk.StringVar()
power_var = tk.StringVar()

# Create and place labels for the readings
tk.Label(root, text="Voltage:").grid(row=0, column=0, padx=10, pady=10)
tk.Label(root, textvariable=voltage_var).grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Current:").grid(row=1, column=0, padx=10, pady=10)
tk.Label(root, textvariable=current_var).grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Power:").grid(row=2, column=0, padx=10, pady=10)
tk.Label(root, textvariable=power_var).grid(row=2, column=1, padx=10, pady=10)

# Create matplotlib figures and axes for three plots
fig_voltage, ax_voltage = plt.subplots(figsize=(5, 2))
fig_current, ax_current = plt.subplots(figsize=(5, 2))
fig_power, ax_power = plt.subplots(figsize=(5, 2))

# Create canvases to embed the plots in the Tkinter window
canvas_voltage = FigureCanvasTkAgg(fig_voltage, master=root)
canvas_voltage.get_tk_widget().grid(row=3, column=0, columnspan=2, padx=10, pady=10)

canvas_current = FigureCanvasTkAgg(fig_current, master=root)
canvas_current.get_tk_widget().grid(row=4, column=0, columnspan=2, padx=10, pady=10)

canvas_power = FigureCanvasTkAgg(fig_power, master=root)
canvas_power.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Lists to store the data for plotting
voltage_data = []
current_data = []
power_data = []

# Start the first update
update_readings()

# Run the Tkinter event loop
root.mainloop()
