"""
Clean figures: output pulse FWHM vs. depth in scattering tissue.
Lutomirski et al., Appl. Opt. 34, 7125 (1995).
"""

import numpy as np
import matplotlib.pyplot as plt
from temporal_broadening import make_params, compute_moments

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
})

OUTDIR = "C:/Users/arayi/Documents/analytical_calculations"

# ---------- compute ----------
p      = make_params()
z_phys = np.linspace(1e-9, 3e-3, 2000)
m      = compute_moments(z_phys, p)

sigma_p   = p["sigma_pulse"]
sigma_out = np.sqrt(sigma_p**2 + m["sigma_t"]**2)
fwhm_out  = sigma_out * 2 * np.sqrt(2 * np.log(2))

z_um     = z_phys * 1e6
z_mm     = z_phys * 1e3
fwhm_fs  = fwhm_out * 1e15
fwhm_ps  = fwhm_out * 1e12
input_fwhm_fs = p["tau_fwhm"] * 1e15
input_fwhm_ps = p["tau_fwhm"] * 1e12

subtitle = (r"$\mu_s = 4340\;\mathrm{m^{-1}}$, $g = 0.93$, $n = 1.4$"
            r"$\quad|\quad$Input FWHM = 100 fs")

# ============================================================
# Figure 1:  Zoomed in, 0 -- 300 um
# ============================================================
fig1, ax1 = plt.subplots(figsize=(5.5, 4))

mask = z_phys <= 300e-6
ax1.plot(z_um[mask], fwhm_fs[mask], "k", lw=1.8)
ax1.axhline(input_fwhm_fs, color="C3", ls="--", lw=1,
            label="Input FWHM = 100 fs")

ax1.set_xlabel(r"Depth $z$ [$\mu$m]")
ax1.set_ylabel("Output FWHM [fs]")
ax1.set_xlim(0, 300)
ax1.set_ylim(bottom=0)
ax1.legend(frameon=False)
ax1.grid(True, alpha=0.2)
ax1.set_title("Pulse FWHM vs. depth (near-surface)\n" + subtitle,
              fontsize=9)

fig1.tight_layout()
fig1.savefig(f"{OUTDIR}/fig_fwhm_zoomed.png", dpi=200)
print("Saved fig_fwhm_zoomed.png")

# ============================================================
# Figure 2:  Full range, 0 -- 3 mm
# ============================================================
fig2, ax2 = plt.subplots(figsize=(5.5, 4))

ax2.plot(z_mm, fwhm_ps, "k", lw=1.8)
ax2.axhline(input_fwhm_ps, color="C3", ls="--", lw=1,
            label="Input FWHM = 100 fs")

ax2.set_xlabel(r"Depth $z$ [mm]")
ax2.set_ylabel("Output FWHM [ps]")
ax2.set_xlim(0, 3)
ax2.set_ylim(bottom=0)
ax2.legend(frameon=False)
ax2.grid(True, alpha=0.2)
ax2.set_title("Pulse FWHM vs. depth (full range)\n" + subtitle,
              fontsize=9)

fig2.tight_layout()
fig2.savefig(f"{OUTDIR}/fig_fwhm_full.png", dpi=200)
print("Saved fig_fwhm_full.png")

plt.show()
