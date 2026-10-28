# REC-HD-PRINT-PRECISION01: source-literal interval obstruction

**Owner**: `cosmosapjw-quantum/rec_bianchi`. **Parent source**: PR #152 immutable `f0ad60fdb1a460b304681fa76d47f4f2f14992b7`. **As of**: 2026-10-29 (KST). **Scope**: narrow source/printed-decimal diagnostic only. Do not merge, alter the original source, rescale H5 epsilon, or activate H6/H7, L4, REI, or a molecular production rate.

## 1. Fixed data and assumptions

Public LAMDA HD June-2021 printed table: 9 rotational labels J=0,...,8, term values w_J in cm^-1 at nine decimal places, photon frequencies nu_J in GHz at eight decimal places for J -> J-1. These 17 printed literals are transcribed into `public_print_transcription.json` from https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat. This is **not** a byte-identical re-ingestion of the protected 2289-byte LAMDA donor. Original frozen LAMDA hash `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb` is an **inherited un-rechecked source pin**, not this fixture's hash. The original CDMS Dec-2011 version-2 `.cat/.egy/.par/.fit` bytes and conversion recipe remain unavailable. CDMS v3 Aug-2026 must not substitute.

SI constants: c=299792458 m/s, h=6.62607015e-34 J s, k_B=1.380649e-23 J/K; retain original mass/energy dimensional distinctions. Optical/line frequencies nu_J are ordinary frequency, not angular frequency. Thus E_J = h c (100 w_J), epsilon_J = h (10^9 nu_J), and delta_nu,J = c(100 w_J-100 w_{J-1}) - 10^9 nu_J has units Hz. No metric/frame/gauge assertion beyond common local source-energy bookkeeping is made.

## 2. Conditional precision theorem (derived and numerically checked)

Assume the printed terms are separately rounded-to-nearest with quantization steps q_w=10^-9 cm^-1 and q_nu=10^-8 GHz, and the underlying unrounded values describe one consistent level energy structure: c 100 (w*_J-w*_{J-1}) = 10^9 nu*_J. Then every observed printed delta satisfies:

  |delta_nu,J| <= c 100 (q_w/2+q_w/2) + 10^9 q_nu/2
               = 34.9792458 Hz = b.

Proof: subtract the underlying equality and apply the triangle inequality separately to both printed term energies and the photon frequency. A joint exact realization of *all* printed intervals would in particular imply each of these eight inequalities. Hence one violated row certifies incompatibility with this particular same-energy + nearest-rounding representation. Row-by-row PASS is not sufficient to prove joint compatibility, because neighboring rows share level errors.

The result also survives a conservative truncation-of-each-field alternative with **twice** this envelope, 69.9584916 Hz. This is a safe outer bound rather than a sharp model of correlated/signed truncation. If a donor uses a different quantization or source-conversion convention, these two stated bounds do not apply automatically.

| J->J-1 | signed delta_nu [Hz] | nearest bound result |
|---|---:|---|
| 1->0 | -8.241016200 | PASS |
| 2->1 | -947678.840324000 | FAIL |
| 3->2 | +1084318.742916400 | FAIL |
| 4->3 | -47627.409091400 | FAIL |
| 5->4 | +1245461.910729000 | FAIL |
| 6->5 | -1827572.560757200 | FAIL |
| 7->6 | +1411205.450255200 | FAIL |
| 8->7 | +6864.989622800 | FAIL |

Minimum strict nonrounding excess among seven failed rows is **6830.010377 Hz** at J=8->7. Even after doubling the precision envelope, all seven of those rows remain excluded by this limited print-only hypothesis. **The original 35-Hz source gate FAIL7/8 is preserved unchanged**. Numerically, this checks printed-column compatibility; it does not diagnose which column, lab measurement, fit, vibrational label or conversion is authoritative, and does not infer physical observability.

## 3. Exact connection to PR #152's source obstruction (derived)

Using the sign convention of the parent PR #152, the eight source-defect coefficients are

  a_J(T) = beta [ (E_J - E_(J-1)) - epsilon_J ] = h delta_nu,J/(k_B T).

Under the same printed nearest-rounding hypothesis, each a_J has an interval h[delta-b, delta+b]/(k_B T), where T>0. This **does not modify** PR #152 incidence B, cycles C, or the 8-dimensional source-defect injection D; it only attaches dimensionful printed-source uncertainty to its existing source-defect vector. In the parent's photon-up orientation, a_J has the opposite sign to the earlier PR #151 photon-down/collision-up pair-loop affinity. Gauge E->E+const leaves a unchanged. The conditional intervals for T={50,100,200} K are in `results/print_precision_certificate.json`, with T exactly the source's printed temperature nodes, not a continuum extension.

