# PR147 collisionless LRS 상태·초기성분 민감도: 독립 유도

## 1. 대상과 기존 결과의 연결

이 유도는 REI PR147 source `3b85dedce84d37b3e165da00685a8a984950aafe`의
`CanonicalFVSpecies`를 대상으로 한다. 실제 읽은 로컬 source는
`intake/unified_z2_snapshot_20261021/vendor/canonical_fv.py`,
`vendor/species_hierarchy.py`, `components/component_adapter.py`, `adapter.py`다.
다음 식은 이 코드의 유한 차원 vector field를 미분한 것이다.
ODE 적분기, 저장 trajectory, 물리 closure를 바꾸지 않는다.

BASS_CR PR93의 `mass_shell_derivatives.py`는 같은 source의 trajectory 방향
mass-shell 압력 도함수와 초기 2차 shear jet을 제공한다. 그 식과 상쇄 구분을
재사용한다. REI PR215는 다른 warm C15 source의 세 moment를 native로 묶었고
rho의 두 미분 항등식을 검증했다. 여기에서 새로 연결하는 기능은 PR147의
전체 H-constraint feedback을 포함하는 상태 JVP/VJP와, 독립 초기
`(S0, Pm0, Pr0)` 세 열에 대한 직접 parameter forcing·초기조건 미분이다.

고정 source: `fm=0.1`, `m/Tref=30`, `ne_source=None`, `nu_visc=0`,
`ellmax=8`, radial×angular=24×12, subcell Gauss3. 따라서 상태 수는40이다.
상태는 `y=(tau,b,v,u,Egamma,Ngamma,Enu,Nnu)`이고 각 radiation block은9차원이다.
`v=s/Href`, `tau=Href*t_elapsed`, 독립변수는 `x=ln(a/aref)`다.
이론의 x 범위는 admissible source chart와 H>0 안이다. z20→2 실행용 source
interval 확장은 원 owner의 z4→2 tail과 같은 별도 입력 계약으로 관리한다.

단위는 H,s가 s^-1, physical pi가 J/m^3이며 kappa_t=8*pi*G/c^2다.
`sigma=diag(-s,-s,2s)`, `pi_X=diag(-pi_s,X,-pi_s,X,2pi_s,X)`.
signed Frobenius 좌표는 `S=sqrt(6)*s/H`, `P_X=sqrt(6)*kappa_t*pi_s,X/H^2`다.
norm은 각각 절댓값이고 total은 signed matter+radiation을 합한 후 절댓값이다.
half-contraction 좌표는 위 좌표를 sqrt(2)로 나눈다.

## 2. 보존 packet으로부터의 미분

질량껍질에서 각 conserved packet의 값과 양의 measure를 다음처럼 둔다.

    U = exp(-2x) q^2 exp(2b) (1-mu^2)
    W = exp(-2x) q^2 exp(-4b) mu^2
    E = sqrt(m^2+U+W)
    d = exp(-3x) N(A)/Nref(A)

`N(A)=N0*(1+A*P2(mu))`, `Nref(A)=sum N(A)*E_initial`이며
`E_initial=sqrt(m^2+q^2)`다. 모든 sum은 실제 유한 grid 위의 합이다.
`d`는 x에 의존하되 고정 x에서 b와 무관하다.

    rho = sum d*E
    pp  = sum d*U/(2E)
    pa  = sum d*W/E
    pi  = (pa-pp)/3
    pbar = (2pp+pa)/3

고정 x,A에서 `U_b=2U`, `W_b=-4W`, `E_b=(U-2W)/E`이므로

    rho_b = -6*pi
    pi_b = sum d*[(-U-4W)/(3E)+2*(W-U/2)^2/(3E^3)]
         = -sum d*[(2U+8W)*m^2+U^2+14UW+4W^2]/(6E^3).

두 번째 표현은 부호와 cancellation을 명확히 한다. 실제 nonnegative packet과
m>0에서는 `pi_b<=0`, `rho_bb=-6*pi_b>=0`이다. 양의 measure를 가진 nonzero
momentum packet이 있으면 부등식은 엄격하다. 즉 고정 분포의 b 응답에 대해
finite-sum energy는 convex이고 anisotropic pressure의 b slope는 음수다.
이것은 finite quadrature의 구조이며 coupled 전체계의 안정성 증명은 아니다.

