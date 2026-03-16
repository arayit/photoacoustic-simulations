"""Sanity checks for the Lutomirski (1995) temporal broadening implementation."""

import numpy as np
import sys
sys.path.insert(0, ".")
from temporal_broadening import (
    make_params, compute_moments,
    normalized_mean_time, mean_delay_normalized, axial_variance_normalized,
)

p = make_params()
print("=" * 65)
print("SANITY CHECK: Lutomirski (1995) Implementation")
print("=" * 65)

# ---------------------------------------------------------------
# CHECK 1: Derived parameters v, w
# ---------------------------------------------------------------
print("\n--- CHECK 1: Derived parameters ---")
g = p["g"]
v_expected = 1 - g
cos2theta = (1 + 2 * g**2) / 3.0
w_expected = 1.5 * (1 - cos2theta)

print(f"  g = {g}")
print(f"  v = 1 - g = {p['v']}  (expected {v_expected})  OK: {np.isclose(p['v'], v_expected)}")
print(f"  cos2theta = (1+2g^2)/3 = {p['cos2theta']:.6f}  (expected {cos2theta:.6f})  OK: {np.isclose(p['cos2theta'], cos2theta)}")
print(f"  w = 1.5*(1-cos2theta) = {p['w']}  (expected {w_expected})  OK: {np.isclose(p['w'], w_expected)}")
print(f"  c = c0/n = {p['c']:.6e} m/s")
print(f"  ell_s = 1/mu_s = {p['ell_s']*1e6:.1f} um  (expected ~230 um)")
print(f"  sigma_pulse = tau_fwhm/2.355 = {p['sigma_pulse']*1e15:.2f} fs")

# ---------------------------------------------------------------
# CHECK 2: Limiting behaviour as z -> 0
# ---------------------------------------------------------------
print("\n--- CHECK 2: Limiting behaviour z -> 0 ---")
z_tiny = np.array([1e-9])
m_tiny = compute_moments(z_tiny, p)
print(f"  At z = {z_tiny[0]*1e6:.3f} um:")
print(f"    delta_t = {m_tiny['delta_t'][0]*1e15:.4f} fs  (should be ~0)")
print(f"    sigma_t = {m_tiny['sigma_t'][0]*1e15:.4f} fs  (should be ~0)")

# ---------------------------------------------------------------
# CHECK 3: T(z) at small z should be approximately z (ballistic)
# ---------------------------------------------------------------
print("\n--- CHECK 3: T(z) ~ z for small z (ballistic limit) ---")
v = p["v"]
w = p["w"]
z_small = np.array([0.01, 0.1, 0.5])
T_calc = normalized_mean_time(z_small, v)
T_approx = z_small + v * z_small**2 / 2
print(f"  z_norm    T(exact)      T~z+vz^2/2    Rel. error")
for i in range(len(z_small)):
    rel = abs(T_calc[i] - T_approx[i]) / T_calc[i]
    print(f"  {z_small[i]:.2f}       {T_calc[i]:.6f}      {T_approx[i]:.6f}      {rel:.2e}")

# ---------------------------------------------------------------
# CHECK 4: Mean delay DeltaT positive and monotonically growing
# ---------------------------------------------------------------
print("\n--- CHECK 4: Delta_t monotonically increasing ---")
z_phys = np.linspace(1e-6, 3e-3, 1000)
m = compute_moments(z_phys, p)
delta_diff = np.diff(m["delta_t"])
print(f"  delta_t always increasing: {np.all(delta_diff >= 0)}")
print(f"  delta_t always >= 0:       {np.all(m['delta_t'] >= 0)}")

# ---------------------------------------------------------------
# CHECK 5: sigma_t monotonically increasing
# ---------------------------------------------------------------
print("\n--- CHECK 5: sigma_t monotonically increasing ---")
sigma_diff = np.diff(m["sigma_t"])
print(f"  sigma_t always increasing: {np.all(sigma_diff >= 0)}")
print(f"  sigma_t always >= 0:       {np.all(m['sigma_t'] >= 0)}")

