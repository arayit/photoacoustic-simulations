#!/usr/bin/env python3
"""
pa_visualize.py  ─  Publication-ready visualization of PA simulation results.

Figures generated
-----------------
  <stem>_p0_map.<fmt>    Initial pressure p₀  on the optical grid  [Pa]
  <stem>_Q0_map.<fmt>    Energy deposition Q₀ on the optical grid  [J m⁻³]
  <stem>_waveform.<fmt>  PA pressure waveform at the central transducer element  [Pa vs μs]

Usage
-----
  python pa_visualize.py <results.mat> [--out DIR] [--dpi N] [--fmt pdf|png|svg] [--show]

Arguments
---------
  results.mat   Path to a .mat file produced by run_pa_sim.m
  --out  DIR    Destination folder (default: same directory as the .mat file)
  --dpi  N      Save resolution in DPI (default: 300)
  --fmt  FORMAT Output format: pdf, png, or svg  (default: pdf)
  --show        Open figures interactively after saving

Requirements
------------
  pip install numpy matplotlib scipy h5py
"""

import argparse
import os
import sys

# ── Default output directory ──────────────────────────────────────────────────
# Change this one line to redirect all figures globally.
# Override per-run with:  --out /your/path
DEFAULT_OUT_DIR = r'C:\Users\SYAVAS-LASERLAB\Documents\LAB_PC_DRIVE'
# ─────────────────────────────────────────────────────────────────────────────

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.colors import LogNorm
from matplotlib.ticker import LogLocator


# ─────────────────────────────────────────────────────────────────────────────
# Publication style
# ─────────────────────────────────────────────────────────────────────────────

RC = {
    # Font
    'font.family':          'sans-serif',
    'font.sans-serif':      ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size':            8,
    'axes.labelsize':       9,
    'axes.titlesize':       9,
    'axes.titlepad':        7,
    # Ticks
    'xtick.labelsize':      8,
    'ytick.labelsize':      8,
    'xtick.direction':      'in',
    'ytick.direction':      'in',
    'xtick.top':            True,
    'ytick.right':          True,
    'xtick.minor.visible':  True,
    'ytick.minor.visible':  True,
    'xtick.major.size':     4,
    'ytick.major.size':     4,
    'xtick.minor.size':     2,
    'ytick.minor.size':     2,
    'xtick.major.width':    0.8,
    'ytick.major.width':    0.8,
    'xtick.minor.width':    0.5,
    'ytick.minor.width':    0.5,
    # Lines / frame
    'axes.linewidth':       0.8,
    # Image
    'image.interpolation':  'none',
    # PDF embedding
    'pdf.fonttype':         42,     # TrueType — editable in Illustrator / Inkscape
    'ps.fonttype':          42,
    # Saving
    'savefig.dpi':          300,
    'savefig.bbox':         'tight',
    'savefig.pad_inches':   0.05,
}

# Figure geometry (single journal column)
_FW = 3.3     # inches — width
_FH = 3.7     # inches — height (slightly taller to fit title)

# Colormap: perceptually uniform, monotone luminance → prints well in B&W
_CMAP = 'inferno'

# Annotation colours
_ANN_COLOR  = 'white'   # target circle, beam guides
_LABEL_FRAC = 0.030     # relative inset for corner text labels


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_results(mat_path: str) -> dict:
    """
    Load the fields required for visualization from a run_pa_sim results file.
    Supports MATLAB v7 (scipy) and v7.3 / HDF5 (h5py).
    """
    try:
        return _load_hdf5(mat_path)
    except Exception as hdf_err:
        try:
            return _load_scipy(mat_path)
        except Exception as sci_err:
            raise RuntimeError(
                f"Could not load {mat_path}.\n"
                f"  HDF5 error  : {hdf_err}\n"
                f"  scipy error : {sci_err}\n"
                "Install required packages:  pip install numpy matplotlib scipy h5py"
            ) from None