고정 b에서는 `E_x=-(U+W)/E`, 따라서

    rho_x = -3*(rho+pbar).
    d_x rho(x,b(x)) + 3*(rho+pbar) + 6*b_x*pi = 0.

이 항등식은 원 stress-work sign과 일치한다. 분포가 x에 대해 바뀌는 collision
source나 다른 closure에는 별도 source term이 필요하다.

### A의 정규화 도함수

`N_A=N0*P2(mu)`, `Z=Nref(A)`, `Z_A=sum N_A*E_initial`라 두고, kernel K가 A와
무관할 때

    M_K = exp(-3x)*sum N(A)*K/Z
    d_A M_K = exp(-3x)*sum N_A*K/Z - M_K*Z_A/Z.

K를 E, U/(2E), W/E에 각각 적용해 rho_A, pp_A, pa_A, pi_A를 얻는다.
finite grid에서 Z_A가 작다고 0으로 대체하면 원 수치 map을 바꾼다.
`N0`는 원 constructor/prepared geometry에서 직접 재사용한다. `N(A)/(1+A*P2)`로
복원하면 분포 경계에서 0/0 문제가 생길 수 있으므로 그 나눗셈을 요구하지 않는다.
이 도함수는 FP rounding map의 도함수가 아니라 동일 finite-sum 수식을 미분한 값이다.

## 3. Einstein constraint가 만드는 두 scalar variation

`M=omega_m*fm/aref^3`, `a=aref*exp(x)`라 하고

    R0 = (omega_gamma*Eg[0]+omega_nu*En[0])/a^4
    DR = (omega_gamma*Eg[2]+omega_nu*En[2])/(3*a^4)
    D  = M*pi+DR
    H^2 = h0^2*(omega_m*(1-fm)/a^3+M*rho+R0+omega_lambda)
          + Href^2*v^2
    w = Href*v/H
    C = 3*h0^2/(Href*H).

원 `fm>0` 경로는 H^2에서 `u=y[3]`를 사용하지 않으며 `u'=0`이다. 이를
자연스럽게 보이도록 수정하지 않는다. `tau` 역시 RHS에 직접 들어가지 않는다.

고정 x,A에서 상태 perturbation delta y에 대해

    L = delta log H
      = [h0^2*(M*rho_b*delta b
         +(omega_gamma*delta Eg[0]+omega_nu*delta En[0])/a^4)
         +2*Href^2*v*delta v]/(2*H^2)
    Q = delta D
      = M*pi_b*delta b
        +(omega_gamma*delta Eg[2]+omega_nu*delta En[2])/(3*a^4)
    delta w = (Href/H)*delta v-w*L.

parameter A도 perturb할 경우 L의 numerator에 `h0^2*M*rho_A*delta A`,
Q에 `M*pi_A*delta A`를 더한다. radiation seed k는 고정된 x,y의 vector field에
별도로 나타나지 않으며 초기 radiation multipoles에만 들어간다.

## 4. 행렬을 만들지 않는 JVP

원 RHS의 첫 네 성분은 `(Href/H,w,-3v+C*D,0)`이다. radiation block U에 대해
`U'=w*B*U`이며 energy block의 B는 원 energy_matrix, number block은 원 number_matrix다.
고정 x,A에서 체인룰을 적용하면

    delta tau' = -(Href/H)*L
    delta b'   = delta w
    delta v'   = -3*delta v+C*(Q-D*L)
    delta u'   = 0
    delta U'   = delta w*(B*U)+w*(B*delta U).

이 식은 임의의 상태 방향과 여러 열을 한꺼번에 처리한다. 3 sensitivity 열을
계산할 때 nonlinear mass-shell geometry와 H, D, B*U는 공통이다. 방향마다 별도
mass-shell RHS를 다시 계산하거나 40×40 Jacobian을 저장할 필요가 없다.
이는 연산 구조에 대한 진술이며 측정된 wall-time speedup은 아니다.

