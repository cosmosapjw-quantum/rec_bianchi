# REC R7B: 짧은 proper-time 구간을 위한 양의 rate-Hermite 적분과 균일 오차

2026-10-14, Asia/Seoul. 연구 단위 `REC_BG_INCREMENT_R7B_20261014`. 직전 R7의 세-case parity 결과는 재실행하지 않았다. 실제 REI 최적화에서 드러난 `HOLD_SHORT_STEP_SUBTRACTION`을 대상으로 선택한 별도 R7 판별 작업이다. 원래 다섯-case/반진폭/정련 의무 및 R8–R10의 상태는 변경하지 않는다.

## 1. 실제 문제와 이번 결과의 경계

읽은 REI 공개 HEAD는 `e09d58a0f9308b76bda78af840bd64639faa3cee`다. 같은 작업트리에서 실제 STATE, OPTIMIZATION_RESUME_CHECKPOINT, background_table의 계약·코드·검토 결과, canonical axbi_background.rs 및 exact-cache 계약을 읽었다. 원 source identity는 별도 보존된 검증 패키지에 있다. 상태 문서에서 AX07은 ZERO zbar20→4의 scoped 완료, AX08은 signed family 미완료, AX11/12는 준비되었으나 실행 전이다. 이 상태 문서가 현재 모든 프로세스의 생존을 직접 증명하지는 않는다.

기존 background table은 누적 t,b를 cubic Hermite로 보간한다. 그 개발팀은 이미 local polynomial increment와 log1p 폭을 구현했고, stable increment는 1024/2048셀에서 각각 최대2.3826e-11/5.8302e-12 상대 차이로 component gate를 통과했다. 그러나 생산 Driver::tentative는 여전히 두 누적 t의 차를 사용한다. 기존 검토에 기록된 누적 차분의 최대 상대 차이는 table1.7637e-6, direct4096 Simpson2.2460e-5였다. 이 값은 기존 검토의 관측값이지 이번에 native suite를 다시 실행한 값이 아니다.

첫 실패 입력은 actual binary64 a1=0.047619047619047616, a2=0.04761904762380952다. 기존 local64 reference는844944.380363970s, direct/table 누적 차분은844944.204474639s, 기존 stable primitive는844944.3803639701s였다. **안정적 차분 자체는 이미 있었으므로 그것을 이번 새 발견이라 하지 않는다.** 이번의 새 결과는 누적 t 대신 F=1/H를 직접 보간하고, 임의로 짧은 부분구간에 성립하는 상대오차를 source 식에서 해석적으로 제한한 것이다. 동일 F를 dt와 db에 사용한다.

이것은 새로운 numerical representation이다. 기존 exact-cache는 원 bit를 보존하는 별도 최적화이며, 그 계약에는 stable-dt 대체가 허용되어 있지 않다. 본 작업은 그 계약이나 생산 소스를 수정하지 않는다. Supplier integration 준비가 가능해졌지만 owner의 table production HOLD를 임의로 해제하지 않는다.

## 2. 물리적 clock과 양의 integrand

서명은(-,+,+,+), normal-comoving gas의 proper seconds를 t로 쓴다.

\[
 ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
 \quad H=\dot a/a,\quad s=\dot b,\quad
 \sigma^i{}_j=\operatorname{diag}(-s,-s,2s).
 \tag{BI-01}
\]

여기서 s는 shear rate[s^-1]이지 dossier의 length-time 좌표가 아니다. 단위 normal u.u=-1, physical velocity U=cu를 구분한다. c,ħ,kB를1로 두지 않는다. 아래 기하비에는 c가 소거되지만 원자 event rate와 source clock은 여전히 physical seconds다.

고정된 source family에서 ar=1/21, ae=.2, L=ln(a/ar), q=q_ref이며

\[
 H_F^2=H_0^2(\Omega_m a^{-3}+\Omega_r a^{-4}+\Omega_\Lambda),
 \quad s=qH_F(a_r)(a_r/a)^3,\quad H^2=H_F^2+s^2.
 \tag{BI-02}
\]

