# 원자물리 세 스레드 최신 진전과 rec_bianchi 의존성 검토

2026-10-04 23:26–23:30 KST 읽기 시점이다. 각 저장소의 branch 목록·최근 commit·열린 PR·현재 handoff와 반환을 직접 읽었다. 아래 “완료”는 명시된 공급기/기록 범위의 기존 게시 상태이며, 이번 검토에서 과학 시험을 재실행한 뜻이 아니다. 20개 읽은 원문을 Git blob identity와 대조했다.

| 저장소 | 관측 commit / branch | 새로 확인한 진전 | 아직 미완료 |
|---|---|---|---|
| bass_cr | 936f78d535416281276102ba825b747c9355c0fc / research/r4q-gap-closure-20261001 | CR-off 전환, receiver F00/F02 진전 동기화, Peebles shell 축약과 정확한 closure defect 게시 | 실제 CR-off 소비기 dispatch 검증, 실제 재결합 history |
| WU088_HH | b0fb3a7cdb0976330d48b97edaf77560ec121e8a / research/r31ao-unequal-order-ladder-20260930 | 외부율·log-T jet·구간 remainder·Maxwell incoming moments·원문 intake; 저장 FT06 pair의 source-only 후처리 | HH-F1 application domain, 실제 HH-on consumer 및 coupled 감도 |
| BASS_HE | 9df4f33577a0b07ca1d3f8ee2f770baf4c3f309c / research/shared-c64-crossrepo-20260928 | KF96 별도 source 추가, HE-F2 event/fraction/chemical ledger, HE-F2B 실제 RCT 제외 결속, generic F01 동기화 | RCT opt-in/실제 provider/열·광자 closure와 application admission |

세 저장소 모두 별도 이름의 fastest branch가 생긴 것이 아니라 위 기존 연구 branch 안의 additive fastest 자료가 전진한 상태다. 열린 PR은 각각 #23, #33, #17이다. 수신기 상태는 여기서 두 단계로 구분한다. 각 원자 기록에 박힌 receiver commit은 과거 증거이며, 이번 root의 rei_bianchi 최신 검토가 현재 수신기 권위다.

## Peebles 검증에 지금 가져올 것

**순수 수소 Peebles benchmark의 선행조건에 이 세 원자물리 lane의 정밀 완결은 없다.** CR/HH/He-CX를 제외하는 별도 모델을 명시하고 thermal CMB 역반응을 유지하면 된다. 재이온화 F00의 SYNTHETIC_CASE_A_ESCAPE에서 shear만 0으로 만드는 경로는 Peebles와 구조적으로 동등하지 않다. 이미 CR 문서와 receiver PB01이 이 결론을 기록했으므로 같은 유도·표본을 또 만드는 작업을 다음 연구로 삼지 않는다.

CR 최신 문서가 지정한 다음 노드는 REI-CHAT-PB02_SOURCE_BOUND_REDUCTION_CONTRACT다. 실제 rec_bianchi level/radiation residual 또는 adapter의 commit/path/blob를 연결하고, 같은 입력의 C, beta_P, Lyα escape, retained residual, reduced RHS를 비교하는 일이 유효한 증분이다. 연결이 없으면 MISSING_PEEBLES_CLOSURE_AT_CONSUMER이지 원자 정밀 자료 부재가 아니다.

CR의 재사용 가능한 convention은 x_2p=3x_2s=3x_2/4, beta_P=4 beta_2, Gamma_2=(Lambda+3R_alpha)/4다. alpha_B의 Case-B, 열적 상세평형, 두꺼운 Sobolev escape, 두 광자 붕괴와 QSS, x_2<<1은 별도 가정이다. finite-relaxation term과 ground-density correction을 버린 과정도 기록되어 있다. 이는 특정 유효 shell 모형에서의 직접 유도/유한 검산이며 full line transfer의 인증은 아니다.

## 원자 공급기의 실제 재사용 범위

HH는 외부 raw fit의 analytic source reference와 별도 piecewise 검산을 제공한다. k57의 T<=3000 K floor와 위쪽 analytic branch를 가로지르는 smooth derivative를 쓰면 안 된다. HH-F1M은 incoming collision energy moment를 계산했지만 이것이 ionization heat나 outgoing spectrum을 정하지 않는다.

새 FT06 후처리는 HH가 꺼진 F/B 두 저장 이력의 65점에 외부율을 평가했다. LCS의 누적 사건/H는 F≈4.4165174e-7, B−F≈4.1706296e-12이고 corrected KS는 F≈4.3590589e-9, B−F≈4.0756212e-14다. 이 숫자는 저장 궤적에서의 source loading이며 HH를 켠 해의 Δx_HII, ΔT, Δτ가 아니다. 65/33점 차이 약 0.27%도 경험적 진단이지 적분오차 상계가 아니다. 따라서 재이온화 omitted-channel 탐색에는 참고할 수 있지만 Peebles 복원이나 물리 history PASS로 승격할 수 없다.

He는 GM25와 KF96를 명시적으로 분리해 공급한다. GM25 범위 200–10000 K와 KF96 nominal 호출 범위 1000–1e7 K의 공통 비교구간은 1000–10000 K다. 이전 FT03의 30000–110000 K guard와 공통 비교구간의 교집합은 없다. 온도 clamp나 source 자동선택으로 메우지 않는다. HeIII+HI RCT의 free-electron 증분은 0이고 chemical energy Q≈40.8193254 eV이나, scalar k만으로 thermal/photon partition을 결정할 수 없다.

HE-F2B는 실제 owner가 RCT/NRCT를 제외했다는 사실을 결속했다. 23:26 KST 최신 동기화에서 generic F01의 구현 완료를 인정했지만 실제 RCT provider instance는 없다고 명시했다. 과거 missing-F00/F01 기록을 현재 blocker로 반복해서 쓰면 안 된다. baseline에 He RCT를 넣지 않는 동안 BASS_HE가 rei/rec 개발을 막지 않는다.

## 현재 연구·코딩 순서에 대한 결정

1. REC 전용 model/closure ID, source pin, beta convention과 thermal bath를 고정한다. REI synthetic lock을 덮어쓰지 않는다.
2. 이미 게시된 PB01/CR 유도를 재사용하여 실제 REC adapter를 연결한다. 같은 입력의 항별 일치와 명확한 실패 분류를 먼저 확보한다.
3. 통과한 모델에 한해 경량 x_e(z) history, 적분기/step 수렴, FLRW 한계를 계산한다. 이 단계는 원자 native/scattering 연구를 필요로 하지 않는다.
4. HH·He는 source provider와 application domain이 명시적으로 요청될 때만 연결한다. coupled atomic sensitivity의 단일 owner REI-F09는 유지한다.
5. 원래 원자 lane의 G02/production/epsilon/Eq55 등 미해결 gate와 소비된 scope는 그대로 보존한다.

이 검토는 원격 읽기와 현재 문서 해석이다. 새 원자 적분·과거 scientific suite 재실행·provider 물리 승인은 0이다. exact URLs와 blob IDs는 SOURCE_INDEX.json, 파일별 byte 검증은 SOURCE_IDENTITY_CHECK.json, 수신기용 구조화 결정은 RECEIVER_DEPENDENCIES.json에 있다.
