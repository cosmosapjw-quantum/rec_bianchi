# T4 He singlet source-to-transport interface closure

## 0. 판정

이번 T4의 목적은 새로운 원자율을 계산하는 것이 아니라, 이미 선택된 He I singlet local collision sources를 Bianchi Einstein–Boltzmann transport에 넣을 때 필요한 frame, clock, measure, reverse process, event ledger를 하나의 비순환 인터페이스로 닫는 것이다.

판정은

`THEORY_INTERFACE_CLOSED_WITH_EXPLICIT_DATA_GAPS__NO_HISTORY_RUN__NO_NUMERICAL_GATE_PROMOTION`

이다. 이는 source formula와 adapter가 implementation-ready라는 의미이며, full He recombination physics가 완비됐다는 의미가 아니다.

## 1. 공통 물질계 상태와 광자 측도

Metric은 `(-,+,+,+)`이고 물질/He 공통 rest congruence를 `u_m^a`라 둔다. `U_m^a=c u_m^a`, `D_m=U_m^a nabla_a`, `theta_U=nabla_a U_m^a`이다. `n_g,n_S,n_+,n_e`와 `W_P`는 material proper density이다.

광자 occupation은 material physical screen의 2x2 Hermitian PSD matrix `F(E,e)`이고

`a_gamma=(h_P c)^(-3)`,

`dn_gamma=a_gamma E^2 tr(F) dE dOmega`,

`tr I_2=2`이다. 편광 degeneracy를 측도에 다시 곱하지 않는다.

P-state는 real Cartesian orbital basis의 3x3 matrix `W_P>=0`, `tr W_P=n_P`로 유지한다. 584 line, IR line, P bound-free가 모두 같은 `W_P`를 사용한다. S는 IR, S bound-free, two-photon에 같은 scalar `n_S`를 사용한다.

## 2. 선택된 다섯 microscopic event channel

Channel order는

`(584, IR, Pbf, Sbf, 2gamma)`

이다.

### 2.1 P -> g 584 bound-bound

WU29의 bound-bound matrix formula에 lower density `n_g`, upper matrix `W_P`, transition energy `Delta_P`, Einstein coefficient `A_584`를 넣는다.

Sharp-line distribution을 `b_584(E)=3 A_584 delta_D(E-Delta_P)/(8 pi)`로 쓴다. `H=I_2+F`이면

`B_584 = integral b_584 [ n_g V F V^T - {V H V^T,W_P}/2 ] dE dOmega`,

`J_584 = b_584 [ {H,V^T W_P V}/2 - n_g F ]`,

`C_584=J_584/(a_gamma E^2)`,

`R_584=integral tr J_584=-tr B_584`.

Positive `R_584`는 net P->g이다.

### 2.2 P <-> S IR bound-bound

동일식에서 lower `n_S`, energy `epsilon_IR`, coefficient `A_IR`를 사용한다.

`B_IR = integral b_IR [ n_S V F V^T - {V H V^T,W_P}/2 ] dE dOmega`,

`J_IR = b_IR [ {H,V^T W_P V}/2 - n_S F ]`,

`C_IR=J_IR/(a_gamma E^2)`,

`R_IR=integral tr J_IR=-tr B_IR`.

Positive `R_IR`는 net P->S이다.

### 2.3 P bound-free

`Phi(T_m)=[m_e k_B T_m/(2 pi hbar^2)]^(3/2)`와

`eta_P(E)=n_+ n_e exp[-(E-chi_P)/(k_B T_m)]/(4 Phi)`

를 사용한다. WU28의 inclusive orbital map은

`T_E[X]=(3 sigma_s-3 sigma_d/5)X+(9 sigma_d/10)X^T+(9 sigma_d/10)tr(X) I_3`.

`J_F=V F^T V^T`, `J_H=V(I_2+F)^T V^T`,
`K_F=T_E[J_F]`, `K_W=V^T T_E[W_P^T]V`이면

`B_P=c a_gamma integral E^2 [ eta_P T_E[J_H] - {K_F,W_P}/2 ] dE dOmega`,

`C_Pbf=c [3 eta_P sigma_tot (I_2+F) - {F,K_W}/2]`.

Signed net ionization spectral density와 event rate는

`j_P=-a_gamma E^2 tr C_Pbf`,

`R_P=integral j_P dE dOmega=-tr B_P`.

Positive `R_P`는 ionization, negative `R_P`는 radiative capture이다.

### 2.4 S bound-free

`eta_S(E)=n_+ n_e exp[-(E-chi_S)/(k_B T_m)]/(4 Phi)`이고

`C_Sbf=c sigma_S(E) [eta_S(I_2+F)-n_S F]`,

`j_S=-a_gamma E^2 tr C_Sbf`,

`R_S=integral j_S dE dOmega`.

### 2.5 S <-> g two-photon

`Delta=Delta_S`, `E_1=Delta y`, `E_2=Delta(1-y)`를 material frame에서 정의한다. 두 screen 사이의 real-basis adapter를 `T_12=V_1^T V_2`로 두고 `H_i=I_2+F_i`라 하면

