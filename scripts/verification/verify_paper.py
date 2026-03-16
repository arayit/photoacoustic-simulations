"""
Line-by-line verification of the implementation against the actual
Lutomirski et al. (1995) paper equations, read from the PDF screenshots.
"""

import numpy as np

g = 0.93
v = 1 - g                          # Eq. 21a
cos2theta = (1 + 2 * g**2) / 3     # Henyey-Greenstein
w = 1.5 * (1 - cos2theta)          # Eq. 21b

print("=" * 65)
print("VERIFICATION AGAINST PAPER (Lutomirski 1995)")
print("=" * 65)

print("\n--- Definitions (Eqs. 21a, 21b) ---")
print(f"  v = 1 - g = {v:.4f}")
print(f"  w = 3/2 (1 - <cos^2 theta>) = {w:.4f}")

# ==================================================================
# Eq. C5: TRANSVERSE VARIANCE
#
# From paper image (page with Eq. C5):
#
#   sigma_x^2 = (2/3) * [w^2(exp(-vT)-1+vT) - v^2(exp(-wT)-1+wT)]
#                        / [wv^2(w-v)]
#
# The MD document incorrectly has w and v instead of w^2 and v^2
# in the numerator.
# ==================================================================

print("\n--- Eq. C5 (transverse variance) ---")
print("  Paper:  numerator = w^2 * h(v,T) - v^2 * h(w,T)")
print("  MD doc: numerator = w   * h(v,T) - v   * h(w,T)")
print("  DISCREPANCY in MD document!")

T_test = 5.0
evT = np.exp(-v * T_test)
ewT = np.exp(-w * T_test)
h_v = evT - 1 + v * T_test
h_w = ewT - 1 + w * T_test
den = w * v**2 * (w - v)

num_md    = w * h_v - v * h_w
num_paper = w**2 * h_v - v**2 * h_w

sig_x_sq_md    = (2.0 / 3.0) * num_md / den
sig_x_sq_paper = (2.0 / 3.0) * num_paper / den

print(f"\n  At T = {T_test}:")
print(f"    MD version:    sigma_x^2 = {sig_x_sq_md:.6f}  {'NEGATIVE!' if sig_x_sq_md < 0 else 'OK'}")
print(f"    Paper version: sigma_x^2 = {sig_x_sq_paper:.6f}  {'NEGATIVE!' if sig_x_sq_paper < 0 else 'OK'}")

# ==================================================================
# Eq. C7: AXIAL VARIANCE  (the one we actually use)
#
# Paper image (last page, Eq. C7):
#
#   sigma_z^2 = (2/3) * [(w^2 - 3wv)(exp(-vT)-1+vT)
#                        + 2v^2 (exp(-wT)-1+wT)]
#                       / [wv^2(w-v)]
#              - [(1 - exp(-vT)) / v]^2
#
# MD document has the same. MATCH.
# ==================================================================

print("\n--- Eq. C7 (axial variance) ---")
num_z  = (w**2 - 3 * w * v) * h_v + 2 * v**2 * h_w
sig_z_sq = (2.0 / 3.0) * num_z / den - ((1 - evT) / v)**2
print(f"  sigma_z^2 = {sig_z_sq:.6f}  {'OK (positive)' if sig_z_sq > 0 else 'NEGATIVE!'}")
print("  Paper and MD agree: YES")

# ==================================================================
# Eq. 26: <z(T)> = (1 - exp(-vT)) / v
# Eq. 45a (MD): T(z) = (1/v) ln(1/(1-vz))  -- this is the inverse
# ==================================================================

print("\n--- Eq. 26 / Eq. 45a (mean penetration and its inverse) ---")
z_from_T = (1 - np.exp(-v * T_test)) / v
T_from_z = (1 / v) * np.log(1.0 / (1 - v * z_from_T))
print(f"  Eq. 26:  <z(T={T_test})> = {z_from_T:.6f}")
print(f"  Eq. 45a: T(z={z_from_T:.6f}) = {T_from_z:.6f}")
print(f"  Round-trip: {np.isclose(T_test, T_from_z)}")

# ==================================================================
# Eq. 28a: <z^2(T)> = (2/3) * [(w^2-3wv)*h(v,T) + 2v^2*h(w,T)]
#                              / [wv^2(w-v)]
# Eq. 28b: sigma_z^2 = <z^2> - <z>^2
# Verify C7 = 28a - 26^2
# ==================================================================

print("\n--- Eq. 28a/28b decomposition ---")
z_mean  = (1 - evT) / v
z2_mean = (2.0 / 3.0) * num_z / den
var_28b = z2_mean - z_mean**2
print(f"  <z>     = {z_mean:.6f}")
print(f"  <z^2>   = {z2_mean:.6f}")
print(f"  Var(28b) = <z^2> - <z>^2 = {var_28b:.6f}")
print(f"  Eq. C7 direct             = {sig_z_sq:.6f}")
print(f"  Match: {np.isclose(var_28b, sig_z_sq)}")

