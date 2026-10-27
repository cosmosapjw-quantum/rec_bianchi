# 병렬 blocker 연구 루프 결과 — 2026-10-26

전체 원본 DAG는 **30/88 → 32/88 (+2, 36.36%)**이다. 새로 완료한 노드는 `REC-EXP-SPECTRAL`과 `REC-FIELD`이다. 독립 검토는 두 노드의 원래 gate를 선택된 He II 연속광원 및 국소 REC callback 범위에서 충족한다고 판단했다. 중앙 통합본은 아직 27/88이며, 이 결과는 PR236 작업 브랜치의 검토된 진척이다. 분모 88, 의존성, 원본 계약, 담당자 예약과 다른 86개 노드는 보존했다. 검사 84개를 DAG 노드로 세지 않았다.

이번 산출물은 실제 저장된 상태와 실제 PW19 광원을 연결한 **21상태 국소 반응률 및 에너지 분배 plot**이다. 전체 시간 진화·복사 피드백을 포함하는 최종 all-selected-isotope/ion physical pilot은 아직 미완료다.

## 병렬 연구와 전체 목표에서의 위치

| 병렬 lane | 이번에 해소한 의무와 남은 의무 | 전체 DAG 기여 |
|---|---|---|
| 광원 → native REC | 기존 `AtomicNetwork.rates/evaluate` 안에 PW19 He II 계수를 실제 삽입하고 RHS/JVP, band 소유권 및 에너지 partner 검증 | REC-EXP-SPECTRAL, REC-FIELD 완료, +2 |
| 상태·정규화·기하 | 기존 donor NPZ 복구, z=2.479 인접 η 구간의 실제 abundance/T 보간, 고정 reference와 baryon 정규화 접합 | 두 완료 노드의 필수 근거; 별도 가산 없음 |
| 시나리오 | SCENARIO, SOURCE_ABSORBER_MATRIX, COVERAGE_DELTA를 실제 상태·21개 identity·24개 native route로 보강 | 기존 시나리오와 중복 집계하지 않음, +0 |
| HD source | LAMDA 열 간 35 Hz 불일치의 의미와 CDMS/원논문의 후속 데이터 경로 규명 | 같은 fit의 정밀한 9준위/8전이 deck 미확보; gate 유지, +0 |
| 다른 producer / history / stopping | 7개 repo의 최신 PR 각 2건과 지정 예약 ref를 조사하고 기존 결과와 대조 | H6, H5, HE, BASS, V6, stopping의 물리 입력 의무 유지, +0 |
| 독립 검토 | 원래 실패와 제한된 수정, 원본 gate 및 시나리오 범위 검토 | 두 노드 admission 확인; +0 |

검색 범위는 위에 명시한 연결 가능한 repo/PR 및 보관본이다. 모든 대화·모든 브랜치를 전수 열람했다고 주장하지 않는다. 지정 논문으로부터 이전 루프에서 구축한 Lumina benchmark 및 PW19 source 근거는 재사용했으며, 완료된 적분·IVP를 재실행하지 않았다.

## 단계별 실행 기록

아래 R/C 단계는 이번에 선택한 blocker 해소 작업의 내부 진행이다. 전체 연구의 완료 수는 마지막 열의 원본 노드 수로만 표시한다.

| 단계 | 산출물 / gate | 전체 DAG |
|---|---|---|
| R1 / C1 | 원본 명세·source·예약·예산 및 PR236 6c160474 기준 확인 | 30/88 |
| R2 / C2 | 7 repo 변경 조사, REC119 native 코드와 donor 복구; HD 일차 문헌 검토 | 30/88 |
| R3 / C3 | 열린 의무별 병렬 분업; 실행 가능한 국소 source 연결 선택 | 30/88 |
| R4 / C4 | native callback, 고정 reference 및 finite snapshot 계약 확정 | 30/88 |
| R5 / C5 | 정상화/JVP 유도와 실제 subclass·reader 구현 | 30/88 |
| R6 / C6 | 단위·소유권·정의역·불변량·에너지 감사 | 30/88 |
| R7 / C7 | 최초 84검사 중 82통과/2실패, 실패 원본 보존 | 30/88 |
| R8 / C8 | 수치 소거 원인 유도, 실패 2개만 한 번 수정 검증 | 30/88 |
| R9 / C9 | 독립 PASS_SCOPED 검토와 root의 원본 두 노드 admission | **32/88** |
| R10 / C10 | plot·보고서·handoff·원본 gate 보존 변경·게시·이중 백업 | **32/88** |

