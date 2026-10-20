# R3R CI isolation 독립 감사

판정: **PASS_SCOPED_CI_ISOLATION_P2_CLOSED**. 검토자는 numerical implementation과 test-only 수정의 작성자가 아닌 독립 context_intake agent다. 새 source의 실제 일반·전용 CI와 raw log, 고정 Git bytes를 읽었다. 이전 C9 및 과학 실행 결과는 보존했다.

## 1. 실행 source와 delivery source

| 역할 | Git identity |
|---|---|
| 실제 기존 tests/benchmark/pilot | `1313b1f1b2c081d57bcce9c60e757ef79110df91` |
| 기존 과학 실행 tree | `97423cad509a9604269740132a6ad850faf8f19a` |
| 실패 CI 당시 branch HEAD | `7d1a05033ad7b82527c66ae45a1feb09ff0d4ccc` |
| 실패 CI 실제 PR checkout | `866646195e93d2d2456cd87a28320466146ac98a` |
| 게시한 test-only 수정 | `70a53396e910869ea069e184a44f1fb21cb47a0a` |
| test-only source tree | `565550bec51506b2a85c48442b9ab0d69be18be7` |
| 새 CI 실제 PR checkout | `2fe1008f31a4ccb36b1b03fe14e31a65a7c75b2f` |
| 새 CI checkout tree | `565550bec51506b2a85c48442b9ab0d69be18be7` |

GitHub Git-data 응답에서 새 synthetic merge의 부모는 PR111 base `5b44bb21ce0599e55e0848e5e3ff320c9e8ca172`와 새 source `70a53396…`였으며, merge tree와 source tree는 정확히 같았다. 따라서 PR metadata의 branch HEAD를 실제 checkout이라고 대체하지 않으면서도 실행된 source bytes를 결부할 수 있다. 원본 provider 응답은 CI archive 안에 보존했다.

중단 전 로컬 test-only commit `1a4e05a1…`은 같은 tree를 가진 과거 준비 기록이다. 실제 새 CI source는 게시된 `70a53396…`다. 원래 benchmark 및 32-step pilot의 실행 source는 계속 `1313b1f1…`다.

## 2. 원래 실패와 최소 교정

실제 [실패한 일반 CI](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/39473175864)의 두 trace test는 imported `benchmark.trace_lane_ratios`에서 원래 CLI의 process-lifetime budget guard를 호출했다. 전체 pytest가 그때까지 사용한 CPU가 새 trace 작업의 사용량으로 들어갔다.

| 실제 실패 | CPU | Wall |
|---|---:|---:|
| all-lane trace | 92.440560 s | 80.063518 s |
| reordered trace | 92.626558 s | 80.249547 s |

두 실패 모두 `R3R_REPLAY_BUDGET:scalar_lane_trace`다. 실제 ratio 불일치가 검출된 실패가 아니다. 새 테스트에서 설정한 wall 181초는 의도적인 반례 상태이며 위 CI wall 값과 다르다.

수정은 `tests/test_r3r_stream_audit.py` 한 파일의 `+92/-3`이다. 파일 SHA256은 `6b29e4018f56ba20e455f7cac375a45d0eb712659827def308258c4bd0cd74d3`다. 기존 18개 test function과 모든 parameterization이 유지됐다. 두 기존 trace test만 각각 새 child에서 수행한다.

부모 guard는 소진된 상태에서 child 실행 전후 모두 거절한다. child는 NumPy/project import 전에 lower-only CPU·AS 제한을 설치하고, 168초 work alarm과 180초 부모 timeout을 사용한다. 새 빈 pycache prefix와 `-B`를 함께 사용한다. 원래 comparator/benchmark/launcher/worker/Budget의 guard를 reset하거나 한도를 높이지 않았다.

기존 25,000 lane, backend당 200,000-byte trace, scalar/NumPy SHA 동등성, differing binary64 lane 0개, 입력 4개 전후 SHA, ordered interleaving 및 child returncode/stderr assertion을 유지했다. 단일 task 내부의 60 CPU / 180 wall / process당 2GiB 경계를 전체 일반 pytest job의 총 CPU라고 해석하지 않는다.

## 3. 실제 새 CI 결과

| source70a의 실제 PR CI | 결과 | 실행 환경 | pytest 보고 시간 |
|---|---|---|---:|
| [일반 39494896783](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/39494896783), job118877283392 | 1038 PASS, 103 SKIP, 72 subtest PASS | Python3.13.16 / NumPy2.5.4 | 138.69 s |
| [전용 39494897256](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/39494897256), job118877284387 | 60 PASS, 1 SKIP | Python3.12.15 / NumPy2.5.4 | 9.47 s |

