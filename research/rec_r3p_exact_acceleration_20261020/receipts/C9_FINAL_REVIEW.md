# REC R3P 최종 독립 C9 후속 검토

**대상 commit:** `e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d`
**최종 실제 파일 확인:** 2026-10-20 06:03:36 UTC
**실행 allocation:** `R3P_U5_SMOKE16_20261020_001`

## 판정

**검토한 Stage2 resource guard와 source/receipt 연결 범위에 남은 P1/P2는 발견하지 못했다. C9-01 후속 검토를 이 정확한 commit에서 닫는다.** 실제 supervisor·worker·profile·verification의 해시와 내용이 일치하며, 16-step 실행은 `first_failure=null`, 종료 코드 0, 원래 상태 **`SMOKE_ONLY`**를 기록한다. same-h 항목의 원래 명칭 **`PASS_PENDING_REVIEW`**도 그대로 보존한다.

리뷰어는 후보 코드를 작성하지 않았다. 이 후속 검토에서는 파일 읽기·Git object 대조·hash/JSON 검증만 수행했다. 저장소 수정, 후보 import, 추가 test/benchmark/build 또는 물리·수치 실행을 하지 않았다. 아래 49개 확인은 파일/영수증 일관성 조건이며 실행한 후보 테스트 수가 아니다.

## 1. 정확한 소스와 불변성

05:58:20, 06:01:28 및 06:03:36 UTC 확인에서 HEAD는 위 Stage2였고 tracked checkout은 clean이었다. 앞서 정적 검토한 다음 5개 SHA가 **현재 파일 및 해당 commit blob과 일치**한다.

| 검토 파일 | SHA-256 |
|---|---|
| `scripts/run_r3p_u6_supervised.py` | `e22c11253f450b3b4b07cc9212d0ebafb1a2bc0d29844cac14de7f453ab437f9` |
| `scripts/run_r3p_u6_audited.py` | `4e0e2482b163c044b9b1b35a8831a7d57aa6440ad8fac98ec79d00889a6f1bb4` |
| `tests/trajectory/test_r3p_u6_audited.py` | `d7d5dbc24f9eb1e57ebcfad2788fd315129d15eaba4818116d080bf7fe34d84d` |
| `scripts/build_r3o_rust.py` | `d33f4761482720cd822a3006460e9462091c9219180541e78cdc51a4ca35cfd5` |
| frozen `scripts/verify_r3i_h2_u6_rt_boundary.py` | `8f30859e99136a5a916ca046bf553c24943d798ef67e783cc295fb4ef9327b50` |

worker의 추가 source **23개 전체**에 대해 receipt SHA = 실제 파일 SHA = Stage2 commit blob SHA를 확인했다. frozen V6 manifest의 **109개 실제 파일 전체**도 원래 SHA와 일치한다. profile source는 worker source와 동일한 audit/build/input launch metadata를 포함한다. 최종 재독해에서도 23개 source, 109개 frozen 파일, 실제 영수증 4개가 그대로였다.

| 원래 입력/빌드 결속 | 실제 확인한 SHA-256 |
|---|---|
| Frozen V6 manifest | `f02f4e0b39dfafbb7656704cee59b8d95c976e9b55e840141d333be15b452585` |
| 원래 U5 checkpoint | `7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b` |
| 원본 October 2012 ZIP | `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27` |
| BUILD_001 receipt | `d53d84663162989f9c6f63731754a253effe8d212bbea84aba222b134c266602` |
| BUILD_001 실제 Rust library | `7e6f4bde4497d7771d0f45167d4c7a33a000949d248cab33bbffa126564aaec8` |
| Vendor archive | `911f4fedc55891656e638b6b9131a57f081a1c7980fcdbb13f3b3e9263c51fc0` |

필수 build source 집합과 hash도 build receipt와 완전히 같았다. 기존 frozen atomic/thermal 연산, stage/causal guard를 바꾸는 변경은 이 후속 guard 수정에 없다. 실행 metadata의 `h=4.245e-5`, `REI_activation=false`도 확인했다.