최종 게시와 백업의 실제 commit/provider readback은 별도 `FINAL_DELIVERY_RECEIPT.json` 및 `DELIVERY_KO.md`에 기록한다. 이 보고서 자체를 백업 성공 영수증으로 사용하지 않는다.

## 실제 계산과 물리적 의미

REC119 commit `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`의 원래 `rates`와 `evaluate`를 변경하지 않고, 준비된 photo 계수의 공급자만 교체했다. He3II→He3III 및 He4II→He4III 두 route에 54.42–50000 eV의 PW19 계수를 넣었다. RR/DR/붕괴는 원래 native 경로를 사용한다. He3/He4 전자 반응률 동일성은 기존 선택 모델의 조건이며, 동위원소별 실측 보정률을 새로 얻은 것이 아니다. 다른 11개 photo route는 이번 비교에서 `OFF_BY_SELECTION`이다.

소스 적분값은 이전 검증 결과를 그대로 소비했다: Γ=7.130091128981093×10⁻¹⁵ s⁻¹, primary kinetic 공급 K=1.4238389467477924×10⁻¹³ eV s⁻¹ target⁻¹. native ≤200 eV 단면적 함수를 50 keV까지 외삽하지 않았다. 50 keV 이상 atomic 기여 및 물리 모델 오차는 unknown으로 남긴다.

201개 저장 knot의 donor에서 η*=ln(21/3.479), 인접 index 184–185, θ=0.7749797107939725로 물리 abundance와 T를 보간했다. 결과는 T=14919.863839279506 K, reference 밀도 r=8.033643390985384 m⁻³, β=1.328080003500061, baryon 밀도 n_b=10.669321142818111 m⁻³, n_e=9.351290694292933 m⁻³이다. 원래 donor history의 한 시점에 PW19를 대입한 counterfactual local response이며 PW19 아래 새로 진화시킨 history가 아니다. 보간의 물리 오차는 평가되지 않았다.

| 구분 | 이번에 확립한 내용 | 관측 해석 |
|---|---|---|
| 대칭성·게이지 / 좌표 관례 | 고정 comoving reference x=n/r에서 Y=x/β, β=A·x, n_b=βr; proper time callback. 이 정규화는 좌표 변경이며 새로운 물리적 gauge 대칭으로 취급하지 않는다. 기존 기하 convention 보존 | η 미분을 요구할 때만 F/H로 변환; 현재 plot은 proper time 기준 |
| 불변량 | A·Y=1; δY=(δx−Yδβ)/β, δβ=A·δx; δ(n_bY)=rδx+xδr. 각 photo 사건의 baryon·핵종 수, 전하 및 외부 광자 debit을 포함한 선택 에너지 ledger 검증 | roundoff 검증과 물리 입력 불확실성 분리 |
| 실제 계산 가능한 국소량 / 관측가능량 | native 21종 dY/dt, source on/off 차이, dn_e/dt 및 binding/primary/radiation power | 이들은 모델의 국소 반응 진단량. 최종 관측 신호는 별도 transport·history·관측 연산자가 필요 |

고정 T에서 native 형태는 F(Y)=λGY+DY+n_b(q·Y)RY이다. 따라서 J=λG+D+n_eR+n_b(RY)qᵀ이며 밀도·소스 변화까지 포함한 δF=JδY+(q·Y)RYδn_b+GYδλ를 검사했다. 정규화된 형태와 βF=(λG+D)x+r(q·x)Rx가 일치한다.

