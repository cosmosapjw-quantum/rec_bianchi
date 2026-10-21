# REC → REI: z20→2 저장 궤적의 축 응답 재사용

2026-10-21 Asia/Seoul. 단위: REC_TRAJECTORY63_20261021.

## 선택과 완료 조건

기존 warm C15 729-case, REC U4B, HE29, collisionless z20→4를 재적분하지 않는다.
최신 공유 원본에서 완료된 REI Lane B의 237개 z20→2 궤적이 확인됐다.
그 중 독립 성분의 완전한 175개 nominal grid만으로 축 응답의 전 시점 사후 비교를 수행한다.
이 단위는 ODE를 호출하지 않는 읽기 전용 소비자다. 원본 owner/source/closure를 변경하지 않는다.

후속 후보는 다음 세 개를 비교했다.

| 후보 | 최신 근거 | 선택 |
|---|---|---|
| 저장 z4 상태에서 z2까지 연장 | 다른 REI 작업에서 237개 이미 완료 | complete_reused; 중복 실행 0 |
| 새 z20→2 궤적에 축 재구성 적용 | 기존 REC116은 warm endpoint만 비교; 새 전체 궤적 비교는 없음 | 선택 |
| HH128 exact 8→3 radiation 감소식 도입 | 이미 구현됨; 이번 소비자에는 적분이 필요 없음 | 해당 결과 재사용, 별도 solver 변경 안 함 |

완료 기준: 입력·source·receipt identity 고정, 정확한 175-grid/63-support/112-held-out 구분,
공통 153개 x 시점 확인, signed 성분 재구성, 실제 전 궤적/끝점 residual 산출,
독립 수학·코드 검토와 필요한 최소 검증, 실제 그림 직접 확인, 단계별 게시·백업·인계.

## 물리와 관측량

metric (-,+,+,+), non-tilted LRS Bianchi I. a_perp=a exp(-b), a_parallel=a exp(2b), s=db/dt.
normal orthonormal frame에서 sigma=diag(-s,-s,2s), pi_A=diag(-p_A,-p_A,2p_A).
여기 p_A=Delta_A/3이고 Delta_A=P_parallel-P_perp이다.
H,s는 s^-1, stress coefficient p_A는 J/m^3, kappa_t=8 pi G/c^2이다.

S_F=sqrt(6) s/H, P_A,F=sqrt(6) kappa_t p_A/H^2.
Sigma_F=abs(S_F), Pi_A,F=abs(P_A,F). Half-contraction 좌표는 모두 sqrt(2)로 나눈다.
총 signed stress는 P_m,F+P_r,F이며 총 norm은 그 합의 절댓값이다.
저장 Sigma_F는 magnitude이므로 재구성에서는 반드시 sqrt(6)*s/H를 사용한다.

Matter=massive canonical Vlasov + zero-stress cold dust; radiation=gamma+massless nu.
massive fraction .1, mass/T_ref=30, initial positive P2 family, gamma/nu common angular seed.
nominal L8, radial24×angular12, subcell Gauss3, collisionless ne_source=None.
원 physical source: REI PR147 commit 3b85dedce84d37b3e165da00685a8a984950aafe.
이 scope는 cold H/He/UV reionization history를 포함하지 않는다.

## 유한 입력 격자와 시간

- S_F,i: 0, .0003, .001, .003, .01, .03, .1. 초기 shear 방향은 양 또는 0이다.
- P_m,F,i: -.0003, -.0001, 0, .0001, .0003.
- P_r,F,i: -.001, -.0003, 0, .0003, .001.
- 175 nominal = 63 axes + 112 mixed. 56 additional nominal와 6 guards는 이 비교에서 제외한다.
- 축 분류는 요청된 config 좌표를 사용한다. 실현된 초기 floating-point 값을 0으로 clip하지 않는다.
- x=ln(a/a_ref), a_ref=1/21. 공통 153개 저장 epoch: 121 prefix + 32 new tail.
- x[120]=ln(21/5), x[-1]=ln7. zbar=1/a-1은 20→2.
- 비교는 같은 x/zbar에서 수행한다. case별 elapsed proper time은 다르며 등시간 합성을 하지 않는다.

## 계산식과 해석

고정 S_i와 저장 epoch x에 대해 각 signed 관측량 F에

Fhat(x;S_i,m,r)=F(x;S_i,m,0)+F(x;S_i,0,r)-F(x;S_i,0,0)

를 적용한다. 63개 축만 prediction 입력으로 사용하고 112개 혼합 궤적은 비교에만 사용한다.
fit, 보간, 새 계수, 새 IVP는 없다. 총량은 예측된 두 signed 성분을 합한 다음 norm을 취한다.

연속 finite-closure 응답이 m,r에 대해 C2이면
R=F-Fhat=int_0^m int_0^r partial_m partial_r F(x;S_i,u,v) dv du.
저장값의 residual에는 exact response interaction과 네 저장 궤적의 수치/초기보정 차이가 함께 들어간다.
이번 실제 비교는 112×153 저장점의 사후 discrepancy다. 전역 derivative bound, ODE error bound,
미계산 parameter/epoch 인증, prospective solver 교체 허용 기준을 새로 주장하지 않는다.
norm 차이는 reverse triangle inequality로 signed residual에 지배되며
abs(abs(Ptot)-abs(Phat_tot)) <= abs(R_m+R_r) <= abs(R_m)+abs(R_r).

## 구현·자원·보존

원본 read-only snapshot은 파일 크기/stat/hash 전후 일치를 확인한다.
postprocessor는 pickle 없이 npz를 읽고, 입력/receipt/config/raw SHA, 시간축/shape/finite/초기축을 검사한다.
공통 좌표에 필요한 세 signed 성분만 투영하고 축 support를 별도로 구성한다. 수치 내부 thread1.
이번 새 분석은 한 프로세스의 유한 저장자료 연산이다. 상세 benchmark와 NCP IVP는 0이다.
NCP의 새 미완료 작업은 기존 cooperative executor와 각 lane의 실제 allocation/debit를 사용한다.
다른 Codex/PID 존재는 전역 veto가 아니며, actual CPU/RAM/disk/lease가 admission을 결정한다.

REC116 기존 HEAD4cffa8a0/tree916132bd, 원 U5 HOLD_9_FAIL/HOLD_8_FAIL,
CLOSED_HOLD_NOT_RESET, REC REI_activation=false를 유지한다.
physical HOLD, global convergence NOT_RUN, production NOT_APPROVED를 유지한다.
새 independent review는 이번 consumer/code 범위에만 기록하고 과거 NOT_RUN 기록은 수정하지 않는다.

최신237 실행은 조사 시점의 공유 원본/hash 근거다. PR199 당시 HEAD8b71c13e에는 새 source가 없었다.
현재 consumer 자체는 REC116 위 새 branch에 게시하고 실제 owner 게시가 확인되면 별도 provenance로 연결한다.
