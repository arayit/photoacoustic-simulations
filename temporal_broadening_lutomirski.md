# Temporal Broadening of Ultrashort Pulses in Scattering Media

## Goal
Create a MATLAB visualization of the temporal broadening (axial variance σ²_z) of a femtosecond pulse propagating through scattering tissue, using the analytical model from Lutomirski et al. (1995).

**Reference:** R. F. Lutomirski, A. P. Ciervo, and G. J. Hall, "Moments of multiple scattering," Appl. Opt. 34, 7125–7136 (1995).

---

## Physical Situation

A ~100 fs laser pulse at 1064 nm propagates into scattering tissue (e.g., porcine liver). As it propagates, scattered photons take longer zigzag paths compared to ballistic (unscattered) photons. This causes the photon cloud to spread in time — the pulse temporally broadens.

Lutomirski provides exact closed-form expressions for the mean delay and temporal spread (axial variance) as a function of propagation depth, without requiring Monte Carlo simulation.

---

## Parameters

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| Scattering coefficient | μ_s | 4340 | m⁻¹ |
| Anisotropy factor | g = ⟨cos θ⟩ | 0.93 | — |
| Refractive index | n | 1.4 | — |
| Speed of light in medium | c = c₀/n | 2.14 × 10⁸ | m/s |
| Mean free path | ℓ_s = 1/μ_s | 230 | μm |
| Input pulse duration (FWHM) | τ_p | 100 | fs |

### Derived parameters

Assuming Henyey-Greenstein phase function:

```
⟨cos²θ⟩ = (1 + 2g²) / 3
```

Then:

```
v = 1 - g = 0.07
w = (3/2) * (1 - ⟨cos²θ⟩) = 0.1351
```

---

## Normalized Units

Lutomirski uses normalized units throughout:

- **Normalized time:** T = μ_s * c * t (dimensionless; T = 1 means one mean-free-path transit time)
- **Normalized distance:** z_norm = z_physical * μ_s (dimensionless; z_norm = 1 means one mean free path)
- **Conversion back to real time:** t = T / (μ_s * c)
- **Conversion back to real distance:** z = z_norm / μ_s

---

## Equations to Plot

### 1. Mean normalized time to reach depth z (Eq. 45a)

```
T(z) = (1/v) * ln(1 / (1 - v*z))
```

where z is in normalized units.

### 2. Mean time delay relative to ballistic photon (Eq. 45b)

```
ΔT(z) = (1/v) * ln(1 / (1 - v*z)) - z
```

Convert to real time: Δt = ΔT / (μ_s * c)

### 3. Axial variance σ²_z(T) — the temporal spread (Eq. C7)

```
σ²_z(T) = (2/3) * [(w² - 3wv)*(exp(-vT) - 1 + vT) + 2v²*(exp(-wT) - 1 + wT)] / [w * v² * (w - v)]
           - [(1 - exp(-vT)) / v]²
```

Convert to real time spread: σ_t = σ_z / (μ_s * c)

### 4. Transverse variance σ²_x(T) — lateral blurring (Eq. C5, optional)

```
σ²_x(T) = (2/3) * [w*(exp(-vT) - 1 + vT) - v*(exp(-wT) - 1 + wT)] / [w * v² * (w - v)]
```

Convert to real distance: σ_x_real = σ_x_norm / μ_s

---

## Visualization Requests

### Plot 1: Temporal spread σ_t vs. depth
- X-axis: physical depth z from 0 to 3 mm
- Y-axis: σ_t in picoseconds
- Add a horizontal dashed line at 100 fs (the input pulse duration) for reference
- This shows where the scattered photon spread exceeds the pulse duration

### Plot 2: Mean time delay Δt vs. depth
- X-axis: physical depth z from 0 to 3 mm
- Y-axis: Δt in picoseconds
- Shows how much the centroid of the photon cloud lags behind ballistic photons

### Plot 3: Combined temporal profile at a given depth
- Show a schematic of the temporal intensity profile at z = 500 μm and z = 2 mm
- Ballistic component: Gaussian with FWHM = 100 fs, amplitude decaying as exp(-μ_s * z) (Beer-Lambert)
- Scattered component: broader Gaussian-like profile with width ~ σ_t, centered at Δt delay
- This is qualitative/schematic — the scattered component shape is not exactly Gaussian but this gives the physical picture

