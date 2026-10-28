# 백업 조사 결과

이 조사는 읽기 전용 목록과 지정 Library 문서 3건의 본문 확인이다. ZIP 전체 bytes 재검증과 과학 실행은 하지 않았다.

## Dropbox (초기 조사: 아래 후속 조사에서 커서 완료)

/bianchi 직계 39개: 1페이지, has_more=false. 지정 /bianchi/rec_bianchi/20261016은 315개, 1페이지, has_more=false.

| 범위 | 항목 | 성공 페이지 | has_more | 커서 남음 | 완결 |
|---|---:|---:|---|---|---|
| bass-master-ssot-v2-w0w1-20260901 | 11 | 1 | False | False | True |
| rec_bianchi | 29 | 1 | False | False | True |
| bass-master-ssot-v2-w2-20260901 | 13 | 1 | False | False | True |
| rei_bianchi | 23400 | 39 | True | True | False |
| program-sync | 16 | 1 | False | False | True |
| control-plane | 11 | 1 | False | False | True |
| research_backups | 367 | 1 | False | False | True |
| htt_research_backups | 7 | 1 | False | False | True |
| _runtime_receipts | 364 | 1 | False | False | True |
| htt_base | 14510 | 41 | True | True | False |
| _runtime_attempt_state | 1 | 1 | False | False | True |
| rec_bianchi/.git | 1800 | 3 | True | True | False |
| rec_bianchi/tests | 114 | 1 | False | False | True |
| rec_bianchi/rust | 17 | 1 | False | False | True |
| rec_bianchi/data | 41 | 1 | False | False | True |
| rec_bianchi/research | 124 | 1 | False | False | True |
| rec_bianchi/.github | 2 | 1 | False | False | True |
| rec_bianchi/archive | 1307 | 3 | False | False | True |
| rec_bianchi/scripts | 55 | 1 | False | False | True |
| rec_bianchi/src | 69 | 1 | False | False | True |
| rec_bianchi/TMP_PRESERVE_20261019 | 57 | 1 | False | False | True |
| rec_bianchi/docs | 539 | 1 | False | False | True |
| rec_bianchi/state | 201 | 1 | False | False | True |
| rec_bianchi/artifacts | 4 | 1 | False | False | True |
| rec_bianchi/environment | 1 | 1 | False | False | True |
| rec_bianchi/20261015 | 4 | 1 | False | False | True |
| rec_bianchi/.cuh | 41 | 1 | False | False | True |
| rec_bianchi/20261016 | 315 | 1 | False | False | True |
| /ode_solver | 4 | 1 | False | False | True |
| /BASS_BACKUPS | 338 | 1 | False | False | True |
| /BASS_DERIVATION_DOSSIERS_20260912 | 5322 | 9 | False | False | True |
| /bianchi_phase_r_bootstrap_v1.2 | 8668 | 15 | False | False | True |

htt_base와 rei_bianchi는 마지막으로 저장된 성공 페이지에 has_more=true다. 직후 요청의 오류는 개별 목록에 저장되지 않았으므로 그 정확한 원인은 미확정이다. rec_bianchi/.git 후속 페이지와 두 별도 직계 목록 요청에서는 `RATE_LIMITED`: “Rate limit exceeded. Please try again later.” 응답을 실제로 받았다. retry_after 값은 반환되지 않았다. 원문은 `rec_bianchi_split.json`과 `dropbox_rate_limit_raw.json`에 있다. 재시도하지 않았으며, 새 업로드가 제한될지는 이 읽기 오류만으로 확정할 수 없다.

## Drive

지정 폴더는 161개 항목과 ZIP 139개가 반환됐다. 4개 관련 root 및 하위 69개 폴더를 조회했다. list_folder는 응답에 후속 토큰·완결 신호가 없어 전수 완결을 보증할 수 없다. BGJET document 검색은 0건이었지만 지정 폴더에는 BGJET ZIP 23개가 있어 document 검색은 ZIP 전수 근거가 아니다.

## 주요 위치

- Thermal SOURCE: `REC_H5_THERMAL_PATH_DEFECT01_SOURCE_20261028_4a9d83540a40.zip`, 1,608,787 bytes; Drive ID `1gWgnUJcdM3gQjpIahana4mLY1zr6XAdK`, Dropbox ID `id:BSpOijBcT10AAAAAAEDJwg`. 요청 측이 95 payload / 96 members로 식별했으나 이 목록 조사에서 ZIP 내부를 확인하지 않았다.
- QSS03 C3: `REC_H5_QSS03_C3_20261028_9a59a1f80201.zip`, 94,641 bytes; Drive ID `1A0giy-weBrEUmLnh_QMiz00g4yWct-CN`, Dropbox ID `id:BSpOijBcT10AAAAAAEDI_Q`.
- Library에서 chemical report, LINE02 handoff, BG R9 delivery receipt 세 건의 전문을 읽었다. 정확한 ID와 메타데이터는 JSON 기록에 있다. 최신 title 검색 네 건은 각각 100건과 후속 커서가 남아 있다.

파일 목록의 존재·크기는 기존 업로드의 실제 ACK나 원격 전체 bytes 동일성 검증과 다르다. 기존 보고서의 ACK 주장은 해당 원문 기준으로만 해석한다.

## 커서 재개 후속 조사

기존 저장된 커서를 이어 읽었다. 원 `/bianchi` recursive 커서와 세 분할 커서, Drive 세 검색, Library 네 검색 모두 terminal에 도달했다. 새 요청 제한 오류는 없었다. 기존 htt_base/rei_bianchi의 당시 중단 원인은 여전히 UNKNOWN이다. 이전 Dropbox 검색 제한과 실제 stage 업로드 성공은 별도 사건이다.

| 제공자 / 목록 | 추가 페이지 | 반환 항목 | 기존·중복 | 신규 고유 ID | terminal |
|---|---:|---:|---:|---:|---|
| Dropbox htt_base | 51 | 30472 | 0 | 30472 | True |
| Dropbox rei_bianchi | 57 | 27367 | 0 | 27367 | True |
| Dropbox rec_git | 6 | 3416 | 0 | 3416 | True |
| Dropbox original | 202 | 107070 | 104088 | 2982 | True |
| Drive Bianchi | 4 | 399 | 4 | 395 | True |
| Drive CMB | 1 | 36 | 1 | 35 | True |
| Drive thermal | 3 | 253 | 3 | 250 | True |
| Library Bianchi | 24 | 2384 | 0 | 2384 | True |
| Library REC | 43 | 4291 | 0 | 4291 | True |
| Library REI | 18 | 1756 | 0 | 1756 | True |
| Library VigilODE | 3 | 245 | 0 | 245 | True |

Dropbox 중복은 저장된 기존 목록과 이번 앞선 목록의 file_id(없는 경우 path)를 기준으로 했고, Drive/Library는 각 검색의 기존 ID와 비교했다. 서로 다른 시점의 snapshot을 단순 합산하지 않는다. Drive 폴더 목록 자체에는 완결 신호가 없다는 한계는 그대로다. 목록 확인은 원격 전체 bytes 검증이나 업로드 ACK를 뜻하지 않는다.
