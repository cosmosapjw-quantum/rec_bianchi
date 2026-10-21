# REC→REI 이론·문헌 검토: 분리 응력, 긴 구간, 보존 운동량

> **현재 선택 갱신:** 아래의 새 z4→2 적분 제안은 최신 다른 스레드의 완료된 237-tail 자료를 발견하면서 폐기했다. 현재 선택은 추가 ODE 없이 같은 원자료의 175 nominal cases ×153 epochs를 사용하는 **63축 support /112 mixed full-trajectory retrospective comparison**이다. 유효한 최신 계약과 유도는 `TRAJECTORY_THEORY.md`, 판정은 `SCIENCE_CONTRACT_REVIEW.json`을 읽는다. 아래 탐색 결과와 CAS는 역사적 근거로 보존하며 새 실행 권한으로 쓰지 않는다.

검토일: 2026-10-21 (KST). 역할: 원자료 기반 독립 scientific review. 새 ODE/benchmark는 실행하지 않았다.
실제 도구: Exa 2검색·11요청결과, SciSpace 1질의·10결과, Exa 원전/공식 문서 fetch, Wolfram Language evaluator 1성공 호출.
Wolfram 최초 JavaScript 포장 시도는 SyntaxError로 도구 실행 전 실패했고, 문자열 포장을 고쳐 실제 1회 실행했다. 원출력의 Symbol::undefined2 경고(A를 symbolic parameter로 사용)를 보존했다.

## 1. 선택과 출처

선택할 과학 단위는 **동일 collisionless owner를 유지한 zbar=20→2 독립 matter/radiation pilot 또는 저장 zbar=4 상태에서의 새 4→2 연장**이다.
기존 z20→4의 축·혼합 사례가 같은 초기조건으로 존재하면 해당 prefix를 재사용한다. 완료된 warm C15 729개는 별도 조건의 complete_reused 입력이다.
REC의 anchored153 endpoint reducer는 긴 구간 mixed trajectory 대용으로 사용하지 않는다.

읽은 실제 코드:

- HH128 source92f5ab9dba531ebe05909dcb77d3740d2c68c580, research/hh_phys75_sector_memory_20261021/source/radiation_flow.py.
- REI198 source materialized by survey agent, owner/pilot.py, owner/matter_radiation_20261021/component_pilot.py 및 CONTRACT_KO.md,
  vendor/canonical_fv.py, vendor/REI_BACKGROUND_FAMILY_LOCK.json.
- REC116 4cffa8a0abdb104a40cac17cfc65593bec909fb3, research/rec_rei_axis_reuse_20261021/README_KO.md.

각 materialized source의 정확한 hash/remote commit 대응은 ../agent_survey/SOURCE_MANIFEST.json가 소유한다. 이 검토는 파일을 변경하지 않았다.

핵심 재사용은 이미 구현된 HH128의 8→3-state radiation exact representation이다.
HH128은 같은 고정 L8 충돌 없는 시스템의 5개 radiation ODE 좌표를 대수적으로 재구성한다. 상태 수 감소와 실제 speedup 측정은 서로 다른 주장이다.

## 2. 규약과 보존식

정상 관측자 orthonormal frame, metric(-,+,+,+), proper time t[s], H,s[s^-1], rho와압력[J m^-3].

a_perp=a exp(-b), a_parallel=a exp(2b), s=db/dt.
sigma=diag(-s,-s,2s); pi_A=diag(-Delta_A/3,-Delta_A/3,2Delta_A/3), A=m,r.
kappa_t=8piG/c²는 proper-time 방정식의 계수다.

half convention:
S=sqrt(3)s/H,
P_A=kappa_t Delta_A/(sqrt(3)H²),
Sigma=|S|, Pi_A=|P_A|,
Pi_total=|P_m+P_r|.

Frobenius 좌표는 위 값의 sqrt(2)배다. 먼저 signed stress를 합하고 norm을 취한다.
sigma:pi_A=2sDelta_A=6s p_A, p_A=Delta_A/3.

공간 Killing momentum q_i가 보존되는 Bianchi I에서 f(t,q_i)=f0(q_i).
LRS mass-shell energy를
E=[m²c⁴+c²(q_perp²/a_perp²+q_parallel²/a_parallel²)]^(1/2)
로두면, N=a^-3를 포함한 각 positive quadrature packet은

dE/dt=-c²[(H-s)q_perp²/a_perp²+(H+2s)q_parallel²/a_parallel²]/E,

p_perp,packet=c²q_perp²/(2a_perp²E), p_parallel,packet=c²q_parallel²/(a_parallel²E)

를 만족한다. 따라서 합산해도

dot rho_A+3H(rho_A+pbar_A)+2sDelta_A=0

가 보존된다. 이는 quadrature가 연속 적분과 정확히 같다는 주장이 아니라, 고정 quadrature packet의 에너지식이 독립적으로 보존되는 이유다.

