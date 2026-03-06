"""
exp_004/plot_results.py  —  Generate figures for selected exp_004 scenarios.

Identical to exp_002 but with BODIPY-TR at 10 mM (alpha2 = 9e-13 m/W).

Scenarios:
  s01_ns_tau3ns_F10      NS single pulse
  s02_fs_tau100fs_F1     FS single pulse
  s03_burst_N020         FS burst, N = 20
  s03_burst_N040         FS burst, N = 40
  s03_burst_N060         FS burst, N = 60
  s03_burst_N080         FS burst, N = 80
  s03_burst_N100         FS burst, N = 100

Also generates a peak-pressure comparison across all scenarios (s01, s02,
and the full burst sweep N=10:10:300), saved to OUT_ROOT directly.

Output: LAB_PC_DRIVE/exp_004/<label>/  (one subfolder per scenario, 6 PNG each)
        LAB_PC_DRIVE/exp_004/peak_pressure_comparison.<fmt>

Usage:
  python plot_results.py [--dpi N] [--fmt png|pdf|svg] [--show]
"""

import argparse
import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# --- Paths ---
HERE        = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, 'results')
OUT_ROOT    = r'C:\Users\SYAVAS-LASERLAB\Documents\LAB_PC_DRIVE\exp_004'

# Add parent dir so pa_visualize is importable
sys.path.insert(0, os.path.join(HERE, '..', '..'))
import pa_visualize as pav

# --- Scenarios to plot individually ---
SCENARIOS = [
    's01_ns_tau3ns_F10',
    's02_fs_tau100fs_F1',
    's03_burst_N020',
    's03_burst_N040',
    's03_burst_N060',
    's03_burst_N080',
    's03_burst_N100',
]

# --- Full burst sweep for comparison plot ---
N_LIST = list(range(10, 310, 10))   # 10:10:300


def _peak_pressure(mat_path):
    """Return peak absolute pressure [Pa] from a results .mat file."""
    d = pav.load_results(mat_path)
    return float(np.max(np.abs(d['sensor_data'])))


def fig_peak_pressure_comparison():
    """
    Line plot of peak PA pressure vs scenario:
      - s01 (NS) and s02 (FS) as horizontal reference lines
      - s03 burst sweep (N=10..300) as a curve
    """
    print('Building peak-pressure comparison...')

    # --- Reference scenarios ---
    p_ns, p_fs = None, None
    path_ns = os.path.join(RESULTS_DIR, 's01_ns_tau3ns_F10.mat')
    path_fs = os.path.join(RESULTS_DIR, 's02_fs_tau100fs_F1.mat')
    if os.path.isfile(path_ns):
        p_ns = _peak_pressure(path_ns)
        print(f'  s01 NS  peak = {p_ns:.3e} Pa')
    if os.path.isfile(path_fs):
        p_fs = _peak_pressure(path_fs)
        print(f'  s02 FS  peak = {p_fs:.3e} Pa')

    # --- Burst sweep ---
    burst_N  = []
    burst_pp = []
    for N in N_LIST:
        path = os.path.join(RESULTS_DIR, f's03_burst_N{N:03d}.mat')
        if os.path.isfile(path):
            pp = _peak_pressure(path)
            burst_N.append(N)
            burst_pp.append(pp)
            print(f'  N={N:3d}  peak = {pp:.3e} Pa')

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(7, 4.5))

    if burst_N:
        ax.plot(burst_N, np.array(burst_pp), color='#4C9BE8',
                lw=1.8, marker='o', ms=3.5, label='FS burst')

    if p_ns is not None:
        ax.axhline(p_ns, color='#E88C4C', lw=1.5, ls='--', label='NS single pulse')
    if p_fs is not None:
        ax.axhline(p_fs, color='#4CE87A', lw=1.5, ls='--', label='FS single pulse')

    ax.set_xlabel('Burst pulse count  $N$')
    ax.set_ylabel('Peak pressure  [Pa]')
    ax.set_title('exp_004 — Peak PA Pressure vs Scenario\n(BODIPY-TR 10 mM)')
    ax.legend(framealpha=0.9)
    ax.set_xlim(left=0)
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, _: f'{x:.2e}')
    )
    fig.tight_layout()
    return fig


def parse_args():
    p = argparse.ArgumentParser(description='Plot selected exp_004 scenarios.')
    p.add_argument('--dpi',  type=int, default=300,
                   help='Save DPI (default: 300)')
    p.add_argument('--fmt',  default='png',
                   choices=['png', 'pdf', 'svg'],
                   help='Output format (default: png)')
    p.add_argument('--show', action='store_true',
                   help='Show figures interactively after saving')
    return p.parse_args()


def main():
    args = parse_args()
    mpl.rcParams.update(pav.RC)

    # --- Per-scenario figures ---
    n = len(SCENARIOS)
    for i, label in enumerate(SCENARIOS, 1):
        mat_path = os.path.join(RESULTS_DIR, f'{label}.mat')
        if not os.path.isfile(mat_path):
            print(f'[{i}/{n}] SKIP {label} -- file not found')
            continue

        out_dir = os.path.join(OUT_ROOT, label)
        os.makedirs(out_dir, exist_ok=True)

        print(f'[{i}/{n}] {label}')
        d = pav.load_results(mat_path)

        for fig_fn, fig_stem in pav.FIGURES:
            fig  = fig_fn(d)
            path = os.path.join(out_dir, f'{label}_{fig_stem}.{args.fmt}')
            fig.savefig(path, dpi=args.dpi)
            print(f'  Saved -> {path}')

        if args.show:
            plt.show()
        else:
            plt.close('all')

        print()

    # --- Peak pressure comparison ---
    os.makedirs(OUT_ROOT, exist_ok=True)
    fig = fig_peak_pressure_comparison()
    path = os.path.join(OUT_ROOT, f'peak_pressure_comparison.{args.fmt}')
    fig.savefig(path, dpi=args.dpi)
    print(f'Saved -> {path}')
    if args.show:
        plt.show()
    else:
        plt.close('all')

    print(f'\nDone. Output: {OUT_ROOT}')


if __name__ == '__main__':
    main()
