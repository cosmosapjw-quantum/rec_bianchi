# Codex handoff — REC_TRAJECTORY63_20261021

아래를 독립 Codex 작업의 시작 context로 복사한다. 실제 구현 commit/tree와 최종 backup ACK는 같은 경로의 `DELIVERY.json` 및 PR117 마지막 보존 댓글을 먼저 읽는다. 이 파일은 완료 자료를 다시 돌리라는 실행 요청이 아니다.

```text
$physmath-research-loop $exa $scispace $wolfram

REC/REI 독립 matter/radiation 연구를 이어받아라.
Repo: cosmosapjw-quantum/rec_bianchi
Draft PR117: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/117
Branch: research/rec-rei-trajectory63-20261021
Science commit: 6f68ad9326d4f6529b9fcde2d35c31631b43d958
Science tree: 7e96a7d329dbea60096fc3f7ef6a53d74020113e
Research path: research/rec_rei_trajectory_reuse_20261021/
먼저 README_KO.md, REPORT_KO.md, DAG.json, DELIVERY.json,
provenance/SOURCE_LOCK.json, FINAL_UPSTREAM_PUBLICATION_CHECK.json,
evidence/C9_INDEPENDENT_REVIEW.json과 마지막 PR 보존/CI 댓글을 읽어라.

완료된 새 consumer: 175 nominal=63 axis support+112 mixed, 153 epochs, z20→2.
Fhat=F(S,m,0)+F(S,0,r)-F(S,0,0), signed F=(sqrt6*s/H,Pm,Pr).
max stored history discrepancy:
S 9.40056251721652e-9, Pm 8.582762394605706e-9,
Pr 1.1057774095034681e-8, total 1.9152545950075223e-8.
total max z7.87707155302417, endpoint max 8.671093121602252e-9.
총 norm은 abs(Pm+Pr); abs(Pm)+abs(Pr)는 상계다.
full Frobenius이고 half는 각 좌표를 sqrt2로 나눈다.
kappa_t=8piG/c²; H,s[s^-1], stress[J/m³].
공통 x=ln(a/a_ref), a_ref=1/21로 비교하며 같은 proper time 비교가 아니다.
그림 5종 PNG/PDF 완료; 8 focused tests PASS; independent C9 PASS_SCOPED.
Reducer SHA 03596192ccd5602187549fb52734870b343aea6e1ca7f13d0df8d7e7b7c1c77a.
실행된 Test SHA 639abdff416becf8978fc0f013c211d8a1bf1fb6fd2346a1da526e643f2b44d7.
EOF 빈 줄1개만 정리한 현재 Test SHA 5a9d6a095e24b64bd6b8a69744da628c1ad3e4cbfecad8ab129075efe0919fe7; body/AST 동일.
NPZ SHA 239595a3313a68e0125ec7b333b8d515c3fd5d6d8ec115fbef2496d3b18428b9.
최종 guard 변경 후 9 arrays/SUMMARY exact same. 과거 PR116 C6 NOT_RUN은 그대로 둔다.

현재 input: 최종 archive의 intake/unified_z2_20261021.
175 nominal+3 component guards 보존, analysis는 175만.
physical source REI PR147 3b85dedce84d37b3e165da00685a8a984950aafe.
wrapper SHA a7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64.
z2 manifest SHA 4f7e599ad9f082be59cbe2203a8b55b7bd9cb21fec9fde55a41afe53b9444853.
snapshot manifest SHA d7b147aa0293646b068e754a9bf03f2b8e47e3544b405a1ad5bfce366b34143e.
전체 upstream 237 tails는 complete_reused. 일부 subset만 저장했으므로 원 MANIFEST의 237을 178로 고치지 마라.
최종 조회 PR199 head 8b71c13e23202edfce1ee67fb2da552fefb9a583은 옛 checkpoint다.
새 237 원격 게시 identity는 미확인: local SHA 결속을 유지하고 owner 최신 게시가 있으면 연결만 추가한다.

재실행 금지: 완료 warm 729, REC U4B, HE29, long 1231, unified 175/237.
REC116 head 4cffa8a0abdb104a40cac17cfc65593bec909fb3/tree 916132bd155140a9589c519a56ff2e80358e3434.
REC116 CI 39565947569 SUCCESS; 역사적 in_progress를 최신으로 읽지 마라.
REI213 result c8e9f67aa031ffb33a9b0347bdea61dbb01fb746/delivery d32cd99fa19c65aa1ca63dbc8aab8741834270e8.
warm C15 a=.1999→.2, gas 12000K와 이번 collisionless L8 ne_source=None의 계수/행을 섞지 마라.
old 153 axis+90 sentinel 243 설계는 NOT_SUBMITTED. 반례 때문에 미검사 486 인증 불가.

이번 새 ODE/NCP/benchmark 0, 동일 case pending 0. performance NOT_MEASURED.
Science archive REC_REI_TRAJECTORY63_SCIENCE_6f68ad93_20261021.zip,31,476,566 bytes,
SHA828eb4667a87b7c23674686daa5b94c260cf0adb4c86851b853de7bf059c6c0f,
Dropbox id:BSpOijBcT10AAAAAAD_gPA, 전체-byte readback PASS.
Stage2 CI의4파일EOF문제는내용/AST변경없이수정;최종HEAD/CI는마지막PR댓글과closingreceipt를읽어라.
Drive미확인상태를성공으로바꾸지마라.

Physical HOLD, global convergence NOT_RUN, production NOT_APPROVED,
REC U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI_activation=false 유지.
후속은 최신 근거 후보 최대 3개에서 하나만 고르고 유한 source/구간/closure/resolution/허용 기준을 고정한다.
다른 세션 존재는 전역 veto가 아니다. 새 미완료 case만 실제 CPU/RAM/lease에 맞춰
기존 pending-only/cooperative executor로 나누고 inner BLAS 1, peer allocation/debit/실패 이력을 보존한다.
현재 Desktop Commander monthly usage paused 반환은 SERVICE_ERROR다; 동일 실패를 반복 호출하지 마라.
각 단계 실행 증거·DAG·create-only backup·draft publication을 남기고 merge/force/reset하지 마라.
```

## 필요할 때만 수행하는 재현 명령

```bash
python rec_bianchi/research/rec_rei_trajectory_reuse_20261021/code/reduce_trajectories.py \
  --snapshot intake/unified_z2_20261021 \
  --output /tmp/rec_trajectory63_new_output
python -m unittest discover \
  -s rec_bianchi/research/rec_rei_trajectory_reuse_20261021/code \
  -p test_trajectory_reuse.py -v
```

원 output 삭제/덮어쓰기 대신 새 경로를 쓴다. plotting은 `evidence/PLOT_REVIEW.json`의 실제 명령을 따른다. GitHub의 current head와 source hash를 확인한 뒤 변경한다.