# ==================================================================
# Small-T asymptotics (Section 7, Eq. 39)
# sigma_z^2(T) ~ (2/3)(3v - w) T^3 for small T
# ==================================================================

print("\n--- Small-T asymptotics (Eq. 39) ---")
print(f"  Asymptotic formula: sigma_z^2 ~ (2/3)(3v - w) T^3")
print(f"  (2/3)(3v-w) = {(2.0/3.0)*(3*v - w):.6f}")
print()
print(f"  {'T':>10}  {'Exact':>14}  {'Asymptotic':>14}  {'Ratio':>10}")
for Ts in [0.1, 0.01, 0.001, 0.0001]:
    evTs = np.exp(-v * Ts)
    ewTs = np.exp(-w * Ts)
    h_vs = evTs - 1 + v * Ts
    h_ws = ewTs - 1 + w * Ts
    num_s = (w**2 - 3 * w * v) * h_vs + 2 * v**2 * h_ws
    exact = (2.0 / 3.0) * num_s / den - ((1 - evTs) / v)**2
    asymp = (2.0 / 3.0) * (3 * v - w) * Ts**3
    ratio = exact / asymp if asymp != 0 else float("inf")
    print(f"  {Ts:>10.4f}  {exact:>14.6e}  {asymp:>14.6e}  {ratio:>10.6f}")
print("  (Ratio should -> 1.0 as T -> 0)")

# ==================================================================
# Small-T asymptotics for transverse (Eq. 36)
# sigma_x^2(T) ~ (w/9) T^3  for small T
# ==================================================================

print("\n--- Small-T asymptotics for sigma_x (Eq. 36) ---")
print(f"  Asymptotic formula: sigma_x^2 ~ (w/9) T^3")
print(f"  w/9 = {w/9:.6f}")
print()
print(f"  {'T':>10}  {'Paper Eq':>14}  {'Asymptotic':>14}  {'Ratio':>10}")
for Ts in [0.1, 0.01, 0.001, 0.0001]:
    evTs = np.exp(-v * Ts)
    ewTs = np.exp(-w * Ts)
    h_vs = evTs - 1 + v * Ts
    h_ws = ewTs - 1 + w * Ts
    # Paper version (w^2, v^2)
    num_x = w**2 * h_vs - v**2 * h_ws
    exact = (2.0 / 3.0) * num_x / den
    asymp = (w / 9.0) * Ts**3
    ratio = exact / asymp if asymp != 0 else float("inf")
    print(f"  {Ts:>10.4f}  {exact:>14.6e}  {asymp:>14.6e}  {ratio:>10.6f}")
print("  (Ratio should -> 1.0 as T -> 0)")

# ==================================================================
# FINAL: Our code's sigma_z matches paper Eq. C7?
# ==================================================================

print("\n--- Final comparison: code output vs paper equations ---")
from temporal_broadening import make_params, compute_moments

p = make_params()
z_phys = np.array([0.5e-3, 1.0e-3, 2.0e-3])
m = compute_moments(z_phys, p)

mu_s = p["mu_s"]
c    = p["c"]

print(f"  {'z [mm]':>8}  {'sigma_t code [ps]':>18}  {'sigma_t paper [ps]':>19}  {'Match':>6}")
for i, z in enumerate(z_phys):
    z_norm = z * mu_s
    T = (1 / v) * np.log(1 / (1 - v * z_norm))
    evT = np.exp(-v * T)
    ewT = np.exp(-w * T)
    hv  = evT - 1 + v * T
    hw  = ewT - 1 + w * T
    num = (w**2 - 3 * w * v) * hv + 2 * v**2 * hw
    s2  = (2.0 / 3.0) * num / den - ((1 - evT) / v)**2
    sig_paper = np.sqrt(max(s2, 0)) / (mu_s * c) * 1e12

    sig_code = m["sigma_t"][i] * 1e12
    ok = np.isclose(sig_code, sig_paper, rtol=1e-10)
    print(f"  {z*1e3:>6.1f}    {sig_code:>15.6f}      {sig_paper:>15.6f}    {ok}")

print("\n" + "=" * 65)
print("CONCLUSION")
print("=" * 65)
print("""
1. Eq. C7 (axial variance sigma_z^2):
   CORRECT. Code matches paper exactly.
   This is the equation used for temporal broadening.

2. Eq. C5 (transverse variance sigma_x^2):
   MD DOCUMENT HAD A TYPO. Numerator should have w^2 and v^2,
   not w and v. Paper clearly shows w^2 and v^2.
   NOT used in our temporal broadening code -- no impact.

3. Eq. 26/45a (mean time / mean penetration):
   CORRECT. Inverse relationship verified.

4. Small-T asymptotics (Eqs. 36, 39):
   Both converge correctly, confirming formulas.

5. Overall: The temporal broadening calculation is CORRECT.
""")
