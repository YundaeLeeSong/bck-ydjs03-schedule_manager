import numpy as np
import matplotlib.pyplot as plt

# Define the function to be graphed (let's use a quadratic function for this example)
def f(x):
    return x**2

# Define the range for x
x = np.linspace(-5, 5, 400)

# Generate y values for the function
y = f(x)

# Define the number of points n to be used for graphing
n_values = [3, 10, 20]

# Create the plot
fig, axs = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

# Plot the function with different number of points, connected by straight lines
for i, n in enumerate(n_values):
    x_n = np.linspace(-5, 5, n)
    y_n = f(x_n)
    
    axs[i].plot(x, y, 'r', label='f(x) = x^2')
    axs[i].scatter(x_n, y_n, color='blue', zorder=5)
    axs[i].plot(x_n, y_n, 'b-', label=f'n={n}', zorder=5)  # Use '-' to connect points with straight lines
    axs[i].legend()
    axs[i].set_title(f'Graph with n = {n} points')
    axs[i].set_xlabel('x')
    axs[i].set_ylabel('f(x)')

plt.tight_layout()


# Save the plot as an image file
plt.savefig('result.png')
plt.show()
