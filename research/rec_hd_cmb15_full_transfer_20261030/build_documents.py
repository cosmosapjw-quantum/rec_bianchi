from __future__ import annotations
from pathlib import Path
import hashlib,json,csv,textwrap
R=Path(__file__).resolve().parent
out=R/'evidence';doc=R/'docs';st=R/'stages'
summary=json.loads((out/'FULLLINE_SCIENCE_SUMMARY.json').read_text())
inv=json.loads((out/'J1_INVERSION_T_Z_PHASE_SUMMARY.json').read_text())
validator=json.loads((out/'INDEPENDENT_SCIPY_16_STATES_9_TAU.json').read_text())
mechanism=json.loads((out/'INVERSION_MECHANISM_SUMMARY.json').read_text())
wins=list(csv.DictReader((out/'J1_INVERSION_T_Z_PHASE_WINDOWS.csv').open()))
std0=next(r for r in wins if r['source']=='std' and r['Tgas_K']=='4000.0' and r['z']=='0.0')
alt0=next(r for r in wins if r['source']=='alternate' and r['Tgas_K']=='4000.0' and r['z']=='0.0')

def write(p,s): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf8')

theory=f'''# HD full 15-state source-locked CMB line transfer, weak inversion (2026-10-30)

## Scientific authority, source, assumptions

Exact input: David A. Neufeld (2026), *Excitation of Warm HD and H2 and Implications for the Interstellar Deuterium Abundance*, ApJ **1007**, 16, DOI 10.3847/1538-4357/ae851a; official original Zenodo **v2** record 21165907 (DOI 10.5281/zenodo.21165907). Four source .dat/.fits files are copied as immutable bytes and SHA256 validated before every model run, with per-file checksums in evidence/FULLLINE_SCIENCE_SUMMARY.json. Original Wan et al. (2019) HD-H2 de-excitation source rates for low J, extrapolated J>8 rates in Neufeld's files are distinguished from measured scattering data.

Uniform slab with source-owned 15-level collision and radiative generator, original level degeneracies g_J=2J+1, source A_ul and frequencies; H2 ortho/para fraction =0.75/0.25; Tgas exact source input values {{100,400,1000,4000}} K (no interpolation); H2 densities 10^2,10^4,10^6,10^8 cm^-3; CMB Tgamma(z)=2.72548(1+z) K, z={{0,10,30,50,100}}. Metric signature (-,+,+,+); SI h,c,kB retained. Mass for Doppler thermal broadening is source header 3.0 atomic mass units (approximation), with separately chosen microturbulent Doppler b={{0,3}} km/s. HD column N={{10^14,10^16,10^18,10^20}} cm^-2, no external continuum beyond CMB, dust, line overlap, chemistry, bulk velocity gradients, or instrument convolution. All reported surface brightness per solid angle is modelled and conditional, not a telescope flux measurement.

## Physical equations (derived, then numerically checked)

Stationary source-owned normalized populations p_i satisfy M p=0, sum_i p_i=1. For Tgamma, nbar_ul=(exp(h nu_ul/(kB Tgamma))-1)^-1. Collisional downward q_ul=nH2[(1-f_o) k_p,ul+f_o k_o,ul] and upward q_lu=q_ul(g_u/g_l)exp[-hc(Eu-El)/(kB Tgas)] using original source energy gaps. Radiative u->l rate A_ul(1+nbar), upward l->u A_ul (g_u/g_l)nbar.

Original positive-power and negative-power terms are preserved:

    P_net,ul = h nu_ul A_ul [p_u(1+nbar_ul) - (g_u/g_l)p_l nbar_ul]  [W/HD].

For an isothermal Doppler Gaussian (frequency profile normalized to 1):

    Delta_nu_D = nu_ul b/c, b^2=2 kB Tgas/m_HD + v_turb^2;
    phi_nu = exp[-((nu-nu_ul)/Delta_nu_D)^2] / (sqrt(pi) Delta_nu_D).

The line absorption coefficient integrated over a column N_HD in m^-2 is

    tau_nu = N_HD [c^2 A_ul/(8 pi nu_ul^2)] [(g_u/g_l)p_l-p_u] phi_nu.

Define D=(g_u/g_l)p_l-p_u. The source function (where D!=0) and excess emergent specific intensity are

    S_nu= [2 h nu_ul^3/c^2] p_u/D,
    Delta I_nu=(S_nu - B_nu(Tgamma)) [1-exp(-tau_nu)].

This is *exact formal transfer for fixed level populations* through a uniform slab. Those populations were solved in the optically thin external-CMB source equation, not self-consistently with trapped emitted photons; thus the physically supported interpretation is restricted by |tau0|<0.1. Rows outside that screened regime are explicitly flagged 'formal_only', not promoted. If D<0, tau<0: the same formal equation provides the unsaturated, weak-gain solution but NOT a saturated maser model.

In the optically thin limit, directly from the Einstein relations:

    Delta I_line(rest) = N_HD P_net,ul/(4 pi)  [W m^-2 sr^-1]

with N_HD in m^-2. The frequency-integrated finite-slab correction is a *purely formal* fixed-population ratio

    beta(tau0)= [1/sqrt(pi)] integral_(R) exp(-x^2) [1-exp(-tau0 exp(-x^2))]/[tau0 exp(-x^2)] dx.

Then Delta I_line,formal=Delta I_line,thin beta(tau0). A separate FLRW *conditional mapping* to observer-frame bolometric surface brightness multiplies by (1+z)^-4. It is not a cosmological history calculation or distance/beam flux.

## Genuine low-J inversion and two-state exclusion

The signed criterion D=3p0-p1 for J1->J0. Under the exact original source at Tgas=4000 K, nH2=1e4 cm^-3, z=0, both standard and alternative rate files produce D<0; at N_HD=1e20 cm^-2, tau0~-5.85e-4 (small gain) and no broad, intense maser claim. Density-window endpoints at z=0: standard {{n_on={float(std0['n_inversion_on_cm3']):.9g},n_off={float(std0['n_inversion_off_cm3']):.9g}}} cm^-3, alternative {{n_on={float(alt0['n_inversion_on_cm3']):.9g},n_off={float(alt0['n_inversion_off_cm3']):.9g}}} cm^-3. The source-knot phase diagram over 9 exact temperatures, 5 redshifts, 2 alternative sources has {inv['case_count']} conditions and {inv['density_samples']} density samples (of these {inv['inversion_condition_cases']} source-temperature-redshift cases exhibit a bounded density inversion window).

For an isolated two-level positive-temperature thermal collision model, let down collision rate q>0, upward q(g1/g0)exp(-h nu/(kB Tgas)), and radiative bath occupation nbar>=0. Stationary p1/p0 divided by g1/g0 equals

    [A nbar + q exp(-h nu/(kB Tgas))]/[A(1+nbar)+q] < 1.

Proof: denominator minus numerator = A + q[1-exp(-h nu/(kB Tgas))] > 0. Therefore an isolated two-level positive-temperature HD J1->J0 model cannot be inverted. The original source-locked J<=2 truncated model is not inverted for the specific T=4000 K,nH2=1e4,z=0 test, but the J<=3 truncated model becomes inverted, as does full J<=14. This is a *controlled diagnostic* of multi-level pumping, not a proof of unique physical mechanism or novelty. Full-model f_ortho in {{0,.25,.5,.75,1}} retains inversion at that fixed test state.

## Numerical checks and limitations

- {summary['stationary_model_states']} source-stationary model states and {summary['line_transfer_rows']} line,column,velocity rows were computed, including signed absorption and weak-gain cases (no negative-population clipping).
- {summary['thin_abs_tau_lt_0p1_rows']} rows satisfy |tau0|<0.1. {summary['formal_only_abs_tau_ge_0p1_rows']} do not, and are NOT self-consistent trapped-radiation predictions.
- Independent dense NumPy/scipy solve: {validator['population_checks']} source states, max |delta p|={validator['max_population_abs_difference']:.7e}; adaptive quadrature for {validator['beta_checks']} tau values compared to 96-node Hermite, max |delta beta|={validator['max_beta_abs_difference']:.7e}. Rounding effects on tiny populations are separate from physical negative opacity.
- Original CDMS2011 v2 35 Hz FAIL7/8 is unchanged. No replacement of source-owner lines/frequencies. Sung et al. joint calibration/line-center covariance and CDMS historical SPFIT full precision covariance remain unavailable. No sky measurement, observing likelihood, detection significance or claimed new strong no-go.

## Primary citations

Neufeld, D.A. (2026), ApJ 1007, 16, DOI 10.3847/1538-4357/ae851a; source v2 DOI 10.5281/zenodo.21165907.
Francis, L. et al. (2025), A&A 694, A174, DOI 10.1051/0004-6361/202451629 (existing JWST data, NOT a new input here).
Sung, K. et al. (2023), JQSRT 295, 108412, DOI 10.1016/j.jqsrt.2022.108412 (historical experimental line-shape data, NOT an input here).
'''
write(doc/'THEORY_KO.md',theory)
report=f'''# REC-HD source-owned 15-state CMB line transfer | scientific report (2026-10-30)

## Source and physical outputs

New bounded auxiliary from frozen PR #173 source, Neufeld (2026) v2 standard and alternate HD collision rates, exact original 15 energy levels, Einstein A and radiative frequencies. The source .dat/.fits files are protected by SHA256 and contained in the entire source ZIP, not promoted to the original CDMS2011 owner.

- Real model solutions: **{summary['stationary_model_states']} 15-level stationary source+CMB states**, **{summary['line_transfer_rows']}** resolved per-line Gaussian transfer rows for 14 rotational lines, two microturbulent widths and four HD columns. This is physical-model data, not measured JWST flux.
- Signed excess line brightness: emission **{summary['counts_sign']['emission']}** rows, CMB absorption **{summary['counts_sign']['absorption']}** rows.
- Screened small optical depth: **{summary['thin_abs_tau_lt_0p1_rows']}** rows with |tau0|<0.1; **{summary['formal_only_abs_tau_ge_0p1_rows']}** formal-only rows outside that self-consistency guard. Max tau0={summary['max_tau0']:.9g}; min tau0={summary['min_tau0']:.9g} at the chosen column upper bound 1e20 cm^-2.
- Signed negative optical depth (weak inversion): **{summary['population_inverted_rows']}** rows. Note this repeats 10 physically distinct source/T/n/z states across line width and column choices, not 80 independent observations.
- Original source-knot inversion phase: **{inv['density_samples']}** density evaluations across **{inv['case_count']}** source/T/z conditions; **{inv['inversion_condition_cases']}** source-condition rows with two bounded roots. Standard source z=0,T=4000K n(on/off) = {float(std0['n_inversion_on_cm3']):.8f}, {float(std0['n_inversion_off_cm3']):.8f} cm^-3. The alternative original gives essentially the same window, but this is not an independent observational confirmation.
- The J1 inversion is absent in the isolated 2-level model and J<=2 truncation, but present in J<=3 (four levels), and persists across f_ortho=0,0.25,0.5,0.75,1 at the T=4000K nH2=1e4 cm^-3 z=0 test state. This strongly indicates multi-level pump/cascade within model; no novel molecular maser detection is claimed.

## Verification

Independent algorithm: {validator['population_checks']} dense linear solves max |population difference|={validator['max_population_abs_difference']:.8g} and {validator['beta_checks']} adaptive transfer integrals max |beta difference|={validator['max_beta_abs_difference']:.8g}. Source SHA256 4/4 original immutable .dat/.fits verified. Normal and Python -O unittest suites, compileall, and clean-restored source replay run receipts in logs. Native distinct-author review NOT_RUN, same-context blind review attached. The underlying Neufeld source collision J>8 extrapolations and the observed JOYS shock gas interpretation are not promoted beyond source support.

## Origin and next scientific dependency

Official Neufeld Zenodo v2 additionally includes **posterior_isobaric.csv.gz** and **posterior_isochoric.csv.gz**, sourced from published Francis et al. (2025) JOYS/MIRI measurements. Exact v2 archive checksums: MD5 f21c0527fcf00829ad95888887d20afd and 6458f83f324a19c8e28fd656dcce2022. The current direct binary fetch path was blocked; Exa text-fetched gzip is irreversibly decoded, and these files are NOT part of this new capsule. No user-provided data is assumed. Source download URLs: https://zenodo.org/records/21165907/files/posterior_isobaric.csv.gz?download=1 and https://zenodo.org/records/21165907/files/posterior_isochoric.csv.gz?download=1. Next separate bounded research unit could ingest those **literal original bytes** and compare published source-owned isobaric/isochoric posterior medians without new fitting claims, then later obtain raw Francis HD/H2 flux and covariance to perform independent likelihood inference.

Original CDMS2011 35Hz 7/8 FAIL, H5 epsilon null, H6/H7 OPEN, L4 false, REI false; original canonical **28/88**, physical **0/313**, production HOLD. This new standalone auxiliary **1/1 SCOPED** does not add a canonical/physical node.

## Rendered figures and data

- `figures/HD_J1_INVERSION_DENSITY_z0.png`, `_z100.png`: source alternative and redshift dependence of overpopulation at the exact 4000 K original source knot.
- `figures/J1_INVERSION_T_Z_PHASE_WINDOWS.png`: original-temperature-knot onset and offset density windows, no invented temperature interpolation.
- `figures/HD_14LINE_CMB_ABSORPTION.png`: z=100 and Tgas=100 K net background absorption, not detection.
- `figures/HD_14LINE_WARM_EXCESS.png`: Tgas=4000 K warm emission, not detection.
- `figures/HD_14LINE_OPACITY_SCREEN.png`: optical-depth regime and 0.1 screening threshold.
- `evidence/FULLLINE_SLAB_TRANSFER_ATLAS.csv`, `J1_INVERSION_T_Z_N_DENSE_ATLAS.csv`, `J1_INVERSION_T_Z_PHASE_WINDOWS.csv`, `LOWJ_PUMPING_MECHANISM.csv`, `OPR_INVERSION_SENSITIVITY.csv` plus JSON summary and SciPy evidence.
'''
write(doc/'REPORT_KO.md',report)
write(doc/'BLIND_REFEREE_SAME_CONTEXT_KO.md','''# REC-HD CMB15 transfer: same-context adversarial review, bounded

Status: SAME_CONTEXT_ONLY, NOT a distinct-author R6/C9 review.

1. Is the J1 inversion a false numerical negative? Source-own 15-level M-matrix solution is nonnegative; separately assembled dense NumPy/SciPy generator agrees within measured max population difference. The signed J1 balance p1-3p0 is order 1e-3 at reference T4000,n1e4,z0, many orders above solver error. Both original source alternatives show inversion, and 5 prescribed ortho H2 fractions retain its sign. Finding: low-level inversion conditional on model, numerically supported.
2. Does this establish a detected maser? NO. At HD column 1e20 cm-2 the center negative tau is only about -5.85e-4 in the reference warm case, so unsaturated amplification is tiny; model excludes velocity coherence, pump nonlocality, line overlap and saturation. 'Physical-model population inversion' is the maximum supported wording.
3. Could it come only from high-J rate extrapolation? The original low-J truncated-source operator (J<=3) already inverts at the specified reference state while J<=2 does not. Not solely high-J extrapolation; however truncation is a diagnostic, not a new validated molecular dataset or a theorem for every collision model.
4. Does homogeneous fixed-population slab solve full radiative transfer? It solves formal transfer for prescribed populations, not photon trapping self-consistently. All |tau0|>=0.1 rows are retained as formal diagnostic and excluded from self-consistent physical admission. Negative-tau gain remains very small within the chosen original column grid. CMB is the only external bath.
5. Is signed absorption at z100 a new observed cosmological signal? NO. It is source-owned per-slab excess intensity given prescribed Tgas, densities, columns, CMB law, and a conditional FLRW observer brightness map. It is not a sky measurement or redshift-history IVP.
6. Is numerical agreement circular? The second solver reconstructs CTMC generator separately and uses NumPy dense solve, compared with original bespoke M-matrix elimination. Adaptive SciPy quadrature checks Gauss-Hermite beta. Same authorship/context is explicitly not an independent referee.
7. Does legacy CDMS2011 35 Hz fail disappear? NO; all source line frequencies and collision models are new isolated auxiliary; original owner/consumer and tolerance unchanged.
8. Do quoted source observational posterior data support a fit here? NO; poster compressed originals not acquired byte-authentically. Public existence and MD5 only. No synthetic covariance, fabricated sigma, or sky likelihood in this unit.

Decision: accept scoped source-authentic physical-model atlas 1/1; R6/C9 distinct-author NOT_RUN, production HOLD, original canonical/physical DAG unchanged. No new strong no-go admitted.
''')
write(doc/'README_REPRODUCE.md','''# REC-HD 15-level CMB and line-transfer scientific reproducibility

Extract archive into an isolated directory; do not write into parent/owner worktree. Source original .dat/.fits bytes are frozen and checked at every computational entrypoint.

```bash
PYTHONPATH=src python src/hd_line_transfer.py --root .
PYTHONPATH=src python src/independent_dense_validator.py --root .
PYTHONPATH=src python src/inversion_window.py --root .
PYTHONPATH=src python src/inversion_phase_diagram.py --root .
PYTHONPATH=src python src/inversion_mechanism.py --root .
python src/render_science_plots.py --root .
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -O -m unittest discover -s tests -v
python -m compileall -q src tests
```

Source identity: `source/zenodo_v2/hd_lamda*.dat`, `hd_population_grids*.fits` have their exact SHA256 in `evidence/FULLLINE_SCIENCE_SUMMARY.json`. Model input T and H2 density source units are K and cm^-3; HD column is cm^-2, output intensities are W m^-2 sr^-1. The observational posterior CSV.gz is not an input. Do not interpret numbers as observed telescope line fluxes or saturated maser predictions.
''')

