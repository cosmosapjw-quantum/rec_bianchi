# REC-HD-FIELD-SEMANTICS01: 이론·코딩 연구 결과 (2026-10-29)

**Owner** `cosmosapjw-quantum/rec_bianchi` · **parent** PR154 `2b86465fe641977aa8a584ed4fb66888fd300929` · **범위** LAMDA 데이터 필드의 계산상 권위와 선택된 광자 주파수에 따른 국소 선 중심 복사 계수. 기존 PR150–154를 반복하지 않고, production Einstein–Boltzmann solver/물리 rate는 수정하지 않았다.

## 1. 핵심 발견과 출처

LAMDA의 공식 [data format](https://home.strw.leidenuniv.nl/~moldata/molformat.html)은 준위 에너지, 통계 가중치, Einstein A와 충돌 계수를 기본 데이터로 정의하고, 인쇄된 `FREQ(GHz)`를 문서에 설명된 프로그램에서 사용하지 않는 선택적 추가 정보라고 명시한다. 그러나 [myRadex](https://github.com/fjdu/myRadex)는 2021-11-25 이후 인쇄된 입력 주파수를 기본 사용하며 `recalculateFreqWithEupElow`로 선택할 수 있다고 명시한다. [pythonradex](https://pythonradex.readthedocs.io/en/latest/notebooks/reading_LAMDA_files.html) 역시 `read_frequencies=True` 옵션을 명시한다. 따라서 **데이터 형식의 의미론과 소비자 코드의 실제 주파수 선택 정책은 동일한 것이 아니다.** 이것은 문헌으로 지지되는 사실이다.

PR154의 Drive 백업 SOURCE ZIP 259327 bytes, SHA256 `972e2e31683a3947ab582a687a63a4c048b12f4086a6ad41345effc1d547fcc2`를 현재 호스트에서 다시 가져와 ZIP CRC를 검사했다. 내부 원본 `private_inputs/hd.dat`는 2289 bytes, SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`로 기존 고정값과 일치한다. 9준위, 8 복사 전이, p/o-H2 각각 9 충돌 행을 원문에서 파싱했다. 이 원본 파일은 사용자 관리 비공개 SOURCE 백업에만 포함하고 공개 Git에는 게시하지 않는다.

## 2. 정확한 수학적 결과

`P_core`는 에너지·통계 가중치·A·충돌율 등 필수 필드의 canonical projection이고 `P_meta`는 출력용 주파수·상준위 온도 필드다. 어떤 소비자 계산이 `F=f∘P_core`로 구현돼 있다면, `P_meta`만 바꾸는 입력에 대해 F는 불변이다. 이는 **그런 구현을 실제로 확인했을 때에만** 적용되며 REC/BASS/REI 전체에 자동 적용되지 않는다.

고정 A, 점유수, Gaussian Doppler 속도폭 σ_v와 각 정책의 자체 선 중심에서 ν_E=100c(w_u−w_l), ν_P=10^9ν_print를 비교하면

    j_peak,P / j_peak,E = 1,
    alpha_peak,P / alpha_peak,E = (nu_E/nu_P)^3,
    S_peak,P / S_peak,E = (nu_P/nu_E)^3,
    integrated_j,P / integrated_j,E = nu_P/nu_E.

LTE 준위 점유에서는 Sν/Bν(T)=expm1(hν/k_BT)/expm1(ΔE/k_BT). 이 식은 PR150의 조건부 Kirchhoff mismatch를 재현하지만 기존 24-case campaign을 다시 실행한 것이 아니다. 중심 emissivity가 불변이어도 주파수 적분 emissivity는 불변이 아니다. 또한 고정된 **주파수폭**을 사용할 때에는 중심 emissivity 비율이 ν_P/ν_E로 바뀌므로 속도폭 가정이 필수다.

원본 소수 문자열을 정확한 Fraction으로 계산한 여덟 행의 선 중심 흡수 계수 상대 차이:

| J→J−1 | alpha_P/alpha_E−1 (ppm) |
|---|---:|
| 1→0 | −0.0000092423 |
| 2→1 | −0.5332463622 |
| 3→2 | +0.4090880119 |
| 4→3 | −0.0135841467 |
| 5→4 | +0.2870752679 |
| 6→5 | −0.3553614231 |
| 7→6 | +0.2385714660 |
| 8→7 | +0.0010319691 |

최대 절대 상대차는 **5.332463622370740788...×10^-7**, J=2→1. Wolfram의 exact-rational 비교가 같은 행·값을 재현했다. 수치는 물리적 불확실성이나 관측 오차가 아니라 **두 명시적 주파수 정책의 조건부 응답 차이**다.

## 3. 실제 구현과 검증

`field_semantics.py`는 원본 SHA/바이트 확인, HD 구조 파싱, core SHA와 metadata 분리, 선택적 FREQ 부재 허용, 정확한 분수 비율 계산, machine-readable JSON 저장을 수행한다. `tests/test_field_semantics.py`의 **16/16 PASS**는 source hash 거부, metadata-only mutation에 대한 core 불변, A/충돌율 mutation의 core 변경, NaN/Inf·음수 A·잘못된 partner 거부, Fraction 비율 항등식, mpmath 직접 Einstein B/Gaussian kernel 대조를 포함한다. 수치 직접 대조는 T=100 K, σ_v=1200 m/s의 제한된 사례이며 고유한 물리 원자료가 아니다.

그림은 여덟 행의 이산 값을 표시하며 J1의 아주 작은 값이 `−0.0000 ppm`으로 반올림되어 보이던 최초 표현을 과학적 표기법으로 교정하고 PNG를 다시 열어 확인했다. Figure는 원본 데이터로부터 유도한 **조건부 계산 결과**이며 관측 그림이 아니다.

## 4. 별도 저장소/브랜치 의존성

- REC PR148 H5 thermal bridge, PR149 H–Li registry, PR150 24-case thermal, PR151 26-channel stationarity, PR152 cycle rank, PR153 print precision, PR154 joint interval은 기존 독립 소유자와 immutable 결과를 유지한다.
- WU088_HH PR155의 H+ + HD(v0,j2) → D+ + H2(v0,j1) 반응율은 **reactive collision source**이며 여기서 다루는 중성 HD 복사선 주파수의 CDMS 분광 원본을 대신하지 않는다. 해당 저장소는 자체 DAG 34/49를 보고하므로 중앙 REC 28/88과 혼동하지 않는다.
- BASS PR239 CE1-F의 angular-source enclosure, REI PR260 UVB 조건부 신뢰구간, bass_cr PR119와 BASS_HE PR104는 각 소유자의 범위에만 적용한다. REC에 새 물리 rate/provider를 수입하지 않았다.
- 이전 대화와 PR154 handoff의 28/88, REC 물리0/313, H5 epsilon=null, H6/H7 OPEN, L4=false, REI activation=false, production HOLD를 유지한다. 전체 비공개 대화와 모든 local dirty tree를 읽었다고 주장하지 않는다.

## 5. 남은 source blocker와 다음 작업

CDMS 2011 v2 원본 `.cat/.egy/.par/.fit/.lin`의 바이트·SHA·QN·TAG·uncertainty·LAMDA 변환 lineage는 여전히 미확보. 기존 PR154는 공식 HTTP503을 기록했으며, 현재 호스트의 직접 HTTP 시도는 DNS failure이고 Exa는 raw archive bytes를 제공하지 못했다. 2026 CDMS v3를 2011 v2로 대입하지 않는다.

따라서 **두 독립 후속 작업**을 구분한다. (1) `REC_HD_CONSUMER_CALLSITE_AUDIT`: REC/BASS/REI의 실제 코드에서 FREQ와 level-energy 선택, line-centre profile, Einstein B, source-frame Doppler/clock을 추적한다. (2) `CDMS_V2_SOURCE_RECOVERY`: 2011 v2 원파일의 출처를 확보한 뒤에만 물리적 source-choice proposal을 연다. 어느 쪽도 자동으로 H5/H6/H7 또는 중앙 DAG를 승격하지 않는다.

## 6. 판정 및 보존

- `PASS_SCOPED_FORMAT_SEMANTICS_AND_CONDITIONAL_LINE_CENTRE_KERNEL`.
- native subagent NOT_RUN; R6/C9 독립 비저자 심사는 PARTIAL. Wolfram/mpmath 교차검산은 알고리즘 수준의 독립성이지 다른 저자의 과학 심사와 동일하지 않다.
- 새 scoped R/C 총 20단계 중 **18개 완료, R6/C9 부분**으로 기록한다. 각 단계 Git 커밋·provider 백업의 실제 성공 여부는 `delivery/`의 영수증에서 판정한다.
- 중앙 canonical **28/88(+0)**, REC physical **0/313(+0)**, H5 epsilon=null, H6/H7 OPEN, L4=false, REI_activation=false, production HOLD. No merge, no production mutation, no old native/IVP/9×9 stationary replay.
