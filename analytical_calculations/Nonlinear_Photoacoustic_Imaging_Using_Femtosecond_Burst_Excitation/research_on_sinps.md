# Nonlinear optical properties of silicon nanoparticles at 1064 nm

**Silicon-based nanoparticles span five orders of magnitude in free-carrier lifetime and offer dramatically different nonlinear absorption profiles at the Nd:YAG fundamental wavelength, making material selection the single most consequential design choice for nonlinear photoacoustic contrast agents.** At 1064 nm (ℏω = 1.165 eV), bulk silicon sits just above its indirect bandgap (1.12 eV), creating a regime where linear absorption is weak (~10 cm⁻¹), two-photon absorption is phonon-assisted and moderate (β ≈ 1.5–2.0 cm/GW), and free-carrier absorption rapidly dominates under pulsed excitation. Nanostructuring silicon fundamentally alters these dynamics: quantum confinement widens the bandgap and eliminates linear absorption in small nanocrystals, while Mie resonances in larger nanoparticles enhance local fields and effective nonlinear cross-sections by up to ~80×. The carrier lifetime — critical for determining whether free-carrier absorption accumulates during a laser pulse — ranges from ~1 ps in amorphous Si to milliseconds in bulk crystalline Si, with profound implications for photoacoustic signal generation.

This report compiles experimentally measured nonlinear optical parameters for nine categories of silicon-based nanoparticles, organized for direct comparison and suitable for conversion into a publication-quality table. All values are at or near 1064 nm unless otherwise noted; data gaps are explicitly identified.

---

## Bulk crystalline silicon establishes the baseline

Bulk crystalline silicon (c-Si) at 1064 nm provides the reference framework against which all nanoparticle properties must be compared. The photon energy (1.165 eV) barely exceeds the **indirect bandgap of 1.12 eV**, resulting in weak phonon-assisted linear absorption. The direct bandgap at the Γ-point is 3.4 eV, far above the single- or two-photon energy but accessible via three-photon absorption (3ℏω = 3.50 eV).

The seminal measurement by **Boggess et al. (IEEE J. Quantum Electron. QE-22, 360, 1986)** simultaneously determined the TPA coefficient **β = 1.5 cm/GW** and the free-carrier absorption cross-section **σ_fc = 5 × 10⁻¹⁸ cm²** at 1064 nm using 4–100 ps pulses. This was the first observation of TPA of 1 μm radiation in single-crystal Si at room temperature, in a regime where stepwise linear-plus-FCA absorption usually dominates. The TPA coefficient was later confirmed and refined by Bristow, Rotenberg, and van Driel (Appl. Phys. Lett. 90, 191104, 2007), who measured **β ≈ 2 ± 0.5 cm/GW** near the indirect gap peak using 200 fs pulses over 850–2200 nm.

The nonlinear refractive index of bulk Si near 1064 nm requires careful interpretation. The intrinsic (bound-electronic) Kerr **n₂ ≈ 4.5 × 10⁻¹⁴ cm²/W** at 1550 nm (widely cited in silicon photonics literature), with dispersion data from Bristow et al. suggesting **n₂ ≈ 3–6 × 10⁻¹⁴ cm²/W** near 1064 nm. However, Boggess et al. (Opt. Commun. 64, 387, 1987) demonstrated that at 1 μm with 25 ps pulses, the nonlinear refraction is **dominated by free-carrier (Drude) effects**, producing self-defocusing ~60× larger than CS₂ at 2.25 GW/cm². This cumulative, carrier-density-dependent effect overwhelms the instantaneous Kerr n₂ under typical pulsed conditions.

The free-carrier lifetime in bulk Si spans an enormous range depending on purity, doping, and injection level: **70–500 μs** for Czochralski/float-zone wafers at low injection (SRH-limited), down to **~5 ns at N = 10¹⁹ cm⁻³** where Auger recombination dominates (Auger coefficient C ≈ 2 × 10⁻³⁰ cm⁶/s). The linear absorption coefficient at 1064 nm is **α ≈ 10–13 cm⁻¹** at 300 K (Jellison & Lowndes, 1982; Green, 2008), highly temperature-sensitive. The refractive index is **n = 3.56** (Green & Keevers, Prog. Photovoltaics 3, 189, 1995). Surface damage threshold for nanosecond pulses is approximately **3–6 J/cm²**.

