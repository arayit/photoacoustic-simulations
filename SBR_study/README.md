# SBR Study

Signal-to-background ratio analysis using the photoacoustic simulation engine.

## Approach

Two simulations are run with identical parameters, differing only in whether the target is present:

- **Run 1** — tissue + target → `p_signal`
- **Run 2** — tissue only (target replaced with tissue properties) → `p_background`

```
SBR = max(p_signal) / max(p_background)   [at target depth]
SBR_dB = 20 · log10(SBR)
```

## Engine

All simulations use `../engine/run_pa_sim.m`.
