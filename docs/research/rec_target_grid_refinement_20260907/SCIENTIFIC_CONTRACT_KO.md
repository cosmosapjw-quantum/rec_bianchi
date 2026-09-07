사용자 첨부의 실행 전 수학 계약을 아래 보존한다. 현재 실행 상태는 후속 RETURN_HANDOFF_KO.md를 따른다.

**다음 노드인 `REC_TARGET_GRID_REFINEMENT_WITH_FIXED_REFERENCE_MEASURE`에 착수했어.** 수용된 보충 결과와 원격 source를 다시 확인했고, 이번에는 **약형 수렴의 기준, 읽기·분배 오차의 정확한 분해, 조건부 \(O(h_{\rm grid}^{2})\) 오차 상한**을 정리했어. 그 기준을 기존 paired/COM API에 적용하는 연구용 코드도 아래에 작성했어. 다만 이번 실행환경은 시작 전에 실패했고, 현재 연결에 GitHub·Atlassian 쓰기 함수가 노출되지 않아 **새 실행 결과·commit·게시 링크는 만들지 못했어.** 기존 보충의 수용 상태는 그대로 유효해.

## 1. 이번 단계에서 정한 비교 대상

재개 기준은 반환 commit `59dafbd34bc21b1b885c716b7b8cc899636bbd60`이야. 기존 `study.py`의 표 loader와 보간 가중치 생성기를 재사용하고, 반응률과 분배는 각각 `PhysicalTwoPhotonRamanBin`과 `COMSourceDepositionPlan`을 실제로 호출하도록 했어. 이전 7개·4개 검사를 다시 실행하거나 생산 소스를 변경하는 단계는 아니야.

이번에 중요한 결론은 세 가지야.

**첫째, atomic bin을 고정하면 비교 대상은 일반적으로 매끄러운 source 함수가 아니라 유한한 이산 source 측도야.** 원래 bin의 두 광자 에너지를 \(u_{t,b},u_{c,b}\), \(u=E/E_{21}\)로 쓰면 기준 source는

$$
{\cal Q}_{\rm ref}
=
\sum_b\Gamma_b^{\rm ref}
\left(\delta_{u_{t,b}}+\delta_{u_{c,b}}\right)
$$

로 표현된다. 여기서 \(\Gamma_b\)는 수소 원자당 초당 사건률이야. target-grid를 세분화하면서 이를 더 좁은 node 영역에 분배하면, 비영점 source가 놓이는 곳에서 \(C_i\sim\mu_i^{-1}\)로 커질 수 있어. 따라서 **\(C_i\)의 점별 크기가 작아져야 수렴한다는 기준은 적절하지 않아.** 이 결론은 위 유한-bin 표현에서 직접 따른다.

대신 고정된 시험함수 \(\psi\)에 대해

$$
M_{\psi,N}
=\frac1{n_H}\sum_i\mu_{i,N}\psi(u_{i,N})C_{i,N}
$$

를 비교한다. 이번 코드의 시험함수는

$$
\psi(u)\in\{1,u,u^2,u^4\}
$$

로 고정했어. 앞의 두 개는 보존 장부를 확인하고, 뒤의 두 개는 보존만으로 잡히지 않는 분배 형상 오차를 본다.

**둘째, 약형 moment에는 \(\mu_i\)가 소거된다.** 기존 분배식

$$
C_i=\frac{n_H}{\mu_i}\sum_sB_{is}R_s
$$

를 대입하면

$$
M_{\psi,N}
=\sum_sR_s\sum_iB_{is}\psi(u_i)
$$

야. 따라서 **약형 moment가 맞는다는 사실만으로 \(\mu_i\)의 물리적 정당성까지 인증할 수 없어.** \(\mu_i\)를 두 배로 하고 \(C_i\)가 절반으로 바뀌면 이 moment는 그대로다. 코드에는 이 관계를 확인하는 별도 검사를 넣었어. 기존 COM 구현도 caller가 제공한 측도와 분배를 사용하는 component이지, 그것들을 물리적으로 결정하는 authority는 아니야.

**셋째, target-grid 오차와 atomic 표 차이를 분리해야 한다.** 각 원자 표에 대해 자기 bin 위치에서 연속 reference 상태를 직접 평가한 기준을 만들고, 그 표를 고정한 채 target-grid만 바꾼다. 기본 표와 hires 표의 직접 기준값 차이는 별도로 저장하며, 그것을 곧바로 원자 표의 참 오차나 target-grid 오차로 부르지 않는다.

## 2. 읽기·분배·교차 오차의 정확한 분해

선형 분배 가중치로 만든 보간 연산자를 \(I_N\)이라 하고,

$$
\begin{aligned}
W_{\psi,N,b}
&=(I_N\psi)(u_{t,b})+(I_N\psi)(u_{c,b}),\\
W_{\psi,b}
&=\psi(u_{t,b})+\psi(u_{c,b}),\\
\Delta\Gamma_b&=\Gamma_{N,b}-\Gamma_b^{\rm ref},\\
\Delta W_{\psi,b}&=W_{\psi,N,b}-W_{\psi,b}
\end{aligned}
$$

로 정의하면 다음 항등식이 성립해.

$$
\boxed{
M_{\psi,N}-M_{\psi,\rm ref}
=
\underbrace{\sum_b\Delta\Gamma_bW_{\psi,b}}_{\text{읽기 오차}}
+
\underbrace{\sum_b\Gamma_b^{\rm ref}\Delta W_{\psi,b}}_{\text{분배 오차}}
+
\underbrace{\sum_b\Delta\Gamma_b\Delta W_{\psi,b}}_{\text{교차항}} .
}
$$

