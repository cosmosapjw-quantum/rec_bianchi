# Bianchi·CMB 연구와 백업 조사 종합

이 문서는 2026년 10월 28일에 보존된 조사 기록을 바탕으로 다음 연구 단위의 입력과 조사 한계를 정리한다. GitHub의 초기 기준 시각은 09:00:44 UTC이며, 그 뒤에 읽은 변경은 별도의 후속 조사 기록으로 구분한다. 목록에 나타난 결과와 내용을 직접 확인한 결과, 그리고 원본 ZIP의 바이트를 검증한 결과는 서로 다른 증거다. 이 문서의 작업에서 새 네트워크 검색이나 과학 계산은 수행하지 않았다. [초기 GitHub 조사](evidence/GITHUB_REPORT_KO.md) · [후속 조사](SURVEY_UPDATE_KO.md)

## 조사 범위와 보존 목록

연결에서 보인 소유자 저장소는 51개였고, 그중 중앙 DAG가 참조하는 저장소와 Bianchi·CMB 계보 및 실행 기반을 포함한 17개를 관련 조사 범위로 정했다. 이 17개 저장소의 브랜치와 열린 PR 목록은 각 페이지의 끝까지 수집했다. 브랜치는 1,823개다. 열린 PR은 **1,100개 수신 행, 1,099개 서로 다른 PR**이다. BASS PR 127이 두 페이지에서 중복으로 수신되었기 때문이다. 나머지 34개 저장소는 소유자 목록의 메타데이터 범위에 머물렀다. [저장소 목록](evidence/GITHUB_REPOSITORIES.json) · [브랜치 목록](evidence/GITHUB_BRANCHES.json) · [PR 목록](evidence/GITHUB_PULL_REQUESTS.json) · [정리된 inventory](inventory/SUMMARY.json)

초기 조사에서는 2026년 10월 27일 00:00 UTC 이후 갱신된 PR 64개와 현재 REC 판단에 필요한 문서에 원문 확인을 집중했다. 저장소별 issue 및 inline comment 목록도 페이지 끝까지 수집했으며, 선택된 REC PR의 timeline은 별도로 읽었다. 1,823개 브랜치의 모든 과학 diff와 과거 commit을 검토했다는 뜻은 아니다. 후속 조사에서는 같은 17개 저장소의 갱신 순 PR 목록을 초기 cutoff까지 다시 확인하고, 아래에 요약한 관련 변경의 본문 또는 명시된 source·status 문서를 선택적으로 읽었다. 각 항목의 읽기 깊이는 [후속 조사 기록](SURVEY_UPDATE_KO.md)에 남아 있다.

백업 조사에서는 기존에 남아 있던 Dropbox의 `/bianchi` 재귀 및 세 하위 목록 커서, Drive의 Bianchi·CMB·thermal 검색 커서, Library의 Bianchi·REC·REI·VigilODE 검색 커서를 모두 끝까지 이어 읽었다. 원 `/bianchi` 재개분 107,070개 행 중 104,088개는 기존에 관측한 ID 또는 경로와 겹쳤고 2,982개는 새로 식별되었다. 서로 다른 시점의 snapshot과 서로 겹치는 검색 결과는 단순히 합산하지 않았다. 정리된 보존 목록에는 Dropbox 122,004개, Drive 1,568개, Library 7,045개의 고유 메타데이터가 있다. 이는 선택한 검색과 목록에서 관측한 식별자 수다. [백업 조사](evidence/BACKUPS_REPORT_KO.md) · [범위와 중복 집계](inventory/SUMMARY.json)

Drive의 지정 백업 폴더 응답에는 161개 항목과 ZIP 139개가 있었다. 다만 `list_folder` 응답은 후속 토큰이나 명시적인 완결 신호를 제공하지 않아 폴더 목록 전체의 완결성을 보증하지 못한다. 문서 유형의 BGJET 검색은 0건이었지만 폴더 목록에는 BGJET ZIP 23개가 있었으므로, 문서 검색의 종료만으로 ZIP 전체가 빠짐없이 검색되었다고 말할 수 없다. 과거 Dropbox 검색의 별도 요청 제한은 실제 오류로 기록되어 있다. `htt_base`와 `rei_bianchi`의 과거 중단 원인은 확인되지 않았으며, 이후 커서 재개 성공이 그 원인을 증명하지는 않는다. [백업 조사](evidence/BACKUPS_REPORT_KO.md)

## REC 자료에서 확인한 연결

