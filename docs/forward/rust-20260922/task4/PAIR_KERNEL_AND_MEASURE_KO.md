# Task4: pair screen tensor, marginal과 ordered quadrature

## Authority와 범위

WU29 §5.4 Eq.(16), §6 Eqs.(19)-(22), §7 Eq.(24), T4 source interface §2.5, WU31-A1의 D86 대체 규칙을 사용한다. WU29에 남은 CHIANTI normalization 서술은 원문으로 보존하지만 계산 authority는 WU31-A1이다. 같은 ng/ns와 real Cartesian material screens를 사용한다. BB/BF kernel, D86/Jacobs 표/보간, 원자 상수, 기존 Python/C solver는 수정하지 않는다.

## 수식과 API

```
PairInput { y, f1, f2, v1, v2 }
T12 = V1^T V2
H1 = I2+F1; H2 = I2+F2
M12 = (ns/2){H1, T12 H2^T T12^dagger}
    - (ng/2){F1, T12 F2^T T12^dagger}
M21 = 같은 식에서 두 photon 입력을 교환하여 별도로 계산
DeltaS_J = DeltaS_eV*EV_J
E1_J = DeltaS_J*y; E2_J = DeltaS_J*(1-y)
R_integrand = (1/2)*w(y)*g_ang*tr M12
C1_integrand = w(y)*g_ang*M12/(a_gamma*E1_J^2*DeltaS_J)
C2_integrand = w(y)*g_ang*M21/(a_gamma*E2_J^2*DeltaS_J)
```

`he_two_photon_pair_source(&PairInput,&SourceState)`는 unweighted M12/M21와 R/C integrands를 반환한다. T12는 일반적으로 unitary가 아니며 F2만 회전시켜 항등 screen을 대체할 수 없다. Source는 signed matrix로 PSD를 강제하지 않는다. M12와 M21는 서로 다른 화면이므로 같은 행렬로 취급하지 않는다. Caller가 F1/F2를 위 material energy에서 공급해야 한다. 이 API가 spectrum을 보간하거나 제공된 F가 해당 에너지에서 취득되었음을 독립 증명하지 않는다.

R_integrand의 측도는 dy*dOmega1*dOmega2, 단위는 proper density/s per dy per sr^2다. C1은 고정 E1에서 dOmega2 적분 전 occupation/s per partner sr이고 C2는 그 반대다. C는 에너지밀도가 아니며 photon number를 얻을 때 a_gamma*E_tag_J^2*dE_J*dOmega_tag를 적용한다. dE_J=DeltaS_J*dy는 assembly에서 한 번만 적용한다. Delta_J와 bin width를 추가하지 않는다. `PairMarginalMeasure`와 `SpectralMeasure::PairDyDOmega1DOmega2`를 별도로 표시한다.

## Full ordered grid와 두 tag의 계수

`WeightedPairMode`는 PairInput, weight_dy, weight_omega1_sr, weight_omega2_sr, exchange_partner를 갖는다. `assemble_he_pair_grid`는 `FullOrderedExchangeClosed`만 허용한다. Partner index가 범위 안이며 involution인지, F/V/각도 weight가 서로 바뀌었는지, dy가 같은지 검사한다. y와 1-y의 비교만 사전등록 4096eps를 사용하고 strict D86 band 검사는 그 전에 수행한다. 이 검사는 f64 consistency 검사이지 domain 확장이나 interval proof가 아니다. Partial band/sky quadrature는 partial result이며 weight rescale이나 missing-node 보충을 하지 않는다.

원문에서 각 marginal은 하나의 tag를 고정한 FULL ordered integral이다. 따라서 exchange-closed grid에서

```
R = (1/2) sum q*w*g*tr M12
N1 = sum (DeltaS_J*dy*dOmega1*dOmega2)*a_gamma*E1_J^2*tr C1
N2 = sum (DeltaS_J*dy*dOmega1*dOmega2)*a_gamma*E2_J^2*tr C2
P1 = sum E1_J*(같은 tag1 number contribution)
P2 = sum E2_J*(같은 tag2 number contribution)
N1=N2=2R; P1=P2=DeltaS_J*R
```

N1+N2는 4R이므로 두 full 추정치를 더하지 않는다. `[N1,N2]`와 `[P1,P2]`를 독립 비교용으로 반환하고 각각의 잔차를 기록한다. 수학적으로 교환 대칭 때문에 두 에너지합이 같고, 그 합이 2*DeltaS_J*R여서 각각 DeltaS_J*R다. 이는 이산 grid가 입력 그대로 교환 폐쇄된 경우의 항등식이며 실제 spectrum의 적분 정확도/물리 closure 인증은 아니다. 계획의 '두 marginal 독립 합산'은 이 의미로 실행하며, 커널에 extra 1/2를 넣어 맞추지 않는다. 이미 unordered half-grid를 제공하는 caller는 별도 authority 부재로 MissingAuthority다.

Integrated R을 ledger의 r2g에 넘길 때 다시 1/2를 곱하지 않는다. Ledger의 두 광자 계수와 C marginal의 number moment를 비교하는 local test를 작성했다. Task5의 전체 BF heat 및 material spatial four-force는 아직 별도 작업이다. V의 plane에서 propagation direction 부호를 추정하지 않는다.

## 입력과 수치 실패

Task2 guards로 state, F1/F2의 finite/Hermitian/PSD, V1/V2의 real orthonormal 조건을 검사한다. PairInput의 domain은 D86의 strict y band다. Empty grid, negative/nonfinite weights, broken exchange mapping은 오류다. Zero weight도 input 검사와 pair 계산을 우회하지 않는다. Nonfinite arithmetic 및 일부 nonzero-factor product underflow를 NumericalDomainUncertain으로 구분한다. 모든 f64 underflow/cancellation의 부재를 증명한 것은 아니며 local strict scale oracle가 필요하다. Output source에 PSD projection, normalization, LTE population forcing을 하지 않는다.

## API 이행과 근거

기존 4-argument pair API를 2-argument PairInput API로 교체했다. 기존 same-screen fixtures는 tests8곳과 example1곳에서 명시적인 test-only adapter로 이행했다. Production의 implicit identity wrapper는 없다. 기존 output의 pair_matrix/event_rate_density/weight metadata는 호환을 위해 보존하되 각 의미를 명시했다. 전체 repo의 외부 caller census와 compile-level migration은 Task8/local Codex의 소유다.

Fixture3개와 Rust test15개를 source 수정 전에 고정했다. Gaussian-rational component-index contraction과 matrix-chain를 네 fixture에서 비교하고, 9개 rational LTE mode, 8-node ordered grid의 독립 marginal moments, D86 20 nodes/reflection 및 19 midpoint를 toy로 검사했다. 7가지 오류 대수를 구별했다. Toy의 Delta=5/2, a_gamma=1은 단위 인자 검사를 위한 무차원 수이며 physical He constants를 변경하지 않는다. Actual Rust coefficient, toolchain format/type, all channel source parity, T4는 NOT_RUN이다.
