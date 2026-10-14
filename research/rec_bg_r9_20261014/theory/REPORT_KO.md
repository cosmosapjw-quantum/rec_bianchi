# REC-BG-R9: 양의 유한구간 시각·전단 적분과 광자 사상의 오차 계약

**선택 단계:** 이론 R9 (정식 결과 및 코드 접속). **작성일:** 2026-10-14, Asia/Seoul. **전체 R10:** 미실행. **이번 단계의 목적:** R7B의 구성적 정리와 R8의 실제 저장 accepted-step 진단을 하나의 finite-interval theory/native input contract에 정리하고, 최신 BASS I–VII 권의 정의와 연결한다. 생산 REI source, 실행, 기존 과학 claim 및 원본 dossier ZIP은 수정하지 않았다.

## 근거와 authority

기준은 6,493,949-byte `BASS_Anisotropy_Dossiers_20261014.zip` (이전 확인 SHA256 `797ed640f999546f2e92b7a3ab0afeb3c78fa19a6c6958766b1f70d3f2f97d75`). 2026-10-14에 백업된 실제 Contents.md를 확인했다. 직접 연결되는 이론 위치는 **제II권 §2.2(사건·clock conversion), §2.6(편광된 null transport), 제VI권 §6.3(적색편이), §6.13(유한 시간 propagation error), 제VII권 §7.12–7.13(양의 적분과 결합 오차)**다. 원 archived volume에 이번 R9를 덮어써 출판 완료로 표시하지 않는다. 새 fragment `R9_DOSSIER_SUPPLEMENT.tex`는 원권에 삽입할 때 검토해야 하는 additive supplement다.

R7B 원 이론: `REC_BG_INCREMENT_R7B_20261014_COMPLETE.zip` SHA256 `992c9552f0045e446795c5c7f2575f5f27f4187ecf6f16684a7ab16214e2dc71`. R8 실험 및 판정: `REC_BG_R8_20261014_COMPLETE.zip` SHA256 `67c230734575ea7bbf74ae7e56c7f2ff84800d71e976a2c8da7173cfe315d211`. Git 공개 전 단계: REC PR84 `0e9e2e0ad56a5b7296de8929b0544647409cbed3`. R9 작성 중 REI PR117의 확인된 HEAD `750b78705beff198b4db4d69b8f07428ac06a64e`, 원 AX07 조건부 완료, AX08 진행/half-minus 부분 종료, AX11/12 미실행. `HALF_MINUS_TERMINAL_PLUS_PRELAUNCH_HOLD_001.json`에 plus prelaunch worker HOLD 및 새 solver0회가 기록됐다. 완전 signed family나 empirical source/IC convergence로 승격하지 않는다.

## 정의·부호·물리적 범위

Metric signature는 $(-,+,+,+)$, 정상계의 $t$는 **proper seconds**이며 $c$는 시간계량에서 명시한다. $a$ 무차원, $b$ 무차원, $s=\dot b$와 $H=\dot a/a$는 $\mathrm s^{-1}$. $c,\hbar,k_B$를 전역으로 1로 두지 않는다.

\[
 ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
 \quad \sigma^i{}_{j}=\operatorname{diag}(-s,-s,2s).\tag{R9-G01}
\]

고정된 prescribed, normal-comoving LRS Bianchi I 배경의 $a_r=1/21$, $a_e=0.2$, $L=\ln(a/a_r)$,
\[
 H_F^2=H_0^2(\Omega_m a^{-3}+\Omega_r a^{-4}+\Omega_\Lambda),
 \quad s=qH_F(a_r)e^{-3L}, \quad
 H^2=S(L)=\sum_{p\in\{0,3,4,6\}}C_pe^{-pL},\ C_p\ge0,\ S>0.
 \tag{R9-G02}
\]

`PhysicalDensityFixed`: $C_6=s_r^2$. `SameHDiagnostic`: $C_6=0$이지만 $s$는 유지하는 반사실적 진단 family. $q$의 부호는 $s,\Delta b$의 부호이고 $H,F,\Delta t$는 이 source family에서 $q$에 대해 짝수다. 지금 결과는 양의 $C_p$를 갖는 fixed background only이고, 기계적인 실제 GR backreaction이나 독립적인 편광 photon feedback을 반영한 동역학적 Bianchi evolution의 정리가 아니다.

## R9 정리: 양의 유한구간 증분