A notable finding from a recent Physical Review B study is that **three-photon absorption dominates indirect two-photon absorption for photon energies below the direct two-photon absorption edge at 1.7 eV** — which is the case at 1064 nm (1.165 eV). Since 3ℏω = 3.50 eV exceeds the direct gap (3.4 eV), three-photon-to-direct-gap transitions are allowed without phonon assistance. This may be significant at high intensities where single-photon absorption is weak.

### Bulk c-Si parameter table (1064 nm, 300 K)

| Parameter | Value | Reference |
|-----------|-------|-----------|
| Indirect bandgap E_g | 1.12 eV | Standard |
| Direct bandgap E_g,dir | 3.4 eV | Standard |
| Refractive index n | 3.56 | Green & Keevers 1995 |
| Linear absorption α | 10–13 cm⁻¹ | Jellison & Lowndes 1982; Green 2008 |
| TPA coefficient β | **1.5 cm/GW** | Boggess et al. 1986 |
| TPA coefficient β | **2 ± 0.5 cm/GW** | Bristow et al. 2007 (200 fs) |
| FCA cross-section σ_fc | **5 × 10⁻¹⁸ cm²** | Boggess et al. 1986 |
| Nonlinear refractive index n₂ (Kerr) | ~(3–6) × 10⁻¹⁴ cm²/W | Bristow et al. 2007 (estimated from dispersion) |
| Free-carrier lifetime τ_c (low injection) | 70 μs (CZ); up to 32 ms (FZ) | Multiple sources |
| Auger coefficient C | ~2 × 10⁻³⁰ cm⁶/s | Literature consensus |
| Surface damage threshold (ns) | ~3–6 J/cm² | Literature |

---

## Mie-resonant crystalline Si nanoparticles show ultrafast carrier relaxation

Crystalline silicon nanoparticles in the 100–250 nm diameter range support geometric (Mie) resonances that dramatically enhance local electromagnetic fields at specific wavelengths. These resonances — magnetic dipole, electric dipole, and higher-order modes — boost effective nonlinear absorption cross-sections by up to **~80×** over unstructured material (Shcherbakov et al., Nano Lett. 15, 6985, 2015, measured on a-Si nanodisks at magnetic dipole resonance). No quantum confinement effects exist at these sizes (Bohr exciton radius of Si ≈ 4.3 nm), so the intrinsic material parameters match bulk values.

The most critical finding for photoacoustic applications is the carrier lifetime. Baranov et al. (ACS Photonics 3, 1546, 2016) measured **τ_c ≈ 2.5 ps** in ~200 nm nanocrystalline (polycrystalline) Si nanoparticles using femtosecond pump-probe spectroscopy near the magnetic dipole resonance. This ultrafast relaxation arises from rapid surface and grain-boundary recombination in the polycrystalline grain structure (~10–30 nm grain sizes, confirmed by Raman and HRTEM). By contrast, single-crystal Si nanowires of ~250 nm diameter show **τ_c ≈ 300–500 ps** due to surface recombination (SRV ~10⁴ cm/s) without grain boundary contributions (Grumstrup et al., J. Phys. Chem. C 118, 8634, 2014; Li et al., Nano Lett. 23, 1445, 2023). Extreme ultraviolet transient absorption spectroscopy on polycrystalline Si nanoparticles resolved carrier-phonon scattering at **870 ± 40 fs** and phonon-phonon relaxation at **17.5 ± 0.3 ps**, both significantly longer than single-crystal values (~195 fs and ~8 ps, respectively), attributed to grain boundary effects.

These nanoparticles are fabricated by laser printing, laser ablation in liquid, or chemical vapor deposition. The native SiO₂ shell (1–3 nm) provides surface passivation. Biocompatibility is excellent — silicon degrades to non-toxic orthosilicic acid Si(OH)₄, and multiple in vivo studies confirm safety (Kabashin et al., ACS Nano 13, 9841, 2019). Photoluminescence quantum yield is very low due to the indirect bandgap. Rudenko, Han, and Moloney (Adv. Opt. Mater. 11, 2201654, 2023) modeled the trade-off between nonlinear efficiency and damage in these particles.