### Plot 4 (optional): σ_t vs. depth for different g values
- Compare g = 0.85, 0.90, 0.93, 0.95
- Shows sensitivity to tissue type

---

## Computation Steps in MATLAB

```matlab
% Parameters
mu_s = 4340;          % m^-1
g = 0.93;
n_tissue = 1.4;
c0 = 3e8;            % m/s
c = c0 / n_tissue;   % speed in medium
ell_s = 1 / mu_s;    % mean free path in meters

% Derived
cos2theta = (1 + 2*g^2) / 3;  % Henyey-Greenstein
v = 1 - g;
w = 1.5 * (1 - cos2theta);

% Depth array (physical, in meters)
z_phys = linspace(0, 3e-3, 500);   % 0 to 3 mm
z_norm = z_phys * mu_s;             % normalized

% Mean time to reach depth z (Eq. 45a)
T = (1/v) .* log(1 ./ (1 - v.*z_norm));

% Mean delay (Eq. 45b)
DeltaT_norm = T - z_norm;
DeltaT_real = DeltaT_norm ./ (mu_s * c);  % in seconds

% Axial variance (Eq. C7)
term1_num = (w^2 - 3*w*v) .* (exp(-v.*T) - 1 + v.*T) + 2*v^2 .* (exp(-w.*T) - 1 + w.*T);
term1_den = w * v^2 * (w - v);
term1 = (2/3) .* term1_num ./ term1_den;

term2 = ((1 - exp(-v.*T)) ./ v).^2;

sigma_z_norm_sq = term1 - term2;
sigma_z_norm = sqrt(sigma_z_norm_sq);

% Convert to real time
sigma_t = sigma_z_norm ./ (mu_s * c);  % in seconds
```

---

## Expected Results

At 500 μm depth: σ_t ≈ 0.5 ps, Δt ≈ 0.2 ps
The 100 fs ballistic pulse remains much shorter than the scattered tail, supporting the argument that nonlinear (two-photon) absorption at the focal volume is dominated by ballistic photons.

---

## Important Notes

- The formula for ⟨ΔT⟩ diverges when vz → 1, i.e., z → 1/v ≈ 14.3 mean free paths ≈ 3.3 mm. Beyond this depth, the centroid model breaks down because backscatter dominates.
- σ²_z can become negative numerically for very small T due to floating point — clamp to zero.
- These are moments of the full photon distribution (ballistic + scattered). The ballistic component itself stays at 100 fs; what broadens is the scattered component.

---

## Model Validity Limit

### Why the model diverges

The Lutomirski model computes the mean normalized travel time as:

```
T(z) = (1/v) · ln( 1 / (1 - v·z_norm) )
```

where `v = 1 − g` (forward-scattering deficit) and `z_norm = z · μ_s` (depth in units of mean free paths).

This expression diverges when `v · z_norm → 1`. The **validity limit** is therefore:

```
z_limit = 1 / (v · μ_s) = 1 / ((1−g) · μ_s)
```

**Physical meaning:** The model was derived under the small-angle (paraxial) approximation — it assumes photons are still propagating mostly forward. The quantity `v · z_norm` tracks accumulated angular randomization. When it reaches 1, the photon distribution has been completely isotropized; the forward-propagating component has vanished and the concept of a well-defined mean arrival time breaks down. Beyond this depth the model has no physical validity.

### Validity limits for each tissue (at 1000 nm)

| Tissue              | μ_s (mm⁻¹) | g    | v = 1−g | z_limit (mm) |
|---------------------|-----------|------|---------|--------------|
| Native White Matter | 28.3      | 0.88 | 0.12    | ~0.30        |
| Skin (Mean)         | 20.8      | 0.94 | 0.06    | ~0.80        |
| Native Grey Matter  | 6.3       | 0.92 | 0.08    | ~1.98        |

White matter has a high scattering coefficient and a relatively low anisotropy compared to skin, so its valid depth range is the shortest. Grey matter scatters much less strongly, giving the largest valid range.

### What to do in practice

All FWHM curves in the figures are **clipped at z_limit** for each tissue/wavelength. Data beyond this point is not shown. For quantitative work, staying below `0.8 · z_limit` is advisable to remain well within the paraxial regime.
