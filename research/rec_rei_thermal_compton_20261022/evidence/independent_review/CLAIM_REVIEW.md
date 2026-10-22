# THERM02 bounded final-document claim review

**Verdict: PASS_LIMITED_CLAIM_CONSISTENCY_WITH_WORDING_REPAIR.**
The scientific claims in `REPORT_KO.md`, `HANDOFF_KO.md`, and `README.md`
agree with the completed independent review's scope, finite results, and
limitations. One Li-threshold sentence was clarified by root and the changed
passage was read to confirm resolution. No unresolved document finding or new
scientific implementation/data defect was identified in this bounded scope.

Reviewer: `/root/thermal02_review`, 2026-10-22 UTC.
Target unit: `research/rec_rei_thermal_compton_20261022`.

## 1. Boundary and evidence

This is a bounded **document-consistency read**, requested after the independent
physics/code/raw-array/figure review was completed. It is not a second numerical
audit or a new primary-source search. The three final documents were read and
compared with the existing `REVIEW.md` and `REVIEW.json`; selected passages in
the already-reviewed `provenance/SOURCE_REUSE_MEMO_KO.md` were read to check
source-domain and Li-threshold wording.

Additional scientific imports, RHS calls, ODE integrations, retained-array
calculations, old-suite reruns, plot generation, and external publication in
this document review: **all zero**. No scientific source or target document was
edited by the reviewer. The original independent `REVIEW.md` and `REVIEW.json`
were not modified.

## 2. Finding F_DOC_1 — Low severity, high confidence

**Location:** `REPORT_KO.md:68` in the source discussion.

**Observed text:** “60 eV cutoff는 64.39 eV 아래의 직접 1s-hole continuum을 닫지만,”.
The placement of “아래의” can be read as saying that the direct 1s-hole continuum
lies below 64.39 eV. The already-reviewed source memo, line 78, identifies
64.39 eV as the direct edge. The intended conclusion is that the 60 eV cutoff
does not reach this edge while the 50–60 eV resonances remain a separate missing
input.

**Effect:** an avoidable ambiguity about the threshold and the scope of the
smoothed continuum. The following resonance caveat is correct, and no numerical
result or implemented source is implicated.

**Minimal correction:** replace the quoted clause with
“60 eV cutoff는 64.39 eV 문턱의 직접 1s-hole continuum에 도달하지 않지만,”
and retain the existing 50–60 eV resonance caveat. Root was notified with the
location, source evidence, and this replacement.

**Resolution:** root applied that exact replacement. The reviewer then read
only the affected passage, `REPORT_KO.md:64–71`, and confirmed both the corrected
threshold wording and the unchanged resonance/missing-input caveat. The report's
corrected SHA-256 is
`501b4764fda8bc1c851bce3781a1048ac8351015f131e7f0869ce9a3fc02b93b`.
No scientific recalculation was performed. Root reported that scientific code
and data were unchanged. F_DOC_1 is **CONFIRMED_RESOLVED**.

## 3. Scoped claim assessment

| Criterion | Assessment | Evidence and interpretation |
| --- | --- | --- |
| Source facts, hybrid identity and allowed domain | CONSISTENT; F_DOC_1 resolved | Report section 2 preserves the six-row/13-channel mapping, donor number-rate ownership, `k_B T alpha_donor f_Mao`, and the distinction between source-fit residual and full hybrid physical error. The 100–1e6 K interval is consistent with the retained PR121 common execution support in the source memo, rather than a new claim of universal physical accuracy. Li missing input is bounded by the stated search, with no universal nonexistence claim. |
| Actual grey hot component, external Planck reference and UV | CONSISTENT | Report sections 3.2–3.3 keep photon-only current `U_gamma`, the separately specified reference `U_r`, the alternatives rather than their sum, and the actual GL4 UV nodes/moments. `THOMSON = sigma_T*c`, the `1/c` flux-to-density conversion, and the affine `B-Aw` contraction agree with the prior review. The off branch retains photoionization. |
| Energy ownership and meaning of total energy | CONSISTENT | Report section 4 defines gas energy as thermal plus ionic potential, preserves separate kinetic/binding escape and bath signs, and calls bath debits passive. The source-owner sum is a local exchange identity; the text explicitly does not equate it to an evolved spectral radiation/Einstein energy closure. The `|Q_C|/(H U)` values are explicitly exchange scales, not backreaction error bounds. |
| Branch resolution | CONSISTENT | Report section 5, handoff lines 25–30, and README lines 32–37 preserve the audited Planck-minus-hot classification: T, electron abundance, scaled charge fractions, tau, photon/radiation/total signed stress exceed both observed refinement maxima; shear, matter and neutrino stress do not. These are finite maximum-based diagnostics, not a pointwise guarantee, statistical significance, or global error estimate. The off, RR-closure, and seed contrasts are not assigned unsupported two-sided refinement claims. |
| Finite acceptance and numeric record | CONSISTENT | Report section 6 reproduces the three audited comparison rows and fixed thresholds, the stored and independently accumulated energy residuals, and their slight roundoff difference. It distinguishes accepted BDF nodes, comparison samples and GL records, and explicitly declines a continuum positivity proof. Global convergence remains NOT_RUN. |
| Numerical method, compact mapping and timing | CONSISTENT | The common scalar T/isotope-electronic/reflection-even assumptions, identity extension on w, coupled BDF evolution, and frozen-subflow fixture agree with the prior review. Timing is attributed to this sandbox's eight cases and cooperative budget; the text avoids an unperformed equal-input speed comparison or an algorithm-only attribution for a changed residual margin. |
| Review and figure claims | CONSISTENT | The original one retained-array calculation, zero scientific imports/RHS/ODE, three final PDF inspections, exact eleven CSV bindings, and resolved display-only finding are reported within the actual review scope. This document review does not add a second calculation or figure inspection to those counts. |
| Complete physical closure and retained decisions | CONSISTENT | All documents retain the conditional 21-population atomic/thermal test-fluid scope. Li final yields, actual-field recoil/induced spectrum and radiation-energy/Einstein backreaction remain open. Physical HOLD, REC U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED and REI_activation=false are preserved. |

