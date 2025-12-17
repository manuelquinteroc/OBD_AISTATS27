# simulate_bmi_sbp.py
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

os.makedirs("data", exist_ok=True)

np.random.seed(20250815)
N = 5000

# 1) Simulate BMI distributions
# H = higher-resource, BMI = 25, K = lower-resource, BMI = 27
bmi_H = np.random.normal(25, 4, N)  # Group H (urban)
bmi_K = np.random.normal(27, 4, N)  # Group K (rural)

# 2) True model parameters
beta_H = 1  # Group H (urban)
beta_K = 1.4  # Group K (rural)
alpha_K = 100
alpha_H = 110.4
mu_H = bmi_H.mean()
mu_K = bmi_K.mean()

dmu = mu_H - mu_K # Δμ
delta_beta = beta_H - beta_K # Δβ
delta_alpha = alpha_H - alpha_K #Δα 

B = dmu * delta_beta # B = Δμ * Δβ

# 3) Generate SBP with noise
sigma = 5.0
sbp_H = alpha_H + beta_H * bmi_H + np.random.normal(0, sigma, N)  # Group H
sbp_K = alpha_K + beta_K * bmi_K + np.random.normal(0, sigma, N)  # Group K

# 4) Fit regressions
def fit(y, x):
    X = np.column_stack([np.ones(len(x)), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef[0], coef[1]

alpha_H_hat, beta_H_hat = fit(sbp_H, bmi_H)
alpha_K_hat, beta_K_hat = fit(sbp_K, bmi_K)

mu_H_hat = bmi_H.mean()
mu_K_hat = bmi_K.mean()
dmu_hat = mu_H_hat - mu_K_hat
db_hat = beta_H_hat - beta_K_hat
da_hat = alpha_H_hat - alpha_K_hat

# OB decomposition
E_H = dmu_hat * beta_H_hat  # Explained component using H reference
U_H = mu_K_hat * db_hat + da_hat  # Unexplained component using H reference
E_K = dmu_hat * beta_K_hat  # Explained component using K reference
U_K = mu_H_hat * db_hat + da_hat  # Unexplained component using K reference
delta_sbp = sbp_H.mean() - sbp_K.mean()
sign_flip = (U_H * U_K) < 0 # Testing if it occurs



# 5) Save results
# Save raw data
df_data = pd.DataFrame({
    "BMI": np.concatenate([bmi_H, bmi_K]),
    "SBP": np.concatenate([sbp_H, sbp_K]),
    "group": ["H"]*N + ["K"]*N
})

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

df_data.to_csv("data/bmi_sbp_data.csv", index=False)

# Save OB table
df_ob = pd.DataFrame([
    ["mu_H", mu_H_hat],
    ["mu_K", mu_K_hat],
    ["delta_mu", dmu_hat],
    ["alpha_H", alpha_H_hat],
    ["beta_H", beta_H_hat],
    ["alpha_K", alpha_K_hat],
    ["beta_K", beta_K_hat],
    ["E_H", E_H],
    ["U_H", U_H],
    ["E_K", E_K],
    ["U_K", U_K],
    ["delta_SBP", delta_sbp],
    ["sign_flip", int(sign_flip)]
], columns=["quantity", "value"])

df_ob.to_csv("data/bmi_sbp_ob.csv", index=False)

# -------------------------------------------------------
# New quantities: add counterfactual quantities 
y_h_ck = alpha_K_hat + beta_K_hat * mu_H_hat  # h counterfactual k
y_k_ch = alpha_H_hat + beta_H_hat * mu_K_hat # k counterfactual h

mu_y_h = sbp_H.mean() # outcome mean H
mu_y_k = sbp_K.mean() # outcome mean K

# Bridge coutnerfactual = y_k^h
composition_H = mu_y_h - y_k_ch  # weight is H: E[y_h] - E[y_k^h]
structure_H = y_k_ch - mu_y_k # E[y_k^h] - E[y_k]

# Bridge coutnerfactual = y_h^k
composition_K = y_h_ck - mu_y_k  # weight is K: E[y_h^k] - E[y_k]
structure_K = mu_y_h - y_h_ck #  E[y_h] - E[y_h^k]


# Four expectations: observed + counterfactuals, with math labels
fig, ax = plt.subplots(figsize=(9, 2.6))

# Baseline
xs_all = [mu_y_h, mu_y_k, y_k_ch, y_h_ck]
xmin, xmax = min(xs_all), max(xs_all)
pad = 0.06 * (xmax - xmin) if xmax > xmin else 1.0
ax.set_xlim(xmin - pad, xmax + pad)
ax.axhline(0, linewidth=1, color="black", zorder=1)

# Observed means: black filled circles + vertical dashed lines
ax.plot([mu_y_h, mu_y_k], [0, 0], "o", color="black", zorder=3)
for x in [mu_y_h, mu_y_k]:
    ax.axvline(x, color="black", linestyle="--", linewidth=1)

# Counterfactuals: open circles
ax.plot(y_k_ch, 0, marker="o", mfc="none", mec="C1", mew=1.5, zorder=3)
ax.plot(y_h_ck, 0, marker="o", mfc="none", mec="C0", mew=1.5, zorder=3)

# E[·] labels under the line (compact placement)
label_y = -0.07
labels = [
    (mu_y_h,   r"$\mathbb{E}[Y_H]$"),
    (y_h_ck,   r"$\mathbb{E}[Y_H^{C(K)}]$"),
    (y_k_ch,   r"$\mathbb{E}[Y_K^{C(H)}]$"),
    (mu_y_k,   r"$\mathbb{E}[Y_K]$"),
]
for x, lab in labels:
    ax.text(x, label_y, lab, ha="center", va="top", zorder=3)

# Cosmetics
ax.set_ylim(-0.18, 0.18)
ax.set_yticks([])
ax.margins(x=0.02)
ax.tick_params(axis="x", pad=2)
ax.set_xlabel("Outcome level")
ax.set_title("Observed vs Counterfactual Means")

plt.tight_layout()
plt.show()


# # -----------------------------------

# # Line plot — H reference
# fig1, ax1 = plt.subplots(figsize=(9, 2.4))
# ax1.axhline(0, linewidth=1, color="black", zorder=1)

# # Points
# xs = [mu_y_h, y_k_ch, mu_y_k]
# ax1.plot(xs, [0, 0, 0], "o", zorder=3)

# # E[·] labels under the line
# label_y = -0.07
# e_labels = [
#     r"$\mathbb{E}[Y_H]$",
#     r"$\mathbb{E}[Y_K^{C(H)}]$",
#     r"$\mathbb{E}[Y_K]$",
# ]
# for x, lab in zip(xs, e_labels):
#     ax1.text(x, label_y, lab, ha="center", va="top", zorder=3)

# ax1.tick_params(axis="x", pad=2)

# # Arrow heights and colors
# y_arrow_comp = 0.09   # composition a bit higher
# y_arrow_str  = 0.05   # structure a bit lower
# y_text_comp  = 0.22
# y_text_str   = 0.16
# col_comp = "C0"
# col_str  = "C1"

# # Composition_H: E[Y_H] -> E[Y_K^{C(H)}]
# ax1.annotate(
#     "", xy=(y_k_ch, y_arrow_comp), xytext=(mu_y_h, y_arrow_comp),
#     arrowprops=dict(arrowstyle="->", linewidth=1.4, color=col_comp),
# )
# mid_comp = 0.5 * (mu_y_h + y_k_ch)
# ax1.text(mid_comp, y_text_comp, rf"$\mathrm{{Composition}}_H = {composition_H:.2f}$", ha="center", va="bottom", color=col_comp)
# # Structure_H: E[Y_K^{C(H)}] -> E[Y_K]
# ax1.annotate("", xy=(mu_y_k, y_arrow_str), xytext=(y_k_ch, y_arrow_str), arrowprops=dict(arrowstyle="->", linewidth=1.4, color=col_str),)
# mid_str = 0.5 * (y_k_ch + mu_y_k)
# ax1.text(mid_str, y_text_str, rf"$\mathrm{{Structure}}_H = {structure_H:.2f}$", ha="center", va="bottom", color=col_str)
# ax1.set_ylim(-0.14, 0.55)
# ax1.set_yticks([])
# ax1.margins(x=0.05)
# ax1.set_xlabel("Body Mass Index (BMI)")
# ax1.set_title("OB Decomposition (H Reference)")

# plt.tight_layout()
# plt.show()

# # Line plot — K reference 
# fig2, ax2 = plt.subplots(figsize=(9, 2.4))
# ax2.axhline(0, linewidth=1, color="black", zorder=1)
# xs = [mu_y_k, y_h_ck, mu_y_h]
# ax2.plot(xs, [0, 0, 0], "o", zorder=3)
# label_y = -0.07
# e_labels = [
#     r"$\mathbb{E}[Y_K]$",
#     r"$\mathbb{E}[Y_H^{C(K)}]$",
#     r"$\mathbb{E}[Y_H]$",
# ]
# for x, lab in zip(xs, e_labels): ax2.text(x, label_y, lab, ha="center", va="top", zorder=3)
# ax2.tick_params(axis="x", pad=2)

# # Arrow heights and colors (match H plot)
# y_arrow_comp = 0.09
# y_arrow_str  = 0.05
# y_text_comp  = 0.22
# y_text_str   = 0.16
# col_comp = "C0"
# col_str  = "C1"

# # Structure_K: E[Y_H] -> E[Y_H^{C(K)}]  (leftward)
# ax2.annotate("", xy=(y_h_ck, y_arrow_str), xytext=(mu_y_h, y_arrow_str), arrowprops=dict(arrowstyle="->", linewidth=1.4, color=col_str),)
# mid_str = 0.5 * (mu_y_h + y_h_ck)
# ax2.text(mid_str, y_text_str,
#          rf"$\mathrm{{Structure}}_K = {structure_K:.2f}$",
#          ha="center", va="bottom", color=col_str)

# # Composition_K: E[Y_H^{C(K)}] -> E[Y_K]  (leftward)
# ax2.annotate(
#     "", xy=(mu_y_k, y_arrow_comp), xytext=(y_h_ck, y_arrow_comp),
#     arrowprops=dict(arrowstyle="->", linewidth=1.4, color=col_comp),
# )
# mid_comp = 0.5 * (y_h_ck + mu_y_k)
# ax2.text(mid_comp, y_text_comp,
#          rf"$\mathrm{{Composition}}_K = {composition_K:.2f}$",
#          ha="center", va="bottom", color=col_comp)

# ax2.set_ylim(-0.14, 0.55)
# ax2.set_yticks([])
# ax2.margins(x=0.05)
# ax2.set_xlabel("Body Mass Index (BMI)")
# ax2.set_title("OB Decomposition (K Reference)")

# plt.tight_layout()
# plt.show()

# ---------------------------------------------
# Putting the two plots together

# Combined subplots: H on top, K below (shared x-axis)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10.5, 6.0), sharex=True, gridspec_kw={"hspace": 0.38})  # slightly tighter

# Make x-axis ticks thicker and labels bigger for both subplots
for ax in (ax1, ax2):
    ax.tick_params(axis="x", labelsize=18, width=2.5, length=8)

# Common x-limits from all four x-positions
xs_all = [mu_y_h, y_k_ch, mu_y_k, y_h_ck]
xmin, xmax = min(xs_all), max(xs_all)
pad = 0.05 * (xmax - xmin) if xmax > xmin else 1.0
exp_label_fs    = 18   # observed E[·] labels
exp_label_fs_cf = 18   # counterfactual E[·] labels

# Helper to nudge counterfactual labels inward
def place_label(ax, x, text, inward=False, fs=16):
    xmid = 0.5 * (xmin + xmax)
    dx = -8 if (inward and x > xmid) else (8 if inward else 0)   # points
    ax.annotate(text, xy=(x, 0), xycoords="data", xytext=(dx, -10), textcoords="offset points", ha="center", va="top", fontsize=fs, zorder=3)

# ---------- Top subplot: H reference ----------
ax1.axhline(0, linewidth=1, color="black", zorder=1)

# Points
xs_H = [mu_y_h, y_k_ch, mu_y_k]
ax1.plot(xs_H, [0, 0, 0], "o", color="black", zorder=3)

# E[·] labels
place_label(ax1, mu_y_h, r"$\mathbb{E}[Y_H]$", inward=False, fs=exp_label_fs)
place_label(ax1, y_k_ch, r"$\mathbb{E}[Y_K^{\mathrm{C}(H)}]$", inward=True, fs=exp_label_fs_cf)
place_label(ax1, mu_y_k, r"$\mathbb{E}[Y_K]$", inward=False, fs=exp_label_fs)

ax1.tick_params(axis="x", pad=2, labelsize=18)

# Arrows/colors
y_arrow_comp = 0.09
y_arrow_str  = 0.05
col_comp = "C0"
col_str  = "C1"

# Explained_H
ax1.annotate("", xy=(y_k_ch, y_arrow_comp), xytext=(mu_y_h, y_arrow_comp), arrowprops=dict(arrowstyle="->", linewidth=3, color=col_comp))

# Unexplained_H
ax1.annotate("", xy=(mu_y_k, y_arrow_str), xytext=(y_k_ch, y_arrow_str), arrowprops=dict(arrowstyle="->", linewidth=3, color=col_str))

ax1.set_ylim(-0.14, 0.3)
ax1.set_yticks([])
ax1.set_xlim(xmin - pad, xmax + pad)
ax1.set_title("H base reference", loc="left", fontsize=20, pad=6, fontweight="bold")

# Legend
from matplotlib.lines import Line2D
handles_h = [
    Line2D([0], [0], color=col_comp, lw=2, label=rf"Explained$_H$ = {composition_H:.2f}"),
    Line2D([0], [0], color=col_str,  lw=2, label=rf"Unexplained$_H$ = {structure_H:.2f}"),
]
ax1.legend(handles=handles_h, loc="upper left", frameon=False, fontsize=20)

# ---------- Bottom subplot: K reference ----------
ax2.axhline(0, linewidth=1, color="black", zorder=1)
xs_K = [mu_y_k, y_h_ck, mu_y_h]
ax2.plot(xs_K, [0, 0, 0], "o", color="black", zorder=3)

# E[·] labels
place_label(ax2, mu_y_k, r"$\mathbb{E}[Y_K]$", inward=False, fs=exp_label_fs)
place_label(ax2, y_h_ck, r"$\mathbb{E}[Y_H^{\mathrm{C}(K)}]$", inward=True, fs=exp_label_fs_cf)
place_label(ax2, mu_y_h, r"$\mathbb{E}[Y_H]$", inward=False, fs=exp_label_fs)

ax2.tick_params(axis="x", pad=2, labelsize=18)

# Unexplained_K
ax2.annotate("", xy=(y_h_ck, y_arrow_str), xytext=(mu_y_h, y_arrow_str), arrowprops=dict(arrowstyle="->", linewidth=3, color=col_str))

# Explained_K
ax2.annotate("", xy=(mu_y_k, y_arrow_comp), xytext=(y_h_ck, y_arrow_comp), arrowprops=dict(arrowstyle="->", linewidth=3, color=col_comp))

ax2.set_ylim(-0.14, 0.3)
ax2.set_yticks([])
ax2.set_xlim(xmin - pad, xmax + pad)
ax2.set_xlabel("Body Mass Index (BMI)", fontsize=20)
ax2.set_title("K base reference", loc="left", fontsize=20, pad=6, fontweight="bold")

# Legend
handles_k = [
    Line2D([0], [0], color=col_comp, lw=2, label=rf"Explained$_K$ = {composition_K:.2f}"),
    Line2D([0], [0], color=col_str,  lw=2, label=rf"Unexplained$_K$ = {structure_K:.2f}"),
]
ax2.legend(handles=handles_k, loc="upper left", frameon=False, fontsize=20)

# Export
import os
os.makedirs("Figures", exist_ok=True)
fig.subplots_adjust(top=0.94, bottom=0.12, left=0.08, right=0.98, hspace=0.35)
fig.set_size_inches(18, 10)
fig.savefig("Figures/counterfactual.pdf", dpi=300, format="pdf", bbox_inches="tight")
plt.show()
