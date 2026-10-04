# PB02 source-bound rec_bianchi 이론 계약

기준일: 2026-10-04. 이 문서는 이미 게시된 REI-CHAT-PB01의 조건부 Peebles 환원을 반복 종결하지 않는다. PB01의 다음 과제인 실제 source-bound 재결합 소비자에 필요한 계수 identity, 온도 convention, line ownership, 비등방 탈출의 제한된 정리를 고정한다. 상태는 **문헌·원 코드 확인 + 조건부 직접 유도**다. 실제 실행 결과는 별도의 runtime evidence로 판정한다.

## 1. 기존 결과와 이번에 추가하는 것

선행 계약은 `rei_bianchi@67957715cf3336b89c27c1e59c33ca23098f8934`, `docs/fastest_track_chat/REI-CHAT-PB01-20261004/PEEBLES_REDUCTION_SPEC.json`이다. PB01은 순수 수소, 열적 bath, Case B, 광학적으로 두꺼운 Sobolev 탈출, 준정상 n=2 shell의 환원을 조건부로 닫았다. 읽은 현재 Case-A 재이온화 모형에는 그 level/bath/escape 구조가 없으므로 같은 production 경로가 복원되었다고 부를 수 없다.

이번 native 구현 범위는 **one-temperature**다. 아래 two-temperature 식과 point fixture는 source-reference 선행 연구이며, native entrypoint가 두 온도를 지원했다는 주장이 아니다. 이번 native 입력은 Tm≠Tr를 거부한다.

이번 추가는 (i) 공식 HYREC-2 TLA의 정확한 coefficient/constant 계약, (ii) 분리된 (T_m,T_r)에서의 상세평형, (iii) QSS closure defect의 동역학적 bound, (iv) 국소 방향 Sobolev 모형의 angular average 부호와 계수다.

## 2. Source identity와 계산 convention

HYREC-2 저자 저장소의 확인한 commit은 `09e8243d0e08edd3603a94dfbc445ae06cafe139`다. `hydrogen.c`의 `rec_TLA_dxHIIdlna`는 `Fudge=1`, `fsR=meR=1`, 추가 ionization/excitation=0으로 고정하면 이번 기준 모형이다. 원 함수의 온도 입력은 eV, 밀도는 proper cm^-3, 반환은 (dx_{{\rm HII}}/d\ln a\)이다. 프로젝트 공개 API가 Kelvin과 proper second를 받는다면 한 번만 변환한다. 고정 상수와 파일 hash는 SOURCE_LOCK 및 PB02_SOURCE_CONTRACT에 있다.