`M_12=(n_S/2){H_1,T_12 H_2^T T_12^dagger}-(n_g/2){F_1,T_12 F_2^T T_12^dagger}`.

`g_ang=3/(64 pi^2)`이고

`C_2g(E_1,e_1)=w(y)/(a_gamma E_1^2 Delta) g_ang integral M_12 dOmega_2`,

`R_2g=(1/2) integral w(y)dy g_ang integral tr M_12 dOmega_1 dOmega_2`.

원자 event에는 unordered pair factor 1/2가 있지만 one-photon marginal source는 두 tagged photons를 세므로 추가 1/2를 넣지 않는다.

## 3. retained atomic equations

선택한 subsystem에서

`(D_m+theta_U)n_g = R_584 + R_2g`,

`(D_m+theta_U)n_S = R_IR - R_S - R_2g`,

`(D_m+theta_U)W_P = B_584+B_IR+B_P`,

`(D_m+theta_U)n_+ = R_P+R_S`,

`(D_m+theta_U)n_e|He = R_P+R_S`.

Photon occupation collision source는

`C_He=C_584+C_IR+C_Pbf+C_Sbf+C_2g`.

Thomson, H continuum, 다른 He line/source가 존재하면 같은 photon RHS에 각 source를 한 번씩 더하고 대응 species/energy ledger도 함께 확장한다.

## 4. material frame에서 Bianchi normal tetrad로의 exact clock adapter

Bianchi normal observer를 `n^a`, material congruence를

`u_m^a=gamma_m(n^a+beta_m^a)`

로 둔다. Normal frame photon은

`p^a=(E_n/c)(n^a+e_n^a)`

로 쓴다. Material measured photon energy는

`E_m=-c u_m.p = D_mray E_n`,

`D_mray=gamma_m(1-beta_m.e_n)>0`.

Photon worldline의 두 local clock은

`dt_m=-u_m.dx/c`, `dt_n=-n.dx/c`

이므로

`dt_m/dt_n=D_mray`.

따라서 material ray-clock second당 collision source를 `C_t^(m)`라고 하면 normal proper-time RHS는

`C_t^(n)(E_n,e_n) = D_mray * B_(m->n)[ C_t^(m)(E_m,e_m) ]`,

여기서 `B_(m->n)`은 기존 BASS finite photon boost의 screen-component map이다. 새 Jones/sign convention을 만들지 않는다.

Normal length parameter `s_n=c t_n`을 쓰는 transport에서는

`C_len^(n)=(D_mray/c) B_(m->n)[C_t^(m)]`.

Comoving limit `beta_m=0`에서는 `D_mray=1`이고 WU29의 `C_len=C_t/c`를 회복한다.

### 4.1 atomic population clock은 다른 factor이다

Homogeneous scalar proper density에 대해

`D_m n = gamma_m d n/dt_n`.

따라서

`dn/dt_n=(R-theta_U n)/gamma_m`.

`W_P` collision block도 normal coordinate time에서는 `B/gamma_m`가 된다. Orbital basis rotation/connection은 collision B에 넣지 않고 inherited LHS transport connection에서 처리한다.

즉 photon collision의 `gamma(1-beta.e)`와 atom worldline source의 `1/gamma`는 서로 다른 clock conversion이다. 하나의 tilt factor로 통합하지 않는다.

## 5. energy support는 항상 material frame에서 판정

Atomic energy, threshold, line resonance는 atom/material rest frame scalar input이다.

### Bound-bound line

Material sharp line `delta(E_m-epsilon)`는 normal coordinates에서 direction-dependent support

`E_n=epsilon/D_mray(e_n)`

를 가진다. 고정 direction에서

`delta(D E_n-epsilon)=D^(-1) delta(E_n-epsilon/D)`.

따라서 normal-frame grid에서 모든 방향에 동일한 `E_n=epsilon` line을 넣으면 tilt adapter를 위반한다. 실제 finite-bin/profile implementation은 material-frame line source를 적분한 뒤 기존 boost adapter로 전달해야 한다.

### Bound-free

Threshold는 `E_m>=chi_i`, atomic table coordinate는 `q=(E_m-chi_i)/Ry`이다. Normal frame에서는 threshold와 table coverage가 방향 의존적으로

`E_n>=chi_i/D_mray(e_n)`

로 보인다. Cross section lookup은 항상 먼저 `E_m=D E_n`을 만든 뒤 수행한다.

### Two-photon

두 광자의 material energy constraint는

`E_1m+E_2m=Delta_S`.

Normal frame의 서로 다른 ray direction에서는

`D_1 E_1n + D_2 E_2n = Delta_S`.

일반적으로 `D_1 != D_2`이므로 `E_1n+E_2n=Delta_S`를 강제하면 안 된다. Bose factors와 partner lookup은 동일 material frame에서 평가한다.

## 6. screen, coherency, orbital frame

`F`는 dimensionless occupation/coherency이다. 동일 물리 screen에 대한 component map은 기존 BASS photon boost/screen adapter를 사용한다. `F_m=B_(n->m)[F_n]`로 material frame 값을 얻고 collision을 계산한 뒤 inverse map으로 source를 돌린다.