### c-Si NPs (100–250 nm) parameter table

| Parameter | Value | Reference |
|-----------|-------|-----------|
| Size range | 100–250 nm | Multiple groups |
| Crystallinity | Nanocrystalline (10–30 nm grains) | Makarov et al. 2017 |
| E_g | 1.12 eV (same as bulk) | — |
| n | ~3.55 at 1064 nm | Green & Keevers 1995 |
| α (intrinsic) | ~10 cm⁻¹ | Bulk value; Mie cross-sections dominate |
| β (intrinsic) | 1.5–2.0 cm/GW | Bulk value; Mie enhancement up to ~80× |
| σ_fc | ~5 × 10⁻¹⁸ cm² | Bulk value |
| **τ_c (nanocrystalline)** | **~2.5 ps** | Baranov et al., ACS Photonics 2016 (pump-probe, RT) |
| τ_c (single-crystal NW) | ~300–500 ps | Grumstrup et al. 2014; Li et al. 2023 |
| n₂ (Kerr) | ~4.5 × 10⁻¹⁴ cm²/W | Bulk value |
| Damage threshold (fs) | ~0.1–1 mJ/cm² | Makarov group |
| PLQY | Very low | Indirect bandgap |
| Biocompatibility | Excellent; degrades to Si(OH)₄ | Kabashin et al. 2019 |

---

## Silicon nanocrystals trade linear absorption for quantum-tunable bandgaps

Silicon nanocrystals (SiNCs) in the 1–10 nm range exhibit strong quantum confinement, opening the bandgap from bulk 1.12 eV to **~2.0–2.4 eV at 2 nm** diameter. This has profound consequences at 1064 nm: for SiNCs smaller than ~5–6 nm, E_g exceeds the photon energy (1.165 eV), completely eliminating linear absorption and making **two-photon absorption the only pathway** for energy deposition. For SiNCs of 7–10 nm, the bandgap approaches the bulk value and weak linear absorption returns.

The TPA cross-sections of colloidal SiNCs were measured by Furey et al. (phys. stat. sol. (b) 255, 1700501, 2018; and ACS Nano 16, 6023, 2022) using two-photon-excited photoluminescence. For dodecyl-capped SiNCs in toluene at 810 nm excitation: **σ₂ = 0.28 GM (2.0 nm), 1.25 GM (2.6 nm), and 18 GM (5.1 nm)**, showing a steep size dependence scaling roughly as d⁵ to d⁶. These values are notably low compared to CdSe QDs (~10³–10⁴ GM), reflecting silicon's indirect bandgap. He et al. (Nano Lett. 8, 2688, 2008) measured both two-photon (650–900 nm) and three-photon (1150–1400 nm) absorption spectra for Si QDs, confirming that 3PA is accessible near 1064 nm.

The FCA cross-section in Si nanocrystals is **~7× larger than bulk Si**, as measured by Kekatpure and Brongersma (Nano Lett. 8, 3787, 2008) using whispering gallery mode broadening in the 700–900 nm range. The cross-section follows an approximately **quadratic wavelength dependence (σ_fc ∝ λ²)**, consistent with Drude theory. Scaling from their 1540 nm measurement of **σ_fc = (3.6 ± 1.4) × 10⁻¹⁷ cm²** (Kekatpure & Brongersma, Opt. Lett. 34, 3397, 2009), the estimated value at 1064 nm is **~1.7 × 10⁻¹⁷ cm²**.

Carrier lifetimes in SiNCs span a vast range depending on excitation regime. The **single-exciton radiative lifetime** is ~50–300 μs at room temperature (stretched-exponential decay, β ≈ 0.8), reflecting silicon's indirect bandgap (Sangghaleh et al., ACS Nano 9, 7097, 2015; Carroll & Limpens et al., J. Phys. Chem. C 125, 2021). Under multiphoton excitation relevant to photoacoustics, **biexciton Auger recombination** dominates with a universal volume-scaling law established by Robel et al. (Phys. Rev. Lett. 102, 177404, 2009): **τ_XX = γ·V**, where γ ≈ 1 ps/nm³. This gives approximate biexciton Auger lifetimes of **~14 ps (3 nm), ~65 ps (5 nm), ~270 ps (8 nm), and ~520 ps (10 nm)**. Limpens et al. (J. Phys. Chem. C 122, 5525, 2018) measured **τ_XX ≈ 28 ps** for intrinsic 4.5 nm Si NCs in SiO₂ by transient induced absorption, consistent with the universal scaling. Trojánek et al. (Phys. Rev. B 72, 075365, 2005) reported **105 ps** (532 nm pump, quadratic dependence indicating Auger) and **1100 ps** (266 nm pump) for ion-implanted Si NCs.

