# C2: 저장된 Compton 진단의 식–데이터–코드 대응

작성 범위: 현재 C2의 **정적 경로 재구성**. 기존 과학 코드는 실행하거나 수정하지 않았고, 새 IVP·후보 최적화·성능 벤치마크를 수행하지 않았다. 실제 프로파일은 같은 단위의 별도 계측 결과를 따른다. 이 문서는 매핑 작성자의 산출물이며 독립 승인서가 아니다.

`skill_context_used`: physmath-research-loop 1.3.0의 `STAGE_SELECTION.md`, `references/CODING_LOOP.md`와 skillquiver `execute-durably`. 선택 경계는 [C2_SCOPE.md](C2_SCOPE.md), 목표·상속 계약은 [NEXT_UNIT_CONTRACT.md](../rec_compton_coupled_20261022/NEXT_UNIT_CONTRACT.md)다. C3 이후의 설계·구현·전체 동등성 시험 상태는 이 문서로 바뀌지 않는다.

## 1. 소스 권위와 현재 사용 범위

상속 스냅샷은 local commit `40f7cf12b509377350e9a16da461e8ef97cdcb62`, whole tree `a136dea6c4ade8c6be442843800d0eb1458caa5f`다. 다음 SHA256은 작성 중 실제 파일을 읽어 계산했다. 부모 계측 작업의 전체 runtime/input 검사는 별도다.

| 파일 | SHA256 |
|---|---|
| 이전 `NEXT_UNIT_CONTRACT.md` | `02d7b778142ea35402110f042373cae7e4e2b5987039a0b3d32cc93318dafded` |
| `run_compton.py` | `e81220564d303467c08b1162dcd9bea8a365c8d689c64b00aeaac7378e0511b9` |
| `compton_system.py` | `1035690890e2665769e1692e81d49d4209366291b1c8f2345f973818678f9ae9` |
| `analyze_collisions.py` | `acd7a1ed448d282cc4b102ecfd6d2043611caa3dfa480913e105c073ba0969a1` |
| `thermal_system.py` | `1ac1336a3e979ec485cec0e4092ca7d6e1ef04aa43b28f525a06231c49e34375` |
| `thermal_sources.py` | `622bc85b21d819779d98ee2a7645f51deff9a91f7a423872dbe244f5378aa769` |
| `recombination_moments.py` | `5eb740518d04dcbf123125f3d73a85fa10b48bb3bad6577cdf81459d71a390b0` |
| donor `coupled.py` | `e3005323ea085251f14262dac5671fd93d1e31d20b9dc877ca64146b58ac509f` |
| donor `geometry.py` | `b998b83f83da581cf51d08a734b34ecade5215f90ca1e72df43ce129c0fb38a0` |
| donor `atomic_network.py` | `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80` |

함수의 권위는 실제 코드에 있다. 아래 위치는 각 파일의 함수 시작 행 또는 관련 정의 행이며, 줄 번호보다 함수와 소스 해시를 우선한다.

- Compton driver: [run_compton.py](../rec_compton_coupled_20261022/code/run_compton.py), `source_identity` 117, `load_inputs` 133, `gather_set` 221, `one_case` 341.
- Compton adapter: [compton_system.py](../rec_compton_coupled_20261022/code/compton_system.py), `_compton_state` 61, `compton_terms` 131, `sample` 164, `diagnostics` 204.
- Thermal adapter: [thermal_system.py](../rec_thermal_moments_20261022/code/thermal_system.py), `point` 29, `thermal_diagnostics` 74, `diagnostics` 94.
- Thermal owner: [thermal_sources.py](../rec_thermal_moments_20261022/code/thermal_sources.py), `coefficients` 65, `evaluate` 87, `temperature_log_rhs` 116; [recombination_moments.py](../rec_thermal_moments_20261022/code/recombination_moments.py), `evaluate` 87.
- Number/geometry owner: [coupled.py](../rec_rei_hheli_sandbox_20261021/code/coupled.py), `thermal_uv` 52, `diagnostics` 124; [atomic_network.py](../rec_rei_hheli_sandbox_20261021/code/atomic_network.py), `rates` 233, `evaluate` 265; [geometry.py](../rec_rei_hheli_sandbox_20261021/code/geometry.py), `fields` 86, `normalized` 113.
- Omitted collision owner: [collisional_budget.py](../rec_thermal_omitted_budget_20261022/code/collisional_budget.py), `coefficients` 125, `evaluate` 159; [analyze_collisions.py](../rec_compton_coupled_20261022/code/analyze_collisions.py), `integrate_retained` 123, `_support_for` 158, `_evaluate_grid` 203.