Einstein 식:
3H²=kappa_t rho+3s²+Lambda c²,
dot s=-3Hs+kappa_t(Delta_m+Delta_r)/3,
dot H=-kappa_t(rho+pbar)/2-3s².

위 에너지식을 쓰면 constraint derivative는 정확히0이다. x=ln(a/a_ref), q_dec=-1-dot H/H²이면
S'=(q_dec-2)S+P_m+P_r.
초기 P_m+P_r=0은 현재 shear source의 상쇄다. 이후 두 성분 에너지와압력은 서로 다른 redshift/geometry 응답을 가져 별도 evolution이 필요하다.

## 3. 초기조건의 실현 가능 영역

기존 owner의 massive angular weight는 W_m(mu)=1+A_m P2(mu), P2=(3mu²-1)/2.
P2∈[-1/2,1]이므로 전 μ에서 W_m≥0 iff -1≤A_m≤2.

초기 b=0에서 angular 평균:
<W_m>=1,
<P2 W_m>=A_m/5.

따라서 초기 energy density와 isotropic mean pressure는 A_m에 독립이고, Delta_m=(3A_m/5)pbar_m이다.
유한 Gauss3 rule은 angular polynomial 차수4까지 정확히 적분하므로 같은 초기 관계가 고정 quadrature에서 roundoff 범위로 성립한다.
실제 source helper의 brentq inversion을 그대로 쓰면 source normalization과 현재 H를 보존한다.

source 계약은 fm=.1, mass/Tref=30, 24×12 cells, Gauss3, L8, rtol3e-11/atol3e-13이다.
signed S0=.004에서 source가 기록한 attainable P_m0≈[-.0004833821888780,+.0009667643777560].
따라서 symmetric P_m0=±.0004는 허용되고, ±.001은 이 source의 음의 분포 경계를 넘는다.
이 수치는 기존 source 기록을 재사용했으며 이번 agent가 신규 수치실행으로 다시 측정하지 않았다.

photons+massless neutrinos의 common initial brightness는 1+kP2(mu), E0=1,E2=k/5.
수학적 positivity 범위는 동일 [-1,2]지만 기존 owner는 더좁은 |k|≤.5를 채택한다.
후속 실행은 기존 |k|≤.5 제한을 유지한다. matter와 radiation의 k,A는 각 signed initial Pi target에서 따로 실현한다.
|S0|<sqrt(3) 조건에서 initial q=s/H_ref inversion이 실수이며, 현재 작은 축은 이 범위 안이다.

## 4. HH128 exact representation와 재시작

고정 real matrix M과 E'=b'(x)M E에 대해

E(x)=exp[(b(x)-b_i)M]E_i.

증명은 b(x)의 chain rule과 고정 M의 자기 가환성이다. b의 단조성은 필요하지 않다.
같은 M에서 임의 x_*를 지나도
exp[(b-b_*)M]exp[(b_*-b_i)M]=exp[(b-b_i)M].
그러므로 저장된 정확한 full state E_*,b_*,s_*,elapsed time을 사용한 z4→2 extension은 같은 finite system의 재시작이다.
불연속 source 추가/변경, Thomson collision, UV source, noncommuting coefficient matrix에는 이 식을 그대로 적용할 수 없다.

중요한 실행 구별:
- z4 저장 endpoint의 8-state 자체를 사용해 새 구간을 적분하면 old-prefix 재실행0.
- saved observer-only E0/E2로 E4/E6/E8을0으로 만드는 것은 원래 IVP 재시작이 아니다.
- 정확한 state가없으면 같은 source의 데이터 복원을 먼저한다. 새 독립 mixed 초기조건의 z20→2 적분은 completed trajectory replay가 아니다.
- 같은 atol/rtol을사용해도 8-state↔3-state의 adaptive norm과step sequence가달라진다. 이것은 algebraic equivalence와 별도의 numerical comparison 의무다.

기존 RadiationFlow는 |b-b_i|≤.05의 eigenbasis/expm1 경로, conditioning/residual check, 그밖에는 scipy.linalg.expm fallback을 사용한다.
finite moment closure L8과canonical momentum quadrature의 해상도는 그대로다.

## 5. 새 구간에 필요한 최소 과학 검사

1. source/initial triple identity 및 actual realized(S0,P_m0,P_r0) 오차를 기록한다.
2. 저장 prefix→새 continuation 접합에서 x,b,s,elapsed seconds,E0..E8이보존되는지 확인한다.
3. 새 terminal z=2, finite positive H/E0, nonnegative massive populations을 확인한다.
4. tensor signed sum, half/Frobenius conversion과sigma:pi component work를 확인한다.
5. 3-state대원래8-state의 새 구간 비교는 새 구간·새재시작 위험을 대상으로 제한한다. 기존 z20→4 completed scientific matrix를다시 돌릴 필요가없다.
6. fullcoldEoR/production/global convergence 판정은 기존 HOLD/NOT_APPROVED/NOT_RUN으로유지한다.