def _load_hdf5(path: str) -> dict:
    """Load from MATLAB v7.3 (HDF5) file."""
    import h5py  # noqa: PLC0415

    def _arr(node):
        """Dataset → numpy array, transposed to recover MATLAB row-major layout."""
        a = node[()]
        return a.T if a.ndim >= 2 else np.asarray(a).ravel()

    def _scalar(node):
        return float(_arr(node).ravel()[0])

    def _string(node):
        raw = node[()]
        if isinstance(raw, bytes):
            return raw.decode('utf-8', errors='replace')
        arr = np.asarray(raw).ravel()
        if arr.dtype.kind in ('u', 'i'):   # uint16 char array
            return ''.join(chr(int(c)) for c in arr)
        return str(raw)

    with h5py.File(path, 'r') as f:
        r    = f['results']
        cfg  = r['cfg']
        beam = r['beam']
        return {
            'p0_opt':        _arr(r['p0_opt']).astype(np.float64),
            'Q_opt':         _arr(r['Q_opt']).astype(np.float64),
            'I_opt_map':     _arr(r['I_opt_map']).astype(np.float64),
            'z_opt_vec':     _arr(r['z_opt_vec']).ravel().astype(np.float64),
            'y_opt_vec':     _arr(r['y_opt_vec']).ravel().astype(np.float64),
            'sensor_data':   _arr(r['sensor_data']).astype(np.float64),
            't_array':       _arr(r['t_array']).ravel().astype(np.float64),
            'element_y':     _arr(r['element_y']).ravel().astype(np.float64),
            'target_depth':  _scalar(cfg['target_depth']),
            'target_radius': _scalar(cfg['target_radius']),
            'c_sound':       _scalar(cfg['c_sound']),
            'f_grid':  _scalar(cfg['f_grid']),
            'f_max_acoustic': _scalar(r['f_max_acoustic']) if 'f_max_acoustic' in r else np.inf,
            'w0':            _scalar(beam['w0']),
            'label':         _string(cfg['label']),
            'lambda_m':      _scalar(cfg['lambda']),
            'NA':            _scalar(cfg['NA']),
            'T_ballistic':   _scalar(r['T_ballistic']) if 'T_ballistic' in r else None,
            'E_focus':       _scalar(r['E_focus'])     if 'E_focus'     in r else None,
            'E_surface':     _scalar(r['E_surface'])   if 'E_surface'   in r else None,
            'F_surface':     _scalar(r['F_surface'])   if 'F_surface'   in r else None,
        }


