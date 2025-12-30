import matplotlib.pyplot as plt
import numpy as np

# Function to calculate f(x)
def f(x):
    return x**2

# Function to calculate the secant line slope
def secant_slope(a, h):
    return (f(a + h) - f(a)) / h

# Function to calculate the secant line
def secant_line(a, h, x):
    slope = secant_slope(a, h)
    return f(a) + slope * (x - a)

# Function to calculate the tangent line
def tangent_line(a, x):
    slope = 2 * a
    return f(a) + slope * (x - a)

# Values for the function plot
x_vals = np.linspace(0, 2, 400)
y_vals = f(x_vals)

# Point of tangency
a = 1

# Secant line distances
h_vals = [1.0, 0.5, 0.1, 0.01]

plt.figure(figsize=(12, 8))

# Plot the function
plt.plot(x_vals, y_vals, label='$f(x) = x^2$', color='blue')

# Plot the point of tangency
plt.scatter([a], [f(a)], color='red')
plt.text(a, f(a), '  A (a, f(a))', verticalalignment='bottom')

# Plot the secant lines for different h values
for h in h_vals:
    secant_y_vals = secant_line(a, h, x_vals)
    plt.plot(x_vals, secant_y_vals, label=f'Secant line (h={h})', linestyle='--', color='lightgreen')
    plt.scatter([a + h], [f(a + h)], color='lightgreen')
    plt.text(a + h, f(a + h), f'  B (a+h, f(a+h)) (h={h})', verticalalignment='bottom')

# Plot the tangent line
tangent_y_vals = tangent_line(a, x_vals)
plt.plot(x_vals, tangent_y_vals, label='Tangent line', linestyle='-', color='red')

# Add labels and legend
plt.xlabel('x')
plt.ylabel('y')
plt.title('Transition from Secant Line to Tangent Line')
plt.legend()
plt.grid(True)
plt.axhline(0, color='black',linewidth=0.5)
plt.axvline(0, color='black',linewidth=0.5)


# Show the plot
plt.tight_layout()
plt.savefig('result.png')
plt.show()
