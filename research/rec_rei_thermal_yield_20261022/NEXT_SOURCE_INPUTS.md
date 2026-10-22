# 다음 source 계약: 공명·최종 ionic yield·독립 cooling 검증

2026-10-22 KST. 이 문서는 THERM01 이후의 입력·DAG 계약이다. 기존 REC126, REI129, warm729 및 완료된 THERM01의 8 IVP를 재실행 대상으로 지정하지 않는다. 새 source를 채택하면 별도 source identity와 새 cohort를 부여한다.

## 현재 source 모형의 정확한 경계

THERM01은 5–60 eV의 **smoothed ground-state continuum**과 선언한 RR/DR fit-derivative cooling을 사용한다. `60 < 64.39 eV`는 채택한 Li I **직접 1s-hole photoionization** 채널이 닫혀 있다는 뜻이다. 이는 50–60 eV의 resonant core excitation이 물리적으로 없다는 뜻이 아니다. 그 공명과 excited-level kinetics는 이번 source 모형에서 제외되어 있다. 기존 계약의 “core excitation is zero”는 **구현된 직접 core-hole 채널의 값이 0**이라는 범위로 읽고, 실제 원자의 모든 core excitation에 적용하지 않는다. 이 명료화는 기존 계산식·배열을 바꾸지 않는다.

문헌은 Li의 50–70 eV core-excited resonances, 약 81.032 eV부터의 correlated double photoionization, 약 151.68 eV 이상 doubly excited Li+ 경로를 구분한다.[S1–S3] 따라서 다음 source 입력에는 현재 band 안의 빠진 공명과 60–200 eV 확장을 함께 명시한다. “Li K-shell 흡수마다 전자 2개” 또는 “전 구간 단일 yield”를 새 측정값처럼 넣지 않는다.

## 필요한 기계 판독 입력

| 입력 | 필수 정보와 채택 조건 |
|---|---|
| Source identity | 원 논문/데이터 DOI·URL, 실제 파일명, 취득일, 원본 byte size·SHA256, 재배포 조건, 표/열/단위 설명. 미확보 표는 `INPUT_UNRESOLVED`로 둔다. |
| Initial state | 원소, charge, configuration/term, ground/metastable 구분, isotope 적용 범위. electronic isotope equality를 쓰면 그 근사를 명시한다. |
| Cross section | photon E[eV], threshold, sigma[m²], 에너지 해상도·평균화 방법·불확도, resonance/continuum 포함 범위. `photoabsorption`, `net single-ionization`, `net double-ionization`을 다른 의미로 기록한다. |
| Final state/yield | 최종 ionic charge와 level/term, 조건부 확률 또는 해당 exclusive channel의 단면적, 자유전자 수, 잔류 excitation energy, level lifetime와 radiative/autoionizing branching. radiative return에 해당하는 zero-electron outcome도 누락하지 않는다. |
| Energy partition | 총 방출전자 kinetic energy, escaping cascade-photon energy, 잔류 excitation·ionization storage. 분광 분포가 없더라도 총에너지 장부를 닫을 수 있는 source-bound moment가 필요하다. 추정한 distribution을 원자료로 표시하지 않는다. |
| Validity/uncertainty | photon·gas-temperature·density 범위, optical-depth/escape 가정, threshold·정규화 불확도와 가능하면 covariance, missing-channel 목록. |

두 일관된 표현 중 하나를 선택한다: **total absorption × 완전한 branching distribution**, 또는 **서로 배타적인 최종상태의 channel cross sections**. 총흡수 fit에 이미 포함된 기여와 net ionization cross section을 다시 더하지 않는다. 공명의 Fano 간섭 때문에 continuum에 대한 “resonance excess”는 음수일 수 있다. 이를 독립적인 음의 확률 채널로 사용하지 않고, 채택한 **전체 물리 채널 단면적**의 비음수성을 검사한다.[S3]

각 photo event는 다음을 만족해야 한다:

\[
q_f-q_i=N_{e,\mathrm{emitted}},\qquad
E_\gamma=\Delta I_{\mathrm{ground}}+\Delta E_{\mathrm{exc}}
+\sum K_e+E_{\gamma,\mathrm{escape}}.
\]

두 번째 식은 선언한 recoil 무시 근사에서 쓴다. prompt cascade를 제거한 effective channel이면 그 cascade 이후의 최종 상태와 photon escape를 사용한다. 수명이 국소 광이온화·collision·팽창 시간에 비해 충분히 짧은지 먼저 확인하고, 충족하지 않는 level에는 별도 population/excitation-energy 변수를 둔다. 방출전자의 이후 secondary ionization·excitation·열화는 **별도** transport/deposition 과정이며, above-threshold excess energy 전부를 자동 heat로 놓는 기존 가정을 확대하지 않는다.

## 독립 cooling 검증 계약