Beard et al. (Nano Lett. 7, 2506, 2007) demonstrated **multiple exciton generation (MEG)** in 9.5 nm colloidal Si NCs (E_g = 1.20 eV), with an MEG threshold of **2.4 ± 0.1 E_g** and a quantum yield of **2.6 ± 0.2 excitons per photon at 3.4 E_g** — the first report of MEG in an indirect-gap semiconductor. Trinh et al. (Nature Photon. 6, 316, 2012) later demonstrated a novel "space-separated quantum cutting" mechanism in closely-spaced Si NCs embedded in SiO₂, where a single photon generates excitons in **adjacent nanocrystals simultaneously**, with an onset near **2E_g** (the energy conservation limit). Photoluminescence quantum yields of properly passivated colloidal SiNCs reach **30–70%** (alkyl-capped, Hessel et al., Chem. Mater. 24, 393, 2012; Pringle et al., ACS Nano 14, 3858, 2020).

### SiNCs (1–10 nm) parameter table

| Parameter | Value | Reference |
|-----------|-------|-----------|
| Size range | 1–10 nm | — |
| E_g (size-dependent) | 2.0–2.4 eV (2 nm); 1.5–1.6 eV (4 nm); ~1.2 eV (8 nm) | Multiple sources |
| TPA cross-section σ₂ | 0.28 GM (2 nm); 1.25 GM (2.6 nm); 18 GM (5.1 nm) at 810 nm | Furey et al. 2018, 2022 |
| σ_fc | **~7× bulk; ~1.7 × 10⁻¹⁷ cm²** (est. at 1064 nm) | Kekatpure & Brongersma 2008, 2009 |
| **τ_c (biexciton Auger)** | **~14 ps (3 nm) to ~520 ps (10 nm)**; τ_XX ∝ V | Robel et al. 2009; Limpens et al. 2018 |
| τ_c (single exciton, radiative) | 50–300 μs | Sangghaleh et al. 2015 |
| τ_c (He et al. TRPL) | 0.75 ns / 300 ns / 5 μs (multiexponential) | He et al. 2008 |
| n₂ | Not directly measured at 1064 nm for colloidal NCs | — |
| PLQY | 30–70% (alkyl-capped) | Jurbergs et al. 2006; Hessel et al. 2012 |
| Biocompatibility | Excellent; degrades to Si(OH)₄ | Dasog et al. 2016 |

---

## Amorphous silicon nanoparticles offer the fastest carrier trapping

Amorphous silicon (a-Si) nanoparticles present a fundamentally different optical landscape at 1064 nm. The Tauc bandgap of hydrogenated amorphous silicon (a-Si:H) is **1.6–1.85 eV** (commonly ~1.7 eV), placing 1064 nm photons (1.165 eV) firmly **below the bandgap**. This renders a-Si:H nominally transparent, with residual linear absorption of only **~1 cm⁻¹** due to defect-related sub-gap states (Urbach tail). However, two-photon absorption is vigorous since 2ℏω = 2.33 eV substantially exceeds E_g.

At telecom wavelengths (~1550 nm), a-Si:H exhibits **β ≈ 0.5–0.7 cm/GW** (Mehta & Peacock et al., Sci. Rep. 2013; Grillet et al., Opt. Express 20, 22609, 2012), though some optimized samples show negligible TPA (Gai et al., Opt. Express 22, 9948, 2014). At 1064 nm, β is expected to be substantially higher because 2ℏω/E_g is larger. The nonlinear refractive index is a standout feature: **n₂ ≈ 1.7–4.2 × 10⁻¹³ cm²/W** at 1550 nm (Hemsley et al., Sci. Rep. 6, 38908, 2016; Peacock group), which is **2–5× larger than crystalline Si**. The nonlinear figure of merit (FOM = n₂/λβ) reaches **~1.6–2+**, far superior to c-Si (FOM ~0.3).

