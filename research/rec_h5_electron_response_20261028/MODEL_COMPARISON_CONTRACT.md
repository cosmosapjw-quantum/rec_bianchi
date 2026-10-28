# Additive source-prefix model after the preserved real-model bridge failure

## Observed result and reason for the additional model

The original CONTRACT.md remains unchanged. C7 computed all 132 real-model
adjoints. C8_attempt001 passed the 80/120 precision, independent SciPy adjoint,
primal directional, scalar-response and algebraic difference checks. Its
declared source-forcing bridge passed 2/9 and failed 7/9 at the unchanged
512 eps64 criterion. The maximum normalized discrepancy was
2.50906774683485999e-13 versus 1.13686837721616030e-13. The largest individual
row discrepancy was 1.30476552792546896e-11. These results remain immutable.

The native source forms 1-exp(-tau) and then 1-(1-Pi) in binary64. This
provides a concrete numerical mechanism to test. The original exact-exp real
reconstruction mixes saved native M with a newly reconstructed Pi; the failed
bridge belongs to that declared model, not to the mathematical adjoint proof.

## New model, defined before its execution

Reconstruct the original binary64 coefficient *prefixes* from the saved
inputs, preserving the source operation order. Denote lift64 by L and a
binary64 rounded operation by fl. No intermediate bit identity is assumed.

    omega64(tau) = fl(1-fl(fl(1-exp64(-tau))/tau))  if tau>theta64,
                   fl(fl(tau/2)-fl(fl(tau*tau)/6)) otherwise.
    a_b64 = fl(Vbb*x1)
    pi_b64 = fl(1-omega64(tau_b))
    Gprefix[2+b,b] = L(a_b64)*L(pi_b64).

The final product of the two lifts is an exact-real definition; there is no
extra binary64 multiplication between them. For the two Lyman columns,

    RLya64 = fl(fl(fl(kL64*H64)/nH64)/x164)
    g_alpha64 = fl(fl(3*RLya64)*x164)
    g_beta64 = fl(g_alpha64*kBeta64)
    Gprefix[1,311] = L(g_alpha64)
    Gprefix[0,312] = L(g_beta64).

All other M,q,a,d inputs have the same meaning as the original model. Hence
the adjoint lambda is unchanged, Jprefix=Gprefix^T lambda and

    Jprefix-Jreal=(Gprefix-Greal)^T lambda.

The new primary response reuses the saved C7 adjoints. There is no repeat
native point call or repeated 132-point adjoint solve. The old model output
and its failed source bridge remain available beside the new result.

## Validation frozen before the new run

Reconstruct sv via fl(fl(a_b64*u_b64)*pi_b64), and sr via the native c_i
grouping plus its Lyman prefix product. Require **bitwise equality of every
source entry for all 132 primary and all 9 control records**, with fixed
P/M/table/source identity checked. Failures are retained, not erased by
switching a math library or relaxing tolerances.

This observed output equality supports this host's source-prefix reconstruction
on those stored records. It does not prove the identity of unrecorded native
intermediates or portability of exp64 to another libm.

Apply the unchanged 512 eps64 source bridge, 512 eps64 scalar bridge, 1e-60
difference-identity criterion, 1e-60 80/120 precision check and 1e-10 independent
SciPy comparisons to this additional model. Direct primal checks now use its
G. Reuse the all-132 adjoint residual evidence because M and q are unchanged.

For the original worst rows record tau, exact-model Pi, native-reconstructed
Pi, a cancellation-resistant -expm1(-tau)/tau comparison, and source mismatch.
Do not patch the production HyRec source in this unit. Both thin-inner and
thick-outer subtraction effects must be considered when interpreting the
diagnostic. Keep the original model's gate failure separate from the new
model's result.

The resource ledger remains cumulative for this same response unit; the
failed C8 attempt is charged. No budget reset or native calls are allowed.
Scientific ceilings and the separate QSS03 obligations are unchanged.