# ---------------------------------------------------------------
# CHECK 6: Compare with expected values from MD document
# ---------------------------------------------------------------
print("\n--- CHECK 6: Compare with MD expected values ---")
print("  MD states: at 500 um, sigma_t ~ 0.5 ps, delta_t ~ 0.2 ps")
sig_500 = np.interp(500e-6, z_phys, m["sigma_t"]) * 1e12
dt_500 = np.interp(500e-6, z_phys, m["delta_t"]) * 1e12
print(f"  Computed:  sigma_t = {sig_500:.3f} ps  delta_t = {dt_500:.3f} ps")
print(f"  Match:     sigma_t ~ 0.5 ps: {abs(sig_500 - 0.5) < 0.1}")
print(f"             delta_t ~ 0.2 ps: {abs(dt_500 - 0.2) < 0.1}")

# ---------------------------------------------------------------
# CHECK 7: Divergence point z -> 1/v
# ---------------------------------------------------------------
print("\n--- CHECK 7: Divergence near z_norm = 1/v ---")
z_div_norm = 1.0 / v
z_div_phys = z_div_norm / p["mu_s"]
print(f"  Divergence at z_norm = 1/v = {z_div_norm:.2f} mean free paths")
print(f"  That is z_phys = {z_div_phys*1e3:.2f} mm")
print(f"  MD states: ~14.3 MFP, ~3.3 mm")
print(f"  Match:     {abs(z_div_norm - 14.3) < 0.1} and {abs(z_div_phys*1e3 - 3.3) < 0.1}")

# ---------------------------------------------------------------
# CHECK 8: sigma_z_norm vanishes at T=0  (Taylor expansion)
# ---------------------------------------------------------------
print("\n--- CHECK 8: sigma_z_norm -> 0 as T -> 0 ---")
T_test = np.array([0.001, 0.01, 0.1])
sig_z = axial_variance_normalized(T_test, v, w)
print(f"  T          sigma_z_norm  (should -> 0 as T -> 0)")
for i in range(len(T_test)):
    print(f"  {T_test[i]:.3f}       {sig_z[i]:.6e}")

# ---------------------------------------------------------------
# CHECK 9: Direct line-by-line comparison with MATLAB reference
# ---------------------------------------------------------------
print("\n--- CHECK 9: Direct MATLAB-equivalent computation ---")
mu_s = p["mu_s"]
c = p["c"]
z_test = np.array([0.5e-3, 1e-3, 2e-3])
z_n = z_test * mu_s

T_ref = (1 / v) * np.log(1.0 / (1 - v * z_n))
DT_ref = T_ref - z_n
dt_ref = DT_ref / (mu_s * c)

evT = np.exp(-v * T_ref)
ewT = np.exp(-w * T_ref)
num = (w**2 - 3 * w * v) * (evT - 1 + v * T_ref) + 2 * v**2 * (ewT - 1 + w * T_ref)
den = w * v**2 * (w - v)
t1 = (2.0 / 3.0) * num / den
t2 = ((1 - evT) / v) ** 2
sig_sq = t1 - t2
sig_z_ref = np.sqrt(np.maximum(sig_sq, 0))
sig_t_ref = sig_z_ref / (mu_s * c)

m_test = compute_moments(z_test, p)

print(f"  z [mm]   sigma_t(direct) [ps]   sigma_t(func) [ps]   Match")
for i in range(len(z_test)):
    s_dir = sig_t_ref[i] * 1e12
    s_fun = m_test["sigma_t"][i] * 1e12
    ok = np.isclose(s_dir, s_fun, rtol=1e-10)
    print(f"  {z_test[i]*1e3:.1f}      {s_dir:.6f}              {s_fun:.6f}              {ok}")