def _load_scipy(path: str) -> dict:
    """Load from MATLAB v7 (non-HDF5) file."""
    import scipy.io as sio  # noqa: PLC0415

    raw = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
    r   = raw['results']
    cfg = r.cfg

    # 'lambda' is a Python keyword; scipy may rename it to 'lambda_'
    lam = (cfg.__dict__.get('lambda')
           or cfg.__dict__.get('lambda_')
           or getattr(cfg, 'lambda_', None))

    return {
        'p0_opt':        np.asarray(r.p0_opt,       dtype=np.float64),
        'Q_opt':         np.asarray(r.Q_opt,        dtype=np.float64),
        'I_opt_map':     np.asarray(r.I_opt_map,    dtype=np.float64),
        'z_opt_vec':     np.asarray(r.z_opt_vec,    dtype=np.float64).ravel(),
        'y_opt_vec':     np.asarray(r.y_opt_vec,    dtype=np.float64).ravel(),
        'sensor_data':   np.asarray(r.sensor_data,  dtype=np.float64),
        't_array':       np.asarray(r.t_array,      dtype=np.float64).ravel(),
        'element_y':     np.asarray(r.element_y,    dtype=np.float64).ravel(),
        'target_depth':  float(cfg.target_depth),
        'target_radius': float(cfg.target_radius),
        'c_sound':       float(cfg.c_sound),
        'f_grid':  float(cfg.f_grid),
        'f_max_acoustic': float(r.f_max_acoustic) if hasattr(r, 'f_max_acoustic') else np.inf,
        'w0':            float(r.beam.w0),
        'label':         str(cfg.label),
        'lambda_m':      float(lam),
        'NA':            float(cfg.NA),
        'T_ballistic':   float(r.T_ballistic) if hasattr(r, 'T_ballistic') else None,
        'E_focus':       float(r.E_focus)     if hasattr(r, 'E_focus')     else None,
        'E_surface':     float(r.E_surface)   if hasattr(r, 'E_surface')   else None,
        'F_surface':     float(r.F_surface)   if hasattr(r, 'F_surface')   else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Figure construction
# ─────────────────────────────────────────────────────────────────────────────

def _build_map_figure(
    data:         np.ndarray,
    y_um:         np.ndarray,
    z_rel_um:     np.ndarray,
    target_r_um:  float,
    w0_um:        float,
    title:        str,
    cbar_label:   str,
) -> plt.Figure:
    """
    Build a single publication-ready 2D map figure.

    Parameters
    ----------
    data        : 2-D array, shape (Nz, Ny) — must be non-negative
    y_um        : lateral axis [μm]  — length Ny
    z_rel_um    : axial axis relative to focus [μm]  — length Nz
    target_r_um : target radius [μm]  (for boundary circle)
    w0_um       : 1/e² beam waist [μm]  (for annotation)
    title       : figure title (two-line string)
    cbar_label  : colorbar axis label
    """
    # ── Colour scaling ───────────────────────────────────────────────────────
    positive = data[data > 0]
    if positive.size == 0:
        raise ValueError("Data contains no positive values; cannot apply log scale.")
    vmax = positive.max()
    vmin = max(positive.min(), vmax * 1e-4)   # clamp at 4 decades below peak
    norm = LogNorm(vmin=vmin, vmax=vmax)

    # ── Figure / axes ────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(_FW, _FH), constrained_layout=True)

    # ── 2-D colour map ───────────────────────────────────────────────────────
    data_plot = np.where(data > 0, data, np.nan)   # hide zeros cleanly
    im = ax.pcolormesh(
        y_um, z_rel_um, data_plot,
        cmap=_CMAP, norm=norm,
        shading='auto',
        rasterized=True,    # keeps PDF file size small
    )
    ax.set_facecolor('black')   # zero-value background matches 'inferno' minimum

    # ── Target boundary circle ────────────────────────────────────────────────
    circle = Circle(
        xy=(0.0, 0.0), radius=target_r_um,
        edgecolor=_ANN_COLOR, facecolor='none',
        linewidth=0.9, linestyle='--', zorder=5,
    )
    ax.add_patch(circle)

    # ── Focal-plane cross-hairs (guide for beam axis and focal depth) ─────────
    ax.axhline(0.0, color=_ANN_COLOR, linewidth=0.6, linestyle=':', alpha=0.6, zorder=4)
    ax.axvline(0.0, color=_ANN_COLOR, linewidth=0.6, linestyle=':', alpha=0.6, zorder=4)

    # ── Beam-waist label (upper-left corner) ─────────────────────────────────
    ax.text(0.03, 0.97, f'$2w_0$ = {2*w0_um:.2f} $\\mu$m',
            transform=ax.transAxes,
            color=_ANN_COLOR, fontsize=7, ha='left', va='top', zorder=7)

    # ── Target label (lower-right corner) ─────────────────────────────────────
    ax.text(
        y_um.max() * (1 - _LABEL_FRAC),
        z_rel_um.min() * (1 - _LABEL_FRAC),
        f'$r_\\mathrm{{tgt}}$ = {target_r_um:.1f} μm',
        color=_ANN_COLOR, fontsize=7,
        ha='right', va='bottom', zorder=7,
    )

    # ── Axes labels & title ───────────────────────────────────────────────────
    ax.set_xlabel('Lateral position,  $y$  (μm)')
    ax.set_ylabel('Axial position,  $z - z_\\mathrm{foc}$  (μm)')
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.set_xlim(y_um[[0, -1]])
    ax.set_ylim(z_rel_um[[0, -1]])

    # ── Colorbar ─────────────────────────────────────────────────────────────
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, aspect=20)
    cbar.set_label(cbar_label, labelpad=6)
    cbar.ax.yaxis.set_minor_locator(
        LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1, numticks=12)
    )
    cbar.ax.tick_params(which='minor', length=2, width=0.5)
    cbar.ax.tick_params(which='major', length=4, width=0.8)

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Individual figure entry points
# ─────────────────────────────────────────────────────────────────────────────