## 5. 독립적인 transpose 구성

`h=gradient_y(log H)`, `kD=gradient_y(D)`를 앞 절의 sparse row로 둔다.
주어진 output covector lambda에 대해

    T = lambda_b + sum_blocks dot(lambda_U, B*U)
    alpha = -(Href/H)*lambda_tau-w*T-C*D*lambda_v.

그렇다면 VJP는

    J^T lambda = alpha*h + C*lambda_v*kD
                 +[(Href/H)*T-3*lambda_v]*e_v
                 + radiation_blocks(w*B^T*lambda_U).

직접 내적을 전개하면 `dot(lambda,J*d)=dot(J^T*lambda,d)`다.
이 transpose 구현은 행렬 전개 없이 원래 JVP의 각 scalar 경로를 역으로 합친다.
확인할 항목은 independent finite difference와 이 내적 항등식 둘이다.
JVP/VJP끼리의 일치만으로 양쪽의 공통 부호 오류를 배제할 수는 없다.

## 6. 실제 독립 세 seed의 체인룰

원 component adapter의 입력을 `theta=(S0,Pm0,Pr0)`로 고정한다.
`d0=1-S0^2/6`, `Km=Km(0)*d0`, `Kr=Kr(0)*d0`이며

    v0 = S0/sqrt(6-S0^2)
    A = Pm0/Km
    k = Pr0/Kr.

원 adapter의 positive/zero shear slice에서

    dv0/dS0 = 6/(6-S0^2)^(3/2)
    dA/dtheta = (2*S0*A/(6-S0^2), 1/Km, 0)
    dk/dtheta = (2*S0*k/(6-S0^2), 0, 1/Kr).

`Y0=partial y0/partial theta`의 v row에는 `(dv0/dS0,0,0)`가 들어가고,
네 radiation block의 ell2 row에는 각각 `(dk/dtheta)/5`가 들어간다.
monopoles는 상수1, 나머지 상태는 상수0이므로 그 행의 초기 도함수는0이다.
원 positive-shear 입력 경계 S0=0에서 이 식은 admissible right derivative로
해석한다. 명시적인 signed extension을 채택하지 않는 한 음의 S0 case를 원
pilot에 추가했다고 말하지 않는다. S0=0.1의 bounded contract도 왼쪽 미분을 쓴다.

직접 A forcing은 고정 y에서 앞 절의 `delta A=1`, `delta y=0`인 식으로
`f_A`를 얻는다. 따라서 세 열은

    Y' = J_y*Y + f_A*(dA/dtheta)
    Y(0)=Y0.

`J_y*Y`만 적분하면 Pm0의 변화가 canonical packet distribution을 바꾸는 경로를
누락한다. k의 별도 RHS forcing은0이며 Y0에 포함된 radiation seed가 이후
상태를 통해 영향을 준다. 이 정의는 일반 variational equation의 특수화다.

정의역은 source-allowed A in[-1,2], |k|<=0.5, positive H와 admissible state다.
현재 nominal pilot의 max |Pm|,|Pr|는 이 범위 안이다. sandbox의 실제 calibration
확인에서 Km(0)=0.0006836092932371262, Kr(0)=0.0029856941745693474,
Pm0=0.0003일 때 A=0.43884716455418027, Pr0=-0.001일 때 k=-0.33493048568654515다.
이 helper 확인에서 새 ODE는 실행하지 않았다.

## 7. 관측량의 민감도와 후속 해석

actual source가 쓰는 `Bphys=sqrt(6)*kappa_t*rhocrit_J_m3/H^2`를 유지하면

    delta S = sqrt(6)*delta w
    delta Pm = Bphys*[M*(pi_b*delta b+pi_A*delta A)-2*M*pi*L]
    delta Pr = Bphys*[delta DR-2*DR*L]
    delta Ptot = delta Pm+delta Pr.

`kappa_t*rhocrit`를 수학적으로 동등한 상수로 치환하더라도 FP 연산 grouping이
원 관측량과 달라질 수 있다. source-normalized forcing과 SI-observable 규약은
한쪽을 다른 쪽으로 덮지 않고 원 계산식에 맞게 유지한다.

