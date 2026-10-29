# REC HD Sung 2022: 실제 분광선과 실험 폐회로 과학 보고서

2026-10-30. 연구 단위 `REC_HD_SUNG2022_CYCLES_20261030`. PR163 `65c5c4c9105c9957418ff014d34e007e53a63b3b`을 immutable parent로 보호. 2011 CDMS v2 원바이트/원 피팅 공분산 미확보. Source Table4 render text, NOT raw PDF/scan.

## 독립 새 실험 근거

Sung et al., *Journal of Quantitative Spectroscopy and Radiative Transfer* 295 (2023), 108412 (online 2022-11-04), DOI https://doi.org/10.1016/j.jqsrt.2022.108412. 원전 Table 4의 HD(v=0) 실측 `R(0..3)` 네 선중심: **89.22792(3), 177.84141(3), 265.24055(3), 350.85401(4) cm^-1**. 각 전이별 H2 압력폭과 pressure-shift 계수 및 296 K 선강도를 `data/LAB_INPUT.json`에 원전별로 source-locked 했다. 본 논문은 line-fitting error가 total systematic error보다 작다고 명시하며 공동 covariance는 제공된 현 자료에서 확인되지 않았다.

## 9개 실제 실험 관계의 정확 물리 수학

기존 2022 Cozijn 조합차 2개와 1984 Essenwanger–Gush 직접 회전선 3개를 그대로 재사용하고 Sung 실측선 4개를 추가했다. 전이준위차 incidence 행렬 `D (9x9)`는 **rank 6, nullity 3**. 연결 성분 `{J0..J4}`, `{J5..J7}`, `{J8}`. 왼쪽 영공간 basis `C (3x9)`는 `C D=0`이고 **rank 3**.

| 관측 폐회로 | 실험 중심값만의 잔차 (MHz) |
|---|---:|
| 2022 J2−J0 − Sung(R0+R1) | **−3.921711314** |
| 2022 J3−J1 − Sung(R1+R2) | **−17.890385768** |
| 1984 R3 − Sung R3 | **−60.258284058** |

세 값은 서로 다른 실제 실험끼리의 nominal difference이며 2021 LAMDA source photon과의 과거 residual이 아니다. Cov(Cy)=C Cov(y) Cᵀ이지만 joint lab/systematic covariance 및 historic CDMS fit covariance가 없으므로 χ² 또는 통계적 sigma를 계산하지 않는다.

2022 두 조합 nominal center와 Sung R0/R1/R2 nominal center의 exact 선형 보정 `d20,d31`에 대해 `δ0+δ1=d20`, `δ1+δ2=d31`을 동시에 만족시키는 보정의 최소 sup-norm은

`min max(|δ0|,|δ1|,|δ2|) = [max(0,d20,d31) - min(0,d20,d31)]/2 = 8.945192884 MHz`.

증명: `δ1`에 관한 세 개 구간의 공통 교집합 존재 필요충분조건은 세 구간 중심 간 최대 간격 ≤2t이다. 도달 witness `(5.023481570, -8.945192884, -8.945192884) MHz`를 명시 검산했다. 296 K 논문의 calibration 설명 `better than 0.0001 cm^-1`, 즉 약 2.99792458 MHz는 모든 line-shape systematic을 제한하는 hard bound가 아니므로 이 비교도 *조건부 nominal diagnostic*에 한한다.

## 실제 source coefficient를 이용한 물리 데이터 생성

- 측정 선중심에서 `Eγ=hν`, `λ=c/ν`를 계산하고 **과거 2021 LAMDA Einstein A**를 조건부로 결합한 photon-power 기록 **4행**. A는 이 2022 연구의 새 실측 A가 아니다.
- 실제 측정한 296 K H2 collisional HWHM/pressure-shift coefficient를 이용, `ν(P)=ν0+δ_H2 P`, `HWHM=γ_H2 P`, `FWHM=2γ_H2 P`를 `P_H2={0.1,0.5,1} atm`의 **가정 시나리오**에 적용해 **12행**을 생성. 실제 실험 12개 추가나 천체 스펙트럼은 아님.
- 실제 데이터 기반 FIG1 3개 cycle, FIG2 pressure shift 그림 생성 및 육안 점검.

## 검증과 실패 기록

`python -m unittest discover -s tests -v`: **19/19 PASS**. `python -O -m unittest discover -s tests -v`: **19/19 PASS**. `compileall`: **PASS**. 첫 실패는 Hz → 파수 → Hz Decimal 왕복 나눗셈으로 생긴 꼬리 반올림이 minimax의 정확 등식 2개를 깨뜨린 구현 결함. 원본 실험 입력 및 35Hz gate는 그대로 둔 채 Hz exact-domain으로 수리했으며 최초 FAIL 로그 두 개를 보존했다. Wolfram은 exact rank 6, cycle rank 3, `CD=0` 및 minimax 숫자를 재검산. 실제 별개 저자 R6/C9는 NOT_RUN.

## 판정과 후속

`REC-EXP-SPECTRAL=PARTIAL_9_LAB_ROWS_RANK6_CYCLES3`; 보조 연구 1/2 scoped. 원 DAG **28/88 (+0)**, REC physical **0/313 (+0)**; 35Hz FAIL7/8, H5 epsilon null, H6/H7 OPEN, L4/REI false, production HOLD. 

후속: CDMS 2011 v2 `HD.fit/.lin/.par/c003501i.cat` 실제 raw와 fit covariance, Sung 저자 원 multispectral covariance 및 동일 정의/line-shape/hyperfine 처리 확보. 2019/2026 catalog 자동 대체 금지, owner 승인 없는 source switch, main/parent merge 및 heating/cosmology claim 금지.