def fig_p0_map(d: dict) -> plt.Figure:
    """Figure 1 — initial pressure p₀ map on the optical grid."""
    y_um     = d['y_opt_vec'] * 1e6
    z_rel_um = (d['z_opt_vec'] - d['target_depth']) * 1e6
    lam_nm   = d['lambda_m'] * 1e9
    title    = (
        f"{d['label']}\n"
        f"$p_0$ map  |  $\\lambda$ = {lam_nm:.0f} nm,  "
        f"NA = {d['NA']:.2f},  $\\Gamma$ = 0.12"
    )
    return _build_map_figure(
        data        = d['p0_opt'],
        y_um        = y_um,
        z_rel_um    = z_rel_um,
        target_r_um = d['target_radius'] * 1e6,
        w0_um       = d['w0'] * 1e6,
        title       = title,
        cbar_label  = '$p_0$  (Pa)',
    )


def fig_Q0_map(d: dict) -> plt.Figure:
    """Figure 2 — energy deposition Q₀ map on the optical grid."""
    y_um     = d['y_opt_vec'] * 1e6
    z_rel_um = (d['z_opt_vec'] - d['target_depth']) * 1e6
    lam_nm   = d['lambda_m'] * 1e9
    title    = (
        f"{d['label']}\n"
        f"$Q_0$ map  |  $\\lambda$ = {lam_nm:.0f} nm,  "
        f"NA = {d['NA']:.2f}"
    )
    return _build_map_figure(
        data        = d['Q_opt'],
        y_um        = y_um,
        z_rel_um    = z_rel_um,
        target_r_um = d['target_radius'] * 1e6,
        w0_um       = d['w0'] * 1e6,
        title       = title,
        cbar_label  = '$Q_0$  (J m$^{-3}$)',
    )


def fig_waveform(d: dict) -> plt.Figure:
    """Figure 3 — PA pressure waveform at the central transducer element."""
    t_us        = d['t_array'] * 1e6                     # [us]
    sensor_data = d['sensor_data']                        # [n_elements x Nt]
    element_y   = d['element_y']
    f_t         = d['f_grid']
    c           = d['c_sound']
    z_tgt       = d['target_depth']
    r_tgt       = d['target_radius']

    # Central element (closest to y = 0)
    center_idx = int(np.argmin(np.abs(element_y)))
    trace      = sensor_data[center_idx, :].copy()

    # Zoom window: expected arrival ± 10 transducer periods
    t_arrive_us = z_tgt / c * 1e6
    margin_us   = 10.0 / f_t * 1e6
    t_lo        = t_arrive_us - margin_us
    t_hi        = t_arrive_us + margin_us
    mask        = (t_us >= t_lo) & (t_us <= t_hi)

    # Expected signal window from target geometry
    t_sig_lo = (z_tgt - r_tgt) / c * 1e6
    t_sig_hi = (z_tgt + r_tgt) / c * 1e6

    # Remove DC offset: subtract the first sample of the zoom window
    first_idx = int(np.argmax(mask))
    trace -= trace[first_idx]

    t_plot   = t_us[mask]
    p_plot   = trace[mask]
    p_peak   = np.max(np.abs(p_plot)) if p_plot.size else 1.0
    y_lim    = p_peak * 1.25

    # ── Figure ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    # Zero baseline
    ax.axhline(0.0, color='0.6', linewidth=0.5, zorder=1)

    # Waveform trace
    ax.plot(t_plot, p_plot, color='#1c2940', linewidth=1.0, zorder=3)

    # Peak pressure annotation — upper right corner
    ax.text(0.97, 0.97, f'{p_peak:.2e} Pa',
            transform=ax.transAxes,
            color='#1c2940', fontsize=7, ha='right', va='top', zorder=4)

    # Axes
    lam_nm = d['lambda_m'] * 1e9
    ax.set_xlabel('Time  ($\\mu$s)')
    ax.set_ylabel('Pressure  (Pa)')
    ax.set_title(
        f"{d['label']}\n"
        f"PA waveform  |  center element,  $\\lambda$ = {lam_nm:.0f} nm"
    )
    ax.set_xlim(t_lo, t_hi)
    ax.set_ylim(-y_lim, y_lim)
    ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

    # Remove top / right spines for clean line-plot style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    return fig


