# BASS_HE Codex 시작 계약

목표: 기존 B3 외부 rate/count API를 활용하여 원자 입력 공급 역할을 닫고, rei_bianchi가 실제 연구를 진행하도록 한다. 원자 미완료 과제를 scientific PASS로 바꾸지 않는다. 기존 branch `research/shared-c64-crossrepo-20260928`에서 진행하고 새 branch를 만들지 않는다.

처음 읽을 파일은 이 파일, `TASKS.json`, `REPO_SNAPSHOT.json`, `PREWORK_KO.md`의 1–4절뿐이다. legacy 물리 연구를 호출할 때만 `LEGACY_LANE.json`과 지정 원본을 읽는다. 원자 문헌 전수검색이나 원격 전체 archive redownload를 반복하지 않는다.

1. 실제 현재 HEAD/작업트리/AGENTS를 확인한다. `REPO_SNAPSHOT.json`의 observed commit은 2026-10-04 읽기 시점 pin이며 이번 게시 commit은 최종 publication receipt를 따른다. branch가 전진했다면 관련 paths 차이만 확인하고 이 패키지를 예전 HEAD로 reset하지 않는다.
2. `HE-F1`은 2026-10-04 구현·변경영역 검증 완료다. 결과는 `runs/HE-F1_20261004/RETURN.json`이다. 다음은 `HE-F2`의 실제 `REI_SCOPE_LOCK`·`REI_PROVIDER_CONTRACT` 확인이다. 이후 문장의 HE-F1 구현 절차는 완료 이력으로 보존한다: B3의 `registry.py`, `api.py`, `_rate.py`, `_io.py`, contract와 focused tests를 읽는다. 기존 GM25 source core를 고치지 않고 KF96 별도 source ID를 추가하는 최소 변경을 준비한다. 계약은 PR 단위로 작성되어 있으며 실행 전 source identity·domain·null fields를 유지한다.
3. 기존 GM25(`1.70e-13 cm3/s`,200–10000K)와 KF96(`1e-14`,표1000–1e7K) 중 자동 선택은 금지다. paired sensitivity는 공통1000–10000K에서만 두 근거의 직접 비교로 부른다. 더 넓은 모델을 요청받으면 domain 이탈을 정직하게 반환하고 임의 clamp하지 않는다.
4. density, Bianchi geometry, effective opacity를 원자 API에 넣지 않는다. 기존 T4 exact registry/source ownership와 새 rei homogeneous/effective-opacity 구분을 연결한다. 열·recoil·photonenergy·spectrum이 null이면 숫자0으로 승격하지 않는다.
5. 변경영역 검증만 시행한다. 원 B5C2 59개 또는 기존 76개 전체 suite를 문서 이동 때문에 반복하지 않는다. GM25 바이트 identity와 필요한 focused parity, KF96 boundary/unit/rejection, duplicate reaction, packet compatibility가 검증 대상이다.
6. `HE-F2`부터는 rei_bianchi의 explicit provider/closure 계약을 소비한다. photon closure 미결정이면 exact source가 없는 사실을 보고하고 서로 다른 연구문제를 마구 추가하지 않는다. source family가 연결되면 같은 source를 FLRW/Bianchi에 함께 적용하는 한 번의 감도 campaign을 REI-F09에 위임한다. HE-F3는 이 결과의 검토·수락만 수행하고 별도 campaign을 실행하지 않는다. HE-F2 미완료는 optional F09만 대기시키며 REI-F08 baseline 진행을 막지 않는다.
7. 반환은 `../../common/RETURN_CONTRACT.schema.json`의 required envelope인 `task_id,state,input_identity,changed_paths,commands,artifacts,claim,next_task`를 따른다. state는 completed/partial/blocked이며 claim은 basis/ceiling을 포함한다. 각 command는 command/exit_code/evidence_path를 담는다. source_ids/tests/claims_allowed/claims_forbidden/unresolved는 부가필드다. actual run이 없으면 tests를 null/NOT_RUN으로 쓴다. private archive·copyrighted paper·tokens를 public Git에 넣지 않는다.

이번 사용자 요청은 선행 연구·계획·PR/DAG·백업 게시다. 이 패키지는 실행 승인을 가장한 scientific admission token이 아니다. 본 요청으로 작성하지 않은 후속 제품 구현과 physical runtime은 해당 task의 explicit input/acceptance contract를 만족시킨 뒤 수행한다. 이미 존재하는 source/assumptions를 바꾸는 문제는 근거와 실패를 보존하여 연구 스레드에 반환한다.

재개 키: fastest=`HE-F2`; thermal precision=`HE-L1`; fast-ion population=`HE-L2`; coherent/continuum=`HE-L3`. 후자의 세 키는 LEGACY_LANE.json의 trigger에 의해 선택하며 서로를 무조건 선행조건으로 만들지 않는다.

## 2026-10-04 HE-F2B live-sync update

매 재개 시 `CURRENT_FASTEST_STATE.json`과 `REPO_SYNC_POLICY.json`을 먼저 읽는다.
HE-F2A 전달물은완료, HE-F2B는실제REI-F00의RCT제외를결속했다. 현재baseline은BASS_HE source를필요로하지않는다.
현재scope가없다는옛관측은재사용하지않는다. RCT포함의실제수락은여전히미완료이고새owner opt-in/provider/closure가필요하다.
source선택·실제감도·legacy원자연구를자동재개하지않는다. 입력변경이없으면같은검증을반복하지않는다.
시작·게시직전·게시직후에실제Git HEAD를조회하고변경경로만조정한다. 백그라운드worker는없다.
현재 실행상태는 `CURRENT_FASTEST_STATE.json`이 우선하며, 기존 `TASKS.json`의 연구 의존성과 acceptance는 삭제하지 않는다.
최신 Codex 동기화 결과는 `CURRENT_FASTEST_STATE.json`의 `latest_sync_return`과 [스레드 전달 기록](execution/CHATGPT_SYNC_KO.md)을 따른다. 과거 execution intake의 missing-F00/F01 관측 또는 초기 선택기의 READY를 현재 RCT 수락으로 사용하지 않는다.
