# REC-H5-DEFECT-BOUND01 independent theoretical review

Date: 2026-10-25. Reviewer: atomic scientific authority, independent of the thermal/REC author. Runtime model identity: UNOBSERVED. Scope: conditional analytic derivation only; no scientific runtime, plot, numerical test, new source callback or trajectory was used.

**Decision: PASS_DERIVED_SCOPED.** The corrected source-matched defect → endpoint → interpolation → frozen-response construction is mathematically sufficient under its stated conditional assumptions. Actual REC-H5 physical epsilon, defect/stability/curvature inputs and physical admission remain null/input-dependent.

## Independent derivation

Use a fixed norm on the state space, with fixed component scales when state variables carry different units. For an absolutely continuous exact solution x and continuous piecewise absolutely continuous reconstruction x_h, define e=x_h−x and residual r=x_h'−F(eta,x_h). Where derivatives exist,

    e' = F(eta,x_h) − F(eta,x) + r.

The norm is Lipschitz as a function of e, so its composition with an absolutely continuous e is absolutely continuous. With a nonnegative integrable Lipschitz bound L and ||r||≤d almost everywhere,

    d||e||/deta ≤ L(eta)||e|| + d(eta)  almost everywhere.

For eta≥eta0, the integrating factor gives exactly the proposed Gronwall convolution. It is valid as a conditional enclosure while exact and approximate states remain in the declared tube. A bootstrap/continuation argument must establish the tube inclusion; a sampled trajectory staying in the tube is not that argument. If the physical target has a separately bounded source/model discrepancy b, the forcing envelope becomes d+b in the same norm and clock.

For backward continuation, set eta(s)=eta0+sigma*s, sigma∈{−1,+1}, s≥0. The transformed residual is sigma*r and has the same norm. The valid bound uses positive-orientation integrals in s with L(eta(s)) and d(eta(s)). A negative eta integration interval must not be inserted unchanged into the forward nonnegative forcing convolution.

For a history channel y_j=G_j(eta,x), a state-Lipschitz bound K_j maps the state-norm radius to an absolute channel endpoint radius K_j E. Source/reference discrepancy and representation error enter separately, without counting the same contribution twice. E may be dimensionless in a scaled state norm while the channel radius has the units of y_j. The endpoint symbols e_L/e_R must denote nonnegative upper bounds on absolute channel errors, not signed errors or relative tolerances.

An independent interpolation proof avoids dependence on a shared scalar mean-value point. For q=L+a*h, h=R−L>0, the exact linear interpolation error has the integral form

    y(q)−I[y](q)
      = −(1−a) integral_L^q (s−L)y''(s) ds
        −a integral_q^R (R−s)y''(s) ds.

Therefore, if |y''|≤M2 on the cell,

    |y(q)−I[y](q)| ≤ M2*h²*a*(1−a)/2 ≤ M2*h²/8.

The factor 1/2 and the midpoint 1/8 are correct. Constant/linear functions give zero curvature remainder; y=M2*eta²/2 attains the midpoint bound in absolute value. The integral form also supplies a sufficient weak-derivative version when y' is absolutely continuous and y'' is essentially bounded. A jump in y or y' requires separate treatment; it cannot be hidden inside an L-infinity curvature bound.

Positive endpoint weights give

    |I[y_h](q)−y(q)|
      ≤ (1−a)*e_L + a*e_R + M2*h²*a*(1−a)/2.

At a=0 or1 the curvature term vanishes. These are absolute coordinate bounds. Relative physical-density or temperature tolerances require a separate positive denominator/reference mapping. No such conversion is supplied by interpolation alone.

If extra smoothness is used to construct M2 rather than receive it, the complete derivative of the native channel is required. For smooth G and F along the exact solution,

    y'' = G_etaeta + 2 G_etax F + G_xx[F,F]
          + G_x (F_eta + F_x F).

