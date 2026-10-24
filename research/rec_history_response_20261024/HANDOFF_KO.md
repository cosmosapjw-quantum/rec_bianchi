# REC-HISTORY-RESP01 재개용 handoff

## 현재 위치와 완료 범위

REC-HISTORY-RESP01은 원래 target의 전체313입력→314출력 frozen response 및 represented-operator enclosure를 완료했다. Root science decision은 `PASS_SCOPED_REPRESENTED_OPERATOR_AFTER_DIAGNOSED_CHECK_REPAIR`다. 물리적 history 입력 오차는 여전히 null이고, parent REC-HISTORY는 PARTIAL, H5는 INPUT_DEPENDENT_UNCALIBRATED다. 과학 결론은 `CLAIM_GATES.json`, 원문 설명은 `REPORT_KO.md`, 다음 연구 입력은 `NEXT_INPUT_CONTRACT.md`를 사용한다.

원래 target T0=2.728K, nH0=0.18745798773143102m^-3, face z=1099.9986525171403 및313retarded queries를 유지한다. Candidate cosmology나 early-time prefix로 target을 바꾸지 않았다.

## 실제 결과와 보존된 finding

저장된 binary64 M,B,T,P가 나타내는 정확한 실수 연산자 `T inverse(M) B+P`의 norm enclosure는 [1.175627229227178,1.1756272292401924], rho upper는3.5019104723714056e-12다.128Fraction dot checks,14arithmetic/refusal controls,4manufactured exact systems가 보존되어 있다. 이 범위는 저장 계수의 represented operator이며 physical history uncertainty나 libm의 오차 enclosure는 아니다.

최초 primary는 diagnostic gross scale에 취소되는 incoming 중간항이 빠져 exit2로 끝났다. 원 코드·failure·raw residual·criterion·실행 receipt는 그대로 남아 있다. Root가 승인한 한 번의 saved-data recheck는 virtual rows에2abs(u)를 더한 gross scale과 같은512eps 기준을 사용했고 새 solve·native action·certificate 재계산은0이었다. 최종 독립 검토는 material blockers0으로 scopedPASS, root는 최초 두 PNG를 실제로 보았다.

실행은 primary1, saved-data recheck1, figure process1이다. Main algebraic dense RHS627columns; 새 IVP/native/old replay/completed-science replay0. 실제 CPU6.0766539999999996s, execution wall6.1121022639999865s; cap45CPU/90wall,1thread,1GiB였다. 남은 allocation은 새 실행 허가가 아니다. 원실행 receipts와 최종 명시 count는 `BUDGET_LEDGER.json`을 읽는다.

## 실제 게시와 백업

| Checkpoint | 당시 유한 단계 | 실제 Git/readback | 실제 backup |
|---|---|---|---|
| S0 |9/20 | f05acda54e45e1be1a47fa4a43ca9b0951840a05;26/26PASS | Dropbox completed ACK;archive4480409B |
| S1 |11/20 |31d3d5b34ae8281e5f958648051a8459a9a0b46b;49/49PASS |Dropbox completed ACK;archive259448B |
| S2 |18/20 |277572a17b27c09246dbeaa707a1fa82f89cffcd;104/104PASS |Dropbox id:BSpOijBcT10AAAAAAD_9dg;7473354B |
| S3 | final delivery 준비 | 실제 ACK 전에는 완료로 승격하지 않음 | 실제 ACK 전에는 pending |

REC draft PR134는 <https://github.com/cosmosapjw-quantum/rec_bianchi/pull/134>다. S2 archive SHA256은a41da3e7df6b26bd6af756473bd8bdcdd96a915dfa2561b07fe2ca29c6f26c37이며178payloads/180members다. Bulk RAW_RESPONSE.npz/COEFFICIENTS.npz와 정확한 실행 source snapshots는 S2 archive에 보존되어 있다. `provenance/S2_RAW_ARCHIVE_LOCATORS.json`의 member/bytes/SHA256으로 복구한다. 과학을 다시 실행하여 복구하지 않는다.

원본 ZIP CRC/payload SHA/size는 PASS다. Provider content-hash 검증과 whole-byte remote download는 구별한다. S0/S1 remote GET은 환경 network restriction으로 막혔고, S2는 알려진 같은 제한 때문에 새 HTTP GET을 하지 않았다. Remote whole-byte readback을 주장하지 않는다. 실제 unsigned hash verification receipts는 delivery에 보존되어 있다. 이전 REFINE01 Drive upload의 server state UNKNOWN을 그대로 두고 이번 새 Drive upload는 NOT_RUN이다.

현재 repo CI는 S1 run40082526586/job120838832536에서 import smoke success, verify_repo.py --quick failure, pytest skipped다. 이를 green으로 표현하지 않으며 수동 CI replay0이다. 새 owned inline projection의 whitespace는 별도 PASS이고 원 source bytes는 정규화하지 않았다.

## 중앙 의존성과 다음 작업

현재 원문 intake 중앙 cutoff는 a814dab41a8f3f543dec71cde59f17e0d497fcda다. 원래40author contracts와17edges·fixed authority를 그대로 보존하고 REC 관측만 additive하게 전달한다. 기존 PR225 REC 관측의 immutable S2 18/20과 후속 final external20/20을 구별한다. 최신 HE-ANG19complete/C8partial, pressure finite completion과 stock NOT_RUN도 그대로 유지한다. 실제 중앙 게시 commit은54a65d4d84d3cb7a8dc05a2d69c6910690b30bff, tree6a73de4b93d286c5aa290e5baa1003b70b7f9e3e, draftPR226 <https://github.com/cosmosapjw-quantum/rei_bianchi/pull/226>다. 실제3paths/blob readback과 보존검증은 PASS이며 `delivery/CENTRAL_ACTUAL_RECEIPT.json`에 남아 있다.

R10/C10은 S3 actual ACK 뒤 작은 D1 receipt projection으로20/20을 기록한다. S2 `CLAIM_GATES.json.stage_scope=18/20`은 당시 과학 checkpoint로 그대로 남고, final external companion이 실제 D1 commit/readback을 붙인다. 유한20/20은 전체 물리 완료율이 아니다. 전체 물리 완료율은 null이다.

같은 original source/frame/domain의 독립적 reference uncertainty 또는 정당한 endpoint/whole-cell curvature/stability bound가 공급되면 저장된 querywise response와 conditional box API로 전달한다. 실제 h2U4/h4U4A/U4B/h2U5 후보는 존재하며 다시 없다고 주장하지 않는다. Full angular incident trace와 thermodynamic coefficient/system Jacobian은 별도 열린 입력이다.

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false; first failed REI raw HISTORICAL_LOCAL_ONLY. 원래 계약·failure·raw arrays·첫 PNG·완료 근거를 재사용한다.
