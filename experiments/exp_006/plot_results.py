"""
exp_006/plot_results.py  --  Publication figures for depth & signal study.

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
OUT_ROOT    = os.path.join(r'C:\Users\SYAVAS-LASERLAB\Documents\LAB_PC_DRIVE', 'exp_006')

sys.path.insert(0, os.path.join(HERE, '..', '..'))
import pa_visualize as pav

# ---------------------------------------------------------------------------
# Experiment grid
# ---------------------------------------------------------------------------
DEPTHS_MM = [round(d, 1) for d in np.arange(0.1, 3.01, 0.1).tolist()]

BURST_N_VALUES = list(range(20, 301, 20))

CONFIGS = [
    {'tag': 'ns',   'label': 'NS (3 ns, 10 J cm$^{-2}$)',
     'color': '#D95319', 'marker': 's', 'ls': '-',  'ms': 3},
    {'tag': 'fs',   'label': 'FS (100 fs, 1 J cm$^{-2}$)',
     'color': '#77AC30', 'marker': '^', 'ls': '-',  'ms': 3},
    {'tag': 'b060', 'label': 'Burst $N=60$',
     'color': '#0072BD', 'marker': 'o', 'ls': '-',  'ms': 2.5},
    {'tag': 'b160', 'label': 'Burst $N=160$',
     'color': '#7E2F8E', 'marker': 'D', 'ls': '-',  'ms': 2.5},
    {'tag': 'b300', 'label': 'Burst $N=300$',
     'color': '#A2142F', 'marker': 'v', 'ls': '-',  'ms': 2.5},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mat_path(tag, d_mm):
    return os.path.join(RESULTS_DIR, f'{tag}_d{round(d_mm * 1000):04d}um.mat')


def _peak_pressure(mat_path):
    d = pav.load_results(mat_path)
    return float(np.max(np.abs(d['sensor_data'])))


# ---------------------------------------------------------------------------
# Figure 1: Peak pressure vs depth
# ---------------------------------------------------------------------------

def fig_pressure_vs_depth(cache, ylabel='Peak PA pressure  (Pa)'):
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
                    markevery=3, label=cfg['label'])

    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, 3.15)

    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    ax.legend(frameon=True, fancybox=False, framealpha=0.9,
              edgecolor='0.8', fontsize=6, loc='upper right',
              handlelength=1.5, handletextpad=0.4,
              borderpad=0.3, labelspacing=0.25)

    return fig


# ---------------------------------------------------------------------------
# Figure 2: Enhancement vs depth
# ---------------------------------------------------------------------------

def fig_enhancement_vs_depth(cache):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    depths_plot, enhancement = [], []
    for d_mm in DEPTHS_MM:
        ns_key = ('ns', d_mm)
        if ns_key not in cache or cache[ns_key] <= 0:
            continue
        val_ns = cache[ns_key]
        best_val = 0
        for N in BURST_N_VALUES:
            key = (f'b{N:03d}', d_mm)
            if key in cache and cache[key] > best_val:
                best_val = cache[key]
        if best_val > 0:
            depths_plot.append(d_mm)
            enhancement.append(best_val / val_ns)

    ax.plot(depths_plot, enhancement,
            color='#0072BD', marker='o', ls='-', lw=1.0, ms=2.5,
            markeredgecolor='white', markeredgewidth=0.3,
            label='Best burst / NS')

    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Enhancement  (max burst / NS)')
    ax.set_xlim(0, 3.15)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f'{x/1000:.0f}k' if x >= 1000 else f'{x:.0f}'))

    ax.legend(frameon=True, fancybox=False, framealpha=0.9,
              edgecolor='0.8', fontsize=5.5, loc='upper right',
              handlelength=1.2, handletextpad=0.3,
              borderpad=0.25, labelspacing=0.2)

    return fig


# ---------------------------------------------------------------------------
# Figure 3: Waveform comparison at a single depth
# ---------------------------------------------------------------------------

WAVEFORM_CONFIGS = [
    {'tag': 'ns',   'label': 'NS (3 ns)',      'color': '#D95319'},
    {'tag': 'fs',   'label': 'FS (100 fs)',     'color': '#77AC30'},
    {'tag': 'b300', 'label': 'Burst $N=300$',   'color': '#A2142F'},
]

def fig_waveform_comparison(d_mm):
    """Overlay waveforms from NS, FS, and burst at a single depth."""
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

        # Zoom window
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
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    ax.legend(frameon=True, fancybox=False, framealpha=0.9,
              edgecolor='0.8', fontsize=6, loc='upper right',
              handlelength=1.5, handletextpad=0.4,
              borderpad=0.3, labelspacing=0.25)

    return fig


# ---------------------------------------------------------------------------
# Figure 4: p0 map comparison (NS vs burst)
# ---------------------------------------------------------------------------

def fig_p0_comparison(d_mm):
    """Separate p0 maps for NS and burst N=300 at a given depth, each with own colorbar."""
    from matplotlib.colors import LogNorm
    from matplotlib.patches import Circle

    tags   = ['ns', 'b300']
    labels = ['NS (3 ns, 10 J cm$^{-2}$)', 'Burst $N=300$ (100 fs, 1 J cm$^{-2}$)']

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
                         ec='white', fc='none', lw=0.7, ls='--', zorder=5)
        ax.add_patch(circle)
        ax.axhline(0, color='white', lw=0.4, ls=':', alpha=0.5, zorder=4)
        ax.axvline(0, color='white', lw=0.4, ls=':', alpha=0.5, zorder=4)

        ax.set_aspect('equal')
        ax.set_xlim(y_um[[0, -1]])
        ax.set_ylim(z_rel_um[[0, -1]])
        ax.set_xlabel('$y$  ($\\mu$m)')
        if i == 0:
            ax.set_ylabel('$z - z_{\\mathrm{foc}}$  ($\\mu$m)')
        ax.set_title(f'{label}  —  $d = {d_mm:.1f}$ mm', fontsize=7)

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, aspect=20)
        cbar.set_label('$p_0$  (Pa)', fontsize=6)
        cbar.ax.tick_params(labelsize=5.5)

    return fig


# ---------------------------------------------------------------------------
# Figure 5: Enhancement vs N at fixed depths
# ---------------------------------------------------------------------------

ENHANCEMENT_DEPTHS = [0.5, 1.0, 2.0]
ENHANCEMENT_COLORS = ['#0072BD', '#D95319', '#7E2F8E']

def fig_enhancement_vs_N(cache):
    """Enhancement (burst / NS) vs pulse count N at selected depths."""
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    for d_mm, color in zip(ENHANCEMENT_DEPTHS, ENHANCEMENT_COLORS):
        ns_key = ('ns', d_mm)
        if ns_key not in cache or cache[ns_key] <= 0:
            continue
        val_ns = cache[ns_key]

        N_vals, enh_vals = [], []
        for N in BURST_N_VALUES:
            key = (f'b{N:03d}', d_mm)
            if key in cache:
                N_vals.append(N)
                enh_vals.append(cache[key] / val_ns)

        if N_vals:
            ax.plot(N_vals, enh_vals, color=color, marker='o',
                    ls='-', lw=1.0, ms=2.5,
                    markeredgecolor='white', markeredgewidth=0.3,
                    label=f'{d_mm:.1f} mm')

    ax.set_xlabel('Burst pulse count  $N$')
    ax.set_ylabel('Enhancement  (burst / NS)')
    ax.set_xlim(0, 310)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f'{x/1000:.0f}k' if x >= 1000 else f'{x:.0f}'))

    ax.legend(frameon=True, fancybox=False, framealpha=0.9,
              edgecolor='0.8', fontsize=6, loc='upper left',
              title='Depth', title_fontsize=6,
              handlelength=1.5, handletextpad=0.4,
              borderpad=0.3, labelspacing=0.25)

    return fig


# ---------------------------------------------------------------------------
# Cache builder
# ---------------------------------------------------------------------------

def _build_cache():
    cache = {}
    all_tags = ['ns', 'fs'] + [f'b{N:03d}' for N in BURST_N_VALUES]
    total = len(all_tags) * len(DEPTHS_MM)
    idx = 0
    for tag in all_tags:
        for d_mm in DEPTHS_MM:
            idx += 1
            path = _mat_path(tag, d_mm)
            if os.path.isfile(path):
                pp = _peak_pressure(path)
                cache[(tag, d_mm)] = pp
                print(f'  [{idx:3d}/{total}] {tag:6s} @ {d_mm:.1f} mm  peak={pp:.3e} Pa')
            else:
                print(f'  [{idx:3d}/{total}] {tag:6s} @ {d_mm:.1f} mm  ->  MISSING')
    return cache


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description='Plot exp_006 results.')
    p.add_argument('--dpi',  type=int, default=300)
    p.add_argument('--fmt',  default='png', choices=['png', 'pdf', 'svg'])
    p.add_argument('--show', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    mpl.rcParams.update(pav.RC)
    os.makedirs(OUT_ROOT, exist_ok=True)

    print('Loading pressures...\n')
    peak_cache = _build_cache()
    print(f'\n{len(peak_cache)} entries loaded.\n')

    print('Peak pressure vs depth...')
    fig = fig_pressure_vs_depth(peak_cache)
    p = os.path.join(OUT_ROOT, f'peak_pressure_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Enhancement vs depth...')
    fig = fig_enhancement_vs_depth(peak_cache)
    p = os.path.join(OUT_ROOT, f'enhancement_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    wf_depth = 1.0  # mm
    print(f'Waveform comparison at {wf_depth} mm...')
    fig = fig_waveform_comparison(wf_depth)
    p = os.path.join(OUT_ROOT, f'waveform_comparison_{wf_depth:.0f}mm.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    p0_depth = 3.0  # mm
    print(f'p0 map comparison at {p0_depth} mm...')
    fig = fig_p0_comparison(p0_depth)
    p = os.path.join(OUT_ROOT, f'p0_comparison_{p0_depth:.1f}mm.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Enhancement vs N...')
    fig = fig_enhancement_vs_N(peak_cache)
    p = os.path.join(OUT_ROOT, f'enhancement_vs_N.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    if args.show:
        plt.show()

    print('\nDone.')


if __name__ == '__main__':
    main()
