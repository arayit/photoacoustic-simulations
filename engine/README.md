# Photoacoustic Simulation Engine

A modular k-Wave based engine for 2D photoacoustic simulations of focused laser excitation in tissue.

---

## File Structure

| File | Role |
|------|------|
| `run_pa_sim.m` | **Engine** — takes `cfg`, returns `results` |
| `validate_cfg.m` | Input validation — called automatically by the engine |
| `gaussian_beam_params.m` | Focused Gaussian beam parameters |
| `build_intensity_map.m` | 2D intensity map with Beer-Lambert attenuation |
| `build_property_maps.m` | Spatial maps of optical and nonlinear coefficients |
| `visualize_pa.m` | 3-panel visualization (p0, B-scan, RF trace) |
| `scenario_baseline.m` | Example scenario — single absorbing target, linear regime |

---

## Creating a New Scenario

Copy `scenario_baseline.m`, rename it (e.g. `scenario_fs_pulse.m`), and modify the parameters.
The minimum required pattern is:

```matlab
clearvars; close all; clc;

% --- Label (drives figure title and save filename) ---
cfg.label = 'My Scenario';

% --- Beam ---
cfg.lambda        = 1064e-9;    % [m]
cfg.NA            = 0.55;
cfg.n             = 1.33;
cfg.target_depth  = 3e-3;       % [m]
cfg.target_radius = 5e-6;       % [m]

% --- Input radiation ---
cfg.fluence_focus  = 20;        % [J/cm²]
cfg.pulse_duration = 5e-9;      % [s]

% --- Grüneisen ---
cfg.Gamma = 0.12;

% --- Tissue optical properties @ wavelength [m⁻¹] ---
cfg.mu_a_tissue = 18;
cfg.mu_s_tissue = 91;           % FULL scattering coeff [m^-1], NOT reduced mu_s'

% --- Target optical properties [m⁻¹] ---
cfg.mu_a_target   = 500;
cfg.mu_s_target   = 10;
cfg.alpha2_target = 9e-13;      % TPA [m/W]  — set 0 for linear
cfg.alpha3_target = 0;          % 3PA [m²/W²]

% --- Acoustic medium ---
cfg.c_sound     = 1500;         % [m/s]
cfg.rho         = 1000;         % [kg/m³]
cfg.alpha_coeff = 0.75;         % [dB/MHz^y/cm]
cfg.alpha_power = 1.5;

% --- Transducer ---
cfg.f_grid = 50e6;        % [Hz]
cfg.PPW_acoustic = 10;
cfg.n_elements   = 128;

% --- Grid extents ---
cfg.z_max = 6e-3;               % [m] — must be > target_depth + ~2 mm
cfg.y_max = 1.5e-3;             % [m] half-width

% --- Optical resolution ---
cfg.PPW_optical = 5;
cfg.opt_margin  = 5;            % optical grid half-extent in target radii

% --- Solver ---
cfg.pml_size = 40;
cfg.verbose  = true;

% --- Run / load ---
save_path   = ['results_' lower(strrep(cfg.label, ' ', '_')) '.mat'];
force_rerun = false;

if ~force_rerun && exist(save_path, 'file')
    fprintf('Loading %s\n', save_path);
    load(save_path, 'results');
else
    results = run_pa_sim(cfg);
    save(save_path, 'results', '-v7.3');
end

visualize_pa(results);
```

### To re-visualize later without re-running

```matlab
visualize_pa('results_my_scenario.mat')
```

---

## Simulation Pipeline

```
cfg
 │
 ├─ 1. gaussian_beam_params     → beam geometry (w0, zR, w_surface)
 ├─ 2. build_intensity_map      → I_map on acoustic grid (Beer-Lambert)
 ├─ 3. optical grid intensity   → I_opt_map at fine resolution near focus
 ├─ 4. build_property_maps      → mu_a, alpha2, alpha3 on optical grid
 ├─ 5. energy deposition        → Q = N·(μa·I + α2·I² + α3·I³)·τ  [J/m³]  (N=1 for single pulse)
 ├─ 6. initial pressure         → p0 = Γ·Q  [Pa]
 ├─ 7. interpolate p0           → optical grid → acoustic grid
 └─ 8. kspaceFirstOrder2D       → sensor_data [n_elements × Nt]
```

