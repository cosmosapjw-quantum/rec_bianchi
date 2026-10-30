# REC-HD 15-level CMB line transfer: scoped parent-locked startup

PROJECT=cosmosapjw-quantum/rec_bianchi
PARENT_PR=173
PARENT_HEAD=90d883c77b3823322f2ecdb09888442b9a620a97
UNIT=REC_HD_NEUFELD2026_CMB15_FULLLINE_TRANSFER_20261030
SCIENTIFIC_GOAL=Source-locked J0..14 non-LTE HD with CMB: actual radiative emissivity/opacity, line-optical-depth thresholds, signed excess surface brightness for all 14 lines, finite-column formal transfer under fixed populations; optional FLRW (1+z)^-4 brightness mapping explicitly conditional.

PHYSICS_DEFAULTS=metric(-,+,+,+), exact h,c,kB; CMB T=2.72548(1+z) K; exact original Neufeld2026 v2 source temperature knots; para/ortho H2 0.25/0.75, no chemical abundance model; homogeneous isothermal plane-parallel slab, Gaussian Doppler line with free microturbulence parameter; fixed optically thin excitation populations. No input observed spectra; no fabricated covariance or source model switching.

PROTECTED=Original CDMS2011 v2 35Hz FAIL7/8, owner/consumer source unchanged, parent/sibling untouched, no merge or production, canonical DAG 28/88 and REC physical DAG 0/313 unchanged unless separately verified admission.
INPUT_BLOCKED=Neufeld2026 Zenodo v2 posterior_isobaric.csv.gz and posterior_isochoric.csv.gz publicly available, but source-byte acquisition via current tool path failed; no computed observational/posterior claims.
NATIVE_SUBAGENT=NOT_RUN; no native delegation tool advertised in active call inventory.
