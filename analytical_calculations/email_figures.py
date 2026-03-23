"""
Email figures: carrier accumulation problem & recombination mechanisms.

Generates 4 figures showing why naive FCA models are unphysical
and how Auger recombination resolves the issue.

Usage:
  python email_figures.py [--dpi N] [--fmt png|pdf] [--show] [--outdir DIR]
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt

# Import shared constants and helpers
from burst_enhancement import (
    beta, I_p, tau_p, tau_burst, hbar_omega, sigma_fc,
    C_auger, SRV, _bernoulli_decay,
    mu_t_tissue,
)

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
# Constants
# ═══════════════════════════════════════════════════════════════════════════

# Si atomic density [m^-3]  (8 atoms/unit cell, a = 5.431 Å)
n_Si = 5.0e28

# Per-pulse carrier generation
delta_N = beta * I_p**2 * tau_p / (2 * hbar_omega)

# Burst parameters
N_pulses = 1000
tau_r = tau_burst / N_pulses  # inter-pulse gap [s]

# Nanostructure
d_nw = 100e-9  # 100 nm nanowire diameter
tau_s = d_nw / (4 * SRV)  # surface recombination lifetime

# Radiative recombination for c-Si [Trupke 2003]
B_rad = 4.73e-15 * 1e-6  # cm^3/s -> m^3/s

# Linear recombination lifetime for eq. 5
tau_c = 300e-12  # 300 ps

# Beer-Lambert attenuation
z_depth = 500e-6  # 500 um imaging depth
I_z = I_p * np.exp(-mu_t_tissue * z_depth)  # attenuated intensity
G_surface = beta * I_p**2 / (2 * hbar_omega)  # generation rate at surface
G_depth = beta * I_z**2 / (2 * hbar_omega)    # generation rate at depth
delta_N_depth = G_depth * tau_p                # per-pulse generation at depth


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1: No-recombination carrier accumulation
# ═══════════════════════════════════════════════════════════════════════════

def fig1_no_recombination():
    """Carrier density vs pulse number — no recombination (linear growth)."""
    fig, ax = plt.subplots(figsize=(5.0, 3.5), constrained_layout=True)

    k = np.arange(1, N_pulses + 1)
    N_fc = k * delta_N_depth

    ax.plot(k, N_fc, color='#0072BD', lw=1.4)

    # Si atomic density line
    ax.axhline(n_Si, color='#A2142F', lw=1.2, ls='--',
               label=f'$n_{{Si}}$ = {n_Si:.0e} m$^{{-3}}$ (1 carrier/atom)')

    # Mark crossing point if it occurs
    k_cross = int(np.ceil(n_Si / delta_N_depth))
    if k_cross <= N_pulses:
        ax.plot(k_cross, n_Si, 'o', color='#A2142F', ms=6, zorder=5)
        ax.annotate(f'$k = {k_cross}$\n(exceeds atomic density)',
                    xy=(k_cross, n_Si), xytext=(k_cross + 150, n_Si * 0.3),
                    fontsize=8, ha='left',
                    arrowprops=dict(arrowstyle='->', color='#A2142F', lw=0.8))
    else:
        ax.text(N_pulses * 0.5, N_fc[-1] * 1.5,
                f'$N_{{1000}}$ = {N_fc[-1]:.1e} m$^{{-3}}$',
                fontsize=8, color='#0072BD')

    I_focus_GW = I_z * 1e-4 * 1e-9
    ax.set_xlabel('Pulse number $k$')
    ax.set_ylabel('Carrier density $N_{fc}$ (m$^{-3}$)')
    ax.set_xlim(1, N_pulses)
    ax.set_yscale('log')
    ax.set_ylim(delta_N_depth * 0.5, n_Si * 5)
    ax.legend(loc='lower right', fontsize=8)
    ax.set_title('No recombination: $N_k = k \\cdot \\Delta N_{fc}$', fontsize=10)
    ax.text(0.02, 0.98,
            f'$z$ = {z_depth*1e6:.0f} $\\mu$m, '
            f'$I_{{focus}}$ = {I_focus_GW:.0f} GW/cm$^2$',
            transform=ax.transAxes, fontsize=7, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                      edgecolor='0.8', alpha=0.9))

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2: Eq. 5 linear recombination (tau_c = 300 ps)
# ═══════════════════════════════════════════════════════════════════════════

def fig2_linear_recombination():
    """Carrier density vs pulse number — eq. 5 with tau_c = 300 ps."""
    fig, ax = plt.subplots(figsize=(5.0, 3.5), constrained_layout=True)

    k = np.arange(1, N_pulses + 1)
    decay = np.exp(-tau_r / tau_c)

    # Iterative: add delta_N_depth, then decay
    N_fc_lin = np.zeros(N_pulses)
    Nfc = 0.0
    for i in range(N_pulses):
        Nfc = (Nfc + delta_N_depth) * decay
        N_fc_lin[i] = Nfc

    # No-recombination reference
    N_fc_none = k * delta_N_depth

    # Analytical steady state
    N_ss = delta_N_depth / (1 - decay)

    ax.plot(k, N_fc_none, color='#0072BD', lw=0.8, ls=':', alpha=0.5,
            label='No recombination')
    ax.plot(k, N_fc_lin, color='#D95319', lw=1.4,
            label=f'Eq. 5 ($\\tau_c = {tau_c*1e12:.0f}$ ps)')
    ax.axhline(N_ss, color='#D95319', lw=0.8, ls='--', alpha=0.6)
    ax.text(N_pulses * 0.6, N_ss * 1.3,
            f'$N_{{ss}}$ = {N_ss:.1e} m$^{{-3}}$',
            fontsize=8, color='#D95319')

    # Si atomic density line
    ax.axhline(n_Si, color='#A2142F', lw=1.2, ls='--',
               label=f'$n_{{Si}}$ = {n_Si:.0e} m$^{{-3}}$')

    ax.set_xlabel('Pulse number $k$')
    ax.set_ylabel('Carrier density $N_{fc}$ (m$^{-3}$)')
    ax.set_xlim(1, N_pulses)
    ax.set_yscale('log')
    ax.set_ylim(1e26, 5e29)
    ax.legend(loc='center right', fontsize=8)
    ax.set_title(
        f'Eq. 5 linear recombination: $\\tau_r$ = {tau_r*1e12:.0f} ps, '
        f'$\\tau_c$ = {tau_c*1e12:.0f} ps',
        fontsize=10)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2b: Continuous ODE solution N(t) = G*tau_c*(1 - exp(-t/tau_c))
# ═══════════════════════════════════════════════════════════════════════════

def fig2b_continuous_ode():
    """Pulsed ODE solution (step function source) at focal depth."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.5),
                                    constrained_layout=True)

    I_focus_GW = I_z * 1e-4 * 1e-9  # W/m^2 -> GW/cm^2
    I_p_TW = I_p * 1e-4 * 1e-12     # W/m^2 -> TW/cm^2
    decay = np.exp(-tau_r / tau_c)

    # --- Left panel: full burst, pulse-by-pulse envelope ---
    N_peak = np.zeros(N_pulses)
    N_trough = np.zeros(N_pulses)
    Nfc = 0.0
    for i in range(N_pulses):
        Nfc += delta_N_depth  # add pulse
        N_peak[i] = Nfc
        Nfc *= decay          # decay between pulses
        N_trough[i] = Nfc

    k = np.arange(1, N_pulses + 1)
    ax1.fill_between(k, N_trough, N_peak, color='#0072BD', alpha=0.15)
    ax1.plot(k, N_peak, color='#0072BD', lw=0.8, label='$N$ after pulse')
    ax1.plot(k, N_trough, color='#0072BD', lw=0.8, ls='--',
             alpha=0.6, label='$N$ before pulse')

    N_ss_peak = delta_N_depth / (1 - decay)
    ax1.axhline(N_ss_peak, color='#D95319', lw=0.8, ls=':')
    ax1.text(N_pulses * 0.5, N_ss_peak * 1.15,
             f'$N_{{peak}}$ = {N_ss_peak:.1e} m$^{{-3}}$',
             fontsize=7, color='#D95319')

    ax1.axhline(n_Si, color='#A2142F', lw=1.0, ls='--', alpha=0.5)
    ax1.text(N_pulses * 0.5, n_Si * 1.15,
             f'$n_{{Si}}$', fontsize=7, color='#A2142F')

    ax1.set_xlabel('Pulse number $k$')
    ax1.set_ylabel('Carrier density $N_{fc}$ (m$^{-3}$)')
    ax1.set_xlim(1, N_pulses)
    ax1.set_yscale('log')
    ax1.set_ylim(delta_N_depth * 0.5, n_Si * 2)
    ax1.legend(loc='center right', fontsize=7)
    ax1.set_title('Full burst envelope', fontsize=9)

    # --- Right panel: full burst sawtooth (all N pulses) ---
    t_list = []
    N_list = []
    Nfc = 0.0
    t_now = 0.0
    for i in range(N_pulses):
        # Pulse on: instantaneous carrier addition
        Nfc += delta_N_depth
        t_list.extend([t_now, t_now])
        N_list.extend([Nfc - delta_N_depth, Nfc])

        # Decay between pulses
        t_end = t_now + tau_r
        t_list.append(t_end)
        Nfc_decayed = Nfc * np.exp(-tau_r / tau_c)
        N_list.append(Nfc_decayed)
        Nfc = Nfc_decayed
        t_now = t_end

    t_arr = np.array(t_list)
    N_arr = np.array(N_list)

    ax2.plot(t_arr * 1e9, N_arr, color='#0072BD', lw=0.4)

    ax2.axhline(N_ss_peak, color='#D95319', lw=0.8, ls=':')
    ax2.text(0.55, N_ss_peak * 1.1,
             f'$N_{{peak}}$ = {N_ss_peak:.1e} m$^{{-3}}$',
             fontsize=7, color='#D95319')

    ax2.set_xlabel('Time (ns)')
    ax2.set_ylabel('Carrier density $N_{fc}$ (m$^{-3}$)')
    ax2.set_xlim(0, tau_burst * 1e9)
    ax2.set_title(f'Full burst — {N_pulses} pulses (sawtooth)', fontsize=9)

    # Info box on right panel
    ax2.text(0.98, 0.95,
             f'$I_p$ = {I_p_TW:.0f} TW/cm$^2$\n'
             f'$I_{{focus}}$ = {I_focus_GW:.0f} GW/cm$^2$\n'
             f'$z$ = {z_depth*1e6:.0f} $\\mu$m\n'
             f'$\\tau_c$ = {tau_c*1e12:.0f} ps\n'
             f'$\\tau_r$ = {tau_r*1e12:.0f} ps',
             transform=ax2.transAxes, fontsize=7, va='top', ha='right',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                       edgecolor='0.8', alpha=0.9))

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3: Recombination mechanism lifetimes
# ═══════════════════════════════════════════════════════════════════════════

