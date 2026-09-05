# Original HyRec 2s physical-input trace

`TRACE_DATA_COMPLETE / OWNER_REVIEW_PENDING / NOT_PHYSICALLY_AUTHENTICATED`

This child records the original 2s channel for `b=0..139`. It supplies actual
source values and a review contract. It does not supply physical packet-state
values, a deposition map, or a mode measure. The scientific claim remains
`NO_PASS_REC_PHYSICAL_SPLIT`.

Fixed parent: `aeb01d369436f2d0eda2c946e9c650e54ae06fca`.
Parent tree: `afa41c177aa27d73ef772a7d20522d3ef2ef7835`.
Only this new directory is changed. Source code, tests, old evidence and the
root continuation documents retain their parent bytes. The current user task
supplies the authority for this documentation child and its Draft publication;
the older root handoff concerns a different formal-run stage.

## Deliverables and evidence states

| File | Meaning |
|---|---|
| [bins_2s.csv](bins_2s.csv) | All 140 source rows, raw and normalized values, companion energies, counting convention and unresolved correspondences |
| [OWNER_REVIEW_CONTRACT.json](OWNER_REVIEW_CONTRACT.json) | Explicit unresolved inputs and owner questions; `B`, `mu`, boundaries and physical state values are null |
| [PROVENANCE.json](PROVENANCE.json) | Exact source/blob/member identities, source locations and separately labelled historical evidence |
| [SOURCE_EXCERPTS.txt](SOURCE_EXCERPTS.txt) | Both complete requested C functions and the relevant constants/switches; display whitespace is not byte authority |
| [RUN_RECORD.json](RUN_RECORD.json) | Fresh extraction, arithmetic, input checks and environment limitations |
| [CENSUS_VERIFICATION.log](CENSUS_VERIFICATION.log) | Actual read-only execution of the reproduction block |
| [TARGETED_TEST.log](TARGETED_TEST.log) | Fresh existing table test, including the initial missing-pytest environment error |
| [REPRODUCE.md](REPRODUCE.md) | Read-only regeneration/validation procedure for the numerical census |

`DIRECT_SOURCE` means inspected source bytes, `DERIVED` means the displayed
algebra under stated assumptions, and `NUMERICALLY_CHECKED` refers only to the
fresh recorded arithmetic. `HISTORICAL_EXECUTION` is never a fresh test count.
`UNRESOLVED` is retained where source identity or physical meaning is missing.

## Original input and normalization

The selected archive is
`archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256
`48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
The selected member is `HyRec/two_photon_tables.dat`, SHA-256
`93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9`.
Both were checked against the pre-existing constants at the fixed parent.
The archive's name is October 2012; its source and supplied documentation
identify the May 2012 third release. No alternative table is substituted.

`DIRECT_SOURCE`: `read_twog_params`, `hydrogen.c:278-290`, reads five values
per row in the order `E_b, A1s, A2s, A3s3d, A4s4d`. There are 311 physical
lines without header/comment lines. Thus C index `b` corresponds exactly to
physical line and data row `b+1`; `A2s` is column 3. Default `NSUBLYA=140`,
`NVIRT=311`, `MODEL=FULL`, and `EFFECT_A=1` retain the 140 sub-Lyman-alpha
2s coefficients. Other build switches are not silently covered by this trace.

The unmodified `OriginalHyRecTwoPhotonRamanTable.from_archive` is the source of
the exported normalized values. The normalization is

\[
 S_{\rm raw}=\sum_{b=0}^{139}A^{\rm raw}_{2s,b},\qquad
 \eta=\frac{8.2206\ {\rm s}^{-1}}{S_{\rm raw}},\qquad
 A_{2s,b}=\eta A^{\rm raw}_{2s,b}.
\]

| Fresh quantity | Value |
|---|---:|
| Exact sum of the 140 decimal source tokens, in s^-1 | 8.2245807524349 |
| Normalization used by the binary64 loader | 0.9995159932700859 |
| Sum of normalized coefficients, in s^-1 | 8.2206 |
| Maximum difference from independently rounded decimal-reference results | 1 binary64 ulp |

The constant is the archived `hydrogen.h:38` choice, not a new determination
of the physical lifetime. Only `A2s[0:140]` is rescaled. No bin width, factor
of two, density, temperature or occupation is multiplied into these values.
The C-order sum was also emulated in Python; it is not labelled a C execution.

