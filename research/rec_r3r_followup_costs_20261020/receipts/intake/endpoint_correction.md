# Independent PHYS-MATH correction: source-defined h2 z=0 endpoint

## Verdict and exact scope

**PASS_SCOPED: the saved h2 run supplies the complete original HyRec2012 four-node endpoint stencil.** The historical claim that only three terminal states are available is contradicted by the original interpolation rule, current frozen Python implementation, saved NPZ, and its own producer verification.

This note corrects the interpretation of the existing completed run. It does not alter the original source, saved history, prior review, tolerances, or allocation. No trajectory integration, native solver run, or prior test suite was repeated. Four saved scalar values were independently substituted into the original ordered cubic formula in Python, reproducing the stored Python and native endpoint values exactly as binary64 scalars.

## Definitions and source identity

Let x=ln a with present a=1, so the desired endpoint is x*=0 (z=0). The source grid is

\[
x_i=x_0+i h,\qquad x_0=-\ln8001,\qquad h=4.245\times10^{-5},
\]

and z_i=8001 exp(-h i)-1. Both x and h are dimensionless. The interpolated y is either dimensionless xe=n_e/n_H or Tm measured in kelvin; interpolation coefficients are dimensionless and preserve the units of y.

The inspected original archive is `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`. Original `HyRec/history.c` sets

\[
N_x=\left\lfloor2+\frac{\ln[(1+Z_{\rm start})/(1+Z_{\rm end})]}{h}\right\rfloor.
\]

Original `HyRec/hyrectools.c::rec_interp1d` first checks the global interpolation domain, computes floor((x-x0)/h), clamps the index to [1,Nx-3], and then reads nodes ix-1,ix,ix+1,ix+2. Its interpolation fraction is calculated after this clamp and is not clipped to [0,1]. The source uses an output node with z<0 to bracket the physical endpoint; it does not require a negative-redshift RHS evaluation.

The faithful Python implementation is `src/full_bianchi_hyrec/trajectory/primordial_2012_refined_low_z.py`, SHA256 `6f6cdfa281fc893f80334e43418a130cdd7526be8e14d9575eed74dcbd7edee6`.

## Index proof at the actual endpoint

Set alpha=(0-x0)/h and m=floor(alpha). Here alpha is not an integer. Therefore

\[
N_x=m+2,\qquad N_x-3=m-1.
\]

Since raw ix=m exceeds Nx-3, the source sets ix=m-1. Its four required indices are

\[
(ix-1,ix,ix+1,ix+2)=(m-2,m-1,m,m+1).
\]

The final allocated source index is Nx-1=m+1. Thus all four required endpoint nodes belong to the source grid. The endpoint lies between nodes m and m+1 because m<alpha<m+1. With s=alpha-ix, one has 1<s<2. This fraction is inside the full four-node stencil coordinate interval [-1,2], and between its final two nodes. It is not out-of-domain extrapolation and must not be clipped to1.

The actual recorded values are

| Quantity | Value |
|---|---:|
| x0 | -8.987321812850125 |
| alpha | 211715.47262308892 |
| Nx | 211717 |
| raw floor index m | 211715 |
| clamped ix | 211714 |
| s | 1.4726230889209546 |
| required global indices | 211713,211714,211715,211716 |

The saved NPZ has153328 sequential states, beginning at iz58389 and ending at211716. Its final four redshifts are

\[
(1.0496835891560252\times10^{-4},\;
6.251480409291688\times10^{-5},\;
2.0063051384022756\times10^{-5},\;
-2.238689928646398\times10^{-5}).
\]

The final RHS input is node211715, with positive z. Node211716 is the accepted output of that update and closes the z=0 bracket. An extra step would exceed the original source grid and is neither necessary nor authorized by this endpoint argument.

## Exact cubic and its mathematical properties

Write y0,y1,y2,y3 for values at global nodes ix-1,ix,ix+1,ix+2. The source polynomial is

\[
P_3(s)=
-\frac{y_0s(1-s)(2-s)}6
+\frac{y_1(1+s)(1-s)(2-s)}2
+\frac{y_2(1+s)s(2-s)}2
-\frac{y_3(1+s)s(1-s)}6.
\]

These are the four Lagrange cardinal basis functions on local nodes r=(-1,0,1,2). Each coefficient wi has wi(rj)=deltaij. The resulting identities

\[
\sum_iw_i=1,\qquad
-w_0+w_2+2w_3=s,\qquad
w_0+w_2+4w_3=s^2,\qquad
-w_0+w_2+8w_3=s^3
\]

