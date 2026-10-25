# Pinned LAMDA HD adapter

The new adapter implements **literal source ingestion** for nine HD J-labelled
levels, eight radiative lines, two separate H₂ spin colliders, eighteen downward
pairs and fifty-four tabulated rates. The source is exactly 2289 bytes with
SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`.

**Result:** parser/unit/domain and local thermal-algebra checks are supported by
actual execution. The frozen **35 Hz level-gap versus line-frequency gate fails
for seven of the eight lines**, so the full original REC-HD-ADAPTER admission is
held at `SOURCE_DISCREPANCY_UNQUALIFIED`. No data or tolerance was changed. J=1→0
alone satisfies this rounding gate; physical catalog uncertainty is unresolved.

## Source and supplier reuse

- Provider: <https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat>.
- Exact archived input: [central LAMDA HD snapshot](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/641a725ada4be27473069c2c35005a94c2ab0248/research/orchestration_expansion_20261025/authority/molecular/lamda_hd_20261025.dat).
- Source metadata: CDMS version 2, December 2011; H₂ collision coefficients from
  Flower (1999), Tables 1 and 2 as the actual file states.
- Canonical molecule/isotope schema: [WU Species implementation](https://github.com/cosmosapjw-quantum/WU088_HH/blob/34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad/research/rei_chem_ledger_20261025/chem_ledger.py),
  SHA256 `60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af`.
  `bind_wu_species` calls the unchanged pinned `Species.from_record`; no supplier
  fixture or 249-check campaign is rerun. Each state has composition
  `{(Z=1,A=1,ground):1,(Z=1,A=2,ground):1}`, charge zero and material-pool identity.
- The HD vibrational assignment is explicitly `UNSPECIFIED`; the webpage wording
  and the J-only file labels have not been reconciled.

The public change does not mirror the provider data table. The caller supplies the
original local file, which is checked by byte count and SHA256. Citation guidance
is recorded in the parent source intake; a redistribution licence remains
unresolved. The source ZIP and private backup may carry the recovered inputs.

## API and qualification

```python
import lamda_hd
hd = lamda_hd.load_hd("/path/to/pinned/hd.dat")
q_down_m3_s = hd.downward_rate(2, 2, 1, 100)  # Decimal, exact source node
q_up_m3_s = hd.upward_rate(2, 1, 2, 100)      # Maxwellian detailed balance
line = lamda_hd.require_energy_frequency_bridge(hd, 1)
species = lamda_hd.bind_wu_species(hd, "/path/to/pinned/chem_ledger.py")
```

LAMDA source level IDs are **one-based**: IDs 1–9 correspond to J=0–8. Collider 2
is para-H₂, collider 3 is ortho-H₂. The exact source nodes are 50, 100 and 200 K.
Off-grid temperatures, including 75 K, out-of-range temperatures, unspecified
colliders and missing pairs raise `UnsupportedDomain`; they are never zero-filled,
interpolated, clamped or averaged. Upward rates preserve the collider identity.

Every scalar retains its source spelling and Decimal value. Energies use
`E_J = h*c*100*E_cm_inverse`, frequency uses `1e9*nu_GHz`, and collision coefficients
use `1e-6*q_cm3_s`. Products and energy differences are evaluated with an explicit
80-digit Decimal context. Independent Fraction comparisons check the exact
conversions. Original bytes and source-line/token positions are retained for exact
roundtrip and diagnostics.

`line` returns the literal catalog line. `transition_qualification` reports the
separate internal-energy/photon consistency gate. A consumer requiring that
bridge must use `require_energy_frequency_bridge`: line IDs 2–8 currently raise.
The rounding gate is a representation-consistency check, not an experimental
uncertainty.

## Thermal identities and units

For one Maxwellian collider at a tabulated temperature,

\[
q_{lu}^{(a)}=q_{ul}^{(a)}\frac{g_u}{g_l}
 \exp[-(E_u-E_l)/(k_B T)].
\]

The collision construction uses the **tabulated level energy difference**.
Einstein coefficients use **the catalog line photon energy**. For the convention
where B multiplies the profile-averaged mean specific intensity,

\[
g_l B_{lu}=g_u B_{ul},\qquad
A_{ul}/B_{ul}=2h\nu^3/c^2,
\]

\[
j_\nu=\frac{h\nu}{4\pi}n_u A_{ul}\phi_\nu,\qquad
\alpha_\nu=\frac{h\nu}{4\pi}(n_l B_{lu}-n_u B_{ul})\phi_\nu.
\]

Here n has units m⁻³, φ has units Hz⁻¹ with frequency normalization supplied by the
caller, j has units J s⁻¹ m⁻³ sr⁻¹ Hz⁻¹ and α has units m⁻¹. The thermal test uses
`n_u/n_l=(g_u/g_l)*exp(-h*nu/(k_B*T))`, so all terms share the same photon energy.
`expm1` evaluates the Planck denominator and the thermal population difference.
These algebra tests do not reconcile the source energy-frequency discrepancy.
General inverted populations retain negative α; they are not clipped. Exact
zero inputs are classified `ANALYTIC_ZERO`. Underflow of a positive Decimal input
or a nonzero emissivity/absorption term raises `NumericalDomainError`.

## Actual bounded executions

The parent `EXECUTION_FREEZE_HD_H5.json` allocates HD CPU 90 s, execution-wall
600 s, one thread and 1 GiB per-process memory. This unit measures process CPU
and wall time, applies child CPU/address-space limits and preserves all outputs.
The runner automatically includes existing `raw/**/EXECUTION.json` receipts;
`--previous-receipt` adds relocated prior receipts without duplicate charging.
Network, model and source-recovery costs and final-receipt-write overhead are not
claimed to be zero.

From this repository root, with the exact inputs restored:

```sh
python3 research/program_expansion_20261025/hd_adapter/run_bounded.py \
  --source /absolute/path/lamda_hd_20261025.dat \
  --wu-module /absolute/path/WU_chem_ledger.py \
  --output /absolute/path/new_HD_attempt