def fig3_recombination_mechanisms():
    """Effective recombination lifetime vs carrier density."""
    fig, ax = plt.subplots(figsize=(5.0, 3.5), constrained_layout=True)

    N_arr = np.logspace(23, 29, 300)  # carrier density [m^-3]

    # Surface recombination: constant
    tau_surf = np.full_like(N_arr, tau_s)

    # Radiative: tau_rad = 1/(B*N)
    tau_rad = 1.0 / (B_rad * N_arr)

    # Auger: tau_aug = 1/(C*N^2)
    tau_aug = 1.0 / (C_auger * N_arr**2)

    # Effective (all three): 1/tau_eff = 1/tau_s + B*N + C*N^2
    tau_eff = 1.0 / (1.0/tau_s + B_rad * N_arr + C_auger * N_arr**2)

    ax.plot(N_arr, tau_surf * 1e12, color='#77AC30', lw=1.2, ls='--',
            label=f'Surface ($d = {d_nw*1e9:.0f}$ nm)')
    ax.plot(N_arr, tau_rad * 1e12, color='#4DBEEE', lw=1.0, ls=':',
            label='Radiative (indirect)')
    ax.plot(N_arr, tau_aug * 1e12, color='#A2142F', lw=1.2, ls='-.',
            label='Auger')
    ax.plot(N_arr, tau_eff * 1e12, color='black', lw=1.4,
            label='Effective $\\tau_{eff}$')

    # Mark our per-pulse carrier generation
    ax.axvline(delta_N, color='#D95319', lw=1.0, ls='--', alpha=0.7)
    ax.text(delta_N * 1.5, 1e4,
            f'$\\Delta N_{{fc}}$ = {delta_N:.1e} m$^{{-3}}$\n(per pulse)',
            fontsize=7, color='#D95319')

    # Mark tau_r
    ax.axhline(tau_r * 1e12, color='gray', lw=0.8, ls='-', alpha=0.4)
    ax.text(2e23, tau_r * 1e12 * 1.5,
            f'$\\tau_r$ = {tau_r*1e12:.0f} ps (inter-pulse gap)',
            fontsize=7, color='gray')

    ax.set_xlabel('Carrier density $N$ (m$^{-3}$)')
    ax.set_ylabel('Recombination lifetime (ps)')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1e23, 1e29)
    ax.set_ylim(1e-3, 1e6)
    ax.legend(loc='lower left', fontsize=7)
    ax.set_title('Recombination lifetimes in c-Si', fontsize=10)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Figure 4: All models compared — Auger resolves the problem
