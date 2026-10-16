# R3h phase 2: nine-bin binary64 diagnostic, adversarial sandbox tests

Upstream authority: R3g PR #99 HEAD `e6596cf6083c0a1f28a26700170c971a20244d23`, historical repair audit `research/rec_r3g_primordial_20261016/thermal_transition_001/ROUNDOFF_AUDIT_REPAIR_001.json` (Git blob `09732201ed91c017043ac0a330dde7177c7b9b4d`). Original October-2012 HyRec ZIP SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.

## Independently executed sandbox

A standalone stdlib `decimal` precision-80 nine-bin verifier reproduces `phi(t)=1-(1-exp(-t))/t` for each owner's stored binary64 tau and evaluates the shadow `A80=f_in+phi80*Q`. It then independently constructs the finite-precision error budget with `u=2^-53`: `epsilon_phi<=u/tau+4u`, and `epsilon_A<=sum(|Q|epsilon_phi)+32u sum(|f_in|+|phi64 Q|)`. All nine saved cross-history rows are checked against *their own frozen original tolerance*, their literal legacy failure, and the new propagated budget. No source C or Python actual trajectory was rerun in phase 2. Input is a strictly bounded nine-row numeric fixture transcribed from GitHub R3g audit (not mislabelled as raw original audit). Executable also accepts the full original audit JSON on a real checkout.

**Actual status:** 9/9 new `PASS_NINE_IEEE_EXPLAINED`; original U5 stays `HOLD_ORIGINAL_TOLERANCE_NOT_MET` with raw failures 9/2,290,204. Worst raw/original tolerance ratio **32.65320690729941**, while worst independently reconstructed 80-digit shadow/original tolerance ratio **4.193090430596967e-05**. This is scientific diagnosis of legacy cancellation, NOT a pass of the old exact arithmetic contract.

**Adversarial tests (actual Python unittest):** six PASS, including 20x deliberately corrupted legacy raw difference correctly rejected, corrupted phi64 correctly rejected, immutable source ID mismatch rejected, unexpected coordinate rejected, fake original PASS rejected and all nine correctly admitted only as a separate diagnostic. No native subagent tools exposed, so `native_subagent=NOT_RUN`.

## Durable per-stage backups

- Complete runnable source, bounded nine-row fixture, result JSON and six-test module in `REC_R3H_P2_IEEE_SHADOW_SANDBOX_20261016.zip`, **8,317 bytes**.
- SHA-256 `a4a966eb346abd9a29e1933612780d91e1f1ccb665e1dad555d1f1cd40f936be`.
- Independently materialized both after upload and hashed exact bytes on 2026-10-16:
  - Library `/rec_bianchi_recovery/R3H_20261016/REC_R3H_P2_IEEE_SHADOW_SANDBOX_20261016.zip`
  - Google Drive `/Google Drive/rec_bianchi_research_backups/20261016/R3H_U5_IEEE_P2/REC_R3H_P2_IEEE_SHADOW_SANDBOX_20261016.zip`.
- Dropbox backup not executed by this runtime. Existing R3g Dropbox source archives immutable.

## Live DAG at phase-2 exit

| Node | Status | Backups / publication | Next |
| --- | --- | --- | --- |
| P1 original source & analytic mechanism | DERIVED / VERIFIED | GitHub branch doc + Drive Docs readback | closed |
| P2 IEEE shadow 9-sample test | SCOPED_NUMERIC_PASS, old U5 HOLD | runnable ZIP verified on Library + Google Drive, this GitHub record | closed |
| P3 actual source-only C h,h/2,h/4 numerical reference | IN_PROGRESS | local sandbox h,h/2 control produced, not yet admitted or published | finish h/4 and inspect step convergence |
| P4 independent Python temporal refinement | NOT_RUN | no numerical claim | Codex next scientific full solver job |

**Important:** P2 does not establish temporal convergence, source exact-byte identity for non-default DLNA variants, or Bianchi/REI/CMB science.
