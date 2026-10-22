# ANGULAR01 independent review

**Decision: PASS_AFTER_TARGETED_REPAIRS for the frozen local research unit.**
There are no open BLOCK_NOW or FIX_SOON findings. This decision covers the
supplied-source local operator, the finite study and its data-bound figures.
Physical/REC holds, global convergence NOT_RUN, production NOT_APPROVED and
REI_activation=false remain unchanged.

This is the one delegated fresh review pass for the selected R6/C9 work. The
reviewer is `/root/angular01_review`; no subreviewer was created. The 405-point
production study and historical campaigns are not executed by this review.

## Scope and checks completed

The reviewer actually read physmath-research-loop 1.3.0 `SKILL.md`,
`STAGE_SELECTION.md`, and `references/{SUBAGENT_MODE,POLICY_INTEGRATION,THEORY_LOOP,CODING_LOOP}.md`
at `/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop/`.
Only the supplied R6 scientific audit and C9 implementation audit are selected.
The applicable rules are one fresh pass, concrete findings, selective repair
checks, retained failed evidence, typed identity and no promotion of held claims.

The sign of directional redshift follows directly from the supplied Bianchi-I
energy and conserved momenta. The coefficient has units s^-1 and its ratio to
the directional expansion is dimensionless. The isotropic average, fourth
moment, scalar variance, PSTF normalization, concavity, clipped curvature
maximum, thick errors and actual-mean-normalized switching criterion agree
with independent algebra. The finite-depth formula is conditional on a fixed
isotropic source, positive directional expansion and the supplied local
Sobolev model; no conclusion about the full recombination history follows.

Primary-source locations read directly during review:

