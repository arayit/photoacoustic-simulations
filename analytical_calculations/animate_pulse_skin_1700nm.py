"""
Animation: 100 fs Gaussian pulse temporal broadening vs. depth.
Tissue: Skin (Mean, Native) at 1700 nm.

Physical model
--------------
sigma_t(z) from Lutomirski (1995) is the RMS temporal spread of the
photon arrival-time distribution (second central moment of the full
photon cloud).  For a Gaussian input pulse of width sigma_pulse, the
output pulse width at depth z follows from quadrature addition:

    sigma_output(z) = sqrt( sigma_pulse^2 + sigma_t(z)^2 )

The pulse centroid is delayed by delta_t(z) relative to ballistic arrival.
No ballistic / scattered decomposition — just the broadening Gaussian.

Reference: Lutomirski, Ciervo, Hall, Appl. Opt. 34, 7125 (1995)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from temporal_broadening import make_params, compute_moments


# ---------------------------------------------------------------------------
# Parameters & pre-computation
# Skin (Mean, Native) at 1700 nm: mu_s = 5.1 mm^-1, mu_a = 0.50 mm^-1, g = 0.83
# ---------------------------------------------------------------------------

p      = make_params(mu_s=5.1e3, g=0.83)

# depth range: 0 → 0.8 × z_limit  (model validity)
z_limit = 1.0 / (p["v"] * p["mu_s"])
z_max   = 0.8 * z_limit

z_phys = np.linspace(0, z_max, 400)
z_phys[0] = 1e-9
m = compute_moments(z_phys, p)

sigma_p = p["sigma_pulse"]
tau_p   = p["tau_fwhm"]

sigma_out = np.sqrt(sigma_p**2 + m["sigma_t"]**2)
fwhm_out  = sigma_out * 2.0 * np.sqrt(2.0 * np.log(2.0))

max_sigma = sigma_out[-1]
max_delay = m["delta_t"][-1]
t_hi =  max_delay + 6 * max_sigma
t_lo = -t_hi
t    = np.linspace(t_lo, t_hi, 5000)
t_ps = t * 1e12


# ---------------------------------------------------------------------------
# Figure setup
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor("#0d0d0d")
ax.set_facecolor("#0d0d0d")

ax.set_xlim(t_ps[0], t_ps[-1])
ax.set_ylim(-0.03, 1.08)
ax.set_xlabel("Time  [ps]", color="white", fontsize=12)
ax.set_ylabel("Normalised intensity", color="white", fontsize=12)
ax.tick_params(colors="white")
for spine in ax.spines.values():
    spine.set_edgecolor("#444444")

ax.set_title(
    "100 fs Gaussian pulse broadening in scattering tissue  "
    r"(Lutomirski 1995  |  Skin 1700 nm  |  $\mu_s$=5.1 mm$^{-1}$, g=0.83, n=1.4)",
    color="white", fontsize=11, pad=10,
)

input_pulse = np.exp(-0.5 * (t / sigma_p) ** 2)
ax.plot(t_ps, input_pulse, color="#555555", lw=1.2, ls="--",
        label="Input pulse  (z = 0,  FWHM = 100 fs)")

line,    = ax.plot([], [], color="#00cfff", lw=2.5, label="Pulse at depth z")
fill_ref = [None]

ax.legend(loc="upper right", fontsize=9,
          facecolor="#1a1a1a", edgecolor="#555555", labelcolor="white")

ann_z     = ax.text(0.03, 0.93, "", transform=ax.transAxes,
                    color="white",   fontsize=13, va="top", fontfamily="monospace")
ann_sigma = ax.text(0.03, 0.83, "", transform=ax.transAxes,
                    color="#00cfff", fontsize=10, va="top")
ann_fwhm  = ax.text(0.03, 0.76, "", transform=ax.transAxes,
                    color="#00cfff", fontsize=10, va="top")
ann_delay = ax.text(0.03, 0.69, "", transform=ax.transAxes,
                    color="#ff9944", fontsize=10, va="top")
ann_broad = ax.text(0.03, 0.62, "", transform=ax.transAxes,
                    color="#aaaaaa", fontsize=10, va="top")


# ---------------------------------------------------------------------------
# Frame subsampling
# ---------------------------------------------------------------------------

frame_idx = np.linspace(0, len(z_phys) - 1, 200, dtype=int)


# ---------------------------------------------------------------------------
# Animation functions
# ---------------------------------------------------------------------------

def init():
    line.set_data([], [])
    return (line,)


def update(i):
    k = frame_idx[i]

    sig  = sigma_out[k]
    fwhm = fwhm_out[k]

    amplitude = sigma_p / sig
    profile   = amplitude * np.exp(-0.5 * (t / sig) ** 2)

    line.set_data(t_ps, profile)

    if fill_ref[0] is not None:
        fill_ref[0].remove()
    fill_ref[0] = ax.fill_between(t_ps, 0, profile,
                                  color="#00cfff", alpha=0.10)

    z_mm    = z_phys[k] * 1e3
    sig_ps  = sig  * 1e12
    fwhm_ps = fwhm * 1e12
    ratio   = fwhm_ps / (tau_p * 1e12)

    ann_z.set_text(f"z = {z_mm:.2f} mm")
    ann_sigma.set_text(f"sigma_out = {sig_ps:.3f} ps")
    ann_fwhm.set_text( f"FWHM_out  = {fwhm_ps:.3f} ps")
    ann_delay.set_text(f"peak amp  = {amplitude:.4f}  (energy conserved)")
    ann_broad.set_text(f"broadening = {ratio:.1f}x input FWHM")

    return (line,)


ani = animation.FuncAnimation(
    fig, update,
    frames=len(frame_idx),
    init_func=init,
    interval=80,
    blit=False,
)

out_path = "C:/Users/arayi/Documents/analytical_calculations/figures/pulse_propagation_skin_1700nm.gif"
print("Saving animation ...")
ani.save(out_path, writer="pillow", fps=12, dpi=120)
print(f"Saved -> {out_path}")