## 2. Stage2 → supervision → worker → verification

| 실제 영수증 | SHA-256 |
|---|---|
| [supervision.json](smoke16/supervision.json) | `294cdc2eec8a2f30c61444599f6fe907234900974e424d3afbc1b7ddedd1102b` |
| [r3p_smoke16_001.r3p_execution.json](smoke16/r3p_smoke16_001.r3p_execution.json) | `b3673f7fcd10ffd2bcd3652fcdb7744f2aeb28e725594be70f0677eaeb5af403` |
| [r3p_smoke16_001.r3l_profile.json](smoke16/r3p_smoke16_001.r3l_profile.json) | `28aada196ab9736a7566a5df8dcaefdd0482d51eb94b3603929fdf7bb920528b` |
| [verification.json](smoke16/verification.json) | `b759d530776873ce7c0080a077e9d67280044d2a540a769a33995ec94170172b` |

supervisor의 expected commit, worker/profile의 source commit은 모두 Stage2다. supervisor가 기록한 worker receipt hash가 실제 worker 파일과 같고, worker의 profile hash 및 worker/profile의 verification hash가 실제 파일과 같다. 두 verification 요약도 실제 verification JSON과 완전히 일치한다. 이는 파일 identity 연결이며 외부 서명이나 원격 backup readback을 대신하지 않는다.

supervisor 및 worker command **exit=0**; supervisor/worker/verification **`first_failure=null`**; profile **`run_error=null`**; closeout/profiling errors=[]다. worker source identity=`UNCHANGED`, profile accounting=`VALID`다. 실제 worker logs, native/common binaries, 추출 C source 4개 및 작은 partial evidence 6개의 hash도 해당 영수증과 일치한다.

## 3. 실제 16-step gate와 자원 범위

| 확인 항목 | 실제 기록 |
|---|---|
| 새 적분 구간 | **16 accepted steps / 16 full evaluations**; `HOLD_CAP_BEFORE_RT_BOUNDARY`; 마지막 iz=53195, RT boundary=58389 |
| Same-h spectral | **10,000 fields**; average 최대 ratio `2.1722981554269436e-5`, virtual `5.653137029811636e-6`, lyman `4.376735287656637e-6`; 모두 원래 단위 gate 미만 |
| Original average failures | **[]**; 이번 smoke에서 예외적 Decimal80/IEEE 경로로 넘긴 original-average 실패 없음 |
| Causal history | **5,008 links=16×313**, accepted_inputs=16 |
| Common-input oracle | **PASS, 2 sampled evaluations**; 16회 전체 common-input 재검증으로 확대하지 않음 |
| 기존 prefix 감사 | **5,254,162 records**, attempted=validated; 16,733 columns, Rust1, block columns=32 |
| Prefix scratch | max text=356,988 bytes <4 MiB; max array scratch=163,536 bytes |
| Whole supervisor CPU/wall | **8.826414 CPU초 / 8.790703708000365 wall초** |
| 마지막 receipt write reserve | **2 CPU초 / 3 wall초**; 실제 write 측정값이 아닌 예약분 |
| 전체 측정값 + reserve | **10.826414 <60 CPU초**, **11.790703708000365 <180 wall초** |
| 실제 inherited CPU 처리 | frozen 요청 `[60,60]`, inherited `[58,59]`, 적용 **`[58,59]`** |
| 메모리 및 스레드 | AS=2,147,483,648 bytes; sampled worker-tree RSS 최대=383,242,240 bytes; affinity `[0]`, BLAS/OMP=1, Rust threads=1 |

state/RHS·coupled-stage·Schur·count/end/finite 검사도 comparator가 정상 반환한 영수증과 검토한 원래 제어 흐름에 결속된다. 이것은 새 smoke의 tolerance gate 확인이며, 앞서 수행한 saved-stream 15개 bitwise 대조와 구분한다. 이번 리뷰어가 raw trajectory를 다시 계산한 것은 아니다.

