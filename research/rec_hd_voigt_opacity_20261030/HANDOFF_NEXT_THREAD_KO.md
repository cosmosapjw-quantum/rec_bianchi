# REC HD | 296 K Voigt 원 실측계수 사용 연구 인계

PROJECT=cosmosapjw-quantum/rec_bianchi
PARENT_PR=164
IMMUTABLE_PARENT_HEAD=e050b97b7d5c6c0929062fafd7333e0164112399
UNIT=REC_HD_VOIGT_OPACITY_20261030
NEW_SCOPED=18/20
CANONICAL_DAG=28/88
REC_PHYSICAL_DAG=0/313
AUTO_NEXT_NODE=false

Sung 2022 measured 4 line centers, 4 intensities, H2 broadening/shift coefficients reused from PR164, no new laboratory observations. New physical output: Voigt opacity/transmission from source measured coefficients at T296K, p_H2={.01,.1,.5}atm, HITRAN Nref={1e22,1e23,1e24} molecules/cm², 36 conditional cases and 7236 spectral data points. Report 3 physical science figures and peak τ/W with unit conventions. Model distinct from primary Rautian fit.

REGRESSION=Python 15/15 normal,15/15 -O, compileall PASS; Wolfram independent-method central τ and σ, profile normalized/Gaussian/Lorentz limits. R6/C9 distinct author NOT_RUN, source covariance not acquired. Original GH verify-durable-backup preexisting broad whitespace FAIL, distinguish CI from local science.

ORIGINAL_35HZ=FAIL7/8
CDMS2011_V2_RAW=NOT_ACQUIRED
H5_EPSILON=null
H6=OPEN
H7=OPEN
L4_READY=false
REI_ACTIVATION=false
PRODUCTION=HOLD

NEXT: acquire 2011 v2 raw SPFIT original files and actual fit covariance; Sung original lab Rautian spectrum and full systematic/multispectral covariance; then test with same isotope abundance and actual experimental pressure, temperature, path, line-mixing, instrument response. Never replace with CDMS 2019/2026, never alter production default, main/parent branch or old 35Hz gate, never infer observed cosmic heating/τ from model columns.

RUN:
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python src/voigt_opacity.py
python src/figures.py

After Git/Drive completion consult external final delivery ACK for exact new PR/HEAD and package SHA.