The documents' condensed references to ionic fractions and stress resolution
are interpreted in the explicit maximum-based comparison definitions in the
report and the existing review. They do not establish that every component at
every saved time has a resolved difference.

## 4. Outside this follow-up's authority

The concurrent PR124 restart cohort is contextual intake outside the original
THERM02 numerical review. These documents correctly keep its 5–200 eV/full63/
109-node restart separate from the present 5–60 eV/193-node cohort and make no
combined-cohort or speedup claim. Its new public state, complete raw payload and
backup integrity were not independently reverified here.

Final publication, remote-backup acknowledgement, and whole-byte verification
remain **pending root's actual delivery receipts** at this review snapshot.
The documents direct the reader to those receipts instead of assigning a future
commit identity or claiming this reviewer verified delivery. This verdict does
not approve production or close any physical dependency.

## 5. Document identity and preservation

SHA-256 values of the inspected snapshots:

| File | SHA-256 |
| --- | --- |
| `REPORT_KO.md`, after the verified wording correction | `501b4764fda8bc1c851bce3781a1048ac8351015f131e7f0869ce9a3fc02b93b` |
| `HANDOFF_KO.md` | `f062ebf95a84538692b4c33b39457b3f430f7aff600b2e7a89365673d228d0e7` |
| `README.md` | `80f731a685c6b1acda0267106b8cef59f0c8b5e8ffd49aeb7e1f0b3f2b6852de` |
| Original independent `REVIEW.md` | `1959e0906a3ca67dd62feb6b39b018fefcff6278d4c34f2765f9441cbfe216a9` |
| Original independent `REVIEW.json` | `d727ee1be958ddbf2e908851847d19d6d1c45c2877566919dcb40ed4fb1df73f` |

The report's pre-correction SHA-256 was
`1f0bbc39e09dc0ebcfecda1e933a8413058cf7e551815da9f2820e36e91ba472`.
The last two table hashes match the already delivered independent review. A later
document-only correction or delivery update does not change the completed
scientific audit; only the changed claims and corresponding file identity need
to be read if a follow-up is requested.

## 6. Actual inspection commands

The following read-only shell commands all returned **exit 0**. Commands on the
three target documents and provenance ran from the unit directory; commands on
the review files ran from the independent-review working directory.

```text
cat REPORT_KO.md HANDOFF_KO.md README.md
cat REVIEW.md
nl -ba REPORT_KO.md | sed -n '285,390p'
nl -ba HANDOFF_KO.md
nl -ba README.md
sha256sum /workspace/scratch/a6dfe82cc85f/repos/rec_bianchi/research/rec_rei_thermal_compton_20261022/REPORT_KO.md /workspace/scratch/a6dfe82cc85f/repos/rec_bianchi/research/rec_rei_thermal_compton_20261022/HANDOFF_KO.md /workspace/scratch/a6dfe82cc85f/repos/rec_bianchi/research/rec_rei_thermal_compton_20261022/README.md /workspace/scratch/a6dfe82cc85f/thermal02_work/independent_review/REVIEW.md /workspace/scratch/a6dfe82cc85f/thermal02_work/independent_review/REVIEW.json
rg -n -C 3 '100|1e6|10\^6|64\.39|2026-03-09|033105|Sazonov|Mao|hybrid|induced|recoil' provenance/SOURCE_REUSE_MEMO_KO.md
rg -n -C 2 'domain|temperature|424|15538|5\.501|2\.220|5\.784|1\.876|symmetric|preserv|scientific_' REVIEW.json
rg -n 'cutoff|Source fit|domain|분해되지|error bound|passive|유지|최종|소급|Branch peak|Global convergence' REPORT_KO.md HANDOFF_KO.md README.md
sed -n '64,71p' REPORT_KO.md
sha256sum REPORT_KO.md
```

The initial combined tool display was truncated; the report's remaining tail
and the complete handoff/README were subsequently read with the explicit `nl`
commands above. No unviewed tail was treated as reviewed. The only new file
written by this follow-up is this `CLAIM_REVIEW.md`.