The defining advantage of a-Si for photoacoustic applications is the **ultrafast carrier trapping**. Fauchet and Hulin (JOSA B 6, 1024, 1989) measured recovery times of **~1 ps and ~10 ps** using femtosecond pump-probe on a-Si:H thin films. Esser et al. (Phys. Rev. B 41, 2879, 1990) found that quadratic (bimolecular) recombination dominates on the picosecond timescale above carrier densities of 5 × 10¹⁸ cm⁻³ in a-Si:H. For fully amorphized (non-hydrogenated) silicon, carrier lifetimes as short as **~0.6 ps** have been reported. Shcherbakov et al. (Nano Lett. 15, 6985, 2015) demonstrated **65 fs TPA-governed ultrafast switching** in a-Si nanodisks at Mie resonance, with free-carrier effects persisting on longer (ps) timescales. Della Valle et al. (ACS Photonics 4, 2129, 2017) showed full return to zero in **~20 ps** for a-Si nanobrick metasurfaces.

The refractive index of a-Si:H is **n ≈ 3.5–3.7** in the near-IR, slightly higher than c-Si. Mid-gap defect states in some a-Si:H samples can cause single-photon absorption (SPA) that competes with or exceeds TPA, introducing sample-to-sample variability. Biocompatibility data for a-Si NPs specifically is limited compared to crystalline variants.

### a-Si NPs parameter table

| Parameter | Value | Reference |
|-----------|-------|-----------|
| Size range (Mie-resonant) | 100–300 nm | Multiple groups |
| E_g (Tauc, a-Si:H) | **1.6–1.85 eV** | Literature consensus |
| n | 3.5–3.7 | Standard |
| α at 1064 nm | ~1 cm⁻¹ (sub-gap) | Bülbül et al. |
| β at 1550 nm | 0.5–0.7 cm/GW | Mehta/Peacock 2013; Grillet et al. 2012 |
| β at 1064 nm | Not directly measured; expected > 1 cm/GW | — |
| n₂ at 1550 nm | **1.7–4.2 × 10⁻¹³ cm²/W** | Hemsley et al. 2016; Peacock group |
| **τ_c** | **~1–10 ps** (trapping-dominated) | Fauchet & Hulin 1989; Esser et al. 1990 |
| τ_c (amorphized Si) | ~0.6 ps | Radiation-damage studies |
| σ_fc | Not reported for a-Si NPs at 1064 nm | — |
| Damage threshold | Not specifically reported for NPs at 1064 nm | — |
| PLQY | Very low (~10⁻⁷ for bulk a-Si) | — |
| Biocompatibility | Limited data; expected similar to c-Si | — |

---

## Porous silicon bridges nonlinear optics and biodegradable drug delivery

Porous silicon nanoparticles (pSi NPs), typically 100–300 nm in diameter with tunable porosity of **46–80%+** and pore sizes of 2–50 nm, represent a composite nanostructure: a skeleton of Si nanocrystallites (1–10 nm) separated by pores. This creates effective-medium optical properties strongly dependent on porosity. The effective refractive index ranges from **n_eff ≈ 2.5–2.8** (low porosity, ~30%) to **n_eff ≈ 1.3–1.6** (high porosity, ~80%), calculated via Bruggeman or Maxwell-Garnett models. The effective bandgap reflects the nanocrystallite size distribution: from bulk-like **1.12 eV** for large crystallites to **2.0–3.2 eV** for quantum-confined domains <3 nm.

Nonlinear optical measurements on porous Si at telecom wavelengths show TPA comparable to bulk crystalline Si despite high porosity: **β ≈ 0.5–0.8 cm/GW at 1550 nm** for 70% porosity waveguides (Apiratikul & Murphy, Opt. Express 17, 3396, 2009). At 800 nm (closer to 1064 nm), Z-scan measurements yielded **β ≈ 1.0 ± 0.3 cm/GW**, slightly suppressed versus bulk c-Si β = 2.9 cm/GW at the same wavelength (MDPI Appl. Sci. 8, 1810, 2018). The nonlinear refractive index shows an intriguing sign change: **n₂ = (2.3 ± 0.7) × 10⁻¹⁴ cm²/W** (positive) at 1550 nm but **n₂ = −9 × 10⁻¹⁴ cm²/W** (negative, self-defocusing, enhanced ~13× over c-Si) at 800 nm, attributed to quantum confinement effects. Free-carrier effects in porous Si waveguides are **significantly faster and stronger** than in bulk c-Si.

