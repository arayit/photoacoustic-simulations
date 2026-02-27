# exp_001 — TPA-PA with BODIPY-TR

Photoacoustic signal generation via two-photon absorption (TPA) in a BODIPY-TR contrast agent, compared against nanosecond and femtosecond excitation regimes including burst mode.

---

## Common Parameters

| Parameter | Value |
|---|---|
| Wavelength | 1064 nm |
| NA | 0.55 (Mitutoyo Plan Apo) |
| Target depth | 3 mm |
| Target radius | 5 μm |
| Contrast agent | BODIPY-TR |
| μa_target | 0 (no linear absorption) |
| α₂_target | 9×10⁻¹⁴ m/W (~280 GM at 1 mM) |
| μa_tissue | 18 m⁻¹ @ 1064 nm |
| μs'_tissue | 91 m⁻¹ @ 1064 nm |

---

## Scenarios

| Label | Type | τ | F per pulse | N | Total F |
|---|---|---|---|---|---|
| `s01_ns_tau3ns_F1` | NS single pulse | 3 ns | 1 J/cm² | — | 1 J/cm² |
| `s02_fs_tau100fs_F01` | FS single pulse | 100 fs | 0.1 J/cm² | — | 0.1 J/cm² |
| `s03_burst_N010` … `s03_burst_N300` | FS burst | 100 fs | 0.1 J/cm² | 10:10:300 | 1–30 J/cm² |

Burst parameters: τ_burst = 3 ns, intra-burst rate = N/τ_burst.

**Total runs: 32**

---

## Files

```
exp_001/
├── README.md
├── run_scenarios.m    ← runs all 32 simulations, saves results
└── results/           ← .mat files saved here (git-ignored)
```