SameHDiagnostic에서는 H=HF를 사용하고 counterfactual 표기를 유지한다. H0=67.4*1e5/3.0856775814913673e24 s^-1, Om=.315, Or=9.2e-5, Ol=1-.315-9.2e-5의 실제 source 표현을 사용했다. 프로그램에서 저장된 입력 상수는 binary64 dyadic 값이며, exact-real 검산은 이 값들에서 같은 식을 평가한다. 이것은 각 primitive가 legacy와 bitwise 같다는 주장이 아니다.

두 family 모두

\[
 H^2=S(L)=\sum_{p\in\{0,3,4,6\}}C_p e^{-pL},\quad C_p\ge0,\ S>0,
 \quad F=S^{-1/2},\quad dt=F\,dL,\quad db=sF\,dL
 \tag{BI-03}
\]

로 쓴다. SameH는 C6=0이다. F와 dF/dL의 단위는 seconds, sF는 무차원이다. 음의 밀도 항이나 curvature 항, H=0, 임의 shear forcing은 이 간단한 계수 상계의 범위가 아니다.

## 3. 직접 유도한 전구간 interpolation bound

양의 가중치를 w_p=Cp exp(-pL)/S로 두고 mk=sum p^k wp라 한다. sum wp=1이고 0<=mk<=6^k다. 따라서 F'/F=m1/2는[0,3]에 있으며, 길이 h의 한 cell에서 Fmax/Fmin<=exp(3h)다. 직접 네 번 미분하면

\[
 \frac{F^{(4)}}F=
 \frac{105}{16}m_1^4-\frac{45}{4}m_1^2m_2
 +\frac94m_2^2+3m_1m_3-\frac12m_4.
 \tag{BI-04}
\]

각 항에 mk<=6^k를 적용하면

\[
 |F^{(4)}|\le K_4F,\qquad
 K_4=6^4(105/16+45/4+9/4+3+1/2)=30537.
 \tag{BI-05}
\]

이 상계는 최적 상계가 아니지만 현재 gate에 충분하다. 물리 fit이나 sampled maximum으로 결정한 수가 아니다. Wolfram은 BI-04의 symbolic residual0과 K4의 정확한 정수를 확인했다.

한 cell [Li,Li+h]에서 F와 F'의 정확한 양끝 데이터를 맞춘 cubic Hermite polynomial을 P라 하자. 내부 x에서 K=(F(x)-P(x))/[(x-Li)^2(x-Li-h)^2]를 잡으면 F-P-K(x-Li)^2(x-Li-h)^2는 양끝의 중복 영점과 내부 영점을 갖는다. Rolle 정리를 반복 적용하면 어떤 ξ에서 K=F4(ξ)/24다. 따라서

\[
 \frac{|P(L)-F(L)|}{F(L)}
 \le\epsilon_h:=\frac{30537}{384}e^{3h}h^4.
 \tag{BI-06}
\]

여기서 (x-Li)^2(x-Li-h)^2<=h^4/16을 사용했다. 특히 **전체 cell 중 임의의 양의 부분구간 I**에서

\[
 \left|\frac{\int_I P\,dL}{\int_I F\,dL}-1\right|\le\epsilon_h.
 \tag{BI-07}
\]

증명은 |P-F|<=epsilon_h F를 적분하고 양의 분모로 나누는 것이다. 더 일반적으로 양의 가중치 W에 대해서도 같은 식이 성립한다. q≠0에서 s의 부호가 고정되므로 W=|s|를 적용하면 db에도 같은 상대상계가 성립한다. q=0에서는 db=0을 정확히 사용하며 상대오차 나눗셈을 하지 않는다.

여러 cell을 지난 구간은 양의 참 적분들의 가중평균이므로 max epsilon_i가 전체 상대오차를 제한한다. **부분구간 길이의 역수나 cell 개수를 곱할 필요가 없다.** 이것은 시간·b 적분에 대한 구조이지 nonlinear chemistry 해의 error propagation을 생략하는 이유가 아니다.

