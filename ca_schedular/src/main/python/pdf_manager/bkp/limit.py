import numpy as np
import matplotlib.pyplot as plt

# Define the range of angles for one full circle
theta = np.linspace(-2 * np.pi, 2 * np.pi, 400)

# Calculate the corresponding values for sin(x), tan(x), and x
sin_values = np.sin(theta)
tan_values = np.tan(theta)
x_values = theta

# Create the plot
plt.figure(figsize=(10, 6))

# Plot the unit circle
circle = plt.Circle((0, 0), 1, color='lightgrey', fill=False, linestyle='dotted')
ax = plt.gca()
ax.add_patch(circle)
ax.set_aspect('equal', 'box')

# Plot sin(x)
plt.plot(theta, sin_values, label='$\\sin(x)$', color='blue')

# Plot tan(x) (limiting the range to avoid large values)
plt.plot(theta, tan_values, label='$\\tan(x)$', color='red', linestyle='--')

# Plot x
plt.plot(theta, x_values, label='$x$', color='green', linestyle='-.')

# Set plot limits
plt.xlim(-np.pi/2.0, np.pi/2.0)
plt.ylim(-2, 2)

# Add labels at x = 1
x = 1
sin_label_y = np.sin(x)
tan_label_y = np.tan(x)
x_label_y = x

plt.text(x, sin_label_y, '$\\sin(x)$', color='blue', ha='left', va='top')
plt.text(x, tan_label_y, '$\\tan(x)$', color='red', ha='left', va='top')
plt.text(x, x_label_y, '$x$', color='green', ha='left', va='top')

# Add title and labels
plt.title('Comparison of $x$, $\\sin(x)$, and $\\tan(x)$')
plt.xlabel('$x$ (radians)')
plt.ylabel('Values')
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.grid(color='gray', linestyle='--', linewidth=0.5)

# Add a legend
plt.legend()

# Show the plot
plt.show()
