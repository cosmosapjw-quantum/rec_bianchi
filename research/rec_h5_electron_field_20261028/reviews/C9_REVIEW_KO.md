# C9 — 독립 source·구현·실행 결과 검토

판정: **PASS_SCOPED**. 검토 상태: **CLOSED**. 미해결 차단 finding은 0개다. 동결한 explicit-incoming electron source-point component의 구현과 이번 132개 primary 결과를 채택하며, 다음 행동은 C9 게시와 C10 완전한 source/delivery 인계다. C10 저장 완료 여부는 별도 전달 상태로 관리한다.

## 검토자와 실제 방법

Reviewer는 별도 nonauthor agent `/root/electron_c9_independent`다. 이 reviewer는 adapter, binder, runner, Decimal validator를 작성하지 않았다. 구현은 `/root/delivery_implementation` 및 별도 validator 작성자 역할에서 수행되었으며 reviewer는 원본 source, 최종 code, raw results와 실제 resource receipts를 읽었다. 요청 모델은 `gpt-6-astra`, 관측 runtime model identity는 `NOT_OBSERVED`다. 역할 분리를 다른 model-family의 검증이나 CAS의 구현 승인으로 표현하지 않는다.

원본 ZIP의 선택한 hydrogen.c를 직접 읽어 block orientation, source scalar, temperature path를 독립적으로 재구성했다. 최종 검토는 보고서 요약보다 실제 source/diff와 C6–C8 raw evidence를 먼저 대조했다. 새 compilation, native/kernel call, science calculation, residual 재실행, test, probe, remote write는 모두 0이다. 파일 byte/SHA와 기존 JSON record의 identity·count·값 표현을 대조하는 metadata 검토만 수행했다. 정확한 읽기 범위와 파일 bytes/SHA는 C9_RECEIPT.json에 기록한다.

## Source와 구현

불변 입력 16개는 SOURCE_MANIFEST의 bytes/SHA와 모두 일치한다. 원본 hydrogen.c는 37471bytes, SHA256 `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b`다. 최종 code 8개의 SHA와 실제 library SHA는 성공한 C6 build receipt에 일치한다. 전체 원본 archive의 앞선 복원·SHA 증거는 재사용했으며 이번 reviewer가 archive 전체를 다시 해시하지 않았다.

Adapter는 원본 ratio=TM/TR, rescale_T(TR), TM=ratio*TR 경로를 한 번 적용하고, original calloc 초기화, table initialization/A2s normalization, cubic interpolation, feature macros 및 optical-depth branch를 보존한다. 명시적 signed incoming → populateTS_2photon → solve_real_virt → 원 FH grouping 순서가 맞다. Point call에는 history interpolation·integration·write나 파일 IO가 없으며, table 파일 IO는 context 초기화 경계에 있다.

Generated native source diff는 observer header와 세 value-only hook으로 한정된다. 원 diag0 division 직전, 실제 denom assignment 직후, 실제 Schur det assignment 직후를 관측한다. Outside diffusion diagonals 231개는 수정되지 않는 원 matrix에서 한 번씩 관측한다. TLS diagnostics pointer는 저장·복원되고 추가 solve는 없다. 원본 solver의 Trv=B, Tvr[i][b]=C_bi, Tvv[1]=lower, Tvv[2]=upper 및 native summation order가 유지된다.

## 실제 binding과 purity

132개의 bound input과 primary record를 실제 CALLS/QSS_WRITES/WRITES/LAST_WRITERS에 대조했다. 각 (call_id,slot), saved FH/xr/xv, dispatcher scalars 및 coefficient temperature provenance가 일치한다. C1에서 수정한 coefficient-temperature locator는 WRITES.jsonl이며 QSS_WRITES는 departure/incoming 자료다. 해당 교정은 source mapping에 한정되고 식·허용오차 변경은 없다.

313 query mapping은 626 endpoint references, original binding과 geometric exact alpha를 보존한다. Primary 132개 raw API output과 primary serialization도 일치한다. 모든 primary의 status=0, input_nonmutation=true, table_nonmutation=true, Fe=FH를 확인했다. Saved/new coefficient temperatures는 represented binary64 bit가 모두 같다. 일부 동등한 hex string의 자릿수 차이는 수치 차이로 판정하지 않았다.

각 primary에는 실제 472개 finite nonzero divisor 값이 있다. 분류별 count는 initial Thomas pivot 3, recursive pivot 237, outside diagonal 231, Schur determinant 1이다. Zero/nonfinite/overflow count는 모두 0이다. 이는 실제 평가 point의 적용 조건을 확인한다.

## 동결된 수치 수용과 controls