## 2. 독립변수·상태·단위

고정된 LRS convention은 평균 scale factor \(a\), \(a_\perp=a e^{-b}\), \(a_\parallel=a e^{2b}\), \(s=db/dt\)다. Orthonormal frame에서 \(\sigma_{ab}=\mathrm{diag}(-s,-s,2s)\), signature는 \((-,+,+,+)\)다. 현재 작업은 이 기하와 유한 계층의 closure를 변경하지 않는다. 근거: [donor THEORY_KO.md](../rec_rei_hheli_sandbox_20261021/THEORY_KO.md) §1, `Geometry.rhs_from_fields`, `Geometry.normalized`.

\[
x=\ln(a/a_{\rm ref}),\quad a_{\rm ref}=1/21,
\qquad z=21e^{-x}-1,\qquad dt/dx=1/H.
\]

| 저장 위치 | 물리량·정규화 | 코드 연결 |
|---|---|---|
| `raw_state[:,0]` | donor \(z=20\) 이후 proper elapsed time × \(H_{\rm ref}\) | `elapsed_Myr=y[0]/href/31557600e6`; restart에서 0으로 재설정하지 않음 |
| `raw_state[:,1]` | \(b\) | metric anisotropy와 massive momentum moment 입력 |
| `raw_state[:,2]` | \(s/H_{\rm ref}\) | `fields['s']=y[2]*href` |
| `raw_state[:,3]` | 기존 기하의 thermal 슬롯 | 현재 `Geometry.rhs_from_fields`에서 미분 0; full63 기체 에너지를 여기에 넣지 않음 |
| `4:13`, `13:22` | photon energy/number multipoles, \(\ell=0\ldots8\) | `E_gamma`, `N_gamma`; Thomson opacity는 현재 \(n_e\)를 사용 |
| `22:31`, `31:40` | neutrino energy/number multipoles, \(\ell=0\ldots8\) | `E_nu`, `N_nu`; photon Thomson 감쇠를 적용하지 않음 |
| `40:61` | 동위원소 scale로 나눈 21개 abundance | \(Y_i=\mathrm{raw}_{40+i}\,\mathrm{scale}_i\), 핵자당 수 |
| `61` | 누적 Thomson \(\tau_T\) | \(d\tau_T/dx=\sigma_T c n_e/H\); donor 이력 보존 |
| `62` | \(\ln T_g\) | `T_K=np.exp(raw[:,62])`; 동적 온도 |

21개 species는 `n`, `H1 I–II`, `D I–II`, `T I–II`, `He3 I–III`, `He4 I–III`, `Li6 I–IV`, `Li7 I–IV` 순서다. `atomic.q`, `atomic.A`, `atomic.ionization_energy_J`, `atomic.scales`가 각각 전하·핵자수·누적 이온화 에너지·수치 scale의 권위다. \(n_e=n_b q\cdot Y\), \(\eta=(1+q)\cdot Y\), \(n_b=n_{b0}/a^3\). \(Y\)와 \(\eta\)는 무차원이고, \(n_b,n_e\)는 proper \(\mathrm{m}^{-3}\), \(H\)는 \(\mathrm{s}^{-1}\)다.

`ComptonFull63`의 `ThermalSystem.point`는 처방된 `thermal_uv(x)[0]`를 온도로 쓰지 않고 `exp(y[62])`를 사용한다. UV amplitude만 \(q_{\rm UV}(x)=\tfrac12[1+\tanh((7-z)/0.8)]\)에서 가져온다. 상속된 `CoupledSystem.diagnostics`의 옛 prescribed-temperature source는 `ThermalSystem.diagnostics`에서 동적 온도의 장부로 교체된다. 이 dispatch를 빠뜨리면 같은 함수 이름을 읽고도 다른 물리를 복원하게 된다.