| 자료 | 조사 기록에서 확인한 범위 | 다음 단위와의 관계 |
|---|---|---|
| BGJET, REC PR143 | 저장된 313 query 행과 89개 서로 다른 기하학적 셀에 결속된 배경 jet, 그리고 원본과 saved-endpoint 보충분의 독립 검토가 기록되어 있다. 초기 조사 시 원 SOURCE 최종 전달은 별도 진행 상태였다. | 배경의 H와 그 미분은 유용한 입력이지만, coupled 전자 RHS 전체와 물리적 해 enclosure를 제공한다는 뜻은 아니다. |
| Native path, REC PR144 | 후속 owner 기록은 scoped 전달 완료와 중앙 backlink 및 양쪽 백업 ACK를 보고한다. 물리 coverage는 0/313으로 유지된다. | 기존 native capture와 writer 식별을 재사용한다. 전달 완료와 물리적 인증 완료는 구분한다. |
| Thermal path, REC PR145 | 저장된 affine 온도·total electron fraction 경로와 배경 reference에 대한 성분 residual을 실행한 기록을 확인했다. 초기 조사에서 독립 검토는 미실행 상태였고 full-state 물리 defect 등은 열려 있었다. | 이미 지불한 성분 residual 계산을 반복하지 않고, 이를 whole-state 물리 defect로 바꾸어 부르지 않는다. |
| QSS03, REC PR142 | 원 source에 결속된 313×313 inverse-gain 및 structured coefficient box의 계약·설계가 확인되었다. 초기 조사에서 대상 실험은 미실행이었고 R6는 HOLD였다. | 기존 matrix orientation과 계약을 보존하되, 이번 전자 point-field 단위의 완료 조건에 QSS03 전체 인증을 넣지 않는다. |
| WEIGHTED02, REC PR141 | 조건부 defect-to-tube 연결과 고정 weighted norm에 관한 기록은 있으나 실제 연속 F, 초기·모델 오차와 whole-domain defect 등의 입력이 별도로 필요하다. | 이산 recurrence residual이나 조건부 수학 결과를 실제 연속 physical tube로 승격하지 않는다. |
| LINE02, REC PR129 | frozen source adapter의 제한된 완료와 별도 history-boundary 후속 의무가 기록되어 있다. | 저장된 incoming/history와 실제 경계 조건의 설치를 구분한다. |

위 각 행의 상태는 [초기 GitHub 조사](evidence/GITHUB_REPORT_KO.md)가 기록한 시점과 읽기 범위에 한정된다. 서로 다른 PR의 단계 수를 합산하지 않는다. 특히 BGJET의 전달 상태는 그 조사 시점의 기록이며 이후의 별도 전달 결과를 이 표에서 추정하지 않는다.

Native 원 SOURCE는 두 Drive 부분 파일을 원래 순서대로 연결해 복원했다. 결과는 110,654,069 bytes이고 SHA-256은 `94b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c`로 기대값과 일치했다. ZIP을 다시 압축하지 않았다. 선택적으로 읽은 목록과 기록에는 `history.npz`, 원 HyRec source와 table, 저장된 호출 및 recurrence가 있다. `capture002`의 QSS 기록 132개에는 311개 virtual incoming과 2개 Lyman incoming 값이 포함되고, CALLS 기록에는 point 입력과 저장된 수소 도함수가 있다. 이는 point-field 입력을 조사할 수 있는 근거이며, 이 조사만으로 모든 binding과 호출 의존성이 충족되었다는 증명은 아니다. [복원 기록](evidence/NATIVE_RECOVERY_RECEIPT.json) · [ZIP 구성 목록](evidence/NATIVE_ZIP_MEMBERS.json)

## 다른 연구의 결과와 경계

REI의 후속 PR243은 관측된 상태와 별도의 조건부 밀도·온도 저장 이력을 보고한다. 이는 같은 배경의 ionic/nonthermal coupled source가 확인되었다는 의미가 아니다. 초기 조사에서 읽은 PR242의 represented caloric inverse도 recipient의 실제 caloric branch, composition 및 discrepancy certificate가 공급되기 전에는 물리 온도 인증으로 옮길 수 없다. 중앙 정본 28/88과 별도로 보고된 REI working 33/88 역시 서로 더하지 않는다. [초기 조사](evidence/GITHUB_REPORT_KO.md) · [후속 조사](SURVEY_UPDATE_KO.md)