def fig_spectrum(d: dict) -> plt.Figure:
    """Figure 4 — Fourier spectrum of the PA waveform at the central element."""
    t_array     = d['t_array']
    sensor_data = d['sensor_data']
    element_y   = d['element_y']
    f_t         = d['f_grid']
    c           = d['c_sound']
    z_tgt       = d['target_depth']
    r_tgt       = d['target_radius']
    lam_nm      = d['lambda_m'] * 1e9

    # Central element, DC removal (same logic as waveform figure)
    center_idx = int(np.argmin(np.abs(element_y)))
    trace      = sensor_data[center_idx, :].copy()
    t_us       = t_array * 1e6
    t_arrive_us = z_tgt / c * 1e6
    margin_us   = 10.0 / f_t * 1e6
    mask        = (t_us >= t_arrive_us - margin_us) & (t_us <= t_arrive_us + margin_us)
    trace      -= trace[int(np.argmax(mask))]

    # Hann-windowed signal: window applied only over the PA pulse region,
    # zeros elsewhere — preserves frequency resolution of the full trace
    t_sig_lo = (z_tgt - r_tgt) / c
    t_sig_hi = (z_tgt + r_tgt) / c
    pad      = 5.0 / f_t                            # 5 periods either side of pulse
    sig_mask = (t_array >= t_sig_lo - pad) & (t_array <= t_sig_hi + pad)
    windowed = np.zeros_like(trace)
    windowed[sig_mask] = trace[sig_mask] * np.hanning(sig_mask.sum())

    # FFT — one-sided magnitude spectrum
    dt       = t_array[1] - t_array[0]
    N        = len(windowed)
    freqs_Hz = np.fft.rfftfreq(N, d=dt)
    spectrum = np.abs(np.fft.rfft(windowed))

    # Normalize to 0 dB; x-axis limit: 2× f_max_acoustic if set, else 2× f_grid
    f_max_acoustic = d['f_max_acoustic']
    f_max_Hz   = 2.0 * (f_max_acoustic if np.isfinite(f_max_acoustic) else f_t)
    freq_mask  = freqs_Hz <= f_max_Hz
    freqs_MHz  = freqs_Hz[freq_mask] * 1e-6
    spec_plot  = spectrum[freq_mask]
    spec_db    = 20.0 * np.log10(np.clip(spec_plot / spec_plot.max(), 1e-6, 1.0))

    # ── Figure ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(3.5, 2.5), constrained_layout=True)

    ax.plot(freqs_MHz, spec_db, color='#1c2940', linewidth=1.0, zorder=3)

    # f_max_acoustic cut-off line (only when filter was applied)
    if np.isfinite(f_max_acoustic):
        ax.axvline(f_max_acoustic * 1e-6, color='steelblue', linewidth=0.8,
                   linestyle='--', alpha=0.75, zorder=2)
        ax.text(f_max_acoustic * 1e-6 + f_max_Hz * 1e-6 * 0.01, -58,
                f'$f_{{max}}$ = {f_max_acoustic*1e-6:.0f} MHz',
                color='steelblue', fontsize=7, ha='left', va='bottom')

    ax.set_xlabel('Frequency  (MHz)')
    ax.set_ylabel('Amplitude  (dB)')
    ax.set_title(
        f"{d['label']}\n"
        f"Frequency spectrum  |  $\\lambda$ = {lam_nm:.0f} nm"
    )
    ax.set_xlim(0, f_max_Hz * 1e-6)
    ax.set_ylim(-65, 5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    return fig


def _das_reconstruct(
    sensor_data: np.ndarray,    # [n_elements × Nt]
    t_array:     np.ndarray,    # [Nt]
    element_y:   np.ndarray,    # [n_elements]
    c:           float,
    z_img:       np.ndarray,    # [Nz_img]
    y_img:       np.ndarray,    # [Ny_img]
) -> np.ndarray:
    """
    Delay-and-sum beamforming.  Returns a [Nz_img × Ny_img] pressure image.
    Each element's trace is interpolated at the one-way travel time to each pixel.
    A per-element DC offset (mean of early time) is removed before summation.
    """
    Y, Z  = np.meshgrid(y_img, z_img)       # [Nz_img × Ny_img]
    image = np.zeros(Y.shape, dtype=np.float64)

    # Per-element DC removal using first 5 % of time samples
    n_dc = max(1, int(0.05 * sensor_data.shape[1]))

    for ie, y_e in enumerate(element_y):
        trace   = sensor_data[ie].astype(np.float64)
        trace  -= trace[:n_dc].mean()
        t_delay = np.sqrt((Y - y_e) ** 2 + Z ** 2) / c     # [Nz_img × Ny_img]
        image  += np.interp(t_delay.ravel(), t_array, trace,
                            left=0.0, right=0.0).reshape(Y.shape)
    return image


def _get_bscan(d: dict):
    """Compute (or return cached) DAS B-scan envelope in dB."""
    if '_bscan' not in d:
        c         = d['c_sound']
        t_array   = d['t_array']
        element_y = d['element_y']
        z_max_m   = t_array[-1] * c / 2.0
        y_max_m   = np.abs(element_y).max()
        Nz, Ny    = 400, 300
        z_img     = np.linspace(0, z_max_m, Nz)
        y_img     = np.linspace(-y_max_m, y_max_m, Ny)
        image     = _das_reconstruct(d['sensor_data'], t_array, element_y, c, z_img, y_img)
        env       = np.abs(image)
        env_max   = env.max()
        dyn_dB    = 50.0
        env_db    = 20.0 * np.log10(np.clip(env / env_max, 10 ** (-dyn_dB / 20), 1.0))
        d['_bscan'] = (z_img, y_img, env_db, dyn_dB)
    return d['_bscan']


def fig_bscan(d: dict) -> plt.Figure:
    """Figure — DAS-reconstructed PA B-scan."""
    z_img, y_img, env_db, dyn_dB = _get_bscan(d)
    z_tgt  = d['target_depth']
    lam_nm = d['lambda_m'] * 1e9
    y_max_m = y_img.max()

    # ── Figure ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(_FW, _FH), constrained_layout=True)

    im = ax.pcolormesh(
        y_img * 1e3, z_img * 1e3, env_db,
        cmap='gray', vmin=-dyn_dB, vmax=0,
        shading='auto', rasterized=True,
    )

    # Target position marker
    ax.axhline(z_tgt * 1e3, color='steelblue', linewidth=0.8,
               linestyle='--', alpha=0.7)
    ax.text(y_max_m * 1e3 * 0.97, z_tgt * 1e3,
            f'$z_{{tgt}}$ = {z_tgt*1e3:.1f} mm',
            color='steelblue', fontsize=7, ha='right', va='bottom')

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, aspect=20)
    cbar.set_label('Amplitude  (dB)', labelpad=6)
    cbar.ax.tick_params(which='major', length=4, width=0.8)

    ax.set_xlabel('Lateral position,  $y$  (mm)')
    ax.set_ylabel('Depth,  $z$  (mm)')
    ax.set_title(
        f"{d['label']}\n"
        f"B-scan (DAS)  |  $\\lambda$ = {lam_nm:.0f} nm,  "
        f"{dyn_dB:.0f} dB dynamic range"
    )
    ax.invert_yaxis()   # depth increases downward (imaging convention)

    return fig


