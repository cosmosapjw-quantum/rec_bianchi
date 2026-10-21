# 선택된 REC 연구: 저장된 z20→2 궤적의 축 응답과 혼합 잔차

## 현재 결정과 입력

새 적분 후보는 최신 다른 스레드의 완료 자료 발견으로 교체되었다.
현재 단일 작업은 collisionless PR147 source
3b85dedce84d37b3e165da00685a8a984950aafe에서 생성된 저장 궤적의 **63축 support /112 mixed retrospective comparison**이다.
새 ODE/NCP/benchmark0. warm C15 729와 z20→4 long1231은 각각 자체 범위의 재사용 근거이며, 이 분석에 행·계수를 섞지 않는다.

고정된 nominal controls:
S_i^F∈{0,.0003,.001,.003,.01,.03,.1};
m=P_m,i^F∈{-.0003,-.0001,0,.0001,.0003};
r=P_r,i^F∈{-.001,-.0003,0,.0003,.001}.

175=7×5×5 조건 중, 각 고정 S_i^F에서 m=0 또는 r=0인9개가 axis support이다.
전체63 supports,112 mixed trajectories, 각153 저장 epoch.
이들은 x=ln(a/a_ref), a_ref=1/21의 **동일 x 또는 zbar=1/a−1**에서 비교한다.
서로 다른 case의 동일 x는 동일 elapsed proper time을 뜻하지 않는다.

현재 파일 직접 검사:
- unique selected keys175; support63; mixed112.
- 모든 selected x array byte-value identical, shape(153,), x0=0, x_end=ln7.
- signed shear를 raw s,H에서 계산한 |sqrt6 s/H|와 저장 Sigma_F 차이 최대4.163336342344337e-17.
- nominal initial triple과 실제 realized triple의 차이 최대1.3877787807814457e-17.
- endpoint elapsed proper seconds 범위 [9.759090211441186e16,9.75955472966245e16].
이는 원자료를 읽어 검산한 결과이며 ODE를 재실행한 결과가 아니다.
해당 숫자·hash·실행 근거는 TRAJECTORY_INPUT_CONTRACT_INSPECTION.json에 있다.

초기 shear 방향은 양의 orientation과 zero만 포함한다. 음의 초기 signed shear의 실험 결과로 일반화하지 않는다.
진화 중 signed shear는 부호가 바뀔 수 있다.

## 정의와 구현 경로

공통 orthonormal normal frame에서
sigma_ab=diag(-s,-s,2s),
pi_ab^A=diag(-p_A,-p_A,2p_A), A=m,r.
SI H,s는 s^-1, p_A는 J/m³, kappa_t=8piG/c².

signed Frobenius coordinates:
S_F=sqrt6 s/H,
P_m=sqrt6 kappa_t p_m/H²,
P_r=sqrt6 kappa_t p_r/H².

norm coordinates:
Sigma_F=|S_F|,
Pi_m^F=|P_m|,
Pi_r^F=|P_r|,
Pi_total^F=|P_m+P_r|.

half-contraction coordinates는 각각1/sqrt2배다. 이 분석은 원자료의 full-Frobenius convention을 주표기로 사용한다.
P_r는 signed gamma+nu 합으로 정의하며, 부호 있는 component를 합한 뒤 norm을 계산한다.

관측 벡터 F(x;s0,m,r)=(S_F,P_m,P_r)은 signed 값이다.
각 고정 s0에서
Fhat(x;s0,m,r)=F(x;s0,m,0)+F(x;s0,0,r)−F(x;s0,0,0).

저장 Sigma_F를 이 식에 대입한 뒤 sign을 복원하는 절차는 사용하지 않는다.
S_F=sqrt6 raw_s/raw_H를 먼저 계산하고 signed prediction으로부터 abs를 취한다.
각 support case의 현재 H는 그 case의 자기중력 궤적에 따른 값이다. 공통H를 대입하지 않는다.

signed total prediction은 Pmhat+Prhat에서 만들고, 별도의 total-magnitude fit은 만들지 않는다.
axis support값만 prediction 입력이다. mixed값은 comparison에만 쓰며 fitting coefficient는0이다.
실제 realized 초기 offsets는 보존하고 nominal config는 lookup/label에 사용한다.

## 궤적별 혼합 적분 항등식: 직접 유도

x와 s0를 고정하고 scalar component f(m,r)를 생각하자.
f가0,m과0,r를 잇는 닫힌 rectangle의 근방에서 C²라고 가정한다.
미적분학 기본정리를 m 방향에 적용하면

f(m,r)−f(0,r)=integral_0^m f_m(u,r)du,
f(m,0)−f(0,0)=integral_0^m f_m(u,0)du.

두 식을 빼고 integrand에 r 방향 기본정리를 적용하면

R=f(m,r)−f(m,0)−f(0,r)+f(0,0)
 =integral_0^m integral_0^r f_mr(u,v)dv du.

