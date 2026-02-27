# Linear vs. Nonlinear PA Study

Separation and comparison of linear and multiphoton absorption contributions to the photoacoustic signal.

---

## Scientific Goal

In the energy deposition equation:

```
Q = (μa·I + α2·I² + α3·I³) · τ
```

- `μa·I` — linear absorption: occurs everywhere along the beam path (tissue + target)
- `α2·I²` — two-photon absorption (TPA): confined to the focal volume (scales as intensity²)
- `α3·I³` — three-photon absorption (3PA): even more tightly confined (scales as intensity³)

The challenge: linear background from tissue can dominate. Linear and nonlinear signals from the target are **co-located in depth and time**, and cannot be separated in a single measurement.

The key: linear PA scales as `I`, nonlinear PA scales as `I²` or `I³`. They have different intensity dependencies — this is the handle for separation.

---

## Experiment Design

Four simulations are run with identical beam/grid/acoustic parameters, differing only in absorption properties:

| Run | Label | μa_target | α2_target | Description |
|-----|-------|-----------|-----------|-------------|
| A | `linear_only` | 500 m⁻¹ | 0 | Linear absorption in target only |
| B | `nonlinear_only` | = μa_tissue | 9e-13 m/W | TPA in target, no extra linear absorption |
| C | `combined` | 500 m⁻¹ | 9e-13 m/W | Realistic: both linear and TPA in target |
| D | `background` | = μa_tissue | 0 | Tissue only — no target |

---

## Analysis (done separately, after all simulations are saved)

From the four saved results:

- **SBR_linear** = peak(A) / peak(D)
- **SBR_nonlinear** = peak(B) / peak(D)
- **SBR_combined** = peak(C) / peak(D)
- **Nonlinear contribution** = peak(C) − peak(A)  vs.  linear contribution = peak(A) − peak(D)

---

## File Organization

```
linear_vs_nonlinear/
├── README.md                        ← this file
├── run_scenarios.m                  ← runs all 4 simulations, saves results
├── analyse_results.m                ← loads saved results, computes metrics, plots
└── results/                         ← saved .mat files (git-ignored)
    ├── results_linear_only.mat
    ├── results_nonlinear_only.mat
    ├── results_combined.mat
    └── results_background.mat
```

---

## Engine

All simulations use `../engine/run_pa_sim.m`.