Two grids are used throughout:
- **Acoustic grid** — full domain, spacing `dx = c / (f · PPW_acoustic)`, used for Beer-Lambert and k-Wave
- **Optical grid** — focal region only, spacing `dy = w0 / PPW_optical`, used for energy deposition

---

## Results Struct

| Field | Size | Description |
|-------|------|-------------|
| `sensor_data` | `[n_elements × Nt]` | Raw PA time traces |
| `kgrid` | struct | k-Wave grid (spacing, axes, time array) |
| `p0_acoustic` | `[Nz × Ny]` | Initial pressure on acoustic grid |
| `p0_opt` | `[Nz_opt × Ny_opt]` | Initial pressure on optical grid |
| `Q_opt` | `[Nz_opt × Ny_opt]` | Energy deposition map |
| `I_opt_map` | `[Nz_opt × Ny_opt]` | Intensity on optical grid |
| `I_map` | `[Nz × Ny]` | Intensity on acoustic grid |
| `beam` | struct | Beam parameters (w0, zR, w_surface) |
| `z_vec`, `y_vec` | vectors | Acoustic grid axes |
| `z_opt_vec`, `y_opt_vec` | vectors | Optical grid axes |
| `element_y` | `[1 × n_elements]` | Transducer element positions |
| `cfg` | struct | Full configuration — complete reproducibility |
| `burst_N` | scalar | Number of pulses in burst (only present when `burst_N > 1`) |
| `burst_tau` | scalar | Burst window duration [s] (only present when `burst_N > 1`) |
| `burst_fR` | scalar | Intra-burst repetition rate [Hz] = `burst_N / burst_tau` (only present when `burst_N > 1`) |
| `beam_y_center` | scalar | Beam lateral offset [m] (only present when non-zero) |
| `target_y` | scalar | Target lateral position [m] (only present when non-zero) |
| `snr_dB` | scalar | SNR used for noise addition [dB, peak-referenced] — `Inf` when no noise was added |
| `f_max_acoustic` | scalar | Low-pass cut-off frequency [Hz] — `Inf` when no filter was applied |
| `T_ballistic` | scalar | Ballistic transmission to the focal plane — `exp(−µ_t · d)` |
| `E_focus` | scalar | Per-pulse energy at the focal plane [J] |
| `E_surface` | scalar | Per-pulse energy required at the tissue surface [J] = `E_focus / T_ballistic` |
| `F_surface` | scalar | Per-pulse fluence at the tissue surface [J/cm²] |

---

## Parameter Reference

### Beam

| Parameter | Unit | Description |
|-----------|------|-------------|
| `lambda` | m | Laser wavelength |
| `NA` | — | Objective numerical aperture (must be < `n`) |
| `n` | — | Refractive index of medium |
| `target_depth` | m | Focal depth — must be < `z_max` |
| `target_radius` | m | Target radius |

Derived: `w0 = λ/(π·NA)`, `zR = π·w0²·n/λ`, `w_surface = w0·√(1+(z_focus/zR)²)`

### Input Radiation

| Parameter | Unit | Description |
|-----------|------|-------------|
| `fluence_focus` | J/cm² | Peak fluence at focus — always per pulse |
| `pulse_duration` | s | Single pulse duration |

### Burst Mode (optional)

| Parameter | Unit | Description |
|-----------|------|-------------|
| `burst_N` | — | Number of pulses per burst (default: 1, i.e. single pulse) |
| `burst_tau` | s | Burst window duration — required when `burst_N > 1` |

When `burst_N > 1`, the engine multiplies Q by N: `Q = burst_N · (μa·I + α2·I² + α3·I³) · τ_pulse`. The intra-burst repetition rate `f_R = burst_N / burst_tau` is derived and stored in results. `burst_tau` does not affect the simulated pressure — it is used only to characterise the laser and display `f_R`.

