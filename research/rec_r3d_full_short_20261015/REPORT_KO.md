# REC R3d: 원본 HyRec FULL H-only causal accepted-history 단기 적분

작성일: 2026-10-15 KST. 본 작업은 독립 격리 브랜치 `research/rec-r3d-full-accepted-step-20261015`에서 이루어졌다. 원본 REC dirty checkout, REI production, checkpoint, NCP 작업은 수정하지 않았다.

## 원전 및 immutable baseline

- 부모 REC: `8071d2e26d1befe2efe4599c5abd416d90e5e031` (PR94).
- 원본 2012 HyRec ZIP SHA256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
- 원본 HyRec FULL atomic one-step: REC PR93의 `full_2012_atomic_source.py`; 2 real + 311 algebraic virtual, diffusion 80-bin banded Schur, 원본 C와 기존 독립 비교를 재사용한다.
- 원본 photon retarded operator: REC PR92의 `causal_virtual_redshift.py`; 광자 이력 `iz`번째 비승인 column을 읽지 않는다.
- REI 기존 프리미티브 초기조건 후보 PR94와 REI PR150 production 코드는 별도 소유권. 이번 실험으로 변경하지 않았다.

## 이론과 계산형식

Signature `(-,+,+,+)`, 고유시간 `t`, 광자 energy `E`에 대해
`ds²=-c²dt²+a²(e^{-2b}(dx²+dy²)+e^{4b}dz²)`.
`H=ȧ/a`, `s=ḃ`, `q=s/H`, `θ=3H`,
`σ^i_j=diag(-s,-s,2s)`, `Σ²=σ_ij σ^ij/2=3s²`.
방향 코사인 `μ`에 대해 `d ln E/dt=-H-s(3μ²-1)`,
`dμ/dt=-3sμ(1-μ²)`. Face→emission `d=ln(a_face/a_em)>0`에서
`E_em/E_face=e^d[(1-μ_face²)e^{-2qd}+μ_face²e^{4qd}]^{1/2}`.
이 마지막 식의 q=const 실험은 정확한 Killing 운동량 운동학이며 원시 고-z Bianchi 배경 dynamics를 제공하지 않는다.
개별 방향의 미래 방향 적색편이가 모두 양수가 되려면 `-1/2<q<1`이다.
정상 FLRW에서는 `q=0`, `E_em/E_face=e^d`.

실제 구현 범위는 `q=0`의 H-only toy 초기조건에서
`d x_HII/d ln a = F_FULL[x_HII,T_m,fplus]`, 여기서
`F_FULL`은 원본 2012 HyRec effective rates + Lyman line + 2-photon/Raman/diffusion의 원자 2+311 선형계 Schur 솔루션이다.
`fplus_i`는 오직 `fminus_j` (j<i)의 retarded characteristic으로 얻으며
단일 time-step마다 새로운 photon outgoing column을 승인한다.
수소 ODE는 명시적 Euler, 물질 온도는
`T_{i+1}=(T_i+h Γ_C/H*T_rad)/(1+h(2+Γ_C/H))`
로 양수 보존형 backward-Euler Compton/adiabatic 처리를 수행한다.
311개 virtual 상태는 *algebraic*이며 independent ODE 변수로 늘리지 않는다.

새 `src/full_bianchi_hyrec/trajectory/short_full_history.py`에서
`virtual[:,i]`와 `lyman[:,i]`는 column-major로 미리 할당한다.
현재 'zero prehistory'는 (z=900)에서 임의의 광자 스펙트럼 경계조건을 둔 것으로,
과학적으로 실제 원시 재결합 photon history와 다르다. 첫 source redshift는 byte-exact 입력을 보존하도록 roundtrip 오차를 없앴다.

## 직접 실행 증거

