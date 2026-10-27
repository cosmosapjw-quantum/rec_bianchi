# REC source synthesis — 최종 연구·코딩 결과
2026-10-27 KST

## 판정과 현재 위치

과학 판정은 **PASS_SCOPED_HD_JOINT_DIAGNOSTIC_AND_NATIVE_REAL_HISTORY_REMAINDERS**다. 고정 LAMDA 자료의 HD 열평형 불일치를 정량화하는 코드와 실제 저장 history의 knot 이동 나머지·Peano chord 상계를 구현했다. 원래 입력으로 실행하고 독립 코드·원시 결과·그림 검토를 마쳤다.

원 프로그램의 완료 수는 **working32/88, shared27/88**, 이번 증가0이다. R/C 연구단계20개와 원래 DAG88개는 다른 분모다. 이 문서는 전체 R1–R10/C1–C10 결과를 묶는 C10 산출물이다. 마지막 전송 ACK는 업로드 후 별도 delivery receipt에 기록하므로 미래 ACK를 미리 채우지 않는다.

고정 과학·독립 판정 commit은 `3678ce2ea24e0c2c57d156bde99a1c1fa1bccc47`다. REC draft PR은 [#139](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/139), 중앙 DAG draft PR은 [#238](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/238)이다. 중앙 반환 commit은 `60b246beedf3536ecea0848aa74a23e4786eed58`다. 병합은 수행하지 않았다.

## 1. 조사·직접 복구·재사용

고정 인계서와 이전 HD/H5 실행·예산·실패 기록을 먼저 읽었다. 접근 가능한51개 소유 저장소를 확인하고 관련10개 저장소의1380branch refs를 열거했다. 주요7개에는1376refs가 있었고6개 과학 저장소의 열린 PR844개를 조사 범위에 포함했다. Vigilode는 전체branch 목록과 최근20개PR 창을 확인했다. 모든 과거 branch의 전체 코드를 읽었다는 뜻은 아니다.

Dropbox의 지정 REC/REI/BASS 폴더는 terminal pagination을 확인했다. Drive의 관련 폴더도 조사했지만 BASS 검색은 응답·페이지 제한이 있어 계정 전체 확인으로 표시하지 않는다. personal context 서비스는 이 대화에서 사용할 수 없다는 응답을 반환했다. 별도 대화 전체를 읽었다고 주장하지 않고 제공된 인계와 Git·백업을 사용했다. 정확한 범위와 미접근 항목은 [SOURCE_SYNTHESIS_KO.md](SOURCE_SYNTHESIS_KO.md) 및 survey/에 보존했다.

선별 원시 백업6개를 직접 회수해 ZIP CRC·전체 SHA를 확인했다. GEO와 HD/H5의 payload manifest도 대조했다. REI coupled source의 z2.479 문맥을 원래 REC z≈1100과 구별했고, Vigilode의 점별/whole-tube 판정도 분리했다. 유효한 기존 과학 계산은 재실행하지 않았다.

SciSpace·Exa 조사와 원문 확인을 사용했다. LAMDA 준위 cm^-1, A계수 s^-1, 충돌률 cm^3/s, 별도 p/o-H2 collider를 보존했다. LAMDA가 frequency열을 추가 정보로 취급하는 점을 source bridge 해석에 반영했다. CDMS 기본 정밀도만으로35Hz 일관성이 보장되지 않는다. v2 원자료 deck7개 요청은 HTTP503으로 끝났으며 새 정밀 입력으로 채택하지 않았다. 버전·캐시 충돌도 새 고정 source로 바꾸지 않았다.

## 2. HD — 동일 온도에서의 열평형 불일치

준위와 주파수로 각각

`xE=h c 100(Etilde_u-Etilde_l)/(kB T)`,
`xnu=h 10^9 nu_GHz/(kB T)`,
`delta=xE-xnu`

를 정의했다. delta는 source literal과 SI 정의를 정확한 유리수로 처리한 뒤 binary64로 변환한다. 따로 반올림한 xE,xnu를 빼지 않는다.

양의 위·아래 복사 전이율의 정규화 차이와 source/Planck 편차는

`I=tanh(delta/2)`,
`D=expm1(-delta)/[-expm1(-xE)]`

다. 두 부호는 반대이며 exact coherence에서 I=D=0이다. [THEORY.md](THEORY.md)의 유도, R6 독립 검사와 R7 Wolfram 검산을 거쳤다. 독립80자리 기준은 생산식을 호출하지 않고 양의 flux와 원래 지수 비를 계산한다.

| 실제 측정 | 결과 |
|---|---:|
| 대상 |8개 선×50,100,200K=24개|
| 실제 진단 / 표적 대조 |24/24 PASS /21/21 PASS|
| 최대 절댓값 I |8.770964953285911e-7|
| 최대 절댓값 D |1.7541951787469943e-6|
| 최대 I 상대 오차 |3.011593202799463e-16|
| 최대 D 상대 오차 |2.999772662453845e-16|
| 고정 상대 허용치 |2.842170943040401e-14=128eps64|
| source/Planck 비 |0.9999986454572667–1.0000017541951787|

최대 양의 D는 line6,50K다. 가장 작은 실제 D의 크기는 line1,200K의4.1745971013940654e-12다. 검토자는 이 사례와 최대 상대-D오차 사례를 별도100자리 식으로 검사했고 저장된80자리 기준과 약1e-68 상대 수준으로 일치했다. 1+D가1에 가깝다는 사실로 작은 D의 정확도를 대신 판정하지 않았다.

원래35Hz energy-frequency gate는 **7/8 FAIL** 그대로다. line1의8.2410162Hz 차이만 통과한다. 원래9levels·8lines·collider2개·18pairs·54rates가 보존됐으며 외삽·p/o-H2 혼합·production source 승인은 없다. 이 진단은 고정 열들의 공동 관계에서 생기는 수치 결과이며 원자료의 행별 차이가 생긴 원인을 확정한 것은 아니다.

실제 출력은 hd_joint/raw/primary001/의 DIAGNOSTICS.json/CSV, TARGETED_CONTROLS.json, SUMMARY.json, EXECUTION.json 및 PNG/PDF에 있다.

## 3. 실제 history — knot를 넘는 정확한 나머지

35,239,470byte 원래 history와313query/source/cell witness를 사용했다. outgoing_virtual 뒤 outgoing_lyman 순서, eta=ln(a), 원래 T0·nH0·Wien departure reference를 유지했다.

새 객체는 `t_k=Fraction(eta0)+k Fraction(dlna)`와 binary64 sample을 정확한 유리수로 해석한 native-real 선형 보간이다. 반올림된 native C 및 저장 eta-array knot를 지나는 이전 geometric 보간과 각각 구별한다. prefix5127의 도메인은 `[t0,t5126)`다.

양·음 이동에서 방향에 맞는 한쪽 미분을 빼면 나머지는 지나간 slope jump의 유한 가중합이다. 출발 atom은 제외하며 도착 knot의 가중치는0이다. chord 오차는 음의 Peano kernel jump 합이다. 절댓값 jump 합이 상계를 주므로 셀 안의2차미분이0이라는 이유로 knot를 넘는 나머지를 버리지 않는다.

| 실행 항목 | 실제 결과 |
|---|---:|
| 고정 source/cell/endpoint 연결 |313/313 PASS|
| 셀 내부 이동 |626개, 모두 정확히0|
| 왼쪽 / 오른쪽 knot 통과 |313 /301 PASS|
| 총 이동 등식·상계 |1240/1240 PASS|
| Peano chord 등식·상계 |313/313 PASS|
| prefix 밖 오른쪽 이동 |12개 SKIP_CAUSAL_PREFIX|
| 대조 검사 |30/30 PASS|
| 실제 jump 생략 mutation 검출 |비영 나머지614개 모두|

마지막 셀의 incoming index134–144,311에서는 오른쪽 이웃 셀이 없으므로 해당 이동을 건너뛰었다. chord는 query와 마지막 endpoint 사이 내부 midpoint를 사용했다. 모든 등식·포함은 정확한 유리수로 확인했다. 독립 감사는 생산 module을 import하지 않고1240이동·313chord·313query재구성·5127clock record를 검사했다.

| 표현량의 최대치 | 값 |
|---|---:|
| 이동 나머지 절댓값 |1.8566648889656617e-19|
| chord 나머지 절댓값 |1.6749900771700771e-19|
| stored/native-real knot 차이 |4.71736365248443e-16 in eta|
| 새 native-real nominal anchor |1.8495299543650757e-29|
| 보존한 이전 geometric anchor |2.806325270875912e-28|

나머지와 anchor의 단위는 dimensionless occupation departure다. JSON/CSV에 정확한 분자·분모가 있다. 실제 선택 chord들은 상계와 절댓값 오차가 같았으며, 일반적인 cancellation은 합성 대조의 signed0과 양의 envelope6으로 확인했다. 전체 결과는 history_remainder/results/primary001/에 있다.

## 4. H5 물리 입력과 남은 의무

실제313query,626endpoint slot,314×313 interval operator 연결은 완료돼 있다. 기존 ACTUAL_BOUND_INPUTS에는 state_enclosure와 query_bounds가 null이고 물리 proof_artifacts도 없다. 기존 consumer 결과는 BLOCKED_ACTUAL_BOUND_INPUTS, physical epsilon·physical outgoing bound는 null, coverage0/313이다.

다음 producer에는 연속 F/G 재구성·state norm·동일 eta clock, 초기오차, 전도메인 defect/model discrepancy/안정성L, 양의 uniform open tube와 존재/bootstrap 근거, endpoint sensitivity/reference radius, whole-cell 물리 curvature/regularity가 필요하다. inverse-matrix residual rho=3.458800151575591e-12를 ODE tube로 바꾸지 않는다. 엄격한 E_upper<rho_lower 조건을 보존한다.

새 jump bound는 표현된 history의 정확한 정리다. 조건부 유도 승인을 물리 epsilon 승인으로 확대하지 않았다. H6/H7 OPEN, 물리 전체 수렴 NOT_RUN, production NOT_APPROVED, REI activation=false, L4=false, global physical completion=null을 유지한다. 자세한 구분은 [SCIENTIFIC_INTERPRETATION.md](SCIENTIFIC_INTERPRETATION.md)에 있다.

## 5. GEO01·실패·예산 보존과 중단 복구

GEO01의 PASS_SCOPED_CONTROLLED_PROPAGATION_PARTIAL을 재사용했다. 과거 Git·Drive NO_ACK preimage를 고치지 않고 실제 회수·게시 receipt를 뒤에 추가했다. 원래111경로와 history blob을 복구했고 S2/S3의 기존 Dropbox 및 새 Drive ACK를 확인했다.

GEO의17528일반roots·96Decimal·5matvec·1exact interval 및 기존 측정 science/figure/review CPU4.965851초는 재실행하지 않았다. PB01 원래 exit2실패, saved-vector8/8복구통과, patched full primary NOT_RUN도 보존했다. REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET 및 외부REI 예산을 초기화하지 않았다.

R9 게시 후 작업 공간이 비어 있는 현상이 관측됐다. 원인은 확인되지 않았다. 원격R9와 R1–R8 백업을 기준으로 필요한 소스·입력을 직접 복구하고 R9 ZIP을 같은 SHA로 재생성했다. 당시 새 과학 primary는 시작 전이었으므로 완료 유도·CAS·primary를 반복하지 않았다.

## 6. 독립 검토·비용·CI

실제 lower-tier 작업자 둘이 구현했다. parent가 계약과 수용 기준을 고정하고 구현에 참여하지 않은 Astra reviewer가 코드·원시값·그림을 검토했다. 새 reviewer thread 생성은 host limit로 거절돼 AGENTS의 compatible-agent reuse 규칙을 적용했다. 이전R6 문맥을 알던 reviewer를 재사용했으며 fresh thread라고 주장하지 않는다. 실제 runtime model은 UNKNOWN_NOT_EXPOSED다.

| 단위 | 측정된 통제 CPU |
|---|---:|
| HD primary·controls·그림·wrapper |4.301855738s /360s|
| History primary·supervisor |6.109471s|
| History saved-result 그림·supervisor |3.260151s|
| History 합계 |9.369622s /360s|
| 독립 raw-result audit |0.442506s /review180s|
| 로컬 통제 측정 합계 |14.113983738s|

새 과학 child는1thread·2GiB 제한 아래 모두 exit0였다. Wolfram remote CPU/RSS는 미노출이며20초 planning reservation은 측정 debit이 아니다. 미측정 출처·네트워크·게시·metadata는 UNKNOWN_NOT_ZERO다. 새 총 동결 한도1020CPU초와 이전 단위 한도를 구별한다. 잔여 한도를 다음 단위에 자동 이전하지 않는다. [BUDGET_LEDGER.json](BUDGET_LEDGER.json)에 원 기록을 연결했다.

전체 CI는 PASS가 아니다. 관측 REC sciencecommit의 package install·smoke import는 통과했으나 quick verifier가 실패해 pytest는 skip됐다. 해당 job log는 최초·1회진단재시도 모두 Transport closed여서 현재 실패 세부 원인은 확정하지 않았다. 중앙 cargo fmt는 기존 Rust 파일의 포맷 차이로 실패하고 cargo test는 skip됐다. 이번 중앙31파일에는 그 Rust 경로가 없다. 실제 commit·job·한계는 delivery/CI_OBSERVATION.json에 있다. 표적 과학 검증과 저장소 전체 CI의 결과를 구별한다.

## 7. 중앙 통합·게시·백업

최신 shared5abe0d19…를 base로 ee94의6wrapper와 e18의HD/H5두 wrapper에서 실제 바뀐 field만 가져왔다. GEO01·새 결과는 sibling owner return으로 추가했다. 원래88contracts·ID/order·모든dependency·15authority·17edge·외부예산·BASS3반환·CR_N5반환을 보존했다. 직접 참조26파일을 원본과 byte 일치로 복구했다. 이전species source_commit:null/PENDING_ACK를 고치지 않고 adoption envelope로 고정 출처를 연결했다.

중앙ZIP670,474bytes, SHA2564042d5eed82d1ad2ccbeec33e7dedb174aa77dadb4423e71f8a7654da108d9a7의 실제 Dropbox·Drive ACK를 확인했다. Source/입력 전체 ZIP은 history·privateLAMDA·기존HD/H5소스/실패/비용·새코드·원시출력·그림·검토·중앙patch·복구문맥을 함께 보존한다. 최종 C10/source ACK는 업로드 후 별도 receipt로 마감한다. archive가 자신의 미래 ACK를 넣으려고 반복 재포장되지는 않는다.

### 확인된 단계별 기록

| 단계 | Git commit prefix | ZIP bytes | ZIP SHA256 prefix | 백업 |
|---|---|---:|---|---|
| R1 | `22fde058e6b7` | 8169 | `9db0afc9855d` | 양쪽 실제 ACK·크기 확인 |
| R2 | `2be81bf022a7` | 1000143 | `e22d047773b4` | 양쪽 실제 ACK·크기 확인 |
| R3 | `64c19faba51a` | 9110 | `454a34e839aa` | 양쪽 실제 ACK·크기 확인 |
| R4 | `31203362d22d` | 4569 | `18777cbcc187` | 양쪽 실제 ACK·크기 확인 |
| R5 | `8ad619858d5c` | 8806 | `07d7cc71eb0b` | 양쪽 실제 ACK·크기 확인 |
| R6 | `c3df496ebd80` | 12820 | `c3dda280fcba` | 양쪽 실제 ACK·크기 확인 |
| R7 | `2d4917e891e7` | 3856 | `9b73d7d02473` | 양쪽 실제 ACK·크기 확인 |
| R8 | `6d0ddf5f5756` | 3962 | `f4282a4ea7d7` | 양쪽 실제 ACK·크기 확인 |
| R9 | `eb3b390eb59a` | 8690 | `6c4089455d80` | 양쪽 실제 ACK·크기 확인 |
| R10 | `f9d2e9799399` | 7245 | `8da4509064e4` | 양쪽 실제 ACK·크기 확인 |
| C1 | `09b2230c7735` | 5033 | `5494b1e87d19` | 양쪽 실제 ACK·크기 확인 |
| C2 | `e8e81f72257b` | 5156 | `0f8ffd22d97b` | 양쪽 실제 ACK·크기 확인 |
| C3 | `d67c54b85a9e` | 5319 | `42bffbd40dcc` | 양쪽 실제 ACK·크기 확인 |
| C4 | `1ba7efb5d99b` | 35212 | `3d111101e09f` | 양쪽 실제 ACK·크기 확인 |
| C5 | `8ef3abe1f3a4` | 1449327 | `808e90e91ca3` | 양쪽 실제 ACK·크기 확인 |
| C6 | `e10245cd6a07` | 5209 | `d5e5f4ba7f1f` | 양쪽 실제 ACK·크기 확인 |
| C7 | `d9539ad8c2bd` | 5359 | `e6f4855ea9e8` | 양쪽 실제 ACK·크기 확인 |
| C8 | `47dc13af02b8` | 13822 | `e6f770917fbb` | 양쪽 실제 ACK·크기 확인 |
| C9 | `3678ce2ea24e` | 16905 | `9bfd825a543a` | 양쪽 실제 ACK·크기 확인 |
| C10 | 최종 receipt 참조 | 최종 receipt 참조 | 최종 receipt 참조 | 업로드 후 실제 ACK로 마감 |

Full SHA·provider ID·byte수는 delivery/stage_receipts/에 있다. 최종 전달 companion은 C10/source의 실제 수신과 마지막 게시 상태를 보존한다.

## 8. 다음 연구

[HANDOFF_KO.md](HANDOFF_KO.md)의 복사 가능한 인계를 사용한다. 완료 parser·54DB·24LTE·GEO roots/matvecs·새24diagnostics·1240/313 나머지를 자동 재실행하지 않는다.

다음 물리 연구의 첫 후보는 원래HyRec F/G 연속 재구성·norm·eta도메인을 명시하고 실제313cells의 defect/stability/tube/curvature producer를 좁게 동결하는 것이다. 다른 후보는 같은 spectroscopic fit에서 나온 고정 고정밀E/nu deck을 직접 확보해35Hz bridge를 별도 대안으로 검사하는 것이다. LAMDA baseline은 유지한다. 두 경우 모두 새 단위 범위·실행한도를 먼저 명시하고 최신 AGENTS·HEAD·병렬 반환을 확인한다.

