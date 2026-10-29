# REC-HD-1984-LAB-GRAPH: 실제 고회전 실측 3개와 기존 2022 조합차 2개의 관측 제약

**2026-10-30 / 1차 출처 보존 / 신규 연구 단위 / DRAFT-HOLD**

## 성과

원래 2022 실측 조합차 두 개에 더해 Essenwanger & Gush 1984 원논문 출판사 초록의 HD v=0 pure rotational `R(3)`, `R(5)`, `R(6)` 세 전이 주파수와 보고 오차를 신규 물리 입력으로 가져왔다. 첫 세 개의 실제 실측 파수는 각각 **350.852 ± 0.002**, **514.656 ± 0.001**, **591.9327 ± 0.0003 cm^-1**. 이는 parent에서 추정한 값이 아니라 원논문 초록 literal이다. 1984는 출판연도이며 페이지 온라인 게시연도 2011과 구분한다.

| 신규 1984 실측 | ν_meas (Hz) | 보고 ± (Hz) | ν_meas − 2021 photon (MHz) |
|---|---:|---:|---:|
| J4−J3 | 10,518,278,347,421.600 | 59,958,491.600 | −28.7337784 |
| J6−J5 | 15,428,998,726,444.800 | 29,979,245.800 | +433.1123448 |
| J7−J6 | 17,745,695,910,357.6600 | 8,993,773.7400 | +0.00685766 |

2011 CDMS `.egy` 인쇄 준위차와의 잔차도 별도 저장, 원본 2021 photon `νP`와 term-energy `νE`를 혼동하지 않음. `J6−J5`의 433 MHz 차이는 중심값 대조일 뿐 1984 실험과 CDMS fit의 공동 공분산이 없고 1984 자료가 역사적 fit에 포함됐을 수도 있으므로 **σ 또는 χ²로 해석 불가**. `source_2021_photon_A`는 실제 LAB1984의 Einstein A 측정값이 아님.

## 수학·과학 결과

다섯 **실측 제약의 incidence 행렬** rank=5, nullity=4; 전체 9 준위가 4개의 연결 그룹 `{0,2}`, `{1,3,4}`, `{5,6,7}`, `{8}`로 나뉜다. 옛 CDMS/LAMDA `J1−J0` frequency를 **조건부 nominal anchor**로 가정할 때 rank=6, nullity=3, 그룹 `{0..4}`, `{5..7}`, `{8}`가 된다. 이 앵커는 별개 신규 관측이 아니다. 현재 보유 근거로 8개 실측 독립 회전선 전체를 식별할 수 없고, 추가적인 `J5−J4`/`J8−J7` 사이의 연결(그리고 2011 nominal anchor의 측정 원문 불확도)이 필요하다. 이것은 그래프 선형 대수 결과이지 강한 물리 no-go가 아니다.

새 물리 관측량으로 1984 **3개 직접 실측 광자 에너지/파장 및 오래된 Einstein A로 계산한 조건부 spontaneous photon power**, T=50/100/200K에서 9개의 조건부 LTE 상하준위 비를 생성했다. 이 값들은 진짜 분광 측정에 고정된 benchmark지만 천체 non-LTE 점유도·HD heating/cooling history가 아니다.

## 실행 검산

- Python 15/15 일반 및 15/15 `-O` PASS, `compileall` PASS, 3 실제 데이터 기반 PNG 생성 및 시각 검토.
- Wolfram exact incidence rank/nullspace 및 5 실측−source 주파수 잔차, 단위 환산, 조건부 LTE 샘플 검산. 진짜 별개 저자 독립검토는 NOT_RUN.
- 보존된 첫 실패: C5의 CSV fieldname union 오류로 output writing FAIL, 입력과 gate 그대로 두고 구현만 고쳐 PASS.
- PR162 source ZIP SHA256 `9755195a46b997f016103ef37f29dcac305337215ec434c5f6352a74b1c0afaf`, 원본 ZIP을 새 full source package 안에 그대로 포함. 새 DATA/코드 경로 별도 격리, producer/parent/main/외부 repo 변경 없음.

## DAG·gates

`REC-EXP-SPECTRAL`에 **신규 실측 direct line 3개** 입수 및 **기존 2개 재사용**, `PARTIAL_FIVE_LAB_MEASUREMENT_EQUATIONS`라는 신규 evidence overlay를 제안. 원래 노드를 완료했다거나 8개 전이 전체를 실측 재구성한 것이 아님. Canonical `28/88 (+0)` / REC physical `0/313 (+0)`. `original 35Hz=FAIL7/8`, `CDMS2011v2 raw=NOT_ACQUIRED`, `2011 original fit covariance=null`, `H5 epsilon=null`, `H6/H7 OPEN`, `L4=false`, `REI=false`, `production=HOLD`, `auto_next_node=false`. R6/C9 distinct author 미수행.

## 다음 최소 물리 연구

CDMS 2011 v2 `.fit/.par/.lin/c003501i.cat/c003501.egy` 원본 바이트 및 joint covariance 복원, Drouin 2011 J1−J0 측정오차 provenance 확보, 1991 Ulivi의 실측 transition 값과 불확도 원문 확인, 역사적 1984 J6−J5 큰 residual의 원 자료/fit residual 여부 구별. 그 후 원본 source의 전이별 공동 불확도를 계산하여 2022+1984 실측을 합친 검증된 관측 제약 연결을 검토한다. 2019/2026 CDMS로 자동 전환 금지.

## 인용 원전

- Essenwanger & Gush 1984: https://doi.org/10.1139/p84-213
- Cozijn et al. EPJD 2022: https://doi.org/10.1140/epjd/s10053-022-00552-x
- Cozijn et al. PRA 2022: https://doi.org/10.1103/PhysRevA.105.062823
- CDMS 2011 v2 index: https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/
- LAMDA source provenance: https://home.strw.leidenuniv.nl/~moldata/HD.html
