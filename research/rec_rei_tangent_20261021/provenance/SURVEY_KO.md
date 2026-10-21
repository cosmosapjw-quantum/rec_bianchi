# 다음 연구 전 원격 delta 조사

관측 종료: 2026-10-21 22:14:54 KST (13:14:54 UTC).

## 바로 적용할 결과

1. REI PR215 / BASS PR178에 실제 NCP 실행 반환이 새로 게시됐다. REI HEAD는 `926bae816ef8339137e2813cc40f1d514b763e1f`, BASS HEAD는 `215bb3e66d81a7013d2132831d210aee36234ab4`다. 실행 소스 REI `231df3ab717dbc112f63b77953f64def08e9bcb5`와 BASS `7fe0e25a28c0e48110c522378e203ffb934cc504`는 유지됐다. target compile 1회, 제공된 2-step 사례 5개, 원 gate 40/40 PASS다. 완료 729개는 전부 재사용하여 jobs=0이다. 이 반환의 판정은 `EXECUTION_COMPLETE_PENDING_SCIENTIFIC_ADJUDICATION`이며, 독립 검토는 receipt integrity 범위다. 이번 agent가 NCP를 접속하거나 재실행한 것은 아니다.

2. BASS_CR PR93 C21N은 PR147의 conserved packet 합을 직접 미분하는 `mass_shell_derivatives.py`, 초기 정확 zero-shear slice의 실제-offset jet, immutable prepared momentum geometry를 이미 구현했다. content `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9`, 문서 HEAD `0f45d0a422d79ccead565a8abaab860fcc230687`이다. 실제 source 전체와 theory 전체를 읽었다. 기존 `packet_derivatives`는 (eta,b,b_eta)에서 along-trajectory directional derivative를 계산한다. 이번에 선택한 full 40-state matrix-free JVP/VJP와 세 초기 seed tangent adapter는 여기서 보지 못했으며, 기존 chain rule을 재사용할 수 있다. 이는 조사한 코드 범위의 판단이지 모든 branch에 대한 부재 증명은 아니다.

3. HH PR132 PHYS77은 whole-cell source enclosure를 진행 중이다. HEAD `91eeb12012b5fdcdbd2423ab28a72ecf4ca7cbcc`, parent `ec28299fe7e81aab184b93aff787cb00a185dd2e`다. 현 게시물은 S0 계약과 intake 11파일이다. 8-state finite L8 owner의 exact binary64 coefficient export, outward RHS/source box, affine predictor first-exit inclusion이 계약 대상이다. 이 단위와 선택한 PR147 40-state response adapter를 분리한다.

4. 지난 survey snapshot 이후의 REI199 D8 원 owner 게시도 회수했다. 결과 `a3cb0606341688affb6aea29990e960e53188d32`, HEAD `eb8042b729051f4700bd5d88d6781c4620009bcb`이며 기존 네 개 저장 bracket이다. 새 ODE는 0이다. Case c `1c39be4e...`는 원래 `FAILED_WORKER_EXIT/124`였고 이후 data-only recovered raw다. 이것을 원 solver success로 바꾸지 않는다. HH131와 HE83의 D8·전달도 같은 완료물을 재사용한다.

## 조사 범위

REC, REI, HH, BASS, BASS_CR, BASS_HE 여섯 저장소에서 cutoff 2026-10-21T12:47:45Z의 PR 검색과 각각 최근 updated PR 5개 목록을 대조했다. 지정된 REC116/117, REI213/215/216, HH130/131/132, BASS178, CR93, HE83의 head와 관련 원문을 확인했다. 최근 목록으로 찾은 cutoff 이전이지만 이전 snapshot 이후의 변경도 보존했다. 과거 823-ref 조사는 재사용했으며 모든 un-PR branch, 비공개 대화, 모든 파일을 새로 조사하지 않았다. 대화·backup provider 조사는 별도 agent가 맡았다. 원격 쓰기와 과학 실행은 0이다.

## 보존 파일

- `UPSTREAM_DELTA.json`: pins, query 범위, 새 실행·완료·진행 중 구분.
- `evidence/REI215_NCP_TARGET_EXECUTION.json`, `REI215_NCP_CASE_GATE_SUMMARY.json`, `REI215_NCP_INDEPENDENT_REVIEW.json`: 원격 root/evidence의 실제 새 반환 전체. Git blob 일치.
- `evidence/CR93_mass_shell_derivatives.py`: 8,843 bytes, SHA256 `db108994e96f268e074778a3e763dddc8ca72799541b670aca11bbc728d6ef7c`, Git blob `0d471b04fcbfa28786cda1b2bae1304c6fc617e5` 일치.
- `evidence/CR93_MASS_SHELL_DERIVATION_KO.md`: 원 전체 이론과 source 대응.
- `evidence/CR93_REUSE_PROVENANCE.json`: provenance 및 라이선스 조사 범위. CR root listing 및 C21N content manifest에서 LICENSE/COPYING/NOTICE는 찾지 못했다. 외부 open-source license를 추정하지 않았다. 사용자가 소유한 명명 저장소 사이의 재사용 요청에 따라 attribution을 보존하며, 별도로 vendor하는 PR147 파일의 원 LICENSE는 유지해야 한다.
- `evidence/HH132_CONTRACT.json`: 진행 중 단위의 정확한 경계.
- `evidence/PR_METADATA_RECEIPTS.json`, 두 `COMPARE.json`: 해당 관측의 원격 메타데이터와 변경 목록.
