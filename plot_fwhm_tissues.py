"""
FWHM vs. depth — one figure per tissue/wavelength combination.
Depth axis clipped at 0.8 × model validity limit.
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

OUTDIR   = "C:/Users/arayi/Documents/analytical_calculations/figures"
tau_fwhm = 100e-15   # input pulse FWHM [s]

# ---------------------------------------------------------------------------
# One entry per (tissue, wavelength) combination present in the data
# mu_s and mu_a in mm^-1
# ---------------------------------------------------------------------------
CASES = [
    {
        "tissue": "Native White Matter",
        "wl":     1100,
        "mu_s":   27.2,
        "mu_a":   0.10,
        "g":      0.89,
        "fname":  "fig_fwhm_white_matter_1100nm",
    },
    {
        "tissue": "Native Grey Matter",
        "wl":     1100,
        "mu_s":   5.6,
        "mu_a":   0.05,
        "g":      0.92,
        "fname":  "fig_fwhm_grey_matter_1100nm",
    },
    {
        "tissue": "Skin (Mean, Native)",
        "wl":     1100,
        "mu_s":   14.7,
        "mu_a":   0.080,
        "g":      0.925,
        "fname":  "fig_fwhm_skin_1100nm",
    },
    {
        "tissue": "Skin (Mean, Native)",
        "wl":     1700,
        "mu_s":   5.1,
        "mu_a":   0.50,
        "g":      0.83,
        "fname":  "fig_fwhm_skin_1700nm",
    },
]

for case in CASES:
    mu_s_m = case["mu_s"] * 1e3   # convert mm^-1 → m^-1

    p       = make_params(mu_s=mu_s_m, g=case["g"], tau_fwhm=tau_fwhm)
    z_limit = 1.0 / (p["v"] * p["mu_s"])          # model validity limit [m]
    z_max   = 0.8 * z_limit                        # plot up to here

    z_phys  = np.linspace(1e-9, z_max, 4000)
    m       = compute_moments(z_phys, p)

    sigma_out = np.sqrt(p["sigma_pulse"]**2 + m["sigma_t"]**2)
    fwhm_out  = sigma_out * 2 * np.sqrt(2 * np.log(2))

    # axis units: x in mm or µm based on depth scale, y always in ps
    if z_max < 1e-3:
        z_plot  = z_phys * 1e6
        x_label = r"Depth $z$ [$\mu$m]"
        x_max   = z_max * 1e6
    else:
        z_plot  = z_phys * 1e3
        x_label = r"Depth $z$ [mm]"
        x_max   = z_max * 1e3

    fwhm_plot       = fwhm_out * 1e12
    y_label         = "Output FWHM [ps]"
    input_fwhm_plot = tau_fwhm * 1e12
    input_label     = f"Input FWHM = {tau_fwhm*1e15:.0f} fs"

    legend_line = (
        rf"{case['wl']} nm  |  "
        rf"$\mu_s$ = {case['mu_s']:.1f} mm⁻¹,  "
        rf"$\mu_a$ = {case['mu_a']:.3f} mm⁻¹,  "
        rf"$g$ = {case['g']}"
    )

    fig, ax = plt.subplots(figsize=(5.5, 4))

    ax.plot(z_plot, fwhm_plot, "C0", lw=1.8, label=legend_line)
    ax.axhline(input_fwhm_plot, color="k", ls="--", lw=1, label=input_label)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xlim(0, x_max)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=8.5)
    ax.grid(True, alpha=0.2)
    ax.set_title(
        f"{case['tissue']} — {case['wl']} nm  ·  Input FWHM = 100 fs",
        fontsize=9,
    )

    fig.tight_layout()
    out = f"{OUTDIR}/{case['fname']}.png"
    fig.savefig(out, dpi=200)
    print(f"Saved {out}")
    plt.close(fig)
