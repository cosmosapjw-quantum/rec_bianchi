# REC C10 & 새 이론 R1: Bianchi I 광자 위상공간 보존과 릴리스 판정

2026-10-15 KST. 사용자 지시대로 **별도 local Codex 없이 이 대화에서 직접** REC 소스를 구현·검증했다. 원래 유한 시계의 이론 R10은 선행 사이클에서 닫혔고, 이번에는 **코딩 C10 실제 릴리스 판정**과 명시적으로 요청한 *다음 이론 연구*의 새 R1(광자 수·에너지의 물리 source bridge)을 선택했다. R2–R10을 자동 완료하거나 원래 물리 범위를 다시 정의하지 않는다.

## 실제 원본과 과학 범위

REC C9 부모 draft PR88: 72316baef363930fda109b3a9beeaf6aa39dbd9c. 새 작업은 별도 detached Git worktree에서 수행하므로 사용자의 기존 REC dirty checkout HEAD/파일을 덮어쓰지 않는다. REI native owner PR117 HEAD 129627969dae18958ceef520c197bfa8b20b8888에서 AX07 conditional pass, AX08 IN_PROGRESS, AX11·AX12 PENDING, full scientific admission NOT_ISSUED. REI의 기존 SOURCE07 Rust 방향별 SoA와 cohort 압축은 별도 owner 동작이고 이번 REC에서 native 실행·수정은 0회다. 최근 BASS_HE PR59에는 세 번째 warm P01 saved-cell의 원자물리 4 gas + 2904 photon error carry가 있고, bass_cr PR67에는 방향별 안전성을 강조한 cohort/Verner vectorization, WU088_HH PR75에는 two-centre angular 물리의 별도 solver 작업이 있다. 출처와 초기조건·차원·온도/밀도 영역이 다르므로 이들을 REI cold scalar 직접 검산이라고 재명명하지 않는다.

물리: ds²=-c²dt²+a²e^(-2b)(dx²+dy²)+a²e^(4b)dz², signature (-,+,+,+), L=ln(a/a_ref), q_ref=0,±0.005,±0.01; a_ref=1/21, a_face=0.1, s=dot b, shear diag(-s,-s,2s). Frozen prescribed normal-comoving LRS Bianchi I, H²=H_FLRW²+s². 현재 솔버는 광자 free streaming과 주어진 스칼라 j>=0, χ>=0 source를 검사하는 원자물리 독립 oracle이다. 새로운 전체 HyRec Einstein+Thomson solver로 간주하지 않는다.

## 새로운 이론 R1에서 고정한 물리 명제 및 실제 기호 검산

두 사건 initial 1→face 2, ΔL=L2-L1>0, B=b1-b2=-Δb. Face 방향 μ2의 photon energy 방향 사상은

R²=e^(2B)(1-μ2²)+e^(-4B)μ2²,
E1/E2=e^(ΔL)R,
dΩ1/dΩ2=R^(-3),
n1_perp=e^B n2_perp/R, n1_z=e^(-2B)n2_z/R.

따라서 (E1/E2)^3(dΩ1/dΩ2)=e^(3ΔL)이며 Δb가 **완전히 약분**된다. 이 identity는 일정 Killing 공간운동량 p_i=a e^(β_i) E n_i와 Liouville 위상공간 측정량의 일치다. 공간적으로 homogeneous한 충돌 없는 광자 수 n_gamma는 a^-3로 감소한다. 중요한 차이는 photon *energy*에 전단 방향별 redshift가 남는다는 것이다. 초기 isotropic f1(E1)을 가정하는 특정 동질 사례에서

rho_gamma,2/rho_gamma,1=(a1/a2)^4 * (1/4π)∫R^(-4)dΩ2
=(a1/a2)^4 A(B),

A(B)=1+(8/5)B²+(16/21)B³+(8/35)B⁴+O(B⁵).

