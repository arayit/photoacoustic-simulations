"""
exp_009/plot_results.py  --  Figures for TPA-PAM feasibility limits.

Usage:
  python plot_results.py [--dpi N] [--fmt png|pdf|svg] [--show]
"""

import argparse
import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.colors import LogNorm
from matplotlib.patches import Patch

HERE        = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, 'results')
OUT_ROOT    = os.path.join(r'C:\Users\SYAVAS-LASERLAB\Documents\LAB_PC_DRIVE', 'exp_009')

sys.path.insert(0, os.path.join(HERE, '..', '..'))
import pa_visualize as pav

# ---------------------------------------------------------------------------
# Experiment grid
# ---------------------------------------------------------------------------
DEPTHS_MM = [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0]

ALPHA2_LIST = [
    {'tag': 'a1', 'value': 9e-14, 'label': r'$\alpha_2 = 9\times10^{-14}$ m/W  (~1 mM)'},
    {'tag': 'a2', 'value': 9e-13, 'label': r'$\alpha_2 = 9\times10^{-13}$ m/W  (~10 mM)'},
    {'tag': 'a3', 'value': 9e-12, 'label': r'$\alpha_2 = 9\times10^{-12}$ m/W  (high-$\sigma_2$)'},
]

PULSE_CONFIGS = [
    {'tag': 'ns',    'label': 'NS (1 ns)',              'color': '#000000', 'marker': 's', 'ls': '--', 'ms': 4,
     'fluence_focus': 1.0, 'pulse_duration': 1e-9},
    {'tag': 'fs',    'label': 'FS (100 fs)',             'color': '#77AC30', 'marker': 'd', 'ls': '-',  'ms': 4,
     'fluence_focus': 0.1, 'pulse_duration': 100e-15},
    {'tag': 'b0010', 'label': 'Burst $N=10$',           'color': '#4DBEEE', 'marker': 'o', 'ls': '-',  'ms': 3.5,
     'fluence_focus': 0.1, 'pulse_duration': 100e-15},
    {'tag': 'b0050', 'label': 'Burst $N=50$',           'color': '#0072BD', 'marker': 'o', 'ls': '-',  'ms': 3.5,
     'fluence_focus': 0.1, 'pulse_duration': 100e-15},
    {'tag': 'b0100', 'label': 'Burst $N=100$',          'color': '#7E2F8E', 'marker': 'o', 'ls': '-',  'ms': 3.5,
     'fluence_focus': 0.1, 'pulse_duration': 100e-15},
    {'tag': 'b0500', 'label': 'Burst $N=500$',          'color': '#D95319', 'marker': 'v', 'ls': '-',  'ms': 3.5,
     'fluence_focus': 0.1, 'pulse_duration': 100e-15},
    {'tag': 'b1000', 'label': 'Burst $N=1000$',         'color': '#A2142F', 'marker': 'v', 'ls': '-',  'ms': 3.5,
     'fluence_focus': 0.1, 'pulse_duration': 100e-15},
]

# Damage threshold for fs pulses at 1064 nm (approximate)
FS_DAMAGE_THRESHOLD = 0.1   # J/cm^2

# Fixed parameters for analytical TPA efficiency
TARGET_RADIUS = 5e-6        # m  (target diameter = 10 um)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mat_path(alpha2_tag, pulse_tag, d_mm):
    d_um = round(d_mm * 1000)
    return os.path.join(RESULTS_DIR, f'{alpha2_tag}_{pulse_tag}_d{d_um:04d}um.mat')


def _legend(ax, **kw):
    defaults = dict(frameon=True, fancybox=False, framealpha=0.9,
                    edgecolor='0.8', fontsize=5.5, loc='upper right',
                    handlelength=1.5, handletextpad=0.4,
                    borderpad=0.3, labelspacing=0.25)
    defaults.update(kw)
    ax.legend(**defaults)


def _log_y_axis(ax):
    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=15))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=15))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())


# ---------------------------------------------------------------------------
# Figure 1: Peak pressure vs depth — panelled by alpha2
# ---------------------------------------------------------------------------