def fig_intensity_map(d: dict) -> plt.Figure:
    """Figure — optical intensity I on the optical grid."""
    y_um     = d['y_opt_vec'] * 1e6
    z_rel_um = (d['z_opt_vec'] - d['target_depth']) * 1e6
    lam_nm   = d['lambda_m'] * 1e9
    title    = (
        f"{d['label']}\n"
        f"Intensity map  |  $\\lambda$ = {lam_nm:.0f} nm,  NA = {d['NA']:.2f}"
    )
    return _build_map_figure(
        data        = d['I_opt_map'],
        y_um        = y_um,
        z_rel_um    = z_rel_um,
        target_r_um = d['target_radius'] * 1e6,
        w0_um       = d['w0'] * 1e6,
        title       = title,
        cbar_label  = '$I$  (W m$^{-2}$)',
    )



# ─────────────────────────────────────────────────────────────────────────────
# Registry — add new figures here as (function, output_stem) tuples
# ─────────────────────────────────────────────────────────────────────────────

FIGURES = [
    (fig_intensity_map, 'intensity_map'),
    (fig_Q0_map,        'Q0_map'),
    (fig_p0_map,        'p0_map'),
    (fig_waveform,      'waveform'),
    (fig_spectrum,      'spectrum'),
    (fig_bscan,         'bscan'),
]


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument('mat_file',
                   help='Path to a results .mat file from run_pa_sim.m')
    p.add_argument('--out',  default=DEFAULT_OUT_DIR,
                   help=f'Output folder (default: {DEFAULT_OUT_DIR})')
    p.add_argument('--dpi',  type=int, default=300,
                   help='Save DPI (default: 300)')
    p.add_argument('--fmt',  default='png',
                   choices=['pdf', 'png', 'svg'],
                   help='Output format (default: png)')
    p.add_argument('--show', action='store_true',
                   help='Display figures interactively after saving')
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    mat_path = os.path.abspath(args.mat_file)
    if not os.path.isfile(mat_path):
        sys.exit(f'Error: file not found — {mat_path}')

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    stem = os.path.splitext(os.path.basename(mat_path))[0]

    # ── Load ──────────────────────────────────────────────────────────────────
    print(f'Loading  {mat_path}')
    d = load_results(mat_path)
    print(f"  label         : {d['label']}")
    print(f"  target depth  : {d['target_depth']*1e3:.2f} mm")
    print(f"  target radius : {d['target_radius']*1e6:.1f} um")
    print(f"  beam waist w0 : {d['w0']*1e9:.0f} nm")
    print(f"  optical grid  : {d['p0_opt'].shape[0]} (z) x {d['p0_opt'].shape[1]} (y) pts")
    print(f"  sensor data   : {d['sensor_data'].shape[0]} elements x {d['sensor_data'].shape[1]} time pts")
    print()

    # ── Apply style & generate ────────────────────────────────────────────────
    mpl.rcParams.update(RC)

    for fig_fn, fig_stem in FIGURES:
        fig  = fig_fn(d)
        path = os.path.join(out_dir, f'{stem}_{fig_stem}.{args.fmt}')
        fig.savefig(path, dpi=args.dpi)
        print(f'Saved  ->  {path}')

    print()

    if args.show:
        plt.show()
    else:
        plt.close('all')

    print('Done.')


if __name__ == '__main__':
    main()
