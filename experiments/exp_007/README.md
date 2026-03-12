# exp_007 — Realistic Fluence Depth Study

Photoacoustic signal characterization versus target depth for nanosecond, femtosecond, and GHz burst-mode excitation with physically constrained fluence levels.

## Motivation

exp_006 used near-ablation-threshold fluences (1–10 J/cm²), producing initial pressures in the GPa range — unrealistic for biological tissue. This experiment reduces fluence and contrast agent concentration to keep pressures within safe limits while preserving the enhancement physics.

## Changes from exp_006

| Parameter | exp_006 | exp_007 |
|-----------|---------|---------|
| NS pulse duration | 3 ns | 1 ns |
| NS fluence | 10 J/cm² | 1.0 J/cm² |
| FS/burst fluence | 1 J/cm² | 0.1 J/cm² |
| α₂ (TPA coefficient) | 9×10⁻¹³ m/W (10 mM) | 9×10⁻¹⁴ m/W (1 mM) |
| Burst duration | 3 ns | 1 ns |
| Intra-burst rate | 10 GHz | 100 GHz |
| Burst N range | 20–300 | 10–100 |
| Depth range | 0.1–3.0 mm, 100 µm steps | 0.1, 0.5–3.0 mm, 500 µm steps |
| Total scenarios | 510 | 84 |

## Configuration

| Parameter | Value |
|-----------|-------|
| Wavelength | 1064 nm |
| NA | 0.50 |
| Refractive index | 1.33 |
| Target radius | 5 µm |
| Grüneisen parameter | 0.12 |
| Tissue µ_a | 18 m⁻¹ |
| Tissue µ_s | 91 m⁻¹ (used as-run; this was actually µ_s′, not the full scattering coeff — corrected to 4340 m⁻¹ in exp_008) |
| Contrast agent | BODIPY-TR (~1 mM) |
| α₂ | 9×10⁻¹⁴ m/W |
| Speed of sound | 1500 m/s |
| Grid frequency | 50 MHz (dx ≈ 3 µm) |
| Sensor elements | 128 |
| SNR | 40 dB |
| z_max | target depth + 2 mm |

## Pulse Types (12)

| Tag | Type | τ_pulse | Fluence | N |
|-----|------|---------|---------|---|
| ns | Nanosecond | 1 ns | 1.0 J/cm² | 1 |
| fs | Femtosecond | 100 fs | 0.1 J/cm² | 1 |
| b010–b100 | Burst | 100 fs | 0.1 J/cm²/pulse | 10–100 |

Fluence ratio follows the intensity scaling law with ω = 0.75:
F_NS / F_FS = (τ₀/τ_p)^(1−ω) = (1 ns / 100 fs)^0.25 = 10.

## Depths (7)

0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 mm

## Stress Confinement

τ_st = d_c / v_s ≈ 1.36 µm / 1500 m/s ≈ 0.9 ns

Both the NS pulse (1 ns) and burst window (1 ns) are close to τ_st. Marginally within the stress-confined regime.

## Expected Initial Pressures

| Scenario | Focal p₀ |
|----------|----------|
| NS (1 ns) | ~80 Pa |
| FS (100 fs) | ~720 kPa |
| Burst N=10 | ~7.2 MPa |
| Burst N=30 | ~21.6 MPa |
| Burst N=100 | ~72 MPa |

## Theoretical Enhancement

ε = N × √(τ₀/τ_p) = N × √(1 ns / 100 fs) = N × 100

| N | Enhancement |
|---|-------------|
| 10 | 1,000× |
| 50 | 5,000× |
| 100 | 10,000× |

## Figures produced by plot_results.py

| File | Description |
|------|-------------|
| `peak_pressure_vs_depth.{fmt}` | Peak PA pressure vs depth for all pulse types |
| `enhancement_vs_depth.{fmt}` | Burst N=100 / NS enhancement vs depth |
| `enhancement_vs_N.{fmt}` | Enhancement vs burst N at each depth |
| `waveform_comparison_{d}mm.{fmt}` | PA waveform comparison at 1.0 and 3.0 mm |
| `p0_comparison_{d}mm.{fmt}` | p0 map: NS vs Burst N=100 at 1.0 and 3.0 mm |
| `p0_ns_vs_fs_{d}mm.{fmt}` | p0 map: NS vs FS at 1.0 and 3.0 mm |

## Running

```
matlab -batch "cd('C:\Users\SYAVAS-LASERLAB\Documents\MATLAB\photoacoustic-simulations\experiments\exp_007'); run_scenarios"
```