print(f"\n  z [mm]   delta_t(direct) [ps]   delta_t(func) [ps]   Match")
for i in range(len(z_test)):
    d_dir = dt_ref[i] * 1e12
    d_fun = m_test["delta_t"][i] * 1e12
    ok = np.isclose(d_dir, d_fun, rtol=1e-10)
    print(f"  {z_test[i]*1e3:.1f}      {d_dir:.6f}              {d_fun:.6f}              {ok}")

# ---------------------------------------------------------------
# CHECK 10: Physical reasonableness
# ---------------------------------------------------------------
print("\n--- CHECK 10: Physical reasonableness ---")
z_full = np.linspace(1e-6, 3e-3, 2000)
m_full = compute_moments(z_full, p)
print(f"  z [mm]  z/ell_s [MFP]   sigma_t [ps]    delta_t [ps]")
for z_mm in [0.1, 0.25, 0.5, 1.0, 2.0, 3.0]:
    z = z_mm * 1e-3
    sig = np.interp(z, z_full, m_full["sigma_t"]) * 1e12
    dt = np.interp(z, z_full, m_full["delta_t"]) * 1e12
    mfp = z * mu_s
    print(f"  {z_mm:5.2f}   {mfp:12.1f}        {sig:10.4f}        {dt:10.4f}")

# Scaling check
s1 = np.interp(1e-3, z_full, m_full["sigma_t"])
s2 = np.interp(2e-3, z_full, m_full["sigma_t"])
print(f"\n  Scaling: sigma_t(2mm) / sigma_t(1mm) = {s2/s1:.3f}  (pure z^1.5 would give {2**1.5:.3f})")

# ---------------------------------------------------------------
# CHECK 11: Transverse variance sanity (Eq. C5)
# ---------------------------------------------------------------
print("\n--- CHECK 11: Transverse variance sigma_x (Eq. C5) ---")
T_vals = normalized_mean_time(z_full * mu_s, v)
evT = np.exp(-v * T_vals)
ewT = np.exp(-w * T_vals)
num_x = w * (evT - 1 + v * T_vals) - v * (ewT - 1 + w * T_vals)
den_x = w * v**2 * (w - v)
sigma_x_sq = (2.0 / 3.0) * num_x / den_x
sigma_x_sq = np.maximum(sigma_x_sq, 0)
sigma_x_norm = np.sqrt(sigma_x_sq)
sigma_x_real = sigma_x_norm / mu_s  # in metres

# sigma_x should be positive and growing
print(f"  sigma_x always >= 0:       {np.all(sigma_x_sq >= 0)}")
print(f"  sigma_x monotonic:         {np.all(np.diff(sigma_x_norm) >= 0)}")
sx_500 = np.interp(500e-6, z_full, sigma_x_real) * 1e6
sx_1mm = np.interp(1e-3, z_full, sigma_x_real) * 1e6
print(f"  sigma_x at 500 um = {sx_500:.1f} um")
print(f"  sigma_x at 1 mm   = {sx_1mm:.1f} um")
print(f"  (should be tens of um -- photon cloud lateral spread)")

# ---------------------------------------------------------------
# CHECK 12: sigma_z > sigma_x always (temporal > lateral)
# ---------------------------------------------------------------
print("\n--- CHECK 12: sigma_z > sigma_x (temporal > lateral spread) ---")
sigma_z_norm = axial_variance_normalized(T_vals, v, w)
# both in normalized units, compare
all_greater = np.all(sigma_z_norm[10:] >= sigma_x_norm[10:])  # skip near-zero
print(f"  sigma_z >= sigma_x for all z > 0: {all_greater}")
ratio_1mm = np.interp(1e-3, z_full, sigma_z_norm) / np.interp(1e-3, z_full, sigma_x_norm)
print(f"  sigma_z / sigma_x at 1 mm = {ratio_1mm:.2f}")

print("\n" + "=" * 65)
print("ALL CHECKS COMPLETE")
print("=" * 65)