### 실제 사용한 격자의 정확한 폭 검사

N=1024,2048에서 h*=14351/(10000N)를 사용했다. 각 저장 a-knot은 exact dyadic 값으로 바꾸고, 모든3072개의 a_(i+1)/a_i가 sum_(k=0)^12 (h*)^k/k!보다 작음을 Fraction으로 확인했다. 이 유리수 합은 exp(h*)의 엄격한 하한이므로 실제 logarithmic cell width가 h*보다 작다는 결론은 부동소수점 log 비교에 의존하지 않는다.

exp(3h*)<=1/(1-3h*)에서 얻은 정확한 유리수 상계는 다음과 같다.

| N | 이상적 보간 상대상계의 정확한 유리수 | 짧은 상향 표시 |
|---:|---|---:|
|1024|431751417531032299779 / 1401457724289449984000000000000|3.080731e-10|
|2048|431751417531032299779 / 22470660862741839872000000000000|1.921401e-11|

둘 다 기존 component1e-9 gate 아래다. **정확한 endpoint/slopes의 interpolation theorem이며, Python/libm·node evaluation·source physics 전체 인증값은 아니다.**

## 4. 양성, 안정적 적분, 동일한 clock/shear 표현

u=(L-Li)/h에서 polynomial P=c0+c1u+c2u²+c3u³의 계수는

    c0=f0, c1=h d0,
    c2=3(f1-f0)-h(2d0+d1), c3=-2(f1-f0)+h(d0+d1).

Bernstein controls는 f0,f0+h d0/3,f1-h d1/3,f1다. 0<=di<=3fi이고 h<1이므로 모두 양수다. 따라서 P>0, 새 clock은 엄격히 증가한다. 실제 코드도 computed controls의 양성을 검사한다. Missing/domain input을 clipping하거나 다른 model로 대체하지 않는다.

실제 binary64 endpoints a1<a2의 폭은

\[
 \delta L=\log1p((a_2-a_1)/a_1)
 \tag{BI-08}
\]

으로 정의한다. 작은 폭을 두 개의 독립적인 global log 값의 뺄셈으로 복원하지 않는다. 한 cell에서 시작점 u0의 polynomial을 P(u0+v)=p0+p1v+p2v²+p3v³로 옮기면

\[
 \Delta t=\delta L\sum_{k=0}^3\frac{p_k(\delta L/h)^k}{k+1}.
 \tag{BI-09}
\]

이 식은 누적 t의 큰 상수를 전혀 평가하지 않는다. crossing된 실제 a-knot에서 구간을 나누고 작은 적분들을 math.fsum으로 합한다.

별도의 s/H 보간으로 clock 관계를 깨뜨리지 않고 동일 P를 사용한다:

\[
 \Delta b=s(a_1)\delta L
 \sum_{k=0}^3p_k(\delta L/h)^k J_k(3\delta L),\quad
 J_k(z)=\int_0^1v^ke^{-zv}dv.
 \tag{BI-10}
\]

Jk는 sum_(n=0)^12 (-z)^n/[n!(n+k+1)]로 평가한다. 현재 cell의 0<=z<.1에서 이상적 교대급수 나머지는 z^13/[13!(k+14)] 이하다. 따라서 남은 db 적분오차는 |s(a1)|deltaL sum|pk|(deltaL/h)^k z^13/[13!(k+14)]로 따로 제한할 수 있다. 실제 libm/summation roundoff와 이 series remainder를 구별한다. Ideal limit에서는 d b_hat/d t_hat=s가 정확하고 q 반전에 dt는 짝수, db는 홀수다.

### Node 및 arithmetic 오차의 위치

두 endpoint 값의 절대오차가 각각 e0 이하이고 slope가 e1 이하라면 Hermite basis에서

\[
 |\widetilde P-P|\le e_0+\frac h4e_1.
 \tag{BI-11}
\]

