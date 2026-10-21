# 결합·열·GR·주장 범위의 독립 검토

## 판정과 검토자 범위

**판정: 정의된 유한 결합 모형 안에서 현재 차단할 부호·단위·Jacobian 오류를 찾지 못했다.** 초기 125개 축 조합은 massive/radiation source의 양의 각도분포 허용 범위 안에 있다. 그러나 이 판정은 완전한 thermal/nuclear/UV transport closure나 전역 수치 오차 인증이 아니다. `Physical HOLD`, `global convergence NOT_RUN`, `production NOT_APPROVED`, 원래 REC U5 HOLD, `REI_activation=false`를 유지한다.

검토자는 `/root/next_theory_scope`이다. 이 검토자는 `atomic_network.py`의 저자이므로 **원자 코어에 대한 독립 저자 검토라고 주장하지 않는다.** 이번 독립 범위는 root가 작성한 `THEORY_KO.md`, `coupled.py`, `geometry.py`의 결합식·열 장부·GR 해석·headline 범위다. 원자 코어의 별도 독립 검토는 `INDEPENDENT_CODE_REVIEW_STAGE_B.md/.json`의 다른 검토자가 맡았다.

이번 검토에서 새 ODE, benchmark, cosmological case는 각각 **0**이다. source와 문서 읽기, 기존 receipt 확인, `CAMPAIGN.json`의 축 집합·범위·해석적 부등식 계산만 수행했다. 전체 125-case의 완료 결과나 새 opacity-off 궤적을 이 문서로 미리 통과시키지 않는다.

## 읽은 고정 snapshot

| 파일 | 검토 시 SHA256 |
|---|---|
| `THEORY_KO.md` | `d2d5d13ac2ca3b6bf79331dc29b8d3fea1e7e2303beb2777733f5b464efdbee9` |
| `code/coupled.py` | `e3005323ea085251f14262dac5671fd93d1e31d20b9dc877ca64146b58ac509f` |
| `code/geometry.py` | `b998b83f83da581cf51d08a734b34ecade5215f90ca1e72df43ce129c0fb38a0` |
| `data/CAMPAIGN.json` | `f5412401af14b6886dd3d43a5c2f2c8ebfaebb8bfdf4b63fa5764174e7fc7f8e` |
| `evidence/COUPLED_VERIFICATION.json` | `bd675ec8968eb783df82481dc61353b4f0fc8a890bddd145df561e1e5e5f114c` |

함께 읽은 source는 `vendor/baseline/{canonical_fv,species_hierarchy,lrs_boltzmann}.py`, `vendor/he31/prepared_moments.py`, `vendor/tangent/tangent_core.py`, `WOLFRAM_IDENTITIES.json`, `OUTPUT_RECOVERY_CONTRACT.json`, `INDEPENDENT_RECOVERY_PRECHECK.json`이다.

기존 coupled verifier는 `coupled.py=09a3325c…`에서 실행됐다. 현재 `e3005323…`는 NumPy scalar JSON 직렬화 복구가 적용된 버전이다. 별도 독립 recovery receipt는 `atomic_json` 이외의 module AST가 동일함을 확인했고, 여기서 읽은 RHS/Jacobian/진단식도 그대로다. 따라서 기존 finite Jacobian/wiring 결과를 **과학 함수가 동일한 범위에서 재사용**할 수 있다. 새로운 전체 파일 hash에서 verifier를 다시 실행했다고 표기하지 않는다. 실패 namespace와 완성된 초기 trajectory의 보존·복구도 별도 receipt의 범위다.

## 1. 초기 125개 물리축과 source 허용 범위

읽은 캠페인은 정확히 125개 case, 125개 고유 `(Sigma_F, P_m, P_r)` 조합으로, 선언한 5×5×5 Cartesian product와 일치한다. 모든 case가 193개 저장점, prepared backend, opacity on을 사용하고, `x_end` override가 없어 기본 `ln(7)`을 선택한다. 기존 warm729나 다른 완료 캠페인을 새로운 125개로 세지 않는다.

| 양 | 읽은 캠페인의 범위 |
|---|---:|
| 초기 Frobenius shear 크기 | 0 .. 0.6 |
| signed 초기 matter 축 | −0.0005 .. 0.001 |
| signed 초기 radiation 축 | −0.0012 .. 0.0012 |
| 변환된 massive amplitude A_m | −0.7780978094932278 .. 1.5561956189864556 |
| 변환된 radiation amplitude A_r | −0.4275708327913344 .. 0.4275708327913344 |

source의 초기 각도분포는 `W=1+A P2(mu)`이고 `−1/2≤P2≤1`이다. 따라서 전체 연속 각도에 대한 초기 하한은 다음과 같다.