| b / original line | E_b (eV, source token) | Raw A2s (s^-1) | Normalized A2s (s^-1, binary64) |
|---|---:|---:|---:|
| 0 / 1 | 5.1790432 | 0.33259349 | 0.3324325125125144 |
| 69 / 70 | 9.7251678 | 0.0071955789 | 0.007192096191386772 |
| 139 / 140 | 10.197848 | 1.4538371e-06 | 1.4531334330594013e-06 |

The CSV retains the original lexical tokens and 17-digit round-trip values.
The normalized hexadecimal field is the exact binary64 representation. Two
companion columns distinguish subtraction of decimal tokens from binary64
subtraction; neither invents additional source precision.

## Photons, intervals and counting

Use ordinary frequency, with `E_J=h nu` and `h=2 pi hbar`; retain `c` and `k_B`.
The archived transition energy is `E21=10.198714553953742 eV`. For this branch,
the tracked photon is the higher-energy member,

\[
 E_t=E_b,\qquad E_c=E_{21}-E_b,\qquad
 E_t\in[E_{21}/2,E_{21}],\quad E_c\in[0,E_{21}/2].
\]

All exported `E_b`, `E21` and companion numbers are the original reference-energy
coordinates. In the conditional varying-constant extension, the physical
energy is `E_J=(fsR^2 meR) E_eV (1 eV in J)` and `nu=E_J/h`; the CSV values
are not rescaled. This follows the original temperature rescaling at
`hydrogen.c:53-58` and wavelength factor at line 521. No nonunit ratios are
chosen by this trace.

These are continuum integration/range bounds. All 140 actual centers lie
strictly inside them; `E21/2=5.099357276976871 eV`. The companion centers run
from `5.019671353953742 eV` down to `0.000866553953742 eV`, using decimal-token
subtraction. These are derived companions, not extra native rows.

