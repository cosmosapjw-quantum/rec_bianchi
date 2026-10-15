# REC R3b: original HyRec2012 FULL real/virtual atomic source + outgoing photon history

**2026-10-15 KST; theory R3b and coding C5–C8 scoped constructive research.**

Source branch parent: PR #92, exact SHA 98b9f3099fa12b80437531473c627998ff6c0d20.
Original Oct2012 HyRec ZIP SHA256: 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27.
Worktree: /home/cosmosapjw/rec_theory_runs/REC_R3B_FULL_SOURCE_20261015/checkout

## 1. Meaningful physical progress

Implemented the missing FULL (not EMLA2s2p) **single-instant hydrogen atomic/source/radiation update**, using original source's real+virtual algebraic equations and full causal outgoing writeback. Inputs comprise a physically chosen z, x_HII, optional x_e, T_m, and previously accepted 311 virtual + 3 Lyman photon history (PR #92). The q=0 incoming virtual 311 + Lyman 2 values are computed by the source-verified PR92 characteristic operator. This module independently builds the original 2 real + 311 virtual physical matrix from frozen HyRec2012 rates and diffusion source, solves it, computes dx_HII/dln(a), and writes a read-only uncommitted output candidate comprising 311 virtual, 3 Lyman, 311 average values.

Critical distinction: **The state is not a new FULL recombination history**. No coupled time integration xe(z), Tm(z), helium ionization, q != 0 atomic-collision or CMB observable has been claimed. A photon-history writeback candidate is not an accepted evolving global step. The original He part and physical past nonthermal spectrum must still be supplied.

## 2. Source-specific definition and equations

Original oct2012 hydrogen.c: populate_Diffusion ~355–409, populateTS_2photon ~414–553, solveTXeqB and solve_real_virt ~569–625, interp_Dfnu 633–651, fplus_from_fminus 667–718, rec_HMLA_2photon_dxHIIdlna 727–803. Source hx is cgs+eV, public H s^-1, n_H m^-3, T K. k_B=8.617343e-5 eV/K, hc=1.239841874331e-4 eV cm; ħ and c have NOT been set to unity in physical units.

Define x_1s = 1 - x_HII; Tr and Tm in eV; A_up/down source diffusion transition rates; gamma_b the lifetime coefficient computed from *pre-line-neighbor-update* Trv:

\[
\Gamma_b=-T_{rv,0b}-T_{rv,1b}+A^\uparrow_b+A^\downarrow_b,\quad
\tau_b=\frac{x_{1s}n_H}{8\pi H}\Gamma_b\left(\frac{hc}{E_b}\right)^3.
\]

The native virtual-row diagonal and incoming source are

\[
P_b=1-\frac{1-e^{-\tau_b}}{\tau_b},\quad
T_{vv,bb}=\frac{\Gamma_b}{P_b},\quad
s_{v,b}=T_{vv,bb}\,x_{1s}\,\Delta f^+_b(1-P_b),
\]
with source C's small-tau continuation P=tau/2 -tau^2/6 for tau<=1e-6 and the source-defined 0-limit for the diagonal. Nonzero T_vv offdiagonals belong only to bins 100:180, with 139/140 Lyman-alpha interface split. The real/virtual atomic rates include 2s<->2p EMLA transfer, Ly-alpha beta gamma escape, 2s/3s3d/4s4d two-photon and Raman, and A1s diffusion. Rates and energies are original source-locked tables, not RECFAST substitution.

Instantaneous algebraic partition:

\[
\begin{pmatrix} T_{rr}&T_{rv}\\T_{vr}&T_{vv}\end{pmatrix}
\begin{pmatrix}x_r\\x_v\end{pmatrix}
=\begin{pmatrix}s_r\\s_v\end{pmatrix}.
\]

With U=T_vv^-1 T_vr and v=T_vv^-1 s_v,

\[
S=T_{rr}-T_{rv}U,\qquad
x_r=S^{-1}(s_r-T_{rv}v),\qquad x_v=v-Ux_r.
\]

The actual algorithm uses one tridiagonal banded LAPACK solve on the 80-bin subblock for three RHS [s_v, T_vr(:,0), T_vr(:,1)] and diagonal division elsewhere, followed by a 2x2 real solve. Wolfram Language symbolic 2+1 block elimination returned exactly {0,{0,0,0}} for determinant identity and full residual. The 313-case is the same algebraic identity subject to invertibility. It is NOT a proof of positivity of every possible source/thermodynamic input or of global ODE stability.

Original source-prescribed output:

\[
\Delta f^-_b=\Delta f^+_b+
(\Delta f^{\rm eq}_b-\Delta f^+_b)(1-e^{-\tau_b}),
\]
\[
(\Delta f^-_{\mathrm{Ly}\alpha},\Delta f^-_{\mathrm{Ly}\beta},
\Delta f^-_{\mathrm{Ly}\gamma})=
\left(\frac{x_{2p}}{3x_{1s}},
\frac{x_{2s}}{x_{1s}}e^{-E_{32}/T_r},
\frac{x_{2s}}{x_{1s}}e^{-E_{42}/T_r}\right),\quad
\Delta f_b^{avg}=\frac{x_{v,b}}{x_{1s}}.
\]

For tau <=1e-30, source conservatively passes the incoming occupation with no modification. x_HII derivative comes from original C source alpha/beta plus solved real departures. This is H-only atom+photon source at a fixed time, with helium not dynamically evolved.

## 3. Source-C independent parity and actual physical state checks