H00+H01=1, |H10|+|H11|=u(1-u)<=1/4에서 나온다. 이 항을 Fmin으로 나누어 BI-06에 더하고 interval integration arithmetic을 별도로 더해야 computed error bound가 된다. 이번에는 node/libm의 directed enclosure를 만들지 않고 아래의 고정밀 대조로 평가했다. 잘못된 출처의 warm certificate를 이 e0,e1로 사용하지 않는다.

## 5. 광자 운반에 연결되는 정확한 유한 사상

초기 local cosine μ와 db에 대해

\[
 R^2=e^{2\Delta b}(1-\mu^2)+e^{-4\Delta b}\mu^2,
 \quad\log(E_2/E_1)=-\Delta L+\log R,
 \quad\mu_2=\mu e^{-2\Delta b}/R,
 \quad d\Omega_2/d\Omega_1=R^{-3}.
 \tag{BI-12}
\]

초기 방향과 최종 방향을 Jacobian 없이 교환하지 않는다. 코드에서는 expm1,log1p를 사용하고 축방향/수직방향의 정확한 극한을 따로 처리한다. 서로 잇닿은 두 구간의 사상 합성이 직접 전체 구간과 일치하는지 검사했다.

순간극한은

\[
 \dot{\log E}=-H-s(3\mu^2-1),\qquad
 \dot\mu=-3s\mu(1-\mu^2).
 \tag{BI-13}
\]

Wolfram에서 두 생성자와 sphere Jacobian의 잔차가0이다. 독립 local xTensor에서는 unit-sphere tangent, expansion/shear energy contraction, convective product rule의3개 잔차가0이었다. 양의3metric은 normal observer의 공간 metric으로 spacetime signature 변경이 아니다. xCoba나 Einstein equation solve는 수행하지 않았다.

|partial logR/partial b|<=2이므로 bounded interval errors에 대해 photon log-energy error는 |delta L|+2|delta b|로 제한된다. 이것은 geometric map의 안정성이고, 뒤따르는 threshold activation이나 photon/chemistry history의 전체 오차는 별도다.

## 6. 실제 계산 결과와 적용 결정

Python binary64 후보와 mpmath1.3.0의65자리 독립 local quadrature를 비교했다. 입력 상수와 실제 a endpoints를 exact dyadic로 승격하고, v∈[0,1]에서 적분했다. 이 quadrature는 directed interval certificate가 아니다. 여섯 배경(physical q=0,±.005,±.01와 SameH+.01), 두 grid1024/2048, case당67구간을 사용했다. 구간에는 nominal deltaL=1e-14,1e-12,1e-10,1e-8,1e-6,1e-4,.005, knot straddles 및 서로 이웃한 representable a가 포함된다.

| N | 실제 dt 최대 상대차 | 실제 db 최대 상대차 |
|---:|---:|---:|
|1024|4.32886170e-14|4.30962618e-14|
|2048|1.75139339e-15|1.66904620e-15|

총804행이 모두 기존 component1e-9 비교 기준 안이다. 관측 최대가 해석적 uniform bound보다 훨씬 작지만, 샘플 최대를 전체영역 상계로 대체하지 않는다. 실제 중단 입력에서 새 dt는844944.3803639702s이고65자리 기준은844944.380363970140...s다. 이전 stable primitive도 이미 성공한 점을 함께 기록했다. 과거 direct subtraction 값을 다시 만들려고 native suite를 재실행하지 않았다.

기본20tests 후, 후보 table의 public background reference 자체를 교체하면 이미 계산한 coefficient와 다른 model이 결합될 수 있음을 발견했다. 새 behavior assertion이 실패하는 것을 확인하고 public binding을 read-only property로 바꾸어 최종21tests가 통과했다. 입력 model은 기존 frozen dataclass이며 numerical formula 변경은 없다. Private Python internals를 임의 변경하는 reflective caller까지 보호하는 보안 경계라는 주장은 하지 않는다.

