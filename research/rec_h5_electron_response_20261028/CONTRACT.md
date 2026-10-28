# REC-H5-ELECTRON-RESPONSE01 — fixed-point incoming response

## Objective and scope frozen before scientific execution

The current user request is to resume `rec_bianchi`. Its live predecessor,
REC-H5-ELECTRON-FIELD01, has completed science and is receiving its C10
delivery from another active work stream. Reuse that science and do not mutate
its branch. This new unit computes the incoming-radiation response of its
electron point field on a separate branch. The previous task's
`OFF_AFTER_THIS_SELECTED_UNIT` ended that task; the present continuation
authorizes this one successor. Automatic execution of a further unit remains
off. No main merge, canonical count promotion, or REI activation.

Owner: `cosmosapjw-quantum/rec_bianchi`.
Branch: `research/rec-h5-electron-response-20261028`.
Base: `bc9fd57d41dcfc6aaa717bfd7f8e98846d10332e`.
Workflow: physmath-research-loop 1.0.0, R1–R10 and C1–C10.

Source archive: `REC_H5_ELECTRON_FIELD01_C10_20261028_3e841711a381.zip`,
16,076,171 bytes, SHA256
`3e841711a3817dadfb46445ea22bcd1cf9e46aeb52d5270aca86333bd77c6ff2`.
The complete archive was downloaded from its existing Drive object and its
size, SHA256 and ZIP CRC were checked this turn. Its 421 members were recovered.
No old native producer, primary, validation, or history integration is rerun.

The 132 saved primary writer records and nine saved incoming controls are the
inputs. Each record retains index/call_id/slot and the predecessor source SHA.
The physical point restriction is FULL/H_STEADY/He-neutral/xe=xHII/fsR=meR=1,
eta=ln(a), nH in cm^-3, H in s^-1, temperatures in eV. Incoming departures are
signed, with 311 virtual entries followed by Ly0 and Ly1. Preserve metric
(-,+,+,+) and the original physical constants/unit conversions.

## Exact mathematical target

Lift the saved finite binary64 coefficients A, B, Cstored, V, Beta, H, nH,
x1 and Dtau to exact real numbers. Cstored is 2 by 311 and the mathematical
lower-left block is Cstored^T. Let M=[[A,B],[Cstored^T,V]]. The three V arrays
are diagonal, row-indexed lower diagonal and row-indexed upper diagonal.

Define kL as the exact binary64 value of the original source literal
4.662899067555897e15, and kBeta as that of 1.664786871919931. Define theta as
the exact binary64 value of 1e-6. For saved tau>=0, use

    pi(tau) = (1-exp(-tau))/tau                  if tau > theta,
              1-tau/2+tau^2/6                  otherwise.

This preserves the source's branch and its small-tau polynomial. It is an
explicit real reconstruction of coefficients; native omega/RLya intermediary
bits were not saved and are not claimed to have been recovered.

The only nonzero G entries, for u=(u_virtual[0:311],u_Ly0,u_Ly1), are

    G[2+b,b] = V[b,b]*x1*pi(Dtau[b]),
    G[1,311] = 3*kL*H/nH,
    G[0,312] = 3*kL*H/nH*kBeta.

At fixed point and tables, X(u)=M^-1[a+Gu], F(u)=d+q^T X(u),
q=(Beta0/H,Beta1/H,0,...), d=-(c0+c1)/H, with the source real c_i.
Conditionally on exact-real M being invertible,

    M^T lambda=q,  J=G^T lambda,
    F(u+du)-F(u)=J^T du.

The result is the derivative of this defined real coefficient model. It is
not a derivative of the stepwise binary64 rounding map. Exact nonsingularity,
coefficient boxes, inverse-gain bounds and physical tubes remain QSS03/other
provider obligations. Numerical nonzero pivots are reported as diagnostics.

## Numerical design and predeclared acceptance

Use Decimal80 for the new O(311) structured adjoint solve, preserving source
orientation. Reconstruct M^T lambda-q independently by sparse multiplication,
not by replaying the elimination algorithm. Do not assume row diagonal
dominance of V^T. Transpose bands have index shifts:
lT[b]=u[b-1], uT[b]=l[b+1], with zero boundary values.
This structured factorization additionally assumes invertible V and nonzero
exact pivots of its chosen tridiagonal elimination. M invertibility alone is
the condition for the abstract adjoint theorem. The code's nonzero numerical
pivot diagnostics do not replace either exact-real condition.

1. All 132 bindings, finite shapes/domain, source hashes and input nonmutation
   must pass. New native calls must remain zero.
2. Every componentwise normalized adjoint residual must be <=1e-60 at
   precision80; denominator is sum of absolute row products plus |q_i|.
   A zero denominator requires exact-zero numerator.
3. At indices 0,66,131 compare Decimal80 with Decimal120. Require the maximum
   difference in J divided by max(1,max|J120|) to be <=1e-60. Validate an
   independently assembled direct sparse transpose solve in binary64 on these
   three fixtures with scaled max error <=1e-10; its backward residual is
   reported separately. These are numerical checks, not interval guarantees.
4. For each of the nine existing controls, first require bitwise-identical
   A/B/C/V/Beta/H/nH/s/x1/Alpha/DAlpha/Delta and equal point identity. Then
   compare source forcing difference with G du. Require
   ||(S_control-S_base)-Gdu||_1 /
   (||S_control||_1+||S_base||_1+||Gdu||_1) <=512*eps64,
   using an exact-zero rule if the scale vanishes. Record the worst row
   normalized mismatch as a diagnostic. This is a new declared bridge gate,
   distinct from the predecessor's FH parity gate.
5. Compare observed saved DeltaFH with J du using the predecessor's termwise
   absolute scalar scales: |DeltaFH-Jdu| <=512*eps64*(S_F_base+S_F_control).
   Decompose the difference into scalar rounding, source reconstruction,
   primal solve residual and adjoint residual contributions. Require the
   residual of that algebraic decomposition divided by max(1,sum|terms|,
   |DeltaFH-Jdu|) <=1e-60. Report every contribution and retain failed gates.
6. Meaningful negative controls must expose wrong transpose band indexing,
   swapped Lyman-source placement and changed solution. Validation failure
   is retained and repaired by diagnosis; thresholds are not enlarged.

The scientific implementation and its saved-data plotting have a new unit
budget of 60 child CPU seconds total, <=30 wall seconds and 512 MiB address
space per child, single-thread environment. This is a separate allocation,
not transfer/reset of the predecessor's 4.704676/60s or 143/146 calls.
All failures/retries charge this unit's ledger. Parent/network/model/metadata/
packaging costs are UNKNOWN_NOT_ZERO unless measured.

## Interpretation and delivery

Report J entries, the two Lyman contributions, virtual-bin contributions,
and point ||J||_1 values. An infinity-norm incoming perturbation obeys the
conditional exact-model inequality |deltaF|<=||J||_1 ||du||_infinity. The
computed point norm is not a certified physical or whole-domain Lipschitz bound.
Map the result to future radiation-to-electron coupling; a full-state tangent
also needs derivatives of M, G, a, q and d.

Reuse old R6/C9 for old science; obtain fresh independent theory review and
final code/result review for this change. Preserve all old raw results.
Publish a draft successor, a complete reproducible source capsule and report,
with verified provider acknowledgements. Canonical 28/88 +0 and physical
0/313 remain the inherited record; all existing physical nulls and H6/H7
remain unchanged. No central DAG write is needed for this auxiliary response
until its intended recipient is explicitly bound.
