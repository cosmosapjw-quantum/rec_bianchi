# REC_HD_NONLTE_J1_SOURCE_CONDITIONAL01 | 이론 연구 (R1–R10)

**연구 기준:** `rec_bianchi` Draft PR160 HEAD `0a8a0bcf740da6e4a2acda9d4fd071f7ed8e2691`, canonical `28/88`, REC physical `0/313`. 기존 원본 35Hz LAMDA 주파수 불일치 `FAIL7/8`. 본 결과는 신규 HD 비LTE 준위/충돌/광자 물리 데이터 생성이고 기존 production/owner 코드를 수정하지 않는다. 독립 원자료 바이트 재획득 미수행 상태는 정직하게 보존한다.

## R1–R3. 과학적 질문과 실제 자료

기존 PR160은 2022년 실험 HD(J2−J0, J3−J1) 두 **조합차**를 도입했다. 새로운 본 단위는 2021-06-07 공식 LAMDA HD 페이지의 원문 가독 자료에서 9개의 J 준위 (0–8), 8개의 복사 A/ν, para/ortho H₂ 각각 9개 하향 충돌 경로 × 실제 세 온도 (50/100/200K)를 별도 진본 출처와 함께 **수치 필드 전사**했다. 이는 54개의 실제 source-printed collision rate literals이다. 완전한 raw hd.dat 2289바이트의 SHA256 인증이나 2011 원본 CDMS fit/line/cat byte acquisition은 NOT_RUN. 원본 owner SHA `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb` 는 historical pin만 승계했다.

Official source: https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat, https://home.strw.leidenuniv.nl/~moldata/HD.html (Flower 1999 collision physics, CDMS Dec2011 v2 spectroscopy). Lab: Cozijn et al. (2022) https://doi.org/10.1140/epjd/s10053-022-00552-x and https://doi.org/10.1103/PhysRevA.105.062823. Related independent research Neufeld (2026) https://doi.org/10.3847/1538-4357/ae851a supports the physical importance of HD non-LTE conditions, **not** a validation of our specific 2021 source calculations.

Keep SI h=6.62607015×10^-34 J s, c=299792458 m/s, kB=1.380649×10^-23 J/K; rates in cm³/s multiplied by collider density in cm^-3 give s^-1, not rates per m³. Positive proper temperatures, no external radiation, no transfer opacity, no dust, no expansion, steady state at prescribed nH₂ and H₂ ortho fraction 0..1. Populations per one HD molecule, no invented HD abundance/column/Hubble clock. Radiative frequencies νP are printed source fields; internal level gaps νE=100c(Eu−El) cm^-1 are *distinct*. Historical 35Hz threshold unchanged.

## R4–R5. Constructive two-level source-gated line derivation

Only J=1→0 source internal gap and printed photon differ by −8.2410162 Hz; this line is the **only** source line within old 35Hz rounding gate. At T∈{50,100,200} K, LAMDA source q10_para=q10_ortho respectively {2.2,2.7,3.9}×10^-11 cm³/s. Define n ≡ n(H₂) in cm^-3, f ≡ ortho fraction, q10=(1−f)q10_p+f q10_o, q01=(g1/g0)q10 exp(−hνE/(kB T)) with g1/g0=3.

For normalized two-state population p0+p1=1, optically thin spontaneous radiative decay and collision kinetics:

```
0 = n q01 p0 − (n q10+A10) p1
p1 = n q01/[A10+n(q01+q10)]
P10_per_HD = A10 p1 h νP
P_Egap_per_HD = A10 p1 h νE
n_half = A10/(q01+q10)
P10_infinity = A10 h νP q01/(q01+q10)
```

Exactly q10_p=q10_o at all three original grid nodes implies ∂P10/∂f=0 for every n≥0, conditional on the two-state truncation. It is not an unverified universal ortho/para independence statement for full HD. Two energy sectors do **not** close exactly if using νP for photon vs νE for collisions: ΔP ≡ A10 p1 h(νE−νP), known explicit per-molecule source bookkeeping. Relative νE−νP/νE≈−3.0808×10^-12 and source gate PASS, but neither physical heating injection nor arbitrarily set-to-zero.

At 50,100,200K respectively, n_half = {2010.820708,1100.821467,541.081264} cm^-3; high-density P∞={1.8047135542,4.3776011109,5.9054673829}×10^-29 W/HD. Wolfram direct independent exact symbolic/numeric reproduction checked.

## R6–R8. Full-nine level contrast and verification scope

Build 9×9 Kolmogorov generator Q with column sums zero. For each stored radiative upper u>l: Q[l,u]+=A_ul, Q[u,u]−=A_ul. For each source collision channel (including special J2→0 edge), downward n q_ul(f,T), upward n q_ul(g_u/g_l) exp[−(Eu−El)/(kB T)], and corresponding diagonal loss. Solve Qp=0, Σp=1. Per-molecule candidate emitted power is Σ_{J=1}^8 p_J A_{J,J−1}hνP,J; internal-gap energy accounting uses νE,J instead.

This full-nine mixed-source output is an **unqualified scientific diagnostic** because J2–J8 *fail* the inherited source-field consistency gate. No source replacement by νE has been authorized, and the power is NOT a production cooling or actual cosmological history. It shows that multi-level H₂ ortho response can be nonzero even though the J1 two-level response is exactly zero.

Executed 3 temperature×7 prescribed density×3 ortho fractions=63 full-nine rows + 63 J1-two-level rows; 54 collision-rate rows and 504 per-line diagnostic power rows. Python 22/22 tests both normal and -O PASS and compileall PASS. An independent 80-digit mpmath generator/linear solve across 63 cases reproduces aggregate printed photon power to max relative error 2.1014×10^-11; maximum absolute population difference 1.241×10^-15. Wolfram independently confirms exact two-level signs, saturation and ∂_f P10=0. 3 PNG figures were rendered and visually checked. Different-author R6/C9 native subagents NOT_RUN. Floating-point tiny high-J population signs at low T are numerical rounding, not negative physical particles; independently positive mpmath populations are reported.

## R9–R10. Physical meaning and acceptance

**Scoped positive result:** at declared T,n,f and under two-level truncation, the J1 source-gated line has a calculable non-LTE optically thin power per HD and a chemically/radiatively meaningful saturation density; source field provenance is sufficiently visible to transcribe published rates, but exact raw bytes are *not* authenticated.

**Blocked physical promotion:** Source policy for J2–J8, original CDMS 2011 v2 fitted uncertainty/covariance, full optically-thick transport, temperature/density histories, collider abundances, radiation backgrounds, and actual 9-level owner integration. Canonical 28/88 (+0), REC physical 0/313 (+0), L4 false, H5 epsilon null, H6/H7 OPEN, production HOLD. Auxiliary research-specific model DAG `REC-HD-J1-2LVL-COOLING` COMPLETE_SCOPED, `REC-HD-FULL9-SOURCE-RECONCILIATION` PARTIAL, **1/2 auxiliary only**; these are not newly admitted canonical/physical node completions.