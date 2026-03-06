# exp_003 — OR-PAM Imaging Scan with BODIPY-TR

Optical-resolution photoacoustic microscopy (OR-PAM) simulation: the focused beam is scanned laterally across a single BODIPY-TR target. At each scan position a full k-Wave simulation is run and the A-scan is recorded. All A-scans are assembled into a B-scan image in `plot_results.m`.

Physics is identical to exp_002 (BODIPY-TR, pure TPA, 10× fluence regime).

---

## Scene

| Parameter | Value |
|---|---|
| Target y | 0 (centre) |
| Target z | 3 mm |
| Target radius | 5 μm |
| Contrast agent | BODIPY-TR (pure TPA) |

---

## Common Parameters

| Parameter | Value |
|---|---|
| Wavelength | 1064 nm |
| NA | 0.55 (Mitutoyo Plan Apo) |
| Beam waist w₀ | ~0.62 μm |
| μa_target | 0 (no linear absorption) |
| α₂_target | 9×10⁻¹⁴ m/W (~280 GM at 1 mM) |
| μa_tissue | 18 m⁻¹ @ 1064 nm |
| μs'_tissue | 91 m⁻¹ @ 1064 nm |

---

## Scan Parameters

| Parameter | Value |
|---|---|
| Scan range | −65 to +65 μm |
| Step size | 2 μm |
| Scan positions | 66 |
| `beam_y_center` | y_scan (shifts optical grid + beam) |
| `target_y` | 0 (fixed, always at centre) |

---

## Scenarios

| Label prefix | Type | τ_pulse | F_pulse | N | τ_burst |
|---|---|---|---|---|---|
| `s01_ns` | NS single pulse | 3 ns | 13.2 J/cm² | — | — |
| `s02_fs` | FS single pulse | 100 fs | 1 J/cm² | — | — |
| `s03_b300` | FS burst | 100 fs | 1 J/cm² | 300 | 3 ns |

**Total runs: 3 × 66 = 198 ≈ 3.3 hrs**

---

## Files

```
exp_003/
├── README.md
├── run_scenarios.m    ← runs all 198 simulations
├── plot_results.m     ← assembles B-scans and lateral profiles
└── results/           ← .mat files (git-ignored)
```

## Output

- **B-scan** (Figure 1): 3-panel log-compressed image, x = lateral position, y = depth. Target appears as a bright spot at y=0, z=3 mm. Signal drops to near-zero within ~7 μm of the target edge (set by w₀ ≈ 0.62 μm).
- **Lateral profile** (Figure 2): max projection along depth — shows the OR-PAM lateral point spread function for each illumination type.
