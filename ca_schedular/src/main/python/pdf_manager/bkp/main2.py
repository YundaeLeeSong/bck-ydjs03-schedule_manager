import numpy as np
import matplotlib.pyplot as plt

# Define the polynomial function
def polynomial(x):
    return x**3 - 6*x**2 + 4*x + 12

# Generate x values
x = np.linspace(-2, 6, 400)

# Compute the y values for the original and absolute valued functions
y_original = polynomial(x)
y_absolute = np.abs(y_original)

# Plot the original polynomial function (dotted line)
plt.plot(x, y_original, 'r--', label='Original Polynomial')

# Plot the absolute valued polynomial function (solid line)
plt.plot(x, y_absolute, 'b-', label='|Polynomial|')

# Add labels and title
plt.xlabel('x')
plt.ylabel('y')
plt.title('Effect of Absolute Value on a Polynomial Function')
plt.legend()

# Show the plot
plt.grid(True)

# Save the plot as an image file
plt.savefig('result.png')

# Show the plot (commented out for non-interactive environments)
plt.show()