고정 grid·고정 \(\psi\)에서의 방향미분에도 **\(\Gamma\)를 \(\delta\Gamma\)로 바꾼 동일한 분해**가 적용돼. 이로써 “최종 source가 다르다”를 넘어 어느 단계의 오차인지 분리할 수 있어.

분배 오차 검출에는 정확한 다항식 항등식을 사용한다. \(l\le u\le r\)에서

$$
(I_Nu^2)(u)-u^2=(u-l)(r-u).
$$

예를 들어 두 광자가 \(u=3/8,5/8\)에 있고 target node가 \(1/4,1/2,3/4\)라면, 사건률이 1인 경우

$$
M_{u^2,N}=\frac9{16},\qquad
M_{u^2,\rm ref}=\frac{17}{32},\qquad
\Delta M_{u^2}=\frac1{32}.
$$

반면 \(\psi=1,u\)의 분배 오차는 정확히 0이야. **수·에너지 보존을 통과해도 비선형 moment에는 분배 오차가 남는다는, 직접 계산 가능한 대조 사례**다.

### 조건부 2차 약형 정확도

이것은 이번에 직접 유도한 결과이며, 아직 새 코드의 실행으로 확인한 결과는 아니야.

$$
\chi\in C^2,\qquad \chi(u)\ge m_\chi>0
$$

이고 비음수 선형 보간을 사용한다고 하자. 최대 간격을 \(h_{\rm grid}\), \(K_\chi=\|\chi''\|_\infty\)라 두면

$$
\|I_N\chi-\chi\|_\infty
\le\frac{h_{\rm grid}^2}{8}K_\chi.
$$

또한 \(f=(e^\chi-1)^{-1}\), \(F_{\max}=(e^{m_\chi}-1)^{-1}\)에 대해

$$
\left|\frac{df}{d\chi}\right|
=f(1+f)\le F_{\max}(1+F_{\max}).
$$

양의 bin 계수 \(a_b\), 고정 원자 population을 사용하는 기존 두 광자 반응식으로부터

$$
\sum_b|\Gamma_{N,b}-\Gamma_b^{\rm ref}|
\le
2\!\left(\sum_ba_b\right)
\left[x_u+|x_u-x_g|F_{\max}\right]
F_{\max}(1+F_{\max})
\frac{h_{\rm grid}^2K_\chi}{8}
=:R_N
$$

를 얻는다. 따라서

$$
\boxed{
|M_{\psi,N}-M_{\psi,\rm ref}|
\le
2\|\psi\|_\infty R_N
+
\frac{h_{\rm grid}^2}{4}
\|\psi''\|_\infty
\sum_b|\Gamma_b^{\rm ref}|.
}
$$

이 상한은 **고정된 유한 atomic 표, 정칙한 양의 \(\chi\), 선형 에너지 보간**에 대한 것이다. 적외선 끝점까지의 균일 상한, 실제 재결합 연산 전체, 시간 적분의 수렴을 증명한 것은 아니야. log-\(f\)/log-energy 대조에는 이 \(\chi\)-보간 상한을 적용하지 않는다.

문헌에서도 보존·엔트로피·정상상태 보존은 별도의 구조적 성질로 다뤄진다. 이번 분해와 상한은 그 논문에서 가져온 프로젝트 정리가 아니라 위 정의에서 직접 유도한 결과야. SciSpace 검색 후 원저자 초록을 대조했으며, 논문 전문을 새로 검토했다고 표시하지 않았어. ([arXiv][1])

## 3. 여기서 작성한 연구 코드

아래는 **미실행 코드 초안**이야. 새 파일은 생성·게시되지 않았으므로 존재하지 않는 다운로드 링크나 commit을 제시하지 않는다.

계산 부담을 제한하기 위해 첫 실험은 다음으로 고정했어.

* \(N=5,9,17,33,65,129\).
* 동일 구간 \([\epsilon,1-\epsilon]\), \(\epsilon=2^{-30}\).
* 공통 제조 측도 \(d\mu=20(1-2\epsilon)^{-1}du\ {\rm m}^{-3}\), node별 측도는 선형 hat 함수의 적분값.
* 정칙한 방출·흡수 상태와 affine 상세균형 대조. 모든 grid에서 동일한 연속 상태·원자 population·섭동을 사용한다.

**이 측도는 새 연구용 선택이지 물리 photon density-of-states의 채택이 아니야.** \(N=5\)에서도 PR79의 예전 \((2,4,8,4,2)\) 측도와 같지 않으며, 이전 실험의 재현으로 부르지 않는다.

파일명은 `docs/research/rec_target_grid_refinement_20260907/refinement_probe.py`로 지정했어. 코드는 원래 loader·paired·COM 함수를 호출하며, 독립 고정밀 비교에만 별도 primal 공식을 사용한다. 해당 호출 계약은 현재 source에서 확인했어.



이 파일의 범위는 사용자 첨부의 균일 측도 첫 288행/8비교 실험이다. 원격 후속 비균일 측도 초안은 이 계약에 포함하지 않는다.
NO_PASS_REC_PHYSICAL_SPLIT; physical_source_authenticated=false; provider_admitted=false.

[1]: https://arxiv.org/abs/1009.2748