초기조건은 `run_compton.load_inputs`가 검증한 old Mao nominal의 **정확한 63-vector**다. nominal/refined 모두 같은 초기상태를 쓰며, 첫 62개 성분은 donor의 index 84와 정확히 일치해야 한다. 저장 구간의 종점은 \(x=\ln7\), 즉 \(z=2\)다. 현재 C2는 저장된 점을 읽으므로 새 초기조건이나 경계조건을 만들지 않는다. `raw[40,45,46]=0`은 neutron/tritium 원자망 계약이며 핵 생성의 물리적 부재 증명이 아니다.

## 3. 수식에서 source 및 진단으로

### 3.1 Number network와 열원

`AtomicNetwork.evaluate`가 돌려주는 물리시간 source는

\[
F\equiv\dot Y=G_0Y+n_e(G_{\rm RR}+G_{\rm DR})Y+DY,
\qquad \frac{dY}{dx}=F/H.
\]

`rates`의 matrix 단위는 \(G_0,D:\mathrm{s}^{-1}\), \(G_{\rm RR},G_{\rm DR}:\mathrm{m}^3\mathrm{s}^{-1}\)다. `network['jac']`는 \(n_e=n_bq\cdot Y\)의 abundance 의존성을 포함한다. 저장점 진단 재사용은 이를 새 수치 Jacobian이나 고정 \(n_e\) 근사로 바꾸는 작업이 아니다.

`ThermalSources.evaluate`는 전달받은 `network`를 재사용하지만 `coefficients(T)`는 별도로 평가한다. Mao hybrid에서 RR kinetic coefficient는 \(L_{\rm RR}=k_BT\,\alpha_{\rm donor}f_{\rm Mao}\)이며, DR는 고정된 resonance moment 합이다. `RecombinationMoments.evaluate`는 동일 donor RR/DR 수식과 도함수도 계산한다. 기존 number fit와 다른 RR number rate를 조용히 교체할 수 없다.

다음 열 장부는 모두 proper \(\mathrm{W\,m^{-3}}\)다.

\[
Q_{\rm kin}^{(0)}=Q_{\rm primary}-Q_{\rm RR}-Q_{\rm DR},
\qquad Q_{\rm ion}=n_bI\cdot F,
\]

\[
Q_{\rm escape}=Q_{\rm Li\ core}+Q_{\rm recomb\ binding}
 +Q_{\rm RR}+Q_{\rm DR}.
\]

`thermal_sources.py:evaluate`의 source residual은 \(Q_{\rm absorbed}-Q_{\rm escape}-Q_{\rm kin}^{(0)}-Q_{\rm ion}\)이다. Photo absorption을 전부 kinetic heating으로 취급하면 binding/core 소유권이 사라진다.

### 3.2 독점적인 Compton bath와 두 독립 gas 합계

\(K=\sigma_Tc/(m_ec^2)\)일 때 현재 branch별 source는

\[
Q_{C,\rm actual}=-4Kn_ek_BT_gU_{\gamma,\rm actual},
\quad U_{\gamma,\rm actual}=\rho_{c0}\Omega_\gamma y_4/a^4,
\]

\[
Q_{C,\rm ref}=4Kn_ek_BU_{\rm ref}(T_{\rm ref}-T_g),
\quad T_{\rm ref}=2.7255/a,\quad U_{\rm ref}=a_RT_{\rm ref}^4,
\]

\[
Q_{\rm UV,C}=Kn_e(M_{\rm UV}-4k_BT_gU_{\rm UV}).
\]

`compton_terms`는 두 CMB 후보 power를 모두 보고하지만 `branch`가 선택한 하나만 `compton_selected_W_m3`와 동적 열원에 들어간다. `actual_hot`의 실제 energy monopole와 독립 Planck bath를 같은 source로 합치지 않는다. \(U\)는 \(\mathrm{J\,m^{-3}}\), \(M\)은 \(\mathrm{J^2\,m^{-3}}\)다. UV 두 moment는 생성자에서 한 번 계산한 값에 현재 amplitude를 곱한다.

`sample`에서 \(Q_{\rm kin}=Q_{\rm kin}^{(0)}+Q_C+Q_{\rm UV,C}\)를 만든 뒤 **각각의 정의로** 다음 두 합계를 유지한다.

\[
Q_{\rm gas}^{(1)}=Q_{\rm kin}+Q_{\rm ion},\qquad
Q_{\rm gas}^{(2)}=Q_{\rm absorbed}-Q_{\rm escape}+Q_C+Q_{\rm UV,C}.
\]

