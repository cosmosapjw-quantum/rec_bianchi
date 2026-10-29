# REC-HD-CONSUMER-CALLSITE01: actual HD consumer policy and local source-energy ledger

**Date:** 2026-10-29 KST. **Owner:** `cosmosapjw-quantum/rec_bianchi`. **Parent:** Draft PR #155, HEAD `861b7f8b3e52d580437a1b4ad448d9669b0d2706`. **Scientific scope:** exact finite HD source diagnostics and selected real source-code callsites. No physical rate/provider, CDMS v2 source choice, default runtime mutation, old 9×9 stationary solve, native IVP, production or REI activation.

## R1. Fixed question and acceptance

Given the immutable 2021 LAMDA HD `hd.dat` (2289 bytes, SHA-256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`), identify which actual pinned REC/BASS/REI code functions use the **printed photon frequency** `nu_P` and which use the **energy-gap frequency** `nu_E`. Then construct a local, source-only energy-ledger identity, a nonvacuous control and a mutation test of an actual HD consumer. All results are scoped to the exact source and code versions in `CALLSITE_MATRIX.json`. The acceptance is an inspectable proof, source-identity checks, actual consumer invocation, negative tests and a durable handoff. Central DAG 28/88 (+0), REC physical 0/313 (+0).

## R2. Literature and immutable source provenance

The [official LAMDA data format](https://home.strw.leidenuniv.nl/~moldata/molformat.html) states that the printed frequency column is optional and not used by the program described there. [myRadex](https://github.com/fjdu/myRadex) explicitly changed its default in 2021-11-25 to use printed input frequencies, with a recalculate-from-levels switch. This establishes a **consumer-dependent** choice, not universal LAMDA policy. [pythonradex](https://pythonradex.readthedocs.io/en/latest/notebooks/reading_LAMDA_files.html) also documents a `read_frequencies=True` option. The [LAMDA HD file](https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat) contains nine J=0..8 term values, eight J->J-1 radiative lines and two nine-row p/o-H2 collision partners. Its comment attributes spectroscopy to CDMS December 2011 v2; that attribution is not a byte lock on CDMS originals.

[CDMS archived directory](https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/) is a locator only. Original 2011 v2 `.cat/.egy/.par/.fit/.lin` and source-to-LAMDA transformation bytes remain `NOT_ACQUIRED` from previous observed HTTP 503. The 2019-mtime `c003501.cat` is not assumed identical to the 2011 `c003501i.cat`, and CDMS 2026 v3 is not substituted. The parent PR #155 C10 SOURCE archive was restored and its 131011-byte SHA-256 and embedded HD source were verified locally; the actual parent code blobs `029255494bf0a63b93bf8b2715327a8585afb5f3` (PR151) and `21517960f912efbd2dc9df8b94fd577e03ca2e27` (PR155) also match Git blob identities.

## R3. Conventions, quantities, frame and signs

Signature `(-,+,+,+)`. All photon frequencies here are **ordinary** frequencies, not angular frequency. Keep SI `c=299792458 m s^-1`, `h=6.62607015e-34 J s = 2 pi hbar`, `k_B=1.380649e-23 J K^-1`. For a transition u->l,

\[
\nu_E = {E_u-E_l\over h} = 100 c (w_u-w_l),\qquad
\nu_P = 10^9\nu_{\rm printed,GHz},\qquad
\delta\nu = \nu_E-\nu_P.
\]

`w` has units cm^-1; `nu` Hz. The photon frequency is measured in the **local matter/comoving frame** with energy `E_gamma=-p_mu u^mu=h nu_local`; a frequency measured by another observer needs an explicit Lorentz/redshift transform. A frequency-grid coordinate or Doppler width is not itself a CDMS spectroscopic source identity. No global conserved energy is assumed in Bianchi expansion. We only audit the local source exchange between matter internal energy and photons, before spacetime transport/work.

Let `R_ul=n_u W_down^rad - n_l W_up^rad` denote **net downward radiative events per volume per time** (m^-3 s^-1). Positive R removes upper-state internal energy and creates photons. Under no third reservoir or external work for this isolated channel,

\[
(\partial_t U_m)_{\rm rad}=-(E_u-E_l)R_{ul}=-h\nu_E R_{ul},\qquad
(\partial_t U_\gamma)_{\rm rad}=+h\nu_P R_{ul}.
\]

The sign and units of the total source defect follow without assuming equilibrium. If a third reservoir exists, its compensating source must be explicitly modeled, not silently identified with heat or entropy.

## R4. Competing constructive interpretations

**A (printed-photon/level-energy mixed):** use `nu_P` in Einstein radiative occupation and photon energy while retaining `nu_E` for internal level energies and collisional Boltzmann ratios. This is exactly the PR151 diagnostic `generate(...,source_consistent=False)`. **B (energy-gap source-consistent counterfactual):** use `nu_E` in the radiative source too, as in `source_consistent=True`. B closes the local ledger algebraically but **does not authenticate** CDMS v2 or approve replacement. **C (external energy reservoir):** retain mixed fields and introduce a third explicit energy source; physically unresolved without source identity and mechanism. **D (metadata-only):** consumers that provably factor through LAMDA's selected core fields do not respond to optional printed metadata; this must be demonstrated at each actual callsite, not assumed from the format description.

## R5. Derived exact ledger theorem and nonvacuous controls

**Theorem (conditional local source-energy ledger).** For a finite set of transitions with independently specified local internal energy gaps `h nu_E,j`, emitted photon energies `h nu_P,j`, and net downward event densities `R_j`, the local two-sector energy residual is

\[
\boxed{\mathcal Q_{m+\gamma} = \sum_j h(\nu_{P,j}-\nu_{E,j})\,R_j = -h\sum_j\delta\nu_j R_j.}
\]

Proof: the same event decreases molecular internal energy by `h nu_E,j` and increases photon energy by `h nu_P,j`. Sum each contribution and then sum channels. The result has units W m^-3. The per-event coefficient `h(nu_P-nu_E)` is gauge-invariant under a common additive shift of all level energies; it is not a rate, observed heat or physical energy production. The total residual can vanish by cancellation for particular `R_j` even if individual per-event coefficients are nonzero. For a **channel-wise identity valid for arbitrary independent R_j**, every coefficient must vanish, i.e. `nu_P,j=nu_E,j`. The conditional independence of event fluxes is essential for this last iff.

**Actual PR151 rate law:** for radiation occupation `f_P=1/(exp[h nu_P/(k_B T)]-1)`, statistical ratio `g=g_u/g_l` and spontaneous A,

\[
W_{u\to l}^{rad}=A(1+f_P),\qquad W_{l\to u}^{rad}=g A f_P.
\]

Take a synthetic diagnostic bath at temperature `T>0` with `n_l=1 m^-3`, `n_u=g n_l exp[-h nu_E/(k_B T)]`. Then direct substitution yields

\[
R = A g n_l\, {\exp\{h(\nu_P-\nu_E)/(k_B T)\}-1\over
\exp\{h\nu_P/(k_B T)\}-1},
\qquad \mathcal Q_{m+\gamma}=h(\nu_P-\nu_E)R\ge0.
\]

The denominator is positive, and the numerator has the sign of `nu_P-nu_E`. Equality holds when the two frequencies agree. This is an **algebraic consistency control** of a deliberately mixed synthetic bath, not evidence of actual entropy generation. For arbitrary nonequilibrium populations the total residual need not be positive.

**Adversarial null control:** REC `one_photon_planck_null_residual` constructs *both* upper Boltzmann population and Planck occupation from the same supplied `frequency_Hz`. Its `A[x_u(1+f)-g x_l f]` is identically zero for every positive input frequency. Therefore this self-referential null is not an independent test of `nu_P=nu_E`. A genuine source check must supply the independently pinned level gap and photon frequency.

## R6. Review boundary

A same-context review and Wolfram exact symbolic evaluation check the two-sector sign, the synthetic rate formula, the null-control identity and the source-derived exact maximum. The first Python implementation had an extra `exp(-x_E)` multiplying the synthetic rate oracle and was rejected by the actual PR151 direct-rate comparison; that **theory-to-code implementation error was corrected**, then all affected tests rerun. A separate first test assumed an arbitrary display-name token and failed; it was replaced with a structural identity assertion. Neither failure was a physical model failure. **Distinct-author independent R6 is NOT_RUN** because native subagent delegation is not exposed; do not mark this stage complete.

## R7. Symbolic and finite source check

The stateless Wolfram kernel returned the exact symbolic synthetic rate and `Q` expressions and `one_photon_planck_null_residual=0`. For eight source-pinned HD transitions, the largest `|nu_E-nu_P|` is `1827572.5607572 Hz` at J=6->5. The largest **absolute per-event local ledger coefficient** is

\[
\boxed{|h(\nu_P-\nu_E)|_{\max}=1.210962399179234431758\times10^{-27}\ \mathrm{J/event}}
\]

at J=6->5. This number is a signed source-field discrepancy multiplied by the exact Planck constant, not a physical heat rate. The `results/RESULT.json` contains all eight exact rational coefficients and a source-only synthetic net-rate check. Six T/density node combinations were executed by calling **only** PR151 `generate` (no stationary solve, native solver or IVP).

## R8. Scientific decision

Admit a **conditional local source-ledger identity and tested consumer mapping**. PR151 is a real mixed-field *diagnostic consumer*. PR155 is a real dual-policy *diagnostic comparator*. REC production `frequency_liouville.py` instead uses a locked hydrogen Ly-alpha `nu_abs_Hz` and Doppler grid; inspected BASS atomic recombination/Thomson and REI HI/HeI/HeII continuum modules are **different physics**, not confirmed HD rotational consumers. This is an inspected-file finding, **not a proof of absence across all branches, generated/native code or future adapters**. No cross-repo source/rate admission follows.

## R9. Computational contract and transport interface

Each transition is a typed tuple `(source_sha, J_u, J_l, nu_E_Hz, nu_P_Hz, A_s_inv, g_u/g_l, frame, width_policy, energy_owner)`. Compute `delta_nu` with exact decimal/rational source tokens, reject nonfinite and unpinned inputs, and store `h(nu_P-nu_E)` separately from a rate. Do not add a compensating heat term by default. A consumer requiring another frame must explicitly provide `E_gamma=-p_mu u^mu` and its transform; a moving frequency grid requires remap/recompile as the existing REC `ConservativeFrequencyLiouville.from_network` already checks. A source-only metamorphic test mutates one decoded optional frequency *in memory* and asserts only its radiative edge changes while all 18 collision edges and the other seven radiative edges remain unchanged.

## R10. Closeout and next obligation

The scoped constructive derivation, source/commit callsite matrix and executable source-only controls are preserved. The central DAG remains **28/88 (+0)**, REC physical **0/313 (+0)**, H5 epsilon `null`, H6/H7 `OPEN`, L4 and REI false, production `HOLD`; original 35 Hz gate `FAIL_7_OF_8` unchanged. Next scientifically independent dependency remains original CDMS December 2011 v2 bytes plus LAMDA conversion lineage. A wider **production code callsite scan**, including generated C/Rust and actual native execution, is an explicit local Codex follow-up; it is not inferred from selected source files here. R6 and C9 distinct-author review remain partial.

### References / actual code identities

- [LAMDA format](https://home.strw.leidenuniv.nl/~moldata/molformat.html), [HD original file](https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat), [HD metadata](https://home.strw.leidenuniv.nl/~moldata/HD.html).
- [myRadex](https://github.com/fjdu/myRadex) and [pythonradex reader](https://pythonradex.readthedocs.io/en/latest/notebooks/reading_LAMDA_files.html) for differing consumer policies.
- [REC PR #151](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/151), [PR #154](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/154), [PR #155](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/155).
- `CALLSITE_MATRIX.json` lists exact repository commit, Git blob, function, lines and classification for nine selected source files. External research from SciSpace was used only as literature context, not a source for numerical HD literals or code semantics.