실제 실행: unit tests21개,804 local quadrature checks,3072 exact rational knot-width comparisons, cloud symbolic2calls, local Wolfram15.0.0+xTensor1.3.0 exact3zeros. Production REC/REI solver0회, canonical source/STATE/DAG/process 변경0, whole-driver performance 측정0이다. Native subagents와 외부 독립 agent review는 NOT_RUN이다. Roundoff/source/trajectory accuracy와 본 bound를 섞지 않는다.

### 최신 연구의 재사용

HE17 R7의 실제 compact result(f5d9d334...)를 읽었다. 같은 셀을 나누어도 incoming gas/photon error를 버리지 않는다는 구조를 재사용하고, 그 warm P01의 수치 반경은 본 cold background에 이식하지 않았다. 그 스레드가 공급한 xe/Ye floor patch와 HH source_pair_guard도 중복 구현하지 않는다. 이전 REC/FA common-clock 결과는 어느 사건을 비교하는가의 정의로 유지하되, 현재 positive rate integral의 합산 상계는 다른 수학적 대상임을 명시한다.

### Supplier 전이와 남은 정확한 작업

`REC_BG_POSITIVE_INTERVAL_SUPPLIER`를 READY_FOR_OWNER_CONTRACT로 둔다. 작성된 oracle와 BI-03–BI-13, 실제804행 및 guard/limits가 receiver의 별도 interval-interface 계약에 바로 입력될 수 있다. 이것은 실제 생산 table HOLD를 해제한 것이 아니다.

다음 owner 작업은 기존 cache-only 계약을 수정해 섞는 것이 아니라 새 numerical identity의 interval(a1,a2)->(dt,db) interface를 지정하고, tentative의 event dt, geometric db, 누적 출력 clock 및 rate/source 샘플링을 일관되게 연결하는 것이다. Legacy의 누적 t를 차분하는 call-site가 남으면 이 supplier만으로 문제는 해결되지 않는다. 단순 exact-cache integration은 별도로 계속할 수 있다.

Native 통합에서는 같은 supplied endpoints, 원 gate, finite overlap/step controls와 full numerical state·energy/source ledger 검사를 사용한다. New method는 legacy bit preservation을 목표로 하지 않는다. 기존 history/checkpoint의 identity를 조용히 새 provider로 바꾸지 않는다. 생산 launch·allocation·fresh independent review는 해당 owner의 범위다. Full five-case/정련 데이터 의무는 그대로 남고, 이번 호출에서 R8–R10을 완료 처리하지 않는다.

## 원전·출처

[S1] D. Goldberg, What Every Computer Scientist Should Know About Floating-Point Arithmetic, ACM Computing Surveys23(1),1991; Oracle의 원문 재판: https://docs.oracle.com/cd/E19957-01/816-2464/ncg_goldberg.html . 가까운 값의 뺄셈에 앞선 평가오차가 증폭되는 일반 원리를 사용했다. 뺄셈 연산 자체가 항상 부정확하다는 주장이 아니다.

[S2] J. Burkardt, HERMITE_CUBIC original interpolation/integration library description: https://people.math.sc.edu/burkardt/c_src/hermite_cubic/hermite_cubic.html . Classical Hermite construction·integration의 기존 문헌/코드 출발점이다. 이번 source-specific bound는 본문에서 별도로 유도했으며 library code를 복사하지 않았다. SciSpace의 Hermite error papers는 discovery로만 사용했다.

[S3] P. Fleury, C. Pitrou, J.-P. Uzan, Light propagation in a homogeneous and anisotropic universe, Phys.Rev.D91,043511(2015), arXiv:1410.8473. https://arxiv.org/abs/1410.8473 . Bianchi-I conserved-momentum/geometric propagation의 문헌 맥락으로 사용하고, 현재 유한 map은 직접 미분·합성 검산했다.

문헌 최초성, calibrated atomic uncertainty 또는 실제 관측 EoR 결과는 주장하지 않는다. 새 수치표와 검사 기록은 이 증보에 있으며, 기존 이론 전용 I–VII dossier를 runtime 표로 덮어쓰지 않았다.