\[
W_{m,\min}\ge\min(1+A_{m,\min},1-A_{m,\max}/2)
=0.22190219050677218>0,
\]

\[
W_{r,\min}\ge\min(1+A_{r,\min},1-A_{r,\max}/2)
=0.5724291672086657>0.
\]

이는 단순히 일부 각도를 찍은 결과가 아니라 선언된 초기 quadratic angular family의 해석적 범위다. 코드가 정한 `−0.9≤A_m≤1.8`, `|A_r|≤0.45`도 모두 충족한다. 초기 `s²/H²=Sigma_F²/6`의 최대는 0.06이다. 초기 shear 부호는 양의 branch로 고정되고 matter/radiation stress는 signed 축을 쓴다. 전체 signed shear parameter space를 조사한 것으로 확대하지 않는다.

24×12 cells와 Gauss3의 2592개 packet은 동일한 canonical quadrature다. 양의 angular factor와 양의 quadrature measure 때문에 source number weights를 음수로 바꾸는 축은 이 캠페인에 없다. 시간 중에는 이 collisionless number packet을 보존하고 metric으로 physical moment를 다시 평가한다. 이 사실이 유한 L=8 radiation polynomial의 모든 시각·모든 각도 양성을 동시에 증명하지는 않는다.

massless radiation의 `finite_angular_positivity` gate는 **193개 저장 시각에서 129개 각도**의 재구성값을 검사한다. finite diagnostic으로 정확히 표기되어 있다. 저장 시각 사이, 각도 mesh 사이, L→∞ 한계의 전역 양성·수렴을 인증했다는 표현은 허용되지 않는다. 원 source의 `|b|≤1` chart 제한도 runtime에 유지된다.

`f_m=0.1`의 정확한 뜻은 **전체 Ω_m의 10%를 비바리온 massive Vlasov component에 배정**하는 것이다. 나머지 `(1−f_m)Ω_m`은 dust이고 baryon rest density는 이 dust 예산에 남는다. “비바리온 Ω만의 10%”로 설명하면 다른 정규화가 된다. source의 `f_m Ω_m≤Ω_m−Ω_b` 검사가 baryon 예산 중복을 방지한다.

## 2. 결합식과 analytic block Jacobian

결합 상태는 원 geometry 40개, scaled atomic abundance 21개, optical-depth scalar 1개다. x는 `ln(a/a_ref)`이며 초기 z=20, 끝 z=2다. 물리시간 원자 derivative를 `H`로 나누는 위치가 맞다.

고정 x에서 `Y=Wv`, `W=diag(scales)`, `n_e=n_b q^T Wv`이고 `h_j=∂lnH/∂y_j`라 쓰면 atomic block은

