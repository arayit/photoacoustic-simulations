"""
Analytical calculations for burst-mode collective absorption enhancement.

Computes energy deposition, enhancement factors, and regime transitions
for GHz-burst femtosecond excitation with free-carrier absorption (FCA)
accumulation in silicon nanoparticles.

No-recombination model (tau_r << tau_c):
  N_k = k * beta * I_p^2 * tau_p / (2*hbar*omega)
  H_burst = N(N-1)/2 * sigma_fc * beta * I_p^3 * tau_p^2 / (2*hbar*omega)
            + N * beta * I_p^2 * tau_p

Usage:
  python burst_enhancement.py [--dpi N] [--fmt png|pdf] [--show] [--outdir DIR]
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt

# ═══════════════════════════════════════════════════════════════════════════
# Plot style
# ═══════════════════════════════════════════════════════════════════════════
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.minor.size": 2,
    "ytick.minor.size": 2,
    "legend.frameon": True,
    "legend.fancybox": False,
    "legend.framealpha": 0.9,
    "legend.edgecolor": "0.8",
    "legend.fontsize": 8,
})

# ═══════════════════════════════════════════════════════════════════════════
# Physical constants
# ═══════════════════════════════════════════════════════════════════════════
h_planck = 6.62607015e-34
c_light  = 299792458.0

# ═══════════════════════════════════════════════════════════════════════════
# System parameters
# ═══════════════════════════════════════════════════════════════════════════

# Optical
lam        = 1064e-9
hbar_omega = h_planck * c_light / lam   # ~1.87e-19 J
NA         = 0.50
n_medium   = 1.33

# Laser
tau_p      = 100e-15        # fs pulse duration [s]
tau_0      = 1e-9           # ns reference pulse [s]
tau_burst  = 1e-9           # burst window [s]
F_p        = 0.1e4          # fs focal fluence [J/m²]
F_0        = 1.0e4          # ns focal fluence [J/m²]
I_p        = F_p / tau_p    # ~1e16 W/m² (1 TW/cm²)
I_0        = F_0 / tau_0    # ~1e13 W/m² (1 GW/cm²)

# c-Si @ 1064 nm [Boggess 1986]
beta       = 1.5e-11        # TPA coefficient [m/W]
sigma_fc   = 5e-22          # FCA cross section [m²]

# Tissue [Yaroslavsky 2002]
mu_a_tissue = 50.0
mu_s_tissue = 5600.0
mu_t_tissue = mu_a_tissue + mu_s_tissue
Gamma       = 0.12


# ═══════════════════════════════════════════════════════════════════════════
# Core physics — closed-form (no recombination)
# ═══════════════════════════════════════════════════════════════════════════

def burst_heating(N, Ip, tp):
    """Closed-form burst heating: H_tpa + H_fca.

    H_tpa = N * beta * Ip^2 * tp
    H_fca = N*(N-1)/2 * sigma_fc * beta/(2*hbar_omega) * Ip^3 * tp^2
    """
    N = np.asarray(N, dtype=float)
    H_tpa = N * beta * Ip**2 * tp
    H_fca = N * (N - 1) / 2 * sigma_fc * beta / (2 * hbar_omega) * Ip**3 * tp**2
    return H_tpa + H_fca, H_tpa, H_fca


def pulse_heating_k(k, Ip, tp):
    """Heating from the k-th pulse (1-indexed).

    H_k = [sigma_fc * (k-1) * beta*Ip^2*tp / (2*hbar_omega) * Ip + beta*Ip^2] * tp
    """
    k = np.asarray(k, dtype=float)
    Nfc_before = (k - 1) * beta * Ip**2 * tp / (2 * hbar_omega)
    H_fca_k = sigma_fc * Nfc_before * Ip * tp
    H_tpa_k = beta * Ip**2 * tp
    return H_fca_k + H_tpa_k, H_tpa_k, H_fca_k


def carrier_density_after_k(k, Ip, tp):
    """Carrier density after k pulses (no recombination)."""
    return k * beta * Ip**2 * tp / (2 * hbar_omega)


def ns_heating(Ip_ns=None, tp_ns=None):
    """Heating from single NS pulse (TPA only)."""
    if Ip_ns is None:
        Ip_ns = I_0
    if tp_ns is None:
        tp_ns = tau_0
    return beta * Ip_ns**2 * tp_ns


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1: Enhancement vs N
# ═══════════════════════════════════════════════════════════════════════════

def fig1_enhancement_vs_N():
    """Enhancement factor vs burst pulse count N."""
    fig, ax = plt.subplots(figsize=(4.5, 3.2), constrained_layout=True)

    N_arr = np.geomspace(2, 1000, 300)
    H_ns = ns_heating()

    H_total, H_tpa, H_fca = burst_heating(N_arr, I_p, tau_p)

    ax.plot(N_arr, H_total / H_ns, color='#0072BD', lw=1.4, label='Total')
    ax.plot(N_arr, H_tpa / H_ns,   color='#D95319', lw=1.0, ls='--', label='TPA only')
    ax.plot(N_arr, H_fca / H_ns,   color='#7E2F8E', lw=1.0, ls='--', label='FCA only')

    ax.set_xlabel('Burst pulse count $N$')
    ax.set_ylabel('Enhancement $\\varepsilon$')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(2, 1000)
    ax.legend(loc='upper left', fontsize=8)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2: Pulse-by-pulse dynamics
# ═══════════════════════════════════════════════════════════════════════════

# Auger coefficient for c-Si [Dziewior & Schmid 1977]
C_auger = 3.8e-43  # [m^6/s]

# Surface recombination: tau_s = d / (4 * SRV)
# SRV = 2.2e4 cm/s = 2.2e2 m/s [Li 2023, Grumstrup 2014]
SRV = 2.2e4 * 1e-2  # [m/s]


def _bernoulli_decay(N0, tau_r, tau_s, C_aug):
    """Analytical decay between pulses: surface + Auger recombination.

    Solves dN/dt = -N/tau_s - C*N^3  (Bernoulli equation)
    Solution: N(t) = 1 / sqrt[ (1/N0^2 + C*tau_s) * exp(2t/tau_s) - C*tau_s ]
    """
    if N0 <= 0:
        return 0.0
    inv_N0_sq = 1.0 / N0**2
    exp_factor = np.exp(2 * tau_r / tau_s)
    val = (inv_N0_sq + C_aug * tau_s) * exp_factor - C_aug * tau_s
    if val <= 0:
        return 0.0
    return 1.0 / np.sqrt(val)


def _pulse_dynamics_combined(N, Ip, tp, d_nw, C_aug=C_auger):
    """Pulse-by-pulse heating with surface + Auger recombination.

    Parameters
    ----------
    d_nw : float, nanowire diameter [m]
    """
    tau_r = tau_burst / N
    tau_s = d_nw / (4 * SRV)  # surface recombination lifetime
    delta_Nfc = beta * Ip**2 * tp / (2 * hbar_omega)

    H_k = np.zeros(N)
    Nfc_k = np.zeros(N)
    Nfc = 0.0
    for k in range(N):
        H_k[k] = (sigma_fc * Nfc * Ip + beta * Ip**2) * tp
        Nfc_after = Nfc + delta_Nfc
        Nfc = _bernoulli_decay(Nfc_after, tau_r, tau_s, C_aug)
        Nfc_k[k] = Nfc

    return H_k, Nfc_k


def _pulse_dynamics_surface_only(N, Ip, tp, d_nw):
    """Surface recombination only (linear decay)."""
    tau_r = tau_burst / N
    tau_s = d_nw / (4 * SRV)
    decay = np.exp(-tau_r / tau_s)
    delta_Nfc = beta * Ip**2 * tp / (2 * hbar_omega)

    H_k = np.zeros(N)
    Nfc = 0.0
    for k in range(N):
        H_k[k] = (sigma_fc * Nfc * Ip + beta * Ip**2) * tp
        Nfc = (Nfc + delta_Nfc) * decay

    return H_k


def _pulse_dynamics_auger_only(N, Ip, tp):
    """Auger recombination only."""
    tau_r = tau_burst / N
    delta_Nfc = beta * Ip**2 * tp / (2 * hbar_omega)

    H_k = np.zeros(N)
    Nfc = 0.0
    for k in range(N):
        H_k[k] = (sigma_fc * Nfc * Ip + beta * Ip**2) * tp
        Nfc_after = Nfc + delta_Nfc
        Nfc = Nfc_after / np.sqrt(1 + 2 * C_auger * Nfc_after**2 * tau_r)

    return H_k


def fig2_pulse_dynamics():
    """Per-pulse heating H_k vs pulse number k, comparing recombination models."""
    fig, ax = plt.subplots(figsize=(5.0, 3.5), constrained_layout=True)

    N = 1000
    k = np.arange(1, N + 1)
    d_nw = 100e-9  # 100 nm nanowire diameter
    tau_s = d_nw / (4 * SRV)

    # No recombination (closed-form)
    H_k, H_tpa_k, H_fca_k = pulse_heating_k(k, I_p, tau_p)
    ax.plot(k, H_k, color='#0072BD', lw=1.2, label='No recombination')

    # Surface only
    H_k_surf = _pulse_dynamics_surface_only(N, I_p, tau_p, d_nw)
    ax.plot(k, H_k_surf, color='#77AC30', lw=1.0, ls='--',
            label=f'Surface only ($\\tau_s={tau_s*1e12:.0f}$ ps)')
    # Auger only
    H_k_auger = _pulse_dynamics_auger_only(N, I_p, tau_p)
    ax.plot(k, H_k_auger, color='#A2142F', lw=1.0, ls=':',
            label='Auger only')

    # Combined: surface + Auger (Bernoulli solution)
    H_k_combined, _ = _pulse_dynamics_combined(N, I_p, tau_p, d_nw)
    ax.plot(k, H_k_combined, color='black', lw=1.2, ls='-',
            label=f'Surface + Auger ($d={d_nw*1e9:.0f}$ nm)')

    # TPA baseline
    ax.axhline(beta * I_p**2 * tau_p, color='#D95319', lw=0.8, ls='-',
               alpha=0.4, label='TPA baseline')

    ax.set_xlabel('Pulse number $k$')
    ax.set_ylabel('Heating per pulse $H_k$  (J/m$^3$)')
    ax.set_xlim(1, N)
    ax.legend(loc='upper left', fontsize=7)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3: Enhancement vs fluence — finding the sweet spot
# ═══════════════════════════════════════════════════════════════════════════

def _total_burst_heating_combined(N, Ip, tp, d_nw):
    """Total burst heating with surface + Auger recombination."""
    tau_r = tau_burst / N
    tau_s = d_nw / (4 * SRV)
    delta_Nfc = beta * Ip**2 * tp / (2 * hbar_omega)

    H_total = 0.0
    Nfc = 0.0
    for k in range(N):
        H_total += (sigma_fc * Nfc * Ip + beta * Ip**2) * tp
        Nfc_after = Nfc + delta_Nfc
        Nfc = _bernoulli_decay(Nfc_after, tau_r, tau_s, C_auger)

    return H_total


def fig3_enhancement_vs_fluence():
    """Enhancement vs per-pulse fluence, showing Auger-limited sweet spot."""
    fig, ax = plt.subplots(figsize=(5.0, 3.5), constrained_layout=True)

    d_nw = 100e-9
    F_arr = np.logspace(-1, 4, 80)  # J/m² (0.01 to 100 mJ/cm²... wait)
    # F_p range: 0.001 to 1 J/cm² = 10 to 10000 J/m²
    F_arr = np.logspace(np.log10(10), np.log10(1e4), 80)  # [J/m²]

    H_ns = ns_heating()

    for Ni, col, ls in [(100, '#0072BD', '-'), (500, '#D95319', '-'),
                         (1000, '#A2142F', '-')]:
        eps_combined = np.zeros(len(F_arr))
        eps_no_recomb = np.zeros(len(F_arr))
        for i, Fp in enumerate(F_arr):
            Ip = Fp / tau_p
            # Combined model
            H_burst = _total_burst_heating_combined(Ni, Ip, tau_p, d_nw)
            eps_combined[i] = H_burst / H_ns
            # No recombination
            H_tot, _, _ = burst_heating(Ni, Ip, tau_p)
            eps_no_recomb[i] = H_tot / H_ns

        ax.plot(F_arr * 1e-4, eps_combined, color=col, lw=1.2, ls=ls,
                label=f'$N={Ni}$ (surface+Auger)')
        ax.plot(F_arr * 1e-4, eps_no_recomb, color=col, lw=0.7, ls=':',
                alpha=0.5)

    ax.set_xlabel('Per-pulse fluence $F_p$  (J/cm$^2$)')
    ax.set_ylabel('Enhancement $\\varepsilon$')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.legend(loc='upper left', fontsize=7)
    ax.set_title(f'$d = {d_nw*1e9:.0f}$ nm, dotted = no recomb.', fontsize=9)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Parameter table
# ═══════════════════════════════════════════════════════════════════════════

def print_parameter_table():
    print("=" * 65)
    print("  PARAMETER TABLE")
    print("=" * 65)

    print("\n  Optical")
    print(f"    Wavelength             lambda     = {lam*1e9:.0f} nm")
    print(f"    Numerical aperture     NA         = {NA:.2f}")
    print(f"    Refractive index       n          = {n_medium:.2f}")
    print(f"    Photon energy          hv         = {hbar_omega:.3e} J")

    print(f"\n  Laser (femtosecond)")
    print(f"    Pulse duration         tau_p      = {tau_p*1e15:.0f} fs")
    print(f"    Focal fluence          F_p        = {F_p*1e-4:.1f} J/cm2")
    print(f"    Focal intensity        I_p        = {I_p:.2e} W/m2  ({I_p*1e-4:.1e} W/cm2)")
    print(f"    Burst window           tau_burst  = {tau_burst*1e9:.0f} ns")

    print(f"\n  Laser (nanosecond reference)")
    print(f"    Pulse duration         tau_0      = {tau_0*1e9:.0f} ns")
    print(f"    Focal fluence          F_0        = {F_0*1e-4:.1f} J/cm2")
    print(f"    Focal intensity        I_0        = {I_0:.2e} W/m2  ({I_0*1e-4:.1e} W/cm2)")

    print(f"\n  Tissue [Yaroslavsky 2002]")
    print(f"    mu_a                               = {mu_a_tissue:.1f} m-1")
    print(f"    mu_s                               = {mu_s_tissue:.0f} m-1")
    print(f"    mu_t                               = {mu_t_tissue:.0f} m-1")
    print(f"    Gamma                              = {Gamma:.2f}")

    print(f"\n  Contrast agent (c-Si, 1064 nm) [Boggess 1986]")
    print(f"    TPA coefficient        beta       = {beta:.1e} m/W  ({beta*1e11:.1f} cm/GW)")
    print(f"    FCA cross section      sigma_fc   = {sigma_fc:.0e} m2")

    print(f"\n  Derived quantities")
    print(f"    NS heating             H_ns       = {ns_heating():.3e} J/m3")
    for Ni in [100, 500, 1000]:
        H_tot, H_tpa, H_fca = burst_heating(Ni, I_p, tau_p)
        eps = H_tot / ns_heating()
        frac = H_fca / H_tot
        print(f"    N={Ni}:  H={H_tot:.2e}  eps={eps:.2e}  FCA={frac:.1%}")
    print("=" * 65)


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--fmt', default='png', choices=['png', 'pdf', 'svg'])
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--outdir', default=None)
    args = parser.parse_args()

    if args.outdir is None:
        args.outdir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'figures_burst')
    os.makedirs(args.outdir, exist_ok=True)

    print_parameter_table()
    print()

    figures = [
        ('fig1_enhancement_vs_N',    fig1_enhancement_vs_N),
        ('fig2_pulse_dynamics',      fig2_pulse_dynamics),
        ('fig3_enhancement_vs_fluence', fig3_enhancement_vs_fluence),
    ]

    for name, func in figures:
        print(f'{name}...')
        fig = func()
        path = os.path.join(args.outdir, f'{name}.{args.fmt}')
        fig.savefig(path, dpi=args.dpi)
        plt.close(fig)
        print(f'  Saved -> {path}')

    if args.show:
        plt.show()

    print('\nDone.')


if __name__ == '__main__':
    main()
