# LINE01 collapsed 2p source 선택 추가문서

2026-10-23 KST. 부모 루프의 최종 선택에 대한 제한된 추가 검토다. 기존 `LINE_SOURCES.json`과 두 NIST fine-component card는 변경하지 않는다. 새 검색·과학 실행은 하지 않았다.

## 1. 실제 입력과 추가 closure

확보한 native snapshot에는 fine-\(J\) population 없이 **collapsed \(x_{2p}\)** 가 저장되어 있다. 출처는 `donor_source_reads/STORED_NATIVE_LYA_STATE.json`에 고정한 기존 snapshot이며, 원본 Git blob은 `6399b59ca3c97d6c5b1162f83f50a6677fad06ff`, source HEAD는 `df95a074730ea0d13d609cf88d448f01f4a47ef1`이다. 이는 기존 상태를 읽어 재사용하는 것으로 새 궤적 계산이 아니다. native `A2p_up/dn`은 virtual-bin diffusion 교환율이며 자발방출 \(A_{21}\)로 사용하지 않는다.

이번 **effective coincident-line** card는 다음 추가 가정을 부여한다.

- \(n_u=n_{2p}=n_{2p_{1/2}}+n_{2p_{3/2}}\), \(n_l=n_{1s}\), \(g_u/g_l=6/2=3\).
- \(n_{2p_{1/2}}=n_u/3,\ n_{2p_{3/2}}=2n_u/3\). 이 통계적 비율은 native에서 측정·저장한 값이 아니라 부여한 sublevel closure다.
- 두 성분에 정확히 같은 profile, 같은 frequency, 같은 청색 경계 \(f_+\)를 부여하고, 무편극 scalar population 및 공통 Sobolev transfer를 사용한다.
- 공통 에너지는 native 값 \(E_*=10.198714553953742\ {\rm eV}\)로 고정한다. \(\nu_*=E_*/h,\ \lambda_*=hc/E_*=2\pi\hbar c/E_*\)이며 SI에서는 eV를 J로 변환한다. 이는 native 에너지 규약의 재사용이며 NIST의 두 fine 파장을 그대로 보존하는 선택은 아니다.

[NIST H I 표](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable3.htm)의 \(A_{1/2}=6.2649\times10^8\), \(A_{3/2}=6.2648\times10^8\ {\rm s}^{-1}\)로

\[
A_*=\frac{A_{1/2}+2A_{3/2}}3
=\frac{18.7945}{3}\times10^8\ {\rm s}^{-1}
\simeq6.264833333333333\times10^8\ {\rm s}^{-1}
\]

를 정의한다. 마지막 반복 소수는 평균의 산술 표현이며 원자 데이터에 유효숫자를 더하지 않는다. NIST의 전체 \(n=2\) shell \(g_u=8\) 및 그 평균 \(A\)는 사용하지 않는다.

## 2. 선언한 모델 안에서 성립하는 집계

\(g_{1/2}=1,\ g_{3/2}=2\)이면 위 통계적 split 아래

\[
\sum_j A_j n_{u,j}=A_*n_u,\qquad
\sum_j A_j(g_j n_l-n_{u,j})=A_*(3n_l-n_u).
\]

따라서 공통 profile/frequency의 emission과 stimulated absorption을 먼저 합하면

\[
\Delta_*=3n_l-n_u,\quad
D_*=n_u(1+f_+)-3n_l f_+,\quad
C_{S,*}=\frac{A_*\lambda_*^3\Delta_*}{8\pi},
\]

\[
\mathcal R_*=A_*D_*B,\qquad
\dot u_{\gamma,*}=E_*\mathcal R_*.
\]

원전의 Einstein/Sobolev 구조는 [Hirata–Forbes §II.B 식 (1)–(3)](https://arxiv.org/pdf/0903.4925)이며, 위 집계와 공통 에너지는 이번 모델의 직접 유도·추가 가정이다. **총 opacity로 하나의 escape 확률을 계산한다.** 개별 성분에 독립 \(\beta_j\)를 계산한 후 더하는 연산과 같다고 주장하지 않는다.

이는 정확히 겹치도록 정의한 두 채널의 대수적 aggregate다. 실제 fine splitting, frequency-dependent boundary, 중첩된 doublet의 redistribution/feedback, 편극 또는 양자간섭의 완전한 전달 등가성은 입증하지 않는다. native full radiative-transfer source와의 parity도 주장하지 않는다.

## 3. Wien 복원과 full Planck 규약

native 복원은, \(w=\exp[-E_*/(k_BT_r)]\)를 쓰면,

\[
n_u=\delta n_u+3n_l w,\qquad
f_{+,W}=\delta f_+ +w
\]

형태다. 첫 식의 \(3n_lw\)는 Boltzmann population 기준으로서 full Einstein/Planck 평형과도 정확히 양립한다. **차이는 photon background에서 \(w\)를 쓰는 Wien 규약과 \(f_P=w/(1-w)\)를 쓰는 Planck 규약에 있다.**

native 경계 복원을 유지한 채 finite-\(f\) 자극방출식을 적용하면 \(\delta n_u=\delta f_+=0\)에서도
\(D_{*,W}=3n_lw^2\)다. 반면 full Planck 경계 \(f_{+,P}=\delta f_++f_P\)에서는

\[
D_{*,P}=\frac{\delta n_u}{1-w}-\Delta_*\delta f_+,
\]

이므로 같은 영 departure에서 정확히 0이다. 두 경계 선택의 차이는

\[
f_{+,P}-f_{+,W}=\frac{w^2}{1-w},\qquad
D_{*,P}-D_{*,W}=-\Delta_*\frac{w^2}{1-w}.
\]

따라서 native 복원과 full Planck 비교를 구분하여 기록한다. 동일한 stored \(\delta f_+\)에 배경만 바꾸면 작은 값이어도 물리적 경계 입력을 바꾼 것이다. 이 변경을 native source의 exact replay로 표현하지 않는다. Planck 평형 검사는 full Planck 경계와 일치시켜 수행한다. Wien에서 자극방출을 생략한 native형 잔차와 finite-\(f\) 장부를 혼합하지 않는다.

## 4. 정확도 표기와 상태

\(10^{-8}\) angular tolerance는 고정된 \(A_*,E_*,n_l,n_u,f_+\)와 선언된 모델에서 \(B,Q\)를 평가하는 **수치 오차 기준**이다. NIST 표의 미제공 원자 데이터 불확도, fine splitting 제거, 통계적 split, 공통 profile 및 Sobolev 근사의 물리 오차를 제한하지 않는다. native \(E_*\)의 많은 자릿수도 실제 원자 에너지 불확도를 보증하지 않는다. near-balance 상대오차를 전체 source 오차로 일반화하지 않으며, 부모의 finite acceptance에서 절대/정규화 잔차를 함께 사용한다.

이 추가문서는 source 선택만 고정한다. Physical/REC U5 HOLD, CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false 및 REI 첫 실패 raw의 local-only 범위를 유지한다.

