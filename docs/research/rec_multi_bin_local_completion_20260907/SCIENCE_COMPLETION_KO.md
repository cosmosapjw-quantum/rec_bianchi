# REC 다중 bin 연구: 네 보존량과 평형 부분공간의 완결

상태: `DERIVED_AND_SOURCE_AUTHORED / EXECUTION_NOT_PERFORMED`.
작업은 기존 `REC_MULTI_BIN_AFFINITY_COMPATIBILITY_RESEARCH`의 로컬 완결이다.
새 물리모델, provider 또는 시간 적분기를 만드는 단계가 아니다.

## 1. 재개 기준과 변경 범위

Fresh read 기준은 PR79다.

- source: `2e3b73972ee298d44efdfb10016e314f58b0bada`
- tree: `471442ce757fde701340729cd1abde281fd0db01`
- 직접 부모 PR78: `a1acf4037f68131ac4c6068eb0d450ef7e51bc97`
- 기존 코드: `docs/research/rec_multi_bin_affinity_20260907/`

PR79의 원본 표 loader, 다중 bin source, 기존 7개 검사와 그림 코드는 이미
작성되어 있다. 이를 복제하거나 기존 branch에 덮어쓰지 않는다. 이번 변경은
이 디렉터리에 보충 검사, 로컬 실행 캡처, 이 연구 문서와 인계를 추가한다.
`src`, `tests`, `archive`, 기존 결과와 workflow는 변경하지 않는다.
PR77의 10개와 PR78의 3개는 과거 수용 결과이며 이번 실행 수에 더하지 않는다.
PR79 실행 결과를 이 응답에서 수령했다는 주장도 하지 않는다.

## 2. 정의와 적용 영역

같은 수소 정지계, 서명 (-,+,+,+), 고정 격자와 양의 mu_i,n_H,
양의 occupation f_i, 양의 두 원자 population 및 g=1을 가정한다.
상대 boost, 수송, 팽창에 의한 상태 진화, 이동 map, 각도/편광은 제외한다.
SI 에너지는 E21_J=E21_eV*(1.602176634e-19 J/eV), 주파수는 E/h이며
h=6.62607015e-34 J s다. c나 h를 1로 둔 계산이 아니다.

원본 2s 자료는 기본140개/hires408개 bin을 정의한다. 두 표의 provenance는
실제 target cell이나 분배 map의 물리 권위를 제공하지 않는다. 이번 target은
PR79와 같은 제조 입력이다.

    epsilon = 2^-30
    U = E/E21 = (epsilon, 1/4, 1/2, 3/4, 1-epsilon)
    mu = (2,4,8,4,2) m^-3
    beta_i = mu_i/n_H
    w = (x_u,x_g,beta_0 f_0,...,beta_4 f_4)

w는 수소 원자당 무차원 count 좌표다. Gamma_b는 수소 원자당 사건의 초당
변화율이다. 여기서 per-H는 수소 원자 기준이며 Hubble rate H의 역수가 아니다.
H>0의 시간 좌표 변환은 기존 PR79의 G=C/(H f)로만 사용한다.

각 두 광자 source의 에너지비는 u와 1-u다. 동일한 대칭 target의 선형 에너지
분율 B로 두 leg를 읽고 분배하면, 반응벡터는

    v_b = (-1,1,D_0b,D_1b,D_2b,D_1b,D_0b)^T,
    2 D_0b + 2 D_1b + D_2b = 2,
    wdot = V Gamma,

이다. 이는 정확한 유리수 stencil의 구조다. 실제 binary64 B의 반올림 잔차는
별도로 검사하며 exact rank를 부동소수 singular-value cutoff로 정의하지 않는다.

## 3. 네 독립 보존량 — 직접 유도

다음 네 행을 L의 행으로 둔다. 순서는 위 count 좌표와 같다.

    L0 = (1,1,0,0,0,0,0)
    L1 = (2,0,1,1,1,1,1)
    L2 = (0,0,1,0,0,0,-1)
    L3 = (0,0,0,1,0,-1,0)

L0 v=0은 원자수 보존, L1 v=-2+sum D=0은 원자 여기와 두 광자의 합성
count 보존, L2 v=L3 v=0은 두 대칭 photon-node 쌍의 count 차이 보존이다.
네 행의 선형독립성은 원자 ground, upper, photon endpoint 및 inner-pair
성분을 차례로 보면 따른다. 따라서 rank L=4이고 rank V<=3이다.

에너지 행 e=(1,0,U)는 별도의 다섯 번째 보존량이 아니다.

    e = L1/2 + (epsilon-1/2)L2 - L3/4.

이는 이전에 원자수/합성 count/에너지 세 보존량을 나열한 결과와 모순되지
않는다. 그 세 행은 독립이지만 전체 kernel을 생성하지는 않았다.

