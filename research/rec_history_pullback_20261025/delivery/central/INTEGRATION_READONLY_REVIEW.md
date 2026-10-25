# PB01 중앙 후보 — 독립 읽기 전용 보존 검토

**판정: PASS_SCOPED_LOCAL_CENTRAL_PROJECTION_PRESERVATION. Blocking findings 0.**

후보 조립자는 `/root/ks_implementation`, 이 보존 검토자는 `/root/repo_delta_survey`다. 새 과학 판정이나 계산을 수행하지 않고 root가 수락한 PB01 객체를 정확히 재사용했다.

| 확인 항목 | 결과 |
|---|---|
| 최신 base | b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4 / tree210f15423ab8f79f691ae8a1a6cc7128b1094bff |
| 원 계획 보존 | 40 contracts / 17 edges / 7 authorities / 40 statuses / root fields / node order 동일 |
| 현재 sibling | 다른38 완전 객체 동일; 최신 CR/HE 및 HH90 관측 보존 |
| REC 관측 | PR228의18 fields 무변경 + root PB01 한 항목만 추가 =19 |
| 과거 return | 6개 원 bytes/Git blob 모두 동일 |
| PB01 standalone | root 파일5129 bytes 그대로; source S2 f9051f10… |
| Public bundle | 정확히10 paths; 모두 실제 파일 bytes 및 SHA map과 일치 |
| Tree patch | base_tree210f…; DAG1+prior6+PB3, 모두100644 blob, 보호 경로 변경 없음 |
| 전체 DAG 원 bytes | 새 두 observations의 lexical span을 메모리에서 제거하면 원428298 bytes가 정확히 복원됨 |
| 단계 구분 | 과학 S2immutable18/20, R10/C10 실제final20은 후속 S3/companion 별도 |
| ACK | 새 중앙 self commit/ACK 주장 없음. S2 remote outer712 PASS 문구는 별도 실제 local receipt로 근거 확인 |

HI strain69개 신규 파일과 나머지 현재 repository 경로는 준비된 tree patch의 base_tree 상속 대상이다. 이번 검토는 실제 원격 candidate tree가 만들어졌거나 readback이 끝났다고 주장하지 않는다. 실제 게시·readback은 root의 다음 단계다.

H5 uncalibrated/null, H6 actual trace/owner OPEN, 나머지 H7 physical composition OPEN, Physical HOLD, production NOT_APPROVED, REI_activation=false를 보존한다. 원 primary 실패와 saved-data repair 기록은 root accepted 객체 그대로다.

이 검토에서 HEAD 재조회·provider call·remote mutation·science/RHS/IVP/native/old replay·assembler·renderer는 모두0이다. 원격 S2 archive를 다시 내려받거나 inner 과학을 재검증하지 않았다. 상세 기계 판정과 파일 identity는 `INTEGRATION_READONLY_REVIEW.json`을 따른다.