\[
v'=W^{-1}f(Y)/H,\quad
\frac{\partial v'}{\partial v}=W^{-1}J_YW/H,\quad
\frac{\partial v'}{\partial y}=-v'\,h^T.
\]

`coupled.py`가 이 식을 그대로 구현한다. prescribed T/UV와 nb는 고정 x에서 geometry/abundance state와 독립이므로 해당 state Jacobian에 그 chain term이 빠진 것은 오류가 아니다. 원자 Jacobian 내부의 `n_b(RY)q^T` 항은 유지된다.

광자 collision은 두 photon energy/number block에만

\[
-\frac{c\sigma_Tn_e}{H}D_\ell J_\ell
\]

를 넣는다. SI의 `n_e`는 m⁻³이며 기존 `GAMMA_PER_NE`의 cm⁻³ convention에 맞춰 `1e6`으로 나누는 변환이 정확하다. `∂n_e/∂v=n_b q^TW` 교차항의 부호는 음수다. `H` denominator 미분에서 생기는 geometry 교차항은 양수다. neutrino block에는 electron collision이 없다. 기존 unpolarized elastic Thomson의 `D_0=0`, `D_2=0.9`를 사용한다. 이것은 full E/B polarization이나 Compton thermal transfer를 새로 구현한 결과가 아니다.

`geometry.jacobian_blocks`의 `hgrad`도 읽은 constraint와 일치한다. 예를 들어 finite mass-shell sum의 `rho_b=−6p_m`에서 `∂lnH/∂b=−3H0² Pi_m_norm/H²`가 나온다. shear coordinate와 photon/neutrino energy monopole의 미분도 같은 constraint를 따른다. `TangentOperator`는 prepared moment wrapper를 끼우기 전에 원 owner에서 고정 snapshot을 만들며, 동일 source closure의 analytic derivative다.

기존 finite verifier의 3개 state·15개 방향 결과를 읽었다. 저장된 scaled JVP 차이는 `1.4479186012016445e-7`이고, 이 값은 해당 finite check의 결과다. 검토자가 새 finite difference나 ODE를 실행했다고 기록하지 않는다. 이 점검은 trajectory error, full parameter-domain derivative bound, numerical convergence certificate가 아니다.

## 3. GR·stress·number 해석

`sigma=diag(−s,−s,2s)`와 `pi=diag(−p,−p,2p)`에서 Frobenius norm은 각각 `sqrt(6)|s|`, `sqrt(6)|p|`다. code의 `kappa_t=8piG/c²`는 J m⁻³와 inverse-second H를 함께 쓸 때의 시간 단위 계수와 일치한다. half-contraction norm과의 `sqrt(2)` 차이도 문서에 명시돼 있다.

matter/radiation signed stress를 먼저 더하고 total norm을 취한다. `observables_norm=abs(signed_observables)`의 total 열은 앞서 합한 `P_m+P_r`의 절댓값이므로 상쇄를 보존한다. matter와 radiation norm을 먼저 더한 값으로 대체하지 않는다.

collisionless massive source의 shear work, finite-L radiation monopole의 shear work, `dot(s)+3Hs=kappa_t(p_m+p_r)` 및 Hamiltonian constraint의 정규화에 서로 충돌하는 부호를 찾지 못했다. atomic gas는 별도의 common-T isotropic closure여서 `pi_b=0`이고, 이번 finite model의 matter anisotropic stress는 collisionless component가 공급한다.

`number_monopoles` gate는 photon/neutrino의 **comoving number monopole**이 1을 유지하는지 본다. 실제 proper number density가 cosmological expansion 중 상수라는 뜻이 아니다. `elapsed_s=y[0]/H_ref`는 z=20 이후 경과시간이며 우주의 절대 연령이 아니다.

`einstein_constraint` gate는 같은 algebraic H 정의를 다시 대입한 내부 일관성 검사다. 이것을 independent Einstein evolution residual이나 열린 에너지 reservoir까지 닫힌 장부의 증명으로 부르지 않는다.

## 4. prescribed T/UV와 에너지 장부

`thermal_uv()`의 z(x), tanh ramp, analytic `dT/dx` 부호와 계수를 대조했다. 온도는 100–12000 K 안에 있으며 채택한 atomic runtime domain 안이다. 이 이력은 관측 EoR fitting 결과가 아니라 외부 처방이다.

`n_g=n_b ΣY+n_e`, `u_th=3 n_g k_B T/2`, `u_ion=n_b I·Y`에서 실제 atomic n/T flux가 0인 main orbit의 요구 순전력은

\[
Q_{net}=\tfrac32 k_Bn_g H(T_x+2T)
 +\tfrac32k_BT\,n_bq^Tf+n_bI^Tf.
\]

`diagnostics()`의 `q_required`는 이 식과 일치한다. nb를 포함한 source와 원자 physical-time derivative를 혼동하지 않는다. `bath_minus_escape=Q_net−Q_photo_abs`는 net residual이고 heater와 escaping emission을 각각 결정하지 않는다. RR number coefficient에서 에너지 모멘트를 만들어 내지 않는 설명이 맞다. Li I 1s의 unresolved core 항도 별도 진단으로 남아 있다.

외부 UV를 매 순간 **local-frame isotropic reservoir**로 정의했으므로 `pi_UV=0`은 그 모형 가정 안에서 맞다. anisotropic expansion 중 자유 전파하는 UV가 저절로 isotropic 상태를 유지한다는 유도는 아니다. 방출·주입·산란 등이 해당 isotropic field를 유지하는 상황을 대신 지정한 것으로 해석해야 하며, UV의 각도 transport와 local anisotropic spectral feedback은 계산하지 않는다. UV와 CMB/ν는 다른 photon populations이다.

`trace_energy_fraction=(u_th+u_ion+u_UV)/(3H²/kappa_t)`는 **instantaneous omitted-energy diagnostic**이다. 분모는 dynamic critical energy density이며 shear를 빼기 전 conventional H 기준이다. 작은 값은 해당 시각의 test-fluid scale separation을 보여줄 수 있다. 다음 항목은 이 값으로 따라오지 않는다.

- 시간 누적된 H, shear, ionization history 오차의 상한.
- 미지의 bath/escaping-radiation stress까지 작다는 상한.
- CI/CX/secondary-ionization/분자·핵반응 생략 오차의 상한.
- isotropic UV 가정을 완화한 anisotropic transfer 오차의 상한.

따라서 `trace_energy_small<1e-5`는 동결한 pilot acceptance diagnostic이며 production 물리 검증 기준으로 승격하지 않는다. 원자 pressure와 UV isotropic pressure를 Einstein source에 추가하지 않는 근사도 이 범위 안에서 해석해야 한다.

## 5. 125개와 opacity-off 한 개의 비교 범위

대표 초기점 `(Sigma_F,P_m,P_r)=(0.15,0.0005,0.0006)`의 opacity-off control은 main 125개 중 opacity-on 대응점과 다른 유한 문제다. `opacity=False`는 photon hierarchy의 electron scattering term만 끄며 chemistry·UV·T prescription은 유지한다. 이 비교는 해당 점에서 실제 ne→Thomson 결합의 영향을 보여주는 구성적 대조다. benchmark나 기존 완료 ODE의 재실행으로 분류하지 않는다.

주의할 구체적인 해석은 두 가지다.

1. 동일 state를 넣은 순간에는 opacity toggle이 chemistry RHS를 바꾸지 않는다. 그러나 서로 다른 전체 궤적은 radiation→H/shear→physical time 피드백으로 chemistry도 달라질 수 있다. whole-trajectory ne가 정확히 같다고 주장하면 안 된다.
2. 현재 코드는 opacity-off에서도 `tau'=c sigma_T n_e/H`를 적분한다. 그 control의 tau는 자체 electron history에서 계산한 **potential electron-column Thomson depth**다. 실제 적용한 collision opacity가 0이라는 control 정의와 구분해 표시해야 한다. 코드의 tau를 적용 scattering depth라고 표시하면 오해가 된다.

어느 경우든 저장 tau는 **z=20부터 현재 z까지**의 누적량이다. z=0부터 last scattering까지의 관측 CMB optical depth와 같은 quantity로 비교하지 않는다. 한 control은 전체 125개에 대한 물리적 오차 추정이나 모든 seed에서의 민감도 상한을 제공하지 않는다.

## 6. “21개 상태”와 “모든 핵종”의 구분

현재 집합은 문서가 열거한 n, H1/D/T, He3/He4, Li6/Li7의 원자 전하 상태다. n/T는 main에서 zero inventory이며 decay map 검증은 별도다. Be7의 표준 조기 전사는 선택한 Li7 초기량에 반영하는 조건이다. 음이온, 분자, Li8/9 같은 다른 핵종, 각종 nuclear resonances, late injection/production은 포함하지 않는다.

따라서 “명시한 21개 상태의 실제 결합 ODE”는 정당한 headline이다. “알려진 모든 isotope/ion/nuclear reaction을 완전히 계산했다”는 headline은 부정확하다. 200 eV source의 photonuclear support 부재와, 열핵반응 자체를 선택한 generator에서 제외했다는 사실도 구분해야 한다.

## 7. R1–R10와 후속 완료 주장

| 단계 | 이 snapshot에서 확인한 범위 | 확장하지 않는 주장 |
|---|---|---|
| R1–R3 | 질문·최신 근거 재사용·최대 세 후보 비교와 finite number-network 선택 | 모든 원격 대화/문헌을 무한히 조사했다는 완전성 |
| R4 | frame, norm, SI kappa, state inventory, 시간구간 정의 | 모든 핵종/closure의 완성 |
| R5 | source-preserving GR/moment 식과 scaled abundance/collision Jacobian | 연속 PDE 또는 모든 parameter의 오차 인증 |
| R6 | prescribed T/UV와 net gas power 항등식, test-fluid 진단 | 닫힌 열·복사 에너지 모형 |
| R7 | 고정 원표·source coefficient 재사용과 isotope/yield 근사 표시 | isotope-resolved yield의 독립 검증 |
| R8–R9 | CAS receipt와 finite code check 재사용, 상쇄/feedback 반례, 남은 범위 표시 | 검토자의 새 ODE 실행 또는 전역 안정성/수렴 정리 |
| R10 | 허용 범위 안의 125개 full-interval 계약과 별도 control 구성 | 결과 receipt를 읽기 전 125+1 완주·그림 통과 |

따라서 **R1–R10의 유한 이론·설계 루프는 구성되어 있다.** 실제 신규 실행, payload 확인, four-figure 렌더/시각검토, 최종 DAG publication/backup의 완료 표시는 각각 해당 receipt가 나온 뒤에만 붙인다. 이 문서는 그 후속 실행 완료를 대신하지 않는다.

## 남긴 명확성 메모

차단 code defect는 없다. 최종 THEORY/README/figure 설명에는 아래 세 표현을 유지하거나 더 명확히 해 두는 것이 좋다.

- `f_m=.1`은 Ω_m 기준의 비바리온 component 배정이다.
- opacity-off control의 tau는 potential electron-column diagnostic이고, UV isotropy는 외부 처방이다.
- 작은 trace-energy ratio와 finite angular checks는 누적 오차 상한·전역 양성·complete EoR certification이 아니다.

원자 저자가 자기 코어까지 독립 감사했다고 기록하지 않는다. 전체 source bundle에 대한 완전 독립 audit claim도 이 결합 검토로 만들지 않는다.
