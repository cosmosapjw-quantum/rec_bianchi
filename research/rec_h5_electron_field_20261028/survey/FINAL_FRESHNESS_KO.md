# 최종 조사 후속 확인

2026-10-28 10:27:55 UTC에 관련 17개 저장소의 PR 목록을 갱신 시각 내림차순으로 읽어, 09:00:44 UTC 기준 시각까지 도달했음을 확인했다. 각 저장소에서 1페이지를 읽었다. 이전 조사에 이미 기록된 head와 달라진 항목의 PR 본문 및 지정한 핵심 상태·결과 파일 한 개씩을 확인했다. 기록은 이 시점의 snapshot이며, branch의 모든 원문이나 모든 대화를 조사한 결과가 아니다. [범위·SHA와 파일 경로](FINAL_FRESHNESS.json)

## 달라진 head의 범위

| PR | 관측 head | 확인된 범위와 REC point-field에 대한 관계 |
|---|---|---|
| REC 146 | `b2a9da90f3ef0a714f8f12bb02210d8e95d2d2ab` | 현재 동일 단위다. 같은 head의 C8 검증 기록은 132/132 parity와 residual 통과, PASS_SCOPED_C8_NUMERICAL_VALIDATION_PENDING_C9를 기록한다. C8 전달 영수증은 Drive·Dropbox ACK와 크기 readback, 18/20을 기록한다. C7 요약의 C8 대기는 C7 시점의 역사적 상태이며 fresh C9은 진행 중이다. |
| REI 244 | `0da7cac8c064238913b6f49108f4fbfd5edd7523` | 움직이는 knot의 caloric 방향미분과 구현 준비다. 실행 checkpoint는 C6–C8 미실행과 실제 recipient 물리 callback 미제공을 명시한다. |
| REI 245 | `cc17c2481f3f1057062efe0cbfb505114a0e8cfc` | 201개 저장 시점의 비보정 외부 source 및 QSS 진단이다. 상태 파일은 trajectory 주장이 없고 물리적 보정이 미완임을 명시한다. |
| BASS 227 | `90b600519712939e3db123191dcaea0361fdea9e` | 지정된 정적 lapse의 retarded source-memory benchmark다. 결과 파일은 scoped 완료와 targeted CI 성공, 별도 repository policy CI 실패 및 native 구현 미실행을 구분한다. |
| BASS_CR 114 | `3d9818b4b91d00beef946aa88540d73c33e51dac` | 최신 science summary는 조건부 energy-sum 결과를 기록하고 실제 physical K는 null로 둔다. PR 본문에는 이전 R1 상태가 남아 있으므로 현재 source summary와 본문을 같은 시점의 상태로 취급하지 않는다. |
| WU 150 | `dfdefe47ef0c28ae94f6e6727d3230ceed5c356d` | R14의 조건부 quadratic forcing 결과가 채택되어 있다. 해당 admission은 actual HD array와 physical consumer·state·density·clock을 입력 대기로 둔다. |

이 다섯 타 연구의 읽은 범위에서 원 HyRec의 해당 electron point-field를 직접 대체하거나 현재 계약과 충돌하는 새 입력은 확인하지 못했다. 이는 그 연구 전체나 모든 가능한 자료에 대한 부재 증명이 아니다. 서로 다른 clock·state·조건부 결과 및 완료 수를 REC physical certificate에 합산하거나 이식하지 않는다.

별도 재확인에서 REC PR142, 143, 144, 145의 head는 각각 `5438f2a082f7ed204603e441866ca63d1e0bf9de`, `0cb5c5ee16f5be57e71ea6694a8fd93af0394467`, `29e8427fa02ae089b004bce13c3d29ef663c89b4`, `7d3db873dacac29bab40cb5576d1c14b629afa87`였고, 중앙 PR222는 `66ef9a0147a0573b77e74e151dc280ba2bd4b64c`였다. 모두 이전에 확인한 head와 같다.

## 이름 기반 branch 대조

기존 branch snapshot에서 이름에 `20261028` 또는 `2026-10-28`이 들어간 항목을 기존 open/recent PR의 head branch와 기계적으로 비교했다. 대응을 찾지 못한 항목은 BASS_HE의 `he-azimuth09`, `he-exfor11`, `he-harmonic10`, `he-kinematic08`, `he-quartic12`, `he-tangent13` 6개이며 전체 이름과 당시 SHA는 JSON에 있다. 이는 해당 목록과 이름의 대조 결과일 뿐, PR이나 관련 내용이 어디에도 존재하지 않는다는 뜻이 아니다.

이번 확인은 메타데이터 및 선택 원문 읽기다. 네트워크·관리 비용은 측정하지 않아 미상이며, 새 과학 실행과 원격 쓰기는 0이다. 선택된 PR의 결과 주장은 해당 source의 범위에서 보고한 것이고 이번 확인에서 과학 결과를 재실행하거나 독립 검증하지 않았다.

## 미대응 BASS_HE 브랜치 6개 후속 확인

2026-10-28 10:30:52 UTC에 여섯 branch의 현재 ref, tip commit 메시지·변경 경로와 각 tip의 상태 또는 결과 문서 한 개를 읽었다. 다섯 head는 초기 snapshot과 같고 TANGENT13은 `3beb35dc7dea7a60642497dc373c98e75ca07536`에서 `049e79cb453b92ac663c4e0a93577a8364c3cf54`로 이동했다. 중앙 사전확인 DAG는 후자를 동일 TANGENT13의 source commit, 전자를 성공 실행 commit으로 명시한다. TANGENT13은 별도의 중복 신규 단위가 아니다. [각 SHA·tip 변경 경로·선택 원문](HE_BRANCH_FOLLOWUP.json)

| 범위 | 읽은 tip 상태와 TANGENT13과의 관계 |
|---|---|
| KINEMATIC08 | 조건부 kinematic reference의 선행 번호 단위다. 당시 source snapshot은 workflow PARTIAL과 S08 CPU 한도 실패를 보존한다. |
| AZIMUTH09 | 유한 azimuth reference의 선행 번호 단위다. 읽은 closeout은 자기 S10 게시 이전 snapshot이다. |
| HARMONIC10 | 고정 kinematics의 second-harmonic finite-detector reference인 선행 번호 단위다. |
| EXFOR11 | 데이터 조건부 aperture reference인 선행 번호 단위다. 실제 normalization과 물리 입력은 별도로 열려 있다. |
| QUARTIC12 | full positive quartic reference인 선행 번호 단위다. 기록은 S10 게시 이전 snapshot이다. |
| TANGENT13 | 중앙 DAG가 가리킨 동일 단위의 S10 source head다. 읽은 문서는 생성 당시 자기 게시·전달을 pending으로 기록하므로 이후 ACK로 오인하지 않는다. |

선행이라는 표현은 명명된 단위의 순서를 가리키며 다섯 branch의 Git ancestry 또는 중앙의 개별 포함을 새로 증명한 것은 아니다. 이 여섯 선택 문서에서 REC HyRec electron point-field 공급은 확인되지 않았다. 전체 commit history나 여섯 branch의 모든 diff를 검토하지 않았다. 새 과학 실행과 원격 쓰기는 0이다.