Photon `F`의 pointwise boost에 별도의 `E^3` Jacobian을 임의로 곱하지 않는다. Solver가 occupation 대신 spectral coherency/intensity `J_E`를 보관한다면 기존 invariant `E^{-3}J_E` adapter를 통해서만 변환한다.

`W_P`는 photon screen 2-space가 아니라 material orbital 3-space이다. Screen boost를 `W_P`에 적용하지 않는다. Material spatial triad representation이 바뀌면 기존 3D frame-rotation connection을 사용한다.

## 7. electron frame assumption의 firewall

현재 bound-free inverse coefficient `eta_i`는 isotropic, nondegenerate Maxwell electrons가 atom/material rest frame에 있다는 가정 아래 유도됐다. 따라서 T4 baseline closure는

`u_e=u_He=u_m`

을 요구한다.

만약 `u_e != u_He`이면 electron distribution은 He rest frame에서 anisotropic해진다. 이때 현재 scalar Maxwell `eta_i`를 photon boost만 붙여 사용하면 안 된다. Differential electron kernel 또는 재유도된 boosted electron integral이 필요하다. 이 branch는 `DEFERRED_SPECIES_DRIFT_PHYSICS`이다.

Electron-rest-frame Thomson collision은 별도 kernel이며 자신의 finite boost adapter를 유지한다. Bound-free inverse와 Thomson의 rest frame을 같은 식이라고 합치지 않는다.

## 8. normal-frame LTE는 anisotropic해 보여도 collision zero이다

Material frame에서 common temperature T와 Planck/Boltzmann/Saha 상태가 각 microscopic source를 pointwise 0으로 만든다고 하자.

Normal frame에서는 isotropic material Planck occupation이

`F_n(E_n,e_n) = [exp(D_mray E_n/(k_B T))-1]^{-1} I_2`

로 보이며 direction-dependent effective temperature `T_eff(e_n)=T/D_mray`를 가진다. 그러나 collision source는

`C_n=D_mray B_(m->n)[0]=0`.

따라서 tilted Bianchi normal frame에서 LTE를 검사할 때 normal-frame radiation을 억지로 isotropic Planck으로 리셋할 필요가 없다. 올바른 boosted equilibrium이 사용되면 detailed balance는 frame-covariantly 유지된다.

## 9. implementation contract

한 collision evaluation은 다음 순서를 따른다.

1. normal phase-space point `(E_n,e_n,F_n)`과 material tilt를 읽는다.
2. 기존 finite boost로 `(E_m,e_m,F_m)`을 얻는다.
3. material-frame atom/electron proper densities와 `W_P`, `T_m`을 읽는다.
4. atomic data coverage를 `E_m`, 또는 pair의 material `y`에서 판정한다.
5. UNKNOWN coverage면 0을 반환하지 말고 explicit missing-domain state를 반환한다.
6. represented channel에 대해 material `B`, `R`, `C_t`, thermal/force ledger를 계산한다.
7. photon source만 `D_mray B_(m->n)`로 normal-time source로 변환한다.
8. atom proper-density ODE가 normal time이면 collision source를 `1/gamma_m`로 변환한다.
9. energy-momentum은 material-frame four-force로 조립한 뒤 four-vector boost를 사용한다.
10. Liouville redshift/screen rotation을 collision heat나 atomic rate에 다시 넣지 않는다.

이 순서가 T4의 canonical source-to-transport interface이다.

## 11. Dossier II/III direct readback reconciliation

T4 작성 후 Dossier II/III의 해당 절을 Dropbox 원문 추출로 다시 읽었다. Dossier II Eq. (115)–(119)은 electron/material-frame analogue에 대해

`D_e=gamma_e(1-beta_e.e)`, `E_e=D_e E_n`,

invariant affine source에서 frame-rate를 나누면

`C_n = D_e B^{-1} C_e B`,

그리고 screen coherency는 `F_e=T F_n T^T`, solid angle은 `dOmega_e=D_e^{-2}dOmega_n`이라고 직접 적고 있다. 따라서 T4의 abstract `B_(m->n)` 표기는 Dossier II의 `B^{-1}(.)B` component map을 의미한다.

또한 Dossier II는 number- 및 energy-weighted angular carrier가 screen transport 외에 각각 Doppler power를 획득하며 이것이 collision-rate factor를 대체하지 않는다고 명시한다. 따라서 pointwise occupation `F`에 ad hoc Jacobian을 넣지 않는 것과, normal-frame moment 적분에서 올바른 transformed measure/carrier를 쓰는 것을 구별한다.

Dossier III Eq. (65)–(68)은 material proper-volume/proper-time source `R_A`에 대해 `U^a nabla_a n_A+theta_U n_A=R_A`를 사용하고, tilted Bianchi I에서 `d(a^3 gamma n_A)/dt=a^3 R_A`를 준다. 이는 T4의 atomic proper-density normal-time adapter와 정확히 일치한다.

따라서 photon ray-clock Doppler factor와 material proper-density worldline factor의 구별은 새 convention이 아니라 기존 Dossier의 두 서로 다른 변환을 한 인터페이스에 함께 명시한 것이다.
