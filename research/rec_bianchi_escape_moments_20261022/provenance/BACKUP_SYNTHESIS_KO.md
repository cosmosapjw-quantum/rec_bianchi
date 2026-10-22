# REC/REI recombination 백업·대화 조사 — R1 보존 근거

작성 시각: 2026-10-22T22:36:08.861Z (UTC)  
작업자: /root/latest_backups  
선택 범위: **R1의 현재 근거·보존 상태 파악**. 새 이론 유도, RHS/ODE 실행, 과거 cohort 재실행, 원격 변경은 수행하지 않았다.

## 현재 결론

현재 접근 가능한 REC 날짜 백업 폴더와 Drive 최상위 목록을 대조했을 때, 최신 REC 보존물은 **THERM02 Stage C**다. Dropbox 수정 시각은 2026-10-22 18:00:11 UTC, Drive는 18:00:17.626 UTC이며 이름과 **28,138,141 bytes**가 일치한다. 이 파일은 부모 작업의 이미 완료된 checkpoint다. 이번 조사는 같은 ZIP을 다시 다운로드하거나 payload 검증하지 않았다.

별도 REI 후속 자료는 **PR221 coupled-isotope sandbox**와 연결된다. 파일명에 포함된 `de84e782db1e`를 현재 Git HEAD로 취급하지 않는다. GitHub 조사 담당자는 현재 HEAD `9620e1fcc4bdda76e0311206f614234926600381`, science commit `569f784e78676123513b7390001d317eb62d6372`를 확인했다. [GITHUB_INVENTORY.json](GITHUB_INVENTORY.json)과 합쳐 최종 source lock을 정한다.

전체 대화 검색은 현재 세션에서 **사용 불가**였고, 대형 공용 백업 폴더의 과거 전체 목록에도 실제 API 제한이 있다. 따라서 “모든 대화와 모든 백업을 전수 확인했다”는 결론은 내리지 않는다. 아래의 명시된 최신 프로젝트 폴더·검색 범위 안에서 닫는다.

## 1. 다음 DAG에 영향을 주는 핵심 연결

