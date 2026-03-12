# Thermal Damage & Heat Diffusion — Literature Guide

Context: TPA-heated 5 µm exogenous target (BODIPY-TR) in tissue, burst of 1000 fs pulses
within 1 ns, ΔT ~ 100 K at focus. Need to understand thermal safety, diffusion, and
damage mechanisms.

## Foundational Textbooks

1. **Welch & van Gemert — "Optical-Thermal Response of Laser-Irradiated Tissue"**
   Springer, 2nd ed. 2011.
   The definitive reference. Chapters 10–13 cover the heat equation in tissue,
   analytical solutions for localized sources, the Arrhenius damage integral,
   and thermal damage thresholds.

2. **Niemz — "Laser-Tissue Interactions: Fundamentals and Applications"**
   Springer, 4th ed. 2019.
   More concise and accessible. Chapter 3 (thermal interactions) gives a clear
   walkthrough of thermal confinement, diffusion regimes, and damage mechanisms.

## Thermal Confinement & Diffusion

3. **Anderson & Parrish (1983)** — "Selective Photothermolysis: Precise Microsurgery
   by Selective Absorption of Pulsed Radiation"
   *Science* 220:524–527.
   Foundational paper introducing thermal confinement and selective heating of
   chromophore targets. Derives thermal relaxation time for heated microstructures
   of different geometries. Directly relevant — exogenous absorber in tissue is
   exactly this framework.

4. **Goldenberg & Tranter (1952)** — "Heat flow in an infinite medium heated by a sphere"
   *British J. Applied Physics* 3:296.
   Classic analytical solution for T(r,t) after a uniformly heated sphere in an
   infinite medium. The exact Green's function needed for modeling diffusion from
   the 5 µm target.

## Thermal Damage Models

5. **Vogel & Venugopalan (2003)** — "Mechanisms of Pulsed Laser Ablation of
   Biological Tissues"
   *Chemical Reviews* 103:577–644.
   Covers thermal vs stress vs photochemical confinement, transition from thermal
   damage to ablation, cavitation thresholds, and incubation effects. Sections on
   pulse duration role are directly relevant to burst scenario.

6. **Dewhirst et al. (2003)** — "Basic Principles of Thermal Dosimetry and Thermal
   Thresholds for Tissue Damage from Hyperthermia"
   *Int. J. Hyperthermia* 19:267–294.
   Defines CEM43 thermal dose. Gives threshold values for different tissues.
   Important for understanding when the "5 K rule" applies and when it doesn't.

7. **Pearce (2009)** — "Relationship between Arrhenius models of thermal damage
   and the CEM 43 thermal dose"
   *Proc. SPIE 7181*.
   Bridges the Arrhenius integral with CEM43. Useful for converting transient
   temperature profiles into clinically meaningful damage metrics.

## Nanoparticle/Microparticle Heating (closest to our scenario)

8. **Pustovalov (2005)** — "Theoretical study of heating of spherical nanoparticle
   in media by short laser pulses"
   *Chemical Physics* 308:103–108.
   Analytical model for heating and cooling dynamics of absorbing micro/nanoparticles
   in tissue. Derives T(r,t) for particle and surrounding medium. Very close to
   our geometry.

9. **Pitsillides et al. (2003)** — "Selective cell targeting with light-absorbing
   microparticles and nanoparticles"
   *Biophysical Journal* 84:4023–4032.
   Experimental and theoretical study of cell damage around laser-heated
   microparticles. Measures spatial extent of thermal damage as a function of
   particle size and pulse energy. Directly answers "how far does damage extend
   from a heated microsphere?"

## Cavitation & Mechanical Effects

10. **Paltauf & Dyer (2003)** — "Photomechanical Processes and Effects in Ablation"
    *Chemical Reviews* 103:487–518.
    When ΔT > 100 K, cavitation/phase-explosion regime. Covers bubble dynamics,
    shockwave generation, and mechanical damage thresholds.

## Recommended Reading Order

For our specific situation (TPA-heated 5 µm exogenous target):

1. Anderson & Parrish → thermal confinement concept, relaxation time
2. Niemz Ch.3 → quick overview of all thermal interaction regimes
3. Pustovalov → our exact geometry (heated microsphere in medium)
4. Vogel & Venugopalan → deep dive on damage mechanisms, confinement transitions
5. Pitsillides → experimental validation of damage radius around heated particles
6. Dewhirst + Pearce → quantifying damage thresholds (CEM43, Arrhenius)
