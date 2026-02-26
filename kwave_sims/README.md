# Baseline Photoacoustic Simulation

## File Structure

| File | Description |
|------|-------------|
| `baseline_photoacoustic_simulation.m` | Main simulation script |
| `gaussian_beam_params.m` | Computes focused Gaussian beam parameters |
| `build_intensity_map.m` | Builds the 2D normalized intensity map |

---

## Beam Geometry & Focusing

### Input Parameters

| Parameter | Variable | Unit | Description |
|-----------|----------|------|-------------|
| Wavelength | `lambda` | m | Excitation laser wavelength |
| Numerical aperture | `NA` | — | Objective lens NA |
| Refractive index | `n` | — | Refractive index of the medium |
| Target / focal depth | `target_depth` | m | Depth of the target; beam is focused here |

### Derived Parameters

| Parameter | Variable | Formula | Description |
|-----------|----------|---------|-------------|
| Beam waist | `w0` | `λ / (π · NA)` | Minimum beam radius at focus |
| Rayleigh range | `zR` | `π · w0² · n / λ` | Depth over which beam area doubles; corrected for medium |
| Beam radius at surface | `w_surface` | `w0 · √(1 + (z_focus/zR)²)` | Beam radius where it enters the medium |
| Beam radius at depth z | `w_z` | `w0 · √(1 + (Δz/zR)²)` | Δz = z − z_focus |
| Focusing gain at depth z | — | `(w_surface / w_z)²` | Relative intensity increase due to focusing |

### Intensity Map

The normalized 2D intensity distribution `I_map(z, y)` is:

```
I(z, y) = (w_surface / w(z))² · exp(−2y² / w(z)²)
```

The peak value equals 1.0 at the focal point. Absolute intensity is obtained by multiplying by the peak surface intensity.

---

## Functions

### `gaussian_beam_params(lambda, NA, n, z_focus)`

| Argument | Type | Unit | Description |
|----------|------|------|-------------|
| `lambda` | scalar | m | Laser wavelength |
| `NA` | scalar | — | Objective numerical aperture |
| `n` | scalar | — | Refractive index of the medium |
| `z_focus` | scalar | m | Focal depth (= target depth) |

Returns a struct `beam` with fields: `lambda`, `NA`, `n`, `z_focus`, `w0`, `zR`, `w_surface`.

---

### `build_intensity_map(beam, z_vec, y_vec, I_surface_peak, mu_t_map)`

| Argument | Type | Unit | Description |
|----------|------|------|-------------|
| `beam` | struct | — | Output of `gaussian_beam_params` |
| `z_vec` | 1×Nz vector | m | Axial grid positions |
| `y_vec` | 1×Ny vector | m | Lateral grid positions |
| `I_surface_peak` | scalar | W/m² | Peak intensity at the tissue surface (on-axis) |
| `mu_t_map` | Nz×Ny matrix | m⁻¹ | Total attenuation coefficient map (optional; defaults to zero) |

Returns `I_map` (Nz × Ny) in absolute units [W/m²].

**Input radiation:**

Surface peak intensity is derived from fluence and pulse duration in the main script:
```
I_surface_peak = (fluence [J/cm²] × 1e4) / pulse_duration [s]   →   [W/m²]
```

**Beam depletion model:**

At each depth step, Beer-Lambert attenuation is accumulated using the intensity-weighted lateral average of `mu_t`:

```
accumulated_att(z) = ∫₀ᶻ μ_t_eff(z') dz'

μ_t_eff(z) = Σ [ μ_t(z,y) · I(z,y) ] / Σ I(z,y)     [m⁻¹]

I(z, y) = (w_surface/w(z))² · exp(−accumulated_att) · exp(−2y²/w(z)²)
```

---

## Grid Parameters

| Parameter | Variable | Unit | Description |
|-----------|----------|------|-------------|
| Axial extent | `z_max` | m | Total simulation depth |
| Lateral extent | `y_max` | m | Half-width of lateral domain |
| Axial resolution | `dz` | m | Grid spacing along z |
| Lateral resolution | `dy` | m | Grid spacing along y |