첫 합계는 `gas_energy_source_W_m3`, 두 번째 합계는 `gas_source_from_radiation_W_m3`다. 네 저장소 residual은 `sample`의 `gas`, `cmb_bath`, `uv_bath`, `escaped`를 `math.fsum`에 각각 전달한다. UV bath에는 photo absorption과 UV Compton의 반대 부호가 함께 들어간다.

\[
R=\operatorname{fsum}\bigl(Q_{\rm gas}^{(1)},-Q_C,
                         -Q_{\rm absorbed}-Q_{\rm UV,C},Q_{\rm escape}\bigr).
\]

`transfer_ledger_residual_scaled=abs(R)/max(sum_abs_throughput,1e-300)`이며 기존 photo/RR/DR residual은 `photo_rr_dr_source_energy_residual`에 별도로 남는다. 공통 상태 재료를 공유해도 \(Q_{\rm gas}^{(1)}\)을 두 번째 합계에 복사하면 독립 검사가 소실된다. Bath 반대 부호는 장부에만 있고 photon/Einstein RHS에 적용되지 않는다.

### 3.3 온도식·에너지 적분과 기하 진단

\[
\frac{d\ln T_g}{dx}=-2+
 \frac{2Q_{\rm kin}/(3k_BT_gn_b)-\dot\eta}{H\eta},
\quad \dot\eta=(1+q)\cdot F,
\]

\[
e_g=\frac32k_BT_g\eta+I\cdot Y,
\qquad \frac{de_g}{dx}=\frac{Q_{\rm gas}^{(2)}}{n_bH}-3k_BT_g\eta.
\]

`temperature_log_rhs`, `thermal_diagnostics`, `ComptonFull63.rhs`와 `gather_set`이 이 대응을 구현한다. \(\mathrm{W/m^3}\)를 \(n_bH\)로 나누면 \(\mathrm{J/baryon}/x\)이고, `EV_J`로 더 나누면 collision 제품의 \(\mathrm{eV/baryon}/x\)다. `work_J_per_baryon_per_x=3k_BT_g eta`는 양의 work 크기이며 net integrand에서는 뺀다.

`Geometry.normalized`는 signed six-vector \((\sqrt6s/H,P_m,P_r,P_m+P_r,P_\gamma,P_\nu)\)를 반환하며 \(P_A=\sqrt6\kappa_T\pi_A/H^2\), \(\kappa_T=8\pi G/c^2\)다. `gather_set`의 Einstein constraint는 같은 `field`의 dust, massive, radiation, \(\Lambda\), shear를 사용한다. 기체 thermal/ionization와 UV 에너지는 test-fluid 진단이므로 이 constraint에 새로 더하지 않는다. angular positivity는 고정된 129개 각도에서 재구성한 유한 검사이며 continuum 양성 정리가 아니다.

## 4. 한 저장점의 정확한 정적 호출 경로

`gather_set`의 루프 한 번은 다음 네 개 요청을 순서대로 한다.

1. `ComptonFull63.sample`: `ThermalSystem.thermal_diagnostics → point → fields + AtomicNetwork.evaluate`, 이어 `ThermalSources.evaluate`, 이어 `compton_terms → _compton_state → fields`.
2. `ComptonFull63.diagnostics`: 먼저 `ThermalSystem.diagnostics → CoupledSystem.diagnostics → self.point`가 **ThermalSystem.point**를 호출한다. 이어 `self.thermal_diagnostics`가 **ComptonFull63.thermal_diagnostics → sample**로 dispatch한다. 마지막으로 `ComptonFull63.diagnostics` 자신이 `compton_terms`를 다시 호출한다.
3. `geometry.fields`: Einstein constraint와 signed 결과에 사용할 field를 다시 구한다.
4. `geometry.normalized(..., field)`: 전달된 field를 사용하므로 여기서는 `fields`가 추가되지 않는다. `CoupledSystem.diagnostics` 안의 normalized도 field를 전달한다.

| 함수 또는 연산 | `sample` 직접 호출에서 | `diagnostics`에서 | 바깥 `gather_set`에서 | 저장점당 합계 |
|---|---:|---:|---:|---:|
| `ThermalSystem.point` | 1 | 2 | 0 | **3** |
| `Geometry.fields` | 2 | 4 | 1 | **7** |
| `AtomicNetwork.evaluate` / `rates` | 1 | 2 | 0 | **3 / 3** |
| `ThermalSources.evaluate` / `coefficients` | 1 | 1 | 0 | **2 / 2** |
| `RecombinationMoments.evaluate` | 1 | 1 | 0 | **2** |
| `compton_terms` / `_compton_state` | 1 | 2 | 0 | **3 / 3** |
| `thermal_uv` / `baryon_number_density` | 2 | 4 | 0 | **6 / 6** |
| `Geometry.normalized` | 0 | 1 | 1 | **2** |
| 129×9 `legvander` 구성 | 0 | 1 | 0 | **1** |