Carrier dynamics show a characteristic two-component decay. Malý, Trojánek et al. (Phys. Rev. B 54, 7929, 1996) measured a fast component of **~100 ps** (bimolecular recombination of free carriers in nanocrystallite cores) and a slow component of **~100 μs** (recombination of trapped carriers) using picosecond pump-probe and time-resolved PL at 532 nm excitation. Kaplan et al. (Sci. Rep. 8, 17526, 2018) reported **τ_c ≈ 375 ps** for porous Si membranes (~50% porosity) using interferometric pump-probe, attributing the lifetime to SRH recombination.

The biomedical appeal of pSi NPs is exceptional. Park et al. (Nature Mater. 8, 331, 2009) demonstrated that luminescent pSi NPs (LPSiNPs) are **biodegradable**, dissolving in PBS at physiological temperature to produce renally-clearable orthosilicic acid Si(OH)₄. PL quantum yield reaches **up to 65%** for the S-band (red-green emission, μs decay). Black porous silicon (BPSi) NPs exhibit broadband absorption with photothermal conversion efficiency of **48.6% at 1064 nm** — among the highest for semiconductor nanoparticles (Biomaterials, 2017). PEGylated BPSi NPs show no cytotoxicity up to 0.5 mg/mL and produce stronger photoacoustic contrast than Au NPs at equivalent concentrations. Porous Si can also encapsulate molecular agents: Ca-pSiNP loaded with indocyanine green (ICG) achieves a **17-fold photoacoustic signal enhancement** over free ICG (Sailor group).

### pSi NPs parameter table

| Parameter | Value | Reference |
|-----------|-------|-----------|
| Particle diameter | 100–300 nm; pore sizes 2–50 nm | Park et al. 2009; multiple groups |
| Porosity | 46–80%+ | Tunable |
| Nanocrystallite size | 1–10 nm within skeleton | — |
| E_g (effective) | 1.12–3.2 eV | Porosity/size-dependent |
| n_eff | 1.3–2.8 (porosity-dependent) | Effective medium models |
| β at 1550 nm | **0.5–0.8 cm/GW** (70% porosity) | Apiratikul & Murphy 2009 |
| β at 800 nm | ~1.0 ± 0.3 cm/GW | MDPI 2018 Z-scan |
| n₂ at 1550 nm | (2.3 ± 0.7) × 10⁻¹⁴ cm²/W | Apiratikul & Murphy 2009 |
| n₂ at 800 nm | −9 × 10⁻¹⁴ cm²/W (self-defocusing) | MDPI 2018 |
| **τ_c (fast)** | **~100 ps** (bimolecular in NC cores) | Malý et al. 1996 (pump-probe, 532 nm, RT) |
| τ_c (slow) | ~100 μs (trapped carriers) | Malý et al. 1996 |
| τ_c (SRH, membrane) | ~375 ps | Kaplan et al. 2018 |
| PLQY (S-band) | Up to 65% | Canham review; Park et al. 2009 |
| Photothermal efficiency (1064 nm) | **48.6%** (BPSi) | Biomaterials 2017 |
| Biocompatibility | **Excellent; biodegradable** | Park et al. 2009 |

---

## Core-shell, functionalized, and other Si nanostructures modify surface-controlled dynamics

**Si/SiO₂ core-shell nanoparticles** embed silicon nanocrystals in an amorphous SiO₂ matrix, either as individual core-shell particles or as Si NC/SiO₂ superlattices. The oxide interface creates trap states that significantly alter carrier dynamics. Ultrafast transient transmission measurements on 4 nm Si NCs in SiO₂ show an **~11 ps decay component** attributed to quantized-level relaxation, with surface-related states enhancing carrier relaxation and inhibiting Auger recombination (Nanoscale Research Letters, 2008). The FCA cross-section remains **~7× larger than bulk Si** with quadratic wavelength scaling (Kekatpure & Brongersma, Nano Lett. 2008). PL lifetimes are long (25–100 μs for radiative decay). Remarkably, a Si/SiO₂ cuboid supporting a quasi-bound state in the continuum achieved **quantum efficiency enhancement of 6 orders of magnitude to ~13%** via femtosecond two-photon excitation (Nature Communications 2022). Doping modifications matter: P-B co-doped Si NCs in SiO₂ show Auger lifetimes of **~140 ps**, roughly 5× longer than intrinsic NCs (~28 ps) at the same 4.5 nm size (Limpens et al. 2018).