독립 validator source는 represented binary64를 Decimal.from_float로 정확히 가져오고, 80자리 작업 정밀도에서 올바른 B/C 및 band 방향의 MX-S와 S_F를 재구성한다. Frozen gate는 |FH_new-FH_saved| <=512 eps64 S_F와 normalized block residual <=4096 eps64이며, zero scale/denominator의 exact-zero 처리가 구현되어 있다. Tolerance widening이나 새 gate는 없다.

- FH parity: 132/132 통과. 실제 bitwise FH 132/132, xr 264/264, xv 41052/41052. Reviewer도 저장 raw 값의 binary64 bit equality를 대조했다.
- Independent residual: 132/132 통과. 저장된 최대 residual은 1.4989401807314334e-15이며, 동결 threshold는 9.094947017729282e-13이다. Reviewer는 validator와 저장된 세부 결과를 검토했으며 residual을 재실행하지 않았다.
- Decimal 40/80 비교: 사전 지정 indices 0,66,131에서 parity/residual 판정이 같다. 이를 rigorous interval enclosure로 확대하지 않는다.
- Saved-output mutations: B/C swap residual 약0.9999031, band swap 약0.02841408, changed solution 약0.3333333으로 각각 거부되었다.
- C6: 24개 invalid/binding cases가 native 진입 전에 구별되었고, 실제 native calls는 baseline과 signed incoming의 2회다.
- C8: indices 0,66,131에 zero, negative, doubled incoming을 적용한 9개 실제 controls의 residual과 nonmutation이 통과했다. 모든 control에서 A/B/C/V는 해당 primary matrix와 같으며 incoming 변화에 FH 응답이 관측되었다. Signed departures를 clipping하지 않는다. Affine second differences는 관측 보조값이며 새로운 tolerance gate가 아니다.

그림은 저장 primary/validator 결과를 사용한 plotting source와 실행 receipt를 확인했다. 두 PNG의 실제 시각 확인은 root의 C8_VISUAL_READBACK_KO.md를 재사용한다. 이 reviewer가 그림을 직접 열었다고 주장하지 않는다.

## 실패 처리와 자원

C6_attempt001은 과학 계산 전 PID namespace와 proc-visible PID를 혼동한 watchdog 오류로 종료되었다. 원 failure와 단일 observer-only 진단 raw를 읽었다. Namespace child7의 /proc/self PID는390951이지만 /proc/7은 무관한 sites-preview였다. 원인에 맞춘 최소 repair는 child가 기록한 proc-visible PID/starttime으로 family를 관측하고, wait4/killpg는 namespace PID를 유지한다. 실제 retry C6_attempt002는 성공했다. 이는 실행 환경 관측 오류의 교정이며 solver·scope·tolerance 변경이 아니다.

실제 ledger는 실패 CPU0.003394s와 진단0.065527s를 포함한다. Local child CPU4.642406s, 앞선 Wolfram reportedCPU0.06227s를 더한 known scientificCPU4.704676s, 남은 known budget55.295324s다. Stage charge는 C6 0.976597s, C7 0.525494s, C8 validation0.888929s, plots2.251386s다. 모든 성공 child는 wall30s/512MiB 범위 안이며 single-thread 환경과 실제 receipt가 있다. 비용은 wait4 범위의 관측값이고 parent/model/network/metadata/packaging 비용은 UNKNOWN_NOT_ZERO다.

Call journals의 known native calls는 C6 2+C7 132+C8 9=143, unfinished API attempts는0이다. Primary는 정확히132회다. 기존 producer/reference/native-history/old-tests/QSS03/audit science rerun은 이 실행 경로에 없으며 새 호출로 계상하지 않았다.

## 채택 범위와 종료

채택 범위는 FULL/H_STEADY/He-neutral/xe=xHII/fsR=meR=1, source units cm^-3·s^-1·eV에서 명시적 signed incoming311+2를 받는 point component Fe=FH다. Small residual은 coefficient assembly의 새 물리 oracle, box-wide nonsingularity/inverse gain, forward-error certificate를 제공하지 않는다. Autonomous coupled full-state field, incoming evolution, whole-domain defect, model discrepancy, initial error e0, positive physical tube는 별도 의무로 남는다.

Canonical28/88(+0), separateREI33/88는 합산하지 않음, physical0/313을 유지한다. Physical query/K/M2/defect/L/tube/e0/epsilon/outgoing=null, H6/H7OPEN, L4false, REIactivationfalse다. Strong no-go 신규 주장은 없다. 교정 두 건은 닫혔고 새 blocker는 없다. 이번 C9 scientific review는 종료하며 C10 packaging/delivery로 진행한다.