stage_desc={
 'R1':'Fixed previous PR173 source SHA and selected new CMB15 finite-column radiative transfer scientific target',
 'R2':'Read and reuse authentic Neufeld2026 v2 source, original JDWT observational poster located but compressed bytes not obtained, source provenance locked',
 'R3':'Derived source rates, Einstein degeneracies, CMB occupancy, optically thin background subtraction in SI',
 'R4':'Examined positive/negative optical depths and two-level versus multilevel inversion alternative mechanisms',
 'R5':'Derived formal slab transfer, tau(N), Gaussian factor, thin integrated intensity and 2-level no-inversion lemma',
 'R6':'Same-context adversarial scientific review only; distinct-author reviewer NOT_RUN, remain PARTIAL',
 'R7':'Computed 160 CMB15 stationary states, 17920 lines and 90 source-T-z inversion phase states with 14490 density samples',
 'R8':'Source-owned weak J1 inversion window, CMB sign absorption, optical-depth 0.1 physical screening; no sky claim',
 'R9':'Wrote physical theory and report with exact equations, assumptions, source identity and reproducible scientific figures',
 'R10':'Scoped closure and immutable handoff; no owner source promotion, no merge or canonical node promotion',
 'C1':'Bound source files and parent PR173 head, tested source integrity and original physical units',
 'C2':'Mapped original 15-level CMB source-solver inputs to finite-column lines and old CDMS owner kept immutable',
 'C3':'Implemented SI radiation coefficients and Gaussian transfer without clipping negative optical depths',
 'C4':'Isolated source worktree, bounded 160-state, 17920-row, 90-condition scientific run and checkpoint',
 'C5':'Implemented runnable HD line transfer, SciPy validator, inversion window/phase and plots',
 'C6':'Ran normal/-O tests and compileall with actual exit code plus basic source integrity and sign error barriers',
 'C7':'Checked physical source ledger and independent dense solver populations, two-level analytic limit and low-J inversion',
 'C8':'Checked Hermite against adaptive quadrature, fixed optical-depth domain and independent source replay',
 'C9':'Same-context adversarial physics/code review, true different-author reviewer NOT_RUN, remain PARTIAL',
 'C10':'Packaged original source with CSV, figures, logs and test scripts; provenance/handoff and Draft PR'}
