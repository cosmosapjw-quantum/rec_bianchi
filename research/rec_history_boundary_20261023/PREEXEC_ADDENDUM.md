# Pre-execution precision and domain addendum

This addendum precedes implementation and all new scientific executions. It
closes the four concrete pre-review findings without relaxing a tolerance or
changing inherited acceptance. The original FROZEN_CONTRACT bytes are retained.

1. The 313-link oracle uses the exact native arithmetic
   `eta_query=-log((1+z_face)*E_source/E_target)`, and eta0 from the same zstart.
   `incoming_history` accepts optional `z_face` and checks its compatibility with
   eta_face. Without z_face it uses exp(-eta_face) as the defined inverse scale.
   Query values are recorded. The mathematically equivalent subtraction form
   can have amplified clock roundoff and is not silently compared at 64eps.
2. `interpolation_jvp` rejects nonzero query tangents at a knot with
   NONSMOOTH_QUERY. Values-only tangents remain defined. This API exposes a
   fixed-cell derivative, not a two-sided derivative through a slope jump.
3. `boundary_jvp` and `line_ledger` accept optional reference_occupation=0 and
   pass it to physical admission. Valid negative departures with nonnegative
   absolute occupations are preserved. The algebraic FrozenHistoryMap permits
   complex directions for derivative checks; it does not certify admissibility
   of a changed physical history.
4. Nonfinite transformed depth tau/q and tangent intermediates are rejected
   explicitly. Underflow of exp(-tau/q) at finite depth keeps its finite logarithm.
5. Within the three preallocated full-system history directions, two use the
   native thick map and one uses finite tau=2. The finite direction verifies the
   corresponding original Lyalpha diagonal/source-pair replacement together with
   outgoing replacement. Total dense RHS solves stay <=8. No additional case
   budget, campaign, preparation run, or independent review is introduced.
6. The C oracle header is the exact retained h4 hyrec_params.h (DLNA=8.49e-5/4)
   used only for manufactured interpolation/routing inputs. The saved z~1100
   thermodynamic state supplies no history clock; its spacing is never inferred
   from that unrelated h4 header.

Pre-review: /root/independent_review, PRE_REVIEW.md; constructive implementation
and independent harness remain separately authored. Numerical executions before
this addendum: zero.
