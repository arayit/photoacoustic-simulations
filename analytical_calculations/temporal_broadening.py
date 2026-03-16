"""
Temporal broadening of a femtosecond pulse in scattering tissue.

Analytical model from:
  Lutomirski, Ciervo, Hall — "Moments of multiple scattering,"
  Appl. Opt. 34, 7125–7136 (1995).

Physical picture
----------------
A temporally Gaussian 100 fs pulse enters scattering tissue.
Ballistic photons (unscattered) arrive first; scattered photons take
longer zigzag paths, creating a broadening tail.  The Lutomirski model
gives exact closed-form expressions for the mean delay and axial
variance of the photon cloud as a function of depth, without Monte Carlo.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# ---------------------------------------------------------------------------
# 1.  Tissue / pulse parameters
# ---------------------------------------------------------------------------

def make_params(
    mu_s: float = 4340.0,   # scattering coefficient  [m^-1]
    g: float = 0.93,         # anisotropy  <cos θ>
    n: float = 1.4,          # refractive index
    tau_fwhm: float = 100e-15,  # input pulse FWHM  [s]
) -> dict:
    """Return a parameter dict with all derived quantities."""
    c0 = 3e8                         # speed of light in vacuum  [m/s]
    c  = c0 / n                      # speed in medium           [m/s]

    # Henyey-Greenstein second moment
    cos2theta = (1 + 2 * g**2) / 3.0

    # Lutomirski angular-spread parameters  (Eqs. before C5)
    v = 1.0 - g
    w = 1.5 * (1.0 - cos2theta)

    # Gaussian pulse: sigma from FWHM
    sigma_pulse = tau_fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    return dict(
        mu_s=mu_s, g=g, n=n, c=c,
        cos2theta=cos2theta, v=v, w=w,
        tau_fwhm=tau_fwhm, sigma_pulse=sigma_pulse,
        ell_s=1.0 / mu_s,
    )


# ---------------------------------------------------------------------------
# 2.  Lutomirski moment equations
# ---------------------------------------------------------------------------

def normalized_mean_time(z_norm: np.ndarray, v: float) -> np.ndarray:
    """
    Mean normalized time to reach depth z  (Eq. 45a).

      T(z) = (1/v) * ln( 1 / (1 - v*z) )

    z_norm = z_physical * mu_s  (dimensionless, in units of mean free paths)
    """
    arg = 1.0 - v * z_norm
    arg = np.clip(arg, 1e-12, None)   # avoid log(0) near divergence
    return (1.0 / v) * np.log(1.0 / arg)


def mean_delay_normalized(z_norm: np.ndarray, v: float) -> np.ndarray:
    """
    Mean delay of photon cloud relative to ballistic arrival  (Eq. 45b).

      ΔT(z) = T(z) − z
    """
    T = normalized_mean_time(z_norm, v)
    return T - z_norm


def axial_variance_normalized(T: np.ndarray, v: float, w: float) -> np.ndarray:
    """
    Axial (temporal) variance of the photon cloud  (Eq. C7).

      σ²_z(T) =  (2/3) * [(w²−3wv)*(e^{−vT}−1+vT) + 2v²*(e^{−wT}−1+wT)]
                          / [w v² (w−v)]
                 −  [(1 − e^{−vT}) / v]²

    Returns σ_z (standard deviation, normalized units).
    Clamps negative values to zero (can occur at very small T).
    """
    evT = np.exp(-v * T)
    ewT = np.exp(-w * T)

    numerator = (w**2 - 3 * w * v) * (evT - 1 + v * T) + \
                2 * v**2             * (ewT - 1 + w * T)

    term1 = (2.0 / 3.0) * numerator / (w * v**2 * (w - v))
    term2 = ((1.0 - evT) / v) ** 2

    sigma_sq = term1 - term2
    sigma_sq = np.maximum(sigma_sq, 0.0)
    return np.sqrt(sigma_sq)


def compute_moments(z_phys: np.ndarray, p: dict) -> dict:
    """
    Compute all relevant moments over a depth array z_phys [m].

    Returns a dict with keys:
      z_norm, T, delta_t [s], sigma_t [s]
    """
    z_norm  = z_phys * p["mu_s"]
    T       = normalized_mean_time(z_norm, p["v"])

    # Mean delay  [s]
    DeltaT_norm = mean_delay_normalized(z_norm, p["v"])
    delta_t     = DeltaT_norm / (p["mu_s"] * p["c"])

    # Axial temporal spread  [s]
    sigma_z_norm = axial_variance_normalized(T, p["v"], p["w"])
    sigma_t      = sigma_z_norm / (p["mu_s"] * p["c"])

    return dict(z_norm=z_norm, T=T, delta_t=delta_t, sigma_t=sigma_t)


# ---------------------------------------------------------------------------
# 3.  Temporal pulse profile at a given depth
# ---------------------------------------------------------------------------

def temporal_profile(t: np.ndarray, z: float, p: dict, m: dict,
                     z_array: np.ndarray) -> np.ndarray:
    """
    Schematic temporal intensity profile I(t) at physical depth z [m].

    Components:
      Ballistic  — Gaussian(t, 0, σ_pulse) × exp(−μ_s z)
      Scattered  — Gaussian(t, Δt, σ_t)   × [1 − exp(−μ_s z)]
                   (Gaussian approximation; true shape is not exactly Gaussian)

    The two components are weighted by their respective photon fractions and
    the total is normalised to the peak of the ballistic pulse at z=0.
    """
    # Interpolate moments to this z value
    delta_t = np.interp(z, z_array, m["delta_t"])
    sigma_t = np.interp(z, z_array, m["sigma_t"])

    sigma_p = p["sigma_pulse"]
    mu_s    = p["mu_s"]

    # Photon fractions (Beer-Lambert for ballistic)
    f_ball = np.exp(-mu_s * z)
    f_scat = 1.0 - f_ball

    # Gaussian envelopes
    ball = f_ball * np.exp(-0.5 * (t / sigma_p) ** 2)

    if sigma_t > 0 and f_scat > 0:
        # Scattered component convolved with input pulse:
        #   total sigma = sqrt(sigma_t^2 + sigma_p^2)
        sigma_total = np.sqrt(sigma_t**2 + sigma_p**2)
        scat = f_scat * np.exp(-0.5 * ((t - delta_t) / sigma_total) ** 2)
    else:
        scat = np.zeros_like(t)

    return ball + scat


# ---------------------------------------------------------------------------
# 4.  Plots
# ---------------------------------------------------------------------------

def plot_sigma_and_delay(z_phys: np.ndarray, m: dict, p: dict,
                         ax_sigma, ax_delay):
    """Plot σ_t and Δt vs depth on provided axes."""
    z_mm = z_phys * 1e3        # convert to mm
    sigma_ps = m["sigma_t"] * 1e12
    delay_ps = m["delta_t"] * 1e12

    ax_sigma.plot(z_mm, sigma_ps, "C0", lw=2, label=r"$\sigma_t$ (scattered spread)")
    ax_sigma.axhline(p["tau_fwhm"] * 1e12 / (2 * np.sqrt(2 * np.log(2))),
                     color="C3", ls="--", lw=1.2,
                     label=r"Input $\sigma_{pulse}$ = 42 fs")
    ax_sigma.set_xlabel("Depth  z  [mm]")
    ax_sigma.set_ylabel(r"$\sigma_t$  [ps]")
    ax_sigma.set_title("Temporal spread vs. depth")
    ax_sigma.legend()
    ax_sigma.grid(True, alpha=0.3)

    ax_delay.plot(z_mm, delay_ps, "C1", lw=2)
    ax_delay.set_xlabel("Depth  z  [mm]")
    ax_delay.set_ylabel(r"$\Delta t$  [ps]")
    ax_delay.set_title("Mean delay (centroid lag behind ballistic)")
    ax_delay.grid(True, alpha=0.3)


def plot_profiles_stacked(z_phys: np.ndarray, m: dict, p: dict,
                          depths_mm: list, ax):
    """
    Stacked waterfall of temporal profiles at selected depths.
    Each trace is offset vertically for clarity.
    """
    tau_p = p["tau_fwhm"]
    t_max = max(50 * tau_p, 3 * m["delta_t"].max() + 5 * m["sigma_t"].max())
    t = np.linspace(-5 * tau_p, t_max, 5000)

    cmap   = plt.cm.viridis
    nsteps = len(depths_mm)

    for i, z_mm in enumerate(depths_mm):
        z = z_mm * 1e-3
        profile = temporal_profile(t, z, p, m, z_phys)
        norm    = profile.max() if profile.max() > 0 else 1.0

        color  = cmap(i / (nsteps - 1))
        offset = i * 1.3           # vertical separation between traces

        ax.fill_between(t * 1e12, offset, offset + profile / norm,
                        alpha=0.35, color=color)
        ax.plot(t * 1e12, offset + profile / norm,
                color=color, lw=1.5, label=f"z = {z_mm} mm")

    ax.set_xlabel("Time  [ps]")
    ax.set_ylabel("Depth  [offset → increasing z]")
    ax.set_title("Temporal profile evolution along z\n"
                 "(ballistic peak left, scattered tail right)")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_yticks([])
    ax.grid(True, axis="x", alpha=0.3)


def plot_2d_propagation(z_phys: np.ndarray, m: dict, p: dict, ax):
    """
    2-D false-colour map: intensity I(t, z).
    x-axis = time [ps], y-axis = depth [mm].
    """
    tau_p = p["tau_fwhm"]
    t_max = max(50 * tau_p, 3 * m["delta_t"].max() + 5 * m["sigma_t"].max())
    t = np.linspace(-3 * tau_p, t_max, 800)

    # Subsample z for speed
    idx    = np.linspace(0, len(z_phys) - 1, 200, dtype=int)
    z_sub  = z_phys[idx]
    m_sub  = {k: v[idx] for k, v in m.items()}

    image = np.zeros((len(z_sub), len(t)))
    for i, z in enumerate(z_sub):
        prof         = temporal_profile(t, z, p, m_sub, z_sub)
        image[i, :]  = prof

    # Normalise each row independently to show shape evolution
    row_max = image.max(axis=1, keepdims=True)
    row_max[row_max == 0] = 1
    image = image / row_max

    ax.imshow(
        image,
        aspect="auto",
        origin="lower",
        extent=[t[0] * 1e12, t[-1] * 1e12,
                z_sub[0] * 1e3,  z_sub[-1] * 1e3],
        cmap="inferno",
        norm=mcolors.PowerNorm(gamma=0.4),
    )
    ax.set_xlabel("Time  [ps]")
    ax.set_ylabel("Depth  z  [mm]")
    ax.set_title("Pulse temporal profile vs. depth  (row-normalised)")


# ---------------------------------------------------------------------------
# 5.  Main
# ---------------------------------------------------------------------------

def main():
    p      = make_params()
    z_phys = np.linspace(1e-6, 3e-3, 800)   # 0 → 3 mm  (avoid exact 0)
    m      = compute_moments(z_phys, p)

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        "Temporal broadening of a 100 fs pulse in scattering tissue\n"
        r"(Lutomirski 1995 model — $\mu_s$ = 4340 m$^{-1}$, g = 0.93, n = 1.4)",
        fontsize=12,
    )

    gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.35)

    ax_sigma  = fig.add_subplot(gs[0, 0])
    ax_delay  = fig.add_subplot(gs[0, 1])
    ax_stack  = fig.add_subplot(gs[1, 0])
    ax_2d     = fig.add_subplot(gs[1, 1])

    plot_sigma_and_delay(z_phys, m, p, ax_sigma, ax_delay)

    depths_mm = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5]
    plot_profiles_stacked(z_phys, m, p, depths_mm, ax_stack)
    plot_2d_propagation(z_phys, m, p, ax_2d)

    plt.savefig(
        "C:/Users/arayi/Documents/analytical_calculations/temporal_broadening.png",
        dpi=150, bbox_inches="tight",
    )
    plt.show()
    print("Saved -> temporal_broadening.png")

    # Print key values at selected depths
    print(f"\n{'Depth':>10}  {'sigma_t':>12}  {'Delta_t':>12}  {'sigma_t/tau_p':>15}")
    print("-" * 54)
    for z_mm in [0.1, 0.25, 0.5, 1.0, 2.0, 3.0]:
        z = z_mm * 1e-3
        sigma_t = np.interp(z, z_phys, m["sigma_t"]) * 1e12
        delta_t = np.interp(z, z_phys, m["delta_t"]) * 1e12
        ratio   = sigma_t / (p["tau_fwhm"] * 1e12)
        print(f"{z_mm:>8.2f} mm  {sigma_t:>9.3f} ps  {delta_t:>9.3f} ps  "
              f"{ratio:>12.1f}x")


if __name__ == "__main__":
    main()
