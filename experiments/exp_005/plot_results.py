"""
exp_005/plot_results.py  —  Depth study visualisation (depth-grouped).

Output structure:
  LAB_PC_DRIVE/exp_005/
    peak_pressure_vs_depth.<fmt>          global summary (all configs x all depths)
    d<depth>um/
      d<depth>um_comparison.<fmt>         bar chart: all 7 configs at this depth
      <tag>_d<depth>um_intensity_map.<fmt>
      <tag>_d<depth>um_Q0_map.<fmt>
      <tag>_d<depth>um_p0_map.<fmt>
      <tag>_d<depth>um_waveform.<fmt>
      <tag>_d<depth>um_spectrum.<fmt>
      <tag>_d<depth>um_bscan.<fmt>

Old per-scenario folders (named <tag>_d<depth>um/) are deleted on startup.

Usage:
  python plot_results.py [--dpi N] [--fmt png|pdf|svg] [--show]
"""

import argparse
import os
import shutil
import stat
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

HERE        = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, 'results')
OUT_ROOT    = r'C:\Users\SYAVAS-LASERLAB\Documents\LAB_PC_DRIVE\exp_005'

sys.path.insert(0, os.path.join(HERE, '..', '..'))
import pa_visualize as pav

DEPTHS_MM = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

PULSE_TYPES = [
    {'tag': 'ns',   'label': 'NS  (3 ns, 10 J/cm2)',  'color': '#E88C4C', 'ls': '--', 'marker': 's'},
    {'tag': 'fs',   'label': 'FS  (100 fs, 1 J/cm2)', 'color': '#4CE87A', 'ls': '--', 'marker': '^'},
    {'tag': 'b040', 'label': 'Burst N=40',             'color': '#4C9BE8', 'ls': '-',  'marker': 'o'},
    {'tag': 'b080', 'label': 'Burst N=80',             'color': '#9B4CE8', 'ls': '-',  'marker': 'o'},
    {'tag': 'b120', 'label': 'Burst N=120',            'color': '#E84C4C', 'ls': '-',  'marker': 'o'},
    {'tag': 'b160', 'label': 'Burst N=160',            'color': '#E8C84C', 'ls': '-',  'marker': 'o'},
    {'tag': 'b200', 'label': 'Burst N=200',            'color': '#4CE8E8', 'ls': '-',  'marker': 'o'},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _depth_tag(d_mm):
    return f'd{round(d_mm * 1000):04d}um'


def _mat_path(tag, d_mm):
    return os.path.join(RESULTS_DIR, f'{tag}_{_depth_tag(d_mm)}.mat')


def _scenario_label(tag, d_mm):
    return f'{tag}_{_depth_tag(d_mm)}'


def _peak_pressure(mat_path):
    d = pav.load_results(mat_path)
    return float(np.max(np.abs(d['sensor_data'])))


# ---------------------------------------------------------------------------
# Per-depth comparison bar chart
# ---------------------------------------------------------------------------

def fig_depth_bar(d_mm, peak_pressures):
    """
    Bar chart showing peak PA pressure for every pulse type at d_mm.

    peak_pressures : list of (pt_dict, pp_or_None) in PULSE_TYPES order.
    """
    valid = [(pt, pp) for pt, pp in peak_pressures if pp is not None]
    if not valid:
        return None

    labels   = [pt['label'] for pt, _ in valid]
    colors   = [pt['color'] for pt, _ in valid]
    values   = [pp          for _,  pp in valid]
    best_idx = int(np.argmax(values))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(range(len(values)), values,
                  color=colors, edgecolor='white', linewidth=0.5)

    # Highlight best
    bars[best_idx].set_edgecolor('black')
    bars[best_idx].set_linewidth(2.0)
    ax.annotate('best',
                xy=(best_idx, values[best_idx]),
                xytext=(best_idx, values[best_idx] * 1.06),
                ha='center', fontsize=8, fontweight='bold', color='black')

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=8)
    ax.set_ylabel('Peak pressure  [Pa]')
    ax.set_title(f'exp_005 — Peak PA Pressure at {d_mm:.1f} mm depth\n'
                 f'(BODIPY-TR 10 mM, NA=0.55)')
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, _: f'{x:.2e}'))
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Global depth-sweep summary
# ---------------------------------------------------------------------------