**Surface-functionalized Si nanoparticles** demonstrate that surface chemistry profoundly affects nonlinear optical performance. Alkyl-capped (dodecene) SiNCs achieve the highest PLQY (**30–45%**, Hessel et al. 2012) and show standard Auger volume scaling. Thiolate-capped SiNCs exhibit **slower biexciton Auger recombination** than alkyl-capped counterparts due to hole trapping at thiolate surface states (Carroll & Limpens et al., J. Phys. Chem. C 125, 2021), measured by transient absorption, TRPL, and time-resolved terahertz spectroscopy. OH-functionalized SiNCs show a **bandgap red-shift of ~0.22 eV** relative to H-terminated NCs (Bürkle et al., Adv. Funct. Mater. 27, 1701898, 2017). PEG-coated Si NPs maintain colloidal stability and biocompatibility with modest PLQY reduction. For photoacoustic contrast, ball-milled c-Si NPs (~114 nm) functionalized via hydrosilylation with bifunctional ligands showed extinction coefficients **>2 × 10¹⁰ M⁻¹ cm⁻¹** from visible to NIR and were demonstrated in OR-PAM imaging in live zebrafish embryos (Ye et al., ACS Appl. Nano Mater. 2, 7577, 2019).

**Other notable Si nanostructures** include: (1) Hydrogenated amorphous Si nanowires with **n₂ = 1.19 × 10⁻¹³ cm²/W** and essentially zero instantaneous TPA (β = 0.014 cm/GW at 1550 nm), yielding a nonlinear FOM of **5.5** (Carletti et al. 2014; Wathen et al. 2014); (2) Strained Si nanoparticles where compressive lattice strain decreases β and increases n₂ in a Z-scan-measurable manner (Dhara et al., Opt. Lett. 39, 3833, 2014); (3) SiC nanoparticles (620 nm) exhibiting both PL and PA signals for cell tracking >20 days (Chen et al., Nanoscale 2021); and (4) Black hollow SiOₓ NPs with a photothermal conversion efficiency of **48.6% at 1064 nm** specifically (Biomaterials, 2017).

---

## Comprehensive cross-material comparison at 1064 nm

The following master table consolidates all parameters for direct comparison. Values are at 1064 nm unless noted; entries marked "NR" indicate the parameter was not reported in the literature surveyed.