Wolfram15.0.1에서 Jacobian·cubic identity와 4차 expansion 계수를 정확히 0 잔차·유리수 계수로 검산했다. Wolfram Engine15.0.0 + xTensor1.3.0에서는 Killing 대칭 미분의 추상 항등식, photon number 및 energy current의 Leibniz 법칙 3개가 정확히 0이었다. Killing 결과의 완전한 물리적 사용에는 null geodesic k와 ∇_(a ξ_b)=0이 필요하며, 단순 xAct 영잔차가 실제 충돌 항 0을 검증하는 것은 아니다.

**새 R1 연구 질문:** 이 두 물리적으로 다른 number/energy invariant를 REI의 각 source-age/ray cohort에 독립적으로 결속하면, 방향·시간·에너지 압축 때문에 생기는 거짓 비등방성이나 photon heating bias를 어떤 수치 지표로 분리할 수 있을까? 이후 R2 단계에서는 실제 SOURCE07·BASS_CR·warm HE photon payloads의 차원/normalization/clock/source lineage를 수집하여 이 식을 **충돌 없는 transport suboperator의 검증 기준**으로만 적용한다. Collisional ionizing source/escape/heating에는 원자별 ledger 추가 및 실제 source-coupled 계산이 필요하다. 새 이론 R1만 DONE; 새 R2–R10 NOT_RUN.

## C10 실제 코드 수정과 RED/GREEN 기록

새 REC 정식 모듈 src/full_bianchi_hyrec/trajectory/axisymmetric_phase_space.py, API axisymmetric_phase_space_map, prepare_axisymmetric_phase_space_map, PreparedAxisymmetricPhaseVolume, AxisymmetricPhaseVolumeMap; trajectory/__init__.py 공식 export. 배열의 E1/E2, dΩ1/dΩ2, normalized cubic phase volume, n1 및 logR을 read-only로 반환한다. `logR=B+.5 log1p(mu² expm1(-6B))` 형태는 tiny B에서 sqrt of near-unit quantity로 잃기 쉬운 물리 정보를 보존한다. Result dataclass와 source SHA256 및 exact log interval method identity는 분리한다.

첫 테스트 단계에는 모듈 자체가 없는 import RED였다. 구현 후 14 PASS. 이어서 매 호출 내부 clock integral을 반복하는 편의 함수가 작은 광선 수에서 scalar보다 훨씬 느리다는 실제 benchmark를 얻어, **source + (L1,L2) 초기 결속만 1회 수행**하는 prepared provider를 추가했다. 처음 provider 부재 RED, 추가 후 추가 3 tests 포함 17 PASS. 잘못된 q/좌표/방향 거부 및 전체 하늘 Jacobian·independent mpmath75 energy integral 교차검산 포함. 원래 C9 벡터 scalar positive transport 경로는 건드리지 않았다.

실측 a_ref→0.1, one-off positive shear integral 약 5.18ms. Preparatory cost를 공평하게 제외한 matched scalar math loop 대비:
- 64 rays 0.0375ms vs prepared vector 0.0694ms: scalar가 빠름.
- 1024 rays 0.556ms vs 0.1355ms: prepared vector **4.10x 빠름**.
- 8192 rays 4.671ms vs 1.385ms: prepared vector **3.37x 빠름**.
같은 공급자라 해도 cold one-shot vector 함수는 매 호출 shear integral 재계산으로 느릴 수 있으며, benchmark JSON에서 cold/perpared 측정이 구분된다. 이것은 **같은 finite null analytical map과 source-bound ∆b**를 공유한 비교다. 이전 C9의 98–846x는 상대 scalar ODE solver baseline가 다르므로 이번 수치와 혼동 금지. 1-worker vectorized CPU default; 이전 16,384 rays 2·4 ThreadPoolExecutor 실측이 각각 더 느렸으므로 무조건 병렬화하지 않는다.

새 과학 수치 script measure_phase_volume_c10.py: q 0,±.005,±.01, Gauss-Legendre96, independent 75-digit mpmath 전단 및 full-sky ∫R^-4. 5개의 full-sky photon number normalized Jacobian 값은 1과 2.3e-16 이내. Energy-factor parity-even correction q=.01/q=.005 = **3.999864854890417**. 이것은 q² leading geometry response이지 가스 이온화/He thermal response의 수치 검출이 아니다. C10_ENERGY_SHEAR_PARITY.png에 signed q 및 유리계수 4차 근사 대조를 제작했다.