전체 자원 측정은 worker preflight, 모든 worker/descendant 작업, worker closeout, 최종 artifact hashing을 포함한다. **최종 supervisor receipt serialization/fsync만 위 reserve로 처리한다.** 메모리는 **per-process RLIMIT_AS + 50 ms polled worker/descendant RSS**다. supervisor RSS를 포함한 정확한 전체 합계 또는 정확한 peak라고 주장하지 않는다. 이 범위는 실제 `memory_scope`에 명시되어 있다.

## 4. Finding 종결과 남는 범위

| 항목 | 최종 판정 및 근거 |
|---|---|
| C9-01, 원래 P2 | **이 commit에서 CLOSED.** public CLI가 수치 import 전에 supervision으로 진입한다. Budget이 preflight/closeout을 포함하고 마지막 hash 뒤 resource reserve 판정을 한다. 실제 16-step supervisor receipt로 경로 실행도 확인했다. |
| C9-02/03, 원래 P2 | **문서 계약 수정으로 CLOSED.** Rust는 canonical four-ASCII-field 문법과 더 엄격한 metadata 조건을 받는다. earliest logical failure는 전달된 bounded block 내부이며 resource/transport/size abort가 앞설 수 있다. 전체 legacy 입력 언어·incidental exception 동일성을 약속하지 않는다. |
| C9-04, 과거 P1 | **Stage1 benchmark 수정 및 기존 복구 실행으로 CLOSED.** 이 Stage2 worker에서도 inherited `[58,59]` 보존을 확인했다. 과거 실패 영수증을 삭제하거나 실패 sample을 수치 PASS로 바꾸지 않았다. |
| 현재 남은 P1/P2 | **검토한 변경 소스 및 실제 receipt 연결 범위에서 없음.** 모든 ABI caller/OS/platform/abort 경우의 보편적 증명은 아니다. |

정확한 근거 소스:

- [public dispatch 및 worker contract, L25](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d/scripts/run_r3p_u6_audited.py#L25), [inherited clamp, L232](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d/scripts/run_r3p_u6_audited.py#L232), [source/build closeout, L400](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d/scripts/run_r3p_u6_audited.py#L400).
- [whole-worker Budget와 최종 판정, L85](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d/scripts/run_r3p_u6_supervised.py#L85), [수치 import 전 제한, L119](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d/scripts/run_r3p_u6_supervised.py#L119).
- [원래 spectral gate, L278](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d/scripts/r3p_stream_audit.py#L278), [count/end 검사, L322](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d/scripts/r3p_stream_audit.py#L322), [frozen SMOKE_ONLY 분기, L440](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d/scripts/verify_r3i_h2_u6_rt_boundary.py#L440).

## 5. 검토 증거와 유지 판정

[독립 파일/JSON 대조 기록](C9_SMOKE16_CROSSCHECK.json)의 **49개 조건 모두 일치**했다. SHA는 `46b5b05552411f79da89aa545b84fa56f1c70fda41143047db2239b94dccbdd7`다. [최종 파일 불변성 기록](C9_FINAL_STABILITY.json)과 [최종 machine receipt](C9_FINAL.json)를 함께 남긴다. 앞선 finding/수정/실패 이력은 [상세 C9 보고서](C9_STAGE1_REVIEW.md)에 보존한다.

**old U5 h=`HOLD_9_FAIL`, h2=`HOLD_8_FAIL`, cost=`CLOSED_HOLD_NOT_RESET`를 유지한다.** 이번에 확인한 것은 exact Stage2 소스의 guard와 실제 bounded smoke의 증거 연결이다. full run admission, global convergence, production speedup은 확립하지 않는다. 부모가 알린 Actions 4개 성공 및 backup ACK는 별도 부모 증거이며 이 리뷰에서 독립 remote 조회를 수행하지 않았다.
