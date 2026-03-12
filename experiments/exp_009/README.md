# exp_009 — TPA-PAM Feasibility Limits (Ballistic Regime)

## Objective

Determine the achievable operating space for two-photon absorption
photoacoustic microscopy (TPA-PAM) under realistic ballistic-photon
attenuation. For each combination of imaging depth, pulse configuration,
and absorber strength, the experiment evaluates whether:

1. The photoacoustic signal is detectable at the tissue surface.
2. The required surface pulse energy and fluence are physically deliverable
   without exceeding tissue damage thresholds.

## Methodology

### Light transport model

The simulation uses a **ballistic-photon attenuation model**. Only
unscattered photons contribute to the diffraction-limited focus. The
intensity at depth *d* follows Beer–Lambert attenuation with the **full**
(not reduced) scattering coefficient:

$$
I(d) = I_0 \exp\!\bigl(-\mu_t \, d\bigr), \qquad \mu_t = \mu_a + \mu_s
$$

The **ballistic transmission** to the focal plane is:

$$
T_{\text{bal}} = \exp\!\bigl(-\mu_t \, d\bigr)
$$

This is the fraction of surface photons that reach the focus without
scattering. All scattered photons are treated as lost from the focused
beam; their contribution to a diffuse background is not modelled in this
experiment.

### Energy budget

The simulation specifies a target **fluence at focus** (J/cm²). From this
the engine computes the per-pulse energy and fluence required at the tissue
surface:

| Quantity | Definition |
|----------|-----------|
| $A_{\text{focus}} = \pi w_0^2 / 2$ | 1/e² Gaussian beam area at focus |
| $E_{\text{focus}} = F_{\text{focus}} \times A_{\text{focus}}$ | Pulse energy at the focal plane |
| $E_{\text{surface}} = E_{\text{focus}} \;/\; T_{\text{bal}}$ | Pulse energy at the tissue surface |
| $A_{\text{surface}} = \pi w_{\text{surface}}^2 / 2$ | Beam area at the tissue surface |
| $F_{\text{surface}} = E_{\text{surface}} \;/\; A_{\text{surface}}$ | Fluence at the tissue surface |

For burst mode the above quantities are **per pulse**. Total burst energy
is $N \times E_{\text{surface}}$.

### Energy deposition

At the focal plane, the absorbed energy density is:

$$
Q = N \bigl(\mu_a \, I + \alpha_2 \, I^2 + \alpha_3 \, I^3\bigr) \tau
$$

where *N* is the number of pulses in a burst (1 for single-pulse modes),
*I* is the peak intensity at focus, and $\tau$ is the single-pulse
duration. The initial pressure is $p_0 = \Gamma \, Q$.

### Acoustic propagation

The initial pressure distribution is propagated using the k-Wave 2D
acoustic solver. A linear sensor array at the tissue surface (z = 0)
records the photoacoustic waveform. The peak detected pressure is reported
as the signal metric.

## Tissue model

**Native porcine liver** at 1070 nm (Ritz et al.):

| Property | Value | Unit |
|----------|-------|------|
| $\mu_a$ | 18 | m⁻¹ |
| $\mu_s$ (full) | 4340 | m⁻¹ |
| $\mu_t$ | 4358 | m⁻¹ |

These are the full (not reduced) optical coefficients. The reduced
scattering coefficient $\mu_s' = \mu_s(1-g) \approx 434\;\text{m}^{-1}$
(assuming $g \approx 0.9$) is not used in the ballistic model but is noted
for future diffusion-based work.

## Contrast agent

BODIPY-TR at three effective concentrations, modelled via the two-photon
absorption coefficient $\alpha_2$:

| Label | $\alpha_2$ (m/W) | Approximate equivalent |
|-------|------------------|----------------------|
| low   | 9 × 10⁻¹⁴ | ~1 mM BODIPY-TR (~28 GM) |
| mid   | 9 × 10⁻¹³ | ~10 mM or higher-σ₂ agent |
| high  | 9 × 10⁻¹² | Engineered high-σ₂ TPA dye |

No linear absorption at the excitation wavelength ($\mu_{a,\text{target}}
= 0$) for TPA contrast agents at 1064 nm.

## Parameter sweep

| Axis | Values | Count |
|------|--------|-------|
| Depth | 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0 mm | 7 |
| Pulse type | NS, FS, burst N = 10, 50, 100, 500, 1000 | 7 |
| $\alpha_2$ | 9e-14, 9e-13, 9e-12 m/W | 3 |

**Total: 7 × 7 × 3 = 147 scenarios**

### Pulse configurations

| Tag | Type | Duration | Fluence at focus | Burst N | Burst window |
|-----|------|----------|-----------------|---------|-------------|
| ns  | Nanosecond | 1 ns | 1.0 J/cm² | 1 | — |
| fs  | Femtosecond | 100 fs | 0.1 J/cm² | 1 | — |
| b0010 | Burst | 100 fs | 0.1 J/cm²/pulse | 10 | 1 ns |
| b0050 | Burst | 100 fs | 0.1 J/cm²/pulse | 50 | 1 ns |
| b0100 | Burst | 100 fs | 0.1 J/cm²/pulse | 100 | 1 ns |
| b0500 | Burst | 100 fs | 0.1 J/cm²/pulse | 500 | 1 ns |
| b1000 | Burst | 100 fs | 0.1 J/cm²/pulse | 1000 | 1 ns |

### Fixed parameters

| Parameter | Value |
|-----------|-------|
| λ | 1064 nm |
| NA | 0.50 |
| n | 1.33 |
| Target radius | 5 µm |
| Γ (Grüneisen) | 0.12 |
| c_sound | 1500 m/s |
| ρ | 1000 kg/m³ |
| α_coeff | 0.75 dB/MHz^y/cm |
| α_power | 1.5 |
| f_grid | 50 MHz |
| PPW_acoustic | 10 |
| n_elements | 128 |
| SNR | 40 dB |

## Outputs

### Per-scenario quantities
- Peak PA pressure at sensor surface (Pa)
- Ballistic transmission $T_{\text{bal}}$
- Surface pulse energy $E_{\text{surface}}$ (J)
- Surface fluence $F_{\text{surface}}$ (J/cm²)

### Figures
1. Peak pressure vs depth — per pulse type, panelled by α₂
2. Surface energy vs depth — per pulse type, with laser capability lines
3. Surface fluence vs depth — with fs damage threshold line
4. Feasibility heatmap — depth × burst N, hatched where F_surface exceeds
   damage threshold

## References

- Ritz et al. — Optical properties of native porcine liver (tissue model)
- Jacques, Phys. Med. Biol. 58, R37 (2013) — Tissue optical properties review
- Wang & Wu, Biomedical Optics (Wiley, 2007) — Beer–Lambert and diffusion theory
