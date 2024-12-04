import numpy as np
import matplotlib.pyplot as plt

# Data for the baseline cost (y=mx) for the 4o model
x = np.linspace(0, 10, 100)  # Number of reasoning steps
baseline_cost = 2 * x  # Linear growth

# Data for the system's computational cost (exponential growth)
system_cost = np.exp(0.6 * x)  # Exponential growth representing skyrocketing costs

# Data for cost with specifically trained helper models (reduced growth)
reduced_cost = system_cost / 1.5  # Adjusted to show reduced computational load

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(x, baseline_cost, label="Baseline Cost (y=mx)", linestyle='--', color='blue')
plt.plot(x, system_cost, label="System Cost (Exponential Growth)", color='red')
plt.plot(x, reduced_cost, label="Cost with Helper Models", color='green')

# Add labels, title, and legend
plt.title("Comparative Analysis of Computational Costs", fontsize=14)
plt.xlabel("Reasoning Steps", fontsize=12)
plt.ylabel("Computational Cost", fontsize=12)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()