실제 표에서 독립인 세 반응열을 확인하면 rank V>=3이다. rank V=3인 경우
차원정리에 의해 L의 네 행이 ker(V^T) 전체를 생성한다. 보충 검사는 실제
원본 표의 u를 유리수로 lift해 모든 열에서 L V=0을 확인하고, 기존 rank
루틴이 찾은 실제 bin 세 개를 별도의 SymPy rank 검사에 넣는다. 아직 실행한
결과는 없으므로 실제 두 표의 이 검사가 PASS라고 기록하지 않는다.

## 4. 모든 양의 정상상태의 매개화 — rank3 조건부 직접 유도

chi_i=ln(1+1/f_i)이고 읽기와 분배의 affinity가 일치할 때

    A_b = ln(x_u/x_g) + D_:b^T chi = ln(F_b/R_b),
    sigma = ds/dt = sum_b (F_b-R_b) ln(F_b/R_b) >= 0.

s=S/(N_H k_B)이며 양의 F_b,R_b에서 각 항은 비음수다. 순간 source가 0이면
sigma=0이고, 모든 양의 rate bin에서 F_b=R_b다. 합계 반응률의 우연한 상쇄만으로
정상상태를 인증하지 않는다.

rank V=3이면 상세균형 조건은

    chi_0+chi_4 = chi_1+chi_3 = 2 chi_2,
    ln(x_u/x_g) = -2 chi_2

와 동치다. 충분성은 위 D 대칭과 sum D=2에서 즉시 따르고, 필요성은 독립인
세 D 열이 대칭 분배의 3차원 선형공간을 생성한다는 사실에서 따른다.
따라서 양의 정상상태는 다음 네 실수 매개변수로 쓸 수 있다.

    chi=(kappa+p, kappa+q, kappa, kappa-q, kappa-p),
    kappa > max(|p|,|q|),
    A=x_u+x_g>0,
    x_u=A exp(-2 kappa)/(1+exp(-2 kappa)),
    x_g=A/(1+exp(-2 kappa)), f_i=1/expm1(chi_i).

이는 Planck 한 곡선보다 크다. 예를 들어 kappa=1,p=-1/2,q=-1/8이면
chi=(1/2,7/8,1,9/8,3/2)이고, 이 제조 target 에너지에 선형인 Planck 지수가
아니지만 모든 bin에서 상세균형을 만족한다. 이 정적 유도는 실제 시간
진화를 실행한 관측값이 아니다. 다른 원자 과정이나 수송이 이 보존량을
유지한다고 일반화하지 않는다.

## 5. 평형 Jacobian의 좌·우 kernel

고정 beta에서

    s=-x_u ln x_u-x_g ln x_g
      +sum_i beta_i[(1+f_i)ln(1+f_i)-f_i ln f_i],
    W=-Hessian(s)=diag(1/x_u,1/x_g,1/[beta_i f_i(1+f_i)])>0.

각 bin의 상세균형에서 F_b=R_b=r_b>0이고

    J=-V diag(r_b) V^T W,
    WJ=-(WV) diag(r_b) (WV)^T,
    ker(J)=W^-1 ker(V^T)=span(W^-1 L^T).

마지막 등식은 z^T V diag(r)V^T z=sum r_b(v_b^T z)^2에서 따른다.
따라서 rank3 조건에서 네 우영벡터를 W^-1 L^T로 명시할 수 있다. 위 정상상태
매개화의 kappa,p,q,A 방향도 같은 우 kernel을 생성한다. 보충 검사는 실제
기존 API의 count-JVP로 J의 7개 열을 만들고 두 종류의 우영벡터를 대조한다.

추가로, Lw가 고정된 양의 affine compatibility class에서 s는 엄격히 오목하다.
그 class에 양의 정상상태 w_*가 존재하면 grad s(w_*)는 L의 행공간에 속하므로
모든 같은-class 허용방향에서 첫 변분이 0이고, 엄격한 오목성에 의해 w_*는
그 class 안의 유일한 entropy maximum이다. 이는 조건부 유일성이지 모든
초기상태에 공통인 Planck 유일성, interior equilibrium 존재 정리, 전역
수렴률 또는 수치 적분기의 안정성 증명이 아니다.

## 6. density 방향과 누락된 photon 방향의 구현 검사

n_H를 매개변수로 변화시키며 count 좌표를 비교하면 beta=mu/n_H도 변한다.
원본 COM의 dC만 곱하는 것은 count-JVP가 아니다.

    delta(beta_i C_i)=beta_i delta C_i-beta_i C_i delta n_H/n_H.