선택 photo 사건의 전자 생성률은 **2.4847195293909616×10⁻¹⁹ m⁻³ s⁻¹**이다. binding power는 2.1664381991007258×10⁻³⁶ W m⁻³, primary electron power는 7.949751527088793×10⁻³⁷ W m⁻³, prescribed radiation debit은 −2.9614133518096047×10⁻³⁶ W m⁻³이다. primary kinetic power를 열로 치환하지 않았으며, 이 합계는 전체 RR/DR/weak thermal closure를 의미하지 않는다.

n과 T는 21상태 목록 및 native 붕괴망에 남아 있다. 이번 donor의 실제 저장 inventory가 0인 사실은 우주에서 이들의 생성이 없다는 명제가 아니다. n 붕괴에 따른 p와 전자 생성의 기존 반응 구조를 보존했으나, 이번 광원 연결이 CR/별/IGM의 n·T 생성률, inverse-beta 공급 또는 daughter stopping을 새로 정량화한 것은 아니다. 이 물리 source와 cascade/stopping은 기존 열린 의무로 유지한다.

## 실패 원인과 제한된 수정

최초 run01은 **82/84 통과, 2실패(exit 1)**였다. 실패한 H 방향의 centered finite difference는 h=10⁻⁴에서 매우 작은 δY≈10⁻⁹를 큰 전자 밀도 배경에서 차분하여 소거 오차가 지배했다. 고정 T,n_b,λ에서 F는 Y의 2차식이고 n_e는 선형이므로 centered directional difference의 절단 오차는 이 모델에서 정확히 0이다.

이 유도에 따라 물리 모델·방향·상태·2×10⁻⁸ 허용값을 유지하고 **실패 두 검사만 h=10⁻²로 한 번 수행**했다. residual은 각각 4.712660174501273×10⁻⁸→1.3716601921088232×10⁻¹⁰, 5.667163219414058×10⁻⁸→6.434506579011881×10⁻¹¹이다. 양쪽 trial abundance는 양수다. 유효 근거는 **원래 82통과 + 수정 2통과**이며 최초 실패를 덮어쓰거나 전체 84검사를 재실행하지 않았다.

독립 검토 결과는 `review/INDEPENDENT_REVIEW.md`, 기계 판정은 `review/VALIDATION.json` 및 `review/SCENARIO_SUPPLEMENTAL_REVIEW.json`에 있다. strong no-go는 새로 주장하지 않았다.

## 예산·보존·다음 의무

원래 scientific planning cap 10 CPU s에 대해 이번 phase의 13 CPU s(+30%) 일시 한도를 적용한 뒤 **10 CPU s로 복귀**했다. 누적 알려진 debit은 **11.551892911 CPU s**로 보존한다. 이는 초기화를 의미하지 않는다. main ledger 595.225063/600 CPU s와 `NO_MORE_IVPs`를 유지했다. 원격 CAS·역사적 metadata/download 등의 미측정 비용은 0으로 가정하지 않는다. presentation 누적 비용과 packaging 비용은 delivery receipt에서 별도 집계한다. 50% 이상 증액은 별도 승인 대상이다.

실제 다음 연결점은 승인된 source/state callback을 원래 event/coupled assembly에 연결하는 의무다. 그와 병렬로 (1) HD의 동일 fit 정밀 source deck, (2) source-matched H6 causal trace와 reference derivative, (3) 물리적인 daughter/stopping 입력, (4) V6의 원래 full33/reduced30 client와 현재 예약/정의역을 확보해야 한다. H5 0/313 coverage와 L4의 live gas/radiation/geometry feedback 및 refinement gate는 열린 상태다. 기존 원본 gate를 약화시켜 완료 수를 늘리지 않는다.

실제 figure: `delivery/native_callback_pw19.png` 및 PDF/SVG. 휴대 가능한 재개 묶음에는 현재 unit, 실제 donor NPZ와 native 입력, 의존하는 이전 두 unit의 소스, 원래 canonical 계약과 변경분을 보존한다.

