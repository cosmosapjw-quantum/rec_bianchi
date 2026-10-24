# PR-04B2A evidence ledger

## Provenance rule

For this project, `HyRec_Oct2012.zip` is the canonical official-site
October-2012 distribution. The owner's provenance attestation and the exact
byte lock are authoritative. Internal source-header and ZIP timestamp
variations are intrinsic metadata of that canonical release, not a mismatch or
uncertainty gate.

| ID | Claim | Durable evidence | Result |
|---|---|---|---|
| E1 | The supplied ZIP is the canonical official-site October-2012 HyRec distribution for this project. | Owner attestation; archive SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`; size `726954`; 29 safe entries; official HyRec release index lists October 2012. | **ACCEPTED_PROJECT_CANONICAL_PROVENANCE** |
| E2 | Original HyRec simultaneously evolves radiation, level populations, and the ionization history, with virtual levels representing the radiation field algebraically. | Canonical C source, original-HyRec paper, and v0.52 source census. | **ACCEPTED** |
| E3 | `x_b=x_1s \bar f_b` is not literal physical photon number in a finite-volume cell. | Source equations; paper variable definition; v0.52 forbidden physical-weight map residual `5.243277338650812e-3`. | **VERIFIED_FIREWALL** |
| E4 | The physical logarithmic spectral measure is `N_y=(8 pi nu^3)/(c^3 n_H) Delta f_nu`, photons per H per `d ln nu`. | Canonical `PRINT_SPEC` implementation and analytic phase-space conversion. | **VERIFIED** |
| E5 | Compile-time guarded diagnostics preserve the source-identical history. | Canonical and guard-off binary SHA-256 `a5ebb0e6...b733`; canonical, guard-off, and guard-on 8001-row history SHA-256 `9fdee53a...6485`; exactly one snapshot SHA-256 `3a95862b...34b7`. | **VERIFIED** |
| E6 | `x_1s Gamma_b(f_eq-\bar f_b)=H A_b(f_b^- -f_b^+)`, where `A_b=8 pi nu_b^3/(c^3 n_H)`. | Exact SymPy identity; source branch, stable branch, and 100-digit evaluations. Best structural relative residual `3.414e-15`; 100-digit residual `2.214e-101`. | **VERIFIED** |
| E7 | The canonical source solution, independent dense solve, and structured Schur solve give the same physical edge action and spectral source moments on their common domain. | Source/direct solution residual `3.525e-15`; Schur/direct `1.188e-15`; moment residuals `1.250e-13` and `7.541e-14`. | **VERIFIED** |
| E8 | The edge action has units `s^-1` per H and its order-`r` spectral source moment has units `Hz^r s^-1` per H. | Explicit dimensional derivation with `nu` in Hz and `n_H` in cm^-3 combined with source `hc` in eV cm. | **VERIFIED** |
| E9 | A same-event photon/atom energy ledger closes exactly. | `Delta E_gamma=h nu_b` source contribution and equal opposite atom entry; maximum total residual `0 W/H`. | **VERIFIED** |
| E10 | The physical edge update admits an analytic JVP and a positivity-preserving implicit step. | JVP relative residual `4.157e-9`; explicit stress step minimum `-5.548e-16`; implicit minimum `4.042e-19`. | **VERIFIED** |
| E11 | Direct v0.51 COM–KHW/native parity cannot be inferred from centre overlap or from raw `Aup/Adn`, `x_b`, or completed `Tvv`. | Only two native centres fall in the 17-cell `|x|<=4.25` core; source and target objects are respectively a state-dependent escape-compressed net trajectory flux and an occupation-independent event measure. No ratio was fitted. | **OPEN_FAIL_CLOSED** |

## Validation deviation disclosure

The preregistered matrix initially assigned a relative `<1e-12` threshold to a
first-order comparison between the nearest internal grid point and the
separately cubic-interpolated public `z=1100` output. That diagnostic produced
`5.992e-11` for `x_e` and `1.478e-10` for `T_m/T_r`. The threshold was not met
and is not reported as met. It was reclassified as a non-load-bearing
nearest-grid interpolation diagnostic because the two quantities are not
computed by the same interpolation rule. The source-identical binary/history
hashes and the exact internally emitted trajectory state remain the primary
instrumentation gates. The stage hard limits for these diagnostics are
`1e-9` and `1e-8`, respectively, and both pass. No scientific normalization or
parity threshold was relaxed.

## Tool availability

- Web search: official HyRec page and primary original-HyRec/HYREC-2 papers used.
- Wolfram: `UNAVAILABLE_IN_RUNTIME`.
- Precise Special Functions: `UNAVAILABLE_IN_RUNTIME`.
- Independent fallbacks: SymPy exact algebra; mpmath at 100 digits; NumPy dense
  and structured-Schur linear algebra; direct canonical C compile/execution;
  central-difference JVP regression.
- GitHub private-repository connector: not exposed in this execution runtime.
  Local bundle state and `check_remote_state.py` receipts are recorded; no live
  remote SHA or push is inferred.