m 또는 r가 음수일 때 integral은 oriented integral이며 같은 항등식이 성립한다.
따라서 rectangle에서 |f_mr|≤B가 확보되면 |R|≤|mr|B.
이 유도는 vector F의 각 성분에 그대로 적용된다.

현재 분석의 역할은 finite model의 C² response가 있을 때 성립하는 항등식과, 실제 저장 값에서 계산한 mixed finite difference를 연결하는 것이다.
현재 저장값만으로 B=sup|f_mr|를 측정·인증하지 않는다.
시간 전체의 bound를 얻으려면 x와 rectangle에 걸친 uniform derivative bound가 추가로 필요하다.
153개 저장시점의 최대잔차는 그153개 시점의 최대다.

## 저장 residual과 exact finite-system response의 관계

같은 nominal parameter map의 exact finite-closure response를 f라고 하자.
저장 response를 f_tilde=f+e로 쓰면 e는 ODE/roundoff/calibration realization 차이를 포함한다.
그때

R_tilde=R+e(m,r)−e(m,0)−e(0,r)+e(0,0).

e의 상한이 확보되지 않았으므로 작은 R_tilde로 exact-solution error나 physical decoupling을 판정하지 않는다.
이 식은 numerical error가 항상 큰다는 주장도 아니다. 측정된 residual의 구성요소와 남은 불확실성을 정확히 구분한다.
realized 초기 offsets를0으로 강제하거나 더큰 tolerance로 접는 처리는 원자료의 의미를 바꾸므로 하지 않는다.

가장 직접적인 결과는
“이 특정175-point collisionless grid의153 stored epochs에서63 support를 이용한 signed predictor가112 held-out mixed stored trajectories와 어느 만큼 달랐는가”
다. 이는 retrospective 비교이며 사전등록 blind validation을 주장하지 않는다.

## norm 오차의 정확한 유한 bound

실수a,b에 대해 reverse triangle inequality:
||a|−|b||≤|a−b|.

따라서 매 저장시점에서
|Sigma_F−|Shat_F||≤|R_S|,
|Pi_m−|Pmhat||≤|R_m|,
|Pi_r−|Prhat||≤|R_r|.

total에는
||P_m+P_r|−|Pmhat+Prhat||
 ≤|R_m+R_r|
 ≤|R_m|+|R_r|.

이는 **실제 signed stored residual로부터 norm discrepancy를 제한하는 대수적 관계**다.
unknown true solution에 대한 numerical global error bound가 아니다.
일반 텐서에서는 같은 구조가 Frobenius norm의 reverse triangle로 성립한다.

모든norm차이는 같은frame·같은시점·각case의정규화정의 아래 계산한다.
source/closure가다른 warm C15 total norm과여기 total norm을계수추정에함께쓰지않는다.

## 통계·그림·검토 계약

- 주 residual 통계는112 mixed histories×153=17,136 points에서 계산한다.
- 전체175 histories×153=26,775 points를 저장할 수 있으나 supports의 자기재현을 별도 validation 성공으로 세지 않는다.
- 최대값의 case triple,epoch,x,z,actual,predicted,signed residual을 함께 기록한다.
- 각 성분 절대 residual을 주정보로 제시한다. zero crossing과 cancellation 근처 relative residual은 denominator policy를 명시하고, 임의display floor를solver tolerance로 바꾸지 않는다.
- z 또는x 그래프는 실제 저장점에서 만들고, nonuniform parameter axes를 실제 좌표 또는 명시적 categorical labels로 표시한다.
- normalized signed shear와magnitude를 혼동하지 않는다. 고정 초기Sigma의plane에서도 endpoint shear sign reversal을 보존한다.
- axis input와mixed comparison을 코드 구조상 구분한다. 혼합값 perturbation은 prediction에 영향을 주지 않아야 한다.
- shape,missing/duplicate grid point,clock mismatch,nonfinite,H≤0,normalization mismatch는 fail-closed로 처리한다.
- 입력과실행identity를묶고sourcebytes·원본raw를수정하지않는다.

## 검산과현재판정

Wolfram 새호출 결과:
rectangle minus mixed integral=0 (bidegree2 generic polynomial check);
stored-error combination residual=0;
reverse triangle over all reala,b=True;
total reverse+triangle chain over all realcomponents=True;
counts={63,112,26775,17136}.

general C² mixed-integral statement는 위FTC 직접유도가증명이고, polynomial CAS는 보조검산이다.
TRAJECTORY_CAS.json에 실제입출력이있다.

판정: PASS_SCOPED_RETROSPECTIVE_ANALYSIS_CONTRACT.
아직 reducer source의 C9 review/실제 residual값 검토는 별도다.
물리HOLD,globalconvergence NOT_RUN,production NOT_APPROVED,원REC U5HOLD,REC REI_activation=false는보존한다.