def fig_pressure_vs_depth(cache):
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0), constrained_layout=True)

    for i, a2 in enumerate(ALPHA2_LIST):
        ax = axes[i]
        for pc in PULSE_CONFIGS:
            depths, pressures = [], []
            for d_mm in DEPTHS_MM:
                key = (a2['tag'], pc['tag'], d_mm)
                if key in cache:
                    depths.append(d_mm)
                    pressures.append(cache[key]['peak_pressure'])
            if depths:
                ax.plot(depths, pressures,
                        color=pc['color'], marker=pc['marker'],
                        ls=pc['ls'], lw=1.0, ms=pc['ms'],
                        markeredgecolor='white', markeredgewidth=0.3,
                        label=pc['label'])

        ax.set_yscale('log')
        ax.set_xlabel('Target depth  (mm)')
        ax.set_ylabel('Peak PA pressure  (Pa)')
        ax.set_xlim(0, 1.05)
        ax.set_title(a2['label'], fontsize=7)
        _log_y_axis(ax)
        if i == 2:
            _legend(ax)

    return fig


# ---------------------------------------------------------------------------
# Figure 2: Surface energy vs depth — panelled by alpha2
# ---------------------------------------------------------------------------

def fig_energy_vs_depth(cache):
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0), constrained_layout=True)

    for i, a2 in enumerate(ALPHA2_LIST):
        ax = axes[i]
        for pc in PULSE_CONFIGS:
            depths, energies = [], []
            for d_mm in DEPTHS_MM:
                key = (a2['tag'], pc['tag'], d_mm)
                if key in cache and cache[key].get('E_surface') is not None:
                    depths.append(d_mm)
                    energies.append(cache[key]['E_surface'])
            if depths:
                ax.plot(depths, energies,
                        color=pc['color'], marker=pc['marker'],
                        ls=pc['ls'], lw=1.0, ms=pc['ms'],
                        markeredgecolor='white', markeredgewidth=0.3,
                        label=pc['label'])

        ax.set_yscale('log')
        ax.set_xlabel('Target depth  (mm)')
        ax.set_ylabel('Surface pulse energy  (J)')
        ax.set_xlim(0, 1.05)
        ax.set_title(a2['label'], fontsize=7)
        _log_y_axis(ax)
        if i == 2:
            _legend(ax)

    return fig


# ---------------------------------------------------------------------------
# Figure 3: Surface fluence vs depth — panelled by alpha2, damage threshold
# ---------------------------------------------------------------------------

def fig_fluence_vs_depth(cache):
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0), constrained_layout=True)

    for i, a2 in enumerate(ALPHA2_LIST):
        ax = axes[i]
        for pc in PULSE_CONFIGS:
            depths, fluences = [], []
            for d_mm in DEPTHS_MM:
                key = (a2['tag'], pc['tag'], d_mm)
                if key in cache and cache[key].get('F_surface') is not None:
                    depths.append(d_mm)
                    fluences.append(cache[key]['F_surface'])
            if depths:
                ax.plot(depths, fluences,
                        color=pc['color'], marker=pc['marker'],
                        ls=pc['ls'], lw=1.0, ms=pc['ms'],
                        markeredgecolor='white', markeredgewidth=0.3,
                        label=pc['label'])

        ax.axhline(FS_DAMAGE_THRESHOLD, color='red', lw=0.8, ls='--',
                   zorder=1, label=f'Damage threshold ({FS_DAMAGE_THRESHOLD} J/cm$^2$)')

        ax.set_yscale('log')
        ax.set_xlabel('Target depth  (mm)')
        ax.set_ylabel('Surface fluence  (J/cm$^2$)')
        ax.set_xlim(0, 1.05)
        ax.set_title(a2['label'], fontsize=7)
        _log_y_axis(ax)
        if i == 2:
            _legend(ax, fontsize=5)

    return fig


# ---------------------------------------------------------------------------
# Figure 4: Feasibility heatmap — depth x burst N, per alpha2
# ---------------------------------------------------------------------------

