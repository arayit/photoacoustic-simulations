# Session Summary — Burst-Mode PA Paper
**Date: 2026-03-22 (3-day working session)**

## Paper
- **Title**: Nonlinear Photoacoustic Imaging Using Femtosecond Burst Excitation
- **Target journal**: Optics Express
- **Supervisor framing**: "ultrafast burst excitation as a platform for engineering collective light-matter interactions mediated by transient material states"
- **Timeline**: few days for current draft, ~4 weeks total

## Key Decisions Made

### 1. k-Wave simulations removed
Acoustic propagation cancels in the enhancement ratio. The paper's contribution is the absorption mechanism, not imaging reconstruction. Replaced simulation section with analytical calculations.

### 2. Parameter table updated (main.tex)
- Removed: acoustic params (sound speed, density, grid, sensor, SNR), mu_a_target (negligible at 1064nm), target radius, anisotropy factor g, eta_fc
- Added: fs burst params (tau_p=100fs, F_p=0.1 J/cm^2, tau_burst=1ns), ns reference (tau_0=1ns, F_0=1.0 J/cm^2)
- Made compact: single-column, no section headers, references as footnote
- Label changed from tab:sim_params to tab:params

### 3. Gruneisen parameter: Gamma = 0.12 (tissue, not SiNP)
Reasoning: heat transfers to surrounding fluid (Chen 2012).

## Critical Physics Finding: Auger Recombination

### The problem
The original model assumed no carrier recombination (tau_r << tau_c), giving:
- Carrier density grows linearly: N_k = k * delta_N_fc
- FCA heating scales as N^2
- Enhancement epsilon ~ 10^7 for N=1000

### What we found
1. Per-pulse carrier generation: delta_N_fc ~ 4e26 m^-3 at I_p = 1 TW/cm^2
2. At this density, Auger lifetime ~ 16 ps (vs surface recomb. ~ 114 ps for d=100nm NW)
3. **Auger dominates from the first pulse** and clamps carrier density at ~8.4e26 m^-3 (only ~2x one pulse's worth)
4. The no-recombination model overestimates by ~170x

### Combined recombination model (Bernoulli equation)
The ODE dN/dt = -N/tau_s - C*N^3 (surface + Auger) is analytically solvable:

**N(t) = 1 / sqrt[ (1/N0^2 + C*tau_s) * exp(2t/tau_s) - C*tau_s ]**

Limits:
- C=0: pure surface, N = N0 * exp(-t/tau_s)
- tau_s -> inf: pure Auger, N = N0 / sqrt(1 + 2*C*N0^2*t)

Parameters:
- C_auger = 3.8e-43 m^6/s (bulk c-Si, Dziewior & Schmid 1977)
- SRV = 2.2e4 cm/s (Li 2023, Grumstrup 2014)
- tau_s = d/(4*SRV) = 114 ps for d=100nm nanowire

### Enhancement breakdown (N=1000, F_p=0.1 J/cm^2)
| Model               | epsilon    | Notes                        |
|---------------------|------------|------------------------------|
| No recombination    | 6.7e7      | Overestimate, unphysical     |
| Surface only        | ~3.8e6     | tau_s = 114 ps               |
| Auger only          | ~3.8e5     | Auger dominates              |
| Surface + Auger     | ~3.8e5     | Auger is the bottleneck      |
| TPA only (no FCA)   | 1.0e5      | Baseline burst enhancement   |

**Bottom line**: FCA adds ~4x on top of TPA, not ~670x. The 10^5 TPA scaling is the main effect.

## Source of TPA Enhancement (the solid part)
The 10^5 TPA enhancement comes from intensity scaling, NOT carrier dynamics:
- I_p = I_0 * (tau_0/tau_p)^0.75
- Each fs pulse: I_p = 1 TW/cm^2 vs I_0 = 1 GW/cm^2
- TPA per pulse: beta*I_p^2*tau_p = 1.5e8 J/m^3
- N=1000 pulses total: 1.5e11 J/m^3
- NS reference: beta*I_0^2*tau_0 = 1.5e6 J/m^3
- epsilon_TPA = 1.0e5 (rock solid, no material assumptions)

## Reference Papers on Carrier Lifetime

### Grumstrup 2014 (J. Phys. Chem. C, 118, 8634-8640)
- Individual Si NWs, diameters 38-101 nm
- Pump 425nm, probe 850nm, 2.5 pJ/pulse (LOW injection)
- tau proportional to diameter: tau = d/4S (surface recombination)
- d50: tau = 218 +/- 3 ps
- Verified linear (low-injection) regime

### Li 2023 (Nano Letters, 23, 1445-1450)
- s-SNOM near-field probe, individual Si NWs (80-260 nm)
- Pump 400nm, probe 800nm
- Initial carrier density: N(0) ~ 6.5e25 m^-3 (100x less than our per-pulse generation)
- tau_avg = 100-350 ps, linear with diameter
- SRV = 2.2e4 cm/s
- Surface recombination dominates at their densities

**Key caveat**: These lifetimes were measured at much lower carrier densities than our model produces. At our densities, Auger dominates.

## Open Directions (need professor input)

### Option A: Lead with TPA scaling
- Primary story: burst mode gives 10^5 enhancement via TPA intensity scaling
- FCA as secondary bounded effect (additional ~4x)
- Mention Auger limit in Discussion
- Clean, defensible, Optics Express appropriate
- Doesn't need deep solid-state physics

### Option B: Add Mie resonance
- Si NPs support Mie resonances at NIR — internal field enhancement
- TPA scales as E^4 — even 3x field enhancement gives 80x TPA boost
- Purely optical, size-tunable, well-established
- Combined: burst TPA scaling x Mie enhancement
- Different paper, abandons "collective/transient states" framing

### Option C: Full carrier dynamics
- Include Bernoulli recombination model properly
- Material-dependent (Auger coeff, SRV, particle geometry)
- Makes paper more solid-state than optics
- Possibly wrong for Optics Express

## Files

### analytical_calculations/burst_enhancement.py
- Clean script with closed-form TPA+FCA physics
- Bernoulli decay model (surface + Auger)
- Helper functions for all recombination models
- Generates figures to figures_burst/
- Run: `python burst_enhancement.py --fmt png`

### Figures (in figures_burst/)
- fig1_enhancement_vs_N.png — epsilon vs N (TPA, FCA, total), no recombination model
- fig2_pulse_dynamics.png — H_k vs k comparing: no recomb, surface only, Auger only, combined
- fig3_enhancement_vs_fluence.png — epsilon vs F_p showing Auger suppression at high fluence

**Note**: Fig 1 uses no-recombination model. Needs updating once direction is decided.
Fig 2 and Fig 3 are exploratory/diagnostic, not publication-ready.

### main.tex changes
- Parameter table rewritten (compact, no acoustic, added laser params)
- Rewrite plan for Section 3 added as comments (line ~132)
- eta_fc removed from table and text
- Existing theory/results NOT modified (waiting for direction decision)

### MATLAB code
- feature/fca-heating branch has FCA implementation in run_pa_sim.m
- exp_011 configured for Si NP FCA study
- Not relevant anymore if going analytical-only

## What to discuss with professors
1. The Auger finding: FCA accumulation is limited, ~4x boost not ~670x
2. Whether TPA scaling alone (10^5) is sufficient as the main contribution
3. Whether to include Mie resonance angle
4. How deep to go on carrier dynamics vs keeping it an optics paper
5. Journal fit: Optics Express wants optics, not solid-state physics