## C10 release gate와 CI 실제 결함

부모 PR88의 GitHub workflow #38655925867는 2026-10-14 23:44 UTC에 실패했다. jobs를 읽은 결과 install/editable import까지 PASS, `scripts/verify_repo.py --quick`의 **이전 source-derived SVG/CSV/원시 stdout과 과거 원본 theoretical handoff의 줄 끝 공백**에서 FAIL, 이후 pytest는 SKIPPED였다. 이것은 실제 Python/science failing test가 아니다.

최소 수리: scripts/check_commit_range_whitespace.py의 DEFAULT_EXCLUDES에 실제 원본 줄끝 공백 FAIL로 특정한 **11개 path만 명시적으로** 추가하고 오래된 자료의 원시 byte identity는 그대로 유지했다. generic *.py/*.md/*.csv에 대한 공백 검사는 계속 작동한다. 두 음성 회귀를 포함한 tests/test_commit_range_whitespace_policy.py 5 PASS. 실제 PR88를 체크아웃한 별도 worktree에서 기존 feature-base `e6b64e0d...`에 대한 `check_commit_range_whitespace.py`와 `verify_repo.py --quick` 둘 다 PASS를 실행 관측했다. 원본 자료를 수정하거나 원래 feature-base SHA를 조작하지 않았다.

같은 격리 worktree에서 Python3.12, NumPy2.4.2 및 1-thread BLAS로 정식 `python3 -m pytest -q` 458 collected: **421 PASS, 37 SKIP** (--run-slow가 필요한 heavy cases). Runtime ≈52.72s. 이번 test command exit0. GitHub Python3.13의 새 PR workflow는 실제 게시 뒤 별도 검증해야 하므로 **아직 CI green이라고 주장하지 않는다.**

C10 판단:
1. 연구용 REC normal-comoving axisymmetric collisionless photon phase-map 라이브러리: **SCOPED_READY_FOR_REVIEW**. 정확한 q/clock/angle domain, 실제 실행/소스 및 작은 증분 경계 테스트 확보.
2. 연구 코드의 재현성·수치 오차: **SCOPED_PASS**. Full 421 PASS / 37 deferred + mp75 + xAct 별도 근거.
3. REI native Rust full photon/ionization / Full HyRec production: **HOLD_NOT_ADOPTED**. AX08 signed family, AX11 convergence, AX12 source/IC, original H/He rates, material energy and photon number/energy ledgers, observer angular transform과 실제 원자/복사 결합의 수용 기준이 미해결.
4. PR 출시 경로: **DRAFT_C10_PR_UNTIL_GITHUB_CI_TRUE_GREEN**. 문서와 numeric bytes 원본 공급자는 새 SHA lineage로 보존; original C9 Git commit 72316ba... 및 ZIP identity 불변.

## 다음 실제 실행점

REC finite-clock theory R10 completion과 C10 source release boundary는 새 R1에서 재개/확장될 수 있다. 별도 user invocation 없이 이 새로운 R1 다음의 R2–R10 또는 C1을 자동 수행하지 않는다. 다음 source/coupling 연구 과제는 실제 REI SOURCE07 native observer/packet q-cohort의 photon number/energy payload와 독립 Bianchi-I Jacobian factor을 연결하는 최소 adapter와 acceptance benchmark다. 물리적 유효성이 확인되기 전에는 q-dependent photon cohort를 energy-only merge하거나 REI runtime/STATE/checkpoint를 교체하지 않는다.

관련 주요 문헌: Fleury, Pitrou & Uzan, Phys. Rev. D 91 (2015) 043511 DOI 10.1103/PhysRevD.91.043511; Egger & Schlottbom, SIAM J. Numer. Anal. 54 (2016), DOI 10.1137/15M1051336; Rothman et al. (2022) general-relativistic implicit radiation-matter transport, DOI 10.3847/1538-4357/ac75cb (source coupling distinction). 이론 novelty와 우주론적 실측 가능성은 이번 stage로 주장하지 않는다.