BASS에는 native photon의 유한 구간 자료, 원자 transaction, QSS 및 frozen-reset response에 관한 병렬 결과가 있다. 후속 PR225의 조건부 유한 시간 응답은 오차 분석 방법의 후보지만 REC의 coupled F, 모델 오차, norm 또는 tube를 자동으로 공급하지 않는다. PR226의 prescribed static-lapse transport 역시 다른 상태와 clock의 문제다. BASS_CR의 조건부 atomwise support에는 실제 kernel과 physical native 입력이 여전히 별도다. [초기 조사](evidence/GITHUB_REPORT_KO.md) · [후속 조사](SURVEY_UPDATE_KO.md)

WU PR150의 후속 기록은 synthetic 조건부 affine forcing과 적분 bound를 보고하며, 실제 HD 상태·밀도·clock은 별도 입력이다. VigilODE PR95의 source-derived chemical block과 Jacobian·remainder는 고정 BASS chemical restriction에 대한 근거다. 실제 coefficient와 rate의 전체 구간, geometry 및 tau 관련 블록, accepted segment와 전체 ODE tube는 별도 의무로 남는다. 이런 결과의 가정과 시간 변수, 상태 공간, norm을 유지해야 하며 수치 상수나 완료 상태를 REC physical certificate에 그대로 이식하지 않는다. [초기 조사](evidence/GITHUB_REPORT_KO.md) · [후속 조사](SURVEY_UPDATE_KO.md)

## ELECTRON-FIELD01을 선택한 이유

기존 자료는 배경 jet, native 경로와 incoming radiation, 저장 point 상태를 각각 제공하지만, 읽은 범위에서는 원 HyRec의 actual electron point component를 독립적으로 소비할 수 있는 경계가 확인되지 않았다. 따라서 다음 단위는 원 FULL electron RHS를 명시적인 point 상태, 해당 incoming 배열, 고정 tables에 결속하여 공급하는 것으로 정했다. 이 선택은 새 whole-history integration이나 과거 capture를 다시 실행하는 대신 기존 결과를 활용해 빠진 연결을 한 단계 좁힌다. [R1 과학 계약 제안](evidence/ELECTRON_FIELD01_R1_SCIENCE_CONTRACT_KO.md)

계약의 primary 범위는 저장된 He-neutral writer에서의 수소 성분이며, 그 분기에서 total electron derivative와 같다는 조건이 붙는다. H+He 구간의 total source에는 별도 He RHS가 필요하다. point 값의 parity나 진단만으로 whole-cell field enclosure, 연속 physical defect, 초기·모델 오차, tube 또는 physical coverage가 완성되지는 않는다. 후속 조사에서 읽은 자료 중 이 범위의 source point component를 이미 대체하거나 고정된 수식을 무효화하는 근거는 관측되지 않았다. 이는 읽지 않은 모든 과거 자료에 대한 부재 증명은 아니다. [R1 계약](evidence/ELECTRON_FIELD01_R1_SCIENCE_CONTRACT_KO.md) · [후속 조사](SURVEY_UPDATE_KO.md)

## 해석과 접근의 한계

이 조사는 접근 가능한 관련 목록의 페이지를 확인하고 필요한 원문을 선택해 읽은 것이다. 모든 대화의 전체 transcript를 여는 API는 제공되지 않았으며, 모든 저장 archive의 전체 bytes나 member, 모든 branch의 과학 내용을 검사하지 않았다. Library에서 지정된 chemical report, LINE02 handoff, BG R9 delivery receipt는 전문을 읽었지만 다른 목록 항목까지 모두 읽었다는 뜻은 아니다. 저장 메타데이터의 이름·크기·시각은 실제 업로드 ACK나 원격 bytes 동일성 검증을 대체하지 않는다. 원 native SOURCE의 전체 해시 확인은 위에서 특정한 그 archive에 대한 별도 복원 검증이다. [백업 조사](evidence/BACKUPS_REPORT_KO.md) · [복원 기록](evidence/NATIVE_RECOVERY_RECEIPT.json)

이 문서에 포함한 이전 단계 상태는 각 인용 기록의 관측 시점에 속한다. 새로운 단계의 결과, 독립 검토 또는 최종 전달은 실제 기록이 생긴 뒤 그 증거로 판단한다. 이 종합 작성 자체는 새 과학 실행이나 테스트, 원본 ZIP 변경, 원격 쓰기를 수행하지 않았다.

## 보존된 근거의 범위

이 문서에서 직접 참조하는 과거 조사·복원 기록과 Git 메타데이터 목록은 `evidence/`에 원본 바이트 그대로 보존했다. 보존된 과거 보고서 내부의 다른 링크는 별도의 외부 참조이며, 그 대상 전체를 이 묶음에 재귀적으로 복사한 것은 아니다. `inventory/`는 중복 제거한 허용 필드의 메타데이터 보존본이다.
