# THERM02 independent physics, code, data and figure review

**Verdict: PASS_SCOPED_THERM02_WITH_VISUAL_REPAIR.** No unresolved scientific
implementation or numerical-record defect was found in the reviewed scope.
One confirmed display defect in the first figures was repaired by root and
independently verified in all three final PDF exports. This verdict applies to
the declared conditional atomic/thermal test-fluid calculation, not to complete
physical thermodynamic closure or global numerical convergence.

Reviewer: `/root/thermal02_review`, who did not author the scientific unit.
Review date: 2026-10-22 UTC. Target:
`research/rec_rei_thermal_compton_20261022`.

## 1. Independence, execution and evidence boundary

Scientific source was read-only throughout this review. The reviewer performed
**one bounded retained-array calculation**, with **zero scientific-unit imports,
zero RHS calls, zero cosmological ODEs, and zero old-suite reruns**. No source,
contract, raw trajectory, production configuration or external application was
modified by the reviewer. All reviewer-created files are confined to the
independent-review working directory.

The independent calculation is retained as `independent_array_audit.py`,
`INDEPENDENT_ARRAY_AUDIT.json`, and `INDEPENDENT_ARRAY_AUDIT.log`. Its actual
process exit was **0**, with **2.316241782 s** of measured calculation-body time.
This is a verification measurement, not a scientific solver benchmark.

The review read the frozen contract, theory, source-reuse memorandum and
identities; the new source adapter, checks, runner, analyzer and plotter; the
specific inherited owners needed to establish units and projection semantics;
all eight new trajectory/solver-return pairs and receipts; the retained
comparison inputs; and final data/figure manifests. The already completed
Mao-table verification and author pre-ODE checks were examined as retained
evidence and were not rerun. The first failed pre-ODE attempt and its repair
record remain preserved; they are distinct from the eight successful IVPs.

## 2. Confirmed finding and resolution

### F1 — Low severity, high confidence: first-export figure labels collided

**Location:** original `code/plot.py` symlog axis formatter and stress-comparison
legend; preserved `figures/v1/`, `evidence/PLOT_V1_CODE.py.txt`, and
`evidence/PLOT_V1_MANIFEST.json`. The reviewer directly inspected preserved
figure 03: near-zero tick labels overlapped in the radiation/total/shear panels,
and the matter-panel legend obscured part of its linear-threshold note. Root
also recorded the affected first-export panels in `evidence/VISUAL_FINDINGS.json`.

**Effect:** impaired readability of small signed differences and their display
scale. The underlying values, signs, scientific arrays and CSVs were unaffected.

**Minimal correction, now completed by root:** retain the symlog transform and
all plotted values, suppress crowded inner nonzero tick labels, and move the
shared stress legend outside the panels. Final code locations are
`code/plot.py:216–237` and `code/plot.py:400–402`.

**Resolution evidence:** all three final PDFs were rendered by `pdftoppm` and
visually inspected. The crowded tick labels are resolved, the shared legend is
fully visible below figure 03, and no additional clipping or text overlap was
found. The final plot-code SHA-256 is
`39cb5db044b18211a58014e5cce94d4dc69188029aa4570b0e3090ef7d021f56`.
The v1/final manifests have identical scientific input bindings and identical
SHA-256 values for **all 11 plot CSVs**. Therefore the completed numerical audit
was retained without repeating its calculation. F1 is **CONFIRMED_RESOLVED**.

## 3. Physics and implementation assessment

### RR source, units and compact mapping — confirmed

`CoupledThermalAtomic` keeps the donor number-rate method and maps six Mao rows
by `(Z,q_initial)`, with `q_initial=Z-s_recombined+1`. The implementation uses
`t=k_B T/eV_J`, natural logarithms, and the derivative of that same expression.
The hybrid kinetic loss is `k_B T alpha_donor f_Mao`; it is not relabelled as an
independent measurement of the full cooling function. DR retains its separate
signed coefficient sum and resonance kinetic-energy moment. Recombination
binding energy enters the escape owner separately. These conclusions follow
from `code/coupled_thermal.py:115–192`, the retained source memo, and the
unchanged atomic generator/ionization-energy construction.

The new sources depend on a common scalar temperature, electronic element/charge
classes, scalar particle abundances and the current photon monopole. They add no
odd angular component or isotope-specific number rate. The inherited P/R map is
extended by an identity coordinate on w, so the compact invariant argument is
consistent with the implementation. The inherited tiny H/D initial-fraction
division roundoff is admitted under the donor's eight-epsilon rule, while exact
excluded geometry and neutron/tritium zeros are retained. The full63 initial
state was not silently projected to erase that bit difference.