추가 가치가큰 경량 진단: 현재128 μ nodes에서만기록한 brightness minimum을 degree8 polynomial의 수치적 global minimum으로 강화할수있다.
B(mu)=sum_even_l(2l+1)E_l P_l(mu)에대해 candidates={-1,1}∪{real roots of B'(mu) in(-1,1)}에서B를평가한다.
numpy.polynomial.legendre.legder/legroots/legval을쓰면power-basis 변환을피할수있다.
중근·complex-near-real threshold의조건수때문에수치적 진단으로표기하며시간연속·interval certificate로부르지않는다.
실제 양성 margin이 O(1)라면이진단의 roundoff 영향과따로격리하기쉽다.

## 6. 문헌과외부코드채택

| 근거 | 확인한 내용 | 사용 결정 |
|---|---|---|
| Heinzle & Uggla, CQG23(2006)3463, arXiv:gr-qc/0512031 | Bianchi I에서covariant momentum을쓰면f=f0이고, energy/stress integrals가Einstein source를정함; reflection symmetry는 momentum constraint를충족 | canonical FV owner의물리적유래를문헌-supported로재사용 |
| Rendall & Tod, CQG16(1999)1705, arXiv:gr-qc/9811051 | LRS에서 f0(p1,p2²+p3²)의explicit Vlasov solution과massless energy tensor/ODE reduction | 현재 finiteL8를연속 exact kinetic solution이라고부르지않는범위구분 |
| Rendall & Uggla, CQG17(2000)4697, doi10.1088/0264-9381/17/22/310 | massiveLRS evolution의early massless/late dust asymptotic; finite intervalaccuracy를주지않음 | 해석용맥락만 |
| Rabitz & Alis, General foundations of high-dimensional model representations(1999) | cut-HDMR는low-order anchored components의계층적표현 | REC153 재사용식은기존개념, 새finite grid 결과의범위를유지 |
| Gao & Hesthaven, On ANOVA expansions and strategies for choosing the anchor point(2010) | anchoredANOVA는line/plane slices에서구성; anchor선택은정확도에영향 | endpoint153→long-window 대체의근거로사용하지않음 |
| SciPy official expm documentation | variable-order Padé scaling/squaring; Al-Mohy & Higham2009 doi10.1137/09074721X | HH128가이미채택한SciPy fallback그대로재사용 |
| NumPy official legroots documentation | Legendre companion eigenvalue roots, multiple/far roots conditioning주의 | 새 μ-min diagnostic에선택가능 |

URLs:
https://arxiv.org/abs/gr-qc/0512031
https://ar5iv.labs.arxiv.org/html/gr-qc/0512031
https://ar5iv.labs.arxiv.org/html/gr-qc/9811051
https://doi.org/10.1088/0264-9381/17/22/310
https://collaborate.princeton.edu/en/publications/general-foundations-of-high-dimensional-model-representations/
https://www.sciencedirect.com/science/article/abs/pii/S0096300310009252
https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.expm.html
https://numpy.org/doc/stable/reference/generated/numpy.polynomial.legendre.legroots.html

SciSpace는발견용이다. Heinzle–Uggla 항목의2022 메타데이터는원논문2006 publication과다르므로2006 primary문헌을기준으로삼았다. noncommutative/charged/Noether-symmetry 검색결과는현재source와관련없어채택하지않았다.
제3자코드본문을복사하지않았다. NumPy/SciPy는기존dependency 호출이며공식BSD계열 LICENSE를참조했다. 사용자소유HH/REI 코드는exact source/hash provenance를유지한재사용이다.

## 7. 실제 CAS 결과와범위판정

Wolfram returned:
tensor contractions={6s²,2Delta_m²/3,2Delta_m s,2(Delta_m+Delta_r)²/3};
single momentum energy residual=0;
constraint derivative=0;
normalized shear residual=0;
P2 angular averages={1,A/5};
positivity=-1≤A≤2.

입출력원문과경고: RAW_EVIDENCE.json.

- derived/CAS-checked: tensor normalization, energy identity, constraint propagation, signed shear equation, continuous initial P2 positivity.
- source-reviewed: ComponentReduced initial inversion, exact3-state finiteL8 reconstruction, restart semantics.
- literature-supported: conserved Killing-momentum Vlasov formulation, anchoreddecomposition의기존위치.
- not_run: 새 ODE/benchmark/performance claim.
- unresolved: newz2 trajectory 결과, 시간연속양성/전역수렴/fullcoldEoR.
- strong no-go: 새배제정리를채택하지않음; NG1–NG7 해당없음. 기존 finite-sentinel counterexample는원래scope로재사용.
