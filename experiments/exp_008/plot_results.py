"""
exp_008/plot_results.py  --  Figures for burst rate comparison (100 GHz vs 1 THz).

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

HERE        = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, 'results')
OUT_ROOT    = os.path.join(r'C:\Users\SYAVAS-LASERLAB\Documents\LAB_PC_DRIVE', 'exp_008')

sys.path.insert(0, os.path.join(HERE, '..', '..'))
import pa_visualize as pav

# ---------------------------------------------------------------------------
# Experiment grid
# ---------------------------------------------------------------------------
DEPTHS_MM = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

CONFIGS = [
    {'tag': 'b0100', 'label': 'Burst $N=100$ (100 GHz)',
     'color': '#0072BD', 'marker': 'o', 'ls': '-',  'ms': 4},
    {'tag': 'b1000', 'label': 'Burst $N=1000$ (1 THz)',
     'color': '#A2142F', 'marker': 'v', 'ls': '-',  'ms': 4},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mat_path(tag, d_mm):
    return os.path.join(RESULTS_DIR, f'{tag}_d{round(d_mm * 1000):04d}um.mat')


def _peak_pressure(mat_path):
    d = pav.load_results(mat_path)
    return float(np.max(np.abs(d['sensor_data'])))


def _legend(ax, **kw):
    defaults = dict(frameon=True, fancybox=False, framealpha=0.9,
                    edgecolor='0.8', fontsize=6, loc='upper right',
                    handlelength=1.5, handletextpad=0.4,
                    borderpad=0.3, labelspacing=0.25)
    defaults.update(kw)
    ax.legend(**defaults)


# ---------------------------------------------------------------------------
# Figure 1: Peak pressure vs depth
# ---------------------------------------------------------------------------

def fig_pressure_vs_depth(cache):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    for cfg in CONFIGS:
        depths, pressures = [], []
        for d_mm in DEPTHS_MM:
            key = (cfg['tag'], d_mm)
            if key in cache:
                depths.append(d_mm)
                pressures.append(cache[key])
        if depths:
            ax.plot(depths, pressures,
                    color=cfg['color'], marker=cfg['marker'],
                    ls=cfg['ls'], lw=1.0, ms=cfg['ms'],
                    markeredgecolor='white', markeredgewidth=0.3,
                    label=cfg['label'])

    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Peak PA pressure  (Pa)')
    ax.set_xlim(0, 3.15)

    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    _legend(ax)
    return fig


# ---------------------------------------------------------------------------
# Figure 2: Enhancement (N=1000 / N=100) vs depth
# ---------------------------------------------------------------------------

def fig_enhancement_vs_depth(cache):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    depths_plot, enhancement = [], []
    for d_mm in DEPTHS_MM:
        key_100  = ('b0100', d_mm)
        key_1000 = ('b1000', d_mm)
        if key_100 in cache and key_1000 in cache and cache[key_100] > 0:
            depths_plot.append(d_mm)
            enhancement.append(cache[key_1000] / cache[key_100])

    ax.plot(depths_plot, enhancement,
            color='#0072BD', marker='o', ls='-', lw=1.0, ms=3.5,
            markeredgecolor='white', markeredgewidth=0.3,
            label='$N=1000$ / $N=100$')

    ax.axhline(10, color='0.6', lw=0.6, ls='--', zorder=1, label='Theoretical ($10\\times$)')

    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Enhancement  ($N=1000$ / $N=100$)')
    ax.set_xlim(0, 3.15)

    _legend(ax)
    return fig


# ---------------------------------------------------------------------------
# Figure 3: Waveform comparison at a single depth
# ---------------------------------------------------------------------------

WAVEFORM_CONFIGS = [
    {'tag': 'b0100', 'label': 'Burst $N=100$ (100 GHz)', 'color': '#0072BD'},
    {'tag': 'b1000', 'label': 'Burst $N=1000$ (1 THz)',  'color': '#A2142F'},
]

def fig_waveform_comparison(d_mm):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    for cfg in WAVEFORM_CONFIGS:
        path = _mat_path(cfg['tag'], d_mm)
        if not os.path.isfile(path):
            continue
        d = pav.load_results(path)
        t_us = d['t_array'] * 1e6
        c = d['c_sound']
        z_tgt = d['target_depth']
        f_t = d['f_grid']
        element_y = d['element_y']

        center_idx = int(np.argmin(np.abs(element_y)))
        trace = d['sensor_data'][center_idx, :].copy()

        t_arrive = z_tgt / c * 1e6
        margin = 10.0 / f_t * 1e6
        mask = (t_us >= t_arrive - margin) & (t_us <= t_arrive + margin)
        first = int(np.argmax(mask))
        trace -= trace[first]

        ax.plot(t_us[mask], trace[mask], color=cfg['color'], lw=0.8,
                label=cfg['label'])

    ax.axhline(0, color='0.6', lw=0.4, zorder=1)
    ax.set_xlabel('Time  ($\\mu$s)')
    ax.set_ylabel('Pressure  (Pa)')
    ax.set_title(f'$d = {d_mm:.1f}$ mm', fontsize=7)
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    _legend(ax)
    return fig


# ---------------------------------------------------------------------------
# Figure 4: p0 map comparison (N=100 vs N=1000)
# ---------------------------------------------------------------------------

def fig_p0_comparison(d_mm):
    from matplotlib.colors import LogNorm
    from matplotlib.patches import Circle

    tags   = ['b0100', 'b1000']
    labels = ['Burst $N=100$ (100 GHz)', 'Burst $N=1000$ (1 THz)']

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), constrained_layout=True)

    datasets = []
    for tag in tags:
        path = _mat_path(tag, d_mm)
        d = pav.load_results(path)
        datasets.append(d)

    for i, (d, tag, label) in enumerate(zip(datasets, tags, labels)):
        ax = axes[i]
        p0 = d['p0_opt']
        y_um = d['y_opt_vec'] * 1e6
        z_rel_um = (d['z_opt_vec'] - d['target_depth']) * 1e6
        r_tgt_um = d['target_radius'] * 1e6

        positive = p0[p0 > 0]
        if positive.size == 0:
            ax.text(0.5, 0.5, 'No signal', transform=ax.transAxes,
                    ha='center', va='center', fontsize=8, color='0.5')
            ax.set_title(label, fontsize=7)
            continue

        vmax = positive.max()
        vmin = max(positive.min(), vmax * 1e-4)
        norm = LogNorm(vmin=vmin, vmax=vmax)

        data_plot = np.where(p0 > 0, p0, np.nan)
        im = ax.pcolormesh(y_um, z_rel_um, data_plot,
                           cmap='inferno', norm=norm,
                           shading='auto', rasterized=True)
        ax.set_facecolor('black')

        circle = Circle((0, 0), r_tgt_um,
                         ec='white', fc='none', lw=0.5, ls='--',
                         alpha=0.7, zorder=5, label='Target boundary')
        ax.add_patch(circle)
        ax.axhline(0, color='white', lw=0.4, ls=':', alpha=0.5, zorder=4)
        ax.axvline(0, color='white', lw=0.4, ls=':', alpha=0.5, zorder=4)
        ax.legend(frameon=True, fancybox=False, framealpha=0.7,
                  edgecolor='0.5', fontsize=4.5, loc='upper right',
                  handlelength=1.2, handletextpad=0.3,
                  borderpad=0.2, labelspacing=0.2)

        ax.set_aspect('equal')
        ax.set_xlim(y_um[[0, -1]])
        ax.set_ylim(z_rel_um[[0, -1]])
        ax.set_xlabel('$y$  ($\\mu$m)')
        if i == 0:
            ax.set_ylabel('$z - z_{\\mathrm{foc}}$  ($\\mu$m)')
        ax.set_title(f'{label}  \u2014  $d = {d_mm:.1f}$ mm', fontsize=7)

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, aspect=20)
        cbar.set_label('$p_0$  (Pa)', fontsize=6)
        cbar.ax.tick_params(labelsize=5.5)

    return fig


# ---------------------------------------------------------------------------
# Physical constants for temperature calculation
# ---------------------------------------------------------------------------
RHO = 1000.0     # density [kg/m^3]
CP  = 4186.0     # specific heat capacity of water [J/(kg*K)]


# ---------------------------------------------------------------------------
# Figure 5: dT map comparison (N=100 vs N=1000), zoomed near absorber
# ---------------------------------------------------------------------------

def fig_dT_comparison(d_mm):
    from matplotlib.colors import LogNorm
    from matplotlib.patches import Circle

    tags   = ['b0100', 'b1000']
    labels = ['Burst $N=100$ (100 GHz)', 'Burst $N=1000$ (1 THz)']

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), constrained_layout=True)

    datasets = []
    for tag in tags:
        path = _mat_path(tag, d_mm)
        d = pav.load_results(path)
        datasets.append(d)

    for i, (d, tag, label) in enumerate(zip(datasets, tags, labels)):
        ax = axes[i]
        dT = d['Q_opt'] / (RHO * CP)            # temperature rise [K]
        y_um = d['y_opt_vec'] * 1e6
        z_rel_um = (d['z_opt_vec'] - d['target_depth']) * 1e6
        r_tgt_um = d['target_radius'] * 1e6

        # Zoom: ±3 target radii around the focus
        zoom = 3 * r_tgt_um
        y_mask = (y_um >= -zoom) & (y_um <= zoom)
        z_mask = (z_rel_um >= -zoom) & (z_rel_um <= zoom)
        dT_zoom = dT[np.ix_(z_mask, y_mask)]
        y_zoom  = y_um[y_mask]
        z_zoom  = z_rel_um[z_mask]

        positive = dT_zoom[dT_zoom > 0]
        if positive.size == 0:
            ax.text(0.5, 0.5, 'No signal', transform=ax.transAxes,
                    ha='center', va='center', fontsize=8, color='0.5')
            ax.set_title(label, fontsize=7)
            continue

        vmax = positive.max()
        vmin = max(positive.min(), vmax * 1e-4)
        norm = LogNorm(vmin=vmin, vmax=vmax)

        data_plot = np.where(dT_zoom > 0, dT_zoom, np.nan)
        im = ax.pcolormesh(y_zoom, z_zoom, data_plot,
                           cmap='inferno', norm=norm,
                           shading='auto', rasterized=True)
        ax.set_facecolor('black')

        circle = Circle((0, 0), r_tgt_um,
                         ec='white', fc='none', lw=0.5, ls='--',
                         alpha=0.7, zorder=5, label='Target boundary')
        ax.add_patch(circle)
        ax.axhline(0, color='white', lw=0.4, ls=':', alpha=0.5, zorder=4)
        ax.axvline(0, color='white', lw=0.4, ls=':', alpha=0.5, zorder=4)
        ax.legend(frameon=True, fancybox=False, framealpha=0.7,
                  edgecolor='0.5', fontsize=4.5, loc='upper right',
                  handlelength=1.2, handletextpad=0.3,
                  borderpad=0.2, labelspacing=0.2)

        ax.set_aspect('equal')
        ax.set_xlim(y_zoom[[0, -1]])
        ax.set_ylim(z_zoom[[0, -1]])
        ax.set_xlabel('$y$  ($\\mu$m)')
        if i == 0:
            ax.set_ylabel('$z - z_{\\mathrm{foc}}$  ($\\mu$m)')

        peak_dT = vmax
        unit, scale = ('mK', 1e3) if peak_dT < 1 else ('K', 1)
        ax.set_title(f'{label}  \u2014  $d = {d_mm:.1f}$ mm\n'
                     f'peak $\\Delta T = {peak_dT * scale:.2f}$ {unit}',
                     fontsize=7)

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, aspect=20)
        cbar.set_label('$\\Delta T$  (K)', fontsize=6)
        cbar.ax.tick_params(labelsize=5.5)

    return fig


# ---------------------------------------------------------------------------
# Figure 6: Peak dT vs depth
# ---------------------------------------------------------------------------

def fig_peak_dT_vs_depth(dT_cache):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    for cfg in CONFIGS:
        depths, temps = [], []
        for d_mm in DEPTHS_MM:
            key = (cfg['tag'], d_mm)
            if key in dT_cache:
                depths.append(d_mm)
                temps.append(dT_cache[key])
        if depths:
            ax.plot(depths, temps,
                    color=cfg['color'], marker=cfg['marker'],
                    ls=cfg['ls'], lw=1.0, ms=cfg['ms'],
                    markeredgecolor='white', markeredgewidth=0.3,
                    label=cfg['label'])

    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Peak $\\Delta T$  (K)')
    ax.set_xlim(0, 3.15)

    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    _legend(ax)
    return fig


# ---------------------------------------------------------------------------
# Figure 7: Surface pulse energy vs depth
# ---------------------------------------------------------------------------

def fig_energy_vs_depth(energy_cache):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), constrained_layout=True)

    # Left panel: E_surface (per pulse)
    ax = axes[0]
    for cfg in CONFIGS:
        depths, energies = [], []
        for d_mm in DEPTHS_MM:
            key = (cfg['tag'], d_mm)
            if key in energy_cache:
                depths.append(d_mm)
                energies.append(energy_cache[key]['E_surface'])
        if depths:
            ax.plot(depths, energies,
                    color=cfg['color'], marker=cfg['marker'],
                    ls=cfg['ls'], lw=1.0, ms=cfg['ms'],
                    markeredgecolor='white', markeredgewidth=0.3,
                    label=cfg['label'])

    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Surface pulse energy  (J)')
    ax.set_xlim(0, 3.15)
    ax.set_title('Required $E_{\\mathrm{surface}}$ per pulse', fontsize=7)
    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())
    _legend(ax)

    # Right panel: F_surface
    ax = axes[1]
    for cfg in CONFIGS:
        depths, fluences = [], []
        for d_mm in DEPTHS_MM:
            key = (cfg['tag'], d_mm)
            if key in energy_cache:
                depths.append(d_mm)
                fluences.append(energy_cache[key]['F_surface'])
        if depths:
            ax.plot(depths, fluences,
                    color=cfg['color'], marker=cfg['marker'],
                    ls=cfg['ls'], lw=1.0, ms=cfg['ms'],
                    markeredgecolor='white', markeredgewidth=0.3,
                    label=cfg['label'])

    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Surface fluence  (J/cm$^2$)')
    ax.set_xlim(0, 3.15)
    ax.set_title('Required $F_{\\mathrm{surface}}$ per pulse', fontsize=7)
    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())
    _legend(ax)

    return fig


# ---------------------------------------------------------------------------
# Figure 8: Ballistic transmission vs depth
# ---------------------------------------------------------------------------

def fig_transmission_vs_depth(energy_cache):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    # T_ballistic is the same for both pulse types (same tissue), use first available
    depths, trans = [], []
    for d_mm in DEPTHS_MM:
        for tag in ['b0100', 'b1000']:
            key = (tag, d_mm)
            if key in energy_cache:
                depths.append(d_mm)
                trans.append(energy_cache[key]['T_ballistic'])
                break

    if depths:
        ax.plot(depths, trans,
                color='#0072BD', marker='o', ls='-', lw=1.0, ms=3.5,
                markeredgecolor='white', markeredgewidth=0.3)

    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Ballistic transmission  $T$')
    ax.set_xlim(0, 3.15)
    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    return fig


# ---------------------------------------------------------------------------
# Cache builder
# ---------------------------------------------------------------------------

def _build_cache():
    cache = {}
    dT_cache = {}
    energy_cache = {}       # (tag, d_mm) -> dict with E_surface, F_surface, T_ballistic
    all_tags = ['b0100', 'b1000']
    total = len(all_tags) * len(DEPTHS_MM)
    idx = 0
    for tag in all_tags:
        for d_mm in DEPTHS_MM:
            idx += 1
            path = _mat_path(tag, d_mm)
            if os.path.isfile(path):
                d = pav.load_results(path)
                pp = float(np.max(np.abs(d['sensor_data'])))
                peak_dT = float(np.max(d['Q_opt'])) / (RHO * CP)
                cache[(tag, d_mm)] = pp
                dT_cache[(tag, d_mm)] = peak_dT
                if d.get('E_surface') is not None:
                    energy_cache[(tag, d_mm)] = {
                        'E_surface':   d['E_surface'],
                        'F_surface':   d['F_surface'],
                        'T_ballistic': d['T_ballistic'],
                        'E_focus':     d['E_focus'],
                    }
                e_str = ''
                if d.get('E_surface') is not None:
                    e_str = f'  E_surf={d["E_surface"]:.2e} J  F_surf={d["F_surface"]:.2e} J/cm²'
                print(f'  [{idx:3d}/{total}] {tag:6s} @ {d_mm:.1f} mm  '
                      f'peak={pp:.3e} Pa  dT={peak_dT:.3e} K{e_str}')
            else:
                print(f'  [{idx:3d}/{total}] {tag:6s} @ {d_mm:.1f} mm  ->  MISSING')
    return cache, dT_cache, energy_cache


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description='Plot exp_008 results.')
    p.add_argument('--dpi',  type=int, default=300)
    p.add_argument('--fmt',  default='png', choices=['png', 'pdf', 'svg'])
    p.add_argument('--show', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    mpl.rcParams.update(pav.RC)
    os.makedirs(OUT_ROOT, exist_ok=True)

    print('Loading pressures...\n')
    peak_cache, dT_cache, energy_cache = _build_cache()
    print(f'\n{len(peak_cache)} entries loaded.\n')

    print('Peak pressure vs depth...')
    fig = fig_pressure_vs_depth(peak_cache)
    p = os.path.join(OUT_ROOT, f'peak_pressure_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Peak dT vs depth...')
    fig = fig_peak_dT_vs_depth(dT_cache)
    p = os.path.join(OUT_ROOT, f'peak_dT_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Enhancement vs depth...')
    fig = fig_enhancement_vs_depth(peak_cache)
    p = os.path.join(OUT_ROOT, f'enhancement_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    for wf_depth in [1.0, 3.0]:
        print(f'Waveform comparison at {wf_depth} mm...')
        fig = fig_waveform_comparison(wf_depth)
        p = os.path.join(OUT_ROOT, f'waveform_comparison_{wf_depth:.1f}mm.{args.fmt}')
        fig.savefig(p, dpi=args.dpi); plt.close(fig)
        print(f'  Saved -> {p}')

    for p0_depth in [1.0, 3.0]:
        print(f'p0 map comparison at {p0_depth} mm...')
        fig = fig_p0_comparison(p0_depth)
        p = os.path.join(OUT_ROOT, f'p0_comparison_{p0_depth:.1f}mm.{args.fmt}')
        fig.savefig(p, dpi=args.dpi); plt.close(fig)
        print(f'  Saved -> {p}')

    for dt_depth in [1.0, 3.0]:
        print(f'dT map comparison at {dt_depth} mm...')
        fig = fig_dT_comparison(dt_depth)
        p = os.path.join(OUT_ROOT, f'dT_comparison_{dt_depth:.1f}mm.{args.fmt}')
        fig.savefig(p, dpi=args.dpi); plt.close(fig)
        print(f'  Saved -> {p}')

    if energy_cache:
        print('Surface energy vs depth...')
        fig = fig_energy_vs_depth(energy_cache)
        p = os.path.join(OUT_ROOT, f'energy_vs_depth.{args.fmt}')
        fig.savefig(p, dpi=args.dpi); plt.close(fig)
        print(f'  Saved -> {p}')

        print('Ballistic transmission vs depth...')
        fig = fig_transmission_vs_depth(energy_cache)
        p = os.path.join(OUT_ROOT, f'transmission_vs_depth.{args.fmt}')
        fig.savefig(p, dpi=args.dpi); plt.close(fig)
        print(f'  Saved -> {p}')

    if args.show:
        plt.show()

    print('\nDone.')


if __name__ == '__main__':
    main()