공식 논문 [Ali-Haïmoud & Hirata 2011, §IIA](https://arxiv.org/pdf/1011.3758v2)의 n=2 population convention을 채택한다. 

\[
\alpha_B(T)=4.309\times10^{-13}
\frac{(T/10^4\,\mathrm K)^{-0.6166}}{1+0.6703(T/10^4\,\mathrm K)^{0.5300}}
\quad\mathrm{cm^3\,s^{-1}}.
\]

원 코드에는 이 fit의 온도 guard와 atomic accuracy bound가 없다. 따라서 유한 regression domain과 문헌이 보증한 물리적 오차 영역은 구별한다. 본 계약의 초기 시험 영역 (100\le T_m,T_r\le10^4\,\mathrm K\)는 선택한 계산 범위이며, 이 전 영역의 fit 오차를 인증했다는 뜻이 아니다. 원 PPB 1991 논문의 전 범위 오차 확인은 미해결로 남긴다.

\[
\Phi(T)=\left(\frac{2\pi\mu_e k_BT}{h^2}\right)^{3/2},\quad
\beta_P(T_r)=\alpha_B(T_r)\Phi(T_r)e^{-\chi_2/(k_BT_r)},\quad
\beta_{\rm shell}=\beta_P/4.
\]

\(\mu_e\)는 전자–양성자 reduced mass이다. \(\chi_1=\chi_2+E_{21}\), \(E_{21}=hc/\lambda_\alpha\), \(h=2\pi\hbar\)를 같은 상수 집합 안에서 만족시킨다. 원 코드와 bit-level에 가까운 비교에는 코드의 고정 `SAHA_FACT`, `LYA_FACT`를 사용한다. 최신 CODATA 상수로 재계산한 결과와의 차이는 별도의 constant-set 차이이며 구현 오류로 섞지 않는다.

전자와 양성자의 재결합에는 \(\alpha_B(T_m)\), 흑체 광이온화에는 \(\alpha_B(T_r)\)가 들어간다. `beta=alphaB(Tm)*Phi(Tr)*...` 또는 모든 exponent를 (T_m)로 계산하는 구현은 two-temperature 계약과 다르다. 최신 확인 CAMB RECFAST 코드에는 (T_m\) convention이 남아 있어, 기본 실행을 동일 two-temperature oracle로 쓰면 안 된다. RECFAST의 경험적 fudge·Hswitch도 제거하거나 독립 모드로 라벨링한다.

## 3. 상세평형과 QSS defect를 소비자에 연결

\[
A=n_H\alpha_B(T_m)x_ex_p,\quad q=x_{1s}e^{-E_{21}/k_BT_r},\quad
D_g=(\Lambda_{2\gamma}+3R_\alpha)/4,\quad r=\beta_P/4+D_g.
\]

\[
\dot x_2=A-\frac{\beta_P}{4}x_2-D_g(x_2-4q),\qquad
\dot x_e=-A+\frac{\beta_P}{4}x_2.
\]

동일 시각의 실제 \(x_e,T_m,T_r,n_H,R_\alpha\)에서 \(x_2^*=(A+4D_gq)/r\), \(\delta=x_2-x_2^*\)라 놓으면

\[
\dot x_e=-C(A-\beta_Pq)+\frac{\beta_P}{4}\delta,
\quad C=\frac{D_g}{r},
\quad \dot\delta=-r\delta-\frac{d x_2^*}{dt}.
\]

이는 계수가 시간에 따라 바뀌어도 성립하는 대수·미분 identity다. 궤적을 따라 \(r\ge r_*>0\), \(|d x_2^*/dt|\le L\)이면

\[
|\delta(t)|\le e^{-r_*\Delta t}|\delta(t_0)|+
\frac{L}{r_*}(1-e^{-r_*\Delta t}),
\quad
|\dot x_e-\dot x_e^{\rm QSS}|\le\frac{\beta_{P,\max}}4|\delta(t)|.
\]

따라서 단순 (r/H\gg1\) 검사보다 initial-layer와 입력 변화율을 포함한 명시적 remainder를 제공할 수 있다. 다만 (L,r_*,\beta_{P,\max}\)의 유효 interval bound는 아직 계산되지 않았다. 점별 수치평가가 이 bound를 대신하지 않는다.

한 온도에서 \(B=\exp[-E_{21}/(k_BT)]\), \(S=\Phi(T)\exp[-\chi_1/(k_BT)]/n_H\)라 정의한다. 다음 두 평형은 질량 보존 closure가 다르므로 구별한다.

**Collapsed Peebles 평형**은 \(x_2\)를 핵수 보존에서 무시한 \(x_{1s}=1-x_e\), \(x_e=x_p\) 근사에서
\[
\frac{x_e^2}{1-x_e}=S
\]
를 만족한다. 이 식을 유한 \(x_2\)를 보존하는 모형의 정확한 평형으로 사용하지 않는다.

**Retained-shell 평형**은 이 유한 1s+n=2+continuum 모형의 상세평형과 정확한 핵수 보존에서
\[
x_2=4B x_{1s},\qquad \frac{x_p^2}{x_{1s}}=S,\qquad
x_{1s}+x_2+x_p=1,\quad x_e=x_p
\]
를 동시에 만족한다. 따라서
\[
x_{1s}=\frac{1-x_p}{1+4B},\qquad
\frac{x_p^2}{1-x_p}=\frac{S}{1+4B}.
\]
분모 \(1+4B\)는 retained n=2 shell의 partition contribution이다. 이는 유한 모형 안의 정확한 평형이며 무한 다준위 원자의 완전한 partition function을 의미하지 않는다. \(B\to0\) 또는 ground-population에서 shell contribution을 무시하는 극한에서 collapsed 식으로 돌아간다. 구현 검사는 두 식을 각각 해당 closure에만 적용해야 한다.

고정 원 코드 상수의 마지막 자리 반올림으로 \(\chi_2+E_{21}\)와 저장된 \(\chi_1\)이 floating point에서 미세하게 다를 수 있다. 실제 rate residual 검사에서는 \(S_{\rm rate}=\beta_P B/[n_H\alpha_B(T)]\)를 직접 써서 상세평형을 확인하고, 에너지 identity의 반올림 차이는 별도 상수 검사로 기록한다.

\(T_m\ne T_r\)에서 위 한 온도 평형을 영점으로 강제하지 않는다. 두 온도에서의 계산상 영점은 추가 \(\alpha_B(T_r)/\alpha_B(T_m)\) 비율을 가지며, 이를 열평형 Saha 상태라 부르지 않는다. \(C\)가 틀려도 한 온도 collapsed Saha 영점은 맞을 수 있으므로 독립 \(C\)-factor 검사가 필수다.

## 4. 방향 Sobolev 모형의 조건부 정리

Metric signature는 \((-,+,+,+)\). 비회전·비기울어진 geodesic gas의 proper time을 사용하고 (H=\theta/3>0\), \(\sigma^i{}_i=0\), \(n^in_i=1\)이라 한다. 국소 photon drift는

\[
\frac{d\ln\nu}{dt}=-h(\boldsymbol n),\qquad h(\boldsymbol n)=H+\sigma_{ij}n^in^j.
\]

이하에는 모든 방향 (h>0\), 일정한 국소 coefficient, line crossing 동안 작은 계수 변화와 방향 변화, isotropic unpolarized emission/populations, 정상 Sobolev transfer, negligible stimulated population correction, source/boundary의 방향 독립성을 **추가 가정**한다. 이들은 일반 Bianchi의 자동 성질이 아니다.

\[
a_S=\frac{3A_{21}\lambda_\alpha^3n_{1s}}{8\pi},\quad
\tau(\boldsymbol n)=\frac{a_S}{h(\boldsymbol n)},\quad
p(h)=\frac{1-e^{-a_S/h}}{a_S/h},\quad
R_\alpha=A_{21}\langle p(h)\rangle_\Omega.
\]

여기서 (a_S,H,\sigma_{ij},A_{21}\)의 단위는 모두 s^-1, \(\tau,p\)는 무차원이며 (R_\alpha\)는 **2p 원자 하나당** 탈출률이다. 통계적 shell의 총 ground-decay coefficient는 여전히 \((3R_\alpha+\Lambda_{2\gamma})/4\)이다.

각 방향에 uniformly \(\tau\gg1\)이면
\[
R_\alpha\longrightarrow \frac{8\pi}{3\lambda_\alpha^3n_{1s}}\langle h\rangle_{\Omega}
=\frac{8\pi H}{3\lambda_\alpha^3n_{1s}},
\]
왜냐하면 \(\langle n^in^j\rangle=\delta^{ij}/3\)이기 때문이다. 고정된 (H,n_{1s}\)에서 직접 shear 항이 사라지는 결과는 이 제한된 thick-local 모형의 정확한 angular identity다. 배경 (H\) 자체의 shear dependence, anisotropic radiation, finite line memory, tilt 등까지 사라진다는 뜻이 아니다.

이 극한의 잔차도 제한 모형 안에서 bound할 수 있다. \(h_{\max}=H+\lambda_{\max}(\sigma)\), \(\tau_{\min}=a_S/h_{\max}\)라 놓으면 양의 angular weight에 대해
\[
0\le \frac{1}{\tau_0}-\langle p\rangle
=\left\langle\frac{h}{a_S}e^{-a_S/h}\right\rangle
\le\frac{e^{-\tau_{\min}}}{\tau_0}.
\]
따라서 thick asymptote 대비 상대 오차는 \(e^{-\tau_{\min}}\) 이하이다. 이것은 국소 Sobolev 공식 내부의 정확한 bound이며, 그 공식과 실제 radiation transfer 사이의 오차를 bound하지 않는다.

Finite optical depth에서는
\[
p''(h)=-\frac{a_S}{h^3}e^{-a_S/h}<0
\quad\Rightarrow\quad
\langle p(h)\rangle\le p(\langle h\rangle)=p(H).
\]
Jensen 부등식은 임의의 양의 (h\) 분포에 성립하며, 각 quadrature는 비음수 가중치와 정확한 2차 angular moment를 갖추어야 이 비교를 보존한다.

약한 shear에 대해 \(\tau_0=a_S/H\), \(S_2=\sigma_{ij}\sigma^{ij}\)라 두면
\[
\langle(\sigma_{ij}n^in^j)^2\rangle=\frac{2S_2}{15},
\]
\[
\Delta\langle p\rangle=-\frac{\tau_0e^{-\tau_0}}{15}\frac{S_2}{H^2}
+O(\|\sigma\|^3/H^3),
\quad
\frac{\Delta\langle p\rangle}{p(H)}=-\frac{\tau_0^2e^{-\tau_0}}{15(1-e^{-\tau_0})}\frac{S_2}{H^2}
+O(\|\sigma\|^3/H^3).
\]
여기서 (S_2\)는 \(\sigma^2=\tfrac12\sigma_{ij}\sigma^{ij}\) convention과 구별한다. 일반 shear의 cubic angular moment는 영이 아니므로 오류차수를 무조건 4차라고 쓰면 안 된다. \(\sigma\to-\sigma\) 두 결과를 평균하면 odd 항을 제거하는 별도 검사로 쓸 수 있다.

\(h\le0\)가 존재하면 이 단방향 escape 계약은 거부한다. 절댓값을 넣는 임의 보정은 blueshift/re-entry와 경계 문제를 해결하지 않는다. (n_{1s}\to0\)에서는 thick limit이 무너진다. (C\)의 algebraic regularization이 그 물리 가정까지 복구하지 않는다.

## 5. 알려진 Bianchi 선행 연구의 정확한 위치

[Ng & Chu 2025, §II.2](https://arxiv.org/html/2503.14969v2)는 작은 radiation-temperature anisotropy와 isotropic pressure를 가정하고 mean expansion을 Peebles 탈출에 넣는다. 이것은 비교 가능한 제한 모형이다. 그 절의 volume-scale redshift를 각 방향 광자의 exact redshift로 사용하지 않는다. 저자 [Zenodo 코드](https://zenodo.org/records/15847891)는 metadata만 확인했으며, 내려받기·실행·license 검증을 마쳤다고 주장하지 않는다.

일반 Bianchi 확장에는 (f(\nu,\boldsymbol n,t)\), 방향별 blue-side boundary, line diffusion/time dependence 및 두 광자 absorption의 ownership이 필요하다. HYREC-2 SWIFT의 FLRW-calibrated correction table을 그대로 Bianchi 전체의 물리적 보증으로 승격할 수 없다.

## 6. 원자율·광자·열 ownership

`recombination_model_id`는 Case-A reionization과 source-bound Peebles를 별도로 식별한다. 동일 step에서 Peebles의 effective sink와 별도의 ground-state absorption/recombination recycling을 중복 적용하지 않는다. Reduced scalar mode는 Lyα·두 광자 channel을 이미 제거한 모형이므로 상세 photon spectrum이나 정확한 matter heating을 자동 산출하지 않는다. Prescribed thermal bath는 reservoir이며, scalar (x_e\) 계산만으로 닫힌 총에너지 보존을 주장하지 않는다.

후속 explicit-level 모형에서 ground energy=0 convention을 쓰면 excitation/ionization energy per H는 \(E_{21}x_2+\chi_1x_p\)이다. Lyα와 두 광자의 총 방출에너지·free-bound continuum·matter kinetic change·reservoir exchange를 함께 기록해야 한다. 이 파일은 그 spectrum partition을 새로 가정하지 않는다.

## 7. 이번 bounded loop의 acceptance

1. Native one-temperature 범위를 유지하고 Tm≠Tr 거부를 확인한다. 아래 two-temperature 검사는 독립 source-reference arithmetic으로만 분리한다. 동일 constant set에서 \(C_K=C_R\), shell elimination=scalar RHS, time/redshift/log-scale conversion을 확인한다.
2. 한 온도 detailed balance, 두 온도 beta-temperature 분리, beta factor4·escape factor3의 의도적 오류 검출을 확인한다.
3. source-bound alpha·beta·C·RHS point fixture와 matched trajectory를 구별하여 보고한다.
4. angular second/fourth moment, Jensen sign, thick limit, small-shear coefficient와 quadrature convergence를 확인한다. 이는 조건부 closure 검산이며 실제 Bianchi recombination history는 아니다.
5. production source attachment, full atomic accuracy, 구간 인증은 실제 실행한 범위만 통과시킨다. 기존 rei gate와 historical failed interval은 변경하지 않는다.

정확한 출처·버전·코드 재사용 상태는 `SOURCE_LOCK.json`, low-cost LLM 실행 계약은 `PB02_SOURCE_CONTRACT.json`을 따른다.