- 로컬 owner-PC Python 3.12/NumPy2.4.2/SciPy1.17.0, 24 logical CPUs/31GiB: quick REC **484 PASS, 41 deselected**, 집중 16 PASS/1 slow 제외. 원본 unmodified HyRec C source parity slow targeted **1 PASS**.
- 실제 Wolfram 15 + local xAct `xTensor 1.3.0`에서 metric compatibility, 방향 적색편이율, 공간 3체적 (a^3), 횡/종 운동량 anisotropic Jacobian1, FLRW q→0의 5개 항등식 확인. 코드는 `XACT_CHECK.wl`.
- Fixed Δln a=0.0003396, 16/32/64 intervals: x_HII endpoint=[0.038971369005575594,0.03898146538861644,0.03898466228145945]; Tm endpoint=[2454.334843344795,2454.448425718066,2454.497165826266] K. Successive difference ratios x=3.15819, T=2.33037. 무한격자 정확해라고 추정하지 않는다.
- 4 cases ×45 steps: 단일 스레드 중앙값 ~0.19023 s, 2-thread ~0.23238 s, serial/parallel speedup 0.81863; 이 짧은 workload에서 병렬화는 회귀다. 원본 banded operator와 preallocated spectral history 최적화만 유지. 실제 native solver 64 CPU speedup은 측정하지 않았다.
- 원본 2012 native-C source one-step parity는 부모 PR93의 별도 4-point 증거와 regression으로 연결하되 이번 짧은 궤적 자체가 전체 native-C FULL historical series와 일치했다고 주장하지 않는다.

## 불변식과 claim admission

`ESTABLISHED`: null-geodesic photon Liouville/HyRec의 원전 설명.
`DERIVED/XACT_CHECKED`: 국소 Bianchi-I redshift/map/kinematic identities.
`IMPLEMENTATION_VERIFIED`: 유한 구간 source-owned history causality, snapshot Schur algebraic residual, thermal positivity, zero-prehistory repeatability.
`NUMERICALLY_CHECKED`: 위 3격자 수렴 추세와 local thread benchmark.
`UNRESOLVED`: C-accepted self-consistent FULL primordial integrated photon spectral history parity, HeI/HeII 초기조건 온전한 이력, dynamical high-z signed Bianchi Einstein–Boltzmann–recombination, 새로운 REI native ionization/optical depth.

## REI 연결의 정확한 경계

REI 별도 브랜치 PR150에서는 기존 PR94 source-actual FULL H+He q=0 donor x_e=0.000210349192936, Tm=9.306042400380866 K가 **DISABLED** 조건부 비교 초기조건으로 남는다. PR150 원본 config의 Git blob SHA `d9dcdbb4b33ebfe89f6c1322cba2a83a7bab15a6`과 read-only local snapshot byte 동일성을 검사했고, `rei_donor_config_audit.py` 및 6개의 신규 fast 테스트로 설정 drift/미승인 채택을 검출한다. Source scenario SHA256 `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`을 고정한다. 원시 `z=900` toy 짧은 H-only trajectory에서 `z=20` REI IC를 새로 내보내지 않는다. 먼저 REI PR150의 1-step native chemistry/thermal/photon ledger와 후보 IC의 동일상태 재실행 비교를 별도 sandbox에서 수행해야 한다. 사용자 확정 범위를 벗어난 high-z signed-q back-extrapolation은 관측·예측으로 인정하지 않는다.

## 복구 진입점

`PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m pytest -q -m "not slow"`

`PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/benchmark_r3d_full_short.py`

`wolframscript -file research/rec_r3d_full_short_20261015/XACT_CHECK.wl`
(xAct 1.3.0 installed in owner Wolfram Applications or located in isolated `xact_runtime`)

다음 물리 단계는 original HyRec FULL accepted photon history에서 실제 원시 경계조건으로 시작한 독립 H-only 전체 궤적을 native C와 대조하여 지속적인 오차 감소를 확인하는 것이다. 그 이전에는 새 계산을 REI 초기조건 권위로 승격시키지 않는다.