establish exact reproduction of all polynomials of degree at most3. At the actual endpoint the binary64 coefficients computed separately for interpretation are approximately

\[
(w_0,w_1,w_2,w_3)=
(0.06117534136749787,-0.30815127647237867,
0.9601534399213091,0.2868224951835717).
\]

The absolute sum is1.6163025529447574. In real arithmetic this bounds amplification of independent absolute nodal perturbations: if every |delta yi|<=epsilon, then |delta P3|<=1.6163025529447574 epsilon. One coefficient is negative, so unconditional positivity preservation is not a property of this cubic; the actual positive saved endpoints are checked separately.

For a C4 function y(x) sampled exactly on these nodes, the interpolation remainder is

\[
y(0)-P_3(s)=\frac{h^4}{24}(s+1)s(s-1)(s-2)y^{(4)}(\xi)
\]

for some xi within the four-node interval. Hence

\[
|y(0)-P_3(s)|\le
1.227962512414346\times10^{-19}
\sup_{\xi}|y^{(4)}(\xi)|.
\]

This is a conditional interpolation bound in x=ln a. The fourth derivative bound has not been established for the continuous recombination solution, and the saved node values themselves have discretization errors. Therefore this formula does not supply a complete global integration error bound or establish three-grid convergence.

The equation above is an exact-real polynomial identity. The source's binary64 implementation evaluates terms in its original left-to-right arithmetic order. Replacing it with precomputed weights and a dot product, Horner evaluation, FMA, clipped s, or another algebraic ordering would require a separate numerical-equivalence claim; none is made here.

## Independent substitution of saved values

Four-node NPZ identity:
`research/rec_r3o_grid_frontiers_20261019/lowz_ncp_full_001/python_native_lowz.npz`
SHA256 `b25e2cbdafe4037d222116c4985eac95a380552f6799a2b3e950fb499965dbe6`,6982148bytes.

The new small read-only calculation cast each of the four array values to a Python float and evaluated the source-ordered expression above. Each result matched the corresponding saved verification scalar by `float.hex()`, including the separately saved native node sequence.

| Field | Python-node cubic | Native-node cubic | Absolute difference |
|---|---:|---:|---:|
| xe | 0.00017561306612632919 | 0.0001756130661263253 | 3.876022766635678e-18 |
| Tm[K] | 0.02172948290109453 | 0.021729482901094277 | 2.5326962749261384e-16 |

Python/native endpoint hexadecimal scalars:

- xe: `0x1.70498c063fda5p-13` / `0x1.70498c063fd16p-13`.
- Tm: `0x1.64040e9ad40b9p-6` / `0x1.64040e9ad4070p-6`.

This is an independent endpoint recomputation from saved nodes, not a new native solver execution. The previous producer's common-input native interpolation test is reused as its own recorded evidence.

## Correction ledger and decision

| Item | Evidence | Classification and correction |
|---|---|---|
| Historical review reports available_terminal_states=3 | `lowz_ncp_full_001/INDEPENDENT_REVIEW.json`, SHA256 c50c4870de9a9ab294b9d75440beb75b93c5a9f2d7a88b5e5e2afa35a205a001 | Review/report interpretation error. Actual source stencil has4 available states. Preserve the historical file and link this correction. |
| Historical review still says z0_cubic_recompute=PASS | Same review and raw NPZ | Supports original endpoint calculation; its missing-state sentence was internally inconsistent. |
| Producer status STOP_AT_SOURCE_Z0_CUBIC_STENCIL | `verification.json`, SHA2563525f0fc13bc493a8ebc6d42741d7e9af5cbe726478df819f2ea918f5ad98c37 | Source code uses this status only for complete source-end coverage with at least4 retained states. Incomplete tails have their own separate status. |
| No matched complete h4 trajectory | R3Q DAG and actual event checkpoint at iz74411 | Actual remaining numerical coverage obligation for h/h2/h4 comparison. |

The R3R current claim ledger may mark h2 source-defined endpoint reconstruction **complete_reused, with the stated interpretation correction**. Old U5 h=HOLD_9_FAIL, h2=HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN/HOLD, REI_activation=false and physical-production gates retain their original meanings.

## Review result

Mathematical index/clamp and cubic correctness: derived, PASS_SCOPED.
Saved four-node availability and scalar substitution: numerically checked, PASS_SCOPED.
Original same-h trajectory result: complete_reused from prior receipts.
Independent new continuous-solution error bound, new acceleration or production admission: not claimed.
