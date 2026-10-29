# REC-HD-LAB-COMBINATION-20261029 | 실제 분광 데이터와 소스-물리 연결 결과

**목적:** 이전 PR159의 guard/callgraph 개선을 반복하지 않고 2022년 공개된 실제 HD 분광 측정값을 2021 LAMDA 계열 frozen 8 전이의 관측과학적 근거로 도입한다. 총 **2개 고유한 실험 combination-energy constraints**를 현재 연구 evidence로 추가했으며 생산 임계 승인은 하지 않는다.

## 실험과 이전 소스의 정확한 수치 대조

| 실제 실험 v=0 준위 | 실험 2022 (kHz) | 실험 보고 불확도 (kHz) | 2021/2011-source printed νP 조합 (kHz) | 실험−소스 (MHz) |
| :-- | --: | --: | --: | --: |
| J2−J0 | 8,006,533,168 | 26 | 8,006,548,045.4 | **−14.8774** |
| J3−J1 | 13,283,245,098 | 30 | 13,283,290,132.2 | **−45.0342** |

이는 같은 `v=0` HD 준위에 대한 **실험 측정값과 오래된 원소스의 photon transition 주파수합**의 산술 차이이며 새 실험 데이터가 실제 생산 코드에 연결되었다는 의미가 아니다. 직접 측정한 2022 원본 두 조합차의 DOI와 처리를 `data/LAB_ANCHORS.json`에 명시했고, 이전 소스 8개 전이의 Einstein A/νP/νE는 원래 `PR156 RESULT.json` blob의 전사본에서 가져왔다. 원본 raw CDMS 2011 v2가 없어 역사적 fit 오차·공분산을 계산하지 못한다. 이 차이를 '500σ' 식으로 해석하거나 관측된 cosmic drift, gas heating, HD 반동 문제의 해결로 해석하면 안 된다.

## 물리량 생성

- **8개 HD photon data rows:** 실제 frozen source의 `A_J`, `ν_P,J`로부터 `hν_P`, `λ=c/ν_P`, `τ=1/A`, `P=A hν_P` 및 T=50,100,200 K의 blackbody photon occupation 계산. J1 photon λ≈112.0725 μm, 1 upper HD의 spontaneous photon power ≈9.64575209×10⁻²⁹ W. 이 표는 source-only photon physics이며 gas density, all-level population, radiative cooling history가 아니다.
- **실험에 고정된 두 LTE 비:** 독립적인 진동 v=0 ground-state difference를 사용, 50/100/200 K에서 `n2/n0 = 0.00229821658 / 0.107196469 / 0.732108150`, `n3/n1=6.77272836×10⁻⁶ / 0.00397530286 / 0.0963104702`. LTE가 성립하면 성립하는 physical benchmark 값이지만 실제 초기우주 HD 분포를 관측한 값이 아니다.
- **조건부 2011 ν10 앵커 분해:** J2−J1 = 5,331,547,074,000 Hz, J3−J2=7,951,698,024,000 Hz. 2022 두 실험 제약만으로 개별 세 주파수는 rank 2로 불식별이며, 이 값들은 기존 J1−J0 nominal anchor 추가 후에만 성립한다. fit covariance를 모르는 상태에서는 derived error bar를 만들지 않는다.

## 실제 검산과 출처 상태

- Python 19/19 unittest 일반·`python -O` 각각 PASS, `compileall` PASS, exact `Fraction`/80-digit `Decimal` 사용. Wolfram `rank=2`, `null={1,-1,1}`, 두 실험-소스 잔차와 3온도 열평형 인구비 일치.
- 실제 소스 값 조작 시 reject하는 failure controls 포함. 전이원본 35 Hz `FAIL7/8`은 변경하지 않음.
- 3개의 데이터 기반 그림 생성 및 시각 검수: 실험 조합 잔차, 두 LTE 비, 고정 소스 Einstein A와 photon power. 모델 불확도를 제공하지 않는 그림에 실험 불확도만 표시하여 오해 방지.
- SciSpace/Exa로 원전과 LAMDA/CDMS provenance 조사, 실제 원전 공개 텍스트 확인. 공식 CDMS Dec2011 `.cat/.egy/.par/.fit/.lin` 원바이트 취득 실패, 2019 archive file 및 2026 v3 파일로 대체하지 않음. 2026 Zenodo Neufeld dataset은 다른 신규 소스로 확인했으나 이 계약의 2021 `hd.dat` 대체가 아니므로 import 안 함.

## DAG 판정

기존 canonical DAG **28/88 (+0)**, REC physical DAG **0/313 (+0)**. 실제 `REC-EXP-SPECTRAL` 입력에 실험 조합근거 2개를 연결한 **partial evidence delta**를 파일로 생성. 이것은 근거 수준의 진전이지 원래 DAG의 scientific completion이 아니다. H5 epsilon null, H6/H7 OPEN, L4/REI false, production HOLD. R6/C9 서로 다른 저자 검사 NOT_RUN.

## 관련 repo 조사

2026-10-29 현재 REC PR159, REI PR269 (UVB source-shape and electron coupling), BASS PR256 (MPFR ABI), BASS_HE PR111 (conditional angular source ratio), CR PR124 (exact flow), WU088_HH PR163 (reactive HD Laplace bound)을 참조하였다. WU의 ionic `H+ + HD -> D+ + H2` 반응 열량은 본 중성 HD 순수 회전 광자의 Einstein A와 다른 과정이며 서로의 gate를 대체하지 않는다.

## 다음 실제 과학 작업

1. CDMS 공식 2011 vers.2의 원파일 바이트·SHA·line QN/TAG/error 및 fit covariance 확보.
2. 진짜 LAMDA 2021 original 2289B source에 맞춘 full 8개 transition의 데이터 계보 reconstruction.
3. 2022 두 실험 조합차를 포함한 source fit/line uncertainty propagation, 관측량과 실제 owner source 연결.
4. 별개 저자 R6/C9 및 production 소스 승인. 현재 자동 다음 노드 OFF.
