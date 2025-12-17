# plot_signflip_region.py
# Make sure to run first simulate_bmi_sbp.py to generate the data files.

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OB_PATH = "data/bmi_sbp_ob.csv"
OUT_PDF = os.path.join("data/signflip_region.pdf")

ob = pd.read_csv(OB_PATH)

def g(key):
    return float(ob.loc[ob["quantity"] == key, "value"].values[0])

mu_H = g("mu_H")
mu_K = g("mu_K")
dmu  = g("delta_mu")
alpha_H = g("alpha_H")
beta_H  = g("beta_H")
alpha_K = g("alpha_K")
beta_K  = g("beta_K")

# Theorem notation
Delta_mu = dmu
Delta_beta = beta_H - beta_K
Delta_alpha = alpha_H - alpha_K

# Core quantities
B_hat = Delta_mu * Delta_beta
S_hat = mu_K * Delta_beta + Delta_alpha   # S = U^(H)

# Unexplained terms (correct comments)
U_H = mu_K * Delta_beta + Delta_alpha     # U^(H): unexplained with H as reference
U_K = mu_H * Delta_beta + Delta_alpha     # U^(K): unexplained with K as reference

# Plot (B, S)
fig, ax = plt.subplots(figsize=(8, 6))

B_abs = max(1.0, abs(B_hat))
S_abs = max(1.0, abs(S_hat))
B_min, B_max = -3*B_abs, 3*B_abs
S_min, S_max = -3*S_abs, 3*S_abs

B_line = np.linspace(B_min, B_max, 400)
S_zero = np.zeros_like(B_line)
S_negB = -B_line

ax.plot(B_line, S_zero, linewidth=1.5, linestyle='--', color='black', label="S = 0")
ax.plot(B_line, S_negB, linewidth=1.5, linestyle='-.', color='black', label="S = -B")

# Sign-flip band S ∈ (-B, 0)
S_lower = np.minimum(S_zero, S_negB)
S_upper = np.maximum(S_zero, S_negB)
ax.fill_between(B_line, S_lower, S_upper, alpha=0.18, color='tab:blue',
                label="Sign-flip region (S ∈ (-B, 0))")

# Example point
ax.scatter([B_hat], [S_hat], s=80, zorder=3, color='tab:red', edgecolor='white', linewidth=0.6)
ax.annotate(
    f"Example\nB={B_hat:.3f}\nS=U^(H)={S_hat:.3f}\nU^(K)={U_K:.3f}",
    xy=(B_hat, S_hat), xytext=(10, 10), textcoords="offset points",
    bbox=dict(boxstyle="round,pad=0.30", fc="white", ec="gray", alpha=0.95)
)

ax.set_xlabel("B = Δμ · Δβ")
ax.set_ylabel("S = μ_K · Δβ + Δα  (= U^(H))")
ax.set_title("OB Sign-Flip Region and Example Location")
ax.set_xlim(B_min, B_max)
ax.set_ylim(S_min, S_max)
ax.grid(True, alpha=0.25)
ax.legend(loc="best", frameon=True)

plt.tight_layout()
plt.savefig(OUT_PDF, dpi=300, format='pdf')
print(f"Saved: {OUT_PDF}")

# CLI check
print(f"B = Δμ·Δβ = {B_hat:.6f}")
print(f"S = μ_K·Δβ + Δα = {S_hat:.6f}  [= U^(H)]")
print(f"U^(H) = {U_H:.6f},  U^(K) = {U_K:.6f}")
print(f"Sign flip? {'YES' if (U_H*U_K)<0 else 'NO'}")