이 표는 **코드의 dispatch와 호출문으로 유도한 횟수**이며 wall/CPU 측정 결과가 아니다. `gather_set`의 격자별 array 조립·극값·적분·gate와 생성자·입출력은 표 밖이다.

Prepared backend에서는 [canonical_fv.py](../rec_rei_hheli_sandbox_20261021/vendor/baseline/canonical_fv.py) `CanonicalFVSpecies.fields` 227이 \(f_m=0.1\)의 momentum moment를 한 번 요청한다. [prepared_moments.py](../rec_rei_hheli_sandbox_20261021/vendor/he31/prepared_moments.py) `moments` 104가 동일한 2592개 prepared packet에서 energy와 pressure를 계산한다. 따라서 위 경로에는 **prepared momentum evaluation 7회/점**이 따른다. 이는 새 quadrature를 만드는 호출이 아니라 고정된 quadrature의 재평가다.

`AtomicNetwork.rates` 3회와 `RecombinationMoments.evaluate` 2회는 서로 다른 함수 호출이다. 후자도 RR/DR 계수의 대수를 계산하므로 동일 온도의 일부 수치 계산이 중복되지만, 이를 `rates` 5회라고 보고하면 호출 프로파일과 맞지 않는다. `mao_factor`는 thermal coefficients 한 번당 native recombination index 13개를 순회하므로 이 경로에서 26회/점이다.

반면 UV 단면적·spectral bin 적분은 `AtomicNetwork._prepare_spectrum` 165에서 이미 준비된다. `ComptonFull63.__init__` 46의 `uv_reference_moments`도 초기화당 한 번이다. 이들을 상태별 비싼 재적분으로 간주하면 존재하지 않는 병목을 대상으로 삼게 된다.

## 5. Collision 경로와 mask의 소유권

`analyze_collisions._evaluate_grid`는 저장된 \(Y,T_g,H,n_b,n_e,\eta\)를 사용한다. 자체적으로 geometry나 `AtomicNetwork.evaluate`를 다시 호출하지 않는다. 각 점에서 `CollisionalBudget.evaluate` **1회**, 그 안에서 `coefficients` **1회**를 호출한다. 포함된 전자율은 CI H I/He I/He II 3개와 CE H I/He II 2개이며 native isotope에 매핑한 CI channel 7개, CE channel 5개를 조립한다.

CI event \(r_i=n_e C_iY_{\rm lower}\)는 핵자당 \(\mathrm{s}^{-1}\), volumetric event는 \(n_br_i\)다. 채널별 binding 저장은 \(n_br_i\Delta I_i\), kinetic loss는 그 음수다. 별도로 계산하는 \(n_bI\cdot F_{\rm CI}\)와 전하 변화 \(q\cdot F_{\rm CI}\)가 각각 binding 합계와 particle event 합계를 확인한다. CI 총 gas-energy 직접 source가 0이어도 \(\dot\eta_{\rm CI}\) 항은 온도 forcing에 남는다.

CE H I는 native `Y[[1,3,5]]`, CE He II는 `Y[[8,11]]`를 사용한다. `_evaluate_grid` 240은 이 명시적 target 합계와 provider channel 합계를 별도로 비교한다. Li CI/CE와 He I CE는 unavailable mask를 유지하며 물리적 0으로 선언하지 않는다. 채널이 존재하지만 계수가 underflow된 경우, event/volume/power 곱이 underflow된 경우, source range 밖인 경우도 각각 별도 flag다.

\[
f_{\rm CI}=\frac{2Q_{\rm CI,kin}}{3k_BT_g n_bH\eta}
             -\frac{\dot\eta_{\rm CI}}{H\eta}.
\]

이 값과 CE forcing은 **저장된 경로의 조건부 진단**이다. 적분한 forcing을 실제 새 온도 경로의 \(\Delta\ln T\)로 승격하지 않는다. CI/CE는 원래 Compton IVP에 들어 있지 않다.