`LITERATURE_SUPPORTED`: Hirata defines the higher-energy photon as the
integration variable and integrates each decay once over the upper half of
the two-photon spectrum. This removes an additional identical-particle
symmetry factor from that convention. [Hirata 2008, III A, (26)-(29)](https://arxiv.org/pdf/0803.0808)

`DIRECT_SOURCE`: `hydrogen.h:98` and the supplied ZIP readme describe the
stored coefficient as a differential rate times its bin weight. It is already
in `s^-1`, not `s^-1 eV^-1`. The associated spike-region integral is the
definition in HyRec (67); the sharp profile in (66) concentrates the optical
depth at the spike. [Ali-Haimoud and Hirata 2011, V A](https://arxiv.org/pdf/1011.3758)

The per-bin integration regions `I_b`, their endpoints and their generating
procedure are not supplied by these five-column data or by the reader.
Write `A_b = integral over I_b of (dLambda_2s/dE) dE` as the convention, while
leaving `I_b` unresolved. Neither the first/last center nor the continuum
half-domain endpoints are a justified per-cell boundary. This trace does not
re-integrate the atomic spectrum or certify its numerical quadrature.

`DERIVED`: within the higher-energy counting convention, one forward atomic
event produces one tracked photon; a reverse event removes one. The normalized
table is a spontaneous event coefficient per upper-state atom, not a realized
rate per H and not an occupation derivative. Populations and radiation factors
are still required. If both photons are evolved, there are two distinct
frequency contributions per event; doubling the 140-bin tracked vector puts
the companion at the wrong energy and does not define its angular distribution.
No such multiplication is applied here.

## Direct native coefficients and conditional paired-action correspondence

`DIRECT_SOURCE`: `populateTS_2photon`, `hydrogen.c:429,470-473`, sets, for this
branch,

\[
 C_b=\frac{s_A A_{2s,b}}{1-\exp(-E_c/T_R)},\qquad
 D_b=C_b\exp(-E_c/T_R),\qquad s_A=f_{\rm sR}^{8}m_{\rm eR},
\]
\[
 T_{vr}[0,b]=-C_b,\qquad T_{rv}[0,b]=-D_b,\qquad
 \Delta T_{rr}[0,0]=\sum_b C_b.
\]

Here the displayed diagonal increment is only the specified 140-bin 2s
contribution; the full C routine loops over all 311 bins and has other terms.
The two symbols in `s_A` are dimensionless ratios of constants to their
reference values, not dimensionful fine-structure/electron-mass factors.
`T_R` is the source thermal energy in eV, already divided by `fsR^2 meR` when
constants are varied. The tabular normalization and this rate rescaling are
separate. No `T_R`, population or varying-constant input is selected here.

`LITERATURE_SUPPORTED`: the native coefficient form assumes a blackbody
low-energy companion and neglects stimulation by the high-energy photon.
[Ali-Haimoud and Hirata 2011, IV B, (48)-(50)](https://arxiv.org/pdf/1011.3758)

`DERIVED`: put `n_c=[exp(E_c/T_R)-1]^-1`, so that
`C_b=s_A A_b(1+n_c)` and `D_b=s_A A_b n_c`. For the scalar 2s/1s statistical
weight ratio of one, the positive-pair expression is

\[
 R_b^{\rm pair}=s_A A_b\left[
 x_{2s}(1+n_c)(1+f_t)-x_{1s}n_c f_t\right].
\]

Applying the stated high-energy approximation gives
`R_b^native = C_b x_2s - D_b x_1s f_t`.
The dropped term is `C_b x_2s f_t`. In the zero-radiation limit, this reduces
to `s_A A_b x_2s`; summing the 140 spontaneous coefficients gives
`s_A (8.2206 s^-1) x_2s`, with no additional counting factor.

The May-2012 supplement, (4), and C source use departures from a Wien
reference: `Delta x_2s=x_2s-x_1s exp(-E21/T_R)` and
`Delta x_b=x_1s[f_b-exp(-E_b/T_R)]`. Direct substitution gives

\[
 C_b\Delta x_{2s}-D_b\Delta x_b
 =C_bx_{2s}-D_bx_{1s}f_b,
\]

because `D_b exp(-E_b/T_R)=C_b exp(-E21/T_R)`.
This is a coefficient-level algebraic correspondence within the native
approximations. `Delta x_b` is neither a photon-cell count nor `df_b/dt`.
In particular, the native Wien null and an exact Planck null of the separate
full paired action are different statements.

The existing `PhysicalTwoPhotonRamanBin` retains the full `(1+f_t)` factor and
accepts supplied companion occupations. Its correspondence to original native
storage is therefore conditional, not an unconditional byte/source identity.
The table does not establish its directional kernel or its eventual physical
deposition. No production API is changed to close this difference.

## Historical comparisons and fresh verification

`HISTORICAL_EXECUTION`: the v0.68 final receipt is dated
`2026-08-08T13:15:45.747535Z`, payload head
`fc4b1cede1bf91d92a88f00afedfe3f56e604d5e`. Its archive seal and all 29 member
hashes were checked in this turn. The recorded C-comparison maximum relative
residual is `1.634693744337258e-14` over the stored `(311,6)` harness array.
The prior receipt also reports eight targeted tests. These are historical
numbers and are excluded from this turn's fresh test count.

The v0.68 runner compiles the original `hydrogen.c`, calls its actual
`read_twog_params`, and evaluates transcribed coefficient formulas in
`original_hyrec_two_photon_raman_harness.c`. That harness does **not** call
`populateTS_2photon`. A separate full-matrix harness does call that function,
but is only inspected here. Neither historical result proves a physical
`B`, `mu`, all-photon counting map or exact full paired-action correspondence.

`NUMERICALLY_CHECKED`: fresh extraction produced all 140 rows, exact CSV
round trips to the loader, an independent 70-digit decimal normalization
reference, ordered source/line identities, and the expected half-domain
inequalities. Other coefficient columns and the Raman rows are unchanged.
The loader arrays also equal the stored v0.68 arrays bit for bit on this host.
The existing canonical-table test passed once in the available external venv.
The default-runtime attempt failed before collection because pytest was absent.
Both attempts are recorded. No C comparison, historical runner, deposition,
trajectory or provider test was re-executed.

## Owner review boundary

The existing `COMSourceDepositionPlan` requires
`df[i,a]/dt = n_H/mu[i] sum_s B[i,s] R[s,a]`, with `B` dimensionless,
`n_H` and `mu` in `m^-3`, and input `R` in photon packets per H per second.
Its columns each count one declared source packet, satisfy `sum_i B[i,s]=1`,
and match that packet's energy. These numerical constraints do not identify
the physical target representation or a unique physical map.

The review contract leaves six obligations open: original integration regions;
event/photon counting and companion closure; field/population/reference
authority; target measure; deposition-map law; and angular/derivative scope.
The next action is one owner review of those inputs and their source authority.
Document acceptance alone does not authenticate them. Actual `B`, `mu`, target
boundaries, packet arrays and directional weights remain null. Physical-input
authentication, provider/face admission, ready/merge and science promotion
remain false.