- [HyRec-2](https://arxiv.org/pdf/2007.14114), Section III.A, Eq. (10): the
  hydrogen limiting rate and the approximations under which it is used.
- [Chluba–Sunyaev](https://arxiv.org/pdf/0810.1045), Section 3.2.2, Eq. (35b):
  the supplied Sobolev probability.
- [Hirata–Forbes](https://arxiv.org/pdf/0903.4925), introduction, p. 2:
  matching profiles, complete redistribution, an isolated line and
  quasi-stationarity. These are physical assumptions rather than consequences
  of a large optical depth.

The vendored donor and license SHA256 values match the frozen manifest.
The supplied claims do not introduce a strong no-go or an exhaustive novelty
claim. Existing Physical/REC holds and REI inactivity remain unchanged.

## Findings in this one repair episode

1. **FIX_SOON, CLOSED_FIXED — finite-depth normalized LRS amplitude.** The
   original prose assigned `5<P2 p>=s` to `p=b/B` without a thick qualifier.
   At finite depth its leading coefficient is
   `[1-(1+t)exp(-t)]/[1-exp(-t)]`, which is about 0.418 at `t=1`.
   The parent repaired the text to use `p_thick=q` and supplied the finite-depth
   coefficient separately. The changed paragraph was read and confirmed.
2. **FIX_SOON, CLOSED_FIXED — overflow in the thick tensor.** For valid `t=1e308`,
   `S=diag(-0.4,-0.2,0.6)`, `2*S/(15*t)` returns zero because `15*t` overflows.
   The normalized tensor discrepancy is 0.09977753031397177. Evaluate the
   prefactor before dividing by `t`. The targeted recheck gives a normalized
   residual of 3.0054303251241967e-16.
3. **FIX_SOON, CLOSED_FIXED — false exact-zero Jensen label.** The nonzero tensor
   `1e-200*diag(-0.4,-0.2,0.6)` is called `EXACT_ZERO_SHEAR` after its squared
   norm underflows. Check the tensor itself for zero and evaluate its squared
   norm through a scale and logarithm. The recheck returns `UNDERFLOW_USE_LOG`
   with finite `log_bound=-925.3219058939734`.
4. **FIX_SOON, CLOSED_FIXED — complex LRS axis accepted.** A complex ndarray axis
   `[0,0,1+2j]` is cast to real with a warning and used by the quadrature.
   Reject complex axes before conversion. The recheck raises `ValueError`
   before casting, with no warning.
5. **FIX_SOON, CLOSED_FIXED — ill-conditioned thin isotropic validator.** The
   one production study initially returned FAIL: 400/405 grid points passed,
   and the remaining five failed only `thick_scalar_upper`. Its comparison
   subtracted quantities of order `1/t` at an exact isotropic equality. The
   root and reviewer independently read the same saved failures. The repaired
   test uses the exactly equivalent `B+slack >= -expm1(-t/qmax)/t`, retaining
   `slack=2e-12*beta_iso(t)`. Exactly five saved rows were re-adjudicated;
   there was no new angular computation. Their recorded inputs, stable lower
   bounds and unchanged slack agree with the original data. The original
   FAIL, raw CSV, JSON checks and log remain preserved.
6. **FIX_SOON, CLOSED_FIXED — branch-map footer overlap.** Actual PNG and
   rendered PDF inspection found the footer crossing the x-axis label. The
   author reserved the bottom 12% of the layout and re-rendered only the
   branch-map PNG/PDF from the unchanged CSV. Both revised outputs were viewed
   and the overlap is resolved. The original images and renderer are retained
   under `evidence/plot_layout_repair_001/`.

Findings 2–4 were reproduced in one 0.442-second command, exit 0. It made one
4-node invalid-axis quadrature call, one analytic-thick call and no IVP. These
inputs are outside the 405-point measured grid but inside the public input
surface; they do not require rerunning that study. The failed observations are
retained in `REVIEW.json`. No further unbounded input exploration is planned.
The initial inline defect probe did not capture a whole-file hash at execution;
its relevant defective expressions are preserved in the author's pre-repair
source snapshot. The final kernel and subsequent checks have explicit byte
identities. No whole-file byte identity is inferred for that initial probe.

## Independent spot result

The prepared audit ran once: `python evidence/independent_review/spot_audit.py`,
exit 0, 1.2232319659960922 seconds, peak RSS 56568 KiB. Its seven off-grid
angular parameter points cover isotropic, weak/large LRS, thin triaxial,
near-positive-domain-boundary, and both sides of the analytic switch. A
separately written full-sphere rule with 192 Gauss-Legendre nodes and 384
staggered azimuth nodes was integrated directly in the lab frame. All seven
comparisons passed. The maximum scalar relative difference was
8.546625236534993e-10 and the maximum tensor Frobenius difference divided by
the independently evaluated mean was 5.751586131176496e-10. Both occur just
above the thick switch and are below the frozen 1e-8 target. Away from that
switch the observed differences are at the 1e-14 level or below.

The three diagnosed implementation defects passed selective rechecks in the
same command. The original failures remain above and in the JSON evidence.
The kernel SHA256 for this check is
`f8a91ddad8833d4c0079025af81fb8df4b9423da3d87a8363093603922da0c2e`.

Reviewer quadrature budget: eight distinct angular parameter points including
the original invalid-axis probe; seven independent-reference calls (516096
nodes), seven tested-kernel quadrature calls (49156 nodes, including the
original four-node invalid probe). These counts are separate from the 405-point
study and its standalone checks. There were zero production-study reruns,
historical campaign runs or cosmological IVPs.

## Production evidence and saved-data acceptance

The full study ran exactly once: 405 parameter points, 1.7181813220086042
seconds, peak RSS 32.49609375 MiB, with the observed OpenBLAS thread count equal
to one. Its 20 donor comparisons, nine rotation parameter cases and four
weak-shear parameter cases belong to separately recorded standalone checks.
All 89 standalone checks passed on that initial run.

The reviewer read all 405 saved rows, their per-row flags, source identities,
execution request, log and standalone records. The nine files in the original
study manifest match their recorded byte sizes and SHA256 values. Every
spectrum has 45 unique points, and the complete index set is 0 through 404.
There are no saved structural violations, row-flag inconsistencies or summary
maximum discrepancies.

| Saved measurement | Largest observed normalized difference |
|---|---:|
| General B, N=64 versus N=128 | 3.706925453614504e-15 |
| General Q Frobenius, N=64 versus N=128 | 8.74551428676363e-15 |
| LRS 1D versus general 2D B | 2.168404344971009e-15 |
| LRS 1D versus general 2D Q Frobenius | 6.026472479737714e-15 |
| AUTO B versus reference quadrature | 7.080418540979247e-10 |
| AUTO Q Frobenius versus reference quadrature | 4.77376883227185e-10 |
| Rotated principal-frame Q versus lab-frame oracle | 8.61622756874271e-15 |

The first six measurements are normalized by the frozen `beta_iso(t)`.
They are finite observations; they do not constitute a quadrature interval
certificate or global cosmological convergence. The scalar donor comparison
has a recorded maximum relative difference of zero for the specified 20
comparisons. The weak-shear odd central-difference tensor coefficient has
maximum Frobenius discrepancy 8.582068464034813e-9, within its fixed 1e-6 bound.

The original failure indices are exactly 1, 4, 5, 14 and 16, all thin isotropic
cases. For positive `t`,

\[
\frac1t-B\le\frac{e^{-t/q_{\max}}}{t}+\delta
\quad\Longleftrightarrow\quad
B+\delta\ge\frac{-\operatorname{expm1}(-t/q_{\max})}{t}.
\]

This transforms only the floating representation of the comparison. The
recorded five stable residuals are positive, between 1.11e-16 and 2.22e-16;
the fixed slack remains about 2e-12. Thus `FINAL_DECISION.json` correctly
combines the unchanged 400 passes with five corrected validator decisions to
accept 405 points, while retaining the original summary status FAIL. Its raw
grid, original summary, final kernel and corrected validator hash bindings
were verified. No physical formula, tolerance or saved numeric value changed.

## Physical interpretation and figure review

The measured grid selects the analytic thick branch at 61 points and finite
quadrature at 344. This is a count of branch selections on this fixed grid,
not an end-to-end speed benchmark. The largest saved scalar suppression is
0.1952210196474612 at LRS `s=1.8`, `t=1`. The normalized quadrupole approaches
`(2/15)||S||_F`; the largest saved value is 0.29393876913398775 for that LRS
spectrum in the thick regime. These values describe the chosen local
probability model and its supplied source, not a measured cosmological shear
or a change in a self-consistent recombination history.

All three final PNGs and the actual Poppler-rendered single-page PDFs were
inspected. The scalar-suppression and surviving-tensor figures passed their
first visual inspection. The branch-map layout required the one targeted
repair described above; its revised PNG and revised PDF render now pass.
The axes, signs, normalization `5<P2 beta>/B=7.5 Qzz/B`, asymptotic amplitudes,
AUTO threshold and legend meanings agree with the equations and saved data.
The scalar comparison's floating residual plateau near 1e-15 is distinguished
from the analytic truncation bound; it does not refute that bound.

Each of the three plotted CSVs contains 405 rows. Their plotted quantities
were compared with the corresponding raw rows: no mapping/value mismatch was
found. All nine final plotted-data and figure files match their manifest
sizes and hashes. The changed branch-map renderer is separately attributed;
the other two figures and all CSVs retain their original identities.

Key final identities:

| Object | SHA256 |
|---|---|
| Frozen contract | `ced4e9cdbb680780e554abe374fc9e980b088d76b743765b0286fe65e3c29c62` |
| Final angular kernel | `f8a91ddad8833d4c0079025af81fb8df4b9423da3d87a8363093603922da0c2e` |
| Original raw grid | `0800d306eb3d4a07f7b2143e6e451860fc416a32f491df424d635a49c949675f` |
| Original FAIL summary | `358aaec055e89bd79dc0b1e68d350d91aadb169d615f6113323ab365aee079c6` |
| Final saved-data decision | `54b8a1348aad7563b726efaac05eeae6f747f3761355fe6fc732fea1615c957d` |
| Final plot manifest | `7109feebaf0a938b4e5d2cee43fd6a2a781363d35e84baee6da38838739745a0` |

## Closeout

R6/C9 is complete for this bounded objective. The fresh reviewer performed one
pass and one coherent repair episode; no subreviewers or review-of-review were
created. All six actual findings are closed. The parent may package and
publish these reviewed local artifacts. External Git publication, backup
acknowledgements and whole-byte remote readback remain parent-owned actions.

Result validity, source provenance and local figure packaging pass within the
scope above. Physical HOLD, REC U5 HOLD_9_FAIL/HOLD_8_FAIL,
CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED,
REI_activation=false and the historical REI first-failure raw local-only rule
remain unchanged. No further numerical experiment or repeated review is
required for this unit.
