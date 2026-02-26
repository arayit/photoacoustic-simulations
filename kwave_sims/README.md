# Baseline Photoacoustic Simulation

## File Structure

| File | Description |
|------|-------------|
| `scenario_baseline.m` | Entry point — builds `cfg`, calls `run_baseline_pa`, saves/loads results, calls `visualize_pa` |
| `run_baseline_pa.m` | Simulation function — takes `cfg` struct, returns `results` struct |
| `visualize_pa.m` | Visualization function — takes `results` struct, plots p0, B-scan, RF trace |
| `gaussian_beam_params.m` | Computes focused Gaussian beam parameters |
| `build_intensity_map.m` | Builds the 2D absolute intensity map with Beer-Lambert attenuation |
| `build_property_maps.m` | Builds mu_a and mu_t maps over a grid given tissue and target properties |
| `baseline_photoacoustic_simulation.m` | Standalone script (reference) |

### Calling convention

```matlab
% In a scenario script:
cfg.lambda = 1064e-9;
% ... (all parameters) ...
results = run_baseline_pa(cfg);       % run simulation
save('my_results.mat', 'results');    % optional save
visualize_pa(results);                % plot

% To re-visualize saved results without re-running:
load('my_results.mat', 'results');
visualize_pa(results);
```

`results` fields: `sensor_data`, `kgrid`, `p0_acoustic`, `p0_opt`, `Q_opt`, `I_opt_map`, `I_map`, `beam`, `z_vec`, `y_vec`, `z_opt_vec`, `y_opt_vec`, `element_y`, `cfg`.

---

## Simulation Pipeline

1. **Beer-Lambert propagation** — intensity computed on global grid (acoustic spacing). Outputs accumulated attenuation profile `acc_att_vec`.
2. **Optical grid intensity** — accumulated attenuation interpolated from global grid to optical grid z-positions. Gaussian beam evaluated analytically at fine optical resolution.
3. **Energy deposition** — `Q = (μ_a·I + α₂·I² + α₃·I³) · τ` [J/m³] on optical grid.
4. **Initial pressure** — `p0 = Γ · Q` [Pa] on optical grid.
5. **Interpolation** — `p0` interpolated from optical grid onto acoustic grid using `griddedInterpolant`. Values outside optical domain set to zero.
6. **Acoustic propagation** — k-Wave runs on acoustic grid with `p0_acoustic` as source.

---

## Parameters

### Beam

| Variable | Unit | Description |
|----------|------|-------------|
| `lambda` | m | Laser wavelength |
| `NA` | — | Objective numerical aperture |
| `n` | — | Refractive index of the medium |
| `target_depth` | m | Focal depth (= target depth) |
| `target_radius` | m | Target radius |

Derived:

| Variable | Formula | Description |
|----------|---------|-------------|
| `w0` | `λ / (π · NA)` | Beam waist at focus |
| `zR` | `π · w0² · n / λ` | Rayleigh range in medium |
| `w_surface` | `w0 · √(1 + (z_focus/zR)²)` | Beam radius at tissue surface |

### Input Radiation

| Variable | Unit | Description |
|----------|------|-------------|
| `fluence_focus` | J/cm² | Peak fluence at the focal point |
| `pulse_duration` | s | Pulse duration |
| `I_focus_peak` | W/m² | `(fluence_focus × 1e4) / pulse_duration` |
| `I_surface_peak` | W/m² | `I_focus_peak × (w0 / w_surface)²` |

### Grids

| Variable | Unit | Description |
|----------|------|-------------|
| `f_transducer` | Hz | Transducer center frequency — sets acoustic grid |
| `PPW_acoustic` | — | Points per wavelength for acoustic grid |
| `dx_acoustic` | m | `c_sound / (f_transducer × PPW_acoustic)` |
| `PPW_optical` | — | Points per beam waist for optical grid |
| `dy_optical` | m | `w0 / PPW_optical` |

Two grids are used: a **global acoustic grid** (full domain, `dx_acoustic` spacing) for Beer-Lambert propagation and k-Wave; and a **local optical grid** (focal region only, `dy_optical` spacing) for energy deposition.

### Detection

| Variable | Unit | Description |
|----------|------|-------------|
| `n_elements` | — | Number of transducer elements |
| `element_pitch` | m | Element spacing — derived as `c_sound / (2 · f_transducer)` (λ/2) |

Array is placed at the tissue surface (z=0, first grid row), centered at y=0. Element positions are mapped to the nearest acoustic grid points.

---

### Acoustic Medium Properties

| Variable | Unit | Description |
|----------|------|-------------|
| `c_sound` | m/s | Speed of sound |
| `rho` | kg/m³ | Medium density |
| `alpha_coeff` | dB/MHz^y/cm | Acoustic absorption coefficient |
| `alpha_power` | — | Power law exponent y |

Acoustic medium is assumed homogeneous. These map directly to k-Wave `medium` struct fields.

---

### Optical Properties

| Variable | Unit | Description |
|----------|------|-------------|
| `mu_a_tissue` | m⁻¹ | Tissue absorption coefficient |
| `mu_s_tissue` | m⁻¹ | Tissue reduced scattering coefficient |
| `mu_t_tissue` | m⁻¹ | `mu_a + mu_s` — total attenuation (tissue) |
| `Gamma` | — | Grüneisen parameter (tissue ~0.12) |
| `mu_a_target` | m⁻¹ | Target absorption coefficient |
| `mu_s_target` | m⁻¹ | Target reduced scattering coefficient |
| `mu_t_target` | m⁻¹ | `mu_a + mu_s` — total attenuation (target) |
| `alpha2_target` | m/W | Two-photon absorption coefficient |
| `alpha3_target` | m²/W² | Three-photon absorption coefficient |

`mu_t` drives Beer-Lambert beam depletion. `mu_a` drives energy deposition (only absorbed photons heat the medium).

---

## Functions

### `gaussian_beam_params(lambda, NA, n, z_focus)`
Returns struct `beam`: `w0`, `zR`, `w_surface`, `z_focus`.

### `build_property_maps(z_vec, y_vec, mu_a_bg, mu_t_bg, mu_a_tgt, mu_t_tgt, z_target, r_target, alpha2_bg, alpha2_tgt, alpha3_bg, alpha3_tgt)`
Returns `mu_a_map`, `mu_t_map`, `alpha2_map`, `alpha3_map` (Nz × Ny). Nonlinear coefficients optional (default zero). Background tissue everywhere, target region overwritten.

---

### `build_intensity_map(beam, z_vec, y_vec, I_surface_peak, mu_t_map)`
Returns `I_map` [W/m²] (Nz × Ny) and `acc_att_vec` (Nz × 1) — accumulated attenuation at each depth. `mu_t_map` is optional (default: zero).

Beam depletion: accumulated Beer-Lambert with intensity-weighted `mu_t` at each depth step.
