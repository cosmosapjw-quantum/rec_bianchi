# 다음 대화 handoff — 독립 matter/radiation pilot

```text
$physmath-research-loop $exa $scispace $wolfram

REC/REI matter-radiation 연구를 이어서 수행하라. 먼저 REC draft PR117
https://github.com/cosmosapjw-quantum/rec_bianchi/pull/117
branch research/rec-rei-trajectory63-20261021의 최신 HEAD와
research/rec_rei_trajectory_reuse_20261021/{README_KO.md,REPORT_KO.md,DAG.json,DELIVERY.json,CODEX_HANDOFF_KO.md},
마지막 보존·CI 댓글을 읽어라. DELIVERY가 실제 구현 commit/tree/backup identity를 소유한다.

이번 대화에서 완료한 것:

- 최신 다른 작업의 REI collisionless z20→2 완료 237 tails 발견·재사용.
- 그중 175=7×5×5 독립 matter/radiation grid의 153 epoch를 소비.
- 63 axis support로 112 mixed 전체 저장 궤적 재구성; 새 ODE/NCP/benchmark 0.
- signed sector 진화, 비균일 5×5 끝점 map, 전체 residual, cancellation 그림 5종 완료.
- 8 focused tests PASS, 독립 agent 수학/코드/실제 175 raw 감사 PASS_SCOPED.
- max difference S 9.40e-9, Pm 8.58e-9, Pr 1.106e-8, total 1.915e-8.
- total 최대는 z7.877이며 z2 끝점 max 8.671e-9. 작다는 것은 ODE 참해 오차 인증이 아니다.
- 초기 (0,+3e-4,-3e-4)의 상쇄가 z2에서 Pi_total 3.40482544e-5로 풀린다.

관측 규약: sigma=diag(-s,-s,2s), pi_A=diag(-p_A,-p_A,2p_A).
S_F=sqrt6*s/H, P_A,F=sqrt6*(8piG/c²)*p_A/H².
signed matter+signed radiation을 합한 후 norm. half-contraction은 모두 /sqrt2.
공통 redshift z20→2에서 case별 H/proper clock으로 비교한다.
initial shear는 0 또는 양방향만. collisionless finite L8, 24×12 Gauss3,
mass fraction .1, m/T 30, ne_source=None. full cold EoR은 아직 아니다.

원 physical source PR147 3b85dedce84d37b3e165da00685a8a984950aafe.
새 wrapper SHA a7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64.
새 237의 remote publication은 최종 조회에서 미확인, PR199 8b71c13e…는 옛 checkpoint.
따라서 frozen input SHA를 유지하고 새 owner 게시가 보이면 provenance만 연결한다.
개인 대화 검색은 unavailable이어서 모든 대화 전수조사를 완료했다고 주장하지 마라.

기존 warm 729/REC U4B/HE29/long 1231 및 이번 175/237은 complete_reused.
재적분하지 마라. warm 729는 REI213 result c8e9f67a…/delivery d32cd99f…,
REC116 head 4cffa8a0…/tree 916132bd…/CI 39565947569 SUCCESS다.
warm C15 짧은 구간과 현재 collisionless long window를 섞지 마라.
원 153+90 sentinel 제안은 NOT_SUBMITTED, 나머지 486의 인증으로 쓰지 마라.

Physical HOLD/global convergence NOT_RUN/production NOT_APPROVED,
원 REC U5 HOLD/CLOSED_HOLD_NOT_RESET/REI_activation=false를 유지한다.
새로 필요한 후속 후보 최대 3개를 비교한 뒤 하나만 선택하고
source·시간 구간·closure·resolution·허용 기준을 유한 계약으로 고정하라.
상세 benchmark보다 실제 물리·코드·그림을 우선하라.
동시 Codex 존재를 veto로 쓰지 말고 실제 가용 CPU/RAM/공동 lease로 새 pending case만 나누어라.
매 단계 DAG·백업·게시 및 복사형 Codex/다음 대화 handoff를 제공하라.
```
