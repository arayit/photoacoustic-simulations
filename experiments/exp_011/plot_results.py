"""
exp_011/plot_results.py  --  Si NP FCA enhancement study figures.

Figures:
  1. Peak pressure vs depth (all 5 pulse types)
  2. Enhancement vs depth (burst modes normalized to NS)
  3. Heat deposition breakdown at focus (grouped bar, fixed depth)
  4. FCA fraction vs N (one curve per depth)
  5. Heat breakdown vs depth (for N=1000, log scale)

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
OUT_ROOT    = os.path.join(r'C:\Users\SYAVAS-LASERLAB\Documents\LAB_PC_DRIVE', 'exp_011')

sys.path.insert(0, os.path.join(HERE, '..', '..'))
import pa_visualize as pav

# ---------------------------------------------------------------------------
# Experiment grid
# ---------------------------------------------------------------------------
DEPTHS_MM = [0.1, 0.2, 0.4, 0.6, 1.0]

CONFIGS = [
    {'tag': 'ns',    'label': 'NS (1 ns)',
     'color': '#77AC30', 'marker': 's', 'ls': '--', 'ms': 4},
    {'tag': 'fs',    'label': 'FS (100 fs)',
     'color': '#EDB120', 'marker': 'd', 'ls': '--', 'ms': 4},
    {'tag': 'b0100', 'label': 'Burst $N=100$',
     'color': '#0072BD', 'marker': 'o', 'ls': '-',  'ms': 4},
    {'tag': 'b0500', 'label': 'Burst $N=500$',
     'color': '#D95319', 'marker': '^', 'ls': '-',  'ms': 4},
    {'tag': 'b1000', 'label': 'Burst $N=1000$',
     'color': '#A2142F', 'marker': 'v', 'ls': '-',  'ms': 4},
]

BURST_CONFIGS = [c for c in CONFIGS if c['tag'].startswith('b')]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mat_path(tag, d_mm):
    return os.path.join(RESULTS_DIR, f'{tag}_d{round(d_mm * 1000):04d}um.mat')


def _load_heat_breakdown(mat_path):
    """Load Q_linear, Q_tpa, Q_fca maps saved by the engine."""
    import h5py

    def _arr(node):
        a = node[()]
        return a.T.astype(np.float64) if a.ndim >= 2 else np.asarray(a, dtype=np.float64).ravel()

    with h5py.File(mat_path, 'r') as f:
        r = f['results']
        return {
            'Q_linear': _arr(r['Q_linear']),
            'Q_tpa':    _arr(r['Q_tpa']),
            'Q_fca':    _arr(r['Q_fca']),
        }


def _peak_heat(mat_path):
    """Return peak values of Q_linear, Q_tpa, Q_fca from the engine output."""
    hb = _load_heat_breakdown(mat_path)
    return (float(np.max(hb['Q_linear'])),
            float(np.max(hb['Q_tpa'])),
            float(np.max(hb['Q_fca'])))


def _legend(ax, **kw):
    defaults = dict(frameon=True, fancybox=False, framealpha=0.9,
                    edgecolor='0.8', fontsize=6, loc='upper right',
                    handlelength=1.5, handletextpad=0.4,
                    borderpad=0.3, labelspacing=0.25)
    defaults.update(kw)
    ax.legend(**defaults)


# ---------------------------------------------------------------------------
# Figure 1: Peak pressure vs depth (all pulse types)
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
    ax.set_xlim(0, 1.1)

    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    _legend(ax)
    return fig


# ---------------------------------------------------------------------------
# Figure 2: Enhancement vs depth (burst / NS)
# ---------------------------------------------------------------------------

def fig_enhancement_vs_depth(cache):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    for cfg in BURST_CONFIGS:
        depths_plot, enhancement = [], []
        for d_mm in DEPTHS_MM:
            key_ns   = ('ns', d_mm)
            key_burst = (cfg['tag'], d_mm)
            if key_ns in cache and key_burst in cache and cache[key_ns] > 0:
                depths_plot.append(d_mm)
                enhancement.append(cache[key_burst] / cache[key_ns])

        if depths_plot:
            ax.plot(depths_plot, enhancement,
                    color=cfg['color'], marker=cfg['marker'],
                    ls=cfg['ls'], lw=1.0, ms=cfg['ms'],
                    markeredgecolor='white', markeredgewidth=0.3,
                    label=cfg['label'])

    # Also show single FS / NS
    depths_fs, enh_fs = [], []
    for d_mm in DEPTHS_MM:
        if ('fs', d_mm) in cache and ('ns', d_mm) in cache and cache[('ns', d_mm)] > 0:
            depths_fs.append(d_mm)
            enh_fs.append(cache[('fs', d_mm)] / cache[('ns', d_mm)])
    if depths_fs:
        ax.plot(depths_fs, enh_fs,
                color='#EDB120', marker='d', ls='--', lw=1.0, ms=4,
                markeredgecolor='white', markeredgewidth=0.3,
                label='Single FS')

    ax.axhline(1, color='0.6', lw=0.6, ls=':', zorder=1)
    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Enhancement  (vs NS pulse)')
    ax.set_xlim(0, 1.1)

    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    _legend(ax)
    return fig


# ---------------------------------------------------------------------------
# Figure 3: Heat deposition breakdown (grouped bar at fixed depth)
# ---------------------------------------------------------------------------

def fig_heat_breakdown_bar(heat_cache, depth_mm=0.4):
    fig, ax = plt.subplots(figsize=(4.0, 2.8), constrained_layout=True)

    tags_order = ['ns', 'fs', 'b0100', 'b0500', 'b1000']
    labels     = ['NS', 'FS', 'N=100', 'N=500', 'N=1000']
    x = np.arange(len(tags_order))
    width = 0.25

    q_lin_vals, q_tpa_vals, q_fca_vals = [], [], []
    for tag in tags_order:
        key = (tag, depth_mm)
        if key in heat_cache:
            ql, qt, qf = heat_cache[key]
        else:
            ql, qt, qf = 0, 0, 0
        q_lin_vals.append(ql)
        q_tpa_vals.append(qt)
        q_fca_vals.append(qf)

    ax.bar(x - width, q_lin_vals, width, label='Linear', color='#77AC30', edgecolor='white', lw=0.3)
    ax.bar(x,         q_tpa_vals, width, label='TPA',    color='#0072BD', edgecolor='white', lw=0.3)
    ax.bar(x + width, q_fca_vals, width, label='FCA',    color='#A2142F', edgecolor='white', lw=0.3)

    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Peak heat deposition  (J/m$^3$)')
    ax.set_title(f'Heat breakdown at $d = {depth_mm}$ mm', fontsize=7)

    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    _legend(ax, loc='upper left')
    return fig


# ---------------------------------------------------------------------------
# Figure 4: FCA fraction vs N (one curve per depth)
# ---------------------------------------------------------------------------

def fig_fca_fraction_vs_N(heat_cache):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    burst_tags = ['b0100', 'b0500', 'b1000']
    burst_Ns   = [100, 500, 1000]
    depth_colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(DEPTHS_MM)))

    for i, d_mm in enumerate(DEPTHS_MM):
        Ns, fracs = [], []
        for tag, N in zip(burst_tags, burst_Ns):
            key = (tag, d_mm)
            if key in heat_cache:
                ql, qt, qf = heat_cache[key]
                total = ql + qt + qf
                if total > 0:
                    Ns.append(N)
                    fracs.append(qf / total)
        if Ns:
            ax.plot(Ns, fracs,
                    color=depth_colors[i], marker='o', ls='-', lw=1.0, ms=3.5,
                    markeredgecolor='white', markeredgewidth=0.3,
                    label=f'$d = {d_mm}$ mm')

    ax.set_xlabel('Burst pulse count $N$')
    ax.set_ylabel('FCA fraction  ($Q_{\\mathrm{FCA}} / Q_{\\mathrm{total}}$)')
    ax.set_xlim(0, 1100)

    _legend(ax, loc='upper left')
    return fig


# ---------------------------------------------------------------------------
# Figure 5: Heat breakdown vs depth (N=1000)
# ---------------------------------------------------------------------------

def fig_heat_vs_depth(heat_cache, tag='b1000'):
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    depths, q_lin, q_tpa, q_fca = [], [], [], []
    for d_mm in DEPTHS_MM:
        key = (tag, d_mm)
        if key in heat_cache:
            ql, qt, qf = heat_cache[key]
            depths.append(d_mm)
            q_lin.append(ql)
            q_tpa.append(qt)
            q_fca.append(qf)

    if depths:
        ax.plot(depths, q_lin, color='#77AC30', marker='s', ls='--', lw=1.0, ms=3.5,
                markeredgecolor='white', markeredgewidth=0.3, label='Linear')
        ax.plot(depths, q_tpa, color='#0072BD', marker='o', ls='-', lw=1.0, ms=3.5,
                markeredgecolor='white', markeredgewidth=0.3, label='TPA')
        ax.plot(depths, q_fca, color='#A2142F', marker='v', ls='-', lw=1.0, ms=3.5,
                markeredgecolor='white', markeredgewidth=0.3, label='FCA')

    ax.set_yscale('log')
    ax.set_xlabel('Target depth  (mm)')
    ax.set_ylabel('Peak heat deposition  (J/m$^3$)')

    cfg_label = [c for c in CONFIGS if c['tag'] == tag]
    title_label = cfg_label[0]['label'] if cfg_label else tag
    ax.set_title(f'Heat breakdown \u2014 {title_label}', fontsize=7)
    ax.set_xlim(0, 1.1)

    ax.yaxis.set_major_locator(ticker.LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10, subs=np.arange(2, 10) * 0.1, numticks=12))
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())

    _legend(ax)
    return fig


# ---------------------------------------------------------------------------
# Cache builder
# ---------------------------------------------------------------------------

def _build_caches():
    peak_cache = {}      # (tag, d_mm) -> peak pressure [Pa]
    heat_cache = {}      # (tag, d_mm) -> (Q_linear, Q_tpa, Q_fca)
    all_tags = [c['tag'] for c in CONFIGS]
    total = len(all_tags) * len(DEPTHS_MM)
    idx = 0
    for tag in all_tags:
        for d_mm in DEPTHS_MM:
            idx += 1
            path = _mat_path(tag, d_mm)
            if os.path.isfile(path):
                d  = pav.load_results(path)
                pp = float(np.max(np.abs(d['sensor_data'])))
                peak_cache[(tag, d_mm)] = pp

                ql, qt, qf = _peak_heat(path)
                heat_cache[(tag, d_mm)] = (ql, qt, qf)

                total_q = ql + qt + qf
                fca_str = f'  FCA={qf/total_q:.3f}' if total_q > 0 and qf > 0 else ''
                print(f'  [{idx:3d}/{total}] {tag:6s} @ {d_mm:.1f} mm  '
                      f'peak={pp:.3e} Pa  Q_lin={ql:.2e}  Q_tpa={qt:.2e}  Q_fca={qf:.2e}{fca_str}')
            else:
                print(f'  [{idx:3d}/{total}] {tag:6s} @ {d_mm:.1f} mm  ->  MISSING')

    return peak_cache, heat_cache


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description='Plot exp_011 results.')
    p.add_argument('--dpi',  type=int, default=300)
    p.add_argument('--fmt',  default='png', choices=['png', 'pdf', 'svg'])
    p.add_argument('--show', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    mpl.rcParams.update(pav.RC)
    os.makedirs(OUT_ROOT, exist_ok=True)

    print('Loading results...\n')
    peak_cache, heat_cache = _build_caches()
    print(f'\n{len(peak_cache)} entries loaded.\n')

    print('Fig 1: Peak pressure vs depth...')
    fig = fig_pressure_vs_depth(peak_cache)
    p = os.path.join(OUT_ROOT, f'fig1_peak_pressure_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Fig 2: Enhancement vs depth...')
    fig = fig_enhancement_vs_depth(peak_cache)
    p = os.path.join(OUT_ROOT, f'fig2_enhancement_vs_depth.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    for bar_depth in [0.2, 0.4, 1.0]:
        print(f'Fig 3: Heat breakdown bar at {bar_depth} mm...')
        fig = fig_heat_breakdown_bar(heat_cache, depth_mm=bar_depth)
        p = os.path.join(OUT_ROOT, f'fig3_heat_breakdown_{bar_depth:.1f}mm.{args.fmt}')
        fig.savefig(p, dpi=args.dpi); plt.close(fig)
        print(f'  Saved -> {p}')

    print('Fig 4: FCA fraction vs N...')
    fig = fig_fca_fraction_vs_N(heat_cache)
    p = os.path.join(OUT_ROOT, f'fig4_fca_fraction_vs_N.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Fig 5: Heat breakdown vs depth (N=1000)...')
    fig = fig_heat_vs_depth(heat_cache, tag='b1000')
    p = os.path.join(OUT_ROOT, f'fig5_heat_vs_depth_N1000.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    print('Fig 5b: Heat breakdown vs depth (N=500)...')
    fig = fig_heat_vs_depth(heat_cache, tag='b0500')
    p = os.path.join(OUT_ROOT, f'fig5b_heat_vs_depth_N500.{args.fmt}')
    fig.savefig(p, dpi=args.dpi); plt.close(fig)
    print(f'  Saved -> {p}')

    if args.show:
        plt.show()

    print('\nDone.')


if __name__ == '__main__':
    main()