Grid당 `integrate_retained`는 energy 13개와 forcing 6개에 총 **19회** 호출되고, 각 호출은 trapezoid와 Simpson을 따로 산출한다. 구간 support는 `valid[:-1] & valid[1:]`이다. `_support_for`의 CI 합성량은 세 CI mask의 AND, 포함된 total kinetic/forcing은 다섯 mask의 AND, 포함된 total gas energy는 두 CE mask의 AND다. 합성 support를 단일 channel의 source 정확도와 혼동하지 않는다.

## 6. 점 재사용과 격자 재구성의 구분

현재 `run_compton.one_case`는 comparison109, accepted, dense513, dense1025에 각각 `gather_set`을 적용한다. `dense513.x=dense1025.x[::2]`지만 `sol.sol`을 별도로 평가한 raw state는 과거 비교에서 완전히 byte-identical하지 않았다. 따라서 다음 두 관계를 분리해야 한다.

| 관계 | 현재 근거와 허용 범위 |
|---|---|
| 같은 branch/config/source와 정확히 같은 \(x,y\) | 상태 재료·점 진단 재사용의 동등성 후보. 현재는 경로를 특정했으며 후보 구현 증명은 남아 있음 |
| 서로 다른 branch | 같은 숫자 상태라도 `compton_selected`의 소유자가 다름. branch key 없는 공유 금지 |
| old dense513와 dense1025 slice | 알려진 roundoff 규모 차이를 가진 서로 다른 입력. 새 slice 제품은 별도 provenance와 비교 필요 |
| 1025점 cumulative의 slice | 513점 trapezoid가 아님. 513점 적분·누적·support·extrema·gates를 그 격자에서 재계산해야 함 |
| comparison109 / accepted와 dense1025 | 근접 x 매칭·보간으로 동등하다고 간주할 수 없음. 원래 입력과 순서 유지 |

점 재사용이 보존해야 할 출력은 scalar diagnostic만이 아니다. `diagnostic_names` 순서, inherited diagnostic 이름, signed six-vector, initial state/scale, branch, energy integrand, residual normalization과 mask가 함께 계약에 속한다. 기존 admission 임계값·출력 schema를 줄이는 것이 비용 감소의 근거가 될 수 없다.

## 7. C2에서 확인한 것과 C3에 전달할 질문

**정적으로 확인됨:** 같은 점에서 fields·number network·thermal source·Compton state를 반복 계산한다. 재사용 가능한 재료의 경계는 \((x,y,\mathrm{config},\mathrm{branch},\mathrm{source\ identity})\)이며, 두 독립 energy 합계와 격자 연산은 별도 정의를 유지한다. 고정 UV spectrum/moments와 prepared FV packet은 이미 준비되어 있다.

**아직 이 문서로는 확인되지 않음:** 어떤 함수가 최대 wall/CPU 비용을 차지하는지, compression/I/O의 비중, 환경 변동 크기, 재사용의 실제 속도 개선과 전체 저장점의 동등성이다. Geometry의 7회 호출만으로 최우선 비용이라는 결론을 내리지 않는다. inclusive 시간을 더해 전체 시간처럼 보고하지 않는다.

측정 후 C3에서 검토할 구체적 경계는 다음과 같다.

1. 한 호출에 한정된 state context로 fields/network/thermal/Compton 재료를 전달할 수 있는가? 상속 dispatch가 만드는 중복을 제거하면서 기존 합산 순서와 진단을 보존해야 한다.
2. constant 129각도 Legendre 행렬의 준비 비용이 의미 있는가? 값과 normalization이 고정임은 코드에서 확인되지만 성능 우선순위는 계측으로 결정한다.
3. 동일 dense1025 점 결과로 별도 513 제품을 만드는 경우, 원래 입력 roundoff와 새 경로 차이를 분리해 어떻게 검증할 것인가?
4. Collision에서는 이미 geometry 재사용이 되어 있다. 실제 비용이 계수/채널 조립, 구간 적분, serialization 중 어디인지 따로 판별해야 한다.

이 질문들은 다음 단계의 설계 입력이며 후보 코드나 성능 개선의 완료 주장이 아니다. 현재의 physical HOLD, production NOT_APPROVED, global convergence NOT_RUN, REI false와 U5 closed 상태도 유지한다.