# ═══════════════════════════════════════════════════════════════════════════

def fig4_all_models():
    """Carrier density at focus: linear-only vs linear+Auger."""
    fig, ax = plt.subplots(figsize=(5.0, 3.5), constrained_layout=True)

    I_focus_GW = I_z * 1e-4 * 1e-9
    k = np.arange(1, N_pulses + 1)
    decay_lin = np.exp(-tau_r / tau_c)

    # 1. No recombination
    N_none = k * delta_N_depth

    # 2. Linear only (eq. 5) at focus
    N_lin = np.zeros(N_pulses)
    Nfc = 0.0
    for i in range(N_pulses):
        Nfc = (Nfc + delta_N_depth) * decay_lin
        N_lin[i] = Nfc

    # 3. Linear + Auger (eq. 5 + CN^3) at focus — Bernoulli decay
    N_aug = np.zeros(N_pulses)
    Nfc = 0.0
    for i in range(N_pulses):
        Nfc += delta_N_depth
        Nfc = _bernoulli_decay(Nfc, tau_r, tau_c, C_auger)
        N_aug[i] = Nfc

    ax.plot(k, N_none, color='#77AC30', lw=1.2, ls='--',
            label='No recombination')
    ax.plot(k, N_lin, color='#0072BD', lw=1.4,
            label=f'SRH (surface): $-N/\\tau_c$ ($\\tau_c = {tau_c*1e12:.0f}$ ps)')
    ax.plot(k, N_aug, color='#A2142F', lw=1.4,
            label=f'SRH + Auger: $-N/\\tau_c - CN^3$')

    # N_ss labels — right side, annotated
    N_ss_none = N_none[-1]
    N_ss_lin = delta_N_depth / (1 - decay_lin)
    N_ss_aug = N_aug[-1]

    # No-recomb label
    ax.annotate(f'$N_{{1000}}$ = {N_ss_none:.1e}',
                xy=(N_pulses, N_ss_none),
                xytext=(N_pulses * 0.55, N_ss_none * 1.8),
                fontsize=7, color='#77AC30',
                arrowprops=dict(arrowstyle='->', color='#77AC30', lw=0.6))

    # Linear label
    ax.annotate(f'$N_{{ss}}$ = {N_ss_lin:.1e}',
                xy=(N_pulses, N_ss_lin),
                xytext=(N_pulses * 0.55, N_ss_lin * 2.5),
                fontsize=7, color='#0072BD',
                arrowprops=dict(arrowstyle='->', color='#0072BD', lw=0.6))

    # Auger label
    ax.annotate(f'$N_{{ss}}$ = {N_ss_aug:.1e}',
                xy=(N_pulses, N_ss_aug),
                xytext=(N_pulses * 0.55, N_ss_aug * 0.25),
                fontsize=7, color='#A2142F',
                arrowprops=dict(arrowstyle='->', color='#A2142F', lw=0.6))

    # Si atomic density
    ax.axhline(n_Si, color='gray', lw=0.8, ls='--', alpha=0.3)
    ax.text(N_pulses * 0.02, n_Si * 1.3,
            f'$n_{{Si}}$ = {n_Si:.0e} m$^{{-3}}$', fontsize=7, color='gray')

    # Info box — bottom right
    ax.text(0.98, 0.05,
            f'$z$ = {z_depth*1e6:.0f} $\\mu$m, '
            f'$I_{{focus}}$ = {I_focus_GW:.0f} GW/cm$^2$\n'
            f'$\\tau_c$ = {tau_c*1e12:.0f} ps, '
            f'$C$ = {C_auger:.1e} m$^6$/s',
            transform=ax.transAxes, fontsize=7, va='bottom', ha='right',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                      edgecolor='0.8', alpha=0.9))

    ax.set_xlabel('Pulse number $k$')
    ax.set_ylabel('Carrier density $N_{fc}$ (m$^{-3}$)')
    ax.set_xlim(1, N_pulses)
    ax.set_yscale('log')
    ax.set_ylim(delta_N_depth * 0.3, n_Si * 5)
    ax.legend(loc='upper left', fontsize=7,
              bbox_to_anchor=(0.02, 0.88))
    ax.set_title('Comparison of all three models at focus', fontsize=10)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# Print key numbers