### Compton signs, heat capacity and radiation owners — confirmed

With `w=(3/2) eta T`, division of the proper volume source by `n_b k_B H` gives
the implemented `B-Aw`, including the factor `8/(3 eta)` in A. The inherited
`THOMSON` is `sigma_T*c`; using `THOMSON/(m_e*c^2)` introduces no extra c.
The independent retained-state reconstruction of the direct volume expressions
and radiation-density owners agrees at at most **1.70e-15 relative** across
the saved new8 states.

The hot branch uses the current full-state photon energy monopole and photon
Omega only. The Planck branch owns an independently specified external bath;
the two alternatives are never summed. Their different density owners remain
explicit in the exchange-ratio diagnostics. UV moments use the actual GL4
node/flux weights, with scalar photon flux `c*n_gamma` and one factor of `1/c`.
The off branch disables both Compton contributions while retaining the
prescribed photoionizing UV source.

Current T feeds the number rates, current electron density feeds photon opacity,
and current geometry supplies H and the actual photon monopole. No historical
ionic or photon trajectory is replayed inside the new RHS. The frozen analytic
subflow is a fixture, not a replacement for the coupled BDF evolution.

### Energy owners and finite acceptance — confirmed

The implementation's thermal, ionic-potential, escaping-radiation, CMB/reference
bath and UV-bath signs agree with the frozen first law. Binding and DR resonance
kinetic energy are not counted twice. Matter, photon, neutrino, radiation-total
and overall signed stress remain separately available.

The runner uses `t_eval=None`; `solver_return.npz` contains actual accepted BDF
nodes, separate from the 193 dense comparison samples. Both GL8 and GL16 dense
states and their five source integrands are retained. The reviewer independently
checked the available algebraic state invariants on saved193, accepted-node,
GL8 and GL16 records. The local source, Einstein, trace-energy and signed-tensor
diagnostics were assessed from source plus their explicit per-scope execution
receipts; the reviewer did not re-evaluate dense scientific RHS values.

All **70 retained input files** matched their byte counts, SHA-256 and Git blob
identities. All eight execution source/config identities and artifact manifests
matched the retained files. There are **6,710 accepted BDF nodes**, plus
1,544 saved comparison states, 12,288 GL8 states and 24,576 GL16 states across
the eight histories. These are finite sampled-state records, not a continuum
positivity proof.

The independent ledger calculation used SciPy Legendre weights and compensated
`math.fsum` accumulation, distinct from the runner's NumPy/einsum/cumsum path.
It reconstructed thermal-plus-binding energy from retained w/populations and
the locked ionic thresholds. Absolute instantaneous source throughput was
integrated before summation; the denominator was reconstructed as the frozen
`max(|epsilon0|, |epsilon|, sum integral |source_j|)`.

The worst independent normalized gas-energy residual is
**3.7671763360e-7**, in `t02_split_mao_off` at **z=11.910551212**, against
**3e-6**. Its remaining gate margin is **87.4427455%**. The largest disagreement
between reconstructed and stored residual arrays is **7.9131e-16**. The largest
GL8/GL16 ledger difference is **8.9934e-12**. Both tight cases have peak energy
residuals about **6.98e-9**. These results establish the frozen finite ledger
acceptance, not an extrapolated error bound.

## 4. Numerical comparisons and physical interpretation

The three required comparison receipts were independently reproduced exactly
from the retained arrays:

| Comparison | Max relative T | Max absolute charge fraction | Max absolute tau | Max absolute signed six-vector |
| --- | ---: | ---: | ---: | ---: |
| hot tight34 versus nominal | 1.3967462405e-7 | 9.9662619719e-9 | 1.2703788233e-10 | 9.3956807959e-10 |
| Planck tight34 versus nominal | 1.4007600105e-7 | 9.9623412853e-9 | 1.2703683895e-10 | 6.5035601904e-10 |
| Planck full63 versus compact34 | 3.4167474117e-9 | 1.8718200323e-9 | 1.0519807248e-11 | 1.4853293595e-10 |
| Frozen limit | 3e-5 | 3e-5 | 3e-7 | 3e-7 |

For Planck minus hot, the independent maximum absolute temperature difference is
**7.1947326867 K**, versus observed hot/Planck refinement changes of
**9.6262104307e-5 K** and **9.6108884463e-5 K**. Temperature, electron abundance,
ionic fractions, tau, photon stress, combined radiation stress and total stress
exceed both observed refinement changes. **Matter stress, neutrino stress and
shear do not.** In particular, the shear difference is 2.8731e-10 while the two
observed refinement changes are 9.3957e-10 and 6.5036e-10.

