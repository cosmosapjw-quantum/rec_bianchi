# 전체 125-case 저장 결과: 독립 판독

**판정: PASS_ALL_125_SAVED_TRAJECTORIES.** `results/pilot_v2`의 125개 COMPLETE, RESULT, NPZ를 모두 읽었다. 새 적분이나 RHS 평가를 수행하지 않았으며 project physics module도 import하지 않았다. 전체 모형의 수치 정확도나 물리적 완전성을 인증하는 판정은 아니다.

## 확인한 산출물

- frozen campaign: 초기 Σ_F 5개 × signed matter stress 5개 × signed radiation stress 5개 = 125개.
- case마다 193개 z20→2 저장 노드, 전체 24,125개 time node.
- 각 raw state는 62개; 실제 21종 isotope/ion abundance와 6개 signed stress/shear 관측량을 별도로 보존.
- NPZ 전체 22,172,552 byte. COMPLETE→RESULT→NPZ의 size/SHA와 case scientific identity가 모두 일치.
- 현재 frozen source 파일도 모두 일치하며, case 설정의 누락/중복 없음.
- v2에는 새 claim 124개와 data-only 복구 1개가 있다. 복구된 한 case도 이번 새 물리 campaign의 첫 실제 적분에서 나온 결과이며, 과거의 729-case 결과를 재계산한 것이 아니다. 첫 적분 1개+후속 124개가 전체 125개 궤적을 구성하고 복구 자체의 ODE 실행은 0이다.

## 저장 자료에서 독립 계산한 값

| 진단 | 전체 case/저장 지점 범위의 값 |
|---|---:|
| baryon inventory 최대 절대차 | 1.5543e-15 |
| isotope inventory 최대 scaled 차이 | 2.3283e-15 |
| initial Σ_F/P_m/P_r target 최대차 | 3.3307e-16 |
| signed matter+radiation 합 최대차 | 2.1684e-19 |
| signed gamma+nu 합 최대차 | 1.0842e-19 |
| raw state로 재구성한 Σ_F 최대차 | 2.2204e-16 |
| raw photon multipole로 재구성한 signed Pi_gamma 최대차 | 1.3010e-18 |
| raw neutrino multipole로 재구성한 signed Pi_nu 최대차 | 1.1926e-18 |
| ne=nb q·Y 관계 최대 scaled 차이 | 5.5097e-16 |
| 최소 scaled population | 0 |
| n/T의 최대 절대 abundance | 0 |
| radiation number monopole 최대차 | 0 |
| photon energy 129-angle 최소값 | 0.207319 |
| photon number 129-angle 최소값 | 0.279015 |
| neutrino energy 129-angle 최소값 | 0.168726 |
| neutrino number 129-angle 최소값 | 0.242517 |
| 최대 thermal+ionization+UV energy fraction | 2.1940642e-8 |
| accumulated τ_T(z20→2) 최종 범위 | 0.0692155865–0.0693407679 |

각도 복원은 저장 raw multipole에 대해 Legendre 3항 recurrence로 basis를 별도 구성해 수행했다. 원 코드가 저장한 네 energy/number angular minima와 일치한다. 193개 시간 지점과 129개 각도 지점의 유한 검사이며 전체 연속 시간·각도의 positivity 정리가 아니다. Σ/γ/ν normalization은 frozen cosmology와 SI 상수로 재구성했다. massive matter momentum 적분 자체를 이번 데이터 판독에서 새로 재계산하거나 독립 적분하지는 않았다.

gas pressure, trace-energy fraction, bath-minus-escape의 저장 식도 원자 Y와 ne/diagnostic column으로 대조했다. H/D, He3/He4, Li6/Li7의 scaled charge histories 차이는 각각 최대 7.77e-16, 1.33e-15, 1.78e-15다. 이는 채택한 elemental electronic equality에 따른 결과이며 동위원소별 정밀 원자율을 검증한 결과가 아니다.

작은 보존 잔차와 데이터 항등식 차이는 구현과 저장 일관성의 근거다. 이 값을 ODE 참해 오차 상한으로 사용할 수 없다. τ는 z20에서 z2까지의 누적량이며 관측자의 z0까지 광학깊이와 동일한 양이 아니다. 초기 T/UV, Li inner-shell single-step charge yield, isotropic/test-fluid baryon과 제외한 반응의 조건은 그대로 유지된다.

`Physical HOLD`, `global convergence NOT_RUN`, `production NOT_APPROVED`, 기존 REC U5 HOLD는 유지한다. 모든 per-case hash와 수치는 `INDEPENDENT_RESULT_AUDIT.json`에 보존했다. 그림의 직접 시각 검토는 별도 receipt에 기록한다.
