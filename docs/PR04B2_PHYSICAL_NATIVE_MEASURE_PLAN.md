# PR-04B2 execution plan — physical native measure and FLRW closure

## Objective

Map original-HyRec's algebraic virtual-level proxy onto the positive physical frequency-space common measure fixed in PR-04A, without a fitted normalization, and close one source-identical full-trajectory FLRW snapshot.

## Locked conventions

- metric signature `(-,+,+,+)`;
- ordinary frequency `nu` in Hz;
- `Delta nu = nu_target - nu_source`;
- `Delta E_gamma = h Delta nu`, `Delta E_H = -h Delta nu`;
- retain `c`, `h`, and `k_B` explicitly;
- local hydrogen-frame microphysics remains independent of Bianchi type.

## Bounded work packages

### B2.1 Source-identical instrumentation

Add compile-time-gated diagnostic hooks without changing the uninstrumented baseline numerics. At a locked recombination snapshot, dump:

- redshift, `T_m`, `T_r`, `n_H`, `H`, `x_e`, `x_1s`;
- `Dfplus`, `Dfminus`, `Dfnu_hist`, `xv`, and `Dtau`;
- real/virtual `Trr`, `Trv`, `Tvr`, `Tvv`, `sr`, `sv`;
- frequency/bin centres and boundaries used by the diffusion/escape stencil.

The uninstrumented executable and its baseline-output SHA-256 must remain unchanged.

### B2.2 Physical-measure derivation

Starting from the code's diagnostic spectrum

```text
(8 pi nu^3)/(c^3 n_H) Delta f_nu
```

per hydrogen atom per logarithmic frequency, derive the cell measure and the Hubble redshift boundary flux. Keep all Jacobians between eV, Hz and `d ln nu`; identify where `x_1s`, degeneracy and escape compression enter. The resulting finite-volume operator must have the physical photon-number left null vector, not the unit proxy left vector.

### B2.3 Primitive/Schur/direct comparison

On the locked snapshot, compare:

1. direct PR-04A COM–KHW event moments;
2. original-HyRec primitive virtual-state action before Schur elimination;
3. Schur-reduced real-state/escape action;
4. reconstructed physical finite-volume action.

No free multiplicative scale, empirical offset or output-matching correction is allowed.

### B2.4 Hard gates

- source-identical uninstrumented baseline hash;
- dimensional and sign census;
- physical photon-number conservation including redshift/escape boundary flux;
- detailed balance/BE null in the local no-expansion limit;
- photon-plus-atom recoil-energy closure;
- primitive-to-Schur algebraic parity;
- analytic/JVP Jacobian parity;
- positivity-preserving implicit update;
- one full FLRW snapshot residual with a predeclared tolerance;
- Bianchi microphysics firewall at identical local hydrogen-frame state.

## Fail-closed conditions

Keep PR-04 open if the physical bin measure, redshift boundary flux, escape normalization, or source-identical snapshot parity cannot be derived without fitting. Do not substitute HYREC-2 correction tables for the original primitive transfer operator.
