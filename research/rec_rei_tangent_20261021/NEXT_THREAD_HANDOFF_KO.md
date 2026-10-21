# 다음 대화 스레드 handoff

아래 내용을 새 대화에 그대로 붙여넣는다. 게시 commit·tree·CI·archive는
REC PR118 최종 보존 댓글의 실제 반환값을 먼저 읽고 고정한다.

```text
$physmath-research-loop $exa $scispace $wolfram

REC/REI matter-radiation 분리 연구를 REC PR118부터 이어서 수행하라.
가장 먼저 PR118 최종 보존·CI 댓글과 원격 HEAD를 읽고,
REC116/117, REI199/213/215/216, BASS178, BASS_CR93, HH130/132 및
관련 백업에 새 실행 반환이 생겼는지 delta 조사하라.
다른 대화 검색은 앞 turn에서 Personal Context unavailable였다.
전체 대화 조사를 완료했다고 간주하지 마라.

PR118:
https://github.com/cosmosapjw-quantum/rec_bianchi/pull/118
branch research/rec-rei-tangent-20261021
project research/rec_rei_tangent_20261021/
stacked base REC117 research/rec-rei-trajectory63-20261021
최종 commit/tree/CI/archive는 마지막 보존 receipt의 값을 사용하라.

필수 읽기:
README_KO.md, THEORY_KO.md, CONTRACT_KO.md, DAG.json,
results/SUMMARY.json,
results/verification_v1/VERIFICATION.json,
results/wiring_v1/TINY_WIRING.json,
evidence/C9_PHYSICS_CODE_REVIEW.json,
evidence/C9_AUGMENTED_REVIEW.json,
evidence/C9_DISPATCH_OPERATIONAL_AUDIT.json,
evidence/C9_PLOT_ADAPTER_REVIEW.json,
evidence/PLOT_VISUAL_REVIEW.json,
CODEX_HANDOFF_KO.md 및 마지막 게시/백업 receipt.

새 완료 단위는 pinned PR147 40-state collisionless RHS의
matrix-free analytic JVP/VJP와 세 초기 signed seed tangent다.
Z'=F_y Z+F_A A_theta, Z(0)=y0_theta.
Matter 분포 amplitude 직접항과 N(A)/Nref(A) 정규화 미분을 유지한다.
L8, fm=.1, m/Tref30, 24x12 Gauss3, ne=None, viscosity0.
Source3b85dedce84d37b3e165da00685a8a984950aafe.
부호를 가진 matter/radiation을 따로 보존한 뒤 더하고 norm을 취한다.
kappa_t=8piG/c², Frobenius와half-contraction을구별한다.
S=0의미분은signed smooth extension; abs의0Jacobian은주장하지않는다.

실제 완료:
저장40case x5epoch=200state,600방향,19gate/8unit PASS.
maxscaled RHS2.1684e-19,stateJVP4.9455e-11,
directA3.6692e-12,observableJVP7.2149e-12.
VJPduality 최대절대1.5099e-14.
새 ODE는x0→1e-4,parent1+augmented1=2회뿐이다.
13wiring gatesPASS,parentstate차0,실제z20→19.9979001049965.
새 tangent NCP0,benchmark0.
운영20checks는synthetic worker/자원/PID 검증이지NCP실측이아니다.
새 그림2장은저장state의localpartials와tinyresponse를보여준다.

NCP는새interior3case의fullz20→2/153node/160state 실행만READY_NOT_SUBMITTED다.
interior_1=(.002,.00007,-.0002)
interior_2=(.006,-.00007,.0002)
interior_3=(.015,.0002,-.0007)
rtol3e-11,atol3e-13,scaledtangent[.1,.0003,.001],
percase120s cooperative RHS deadline/controller900s.
다른세션존재는veto가아니다. 실제가용CPU/RAM+공동예약내에서배분한다.
maxworkers63은상한이고pending3개이므로최대동시3이다.
기존실패/claim/attempt/CPUdebit/peerlease를보존한다.
완료결과는identity+NPZhash일치때complete_reused로연결한다.
NO_PENDING_WORK를모든case성공으로해석하지마라.

warm729,REC175,unified237,HH1231prefix/tail,REC U4B,HE29,D8 재실행금지.
기존parameter sweep과z20→2norm그림은REC117에있다.
PR116warmC15a.1999→.2gas12000K와PR147collisionless결과를섞지마라.
REI215의40/40NCPnativegates는별도warmowner반환이며
EXECUTION_COMPLETE_PENDING_SCIENTIFIC_ADJUDICATION이다.
D8 casec1c39be4e...의FAILED_WORKER_EXIT124/data-onlyrecovery를바꾸지마라.

새NCP반환이있으면먼저재사용하고결과schema:
outerCOMPLETE, nestedintegrationCOMPLETED, tangent.npz/npz_sha256,
RUN_MANIFESTidentity,153canonicalgrid와양끝점을검증한다.
그뒤actualsignedO및3seedresponse를plot_tangent.py --ncp-output으로그려라.
새반환이없고NCP실행환경이가능하면CODEX_HANDOFF의유한3case계약을실행하라.
새후속연구는최대3후보비교후하나만선택하라.
상세benchmark대신물리/코드/그림산출물에집중하고매단계backup/publication/DAG를기록하라.

Physical HOLD,global convergence NOT_RUN,production NOT_APPROVED,
REC U5 HOLD_9_FAIL/HOLD_8_FAIL,CLOSED_HOLD_NOT_RESET,REI_activation=false유지.
기존REC116의독립감사NOT_RUN이력은이번PR118의독립검토와별개다.
```