$f(L)=F(L)=S(L)^{-1/2}>0$로 쓰고 양의 weights $w_p=C_pe^{-pL}/S$와 $m_k=\sum p^kw_p$를 정의한다. $\sum w_p=1$과 $p\le6$에서 $F'/F=m_1/2\in[0,3]$를 얻는다. 직접 미분한
\[
 \frac{F^{(4)}}F=\frac{105m_1^4-180m_1^2m_2+36m_2^2+48m_1m_3-8m_4}{16}
\tag{R9-T01}
\]
으로부터 $|F^{(4)}|\le30537F$다. 길이 $h$인 cell에서 정확한 endpoint $F,F'$에 대한 cubic Hermite 다항식 $P$라 하면 표준 Hermite remainder와 $F_{\max}/F_{\min}\le e^{3h}$로
\[
 \left|\frac{P-F}{F}\right|\le\epsilon_h,
 \quad \epsilon_h=\frac{30537}{384}e^{3h}h^4.
\tag{R9-T02}
\]

모든 cell의 **부분구간** $I$에서
\[
 \Delta t_I=\int_I F\,dL>0,\quad
 \Delta b_I=\int_I sF\,dL,\quad
 \widehat{\Delta t}_I=\int_I P\,dL,\quad
 \widehat{\Delta b}_I=\int_I sP\,dL.
\tag{R9-T03}
\]

$\epsilon_h<1$이고 $s$가 $I$에서 한 부호이므로
\[
 \left|\frac{\widehat{\Delta t}_I}{\Delta t_I}-1\right|\le\epsilon_h,
 \qquad
 \left|\frac{\widehat{\Delta b}_I}{\Delta b_I}-1\right|\le\epsilon_h\ (q\ne0).
\tag{R9-T04}
\]

$q=0$에서는 $\Delta b=\widehat{\Delta b}=0$을 정확히 사용하며 상대오차를 정의하지 않는다. 이 상대상계는 부분구간의 길이에 의한 나눗셈을 포함하지 않는다. **이것은 정확한 node/derivative를 가진 이상적 수학적 다항식의 정리이지 binary64 구현에 대한 인증이 아니다.**