signed value가0이 아닌 곳에서 norm의 변화는 sign(value)*delta value다.
signed value가0인 곳의 절댓값은 일반적으로 선형 미분이 없으므로 signed
sensitivities를 주 결과로 저장한다. 실제 영점의 한쪽 방향 미분은
|delta value|지만 이를 Jacobian 한 행으로 표시하지 않는다.

향후 실제 tangent trajectory가 있으면 초기조건 변화의 국소 반응을 직접
표시할 수 있다. 예를 들어 transverse signed-shear zero x*에서 S_x!=0과
solution differentiability가 확보되면 implicit function theorem으로
`partial_theta x*=-S_theta/S_x`다. `z=21*exp(-x)-1`이면
`partial_theta z*=(1+z*)*S_theta/S_x`다. 현재 저장 sample bracket만으로 이
root derivative를 측정했다고 주장하지 않는다.

## 8. 필요한 경량 검증과 claim 범위

1. 고정 source의 실제 저장 state에서 몇 개의 independent direction을 선택하고,
   original RHS의 5-point finite difference와 JVP를 비교한다.
2. A의 normalization derivative와 원 constructor에 대한 중심차분을 비교한다.
3. 원 초기 calibration map의 세 derivative 열과 analytic Y0, A_theta를 비교한다.
4. arbitrary covector로 transpose inner-product identity를 확인한다.
5. rho_b=-6*pi, pi_b<=0, rho_x=-3(rho+pbar), source energy identity를 확인한다.
6. signed observable JVP를 같은 물리 단위의 원 component observables와 대조한다.

FD에서 원 source guard를 존중한다. 특히 u=0인 raw에서 negative u perturbation은
super.fields의 u>=-1e-12 guard를 넘을 수 있다. random state directions의 u를0으로
두고, inert u column은 admissible positive perturbation으로 별도 확인한다.
tau와 u input columns0은 알려진 원 source 구조에 대한 검증이다.

이 검증은 finite vector field의 도함수 구현을 검사한다. 기존175 trajectory
전체나 NCP scalability를 재계산할 필요가 없다. 전체 time-dependent tangent
정확도, convergence, continuum quadrature error는 실제 적분 검증과 별도다.
Physical HOLD, global convergence NOT_RUN, production NOT_APPROVED는 유지한다.

## 9. primary sources와 재사용 범위

- Heinzle–Uggla, Classical and Quantum Gravity23(2006)3463–3489,
  DOI10.1088/0264-9381/23/10/016. Sec2 Eqs2d–2f,3에서 Bianchi I conserved
  covariant momenta와 density/stress 적분을 확인했다. 여기서는 그 kinetic
  구조와의 대응만 재사용하며 논문의 asymptotic theorem을 현재 finite L8
  matter+radiation+Lambda source에 그대로 적용하지 않는다.
  https://pure.mpg.de/rest/items/item_150627_1/component/file_150626/content
- SUNDIALS CVODES official Mathematics §4.2.7 Eq4.15 및 §4.2.1.1의 Jv 설명.
  `s_i'=f_y*s_i+f_p_i`, `s_i(0)=y0_p_i`라는 표준 variational structure와
  matrix-free derivative 연결을 재사용한다. CVODES solver 자체를 새 dependency로
  도입하지 않는다.
  https://sundials.readthedocs.io/en/latest/cvodes/Mathematics_link.html
- SciSpace는 Forward Sensitivity Method: General Case (2017),
  DOI10.1007/978-3-319-39997-3_4와 Cao–Li–Petzold–Serban(2002),
  DOI10.1137/S1064827501380630 등을 발견했다. 이 단위의 proof는 앞의 직접
  chain-rule 유도와 primary official equations에 의존한다. DAE adjoint theorem을
  현재 explicit ODE에 필요 이상으로 추가하지 않는다.

현재 노트는 독립적인 source·수식 검토다. 구현 검토는 실제 코드 diff와 출력이
준비된 후 별도 receipt로 기록해야 한다.
