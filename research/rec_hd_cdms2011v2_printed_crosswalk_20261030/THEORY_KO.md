# REC HD | 2011 CDMS v2 printed-energy crosswalk, theory (2026-10-30)

## Source and authority

Parent PR161 HEAD `5bf22a4258ba571e8aebb1cfedab9cafe7ac6481` is the isolated reference for the 2021 LAMDA source numeric transcription, whose historical 2,289-byte `hd.dat` SHA-256 was recorded earlier but NOT newly reacquired. PR160 `0a8a0bcf740da6e4a2acda9d4fd071f7ed8e2691` owns the two real 2022 laboratory constraints. **New independent actual source input:** the official `CDMS/classic/entries/archive/H2/vers.2/c003501.egy` first nine *v=0* energies for J=0..8, archived as dated 2011-12-07. The official source-rendered text was read in this run via Exa and manually checked, but the raw original `.egy` bytes and SHA were not acquired. Neither the 2019 `c003501.cat` nor the 2026 v3 was used. `HD.par` printed 2011 coefficients are available as source-rendered text; `HD.fit` full original fit covariance remains NOT_ACQUIRED.

The nine archived printed wavenumbers in cm^-1 are

`0.000000, 89.227932, 267.069695, 532.310797, 883.163755, 1317.309216, 1831.950769, 2423.883469, 3089.576062`.

They are printed to six decimal places in cm^-1. `E_0 = 0` defines the relative energy zero. The source's *listed level marginal errors* are separate from the decimal-display widths and from the unprovided full joint fit covariance.

## Research construction, R4–R5

Let `F_j` be the inherited 2021 LAMDA *printed-photon* frequencies in Hz for J -> J-1, j=1..8. Let `e_j^CDMS` be the displayed 2011 v2 `.egy` term energies in cm^-1. Use exact SI c=299792458 m/s, so K = 100 c Hz/(cm^-1). Construct the unique ground-anchored *photon-integrated* nine-level vector

\[
 e^*_0=0,\qquad e^*_j=K^{-1}\sum_{k=1}^{j}F_k.
\]

A single underlying level-energy vector can represent *all eight* printed photon differences while rounding to the displayed `.egy` wavenumbers if and only if all `|e^*_j-e_j^CDMS| <= 0.5 × 10^-6 cm^-1` simultaneously (assuming conventional rounding-to-nearest and a fixed ground zero). A separate line-by-line check `|F_j-K(e_j-e_{j-1})| <= K ×10^-6` is necessary but not sufficient, since it may require inconsistent shared levels. The construction explicitly checks the stronger global condition.

**Calculated result:** all 8/8 excited levels satisfy the single-vector global print-cell test. Maximum absolute level offset = `0.00000048713770511198116931947634253027139195076081600425051386 cm^-1`, i.e. `14,604.021 Hz`; minimal remaining print-cell slack = `0.00000001286229488801883068052365746972860804923918399574948614 cm^-1`, i.e. `385.6019 Hz`, at J=4. The largest difference between an individual printed `.egy` gap and the LAMDA printed photon is `24,917.6546 Hz` (J=2); this is below the `29,979.2458 Hz` maximum two-cell *display rounding* difference. The eight inherited printed photon frequencies each have eight digits after the decimal in GHz, i.e. a last-decimal half-width of 5 Hz, far smaller than the 385.6 Hz bottleneck for the joint representation.

This is **representation-level reconciliation of two historical source presentations**, not an experimental fit result, and does **not** establish raw identity, line uncertainties or a physical gas/radiation history. It does, however, show that the v2 `.egy` printed levels do *not* themselves create an additional eight-line inconsistency with LAMDA printed photon frequencies at the six-decimal precision. The original LAMDA **term-level** field vs photon 35Hz gate still FAILS 7/8. That gate involves the different, more precise LAMDA term energies and is not modified or replaced.

## Two 2022 measured ground-state combinations

Original laboratory measurements:

- Cozijn et al., EPJD 76, 220 (2022), DOI 10.1140/epjd/s10053-022-00552-x, `(J2-J0)_v0 = 8,006,533,168(26) kHz`.
- Cozijn et al., PRA 105, 062823 (2022), DOI 10.1103/PhysRevA.105.062823, `(J3-J1)_v0 = 13,283,245,098(30) kHz`.

Differences `experiment minus 2011 .egy printed term gaps` are respectively `-14,864,136.031 Hz` and `-45,021,603.217 Hz`. Differences `experiment minus 2021 LAMDA printed photon combinations` are exactly `-14,877,400 Hz` and `-45,034,200 Hz`. Source printing bounds are orders smaller than these nominal discrepancies, so **display precision alone cannot eliminate them**, but joint fit uncertainty/covariance, inter-publication systematics and older catalog model error remain unknown; neither a sigma-level significance nor a statistically fitted eight-line replacement is inferred. In particular the two measurements constrain only rank-2 combinations of three adjacent lines, with nullspace `(1,-1,1)`.

No prior 35 Hz gate, catalog version, source default or production parameter is changed.

## Covariance formulation for future source owners

For measured constraints `y = M ν`, `M=[[1,1,0],[0,1,1]]`. Under a source model `ν=f(θ)` with parameters θ and genuine covariance `Cθ`, a new measurement covariance `Cy`, and any documented cross-source covariance `Ccross`, the residual covariance should be `Cy + M J Cθ J^T M^T - cross terms` with `J=∂f/∂θ`. Neither joint matrix has been obtained. The `.egy` marginal uncertainty column alone is insufficient to reconstruct the full matrix or an authoritative eight-line fit. The displayed decimal rounding cell is **not** a Gaussian uncertainty.

## Gate and scientific status

- **Derived, independently Wolfram-checked:** global simultaneous 8/8 printed-energy compatibility; 8-line/9-level source output; exact two lab-source differences.
- **Acquired evidence:** official 2011 v2 readable text (first nine v0 `.egy` levels) and the older source numeric transcription. Raw original CDMS `.egy/.cat/.par/.fit/.lin` bytes NOT_ACQUIRED.
- **Auxiliary scoped DAG:** one newly completed source-text crosswalk node out of two (1/2); second original raw/covariance node OPEN.
- **Canonical DAG 28/88 (+0), REC physical DAG 0/313 (+0)**. H5 epsilon=null, H6/H7 OPEN; 35Hz FAIL7/8, L4=false, REI=false, production HOLD. Independent different-author R6/C9 NOT_RUN.
