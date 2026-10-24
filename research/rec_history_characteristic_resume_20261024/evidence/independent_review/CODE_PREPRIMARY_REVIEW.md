# Same independent review pass: actual code before primary

## Authorized preexecution correction checked

Read-only inspection confirms the executor now computes `deta_s=deta_t-dd`, includes deta_s in `finite(dd,dns,dqt,deta_s)`, and returns that checked value. This closes the static guard finding with the exact requested minimal correction. Root reports corrected adapter SHA256 82d67ca3858dab586fd81457eb3b86d157e8bbe5fda55742a92c2402d7b75008 and preserved original source/correction receipt. The numerical P1 regression remains pending; no run was implied by this inspection. **GO_PRIMARY and GO_S1_DRAFT_PUBLICATION** for the fixed unit, with static/syntax claims only until raw results exist.

Decision: **GO_PRIMARY for the frozen 127-case finite unit**. Static equations and primary/oracle structure are consistent with the contract. Scientific numerical admission remains pending. Draft S1 publication may describe implementation and syntax status; apply the small guard correction below before freezing its final source identity.

Read all six actual code files, IMPLEMENTATION_READY.md and SYNTAX_AND_CASE_PLAN.json. The supplied case-plan identity is bb4320162f04a894bcaedf6e59d1828b07ed1a73d4a91ad2859156fab5f9ea28. This review executed no numerical science and did not modify production code.

## Concrete finding: transformed source-time tangent guard

`crossing_jvp` checks dd, dns and dqt for finiteness, then returns `deta_t-dd` without checking the result. With the FLRW x-axis base at Lambda=1, `dlam=-1e308`, `deta_t=1e308`, and other tangents zero, the algebraic dd is finite -1e308, but deta_s overflows. This violates the explicit rejection of nonfinite transformed tangents. The frozen primary inputs do not reach this case, so it does not block that bounded execution. The minimal correction is to compute deta_s once, include it in the existing finite check and return the checked value. Controller authorizes the coding executor's correction; this reviewer does not silently implement it. Exact regression is probe P1 in the proposed plan.

## Actual code assessment

The crossing uses nonzero-component log weights and a bracketed Newton/bisection step. Axis, FLRW and zero-Lambda value branches feed the same general tangent, including tangent amplification at zero direction components. Native-Wien evaluation uses log transformed x and signed expm1 differences. The source field supplies its data/time derivative through vendor interpolation_jvp and its angular derivative through the projected characteristic tangent. Prefix guards precede the legacy interpolation. The composed boundary and ledger use q_t; the implicit root uses q_s.

The independent reference imports neither adapter nor vendor and uses 80-digit direct equations, bisection and fixed 1e-25 central differences. Its binary-input normalization differs from machine normalization only at the admitted roundoff level. Its cutoff x>1e10 for occupation evaluation lies vastly below the declared numerical floor and is explicitly documented. The primary preserves per-row raw output, records first failure and stops. The actual-data path verifies the fixed NPZ hash and uses eight scalar interior queries, with uncertainty left missing. The deliberate photon-clock defect is assessed by clock/stencil identity rather than falsely demanding a unit-scaled amplitude failure.

Conditional envelopes use the analytic field with globally valid K_eta=.03 and K_n=.02 and supplied perturbation/error terms. These are finite containment controls; no actual history curvature is inferred. The controller establishes thread environment before numerical imports, applies CPU/address-space limits in the single child and kills its process group on the wall deadline. It records postexit child usage and source snapshots; no live aggregate monitor is claimed. Root remains responsible for cumulative accounting between invocations.

Saved-row rendering reads primary rows and summary only. Actual visual review is still pending and will be performed on both PNGs, not inferred from plotting source.

## Transition and ceilings

After the targeted guard correction and updated source identity, freeze S1 and execute the original primary with its original thresholds. This is the same review pass, not a new review chain. All physical/global holds and missing-input statuses in PRECODE_REVIEW.md remain unchanged. No primary or reviewer numerical result is asserted here.
