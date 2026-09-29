# Task3: 방향별 BB 커널과 sharp-line 측도

## 원문 및 변경 범위

WU29 §2와 §4 (7)-(10), T4 source interface §§2.1-2.2를 사용한다. 원문은 source_subset에 바이트 그대로 있으며 API_SOURCE_MAP.json에 원문/코드 hash와 줄을 고정한다. 이번 변경은 BB에만 적용된다. BF의 transpose 규칙, pair identity shortcut, D86와 Jacobs 값, 원자 상수, 기존 Python/C solver는 바꾸지 않는다. Task2 검사를 새 진입점에도 적용한다.

## 수식에서 함수까지

H=I2+F, b_shell=3A/(8pi), a_gamma=(h_P c)^(-3)에서

```text
B_shell = b_shell [n_lower V F V^T - {V H V^T, W_P}/2]
J_shell = b_shell [{H, V^T W_P V}/2 - n_lower F]
C_shell = J_shell / (a_gamma epsilon_J^2)
C_E(E,e) = C_shell delta_J(E-epsilon_J)
```

584에서는 n_lower=ng, A=A584, epsilon=DeltaP이고 IR에서는 n_lower=nS, A=AIR, epsilon=epsilonIR이다. 동일한 caller-owned WP를 두 channel에 건넨다. BB에 F^T나 WP^T를 새로 삽입하지 않는다.

`he_bb_kernel(channel,n_lower,wp,f,v)`는 한 방향의 unweighted B_shell/J_shell/C_shell과 tr(J_shell)를 반환한다. `he_bb_source(channel,n_lower,wp,&[WeightedBbMode])`만 weight_sr로 B 및 scalar event를 합산한다. 각 J/C matrix는 서로 다른 screen에 있으므로 한 2x2 matrix로 직접 합하지 않고 mode 순서대로 보존한다. 모든 F는 caller가 해당 line energy에서 평가해야 한다. 새 API는 spectrum을 추정하거나 interpolation하지 않는다.

B_shell와 J_shell은 m^-3 s^-1 sr^-1이다. 각도적분한 B와 event_rate는 m^-3 s^-1이다. C_shell은 delta_J를 곱하기 전의 J s^-1 계수이다. C_shell 자체를 occupation/s라고 읽으면 안 된다. `SharpLineDeltaPerJoule { energy_ev }`는 분포 규약이며 pointwise delta 값이나 유한 bin profile이 아니다. 이 API에는 energy bin width 입력이 없다. Downstream delta/bin 적분은 별도 소유자가 해야 한다. 새 Doppler/line-wing/tilt 가정은 넣지 않았다.

## Angular stencil

`audit_bb_stencil`은 실제 sum(weight)와 sum(weight V V^T), 각각 4pi와 (8pi/3)I3에 대한 residual을 반환한다. 두 residual의 기준은 승인된 4096eps 그대로이며 `full_sphere_moments_match`는 그 두 moment의 일치만 뜻한다. 일반 F(E,e)에 대한 quadrature convergence/정확도 증명이 아니다. 임의 부분 stencil도 합법적인 부분 source이며 weights를 rescale하거나 빈 방향을 채우지 않는다. B=-AWP는 full-stencil vacuum 시험에서만 요구한다. V만으로 방향 부호를 복원해서 four-force를 계산하지 않는다.

## 입력 및 API 이행

WeightedBbMode는 v:RealV, f:Mat2, weight_sr:f64를 가진다. source entry에서 finite/nonnegative n_lower, finite Hermitian PSD WP/F, real orthonormal V를 검사한다. Finite nonnegative weight를 받으며 zero weight도 mode validity를 우회하지 못한다. Empty stencil은 명시적 invalid다. Input validation 후 overflow 등 nonfinite arithmetic은 NumericalDomainUncertain으로 분리한다. Signed B/J를 PSD projection하지 않는다. 이 검사만으로 모든 f64 underflow나 오류를 증명한 것은 아니다.

기존 5-argument BB API는 승인된 0.1 API 변경으로 4-argument API가 된다. SharpLineConvention의 bool을 SpectralMeasure variant로 대체했다. Tests 8곳과 example 3곳의 호출을 함께 변경했다. 이전 isotropic fixtures의 F broadcast는 test/example caller helper에서 명시한다. Production wrapper가 임의의 anisotropic input을 몰래 broadcast하지 않는다. 다른 외부 consumer migration과 repository-wide caller census는 Task8/Local Codex에 남긴다.

## 근거 상태

bb_inputs_task3.json, bb_acceptance_task3.json, bb_reference_task3.json을 source 수정 전에 고정했다. Reference는 Fraction 복소 성분합으로 계산했고 Rust 출력에서 만들지 않았다. 네 작은 fixture의 component-index 식과 matrix-chain 식을 비교했으며, pointwise/합산 trace, 여섯 방향 vacuum, 유리수 LTE를 검산했다. 4가지 오류 대수는 반례로 검출했다. b_shell 누락을 실제 Rust 출력에서 검출하는 시험은 local에 남아 있다.

12개 새 Rust test와 기존 26개 이름을 유지한다. 원형 변경 때문에 기존 테스트 8개 call site와 spectral assertion을 기계적으로 이행했으며 기존 시험이 바이트 불변이라고 주장하지 않는다. Cargo fmt/test/clippy, full source parity, T4는 NOT_RUN이다.