# ═══════════════════════════════════════════════════════════════════════════

def print_summary():
    decay_lin = np.exp(-tau_r / tau_c)
    N_ss_lin = delta_N / (1 - decay_lin)

    # Auger steady state (from simulation)
    Nfc = 0.0
    for _ in range(N_pulses):
        Nfc += delta_N
        Nfc = Nfc / np.sqrt(1 + 2 * C_auger * Nfc**2 * tau_r)
    N_ss_aug = Nfc

    # Combined steady state
    Nfc = 0.0
    for _ in range(N_pulses):
        Nfc += delta_N
        Nfc = _bernoulli_decay(Nfc, tau_r, tau_s, C_auger)
    N_ss_comb = Nfc

    k_cross = int(np.ceil(n_Si / delta_N))

    print("=" * 60)
    print("  KEY NUMBERS FOR EMAIL")
    print("=" * 60)
    print(f"  Per-pulse carrier generation:  delta_N = {delta_N:.2e} m^-3")
    print(f"  Si atomic density:             n_Si    = {n_Si:.1e} m^-3")
    print(f"  Inter-pulse gap:               tau_r   = {tau_r*1e12:.1f} ps")
    print(f"  Linear recomb. lifetime:       tau_c   = {tau_c*1e12:.0f} ps")
    print(f"  Surface recomb. lifetime:      tau_s   = {tau_s*1e12:.0f} ps")
    print(f"  Auger lifetime (at delta_N):   tau_A   = "
          f"{1/(C_auger*delta_N**2)*1e12:.1f} ps")
    print()
    print(f"  No recomb: crosses n_Si at k = {k_cross}")
    print(f"  No recomb: N(1000) = {1000*delta_N:.2e} m^-3  "
          f"({1000*delta_N/n_Si:.0f}x n_Si)")
    print(f"  Eq. 5 (tau_c=300ps): N_ss = {N_ss_lin:.2e} m^-3  "
          f"({N_ss_lin/n_Si:.1f}x n_Si)")
    print(f"  Auger only: N_ss = {N_ss_aug:.2e} m^-3  "
          f"({N_ss_aug/n_Si:.2f}x n_Si)")
    print(f"  Surface+Auger: N_ss = {N_ss_comb:.2e} m^-3  "
          f"({N_ss_comb/n_Si:.2f}x n_Si)")
    print()
    print(f"  --- Beer-Lambert at z = {z_depth*1e6:.0f} um ---")
    print(f"  mu_t = {mu_t_tissue:.0f} m^-1")
    print(f"  I(z) = {I_z:.2e} W/m^2  ({I_z/I_p:.4f} x I_p)")
    print(f"  G_surface = {G_surface:.2e} m^-3/s")
    print(f"  G_depth   = {G_depth:.2e} m^-3/s")
    print(f"  Continuous ODE N_ss (surface) = {G_surface*tau_c:.2e} m^-3  "
          f"({G_surface*tau_c/n_Si:.1f}x n_Si)")
    print(f"  Continuous ODE N_ss (z={z_depth*1e6:.0f}um)  = {G_depth*tau_c:.2e} m^-3  "
          f"({G_depth*tau_c/n_Si:.4f}x n_Si)")
    print("=" * 60)


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
            os.path.dirname(os.path.abspath(__file__)), 'figures_email')
    os.makedirs(args.outdir, exist_ok=True)

    print_summary()
    print()

    figures = [
        ('fig1_no_recombination',        fig1_no_recombination),
        ('fig2_linear_recombination',    fig2_linear_recombination),
        ('fig2b_continuous_ode',         fig2b_continuous_ode),
        ('fig3_recombination_mechanisms', fig3_recombination_mechanisms),
        ('fig4_all_models',              fig4_all_models),
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
