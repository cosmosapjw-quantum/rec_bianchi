# PR-05C2C1B2B1E1A single-COM-macro formalism

## Scope

This stage solves one source-conditioned 35-state by 26-direction COM
collision--frequency-transport backward-Euler subblock.  The v0.73 accepted
parent and red/blue boundary occupations are immutable inputs.  The Bianchi-II
geometry is evaluated at the provider macro endpoint.  Atomic populations,
one-/two-photon/Raman source coefficients and accepted original-HyRec history
are **not** advanced here.

## Physical residual

With ordinary frequency in Hz and metric signature `(-,+,+,+)`,

\[
 R(f)=f-f_n-\Delta t\,[C_{\rm Bose}(f)+L_\nu(f)].
\]

Occupation is dimensionless and both actions have units `s^-1`.

## Gross-event backward error

The net residual is cancellation dominated.  The collision gross scale is the
forward+reverse event-action scale divided by the smallest weighted frequency
mode measure.  The transport gross scale is the sum of absolute adjacent face
fluxes divided by each cell mode measure.  The hard residual gate uses

\[
 \epsilon_{\rm gross}=
 \frac{\|R\|_\infty}{
 \max(\|f_n\|_\infty,\|f\|_\infty,
      \Delta t C_{\rm gross},\Delta t L_{\rm gross})}.
\]

The cancellation-amplified net/state diagnostic remains public.  It may exceed
`1e-11` only when the raw residual is also below a conservative floating-point
bound `128 eps_machine * gross_scale`.

## Number restoration

At the numerical floor, photon number is restored along the common Bose
chemical-activity direction

\[
 \phi_i=\frac{f_i}{z_i(1+f_i)},\qquad
 \phi_i\mapsto e^\delta\phi_i.
\]

The correction is accepted only when it is below `1e-8` pointwise and closes the
independent number ledger.  It is an internal conservation restoration, not a
fit to external data and not a free thermodynamic normalization.

## Result and claim boundary

Gross backward error: `3.19245327058447485e-17`.
Photon-number residual: `1.40797926116813230e-16`.
Energy gross backward error: `3.65397550639948559e-19`.
Net/state residual diagnostic: `7.00446583458104169e-06`.

This is a roundoff-limited COM subblock root.  It is **not** a full atomic,
native-history or exactly-once-history-commit macro endpoint.