This includes the source/reference/temperature dependence of G and F. A bound on an unrelated temperature history or on only its explicit eta derivative does not bound a native departure variable. Converting proper-time equations requires F_eta=F_t/H on a domain where H is nonzero, with the actual H and state/source dependencies retained. No proper-time second derivative can be inserted into the eta-cell formula without the corresponding conversion.

Finally, for the already admitted frozen response delta_o=K_s*delta_y, an entrywise enclosure Klo≤K_s≤Khi implies W_ij=max(|Klo_ij|,|Khi_ij|) and

    |delta_o_i| ≤ sum_j W_ij*epsilon_j.

Here j ranges over every represented channel/query coordinate used by K_s. W has output-unit/input-unit and epsilon has the corresponding input units. This deterministic box inequality requires no statistical independence; correlated inputs are still safely enclosed. It may overestimate a correlated set. An error in the nominal output/operator itself, coordinate retiming, source-model error and nonlinear outgoing remainder need their own nonduplicated allocations. The inequality alone certifies only the frozen linear variation it defines.

## Targeted findings

1. The initial note used a pointwise upper-right Dini statement under only piecewise absolute continuity and integrable envelopes. The sufficient minimal statement is an almost-everywhere norm derivative or its integral version, with L locally integrable. Stronger pointwise regularity would be needed for a pointwise Dini assertion.
2. The initial forward formula did not explicitly state eta≥eta0 or a backward orientation rule. The nonnegative forcing convolution needs the orientation described above.
3. Endpoint e_L/e_R and state norm units needed an explicit absolute-radius/fixed-scale convention. This also prevents interpreting a dimensionless scaled-state error as an absolute temperature or native-history error.

The author was asked for this single bounded analytic correction. No change to REC source identity, physical tolerance, runtime budget, frozen historical result or implementation was requested.

## Claim and remaining physical gate

The conditional result connects an actual source-matched differential defect and stability/tube enclosure to native endpoint error, cell interpolation error and the existing frozen response map. It is a useful analytic input contract, not a new general theorem or strong no-go. No H5 physical bound follows until the actual per-query d/L/K/M2, endpoints/reference/representation radii, tube/support and K_s identities are supplied.

PB01 query-coordinate uncertainty is distinct and must be composed once. Existing REFINE01 stored-history differences do not by themselves provide d or M2. KS01's represented-matrix certificate does not by itself provide physical history uncertainty. The original cosmology, eta clock, native departure reference, causal prefix and exact source remain part of the applicability conditions.


## Correction closure and exact reviewed artifact

Final changed-paragraph readback completed on 2026-10-25 for `thermal/REC_H5_DEFECT_BOUND01_DERIVATION.md`, SHA256 `e4dc39a4d142a5baea3458b8a68ca2d68ce7aed0a1537c6160401c646258169b` (author-status text still marked independent admission pending at review time).

All three targeted findings are closed. The revised note explicitly restricts the forward Gronwall convolution to eta>=eta0 and supplies the positive path-length transformation for backward evolution; states the almost-everywhere derivative inequality with nonnegative integrable envelopes; and uses fixed positive dimensional state scales and nonnegative absolute native-channel endpoint radii. The full G/F chain rule, temperature-dependent reference obligation, unit mapping and deterministic outgoing box bound are correct. The interpolation factor a(1-a)/2 and its maximum1/8 are correct. No blocking mathematical finding remains within this conditional scope.

The proper-time-to-eta conversion applies only where H is nonzero so eta is an admissible clock, and all derivative/Lipschitz bounds must hold on the same validated tube and cell. These are applicability conditions, not additional computed evidence. The general weak-derivative alternative is supported by the integral remainder above; the displayed scalar mean-value formula itself uses the note's smooth-case assumption.

This admission closes the independent theoretical review only. Implementation and execution remain NOT_RUN. Physical H5 remains INPUT_DEPENDENT_UNCALIBRATED with epsilon=null. Neither numerical defect/radius/curvature data nor an observable tolerance has been supplied or inferred. No old calculation was rerun, no frozen evidence or source identity was changed, and no cumulative or unknown budget was reset. Subsequent author-status or review-link metadata edits do not broaden this mathematical admission.
