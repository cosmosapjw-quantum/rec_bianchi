# PB01 중앙 실제 게시 — 원격 보존 확인

**PASS_ACTUAL_REMOTE_10_PATHS_AND_PINNED_BASE_PRESERVATION. Blocking findings 0.**

- 실제 commit: `219fe60a3f069dda26e109f6e0cd1fd339c83701`
- 실제 tree: `8188397a0e94faac70c4352b14cc807b3e384843`
- 새 branch: `research/orchestration-rec-history-pullback-20261025`
- [PR229](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/229): open/draft, HEAD가 실제 commit과 일치
- 직접 parent: `b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4`; 캡처 base tree `210f15423ab8f79f691ae8a1a6cc7128b1094bff`

## 승인 후보와 실제 원격 tree 대조

Actual compare는 정확히 1 commit, 10 paths(DAG 수정1 + observations 추가9)다. 10개 모두 승인한 local 파일의 Git blob·size 및100644 mode와 실제 tree가 일치한다. Unexpected/deleted paths는0이다.

| 실제 path 범위 | 결과 |
|---|---|
| DAG.json | blob cfa0d62a122b3a13bb5bf1a59c210ed6057a18f6 /472199 bytes; 독립 검토한 후보와 동일 |
| 기존 THERMO/KS return6 | 원 Git blob 그대로 게시됨 |
| 새 PB01 observation/status/guardrail3 | 승인 local file의 blob·size·mode와 모두 일치 |
| AGENTS.md | 429a5a13ee75b1222bc50627f8d5973d01dd21c4 /9351 bytes; base와 동일 |
| 고정 REI handoff | b7282c1d88dbb7622853c697d5787d43b12fe8ef /19988 bytes; base와 동일 |
| HI strain69 및 해당 전체 subtree | base/actual의 rei_source_pair_binding tree가3d04e9166aa34363246d63cb350b54a76d18c325로 동일 |

Root→research→orchestration→assembly/observations의 완결된 nonrecursive tree를 대조했다. 각 단계에서 허용 경로를 제외한 모든 entry의 mode/type/SHA가 동일하다. 이 Merkle tree 증명으로 승인10개 외의 repository 내용과 최신 HI69 상속을 확인했다. HI69의 과학 payload 본문을 개별 재검증하거나 계산하지 않았다.

실제 DAG blob이 독립 심사를 통과한 local 후보와 같으므로 다른38개 최신 CR/HE/HH 객체, 원40contracts/17edges/7authorities/40statuses/root fields, donor18+exact PB01 보존 판정이 실제 게시된 DAG에 결속된다. 과학 S2immutable18/20 기록과 후속 S3/companion 최종 전달 구분도 그대로다.

## 조회 범위와 종료

최초 recursive base/actual tree GET 두 건은 connector Transport closed로 실패했다. 그 원문을 보존하고 큰 요청을 반복하지 않은 채 작은 nonrecursive tree9개로 필요한 모든 경로를 확인했다. 전체 provider GET15회 중 성공13/해당 전송 실패2이며, 열린 보존 gate는 없다.

Canonical HEAD를 다시 갱신하지 않았고, 전체 repo/branch census·CI조회·provider mutation·새 과학/RHS/IVP/native/old replay·assembler·renderer는 모두0이다. CI는 root의 별도 확인 대상이다. 모든 요청 gate를 만족하여 추가 탐색을 중단한다. 상세 source와 파일별 identity는 `ACTUAL_REMOTE_READBACK.json`, 원 tool response는 `ACTUAL_REMOTE_RAW_READS.json`에 있다.