따라서 실제 count-source와 count-JVP에 L을 적용해 0을 확인하며, 두 번째
항을 삭제한 진단식은 실패해야 한다. 이 검사는 n_H의 물리시간 진화를
도입하는 것이 아니라 같은 순간 source의 매개변수 미분이다.

PR79의 84개 JVP 비교는 photon y1, 다섯 다른 매개변수 축과 한 혼합 방향이다.
그 범위를 모든 photon 좌표 방향 검사로 과장하지 않는다. 새 보충은 하나의
명시적 비평형 상태에서 y0,y2,y3,y4를 두 표/두 읽기에 적용한 16개 비교다.
독립 80/120자리 primal과 h=2^-32,2^-36 중앙차분을 재사용하고 기존 허용치를
넓히지 않는다. 이 두 검사는 서로 다른 영역/방향을 보충하지만 전 정의역의
미분 검증이나 보편 오차 상한은 아니다.

## 7. 작성된 실행 경로와 정확한 미검증 상태

`verify_nullspace.py`: 위 4개 표적 unittest 그룹, 16개 추가 방향 비교,
실제 원본 API 호출, 별도 RESULT와 CSV. 새 production source는 없다.

`run_local.py`: 표준 라이브러리 외부 supervisor. 수학 import 전에 실제
commit/tree/보호 경로를 기록하고 원래 PR79 runner와 보충 runner를 별도
subprocess로 실행한다. 원본 stdout/stderr, 실제 process returncode,
TestID 집합, timeout, source identity를 분리한다. 출력은 worktree 밖에 두며
설치·Git 쓰기·네트워크 호출·GitHub Actions 실행은 하지 않는다.
`GITHUB_ACTIONS=true` 환경에서는 시작을 거부한다. OS 수준 네트워크 격리까지
수행했다고 주장하지 않는다. 그림 생성 실패는 과학 검사와 별도 기록되고,
시각검토는 자동 PASS로 바뀌지 않는다.

현재 대화에서 container와 Python은 process-start ClientError였다.
WolframContext도 kernel 평가 전 MCP HTTP404였다. 새 code execution,
syntax compilation, 새 4개 검사, 기존 7개 검사, 신규 그림/시각검토 및
제3자 독립 review는 모두 미수행이다. 동일한 실패를 재시도하거나 Actions로
대체하지 않는다. GitHub source publication은 실행 검증과 별개다.

이 문서의 수학 점검과 코드 경로 점검은 같은 작성자의 검토다. 실행하지
못한 detector의 이름이나 정확해 보이는 SHA를 PASS 근거로 사용하지 않는다.

## 8. 문헌 탐색의 역할

SciSpace의 첫 검색은 직접적인 이산 read/scatter 증거를 주지 않았다.
후속 검색에서 Maas & Mielke의 상세균형 gradient-structure 논문을 확인했고,
arXiv 원저자 초록과 DOI도 대조했다.

- Jan Maas and Alexander Mielke (2020), Modeling of Chemical Reaction Systems
  with Detailed Balance Using Gradient Structures, doi:10.1007/s10955-020-02663-4,
  https://arxiv.org/abs/2004.02831
- Markowich and Pareschi, Fast conservative and entropic numerical methods for
  the Boson Boltzmann equation, Numerische Mathematik 99 (2005), 509-532,
  https://arxiv.org/abs/1009.2748

전자는 상세균형과 상대엔트로피에 의한 gradient 구조, 후자는 보존/entropy/
Bose 정상상태를 구분하는 수치 방법론의 배경이다. 이번 네 보존량, 5-node
rank와 정상상태 매개화는 위에서 직접 유도한 프로젝트 결과이며, 검색한
논문이 이 특정 source나 B/mu를 인증하는 것은 아니다. 논문 PDF 전문을 이번에
검토한 것으로 표시하지 않는다. PR79가 언급한 TEFF 원고는 이번 응답에서
열람하지 않았고 새로운 유도의 근거로 사용하지 않았다.

## 9. 완료 조건과 다음 한 작업

이 child의 현재 완료 범위는 유도와 실행 가능한 형태의 source 작성·인계다.
실행 가능한 형태라는 표현은 실제 syntax/runtime 검증을 통과했다는 뜻이 아니다.
다음 한 작업은 고정 소스에서 로컬 7+4 그룹의 실제 결과와 그림을 얻고,
같은 scope 안의 관측 결함을 수정·검증해 결과 branch로 반환하는 것이다.
이미 동일 source의 유효한 결과가 게시되었다면 해당 결과를 재사용한다.

`NO_PASS_REC_PHYSICAL_SPLIT`; physical_source_authenticated=false;
provider_admitted=false. 전체 repository GREEN, 실제 B/mu 인증, BASS evolution,
실제 재결합 history, provider, merge/ready와 공식 Jira dependency는 미완료다.