| Parameter | Bulk c-Si | c-Si NPs (100–250 nm) | SiNCs (3–5 nm) | SiNCs (8–10 nm) | a-Si(:H) NPs | pSi NPs (~70% porosity) | Si/SiO₂ core-shell | Si QDs (<3 nm) |
|---|---|---|---|---|---|---|---|---|
| **E_g (eV)** | 1.12 (ind.) | 1.12 | 1.5–1.8 | 1.12–1.3 | 1.6–1.85 (Tauc) | 1.12–3.2 (eff.) | 1.12–1.8 (NC size-dep.) | 1.8–2.4 |
| **n at 1064 nm** | 3.56 | 3.55 | ~3.5 (particle) | ~3.5 | 3.5–3.7 | 1.3–2.8 (eff.) | NC in SiO₂ matrix | ~3.5 (particle) |
| **α at 1064 nm (cm⁻¹)** | 10–13 | ~10 (intrinsic) | ~0 (below gap) | Weak | ~1 (sub-gap) | Varies widely | NC-dependent | ~0 (below gap) |
| **β (cm/GW)** | 1.5–2.0 | 1.5–2.0 (Mie-enhanced ×80) | σ₂ = 1–18 GM (810 nm) | Approaching bulk | 0.5–0.7 (1550 nm) | 0.5–1.0 (1550/800 nm) | NR at 1064 nm | σ₂ = 0.28 GM (810 nm) |
| **σ_fc (cm²)** | 5 × 10⁻¹⁸ | ~5 × 10⁻¹⁸ | ~1.7 × 10⁻¹⁷ (est.) | ~1.7 × 10⁻¹⁷ (est.) | NR | Enhanced vs bulk | ~7× bulk | NR |
| **τ_c (fast)** | 70 μs–32 ms (low inj.) | **2.5 ps** (polycryst.) | **10–100 ps** (Auger) | **270–520 ps** (Auger) | **1–10 ps** (trapping) | **~100 ps** (bimolec.) | ~11 ps (relaxation) | **~few ps** (Auger) |
| **τ_c method** | μ-PCD, QSSPC | Pump-probe (fs) | TA (fs) | TA (fs) | Pump-probe (fs) | Pump-probe (ps) | TA (fs) | TA/TRPL |
| **n₂ (cm²/W)** | (3–6) × 10⁻¹⁴ | ~4.5 × 10⁻¹⁴ | NR at 1064 nm | NR | (1.7–4.2) × 10⁻¹³ (1550 nm) | (2.3–9) × 10⁻¹⁴ | NR | NR |
| **PLQY** | N/A | Very low | 30–70% | Very low | Very low | Up to 65% | Long-lived PL | 10–45% |
| **Biocompatibility** | N/A | Excellent | Excellent | Excellent | Limited data | **Biodegradable** | Good | Excellent |
| **Surface passivation** | N/A | Native SiO₂ | Alkyl, H, oxide | Alkyl, H, oxide | Si-H (a-Si:H) | Si-H, Si-Ox, PEG | SiO₂ shell | Various |

---

## What the data reveals for nonlinear photoacoustic contrast agent design

The compiled data points to several non-obvious conclusions for selecting a Si-based nonlinear photoacoustic contrast agent at 1064 nm.

**Carrier lifetime governs the nonlinear absorption mechanism.** At 1064 nm with nanosecond pulses (typical Nd:YAG), free carriers generated by linear or two-photon absorption persist long enough to undergo free-carrier absorption, creating a cascading nonlinear process. The **2.5 ps carrier lifetime** in nanocrystalline Si NPs (Baranov et al. 2016) versus **~100 ps** in porous Si (Malý et al. 1996) versus **microseconds** in bulk Si creates fundamentally different nonlinear heating dynamics. Paradoxically, the ultrashort lifetime in nanocrystalline NPs means carriers recombine before significant FCA accumulates, potentially reducing the net nonlinear absorption — while the longer lifetime in pSi enables greater FCA buildup within a nanosecond pulse.

**The Mie enhancement of local fields is the dominant nonlinear amplification mechanism** for 100–200 nm particles. The ~80× TPA enhancement measured in Mie-resonant a-Si nanodisks (Shcherbakov et al. 2015) converts intrinsic β = 1.5 cm/GW into effective values approaching ~100 cm/GW at magnetic dipole resonance. This geometric resonance effect is independent of quantum confinement and operates for both crystalline and amorphous particles.

**Amorphous Si NPs occupy a unique parameter space**: below-gap transparency (negligible linear absorption) combined with strong TPA (2ℏω >> E_g), very high n₂ (2–5× c-Si), and ultrafast carrier trapping (~1–10 ps). This combination maximizes the intensity-dependent nonlinear contrast while minimizing background linear absorption — ideal for nonlinear photoacoustic imaging where the signal should scale nonlinearly with fluence.

**Porous Si NPs offer the best-documented biomedical pathway** with published in vivo biodegradation data, FDA-related safety classification, and demonstrated photoacoustic contrast superior to Au NPs. Their photothermal conversion efficiency of **48.6% at 1064 nm** (for BPSi) is the highest among semiconductor nanoparticles. The moderate carrier lifetime (~100 ps fast component) enables meaningful FCA accumulation within nanosecond pulses.

**Critical data gaps remain.** No study has directly measured TPA coefficients or three-photon absorption coefficients of any Si nanoparticle type at exactly 1064 nm. The FCA cross-section of nanoparticles at 1064 nm is universally estimated from bulk or telecom-wavelength data rather than directly measured. No paper was found combining nonlinear optical parameter characterization with photoacoustic imaging performance at 1064 nm for Si nanoparticles — this represents a significant opportunity for the field.