Physical relaxation, entropy generation, collisions, gradients, radiative transfer and Einstein–Boltzmann H5 remain untouched. Failure of a print-only identity does not prove a thermodynamic entropy-production signal.

## 4. Source hypotheses and adversarial checks

H1 (rejected at 7/8 rows): **same-energy and nearest printed rounding** alone caused mismatch. Predicted |delta|<=b and 1/8 PASS contradicts it. H1b conservative truncation also ruled out at 7/8.

H2 (unresolved): two printed columns were generated from different spectroscopic fit/product or versions; requires raw Dec-2011 CDMS catalog/energy/fit bytes and transformation recipe.

H3 (unresolved): label map including v=0/v=1 is inconsistent; requires original level quantum-number mapping, not the ambiguous summary description. Numerical coincidence near 3100 cm^-1 is not a vibrational identification.

H4 (unresolved): a nontrivial source-conversion or rounding/truncation policy with an additional transformation was used; requires original LAMDA generator/provenance.

Potential CDMS experimental/predicted tags: the official SPCAT `.cat` format has `TAG<0` for a catalog line whose frequency and uncertainty were entered as experimental. A positive tag is not by itself a measured frequency. This metadata **cannot** assign each LAMDA photon literal to a particular measurement without quantum-number mapping and version-locked raw files.

Original CDMS v2 HTML directory indexes `HD.fit`, `HD.lin`, `HD.par`, `c003501.egy`, `c003501i.cat` with Dec 2011 timestamps; `c003501.cat` directory mtime Feb 2019. This is a locator, not bytes or proof that its contents match Dec 2011. Raw file fetch through web/Exa/local network failed in this session; keep source-choice HOLD.

## 5. Verification and limitations

- Python stdlib `Decimal` 60-digit exact arithmetic on the public printed *literals*: 8 rows and 3 conditional thermal intervals, results saved JSON; 10/10 `unittest` PASS after repairing two tests that incorrectly compared insignificant trailing zero formats.
- Wolfram Language exact rational integer arithmetic independently returned signed deltas, b=34.9792458, FAIL rows 2..8 and minimum excess 6830.010377. Algorithms/implementations differ but input transcription and scientific interpretation are not an independent nonauthor review.
- Executed negative controls: wrong J ordering, negative photon frequency, changed metadata/hash mismatch, conservative two-times envelope, measured vs predicted SPCAT flag, conditional a_J interval sign. Python test 10/10, C++ 42 smoke compiler probe, no production Rust/native/physical IVP.
- Plot directly read after generating; first plot's legend obscured J2/J3 and was repaired by moving legend below. Current `results/printed_precision_discrepancy.png` is discrete, source-derived. No interpolation or fit.
- `native_subagent: NOT_RUN_TOOL_NOT_EXPOSED`; R6 and C9 distinct nonauthor verification PARTIAL. External archived source original byte lock and provider upload for this new package NOT_RUN; no promotion to physics readiness.

## 6. Literature and owner provenance

1. [LAMDA HD public datafile](https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat) and [metadata](https://home.strw.leidenuniv.nl/~moldata/HD.html). Current printed source only, not proof of original byte identity.
2. [CDMS Dec2011 v2 directory listing](https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/) (Exa directory retrieval), raw files NOT_ACQUIRED.
3. [CDMS SPCAT format](https://cdms.astro.uni-koeln.de/classic/general), field widths, MHz, lower wavenumber and negative-tag lab signal.
4. [Ulivi et al. (1991)](https://doi.org/10.1086/186134), archival measured rotational spectrum, not a literal-by-literal LAMDA attribution.
5. [Essenwanger & Gush (1984)](https://doi.org/10.1139/P84-213), R(3), R(5), R(6) at the reported study's conditions, not a proof of the CDMS v2 file's row provenance.
6. [REC PR #150](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/150), [#151](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/151), [#152](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/152); immutable inherited source/algorithm evidence.

**Scientific admission**: `PASS_SCOPED_PRINTED_INTERVAL_OBSTRUCTION`; `CDMS_V2_RAW=BLOCKED`, `PHYSICAL_H5_APPROVAL=false`, `R6_C9_NONAUTHOR=PARTIAL`. New canonical completed DAG nodes **+0** (28/88), physical 0/313. A mathematical print incompatibility must not be relabelled `NEW_HD_PHYSICS`.
