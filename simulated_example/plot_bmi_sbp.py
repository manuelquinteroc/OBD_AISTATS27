# plot_bmi_sbp.py
# Make sure to run first simulate_bmi_sbp.py to generate the data files.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Load data
df_data = pd.read_csv("data/bmi_sbp_data.csv")
df_ob = pd.read_csv("data/bmi_sbp_ob.csv")

# Separate groups
group_H = df_data[df_data["group"] == "H"]  # Higher-resource settings
group_K = df_data[df_data["group"] == "K"]  # Lower-resource settings

# Get coefficients from OB table
alpha_H = df_ob.loc[df_ob["quantity"] == "alpha_H", "value"].values[0]
beta_H = df_ob.loc[df_ob["quantity"] == "beta_H", "value"].values[0]
alpha_K = df_ob.loc[df_ob["quantity"] == "alpha_K", "value"].values[0]
beta_K = df_ob.loc[df_ob["quantity"] == "beta_K", "value"].values[0]

# Set data range with padding
bmi_min = df_data["BMI"].min() - 0.5
bmi_max = df_data["BMI"].max() + 0.5
sbp_min = df_data["SBP"].min() - 5
sbp_max = df_data["SBP"].max() + 5

# Create fitted line range
x_fit = np.linspace(bmi_min, bmi_max, 200)
y_H_fit = alpha_H + beta_H * x_fit
y_K_fit = alpha_K + beta_K * x_fit

# Create single panel figure
fig, ax = plt.subplots(figsize=(8, 6))

# Color-blind friendly palette (H = orange, K = blue)
color_H = '#ff7f0e'  # Higher-resource
color_K = '#1f77b4'  # Lower-resource

# Scatter points with transparency
ax.scatter(group_H["BMI"], group_H["SBP"], alpha=0.25, color=color_H, s=20, edgecolor='none',
           label=f"Group H data")
ax.scatter(group_K["BMI"], group_K["SBP"], alpha=0.25, color=color_K, s=20, edgecolor='none',
           label=f"Group K data")

# Fitted lines
ax.plot(x_fit, y_H_fit, color=color_H, linewidth=2.5, label=f"Group H fit (β={beta_H:.2f})")
ax.plot(x_fit, y_K_fit, color=color_K, linewidth=2.5, label=f"Group K fit (β={beta_K:.2f})")

# Axis labels and limits
ax.set_xlabel("BMI (kg/m²)", fontsize=20)
ax.set_ylabel("SBP (mmHg)", fontsize=20)
ax.set_xlim(bmi_min, bmi_max)
ax.set_ylim(sbp_min, sbp_max)

# Grid
ax.grid(True, alpha=0.2)
ax.legend(fontsize=20, loc='upper left', frameon=False)
ax.tick_params(axis='both', which='major', labelsize=20)
plt.tight_layout()

# Create Figures directory if it doesn't exist
os.makedirs("Figures", exist_ok=True)

# Save as PDF
plt.savefig("Figures/bmi_sbp_comparison.pdf", format='pdf', bbox_inches='tight', dpi=300)

# Create same plot with population values rather than estimated values ----

# ----------------------------
# Population (true) lines version
# ----------------------------
from matplotlib.lines import Line2D

# True model parameters from simulate_bmi_sbp.py
alpha_H_pop = 110.4
beta_H_pop  = 1.0
alpha_K_pop = 100.0
beta_K_pop  = 1.4

# Custom legend handles (ONLY affects legend appearance)
legend_handles = [
    Line2D(
        [], [], marker='o', linestyle='None',
        markersize=10, markerfacecolor=color_H, markeredgecolor='none',
        alpha=1.0, label="Group H data"
    ),
    Line2D(
        [], [], marker='o', linestyle='None',
        markersize=10, markerfacecolor=color_K, markeredgecolor='none',
        alpha=1.0, label="Group K data"
    ),
    Line2D(
        [], [], color=color_H, linewidth=2.5,
        label=f"Group H (β={beta_H_pop:.2f})"
    ),
    Line2D(
        [], [], color=color_K, linewidth=2.5,
        label=f"Group K (β={beta_K_pop:.2f})"
    )
]

# True model parameters from simulate_bmi_sbp.py
alpha_H_pop = 110.4
beta_H_pop  = 1.0
alpha_K_pop = 100.0
beta_K_pop  = 1.4

# Create fitted line range (same x grid as before)
y_H_pop = alpha_H_pop + beta_H_pop * x_fit
y_K_pop = alpha_K_pop + beta_K_pop * x_fit

# Create single panel figure (same styling)
fig, ax = plt.subplots(figsize=(8, 6))

# Scatter points (same)
ax.scatter(group_H["BMI"], group_H["SBP"], alpha=0.25, color=color_H, s=20, edgecolor="none",
           label="Group H data")
ax.scatter(group_K["BMI"], group_K["SBP"], alpha=0.25, color=color_K, s=20, edgecolor="none",
           label="Group K data")

# Population fitted lines (true)
ax.plot(x_fit, y_H_pop, color=color_H, linewidth=2.5, label=f"Group H (β={beta_H_pop:.2f})")
ax.plot(x_fit, y_K_pop, color=color_K, linewidth=2.5, label=f"Group K (β={beta_K_pop:.2f})")

# Axis labels and limits (same)
ax.set_xlabel("BMI (kg/m²)", fontsize=20)
ax.set_ylabel("SBP (mmHg)", fontsize=20)
ax.set_xlim(bmi_min, bmi_max)
ax.set_ylim(sbp_min, sbp_max)

# Grid + legend + ticks (same)
ax.grid(True, alpha=0.2)
ax.legend(
    handles=legend_handles,
    fontsize=20,
    loc="upper left",
    frameon=False
)
ax.tick_params(axis="both", which="major", labelsize=20)
plt.tight_layout()

# Save as PDF (new filename)
plt.savefig("Figures/bmi_sbp_comparison_population.pdf", format="pdf", bbox_inches="tight", dpi=300)