노드값 절대오차 $e_F$와 도함수 절대오차 $e_{F'}$가 알려져 있으면 Hermite basis에서 $|\widetilde P-P|\le e_F+h e_{F'}/4$다. $\alpha_I=\epsilon_h+(e_F+h e_{F'}/4)/(\inf_I F)$로 정의하고, **기계적 로컬 적분값과 다항식의 정확한 적분값의 차**를 그 다항식 적분의 상대오차 $\eta_{\rm eval}$로 제한하면, 양의 적분에 대해
\[
 \boxed{\eta_I\le\alpha_I+(1+\alpha_I)\eta_{\rm eval}.}
\tag{R9-T05}
\]
이는 두 단계의 상대오차를 합성한 보수적 상계다. 교차항 $\alpha_I\eta_{\rm eval}$을 임의로 삭제하면 엄밀한 상계가 아니다. 별도 수치인증 없이 $e_F=e_{F'}=\eta_{\rm eval}=0$으로 선언하지 않는다. $N$개의 계산된 양의 시간증분에 공통 상대상계 $\eta<1$가 있고 순차 binary64 합산이 통상적 모델을 만족하면
\[
 \frac{|\widehat t_N-t_N|}{t_N}\le\eta+(1+\eta)\gamma_{N-1},\quad
 \gamma_{N-1}=\frac{(N-1)2^{-53}}{1-(N-1)2^{-53}}.
\tag{R9-T06}
\]

## Native computational form: 로컬 다항식과 지수 moment

한 cell $[L_j,L_j+h]$의 정규화 좌표 $u=(L-L_j)/h$, $P(u)=c_0+c_1u+c_2u^2+c_3u^3$를 둔다. 실제 supplied binary64 $a_1<a_2$로 폭을 $\Delta L=\log1p((a_2-a_1)/a_1)$로 만들고, cell을 가로지르면 실제 매듭에서 분할한다. 각 구간을 $u\to u+v$라 쓰고
\[
 A_0=P(u),\quad A_1=vP'(u),\quad A_2=v^2(c_2+3c_3u),\quad A_3=v^3c_3.
\]

그 구간 적분의 **누적 시각값 뺄셈이 없는 exact-polynomial 계산식**은
\[
 \boxed{\Delta t=hv\sum_{k=0}^3\frac{A_k}{k+1},\qquad
 \Delta b=s(L_1)hv\sum_{k=0}^3 A_k M_k(3hv)},
 \quad M_k(z)=\int_0^1y^ke^{-zy}dy
 =\sum_{j=0}^{\infty}\frac{(-z)^j}{j!(k+j+1)}.
\tag{R9-N01}
\]

이 식은 $s(L)$를 exact exponential로 유지하여 $\Delta t$와 $\Delta b$를 동일한 $P$에서 얻는다. 짧은 $hv$에서 `M_k`의 작은 $z$ 급수를 사용해 취소를 피한다. 증명과 수치 구현을 구분한다: 유한 자른 급수·node 연산·합산의 실제 roundoff는 별도다. 코드 `code/interval_reference.py`는 이 식의 소규모 재현 오라클이며, 표준 crate의 일부가 아니고 Rust native solver 수정을 수행하지 않는다. 값의 부호·단위·양의 증분·$q\mapsto-q$ parity·동일 사건 출력이 interface acceptance에 필요하다.

## 새 광자 finite-map Lipschitz 상계

초기 local null 방향 cosine $\mu\in[-1,1]$에서
\[
 R^2=e^{2B}(1-\mu^2)+e^{-4B}\mu^2,\quad
 \mu'=\frac{\mu e^{-2B}}R,\quad
 \frac{E_2}{E_1}=e^{-\Delta L}R,\quad
 \frac{d\Omega_2}{d\Omega_1}=R^{-3},\quad B=\Delta b.
\tag{R9-P01}
\]

직접 미분과 $|\mu'|\le1$로
\[
 \partial_B\ln R=1-3{\mu'}^2,\quad
 \partial_B\mu'=-3\mu'(1-{\mu'}^2),\quad
 \partial_B\ln(d\Omega_2/d\Omega_1)=-3(1-3{\mu'}^2).
\tag{R9-P02}
\]

같은 $\Delta L$을 가진 두 유한 구간 변수 $B,\widetilde B$에 대해 평균값 정리로
\[
 \boxed{\left|\ln\frac{\widetilde E_2/E_1}{E_2/E_1}\right|\le2|\widetilde B-B|,\quad
 |\widetilde\mu'-\mu'|\le\frac2{\sqrt3}|\widetilde B-B|,\quad
 \left|\ln\frac{\widetilde J}{J}\right|\le6|\widetilde B-B|.}
\tag{R9-P03}
\]

이는 **유한 $B$에 대해 성립하는 기하·각도 사상 오차**이고, collision, polarized spectral energy redistribution, $x_e$ 진화 또는 광학깊이 전체의 충분 상계가 아니다. $\Delta L$도 바뀐다면 에너지의 로그 오차에 $|\delta\Delta L|$를 추가해야 한다. Wolfram15.0.1에서 R9-P02 및 Jacobian과 Hermite full-cell 적분식의 잔차 0을 확인했다. 실제 xTensor 1.3.0의 기존 R7B/R8 접선성·current product 검산은 재사용했으며, **이번 새 projector xAct 실행은 일회성 Wolfram `-code`에서 Global symbol shadow가 관측되어 PASS로 채택하지 않았다.** Wolfram 클라우드에서는 xTensor가 설치되지 않았음을 확인했다. 독립 xAct 성분 계산이 없다는 사실을 새 증거처럼 기재하지 않는다.

## 결합 상태·source 및 관측량의 적용범위

바리온수 보존 $\nabla_a(n_HU^a)=0$에서 $n_H=n_{H,r}(a_r/a)^3$는 같은 scale factor의 background dilution이지만, 이온분율과 thermal $w$는 실제 source와 clock을 따라 진화한다. 소스가 $dY/dt=S(Y,t;\text{radiation})$를 사용한다면 새 increment에 의한 $\delta Y$는 source Jacobian/variation equation 또는 empirical paired refinement로 검증해야 한다.

옵션 observer optical-depth를 나중에 계산할 경우 $\tau=\sigma_T c\int n_H x_eF\,dL$이다. $F\mapsto F+\delta F$, $x_e\mapsto x_e+\delta x_e$에서는
\[
 \delta(n_H Fx_e)=n_H\left(F\delta x_e+x_e\delta F+\delta F\delta x_e\right).
\tag{R9-P04}
\]
따라서 $\delta x_e=0$인 **fixed-history readout**에 대해서만 $F$의 양의 상대오차가 $\tau$ 적분으로 바로 전달된다. 실제 기체·광자 결합 진화의 별도 조건은 반드시 남긴다. Tau/visibility는 사용자가 고정한 abundance-first goal의 차단 선행조건이 아니다.

## 실제 저장 자료와 연동 판정

R8에서 관측한 저장된 102개 accepted-step은 ZERO 40개, PLUS/MINUS 31개씩이며, 24개에서 local clock 상대차가 1e-8을 초과했다. 최대 차이는 signed PLUS #100에서 $-1.81900864\times10^{-8}$, log 차분만의 예상값 $-1.81898935\times10^{-8}$였다. 차이 $\simeq-1.93\times10^{-13}$는 cancellation 원인 설명의 강한 증거이지 전체 IVP 오차는 아니다. R9에서는 그 파일을 다시 처리하지 않았다. Source identity와 R8 결과를 입력 contract에 기록했다.

최신 REI 공개 HEAD `750b78705beff198b4db4d69b8f07428ac06a64e`의 `HALF_MINUS_TERMINAL_PLUS_PRELAUNCH_HOLD_001.json`에서 HALF_MINUS의 accepted 200000 scoped partial result가 확인됐고, PLUS prelaunch는 worker/children HOLD로 실제 새 solver 0회이며 독립 회복 lane이 존재한다. 이 blocker는 이번 clock 법칙 자체의 실패가 아니며, 해당 dispatcher를 재작성·재시작하거나 새로운 READY 과학 실행으로 승격하지 않는다. BASS_HE PR53에서 이미 구현한 source-pair guard, electron floor, knot-union reducer도 재구현하지 않았다.

## 결론 및 통합 선택

- **R9 완료 대상**: 정확한 물리 변수 정의 → R7B source-specific Hermite 증명 → 짧은 구간 dt/db 계산식 → 유한 null map 오차 상계 → native 입력·출력·검증 계약 및 코드 연결.
- **이론 근거 상태**: R9-T01–T04 / P01–P04 `DERIVED`, Wolfram 기호 검사 `SYMBOLIC_CHECKED`(xAct 신규 projector는 `UNVERIFIED`), Python 참조 코드는 변경 범위에 대해 `UNIT_TESTED`.
- **실제 production state**: `NOT_EXECUTED`. REI 기존 `HOLD_SHORT_STEP_SUBTRACTION`과 AX11/12 pending을 임의로 닫지 않는다.
- **채택 순위**: 이미 component PASS인 기존 stable polynomial increment의 유한 native-step 통합 검사를 우선. Positive-rate-Hermite는 이론적 uniform bound를 가진 대안으로 분리 유지. 캐시 최적화는 bit-preserving lane, 본 변경은 new numerical identity.
- **정확한 최소 후속 행동**: 새로운 native 변경 권한과 소유권이 확보되면 all-callsite inventory 후 두 기하 증분·photon/source/ledger overlap을 실제 source/config 단위와 비교하고, 유한 refinement와 새 binary/metadata identity를 보존한다. 해당 과학 owner의 실행 허가 없이 benchmark/trajectory를 시작하지 않는다.

### 핵심 문헌

1. Fleury, Pitrou & Uzan, *Light propagation in a homogeneous and anisotropic universe*, PRD **91** 043511 (2015), https://arxiv.org/abs/1410.8473 . 기하학적 null momentum 보존·적색편이의 기존 맥락.
2. Fritsch & Carlson, *Monotone Piecewise Cubic Interpolation*, SIAM J. Numer. Anal. **17** 238 (1980), https://doi.org/10.1137/0717021 . Hermite 다항식과 shape preserving 조건의 기본 문헌. 현재 source-specific K4는 R7B 직접 유도.
3. Dougherty, Edelman & Hyman, *Nonnegativity-, monotonicity-, or convexity-preserving cubic and quintic Hermite interpolation*, Math. Comp. **52** (1989) 471, https://www.ams.org/journals/mcom/1989-52-186/S0025-5718-1989-0962209-1/ . 근사의 positivity/monotonicity를 별도로 검토할 때의 문헌.
4. Higham, *Accuracy and Stability of Numerical Algorithms*, SIAM 2nd ed. (2002), https://doi.org/10.1137/1.9780898718027 . 부동소수점 $\gamma_n$와 오차 누적의 일반 근거.
5. Viswanath, *Global errors of numerical ODE solvers and Lyapunov's theory of stability*, IMA J. Numer. Anal. **21** (2001) 387, https://doi.org/10.1093/imanum/21.1.387 . local error에서 nonlinear IVP global accuracy로 자동 승격할 수 없다는 맥락.

새로운 논문 최초성·외부 peer review·완전한 GR+RT solver는 주장하지 않는다.
