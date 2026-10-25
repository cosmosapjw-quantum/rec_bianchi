# REC HD/H5 구현·게시·복구 전달

## 이번 단위의 결과

고정 인계서 5dd414982c5c9ada97dfdfcc0b77cf83af86d66e에서 이어 받은 HD parser와 H5 조건부 소비기를 구현하고, 실제 원자료를 직접 복구하여 연결했다. 구현 위임과 독립 과학 검토를 거쳤고 원 실패, 한정 수리, 실행 계측과 완료된 선행 계산을 보존했다.

| 구분 | 실제 완료 | 남은 과학 의무 |
|---|---|---|
| HD | 9 준위, 8 전이, 2 collider, 18 downward pairs, 54 rate values; 원 decimal과 정확한 SI 변환; WU species 재사용 | 원 35 Hz 기준에서 8개 선 중 7개가 불일치. 전체 계약은 HOLD_SOURCE_DISCREPANCY_UNQUALIFIED |
| H5 | 실제 313 queries, 626 endpoint slots, 기존 Ks 314×313 및 표현 반경을 조건부 소비기에 연결 | same-source continuous defect/stability/tube/curvature proof packet 0/313. 물리 epsilon과 outgoing bound는 null |

HD의 collision 온도는 정확한 50/100/200 K만 지원한다. p-H2와 o-H2를 별도 보존하며 외삽, endpoint clamping, off-grid interpolation, 혼합, missing-pair의 zero 대입을 하지 않는다.

H5는 E_upper < rho_lower의 엄격한 tube 포함 조건을 적용한다. 인증 하계 대신 radius 상계만 받는 입력은 거절한다. 실제 표현 차이의 최대값 2.806325270875912e-28은 물리 defect나 epsilon을 대신하지 않는다. 조건부 유도 승인은 물리 epsilon 승인이 아니다.

## 고정된 과학 결과와 게시

- REC 과학 구현 S1: [683c3f2ac3cdcc62ad6be9fe983ea39fcd74d1de](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/683c3f2ac3cdcc62ad6be9fe983ea39fcd74d1de)
- REC 전달 PR: [PR138](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/138)
- 중앙 관측 commit: [e18b4349f2a2da3ef7caf5ec73c8787d03894620](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/e18b4349f2a2da3ef7caf5ec73c8787d03894620)
- 중앙 DAG PR: [PR232](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/232)
- 중앙 최신 입력 snapshot: 3f287279c9ae4e8bcd4949a56b8c4cc0601b1eb8
- 독립 과학 결정 SHA256: 08649ed915d970812c342205ffe9862b4368b0fa4d152ea820de579a882db962

두 게시 모두 expected-SHA와 force=false를 사용했고 실제 branch HEAD/tree를 다시 읽어 일치를 확인했다. 중앙 전달은 최신 HE·GRID044·CR 변경을 포함한 88개 노드에서 REC 두 node wrapper만 갱신했다. 다른 86개 노드, 원 nested contracts 88개, authority 15개와 integration edge 17개를 보존했다. 두 PR은 draft이며 merge와 activation은 수행하지 않았다.

최종 containing REC commit은 S1 과학 코드·결과·독립 결정을 바꾸지 않고 전달 문서와 영수증을 추가한다. 그 commit의 Git identity가 최종 전달 identity이며, 자기 SHA를 파일 내부에 미리 적는 방식을 쓰지 않는다. 자세한 실제 게시 근거는 PUBLICATION_RECEIPT.json에 있다.

## 검증과 예산

HD는 고유 검사 26개 중 25개 PASS와 원 source-gate 검사 1개 FAIL의 증거를 보존했다. 그 FAIL 안에서 line 2–8의 원자료 차이를 확인했다. 별도 detailed-balance 54개와 LTE/Kirchhoff 24개는 동결한 128 epsilon64 수치 기준 안에 있었다. 이 대수적 일치는 원자료 불일치를 해소하지 않는다.

H5는 고유 검사 41개에 대한 PASS 증거를 보존했고, 마지막 tube 수정은 해당 10개 검사로 검증했다. 별도 독립 검토의 6개 방향성 대조도 PASS다. 전체 primary를 수정 후 다시 돌렸다고 주장하지 않는다.

