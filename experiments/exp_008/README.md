# exp_008 — Burst Rate Comparison: 100 GHz vs 1 THz

Compares burst-mode PA signal and thermal response for N=100 (100 GHz) and N=1000 (1 THz) intra-burst repetition rates, using corrected tissue scattering (full µ_s, not µ_s′).

## Motivation

exp_007 used µ_s = 91 m⁻¹, which was actually the **reduced** scattering coefficient µ_s′. The ballistic-photon model requires the **full** scattering coefficient. This experiment repeats the N=100 and N=1000 burst comparison with the corrected value (µ_s = 4340 m⁻¹, native porcine liver at 1070 nm, Ritz et al.), and also evaluates the potential of 1 THz burst rates.

## Changes from exp_007

| Parameter | exp_007 | exp_008 |
|-----------|---------|---------|
| Tissue µ_s | 91 m⁻¹ (µ_s′, incorrect) | 4340 m⁻¹ (full, corrected) |
| Pulse types | NS + FS + burst N=10–100 | Burst N=100 and N=1000 only |
| Total scenarios | 84 | 14 |

## Configuration

| Parameter | Value |
|-----------|-------|
| Wavelength | 1064 nm |
| NA | 0.50 |
| Refractive index | 1.33 |
| Target radius | 5 µm |
| Grüneisen parameter | 0.12 |
| Tissue µ_a | 18 m⁻¹ |
| Tissue µ_s (full) | 4340 m⁻¹ |
| Tissue µ_t | 4358 m⁻¹ |
| Contrast agent | BODIPY-TR (~1 mM) |
| α₂ | 9×10⁻¹⁴ m/W |
| Speed of sound | 1500 m/s |
| Grid frequency | 50 MHz (dx ≈ 3 µm) |
| Sensor elements | 128 |
| SNR | 40 dB |

## Pulse Types (2)

| Tag | Type | τ_pulse | Fluence | N | Burst window | f_R |
|-----|------|---------|---------|---|-------------|-----|
| b0100 | Burst | 100 fs | 0.1 J/cm²/pulse | 100 | 1 ns | 100 GHz |
| b1000 | Burst | 100 fs | 0.1 J/cm²/pulse | 1000 | 1 ns | 1 THz |

## Depths (7)

0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0 mm — **Total: 14 scenarios**

## Outputs

### Results fields (per scenario)
- `sensor_data` — PA time traces
- `T_ballistic` — ballistic transmission to focal plane
- `E_focus`, `E_surface` — per-pulse energy at focus and surface [J]
- `F_surface` — per-pulse fluence at surface [J/cm²]

### Figures produced by plot_results.py

| File | Description |
|------|-------------|
| `peak_pressure_vs_depth.{fmt}` | Peak PA pressure vs depth for both burst rates |
| `peak_dT_vs_depth.{fmt}` | Peak temperature rise ΔT vs depth |
| `enhancement_vs_depth.{fmt}` | N=1000 / N=100 pressure enhancement vs depth |
| `waveform_comparison_{d}mm.{fmt}` | PA waveform comparison at 1.0 and 3.0 mm |
| `p0_comparison_{d}mm.{fmt}` | p0 map side-by-side at 1.0 and 3.0 mm |
| `dT_comparison_{d}mm.{fmt}` | ΔT map side-by-side at 1.0 and 3.0 mm |
| `energy_vs_depth.{fmt}` | Required surface energy and fluence vs depth |
| `transmission_vs_depth.{fmt}` | Ballistic transmission vs depth |

## Running

```
matlab -batch "cd('C:\Users\SYAVAS-LASERLAB\Documents\MATLAB\photoacoustic-simulations\experiments\exp_008'); run_scenarios"
```

```
python experiments/exp_008/plot_results.py [--dpi 300] [--fmt png|pdf|svg]
```
