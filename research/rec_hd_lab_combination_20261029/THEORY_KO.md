# REC HD 실험준위 조합차 이론 연구 (R1–R10)

연구 단위: `REC_HD_LAB_COMBINATION_20261029`, 원본 보호: `rec_bianchi` PR159 HEAD `46ecb52d059e2dea156b9bca144356344db8a51a`. 우선순위는 실험 분광 데이터의 생성·활용이며, 재귀적 code hardening, ODE/IVP 또는 속도경쟁이 아니다. `(-,+,+,+)` 및 SI의 정확한 h=6.62607015e−34 J s, c=299792458 m/s, k_B=1.380649e−23 J/K를 사용한다.

## R1–R3. 실제 원자료 및 증거의 구분

- EPJD **76, 220 (2022)**, Cozijn/Diouf/Ubachs, DOI **10.1140/epjd/s10053-022-00552-x**: HD `v=0, J=2−0` combination difference **8,006,533,168(26) kHz**. 원 논문 초록·본문 §3.2의 압력·초미세구조·라인 모양 보정을 포함한 실험 결과로, 단순 R(0)−P(2) 각 nominal line center 차이를 재가공한 값이 아니다. URL https://link.springer.com/article/10.1140/epjd/s10053-022-00552-x
- PRA **105, 062823 (2022)**, Cozijn/Diouf/Hermann/Salumbides/Schlösser/Ubachs, DOI **10.1103/PhysRevA.105.062823**: HD `v=0, J=3−1` combination difference **13,283,245,098(30) kHz**. 초록에서 정확한 양자준위와 측정값 확인. URL https://journals.aps.org/pra/abstract/10.1103/PhysRevA.105.062823 및 https://arxiv.org/abs/2205.13877
- 2011 Drouin et al. 원 기초자료로 인용되는 1–0 rest frequency **2674.986094 GHz**가 2024 A&A 실제 SOFIA 자료의 관측 기본값임을 별도 확인: https://doi.org/10.1051/0004-6361/202450115 . 이 숫자는 PR156에 고정된 출력 ν_P,1과 일치하나, 이 연구에서 2011 원문 실험 공분산·전체 systematic uncertainty는 미확보이다.
- 고정된 **PR156 RESULT.json Git blob** `5a99c9e31604347cf756abb4ab3ea1a134238e0d`를 8개 radiative source line ν_P, ν_E, Einstein A 전사본으로 사용한다. 이는 `hd.dat` 원바이트 재다운로드가 아니며 구버전 full CDMS 2011 v2 `.cat/.egy/.par/.fit/.lin`도 아니다. 초기 2021 LAMDA `hd.dat` 2289B SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb` 기록은 **상속된 신원 근거**, 현재 새 raw 취득이 아니다.
- CDMS 공식 2011 아카이브: https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/ ; 2011 `c003501i.cat`와 **2019** `c003501.cat` 분리. 2026 v3와의 대체는 금지. 원바이트 취득 시도 불발, 따라서 원 스펙트럼 fit의 이론 오차/공분산 미지.

## R4–R5. 이론 구성과 정확한 조합잔차 유도

`ν=(ν_10,ν_21,ν_32)^T`를 동일 진동 기저(v=0)에서의 인접 회전전이 주파수로 둔다. 실험은 개별 세 주파수를 직접 측정한 것이 아니라 두 준위 *combination difference*에 대응한다.

`y = M ν`, `M=[[1,1,0],[0,1,1]]`, `y=[ν_20^lab,ν_31^lab]^T`. 정확히 `rank(M)=2`, `kernel(M)=span{(1,−1,1)}`. 그러므로 이 두 실험 제약만으로 개별 ν_10,ν_21,ν_32 세 수를 식별하는 것은 불가능하다. 임의의 독립된 ν_10=x 가 추가되면 `ν_21=y_20−x`, `ν_32=y_31−y_20+x`가 유일하게 결정된다.

2021/2011-source frozen printed-photon 값은 `ν_P,10=2674986094000`, `ν_P,21=5331561951400`, `ν_P,32=7951728180800` Hz이다. 실험 조합값은 `y_20=8006533168000`, `y_31=13283245098000` Hz이다. 따라서 **실험 − source printed-photon combination**은 정확히

- `Δ_20 = 8006533168000 − (2674986094000+5331561951400) = −14877400 Hz = −14.8774 MHz`.
- `Δ_31 = 13283245098000 − (5331561951400+7951728180800) = −45034200 Hz = −45.0342 MHz`.

이 잔차는 독립 두 실험의 nominal 수와 오래된 예측치를 비교하는 사실적 진단이다. **카탈로그 예측의 불확도·공분산 없이는 유의도나 fit 실패라는 주장을 만들 수 없다.** 2022 측정의 26/30 kHz만으로 χ², sigma 또는 정확한 uncertainty interval을 인정하지 않는다. 기존 35 Hz 검사는 source ν_E−ν_P의 **내부 정합성**이며 실험적 line center 정확도 gate가 아니다. 두 gate는 교환할 수 없다.

2011 old ν_10을 **조건부 nominal anchor**로 쓰면 새로운 개별 주파수 후보는 `ν_21^cand=5331547074000 Hz`, `ν_32^cand=7951698024000 Hz`이다. 옛 인접 photon ν_P로부터 각각 −14.8774/−30.1568 MHz 변화한다. 이는 **lab constraints와 오래된 한 수를 이용한 수학적 분해**이지 새 authoritative CDMS fit·생산 모델이 아니다.

공분산 정리: `u=(x,y_20,y_31)`, `B=[[1,0,0],[-1,1,0],[1,-1,1]]`이면 `ν_candidate=B u`, `Cov(ν_candidate)=B Cov(u) B^T`. 현재 전체 `Cov(u)`가 없으므로 개별 새 ν의 종합 표준불확도는 **null**이다. 26/30 kHz만 합산한 신뢰구간이나 통계적 독립 주장은 금지한다.

## R5. 실제 실험 데이터에서 물리 관측량 생성

(1) 검증된 실제 실험 준위 간격만 사용하여, **조건부 LTE**와 공통 핵스핀 상태하에서 `g_J=2J+1`을 쓰면

`n(J2)/n(J0) = 5 exp[-h ν_20^lab/(k_B T)]`,
`n(J3)/n(J1) = (7/3) exp[-h ν_31^lab/(k_B T)]`.

50/100/200 K 값은 각각 `n2/n0 = {0.00229821658, 0.107196469, 0.732108150}`, `n3/n1={6.77272836e−6, 0.00397530286, 0.0963104702}`. **실제 천체의 non-LTE 점유도 측정치가 아니다**. 밀도, 복사장, 충돌상대/시간발전 없이 LTE 조건을 가정한 정확한 함수 값이다.

(2) 각 frozen source printed-photon line에서 `Eγ=hν_P`, `λ=c/ν_P`, `τ_sp=1/A`, `Pγ,one excited HD=A h ν_P`를 계산하여 8개 데이터 행으로 저장하였다. 이 값은 실제 source에서 제공된 A, 주파수에 기초하지만 **준위 간 내부 에너지와 강제로 결합하거나 입자 수밀도 및 총 열량을 생성하지 않는다**. blackbody photon occupation `1/(exp[hν_P/(k_B T)]−1)`도 가정 T에서의 표준 함수로만 제공한다.

## R6–R10. 독립 검산과 노드 판정

실제 Wolfram exact `rank(M)=2`, `NullSpace(M)={{1,-1,1}}`, residual `{-14877400,-45034200}` Hz, 50/100/200 K LTE 값 일치. Python 정수/Fraction·Decimal 체크 및 source-value mutation negative tests 재현. 원 논문 상의 R(0), P(2) 단일 nominal 중심값의 **단순** 차이와 출판된 source-calibrated combination difference는 다르며, 실험저자의 cross-correlation 결과를 임의 재구성하지 않는다.

증거로 **2개 독립 실제 실험 조합 준위**를 신규 import했다. 기존 노드 `REC-EXP-SPECTRAL`은 `SOURCE_INPUT_PENDING` → `TWO_LAB_COMBINATIONS_IMPORTED_PARTIAL`이라는 *제안 overlay*만 추가한다. 실제 owner DAG 갱신·노드 완료·원본 CDMS fit 복원은 승인되지 않았으므로 **canonical 28/88 (+0), REC physical 0/313 (+0)**을 유지한다. R6 별개 저자 재검증은 현재 NOT_RUN이다. 본 연구는 강한 no-go가 아니며 더 많은 실제 입력을 확보할 유용한 바탕이다.