새 실행 한도는 HD 90 CPU s, H5 90 CPU s, 독립 검토·통합 60 CPU s, 각 wall 600 s, 프로세스 RSS 1 GiB, 1 thread였다. HD 계측은 CPU 0.629051 s, H5는 CPU 0.883456 s다. 도식, 검토, 기계적 metadata와 I/O 계측은 해당 receipts에 남아 있다. 네트워크·모델·측정하지 않은 비용을 0으로 만들지 않는다. 이번 남은 한도를 다음 연구 단위로 자동 전용하지 않는다.

완료된 PB01/KS01 등의 primary, 기존 campaign, 새 RHS·IVP·native 실행은 0이다. PB01 원 exit2/FAILED, saved-vector repair 8/8 PASS, patched full primary NOT_RUN을 보존했다.

S1에 연결된 기존 GitHub CI는 과거 branch-range 파일의 공백 검사에서 실패했고 이후 pytest는 SKIPPED였다. 신규 S1 과학 파일에서 해당 공백 진단은 발견되지 않았다. CI_OBSERVATION.json에 실제 run/job을 기록했으며 전체 CI PASS를 주장하지 않는다.

## 직접 복구와 이중 백업

원 PB01 S2 ZIP은 Dropbox에서 직접 내려받아 69,336,495 bytes와 전체 SHA256을 확인했다. 원 LAMDA provider bytes도 고정 source와 일치했다.

| 전달 파일 | 크기 | 저장·검증 |
|---|---:|---|
| S0 실행 동결 ZIP | 16,140 bytes | Dropbox/Drive 실제 ACK와 크기 일치 |
| S1 전체 소스 ZIP | 275,856,297 bytes | 6,177 tracked blobs 전부 Git identity와 일치, ZIP CRC PASS; Dropbox 단일 ZIP, Drive 세 조각 |
| S1 재개용 source/input ZIP | 70,113,767 bytes | 현재 단위 소스와 원 PB01 S2 archive 포함; Dropbox/Drive 실제 ACK와 크기 일치 |

전체 소스 ZIP SHA256:

71d0f0a44e43b211bdfabd7ac99be71077e1578814947aca09af56c6acb2fb29

재개용 ZIP SHA256:

ca97417f3a33efc0d3445f115ed7bc29909127c3475c7636846ab921ea2a656e

Drive 연결 도구가 전체 ZIP을 100 MiB 제한으로 거절한 원 응답을 보존했다. 원 ZIP은 바꾸지 않고 90 MiB 이하 세 부분으로 나눴으며, 실제 parts 스트림의 전체 크기·SHA256이 원 ZIP과 일치했다. Drive의 세 파일도 각 크기를 readback했다. full_source_restore 안의 manifest와 표준 Python 복구 스크립트를 사용한다.

정확한 object ID·경로·각 조각 hash는 BACKUP_RECEIPT.json과 full_source_restore/PARTS_MANIFEST.json을 따른다. 새 업로드의 원격 검증은 완료 ACK와 크기 readback이다. 새 원격 ZIP 전체를 다시 내려받아 SHA256을 검사했다고 주장하지 않는다.

최종 동반 ZIP은 이 전달 문서, 기존 ACK, 중앙 DAG 산출물과 복구 스크립트를 묶는다. 그 ZIP 자신의 ACK는 이후 containing REC commit의 COMPANION_BACKUP_RECEIPT.json에 기록한다. 자기 ACK를 다시 ZIP 안에 넣는 무한 재포장은 하지 않는다.

## 다음 실행

HD의 다음 단위는 일곱 전이의 CDMS/LAMDA source별 준위·주파수 fit/version/uncertainty 대조다. 원 숫자와 35 Hz 기준을 유지한다.

H5의 다음 단위는 동일 source의 retarded history를 포함한 연속 state/closure, F/G, 고정 norm과 초기 error, 전체 구간 defect/stability, 인증된 tube 하계와 whole-cell curvature proof packet 생산이다. 입력이 들어온 뒤에도 독립 물리 내용 검토와 observable error allocation을 거쳐야 physical epsilon을 승인할 수 있다.

새 단위 전에 최신 AGENTS·HEAD·병렬 작업·입력 identity와 새로운 실행 한도를 먼저 확인한다. global_physical_completion=null, L4_ready=false, REI_activation=false와 기존 Physical HOLD를 유지한다.
