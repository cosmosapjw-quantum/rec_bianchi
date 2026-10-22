# ANGULAR01 — local Bianchi escape moments

**Completed scoped theory, sandbox implementation, finite study and independent
review.** One 405-point angular study, 89 standalone checks and one independent
seven-point numerical audit are retained. New cosmological IVPs: **0**;
historical campaign reruns: **0**.

For a supplied, fixed isotropic line source and positive expansion in every
direction, the finite-depth mean Sobolev escape probability obeys
`B <= beta_iso`. In the thick limit its mean reduces to `1/t`, while the
probability PSTF moment remains `Q = 2 S/(15 t)`. The analytic truncation bound
controls the AUTO switch at `t/qmax >= 18.420680753952364` for epsilon `1e-8`.
This Q is not a physical photon stress tensor.

The new implementation reuses the exact PR114 directional-spike donor and its
MIT license under `vendor/`. The study observed a maximum mean-probability
suppression of **19.5221%** on its finite grid; this is not an electron-history
or total-recombination-rate result. AUTO chose the analytic branch at **61/405**
points. No wall-time speedup is inferred from that branch count.

## Read the result

- [Korean research report](REPORT_KO.md), [complete derivation](THEORY.md), and
  [frozen pre-execution contract](FROZEN_CONTRACT.md).
- [Kernel](code/escape_moments.py) and [reuse/execution record](RUN_COMMANDS.md).
- [Original study result](results/attempt_001/study_summary.json) and
  [final saved-data decision](results/attempt_001/FINAL_DECISION.json).
- [Independent review](evidence/independent_review/REVIEW.md):
  `PASS_AFTER_TARGETED_REPAIRS`, zero open findings.
- [Physical suppression](figures/attempt_001/physical_bounds.png),
  [surviving tensor](figures/attempt_001/surviving_tensor.png), and
  [AUTO domain](figures/attempt_001/branch_map.png). PDF companions and exact
  plotted CSVs are included with a per-figure provenance manifest.
- [Local DAG](DAG.json), [whole-goal DAG](GLOBAL_DAG.json), and
  [copyable next-thread handoff](HANDOFF_KO.md).

## Preserve the actual failure history

The original study exited 1 with 400/405 accepted rows. Five thin isotropic
rows failed a numerically ill-conditioned inequality validator. An algebraically
equivalent `expm1` expression with the same frozen slack re-adjudicated only
those five saved rows; the other 400 passes were reused. Final acceptance is
405/405. The original FAIL, raw arrays, logs, pre-repair code and targeted repair
records remain unchanged. The full study was never rerun.

Three boundary defects were repaired before the study. One finite-depth LRS
wording error and one figure-layout issue were also corrected within the same
independent review. The review inspected all final PNGs and rendered PDFs.

## Stages and delivery

Stage A source/theory/contract and Stage B numerical artifacts were separately
committed and backed up to Dropbox and Drive. Their actual Git and provider
receipts are under `delivery/`. This Stage C commit closes the scientific,
review and handoff artifacts. Its post-publication Git and backup receipts live
in the final archive and PR127, avoiding self-referential commit hashes.

PR: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/127

Full provider inventory metadata is retained in the owner's complete archive.
Repository provenance contains the scientific synthesis and explicitly states
the inaccessible-conversation and capped-Drive coverage gaps.

## Continuing the physics

The next selected obligation is a source-owned resolved line's population,
Einstein/degeneracy and number/energy ledger, connected to the escape moments
without duplicating HyRec's compressed Tvv, feedback or diffusion owners.
Li ionic yield, spectral recoil/induced sources, nuclear daughter inputs and
coupled thermal/radiation/metric evolution remain separate open obligations.

Physical **HOLD**; REC U5 **HOLD_9_FAIL/HOLD_8_FAIL**;
**CLOSED_HOLD_NOT_RESET**; global convergence **NOT_RUN**;
production **NOT_APPROVED**; **REI_activation=false**.
The first failed REI raw remains historically local-only.
