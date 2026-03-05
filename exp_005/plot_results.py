"""
exp_005/plot_results.py  —  Depth study: peak PA pressure vs target depth.

Loads all exp_005 results and generates a peak-pressure vs depth plot
with one curve per pulse type.

Output: LAB_PC_DRIVE/exp_005/peak_pressure_vs_depth.<fmt>

Usage:
  python plot_results.py [--dpi N] [--fmt png|pdf|svg] [--show]
"""

import argparse
import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

HERE        = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, 'results')
OUT_ROOT    = r'C:\Users\SYAVAS-LASERLAB\Documents\LAB_PC_DRIVE\exp_005'

sys.path.insert(0, os.path.join(HERE, '..'))
import pa_visualize as pav

DEPTHS_MM = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

PULSE_TYPES = [
    {'tag': 'ns',   'label': 'NS  (3 ns, 10 J/cm²)',      'color': '#E88C4C', 'ls': '--',  'marker': 's'},
    {'tag': 'fs',   'label': 'FS  (100 fs, 1 J/cm²)',     'color': '#4CE87A', 'ls': '--',  'marker': '^'},
    {'tag': 'b040', 'label': 'Burst N=40',                 'color': '#4C9BE8', 'ls': '-',   'marker': 'o'},
    {'tag': 'b080', 'label': 'Burst N=80',                 'color': '#9B4CE8', 'ls': '-',   'marker': 'o'},
    {'tag': 'b120', 'label': 'Burst N=120',                'color': '#E84C4C', 'ls': '-',   'marker': 'o'},
    {'tag': 'b160', 'label': 'Burst N=160',                'color': '#E8C84C', 'ls': '-',   'marker': 'o'},
    {'tag': 'b200', 'label': 'Burst N=200',                'color': '#4CE8E8', 'ls': '-',   'marker': 'o'},
]


def _peak_pressure(mat_path):
    d = pav.load_results(mat_path)
    return float(np.max(np.abs(d['sensor_data'])))


def fig_depth_comparison():
    print('Building peak-pressure vs depth comparison...')
    fig, ax = plt.subplots(figsize=(8, 5))

    for pt in PULSE_TYPES:
        depths_found = []
        pressures    = []
        for d_mm in DEPTHS_MM:
            d_um   = round(d_mm * 1000)
            label  = f"{pt['tag']}_d{d_um:04d}um"
            path   = os.path.join(RESULTS_DIR, f'{label}.mat')
            if os.path.isfile(path):
                pp = _peak_pressure(path)
                depths_found.append(d_mm)
                pressures.append(pp)
                print(f"  {label}  peak = {pp:.3e} Pa")
            else:
                print(f"  SKIP {label} -- not found")

        if depths_found:
            ax.plot(depths_found, pressures,
                    color=pt['color'], ls=pt['ls'],
                    lw=1.8, marker=pt['marker'], ms=5,
                    label=pt['label'])

    ax.set_xlabel('Target depth  [mm]')
    ax.set_ylabel('Peak pressure  [Pa]')
    ax.set_title('exp_005 — Peak PA Pressure vs Depth\n(BODIPY-TR 10 mM, NA=0.55)')
    ax.legend(framealpha=0.9, fontsize=8)
    ax.set_xlim(left=0)
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, _: f'{x:.2e}')
    )
    fig.tight_layout()
    return fig


def parse_args():
    p = argparse.ArgumentParser(description='Plot exp_005 depth study results.')
    p.add_argument('--dpi',  type=int, default=300)
    p.add_argument('--fmt',  default='png', choices=['png', 'pdf', 'svg'])
    p.add_argument('--show', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    mpl.rcParams.update(pav.RC)
    os.makedirs(OUT_ROOT, exist_ok=True)

    fig  = fig_depth_comparison()
    path = os.path.join(OUT_ROOT, f'peak_pressure_vs_depth.{args.fmt}')
    fig.savefig(path, dpi=args.dpi)
    print(f'\nSaved -> {path}')

    if args.show:
        plt.show()
    else:
        plt.close('all')


if __name__ == '__main__':
    main()