for key,desc in stage_desc.items():
    status='PARTIAL_DISTINCT_AUTHOR_NOT_RUN' if key in ('R6','C9') else 'SCOPED_COMPLETED'
    row={'stage':key,'unit':'REC_HD_NEUFELD2026_CMB15_FULLLINE_TRANSFER_20261030',
         'status':status,'objective_evidence':desc,'scientific_assumptions':'Neufeld2026 Zenodo v2 original, 15-level HD nonLTE CMB; |tau0|<0.1 fixed-population physical screen',
         'evidence_artifacts':['docs/THEORY_KO.md','docs/REPORT_KO.md','evidence/FULLLINE_SCIENCE_SUMMARY.json','evidence/J1_INVERSION_T_Z_PHASE_SUMMARY.json'],
         'canonical_DAG':'28/88','REC_physical_DAG':'0/313','new_auxiliary':'1/1_SCOPED',
         'original_CDMS2011_35Hz':'FAIL7/8','R6_C9_distinct_author':'NOT_RUN',
         'parent_PR':173,'immutable_parent_HEAD':'90d883c77b3823322f2ecdb09888442b9a620a97',
         'no_merge':True,'production':'HOLD','stage_publication_ack':'PENDING_AT_RECORD_CREATION'}
    write(st/(key+'.json'),json.dumps(row,indent=2,ensure_ascii=False))
print('wrote docs',len(list(doc.glob('*.md'))),'stages',len(list(st.glob('*.json'))))
