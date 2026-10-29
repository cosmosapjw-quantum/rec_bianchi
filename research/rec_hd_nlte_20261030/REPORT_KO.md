# BASS/REC 실제 분자 데이터 우선 연구 | HD 2021 LAMDA 충돌·복사 냉각

## 핵심 성과

2021년 LAMDA HD 데이터의 공식 텍스트에 실제 존재하는 9개 에너지 준위, 8개 방사선 전이, 2×9×3=54 충돌계수 값을 전사하고, 물리적으로 조건을 선언한 HD 준위 냉각 계산 126개 및 전체 줄별 방출량 504개를 생성했다. 본 연구의 최우선 목표는 실제 물리 데이터 생성이며, 코드 최적화·GPU 벤치마킹은 시행하지 않았다.

- **실제로 source-gate를 통과한 부분:** J1→0의 내부 에너지/표기 광자 주파수 차이 -8.2410162 Hz는 기존 35 Hz 내부 정합 기준을 통과한다. A10=5.442×10^-8 s^-1, q10 at T=[50,100,200] K = [2.2,2.7,3.9]×10^-11 cm³ s^-1. para/o-H₂ 모두 동일하다. 정상 2준위 P10(n,T)와 반포화 밀도를 직접 유도·실행했다. 한 HD 분자당 정확한 모델 조건에서 산출한 **optically thin collisional cooling power**, not a measured intensity of actual gas.
- **새로운 구별:** J1 2준위에는 f_ortho 비율 의존성이 **0**지만, 실제 source가 다른 고회전 준위 9준위 계에서는 200K, nH₂=100 cm^-3에서 순수 o-H₂ vs 순수 p-H₂ 총 혼합-source 광자 파워 차이가 약 +0.8942%라는 *source-policy-unqualified* 정량 진단이 나타난다. 2준위 결과의 과잉 일반화를 배제한다.
- **검산:** Python 22/22 일반 및 최적화 -O PASS, compileall PASS, Wolfram exact SI/위상·온도 산술, 독립 mpmath 80 digits 63/63, 냉각 상대 오차 최댓값 2.1014e-11; PNG 3개 직접 검토.
- **DAG:** 신규 별도 auxiliary research overlay 1/2 (J1 2-level model scoped pass; 9-level source reconciliation partial). `REC-EXP-SPECTRAL` 실제 충돌계수 및 상태 모델 증거는 증가했지만 기존 중앙 DAG **28/88 (+0)**, REC physical **0/313 (+0)**. H5 ε null, H6/H7 OPEN, L4·REI false, production HOLD. R/C scoped 18/20, 실제 별개 작성자 R6/C9 NOT_RUN.

## 수치 (출처 필드 고정, 외부 복사장 없음)

| T (K) | n_half (cm^-3) | high-density P10 (W/HD) | nH₂=1e4 cm^-3 P10 (W/HD) |
|---:|---:|---:|---:|
| 50 | 2010.820708 | 1.8047135542e-29 | 1.5025730531e-29 |
| 100 | 1100.821467 | 4.3776011109e-29 | 3.9434929421e-29 |
| 200 | 541.081264 | 5.9054673829e-29 | 5.6023355052e-29 |

Full-nine diagnostic at T=100K n=1e4 cm^-3 and f_ortho=0.5: P_printed ≈8.20244e-29 W/HD; this **is not** production-approved because J2–J8 source line νE vs νP gate FAIL. Full 9-level density/ortho grid is provided as physical theory investigation, not certified optical cooling, fitted source or cosmological history.

## Physical data and limits

- `data/LAMDA_HD_SOURCE_TRANSCRIPTION.json` 9 levels, eight A/ν, 54 collision literal entries, two historic 2022 lab combination constraints, provenance.
- `evidence/J1_TWOLEVEL_COOLING.csv` 63 physically explicit two-level points, with source first-line 35Hz gate passed under the prior policy.
- `evidence/HD9_CONDITIONAL_COOLING.csv` 63 9-level source-policy diagnostic points with validity flags; `HD9_PERLINE_PHOTON_OUTPUT.csv` 504 channel values.
- `evidence/LAMDA54_COLLISION_VALUES.csv` 54 original printed collision numbers at actual temperature nodes; `evidence/NONLTE_GRID.json` complete finite 126-row data.
- `evidence/INDEPENDENT_MPMATH.json` independent 80-digit check; 3 diagnostic plots. Figures annotated so full9 cannot be confused with physical source admission.

The 2021 data are not equivalent to new experimental measurements of those 54 rates: the collisional coefficients are Flower (1999) calculations as republished in LAMDA. These are real source-derived physical input coefficients, not newly measured collisions. The 2022 laboratory intervals are separate measured spectroscopy, cited but not artificially re-fitted into the 2021 original source. Not every standalone 9-level rate/line is production-physical because seven line energy gaps differ from printed photon frequencies beyond original 35Hz.

The official accessible source was read as **flattened text**: original private 2289-byte data was not reacquired or byte-hashed this turn. Historical SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb` is provenance only, not a new byte-identity claim. Original CDMS 2011 v2 .cat/.egy/.fit/.lin/.par remained inaccessible via current tooling; 2019 and 2026 catalogs were not substituted.

## Cross-repository integration and next scientific step

Current branch survey: REC PR160; REI PR271 (Puchwein19 physical event ledger), BASS PR258 (Einstein–Vlasov physical histories), BASS_HE PR113 (source-exact EXFOR), CR PR125/126 (actual recombination photon spectrum / dual oracle), WU PR164 (GL2022 reactive state branching). They are research siblings, not automatically source-consistent with REC 2021 HD collisional model. No cross-repo physical kernel/power integrated.

Next source-first milestone: authentic CDMS Dec2011 v2 raw/covariance & full original LAMDA bytes, obtain owner native J1 injection interface with units and optical-depth, then source-consistent expansion to J2–J8 without changing old gate. No old full IVP reruns, arbitrary heating, main merge, force push or production source choice.

## Scientific sources

1. Official LAMDA 2021 HD file, `https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat` and `https://home.strw.leidenuniv.nl/~moldata/HD.html`.
2. Flower 1999 HD-H₂ quantum collision, `https://doi.org/10.1088/0953-4075/32/7/016`.
3. Cozijn, Diouf & Ubachs 2022, `https://doi.org/10.1140/epjd/s10053-022-00552-x`.
4. Cozijn et al. 2022, `https://doi.org/10.1103/PhysRevA.105.062823`.
5. Neufeld 2026 HD non-LTE, `https://doi.org/10.3847/1538-4357/ae851a`.