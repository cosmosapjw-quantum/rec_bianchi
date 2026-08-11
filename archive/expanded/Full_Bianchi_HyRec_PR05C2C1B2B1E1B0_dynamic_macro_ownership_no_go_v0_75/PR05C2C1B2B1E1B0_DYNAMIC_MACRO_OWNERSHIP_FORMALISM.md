# PR-05C2C1B2B1E1B0 dynamic-macro ownership formalism

## Scope and conventions

The metric signature is `(-,+,+,+)`.  Photon frequency is ordinary frequency
in Hz; the original-HyRec virtual registry is stored in eV and converted to the
hydrogen-frame Doppler coordinate

\[
x_b=\frac{E_b-E_{\rm Ly\alpha}}{\Delta E_D}.
\]

The COM collision domain is the fixed interior interval \(|x|\le 21.25\).
Original-HyRec virtual states are zero-width point spikes.  No finite native
cell boundaries are inferred.

## Ownership obstruction

At the locked \(z\simeq1100\) snapshot, eight canonical virtual spikes lie in
the COM interior.  The full original-HyRec block contains adjacent Ly-alpha
diffusion edges, real-to-virtual and virtual-to-real source couplings, and the
completed real/virtual algebra on those same frequencies.  The v0.74 COM--KHW
operator already owns nonlinear stimulated redistribution on the interior.
Therefore the naive full residual

\[
R_{\rm naive}=R_{\rm native}^{\rm full}+R_{\rm COM}^{\rm interior}
+R_{\rm atomic}^{\rm full}
\]

has duplicate physical owners.

A mathematically admissible target contract has the form

\[
R=R_{\rm native}^{\rm exterior}
 +R_{\rm COM}^{\rm interior}
 +R_{\rm interface}^{\rm cross}
 +R_{\rm atomic}^{\rm ext/int},
\]

where the two cross-interface diffusion edges are evaluated exactly once by the
interface owner, the interior atomic source is deposited into the COM
representation, and the completed native algebra is replaced by an exterior
Schur block.  This is a contract witness, not an implementation claim.

## Completion rule

The native/COM owner swap is complete only when the replacement residual,
analytic JVP, photon-number and photon/atom energy ledger, four-force ownership,
restart state, and source parity are present in the same durable stage.  Until
then full dynamic atomic/native/COM macro construction fails closed.