| 연구 단위 / 보존물 | Dropbox | Drive | 이번 확인 / 다음 사용 |
|---|---|---|---|
| REC125 / THERM02 Stage C | `id:BSpOijBcT10AAAAAAD_kpA` | [Stage C ZIP](https://drive.google.com/file/d/1m2pIfhxZd8AiDphUMgz_TAanl1pIl0IX/view?usp=drivesdk) | 양쪽 28,138,141 bytes. 부모의 기존 whole-GET·SHA·CRC·181 payload PASS를 재사용. |
| REC119 / H/He/Li final | `id:BSpOijBcT10AAAAAAD_hpA` | 이번 범위에서 exact-ID 연결 미확정 | 27,040,521 bytes의 존재·metadata 확인. REC126과 원래 685-payload 복구 결과는 기존 근거로 유지. |
| REI220 / isotope quotient final v2 | `id:BSpOijBcT10AAAAAAD_hrw` | [Stage C final v2](https://drive.google.com/file/d/1sLe-jWxxq_tQ4bBmVRV8zEGQ-IappMRe/view?usp=drivesdk) | 양쪽 목록상 20,388,650 bytes. REI129의 별도 cohort, 첫 실패 raw의 역사적 local-only 범위를 유지. |
| REI221 / coupled isotope sandbox | `id:BSpOijBcT10AAAAAAD_h6A` | [Sandbox ZIP](https://drive.google.com/file/d/1nbxnozIHfN7ueiYPhad9iWLjAcwWensl/view?usp=drivesdk) | 양쪽 metadata 440,240 bytes. PR/과학 commit 연결은 GitHub 담당자의 읽기 결과. |
| REC diagnostic C2 | `id:BSpOijBcT10AAAAAAD_jvA` | 이번 조회에서 짝을 확인하지 못함 | 3,792,753 bytes, 17:45:14 UTC. `INTEGRITY.json`, `RESTORE_AUDIT.json` 동반. PR 연결/내용은 별도 GitHub 조사에 맡김. |
| REI219 bootstrap thermal providers | `id:BSpOijBcT10AAAAAAD_h1w` | [Provider ZIP](https://drive.google.com/file/d/1T3EbVgrHWxV5doCYhjO7RyUPslooMfhq/view?usp=drivesdk) | 양쪽 목록/metadata 20,634,190 bytes. runtime 문서의 존재가 계산 완료를 추가로 증명하지 않음. |
| HyRec/RECFAST reference | `id:BSpOijBcT10AAAAAAD7rUg` | [Reference ZIP](https://drive.google.com/file/d/1f-lbA1cXaGCMTroWY4rK2voJL4735MLy/view?usp=drivesdk) | 양쪽 metadata 2,261,457 bytes. 높은 적색편이 recombination 재사용 후보. |
| HMLA Q0 | `id:BSpOijBcT10AAAAAAD74cw` | [HMLA ZIP](https://drive.google.com/file/d/1_FrGd0hHAWpF8PBR8MXEoznZ7sXcouhm/view?usp=drivesdk) | 양쪽 목록/metadata 2,754,441 bytes. 내용과 적용 범위 검토를 위한 입력 후보. |

REC 파일의 관측 경로는 `ns:183516487//bianchi/rec_bianchi/20261016/`, 최근 REI 파일의 관측 경로는 `ns:183516487//bianchi/research_backups/rei_bianchi/`다. HyRec/RECFAST와 HMLA Q0는 `/BASS_DERIVATION_DOSSIERS_20260912/`에 있다.

파일명 `FULL_EXEC`, `FINAL`, `RESTORE_AUDIT`는 식별 단서다. 이번 조사에서 해당 내용이나 실행을 재검증했다는 상태 표시는 아니다.

## 2. 실제 조회 범위와 pagination

총 **43회**의 provider/context 읽기 호출을 기록했다. **41회 응답 성공, 2회 명시적 오류**다. 독립적인 metadata record **1,478개**를 식별했고, 검색과 폴더 조회 사이의 중복은 provider+ID로 합쳤다. 원자료 다운로드는 **0**, 새 ODE/RHS/과학 테스트는 **0**, 원격 mutation은 **0**이다.

| 조회 | 실제 반환 | 종료·한계 |
|---|---:|---|
| Dropbox `/bianchi` 직접 하위 | 36 | `has_more=false` |
| Dropbox `/bianchi/rec_bianchi` 직접 하위 | 29 | `has_more=false` |
| Dropbox REC `20261016` | 76 | `has_more=false` |
| Dropbox REC `20261015` | 1 | `has_more=false` |
| Dropbox REC `TMP_PRESERVE_20261019` | 57 | `has_more=false`; 대형 archive는 다운로드하지 않음 |
| Dropbox `/bianchi/rei_bianchi` 직접 하위 | 41 | `has_more=false` |
| Dropbox `/bianchi/research_backups` | 1 | `has_more=false` |
| Dropbox 해당 `rei_bianchi` 직접 하위 | 73 | `has_more=false` |
| Drive 최상위 직접 하위 | 296 | 요청 상한 1,000 미만, exposed continuation 없음 |
| Drive `rec_bianchi_research_backups` | 17 | 동일 |
| Drive `rei_bianchi_research_backups` | 175 | 동일 |
| Drive `REI_RESEARCH_BACKUPS`와 그 `rei_bianchi` | 2 + 13 | 동일 |
| Drive C15 bridge 폴더 | 1 | 동일 |
| Drive `recombination` 문서검색 | **100 + 100 + 100 + 55 = 355** | 반환 token을 매번 그대로 전달, 마지막 페이지 token 없음 |
| Drive 최근 이름검색 / 최근 문서검색 / HyRec 문서검색 | 47 / 25 / 13 | metadata 조회; ZIP 범위는 보장하지 않음 |
| Drive BASS dossiers 직접 하위 | **1,000** | 상한 도달, 도구에 continuation 입력 없음 |
| Personal Context 대화검색 | 0 | `Personal context is unavailable for this conversation.` |

Dropbox의 broad search들은 최대 1,000개를 요청했는데도 일부가 정확히 **100개와 `has_more=false`**를 반환했다. `include_folders=false` 요청에도 폴더가 나타난 사례가 있었다. 이 검색을 전역 완전성·필터 정확성의 증명으로 쓰지 않고, 실제 프로젝트 폴더 목록을 우선했다. `recombination` 54개, `RECFAST` 8개, HMLA exact-name 1개도 별도 기록했다.

Drive 검색은 이미 존재를 아는 ZIP들을 누락했다. 그래서 직접 폴더 조회와 정확한 ID의 metadata를 사용했다. BASS dossiers에서 `top_k=5000`으로 확장한 호출은 **HTTP400, 허용 page size 1–1000**을 반환했다. 이 경로는 더 재시도하지 않았다. 따라서 공용 dossiers의 오래된 1,000개 이후 파일은 **미열람 범위**다. 최신 관련 파일은 조회된 부분에서 식별했다.

전체 query, timestamp, 요청 인자, row count, pagination 여부, 오류와 반환 ID는 [BACKUP_INVENTORY.json](BACKUP_INVENTORY.json)에 있다. 관련 없는 최상위·공용 파일의 상세 metadata는 산출물에서 제외하되 원래 반환 개수는 보존했다.

## 3. 근거·권한·물리 주장 분리

- **권한:** 부모가 위임한 R1의 읽기 전용 discovery와 지정한 로컬 산출물 작성이다. 원격 게시/업로드 권한으로 확대하지 않았다.
- **이번 직접 근거:** 파일·폴더 존재, 관측한 ID/경로/수정 시각/크기, 실제 search pagination, 오류 응답.
- **재사용한 기존 근거:** THERM02의 기존 Dropbox full GET/SHA/CRC/181 payload PASS와 REC119 복구 완료, REI220의 별도 완료 cohort. 이번 metadata 조회가 이를 새로 수행한 것은 아니다.
- **유형:** 이름·크기 일치는 metadata observation이다. ACK+size를 BYTE_IDENTITY 또는 whole-byte 검증으로 승격하지 않는다.
- **현재 물리 범위:** 21 population, prescribed T/UV 및 조건부 atomic closure의 역사적 범위를 유지한다. 별도 thermal pilot의 자료가 있어도 모든 핵종의 완전한 핵반응망·열역학적 폐쇄 완료로 묶지 않는다.
- **보존 경계:** REI 첫 실패 raw의 historical local-only 상태를 새 remote archive의 존재만으로 바꾸지 않는다.
- **잠금:** Physical HOLD, REC U5 HOLD_9_FAIL/HOLD_8_FAIL 및 CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false.

## 4. successor DAG에 전달하는 결과

이번 하위 작업의 완료조건은 “접근 가능한 최신 백업의 식별자·보존 수준·범위 제한을 확정하여 중복 실행을 피할 수 있게 하는 것”이다. 그 조건을 충족했다. 이후 과학적 선택·계약은 부모가 GitHub inventory와 원문 source를 결합하여 정한다.

| DAG 항목 | 상태 | 전달 내용 |
|---|---|---|
| R1 보존물 inventory | **DONE — 명시된 접근 범위** | 이 JSON/요약, 실제 pagination·실패 범위 |
| 최신 Git HEAD 연결 | **부모·GitHub 담당자 통합** | THERM02, REI221, REC diagnostic C2 및 REI219 교차참조 |
| 재사용 입력 확보 | **IDENTIFIED** | HyRec/RECFAST·HMLA Q0 식별자; 내용 검증·계산 재실행 아님 |
| source-bound successor 계약 | **부모의 다음 선택** | energy ledger, ionic yield, 유한 수용 기준을 최신 source와 결합 |
| 새 coding/IVP | **이번 작업 범위 밖** | 과거 REC126/REI129/warm729/완료 8-case 계열 재실행 없음 |

## 5. 복사 가능한 최소 handoff

```text
R1 backup/context inventory completed in the explicitly observed scope.
Read recombination_next_work/BACKUP_INVENTORY.json and BACKUP_SYNTHESIS_KO.md,
then combine with GITHUB_INVENTORY.json.

THERM02 / REC125 current parent checkpoint:
HEAD b28b387fecd6cc71fddb98e95f336eba5f8a647f
science commit 407a280aff51abefc10374cb6e21c4224140328c
Dropbox id:BSpOijBcT10AAAAAAD_kpA
Drive 1m2pIfhxZd8AiDphUMgz_TAanl1pIl0IX
ZIP 28138141 bytes, SHA b4ebbc130c4626973f3b6ed1bef372a299678756bac708107dc92c7a3842d649.
Existing Dropbox wholeGET+CRC+181payload PASS reused; no repeat download here.
Drive metadata/size only; whole-byte NOT_RUN.

REI221 coupled-isotope sandbox:
HEAD 9620e1fcc4bdda76e0311206f614234926600381
science 569f784e78676123513b7390001d317eb62d6372
Dropbox id:BSpOijBcT10AAAAAAD_h6A
Drive 1nbxnozIHfN7ueiYPhad9iWLjAcwWensl, 440240 bytes.
Filename de84e782db1e is not the current HEAD.

HyRec/RECFAST candidate: Dropbox id:BSpOijBcT10AAAAAAD7rUg,
Drive 1f-lbA1cXaGCMTroWY4rK2voJL4735MLy, 2261457 bytes.
HMLA Q0 candidate: Dropbox id:BSpOijBcT10AAAAAAD74cw,
Drive 1_FrGd0hHAWpF8PBR8MXEoznZ7sXcouhm, 2754441 bytes.
These were inventoried, not re-executed.

Personal Context returned unavailable; full prior conversations not enumerated.
Drive recombination document search exhausted 4 pages / 355 rows.
Drive BASS dossier list capped at1000; no exposed continuation; top_k5000 returned400.
Dropbox broad search100 limits do not prove global completeness.
Archive downloads=0, remote mutations=0, new ODE/RHS/tests=0.

Keep REC126 and REI129 identities/cohorts separate. First failed REI raw historically local-only.
Keep Physical/REC U5 HOLD, global convergence NOT_RUN, production NOT_APPROVED,
REI_activation=false. Bind next source/energy/yield/finite-acceptance contract before new computation.
```

## skill_context_used

실제 읽고 적용한 `physmath-research-loop 1.3.0`의 기준 경로:

`/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop/`

- `SKILL.md`
- `STAGE_SELECTION.md`
- `references/SUBAGENT_MODE.md`
- `references/POLICY_INTEGRATION.md`
- `references/STAGE_GUIDE_KO.md`의 R1
- `references/THEORY_LOOP.md`의 R1 계약

적용 결과: 부모의 R1 경계를 지켰고, 실제 provider 근거와 기존 보존 근거를 분리했으며, 실패한 접근 경로를 반복하지 않았다. 새 IVP·전역 검증·원격 게시로 범위를 넓히지 않았다. 이 산출물의 외부 게시/백업은 부모의 통합 단계에서 처리한다.

