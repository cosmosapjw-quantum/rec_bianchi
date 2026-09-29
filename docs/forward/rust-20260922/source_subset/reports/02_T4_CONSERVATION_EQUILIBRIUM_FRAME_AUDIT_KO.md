# T4 conservation, equilibrium, and frame audit

## 1. event stoichiometry

Species order `(g,S,P,He+,e,photon)`, channel order `(584,IR,Pbf,Sbf,2gamma)`에서

```text
S_event =
[ +1  0   0   0  +1 ]   g
[  0 +1   0  -1  -1 ]   S
[ -1 -1  -1   0   0 ]   P=tr W_P
[  0  0  +1  +1   0 ]   He+
[  0  0  +1  +1   0 ]   e
[ +1 +1  -1  -1  +2 ]   photon
```

He nucleus left-null vector는 `(1,1,1,1,0,0)`이고 charge bookkeeping vector는 `(0,0,0,1,-1,0)`이다. 따라서 모든 다섯 event가 He nuclei와 `He+ - e` collision source를 보존한다.

Photon-number source는

`S_Ngamma=R_584+R_IR-R_P-R_S+2R_2g`.

이는 finite phase-space box에서의 storage/boundary flux와 같지 않으며 escape probability도 아니다.

## 2. energy ledger

Atomic ground energy를 0으로 두면

`u_int=Delta_S n_S + Delta_P tr(W_P) + I_He n_+`.

Level relations은

`Delta_P=Delta_S+epsilon_IR`,
`I_He=Delta_P+chi_P=Delta_S+chi_S`.

따라서 event rates의 internal-energy source는

`P_int=-Delta_P R_584-epsilon_IR R_IR-Delta_S R_2g+chi_P R_P+chi_S R_S`.

Bound-free signed spectral density `j_i`를 쓰면

`P_gamma=Delta_P R_584+epsilon_IR R_IR+Delta_S R_2g-integral E(j_P+j_S)dE dOmega`,

`H_kin=integral[(E-chi_P)j_P+(E-chi_S)j_S]dE dOmega`.

정확히

`P_int+P_gamma+H_kin=0`.

Wolfram exact event algebra가 다섯 channel 각각에서 이 항등식을 확인했다. 첫 ledger call에서 internal changes는

`(-Delta_P,-epsilon_IR,chi_P,chi_S,-Delta_S)`

로 환원되며 photon+kinetic 항을 더하면 전부 0이었다.

## 3. four-force ledger

`S_gamma(E,e)=a_gamma E^2 C_He(E,e)`라 하면 material-frame total matter force는

`Q_m^a=-(1/c) integral E(u_m^a+e_m^a) tr S_gamma dE dOmega`,

`Q_gamma^a=-Q_m^a`.

Positive photon emission에서 `c(-u_m.Q_m)=-P_gamma`가 되어 위 scalar energy ledger와 일치한다.

Bound-bound/two-photon heavy-atom approximation에서 recoil kinetic energy를 leading order에 생략해도 momentum transfer를 0으로 만들지는 않는다. Total material force는 유지한다. Electron/ion/neutral atom 사이의 force partition은 별도 closure이다.

## 4. Planck–Boltzmann–Saha detailed balance

Common material-frame T에서

`F_eq=f_Pl(E,T) I_2`,

`n_g,eq=n_+n_e exp(I_He/kT)/(4Phi)`,

`n_S,eq=n_g,eq exp(-Delta_S/kT)`,

`W_P,eq=n_g,eq exp(-Delta_P/kT) I_3`.

### Bound-bound

`exp(-beta epsilon)[1+f_Pl(epsilon)]=f_Pl(epsilon)`이므로 584와 IR의 gain/loss bracket이 각 `E,e`에서 0이다.

### Bound-free

한 orbital bound density를 `w_i`라 두면 `eta_i(E)=w_i exp(-beta E)`이고 같은 Planck identity로 photoionization/recombination bracket이 pointwise 0이다. P map에서는 `T_E[I_3]=3 sigma_tot I_3`가 degeneracy를 일관되게 닫는다.

### Two-photon

`E_1+E_2=Delta_S`에서

`exp(-beta Delta_S)(1+f_1)(1+f_2)=f_1 f_2`.

따라서 pair integrand가 mode-pair마다 0이다.