The data-only analyzer reports the same distinction. Its other RR-closure and
seed contrasts are labelled observed model/source changes without two-sided
refinement-resolution claims. A full63 comparison is a finite check of the
restriction and numerical evolution; it is not an independent atomic cooling
witness. The plot's relative-T curves use the explicitly named right-case
temperature, whereas acceptance/analyzer comparisons use the declared symmetric
maximum denominator. The two definitions are labelled and are not silently
substituted for each other.

All 11 plot CSVs were checked for exact float64 round-trip binding to the
retained arrays, including the signed-comparison CSV. The final figures preserve
separate matter/radiation signs, named bath owners, the specified energy signs,
and explicit finite-sensitivity/backreaction limitations.

## 5. Execution records, historical repairs and remaining limits

The root science log records exactly **eight new successful IVPs**, with zero
cached executions and zero old-campaign IVPs in that invocation. Individual
reported case times range from **8.421 s to 18.544 s**; the sum is
**92.831601512 s**, and the campaign receipt records **92.951497908 s**
cumulative time, within the cooperative 180 s/1200 s allocation. The reviewer
did not independently instrument those runs or infer a speedup from them.

The initial pre-ODE failure was preserved. Its documented corrections increase
QUADPACK's subdivision limit to admit the already frozen breakpoints and restore
the inherited isotope-roundoff admission rule. Source physics, retained payloads,
the science cohort and frozen gates were not changed by those repairs. The final
11-group author check receipt is identity-bound PASS; no reviewer rerun was made.

Two runner limitations remain accurately scoped rather than hidden: budgets are
cooperative, with the final small JSON write after the elapsed-time sample; and
an exception thrown inside `solve_ivp` before return can preserve the last RHS
trial but cannot expose SciPy's internal accepted-node history. All eight actual
cases returned successfully and are far inside the time allocation. No failure-
path injection or broader campaign was needed to resolve an actual case risk.

Unresolved physical obligations remain: independent physical accuracy of the
full hybrid cooling closure; excluded Li resonances and complete final yields;
other omitted atomic/nuclear/secondary processes; the actual grey field's recoil
and induced-scattering spectrum; and spectral radiation-energy/Einstein
backreaction. Passive bath debits and measured `|Q_C|/(H U)` values do not close
those obligations or bound their errors. No universal impossibility result is
inferred from absent input data.

The separately reported concurrent PR124 restart/5–200 eV cohort is outside this
review. It is neither executed nor combined with THERM02 here. Publication and
remote-backup byte verification are also outside this review's authority.

## 6. Actual reviewer commands

All completed source/receipt reads (`rg`, `cat`, `nl`/`sed`, `wc`, and
`sha256sum`) exited 0. A scoped `git status` attempt exited **128** because this
local recovered source directory has no Git repository metadata. A local Git
diff was therefore unavailable; the exact retained Git blob identities and
execution-file/config SHA-256 bindings establish the reviewed target. These
operations were inspections, not scientific executions. The substantive
executable commands were:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python /workspace/scratch/a6dfe82cc85f/thermal02_work/independent_review/independent_array_audit.py > /workspace/scratch/a6dfe82cc85f/thermal02_work/independent_review/INDEPENDENT_ARRAY_AUDIT.log
exit 0

pdftoppm -r 110 -f 1 -singlefile -png figures/01_temperature_ionization_opacity.pdf /workspace/scratch/a6dfe82cc85f/thermal02_work/independent_review/01_pdf_review
exit 0

pdftoppm -r 110 -f 1 -singlefile -png figures/02_signed_energy_transfer.pdf /workspace/scratch/a6dfe82cc85f/thermal02_work/independent_review/02_pdf_review
exit 0

pdftoppm -r 110 -f 1 -singlefile -png figures/03_signed_stress_branch_changes.pdf /workspace/scratch/a6dfe82cc85f/thermal02_work/independent_review/03_pdf_review
exit 0
```

The three rendered PDF PNGs were actually opened with the image viewer. The
preserved original figure 03 was also opened to confirm the historical defect.
The post-repair operation compared manifests/hashes only; the independent
numerical audit was not rerun. `REVIEW.json` contains the criterion matrix,
source identities, command/exit records and unresolved-scope list.

**Preserved decisions:** Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL;
CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED;
REI_activation=false.