```

The complete frozen test unit deliberately returns failure on the retained 35 Hz
source criterion. This is the reproducible source result. The original first
execution is `raw/attempt1/`: 24 methods ran, 23 passed, one source criterion
failed. The diagnostic-only execution saved the full eight-line discrepancy map,
54 reverse detailed-balance residuals and 24 Kirchhoff residuals; it returned 2.
The two added methods verify fail-closed line admission and isolation from the
caller's Decimal context. Targeted repair tests exercised underflow/zero handling
and the changed thermal arithmetic. In all, **26 distinct methods have actual
results: 25 passed and the unchanged source criterion failed**. Repeated affected
methods are not counted as new methods.

`raw/source_diagnostic/diagnostics.json` is the immutable pre-guard saved numerical
snapshot. Later code changes add the per-line refusal API and repair numerical
edge paths; their execution identities are in the subsequent receipts. The
current source arithmetic and derivative-free helpers were checked only where
changed; the complete primary was not rerun.

The five controlled invocations consumed a known sampled process-tree total
**0.629051 CPU s**, **0.530994809 wall s**, peak observed RSS **15616 KiB**. Costs
of the final receipt writes and separate I/O remain `UNKNOWN_NOT_ZERO`.

## Remaining source obligation

Resolve the seven tabulated level/frequency disagreements with the original CDMS
catalog and LAMDA provider provenance, retaining both original columns. A new
source interpretation or source correction needs its own exact identity and
source-specific uncertainty; the 35 Hz acceptance bound is unchanged. A full
energy-conserving HD population/photon coupling remains unadmitted. No molecular
formation/destruction network, other isotopologue, continuum process, cosmological
transport, population IVP or physical source uncertainty has been computed here.