def fig_global_summary():
    """One curve per pulse type across all depths."""
    print('Building global peak-pressure vs depth summary...')
    fig, ax = plt.subplots(figsize=(8, 5))

    for pt in PULSE_TYPES:
        depths_found, pressures = [], []
        for d_mm in DEPTHS_MM:
            path = _mat_path(pt['tag'], d_mm)
            if os.path.isfile(path):
                pp = _peak_pressure(path)
                depths_found.append(d_mm)
                pressures.append(pp)
                print(f"  {pt['tag']:6s} @ {d_mm:.1f} mm  peak = {pp:.3e} Pa")
            else:
                print(f"  SKIP {pt['tag']:6s} @ {d_mm:.1f} mm -- not found")

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
        mpl.ticker.FuncFormatter(lambda x, _: f'{x:.2e}'))
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

def _force_remove_readonly(func, path, _):
    """onerror handler: clear read-only bit and retry (Windows fix)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _cleanup_old_scenario_folders():
    """Delete old per-scenario folders: <tag>_d<depth>um/"""
    if not os.path.isdir(OUT_ROOT):
        return
    old_tags = {pt['tag'] for pt in PULSE_TYPES}
    for entry in sorted(os.listdir(OUT_ROOT)):
        entry_path = os.path.join(OUT_ROOT, entry)
        if os.path.isdir(entry_path):
            if any(entry.startswith(tag + '_') for tag in old_tags):
                shutil.rmtree(entry_path, onerror=_force_remove_readonly)
                print(f'  Removed old folder: {entry}')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description='Plot exp_005 depth study results, grouped by depth.')
    p.add_argument('--dpi',  type=int, default=300)
    p.add_argument('--fmt',  default='png', choices=['png', 'pdf', 'svg'])
    p.add_argument('--show', action='store_true')
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    mpl.rcParams.update(pav.RC)
    os.makedirs(OUT_ROOT, exist_ok=True)

    print('Removing old per-scenario folders...')
    _cleanup_old_scenario_folders()
    print()

    n_depths = len(DEPTHS_MM)
    n_pulse  = len(PULSE_TYPES)
    n_total  = n_depths * n_pulse
    sidx     = 0

    for d_mm in DEPTHS_MM:
        dtag    = _depth_tag(d_mm)
        out_dir = os.path.join(OUT_ROOT, dtag)
        os.makedirs(out_dir, exist_ok=True)

        print(f'=== Depth {d_mm:.1f} mm  ({dtag}) ===')

        # 1) Collect peak pressures for all configs at this depth
        peak_pressures = []
        for pt in PULSE_TYPES:
            path = _mat_path(pt['tag'], d_mm)
            if os.path.isfile(path):
                pp = _peak_pressure(path)
                peak_pressures.append((pt, pp))
                print(f"  {pt['tag']:6s}  peak = {pp:.3e} Pa")
            else:
                peak_pressures.append((pt, None))
                print(f"  {pt['tag']:6s}  -- not found (skipped)")

        # 2) Depth comparison bar chart
        fig = fig_depth_bar(d_mm, peak_pressures)
        if fig is not None:
            save = os.path.join(out_dir, f'{dtag}_comparison.{args.fmt}')
            fig.savefig(save, dpi=args.dpi)
            print(f'  Saved -> {save}')
            if args.show:
                plt.show()
            else:
                plt.close(fig)

        # 3) All 6 standard figures for each pulse type at this depth
        for pt in PULSE_TYPES:
            sidx  += 1
            label  = _scenario_label(pt['tag'], d_mm)
            path   = _mat_path(pt['tag'], d_mm)

            if not os.path.isfile(path):
                print(f'  [{sidx:02d}/{n_total}] SKIP {label}')
                continue

            print(f'  [{sidx:02d}/{n_total}] {label}')
            d = pav.load_results(path)

            for fig_fn, fig_stem in pav.FIGURES:
                fig  = fig_fn(d)
                save = os.path.join(out_dir, f'{label}_{fig_stem}.{args.fmt}')
                fig.savefig(save, dpi=args.dpi)
                print(f'    Saved -> {save}')

            if args.show:
                plt.show()
            else:
                plt.close('all')

        print()

    # 4) Global depth-sweep summary
    print('--- Global summary ---')
    fig  = fig_global_summary()
    save = os.path.join(OUT_ROOT, f'peak_pressure_vs_depth.{args.fmt}')
    fig.savefig(save, dpi=args.dpi)
    print(f'Saved -> {save}')
    if args.show:
        plt.show()
    else:
        plt.close('all')

    print(f'\nDone. Output: {OUT_ROOT}')


if __name__ == '__main__':
    main()