Wolfram의 첫 two-photon substitution은 assumption 처리 때문에 `False`를 반환했다. 이것은 evidence log에서 CAS setup dead-end로 보존했다. 독립적인 exact 변수 `x=exp(beta E_1)>1`, `y=exp(beta E_2)>1`로 다시 쓴 검사는 `True`를 반환했다. Scientific authority는 대수 유도와 clean second check이다.

## 5. coverage-mask detailed-balance theorem

어떤 source channel c에 대해 forward와 reverse microscopic bracket을 동일 데이터와 동일 deterministic coverage mask `m_c(z)`에 곱한다고 하자.

LTE에서 unmasked bracket이 pointwise 0이면

`m_c(z) * 0 = 0`.

따라서 represented domain 안의 detailed balance는 임의 finite mask 아래에서도 보존된다.

그러나 이 정리는 missing domain의 비평형 source가 0이라는 뜻이 아니다. Mask 밖은 `UNKNOWN`으로 남는다.

Two-photon에서는 pair selector가 forward/reverse에 동일해야 한다. 현재 D86 band `[1/40,39/40]`는 `y <-> 1-y` 대칭이라 unordered-pair convention과 호환된다.

## 6. finite tilt와 LTE covariance

Material-frame collision operator가 `C_m=0`이면 normal-frame source는

`C_n=D_mray B_(m->n)[C_m]=0`.

따라서 detailed balance는 tilt에서 새로 맞춰야 하는 scalar rate identity가 아니다. 올바른 phase-space point, screen basis, ray clock으로 변환하면 zero source가 그대로 zero이다.

## 7. scalar and aligned limits

### Isotropic P

`W_P=n_P I_3/3`이면 P bound-free photon source는

`C_Pbf=c sigma_tot [3 eta_P(I_2+F)-n_P F]`.

이는 full aligned map의 trace-compatible scalar limit이지 aligned calculation의 대체물이 아니다.

### Isotropic bound-bound

`F=fI_2`이면

`R_IR=A_IR[n_P(1+f)-3n_S f]`

이며 584도 lower density만 `n_g`로 바꾼 동일 구조이다.

### Aligned P

584, IR, Pbf에서는 `W_P`의 3x3 alignment가 load-bearing이다. 같은 `n_P`이라도 emission angular/polarization pattern과 P photoionization hazard가 달라진다. Scalar population만으로 일반 source를 대체하지 않는다.

## 8. no-double-count checks

1. two-photon resolved `w(y)`가 atomic event rate와 photon source를 동시에 정의한다. 별도 total decay rate를 더하지 않는다.
2. 584 photon의 H/He continuum absorption은 이미 방출된 photon의 propagation collision이다. P upper-level loss에 다시 더하지 않는다.
3. IR P->S 뒤 S->g two-photon은 두 별개 physical events이다. 이를 별도 direct P->g effective reaction과 동시에 넣지 않는다.
4. WU32 이후 ECG C0 branch는 canonical D86 band를 자동 교체하지 않는다.
5. bound-free forward/reverse는 동일 cross section branch와 동일 coverage mask를 쓴다.
6. geometric redshift는 Liouville operator이다. `H_kin`에 추가하지 않는다.
7. free-electron carrier number change는 bound-free에서만 일어난다. Bound-bound/two-photon에 electron source를 만들지 않는다.

## 9. transformed angular measure and moment warning

Dossier II의 direct readback에 따라 material/electron frame solid angle은 normal frame에 대해 `dOmega_m=D_mray^{-2} dOmega_n`로 변환된다. 이 Jacobian은 occupation matrix F 자체에 곱하는 factor가 아니다. Photon number/energy moments를 normal frame에서 직접 재적분할 경우 energy differential와 solid-angle transform, screen map을 함께 사용해야 한다. 기존 Dossier의 carrier Doppler weights를 재사용하고 collision-rate factor D를 그 weights로 대체하지 않는다.

실무적으로 가장 안전한 T4 route는:
1. pointwise source를 local material phase-space coordinates에서 계산;
2. Eq. (116)형 rate+screen adapter로 normal-frame Boltzmann RHS에 변환;
3. moment/four-force가 필요하면 한 frame에서 일관된 invariant measure로 적분하고 four-vector/tensor로 변환.

이 route는 서로 다른 frame의 E, dOmega, clock factors를 부분적으로 섞는 구현을 금지한다.
