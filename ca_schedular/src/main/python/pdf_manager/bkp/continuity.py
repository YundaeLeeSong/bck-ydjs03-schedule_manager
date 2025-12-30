import matplotlib.pyplot as plt
import numpy as np

def plot_epsilon_delta(ax, func, a, L, eps, delta, x_range):
    # Plot the function
    x_vals = np.linspace(*x_range, 400)
    y_vals = func(x_vals)
    ax.plot(x_vals, y_vals, 'b-', label=r'$f(x)$')
    
    # Plot the epsilon band
    ax.plot(x_vals, [L + eps] * len(x_vals), 'r--')
    ax.plot(x_vals, [L - eps] * len(x_vals), 'r--')
    ax.fill_between(x_vals, L - eps, L + eps, color='red', alpha=0.1)
    
    # Plot the delta interval
    ax.plot([a - delta, a - delta], [L - eps, L + eps], 'g--')
    ax.plot([a + delta, a + delta], [L - eps, L + eps], 'g--')
    ax.fill_betweenx([L - eps, L + eps], a - delta, a + delta, color='green', alpha=0.1)
    
    ax.plot(a, L, 'ko')  # Mark the point (a, L)
    ax.text(a + delta, L, r'$\delta$', fontsize=12, color='green')
    ax.text(a, L + eps, r'$\epsilon$', fontsize=12, color='red')

def plot_epsilon_delta_discontinuous(ax, func, a, eps, x_range):
    # Plot the function
    x_vals = np.linspace(*x_range, 400)
    y_vals = func(x_vals)
    ax.plot(x_vals, y_vals, 'b-', label=r'$f(x)$')
    
    # Plot the epsilon band
    ax.plot(x_vals, [eps] * len(x_vals), 'r--')
    ax.plot(x_vals, [-eps] * len(x_vals), 'r--')
    ax.fill_between(x_vals, -eps, eps, color='red', alpha=0.1)
    
    # Illustrate that delta can't be found
    ax.text(a + 0.1, eps + 1, 'No delta can\ncontain f(x)', fontsize=12, color='green')

    # Add the point at (1,0)
    ax.plot(1, 0, 'ko')  # Mark the point (1,0)

    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(1, color='black', linewidth=0.5, linestyle='--')

    ax.legend()
    ax.grid(color='gray', linestyle='--', linewidth=0.5)


# Create subplots
fig, ax = plt.subplots(1, 3, figsize=(18, 6))

# 1. Continuous and differentiable function (e.g., f(x) = x^2)
x1 = np.linspace(-2, 2, 400)
y1 = x1**2
a1, L1 = 0.5, 0.5**2
delta1 = np.sqrt(0.75) - 0.5  # Correct delta for the given epsilon
plot_epsilon_delta(ax[0], lambda x: x**2, a1, L1, 0.5, delta1, (-2, 2))
ax[0].set_title("Continuous and Differentiable")
ax[0].set_xlabel("x")
ax[0].set_ylabel("f(x)")
ax[0].legend()
ax[0].axhline(0, color='black', linewidth=0.5)
ax[0].axvline(0, color='black', linewidth=0.5)
ax[0].grid(color='gray', linestyle='--', linewidth=0.5)

# 2. Continuous but not differentiable function (e.g., f(x) = |x|)
x2 = np.linspace(-2, 2, 400)
y2 = np.abs(x2)
a2, L2 = 0, 0
plot_epsilon_delta(ax[1], np.abs, a2, L2, 0.5, 0.5, (-2, 2))
ax[1].set_title("Continuous but Not Differentiable")
ax[1].set_xlabel("x")
ax[1].set_ylabel("f(x)")
ax[1].legend()
ax[1].axhline(0, color='black', linewidth=0.5)
ax[1].axvline(0, color='black', linewidth=0.5)
ax[1].grid(color='gray', linestyle='--', linewidth=0.5)

# 3. Discontinuous function (e.g., f(x) = 1/(x-1))
x3 = np.linspace(-2, 2, 400)
y3 = np.where(x3 != 1, 1/(x3-1), np.nan)
plot_epsilon_delta_discontinuous(ax[2], lambda x: np.where(x != 1, 1/(x-1), np.nan), 1, 2, (-2, 2))
ax[2].set_ylim(-10, 10)
ax[2].set_title("Not Continuous and Not Differentiable")
ax[2].set_xlabel("x")
ax[2].set_ylabel("f(x)")
ax[2].legend()
ax[2].axhline(0, color='black', linewidth=0.5)
ax[2].axvline(1, color='black', linewidth=0.5)
ax[2].grid(color='gray', linestyle='--', linewidth=0.5)

# Show the plot
plt.tight_layout()
plt.savefig('result.png')
plt.show()
