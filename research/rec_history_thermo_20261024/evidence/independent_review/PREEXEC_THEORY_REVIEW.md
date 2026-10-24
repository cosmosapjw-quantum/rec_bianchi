# Independent review: theory and source mapping

Reviewer task: `/root/thermo_independent_review`. Requested Astra/high;
actual runtime model identity is not observed. This reviewer has not implemented
the source and has performed no numerical probe, solve, native execution, IVP,
or replay. Root owns execution permission and final scientific admission.

## Materials read

- THEORY.md and FROZEN_CONTRACT.md, version 1, in full.
- Central operating policy readback, blob
  `429a5a13ee75b1222bc50627f8d5973d01dd21c4`.
- Original `intake/rec/ROOT_HYDROGEN_SOURCE.c`, including effective-rate
  interpolation, diffusion, source population, outgoing evaluation and
  characteristic input construction.
- Original `hydrogen.h`, target CSV metadata, and relevant implementations in
  `primitive_rates.py`, `full_2012_atomic_source.py`, and
  `hyrec_two_photon_raman.py`.

## Independent equation check

Differentiating `M X=s` gives `M X_k=s_k-M_k X` with the negative coefficient
term. The outgoing derivative consequently includes both the solution
derivative and direct transfer-coefficient derivatives. The prescribed fixed
incoming Wien departures imply no history-query derivative in this unit.

Native `nH*(s*x1s*DAlpha + Alpha*(xe*xHII-s*x1s))` expands to
`nH*Alpha*xe*xHII-S*Alpha_eq*x1s`. This verifies the contract's `C_l` and its
electron, ionization-fraction and density columns. Differentiating the native
ionization source divided by H gives the explicit `-F*dlnH` term. For the
proper-second source H F this term cancels against the product derivative.

The interpolation coordinate change `r=TM/TR` gives `dA/dlnTM=r*A_r` and
`dA/dlnTR|TM=A_logTR-r*A_r`. The equilibrium Alpha table row has no independent
TM dependence. Native Beta contributes the additional logarithmic factor
`3/2+EI/(4TR)` and S contributes `3/2+EI/TR`.

The native C forms Gamma before inserting the two line-center diffusion
couplings. Matrix assembly must preserve this order. The displayed optical
depth, escape map, diffusion detailed-balance and line-escape derivatives are
consistent with the original source. The two-photon absolute-value signs are
fixed by energy ordering and positive TR, making analytic continuation within
each branch well defined.

There is no xe dependence in M. Common changes dlnnH=dlnH preserve all matrix
coefficients at fixed xHII and temperatures; only the recombination terms in
the two real sources vary. On the pure-H face the physical fraction column is
the sum of xe and xHII columns, not either ambient column separately.

Native outgoing line rows are xr2p/(3*x1s) for Lyalpha and
xr2s/x1s*exp(-E32/TR), xr2s/x1s*exp(-E42/TR) for Lybeta and Lygamma. For the
single Lyalpha event, `R_gamma=3e6*LYA_FACT*H*(o_alpha-u_alpha)` has the extra
H product term specified in the theory; fixed atomic energy gives opposite
radiation/atom energy derivatives. This is a scalar local event convention.

## Numerical implementation issue to resolve in code review

The literal complex expression `1-(1-exp(-z))/z` is an unreliable derivative
oracle near the native tau=1e-6 switch. Cancellation in its imaginary part
can amplify binary64 rounding approximately as epsilon/tau^2, despite a small
complex step. Thus a comparison to a stable analytic p-prime may false-fail
the frozen 2e-8 criterion. A stable complex analytic representation with an
explicitly documented baseline-value anchoring convention is a possible
targeted implementation; simply widening the criterion is not recommended.
This is a concrete implementation review target, not a request for additional
science or a numerical failure already observed. Root subsequently proposed
the cleaner resolution: separate literal-native reconstruction parity from a
consistently stable real-source base used by tangent, complex step, and finite
differences. The reviewer endorsed this before execution. Both native small
branch polynomials must remain unchanged; only the large-branch arithmetic is
stabilized. Such a preexecution clarification requires no relaxed tolerance.

## Preliminary decision

No material theory/source-mapping flaw found. Static implementation review is
pending the prepared code. H5 independent history epsilon, reference error,
and curvature remain absent; the full coupled H7 Jacobian remains open. No
physical, interval, history, global-convergence or production admission is
made by this review.