### Acoustic bandwidth limit (optional)

| Parameter | Unit | Description |
|-----------|------|-------------|
| `f_max_acoustic` | Hz | Low-pass cut-off frequency applied to `sensor_data` after k-Wave. Models the maximum acoustic frequency that propagates meaningfully in tissue. A 5th-order zero-phase Butterworth filter (`filtfilt`) is applied per element. Omit or set to `Inf` to retain all frequencies (default). |

Applied **before** noise so that detector noise remains within the signal band.

### Noise (optional)

| Parameter | Unit | Description |
|-----------|------|-------------|
| `snr_dB` | dB | Peak-referenced SNR — Gaussian noise is added to `sensor_data` via k-Wave's `addNoise`. Omit or set to `Inf` for a noise-free simulation (default). |

Noise is added **after** k-Wave propagation and GPU gather, so it models detector/electronic noise rather than acoustic noise. The same seed is not fixed — each run produces a different noise realisation.

### Scanning / OR-PAM (optional)

| Parameter | Unit | Description |
|-----------|------|-------------|
| `beam_y_center` | m | Lateral position of the beam axis (default: 0 — on-axis) |
| `target_y` | m | Lateral position of the target centre (default: 0 — on-axis) |

Both parameters default to `0`, so all existing single-position scenarios run identically without modification.

When scanning, set `beam_y_center` to the current scan position and `target_y` to the absorber's true lateral coordinate. The optical grid automatically follows the beam (`y_opt_vec` is centred at `beam_y_center`). If the target falls outside the optical grid (i.e. `|target_y − beam_y_center| > opt_margin · target_radius`) it contributes no energy deposition — correct physics for a non-illuminated absorber. The Beer-Lambert intensity map on the acoustic grid is also shifted accordingly.

### Optical Properties

| Parameter | Unit | Description |
|-----------|------|-------------|
| `mu_a_tissue` | m⁻¹ | Tissue absorption |
| `mu_s_tissue` | m⁻¹ | Tissue scattering — **must be the full scattering coefficient** (not reduced µ_s′) |
| `mu_a_target` | m⁻¹ | Target absorption |
| `mu_s_target` | m⁻¹ | Target scattering — **must be the full scattering coefficient** (not reduced µ_s′) |
| `alpha2_target` | m/W | Two-photon absorption coefficient |
| `alpha3_target` | m²/W² | Three-photon absorption coefficient |
| `Gamma` | — | Grüneisen parameter (~0.12 for tissue) |

`mu_t = mu_a + mu_s` drives Beer-Lambert depletion using the **ballistic-photon model**: every scattered photon is treated as lost from the focused beam. `mu_s` must be the full scattering coefficient, not the reduced coefficient µ_s′ = µ_s(1−g). Only `mu_a` (and nonlinear terms) contribute to energy deposition.

### Acoustic Medium

| Parameter | Unit | Description |
|-----------|------|-------------|
| `c_sound` | m/s | Speed of sound |
| `rho` | kg/m³ | Density |
| `alpha_coeff` | dB/MHz^y/cm | Acoustic absorption (k-Wave convention) |
| `alpha_power` | — | Power law exponent |

### Grid & Solver

| Parameter | Unit | Description |
|-----------|------|-------------|
| `z_max` | m | Axial domain extent |
| `y_max` | m | Lateral half-extent |
| `f_grid` | Hz | Maximum acoustic frequency — sets grid spacing via `dx = c / (f_grid · PPW)` |
| `PPW_acoustic` | — | Points per wavelength, acoustic grid (≥ 6 recommended) |
| `PPW_optical` | — | Points per beam waist, optical grid (≥ 3 recommended) |
| `opt_margin` | — | Optical grid half-extent in multiples of `target_radius` |
| `n_elements` | — | Number of transducer elements |
| `pml_size` | grid pts | PML thickness (≥ 20; 40 recommended to avoid back-wall reflections) |
