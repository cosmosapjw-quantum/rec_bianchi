# REC-DONOR-03 문서 연구 checkpoint

상태: `DRAFT_FOR_OWNER_REVIEW`

## 기준과 산출물

- 고정 부모: `aeb01d369436f2d0eda2c946e9c650e54ae06fca`.
- 부모 tree: `afa41c177aa27d73ef772a7d20522d3ef2ef7835`.
- 부모 작업: REC Draft PR #63, 수치 deposition 어댑터 완료.
- 새 branch: `research/rec-donor03-physical-input-authority-contract-20260905-r1`.
- 허용 변경: 이 폴더의 `CONTRACT_DRAFT_KO.md`, `SOURCE_TRACE.json`, `CHECKPOINT_KO.md` 세 문서만.
- 금지: 생산 코드, 테스트, 기존 evidence, 원본 archive, workflow, 물리 map, 다른 저장소 변경.

포함 commit의 SHA를 자기 내용 안에 넣지 않는다. 최종 commit/tree/PR와 Atlassian 댓글 ID는 게시 후 PR 본문 또는 댓글에서 확인한다.

## 이번에 한 일

현재 PR 검색에서 PR #63 이후 같은 구현 또는 입력 계약의 후속 PR이 없는 것을 확인했다. 실제 기준 소스에서 원본 표 reader, real/virtual 결합, 기존 paired packet 식, 원본 경계 flux, 원자 유효 rate, COM 수치 계산기의 역할을 구분했다. 원본 C/header 발췌의 파일 blob과 의미를 현재 코드의 기호에 연결했다.

핵심 결과는 다음과 같다.

1. `A2s/A3s3d/A4s4d`의 구간 적분, 합산 축퇴도, 열적 감소를 packet normalization과 중복 적용하면 안 된다.
2. 이미 `PhysicalTwoPhotonRamanBin`에 추적 광자 paired 식이 존재한다. 그 코드 존재와 실제 입력 인증의 부재를 구분한다. 새로 재구현할 대상이 아니다.
3. 원본 virtual 상태, dimensionless logarithmic mode factor, 실제 target `mu_i`는 서로 다른 양이다. 원본 중심에서 물리 셀이나 map을 추론할 수 없다는 기존 결과를 재사용했다.
4. 한 번 센 원자 사건의 광자 다리 장부를 조건부로 정리했다. 원본 적분 표가 그 사건률에 대응하는지는 별도 근거가 필요하다.
5. 이미 occupation-rate로 변환된 1광자 source와 packet source, signed distortion jump와 total occupation을 구분했다.
6. 원본 사실을 복원해야 하는 항목과 책임자가 모델 범위를 결정할 항목을 D1–D3로 나눴다. 어느 물리 map이나 채널 범위도 새로 승인하지 않았다.

## 근거와 검증 상태

- GitHub에서 exact ref의 파일·blob 메타데이터와 명시된 소스 부분을 읽었다.
- 원본 ZIP의 등록 SHA-256, Git blob과 size는 확인했지만 이번에 ZIP을 새로 압축 해제하거나 재해시하지 못했다. 원본 전체 C와 표를 읽었다는 주장은 하지 않는다.
- 직접 대수로 열평형 소거, 사건별 광자 수·에너지 장부, 조건부 물리 셀 measure를 정리했다. 새 symbolic/numerical execution은 없다.
- container와 Python은 각 실제 호출에서 process 시작 전 ClientError로 종료됐다. 같은 실패를 추가 반복하지 않았다. 사용자 Dropbox checkout을 읽거나 수정하지 않았다.
- WolframContext는 MCP SSE HTTP404로 kernel 결과 전에 실패했다. Wolfram·SymPy·mpmath의 새 PASS는 없다.
- SciSpace에서 관련 논문을 검색하고 HyRec 및 Hirata 원 논문의 공개 초록을 읽었다. 문헌의 정확한 식·표·다중도에 대한 전문 대조로 주장하지 않는다.
- 새로운 테스트, 전체 repository verifier, 수치 어댑터 재실행, 그림 생성·시각 검토는 수행하지 않았다. 이 문서 연구에는 새 수치 결과가 없다.
- JSON 내용은 작성 단계에서 구조를 검토했지만 parser를 실제 실행하지 못했다. 별도 validator PASS는 주장하지 않는다.

## 두 관점 감사

수학·물리 검토: packet과 사건, 추적 광자와 동반 광자, eV/CGS와 SI, 고정 map과 moving map, 에너지 중심과 유한 셀 measure를 구분했다. 조건부 식에는 가정을 붙였고 원본 사실로 승격하지 않았다. 표의 이미 적분된 계수와 스펙트럼 대칭성에 근거 없는 추가 인자를 넣지 않았다.

코드 검토: 각 주장을 실제 파일 기호와 blob에 연결했다. 원본을 재구성하는 C 검사 도구는 원본 C 그 자체가 아니라고 표시했다. 현재 수치 어댑터를 수정하지 않고, 실제 물리 배열을 공급하는 앞 단계의 책임만 기술했다. 두 관점 모두 같은 작성자의 검토이며 독립 재심사로 표현하지 않는다.

미결정 항목은 D1 원본 channel/multiplicity와 첫 대상, D2 target measure/map 생성 규칙, D3 원본 감소 계통과 독립 paired source의 중복 방지다. 이 항목들은 새로운 자동 admission gate 구현이 아니라 책임자 검토 목록이다.

## 이전 완료 상태의 보존

PR #63의 125개 최상위 테스트와 9개 하위 검사, 두 프로세스 identity, Fraction 비교, 변조 검사와 렌더링 검토는 과거 실제 실행 결과로 유지한다. 이번 문서의 검증 수에 다시 더하지 않는다. 과거 실행 source commit과 이후 결과 문서 commit도 구별한다.

일반 repository CI에는 보존된 committed-range whitespace 실패가 남아 있다. 이번에는 해당 CI를 재실행하거나 원인을 새로 검증하지 않았고, 기존 실패를 이 문서의 성공이나 물리 실패로 재분류하지 않는다. 과거 evidence bytes를 고치지 않는다.

## 게시와 동기화 범위

로컬 실행 경로와 별개로 GitHub connector를 이용해 고정 부모에 세 문서만 더하는 새 child를 게시한다. 기존 PR #63 branch에는 변경하지 않는다. 실제 ref 갱신과 Draft PR 및 원격 readback 결과는 최종 PR 기록에서 구분한다.

Atlassian은 `BASS-19`, `BASS-26`, FED-02 page `27492353`에 새 문서와 원본 추적 결과만 append한다. 상태, 공식 dependency, 다른 저장소 snapshot, provider와 ready/merge는 바꾸지 않는다. 게시 성공 여부는 실제 응답으로만 판정한다.

## 다음 단일 작업

D1–D3를 대상으로 책임자가 계약 초안을 검토한다. 첫 대상으로 2s 채널 하나를 제한적으로 다루는 방안은 제안일 뿐이며 아직 채택되지 않았다. 원본 적분 영역·다중도는 근거로 복원해야 하고 임의 승인이 대신할 수 없다. 이후 승인된 좁은 범위에서 필요한 원본 member 검증과 물리 입력 구성을 진행한다.

현재 유지:

```text
physical_source_authenticated = false
provider_admitted = false
NO_PASS_REC_PHYSICAL_SPLIT
```

이 문서 checkpoint에서 종료한다. 새로운 production source, map, provider 또는 coupled evolution으로 자동 진행하지 않는다.