일반 CI의 기존 1036 PASS에 두 수정 case가 PASS로 돌아와 1038 PASS가 됐다. 전용 CI는 기존 61개 case 중 60개 PASS와 외부 unmodified full-CSV optional case 1개 SKIP다. 새 고유 test를 더한 것이 아니며 반복 CI를 기존 61개에 합산하지 않는다. optional raw case의 기존 로컬1313 PASS는 선행 증거로 재사용한다.

두 workflow의 실제 completed/success 응답과 로그를 확인했다. 새 CI에서 출력한 child f64 파일을 별도로 다운로드해 독립 byte readback했다고 주장하지 않는다. 기존1313의 전수 25,000-lane byte 감사와 새 CI의 source-bound assertion 실행을 구별한다.

## 4. 독립 source 및 raw readback

`ci_isolation_evidence_readback.py`를 한 번 실행해 다음을 직접 대조했다.

- 고정100개 frozen source SHA와 runtime/test/input closure 전체111개 Git 파일.
- 보호 대상5개 runtime의7d1a bytes 동등성 및 실제1313 source와 AST/location 동등성. launcher의 과거 EOF 정규화는 byte identity 차이로 남겼다.
- 이전 C9 JSON·Markdown·evidence readback의 원래 bytes.
- 실패7d1a 및 성공70a의 실제 CI log4개, 각 bytes/SHA와 tar member.
- source와 실제 PR merge의 tree identity, 두 workflow의 완료 상태, 실제 raw summary 및 원래 실패값.

명령과 stdout/stderr SHA는 `ci_isolation_evidence_readback.execution.json`에 있다. exit code0, 독립 readback CPU0.458790초, wall0.465906659초였다. 이는 저장된 metadata와 source를 읽은 감사 비용이다. solver·test suite·timed benchmark는 재실행하지 않았다.

`ci/CI_ISOLATION_LOGS.tar.gz`는39,615bytes, SHA256 `a81331bccf93627d846842db6a1f072eb28385180e540c2dd134d40ad6738eee`다. 이전 두 log를 GitHub에서 다시 얻어 과거 관측 SHA와 동일함을 확인했다. 이 새 보존 archive가 소실된 과거 archive 자체의 동일 bytes라는 주장은 하지 않는다.

## 5. 실행하지 않은 formal003

`formal_validation_003`은 **NOT_RUN_SUPERSEDED_BY_ACTUAL_SOURCE70A_CI_RETURN**으로 남긴다. 준비했던 원래 wrapper SHA `e8a168c9768c399fd8e3e2d70aa1f4c2d9858a9b4c7ecb867fd6ac104c734538`는 실행 전에 workspace pruning으로 소실됐으며, 실제 실행 증거로 재사용하지 않았다. 복구 후의 replacement wrapper도 실행하지 않았다.

새 source의 실제 일반·전용 CI가 돌아왔으므로 같은 두 case의 로컬 중복 실행을 생략했다. 따라서 formal003의 local scientific allocation 사용량은0이며, 기존 formal001/002 누적 CPU21.365609000000003초 / wall21.497515038005076초 기록을 초기화하거나 새 실행값으로 바꾸지 않는다.

## 6. 단계별 판정과 claim 유지

| 판정 축 | 이번 감사의 결론 |
|---|---|
| Mathematical correctness | 기존 R3R scoped PASS 재사용. 수치식 변경 없음. |
| Numerical equivalence | 새 source의 CI regression PASS. 기존 직접 lane-byte 증거는 재사용. |
| Implementation correctness | CI isolation 수정 PASS_SCOPED; 해당 P2 CLOSED. |
| Measured acceleration | 새 측정 없음. 기존1313의 audit-only 성능 결과 유지. |
| Memory and resource behavior | bounded child 및 inherited lower-limit assertion이 CI에서 PASS. 새 NCP/RSS 측정 없음. |
| Physical validity | NOT_ESTABLISHED. 기존 U5 실패와 global convergence NOT_RUN 유지. |
| Production readiness | NOT_APPROVED. |

검토 범위에 남은 P1/P2는 없다. 70a source의 CI gate는 실제 성공으로 닫혔다. 이후 delivery 변경의 CI와 원격 보존은 별도 receipt가 필요하다. 이 감사는 미래 delivery HEAD, NCP host64core/128GB의 실제 가용성, full h4 실행 allocation, 전역 수렴, REI 활성화나 production 승인을 부여하지 않는다.
