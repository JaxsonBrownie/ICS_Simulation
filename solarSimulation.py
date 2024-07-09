from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import norm

################################################################################

"""Generates a set of power (W) values to represent a solar panels efficency over 24 hours"""
def generate_norm_power(mean=12, std_dev=2, power_const=10.5, efficency=0.7, hours=24):
    # power_const of 10.5 generates generic normal for a typical 2W solar panel

    # Generate 96 time intervals over 24 hours (every 15 minutes)
    x = np.linspace(0, hours, 96)

    # Generate a normal distribution representing solar generation (provide estimated constants)
    y = norm.pdf(x, mean, std_dev)*power_const*efficency

    plt.figure(figsize=(10, 5))  # Create a figure with width 10 inches and height 5 inches
    plt.plot(x, y, label='sin(x)')
    plt.xlabel('x')
    plt.ylabel('sin(x)')
    plt.title('Plot of sin(x)')
    plt.legend()
    plt.grid(True)
    plt.show()
    return y

################################################################################

if __name__ == '__main__':
    power_generation = generate_norm_power()
    print(power_generation)