import PyQt5
import matplotlib
print("Default backend:", matplotlib.get_backend()) # Print the default backend
# matplotlib.use('Qt5Agg')  # Use Qt5Agg backend [default]










import matplotlib.pyplot as plt
import numpy as np

# Define the vector
v = np.array([3, 4])

# Create the plot
plt.figure(figsize=(6, 6))
plt.quiver(0, 0, v[0], v[1], angles='xy', scale_units='xy', scale=1, color='red')

# Set limits and labels
plt.xlim(0, 5)
plt.ylim(0, 5)
plt.xlabel('x', color='red')
plt.ylabel('y', color='red')

# Add grid
plt.grid(color='red')

# Add the magnitude and angle annotations
plt.text(3.5, 2, f'Magnitude = {np.linalg.norm(v)}', fontsize=12, color='red')
plt.text(3, 4.5, f'Angle = {np.degrees(np.arctan2(v[1], v[0])):.2f}°', fontsize=12, color='red')

# Plot the graph
plt.title('Vector Representation', color='red')
plt.axhline(0, color='red', linewidth=0.5)
plt.axvline(0, color='red', linewidth=0.5)
plt.grid(color='red', linestyle='--', linewidth=0.5)

# Set ticks color
plt.xticks(color='red')
plt.yticks(color='red')

# Save the plot as an image file
plt.savefig('result.png')

# Show the plot (commented out for non-interactive environments)
plt.show()