def fig_feasibility_heatmap(cache):
    burst_tags = ['fs', 'b0010', 'b0050', 'b0100', 'b0500', 'b1000']
    burst_labels = ['FS\n(N=1)', 'N=10', 'N=50', 'N=100', 'N=500', 'N=1000']
    n_burst = len(burst_tags)
    n_depth = len(DEPTHS_MM)

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.5), constrained_layout=True)

    for panel, a2 in enumerate(ALPHA2_LIST):
        ax = axes[panel]
        pressure_grid = np.full((n_burst, n_depth), np.nan)
        infeasible    = np.zeros((n_burst, n_depth), dtype=bool)

        for ib, btag in enumerate(burst_tags):
            for id_, d_mm in enumerate(DEPTHS_MM):
                key = (a2['tag'], btag, d_mm)
                if key in cache:
                    pressure_grid[ib, id_] = cache[key]['peak_pressure']
                    F_s = cache[key].get('F_surface')
                    if F_s is not None and F_s > FS_DAMAGE_THRESHOLD:
                        infeasible[ib, id_] = True

        valid = pressure_grid[np.isfinite(pressure_grid)]
        if valid.size == 0:
            ax.set_title(a2['label'], fontsize=7)
            continue

        vmin = max(valid.min(), 1e-3)
        vmax = valid.max()

        im = ax.pcolormesh(np.arange(n_depth + 1) - 0.5,
                           np.arange(n_burst + 1) - 0.5,
                           pressure_grid,
                           cmap='viridis', norm=LogNorm(vmin=vmin, vmax=vmax),
                           shading='flat', rasterized=True)

        # Hatch infeasible cells
        for ib in range(n_burst):
            for id_ in range(n_depth):
                if infeasible[ib, id_]:
                    ax.add_patch(plt.Rectangle((id_ - 0.5, ib - 0.5), 1, 1,
                                               fill=False, hatch='///',
                                               edgecolor='red', lw=0.5,
                                               zorder=3))

        ax.set_xticks(range(n_depth))
        ax.set_xticklabels([f'{d:.2f}' for d in DEPTHS_MM], fontsize=5.5)
        ax.set_yticks(range(n_burst))
        ax.set_yticklabels(burst_labels, fontsize=5.5)
        ax.set_xlabel('Depth  (mm)')
        if panel == 0:
            ax.set_ylabel('Pulse configuration')
        ax.set_title(a2['label'], fontsize=7)

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, aspect=20)
        cbar.set_label('Peak pressure  (Pa)', fontsize=6)
        cbar.ax.tick_params(labelsize=5.5)

    # Legend for hatching
    hatch_patch = Patch(facecolor='none', edgecolor='red', hatch='///',
                        label=f'$F_{{\\mathrm{{surface}}}}$ > {FS_DAMAGE_THRESHOLD} J/cm$^2$')
    axes[-1].legend(handles=[hatch_patch], loc='lower left',
                    fontsize=5.5, frameon=True, fancybox=False,
                    framealpha=0.9, edgecolor='0.8')

    return fig


# ---------------------------------------------------------------------------
# Figure 5: Ballistic transmission vs depth
# ---------------------------------------------------------------------------

def fig_transmission_vs_depth(cache):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    depths, trans = [], []
    for d_mm in DEPTHS_MM:
        # T_ballistic is tissue-only, same across pulse types and alpha2
        for a2 in ALPHA2_LIST:
            for pc in PULSE_CONFIGS:
                key = (a2['tag'], pc['tag'], d_mm)
                if key in cache and cache[key].get('T_ballistic') is not None:
                    depths.append(d_mm)
                    trans.append(cache[key]['T_ballistic'])
                    break
            if len(depths) > len(trans):
                continue
            break

    if depths:
        ax.plot(depths, trans,
                color='#0072BD', marker='o', ls='-', lw=1.0, ms=3.5,
                markeredgecolor='white', markeredgewidth=0.3)

    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Ballistic transmission  $T_{\\mathrm{bal}}$')
    ax.set_xlim(0, 1.05)
    _log_y_axis(ax)

    return fig


# ---------------------------------------------------------------------------
# Figure 6: TPA absorption efficiency vs depth — panelled by alpha2
# ---------------------------------------------------------------------------