Source oracle is compiled from the unchanged, pinned original 2012 hydrogen.c and hyrectools.c (including original populateTS/solve_real_virt/rec_HMLA_2photon_dxHIIdlna), by our small C ABI wrapper in scripts/c_harness/original_hyrec_full_source_harness.c. No copied C reference history used as an initial condition: the accepted incoming histories are deliberately manufactured nonconstant 311+3 spectral functions; the source computes its own incoming fplus before outgoing update.

Four cases (z,x_HII,Tm/Tr) = (650,.002,.95), (900,.04,.98), (1200,.45,.999), (1450,.97,.99999), with accepted histories (80,95,170,200). All 16 output families checked: Trr,Trv,Tvr,Tvv,sr,sv,Dtau,Alpha,DeltaAlpha,Beta,real,virtual,outgoing virtual,outgoing Lyman,average virtual,electron RHS. Source-specific max relative error scaled against each field's physically nonzero local magnitude and a 1e-12 in-field floor:

**3.5099619408579026e-9**, gate **1e-8**. The previous source-emission matrix residual is **4.36e-16** or below, and electron RHS is much closer to raw C than the limiting virtual component. These are deterministic source-point comparisons, not trajectory/observational validation. Receipt NATIVE_POINT_PARITY.json retains per-sample/per-field abs/global/element error.

## 4. A real numerical defect found in historical source evaluation

The original C binary64 expression for P_b for tau>1e-6 is 1-(1-exp(-tau))/tau. It loses significant relative precision near threshold. A first Python reconstruction used expm1 and differed from C Tvv by up to ~9e-5 in relative source-lifetime entries. This was diagnosed without relaxing the scientific gate: restoring the original C evaluation order produces source binary64 parity up to 3.51e-9 across all blocks and electron RHS essentially at source precision.

An independent 75-digit mpmath check on the exact binary64 input optical depths found:
- z650 worst tau=1.25321e-6: original C factor relative error 6.1959487e-5; expm1 alternative 6.65e-11 at same bin
- z900 worst tau=1.45616e-6: source error 1.3445161e-5
- z1200 worst tau=3.33471e-6: source error 7.3081139e-6
- z1450 worst tau=1.08024e-6: source error 9.0625719e-5

New accurate_escape_factors() uses the analytic series to sixth order for tau<0.03 and expm1 for larger tau. It is a **separate, explicitly opted alternative computational form**, never substituted for source-parity mode. On the independent selected tau test set it reproduces a 75-digit reference with relative error <5e-13. Original source may be improved in a future specifically authorized scientific-equivalence lane, but source-byte/number parity is preserved here. See ESCAPE_CANCELLATION_AUDIT.json. Distinguish cancellation in computed P from a physical claim of huge xe(z) error: only full trajectory convergence can determine the latter.

## 5. Measured numerical efficiency

Independent dense 313x313 system reconstructed from original physical Trr/Trv/Tvr/Tvv to cross-verify the sparse Schur solver. At z900 and z1200, full vector dense/banded agreement in global solution relative norm was 3.66e-14 and 1.41e-15. On local Ubuntu with OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1, fixed-coefficient **algebraic solve-only** 5-trial median per call:

| z | 80-bin banded Schur | 313 dense solve | measured speedup |
|---|---:|---:|---:|
| 900 | 0.0663 ms | 0.6565 ms | 9.90x |
| 1200 | 0.0659 ms | 0.6105 ms | 9.26x |

Full source-rate interpolation, 311 virtual matrix construction, physical photon transport and global xe integration are excluded from this benchmark. Threads are pinned to one due to submillisecond work and previously measured parallel IPC overhead. See SCHUR_BENCHMARK.json.

## 6. Source and cross-repository authority

This is a derived/reimplemented continuation of original HyRec physics, **not an established new theorem/novel observable**. Primary: Y. Ali-Haïmoud & C. M. Hirata, Phys. Rev. D 83, 043513 (2011) https://arxiv.org/abs/1011.3758, and immutable original Oct2012 C source archive. Secondary cross-repo use: REI AX08 latest PR122 completed signed-minus native abundance history, PR121 independently validated proper-time/Killing tables; bass_cr PR71 source-conditioned adaptive spectral support; BASS_HE PR64 saved-source 16-cell warm opacity; WU088_HH PR81 independent radial-angular proof effort. Their physical epochs, scattering Hamiltonians, and UVB photon rates are **NOT** substituted for HyRec EMLA or primordial hydrogen/helium source rates. Useful carryover is provenance and bounded positive/signed error protocol, not numerical values. Cross-repo source modifications=0.

## 7. Stopping/positive transition

**Admitted:** q0 original FULL H atomic source at four independent physical states with manufactured accepted-memory histories; original C equivalence for source matrix/electron response/outgoing writes; exact algebraic sparse inversion and benchmark; mathematically stable separate escape-factor alternative.

**Not admitted:** original FULL independently integrated xe(z), Tm(z), original H/He simultaneous evolution, consistent primordial past photon spectrum, q != 0 collisions, thermal radiation energy exchange or CMB predictions. No virtual-ODE mass inserted; not a production REI replacement. Existing original REC dirty checkout and REI producer unchanged.

**Next strictly meaningful stage:** turn the verified R3b single-step operator into an accepted-step **self-consistent q=0 H-only FULL photon-memory trajectory** with physically specified start/history and controlled finite-time integration; compare to native original C FULL and separate mismatched helium/initial conditions. Then add H/He and Tm coupling, followed by source-owned directional Bianchi extension.

Reproduce with commands in TEST_RECEIPT.json; machine-readable next gate in NEXT_LOOP.json.