현재 \(\beta=k_BT^2\alpha'+3k_BT\alpha/2\)는 Maxwellian moment 항등식을 rate fit에 적용한 closure다. 같은 fit의 유한차분과 analytic derivative 일치는 구현 검증이며 독립적인 물리 cooling 데이터 비교가 아니다.

우선 하나의 H/He recombination 채널에 대해 energy-resolved capture/photoionization 자료와 상세평형의 convention, 또는 독립적으로 계산된 cooling coefficient를 확보한다. 채택한 Maxwellian과 동일한 reduced-mass·통계중량·case-A·cascade 조건에서 \(\alpha=\langle\sigma v\rangle\), \(\beta=\langle E\sigma v\rangle\)를 각각 적분하고 원 fit과 비교한다. Ground-state partial 검증의 결과를 total RR 검증으로 확대하지 않는다. 그다음 He/Li의 final-state-resolved RR 및 DR 자료로 확장한다.[S4,S5]

자료를 읽은 뒤 데이터 오차와 quadrature 오차를 분리한 유한 T mesh·수용 오차를 실행 전에 고정한다. signed DR fit 항을 개별 resonance probability로 해석하지 않는다. 전체 \(\alpha,\beta\)의 양성성·정의역과 escaping recombination energy \(\chi\alpha+\beta\)를 확인하고 DR excitation을 다시 더하지 않는다.

## 긍정적 다음 DAG

| 단계 | 구체적 산출물 | 현재 상태 / 완료 조건 |
|---|---|---|
| N1 source resolution | in-band Li 공명과 60–200 eV charge/state-resolved 자료 목록·실제 파일·권위/단위 대응표 | `READY_TO_SELECT`; 공개로 확보한 자료와 저자 제공이 필요한 자료를 구분 |
| N2 finite channel contract | 확보한 에너지 구간의 exclusive channel schema와 energy/yield ledger | `INPUT_DEPENDENT`; 합확률·전하·threshold·에너지 보존 수용 기준 고정 |
| N3 cooling witness | 독립 source 기반의 H/He partial cooling 비교와 불확도 | `INPUT_DEPENDENT`; 동일 source fit 재미분과 구분 |
| N4 implementation | 새 channel adapter·필요한 level/energy state·source-domain rejection·유한 검증 | `NOT_RUN`; 채택된 source 범위만 구현하고 isotope/reflection 축약의 불변성 재확인 |
| N5 new finite histories | 새 source identity에 묶인 소수 thermal histories·energy/yield 그림·scoped review | `NOT_RUN`; N2–N4 완료 후 새 cohort를 사전 고정, 기존 완료계산 재실행0 |

2026 CCC 논문은 수치자료가 공개 게시되어 있지 않고 저자에게 요청 가능하다고 명시한다.[S3] 이번 작업은 저자에게 연락하지 않았다. 실제 파일이 없는 상태에서 digitized 근삿값이나 임의 branching ratio를 해당 논문의 원 수치표로 채택하지 않는다. 필요한 자료가 일부만 확보되면 그 구간·채널을 고정하여 N2–N4의 실행 가능한 부분을 완성한다.

## Primary sources already inspected

- **S1** Verner et al. (1996), ApJ 465,487, ground-state smoothed photoionization; Verner & Yakovlev (1995), A&AS 109,125, shell fits. Author data index: https://www.pa.uky.edu/~verner/photo.html ; paper: https://arxiv.org/pdf/astro-ph/9601009 .
- **S2** Huang et al. (1999), *Single and double photoionization of lithium*, Phys. Rev. A 59,3397. DOI: https://doi.org/10.1103/PhysRevA.59.3397 ; author PDF: https://pfwww.kek.jp/azuma/MV5.pdf . Thresholds and competing double-ionization paths are source evidence; no numerical branching table was imported in this unit.
- **S3** Müller, Kheifets, Bray & Fursa (2026), *Photoionization of the Li atom: Convergent-close-coupling calculations with a focus on two-electron removal*, Phys. Rev. A 113,033105, published 2026-03-09. https://doi.org/10.1103/l4xt-3sxy ; published PDF: https://journals.aps.org/pra/pdf/10.1103/l4xt-3sxy . Introduction: lower-energy core resonances; channel discussion: unified correlated amplitudes; p14 Data Availability: numerical data on request. The article's CC BY4.0 license does not imply an unprovided numerical dataset was obtained.
- **S4** Verner & Ferland (1996), ApJS 103,467, RR fits and partial-rate data: https://www.pa.uky.edu/~verner/rec.html .
- **S5** Badnell author RR and DR data indices, fit forms, units and final-state-resolved archives: https://amdpp.phys.strath.ac.uk/tamoc/RR/ ; https://amdpp.phys.strath.ac.uk/tamoc/DR/ .

**상태 유지:** Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false. 여기의 다음 단계는 유한 atomic/thermal source 확장이다. 모든 핵종의 완전 핵반응망·완전 열역학적 폐쇄를 완료했다는 주장을 하지 않는다.