def fig_tpa_efficiency_vs_depth(cache):
    """Fraction of incident (surface) pulse energy absorbed via TPA at focus.

    Analytical formula (Gaussian beam, thin target):
        eta_TPA = (alpha2 * I_focus * L_target / 2) * T_ballistic
    where I_focus = fluence_focus_si / pulse_duration, L_target = 2*target_radius,
    and the factor /2 accounts for the energy-weighted <I/I_peak> over the
    Gaussian cross-section.  For burst mode the per-pulse ratio is the same.
    """
    L_target = 2 * TARGET_RADIUS

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0), constrained_layout=True)

    for i, a2 in enumerate(ALPHA2_LIST):
        ax = axes[i]
        alpha2 = a2['value']

        for pc in PULSE_CONFIGS:
            fluence_si = pc['fluence_focus'] * 1e4          # J/cm² -> J/m²
            I_focus    = fluence_si / pc['pulse_duration']   # W/m²

            depths, etas = [], []
            for d_mm in DEPTHS_MM:
                key = (a2['tag'], pc['tag'], d_mm)
                if key in cache and cache[key].get('T_ballistic') is not None:
                    T_bal = cache[key]['T_ballistic']
                    eta   = (alpha2 * I_focus * L_target / 2) * T_bal
                    depths.append(d_mm)
                    etas.append(eta)

            if depths:
                ax.plot(depths, etas,
                        color=pc['color'], marker=pc['marker'],
                        ls=pc['ls'], lw=1.0, ms=pc['ms'],
                        markeredgecolor='white', markeredgewidth=0.3,
                        label=pc['label'])

        ax.set_yscale('log')
        ax.set_xlabel('Target depth  (mm)')
        ax.set_ylabel('TPA absorption efficiency  $\\xi_{\\mathrm{TPA}}$')
        ax.set_xlim(0, 1.05)
        ax.set_title(a2['label'], fontsize=7)
        _log_y_axis(ax)
        if i == 2:
            _legend(ax)

    return fig


# ---------------------------------------------------------------------------
# Cache builder
# ---------------------------------------------------------------------------

def _build_cache():
    cache = {}
    total = len(ALPHA2_LIST) * len(PULSE_CONFIGS) * len(DEPTHS_MM)
    idx = 0
    for a2 in ALPHA2_LIST:
        for pc in PULSE_CONFIGS:
            for d_mm in DEPTHS_MM:
                idx += 1
                path = _mat_path(a2['tag'], pc['tag'], d_mm)
                if os.path.isfile(path):
                    d = pav.load_results(path)
                    pp = float(np.max(np.abs(d['sensor_data'])))
                    entry = {
                        'peak_pressure': pp,
                        'T_ballistic':   d.get('T_ballistic'),
                        'E_surface':     d.get('E_surface'),
                        'F_surface':     d.get('F_surface'),
                        'E_focus':       d.get('E_focus'),
                    }
                    cache[(a2['tag'], pc['tag'], d_mm)] = entry
                    e_str = ''
                    if entry['E_surface'] is not None:
                        e_str = (f'  E_surf={entry["E_surface"]:.2e} J'
                                 f'  F_surf={entry["F_surface"]:.2e} J/cm²')
                    print(f'  [{idx:3d}/{total}] {a2["tag"]} {pc["tag"]:5s}'
                          f' @ {d_mm:.2f} mm  peak={pp:.3e} Pa{e_str}')
                else:
                    print(f'  [{idx:3d}/{total}] {a2["tag"]} {pc["tag"]:5s}'
                          f' @ {d_mm:.2f} mm  ->  MISSING')
    return cache


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description='Plot exp_009 results.')
    p.add_argument('--dpi',  type=int, default=300)
    p.add_argument('--fmt',  default='png', choices=['png', 'pdf', 'svg'])
    p.add_argument('--show', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    mpl.rcParams.update(pav.RC)
    os.makedirs(OUT_ROOT, exist_ok=True)

    print('Loading results...\n')
    cache = _build_cache()
    print(f'\n{len(cache)} entries loaded.\n')

    print('Peak pressure vs depth...')
    fig = fig_pressure_vs_depth(cache)
    p = os.path.join(OUT_ROOT, f'peak_pressure_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Surface energy vs depth...')
    fig = fig_energy_vs_depth(cache)
    p = os.path.join(OUT_ROOT, f'energy_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Surface fluence vs depth...')
    fig = fig_fluence_vs_depth(cache)
    p = os.path.join(OUT_ROOT, f'fluence_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Feasibility heatmap...')
    fig = fig_feasibility_heatmap(cache)
    p = os.path.join(OUT_ROOT, f'feasibility_heatmap.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Ballistic transmission vs depth...')
    fig = fig_transmission_vs_depth(cache)
    p = os.path.join(OUT_ROOT, f'transmission_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('TPA absorption efficiency vs depth...')
    fig = fig_tpa_efficiency_vs_depth(cache)
    p = os.path.join(OUT_ROOT, f'tpa_efficiency_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    if args.show:
        plt.show()

    print('\nDone.')


if __name__ == '__main__':
    main()
