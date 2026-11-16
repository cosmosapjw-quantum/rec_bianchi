# REC → REI F08: 지속 편광 상태를 가진 원본 paired-runtime 결합 진화

## 결과와 범위

원본 F08 `paired_runtime`을 실제로 호출하면서 광자의 I/Q/U/V를 시간 사이에 보존하는 REC 수신기를 구현하고 실행했다. 충돌 후 방향별 광자 I가 다음 native H/He 계산의 입력으로 들어간다. 완결된 다섯 실험에서 **960 paired trials, 2,880 native endpoint calls, 800 편광 macro steps, 2,088,960 spectral-angular Stokes 행**을 계산했다. 결과는 **조건부 point evolution**이며 production과 원 owner admission은 **HOLD**, 모든 canonical DAG 증분은 **0**이다.

원본 tick142의 3% 실패를 실제 저장된 source ray로 재현했다. 인계문 이후 이미 존재하던 REC #200의 물리 tetrad·degree4 교정을 재사용했다. 이번 진전은 그 교정을 새 성과로 다시 세는 것이 아니라, 반복 충돌·screen 수송·스펙트럼 remap·native H/He feedback을 하나의 지속 상태로 연결한 것이다.

## 확인한 기준점

| 역할 | PR / HEAD |
|---|---|
| 변경하지 않은 REC 원 parent | #198 `fa5c484405e901992501ab01795079ed8f2bdee1` |
| 인계 당시 REC source | #199 `c10e97ab3178c423cc7699684b33e1730d26437a` |
| 재사용한 physical-tetrad 교정 | #200 `c995fb84a5523202ab429003a78d7d590b51ace9` |
| 원 F08 runtime owner | REI #83 `c07fc7e765ce204bc3e84016cc6874612e535b86` |
| 중앙 정본 | REI #375 `56dc609ea9b801c88d3364aed3eee140b3a20d46` |
| 원 BASS donor | #328 `b23c6915aeaeedbabbc8e90ffab74f2afa96c1e6` |
| 확인한 BASS 후속 | #331 `ea19c11ee3412b9fcbc8d3d07ec7c7eefcf7ddbf` |

원 F08 paired **input** SHA256은 `0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8`이다. `paired_runtime.rs` **파일** SHA256은 `b6c1d2a07ab51ff02318139ae18387b77f61859c08037347f788524df770ebe7`이다. 서로 다른 객체의 identity를 구분한다.

실행 소스는 기존 REC199 source-full ZIP에서 복원한 원 BASS 106-member archive다. **12 S0 + 51 Rust + 4 photon** 파일의 원 해시를 확인하고, 원 Rust crate를 수정하지 않은 채 별도 bridge를 `cargo build --release --locked --offline`로 빌드했다. 원 native module을 별도 executable의 module surface에 노출했으며 owner 저장소의 파일·branch는 수정하지 않았다. 이미 검증된 과거 640-stage byte-exact replay는 재사용했고 이번에 다시 실행한 것으로 세지 않았다.

## 실제 물리·시간·상태 계약

원본은 상수 diagonal H를 가진 non-tilted Bianchi I다.

\[
(H_x,H_y,H_z)=(1.01,0.99,1.00)\,10^{-14}\ {\rm s}^{-1},
\quad \Delta t=6.25\,10^8\ {\rm s},\quad t_{\rm end}=10^{11}\ {\rm s}.
\]

이는 실제 source 값으로 **triaxial**이다. 중앙 AXBI의 축대칭 시나리오로 바꾸지 않았다. FLRW control은 세 H가 모두 \(10^{-14}\,{\rm s}^{-1}\)다. 원 photon normalization은 photons/H, 에너지는 eV/H이고, 17개 공통 physical-energy node와 q128을 사용한다. source는 원 birth energy 13.7 eV, 초기 photons/H 0.05, emission rate \(5\times10^{-15}\,H^{-1}\,{\rm s}^{-1}\)다.

각 macro step의 순서는 다음과 같다.

1. 원 Rust `paired_trial`이 full comparison과 두 half endpoints를 계산한다. 원 local `<2e-4`, public width `<2e-3`, ledger `<=1e-12` 기준을 변경하지 않는다.
2. 실제 채택된 두 half endpoints의 audit만 사용해 기존 I/Q/U/V를 원 spectral hats로 remap하고, 동일한 absorption factor를 모든 Stokes 성분에 적용한다. 새 source는 I에만 추가한다.
3. 실제 ray 경로를 따라 triaxial screen connection을 적분한다. \((Q+iU)_1=e^{-2i\Omega}(Q+iU)_0\)이며 \(\dot\Omega=n_z(H_x-H_y)n_xn_y/(n_x^2+n_y^2)\)다.
4. 같은 endpoint의 H/He state에서
   \(n_e=n_H[x_{\rm HII}+0.083(x_{\rm HeII}+2x_{\rm HeIII})]\),
   \(n_H=10^{-4}\exp[-(H_x+H_y+H_z)t]\,\mathrm{cm}^{-3}\)를 계산한다. \(\tau=c\sigma_Tn_e\Delta t\)로 충돌을 진행한다.
5. collision 후 I와 guard N/U를 다음 native trial에 입력한다. 기존 Q/U/V도 이어서 수송한다.

탄성 충돌은 **동일 physical energy**의 방향 사이에서만 일어난다. 따라서 각 에너지 group의 총 광자 수, 즉 순간의 scalar H/He photo-rate와 elastic energy를 보존한다. 이후 비등방 redshift에서 방향과 스펙트럼이 다시 결합할 수 있다. F05의 46,080-cell source·OTS clock·상태는 입력에 들어가지 않는다.

## 충돌식과 실제 추가 근사

물리 tetrad 방향 \(n_i\), \(P_i=1-n_in_i^T\), 양의 degree4-exact 가중치 \(\sum_iw_i=1\), coherency mass \(S_i\)에 대해

\[
\frac{dS_i}{d\tau}=\frac32w_iP_i\left(\sum_jS_j\right)P_i-S_i
\]

를 정확한 유한 optical-depth 반군으로 계산한다. 전체 coherency moment의 scalar·real STF·imaginary antisymmetric 성분은 각각 감쇠율 \(0,3/10,1/2\)를 갖는다. 양성성·횡방향성·trace 보존의 유도와 작은 \(\tau\)에서 안정적인 increment 식은 `THEORY.md`에 있다. 이 선형 연산자는 별도의 정규화를 하지 않는다.

원 q-cell continuum samples에는 별도 adapter가 필요하다. \(A_i=w_i/J_i\), \(J_i=d\Omega_n/d\Omega_q\)로 물리 질량을 구성하고 역변환 뒤 각 physical-energy group의 원 총량으로 정규화한다. 이는 **비선형 collocation 근사**다. 유도된 generator에는 상태 의존 scalar extinction correction \(-\kappa(T)T_i\)가 추가된다. 실제 160-step BI 실행에서 단계당 raw inverse-projection drift의 최대치는 \(2.16803\times10^{-15}\), \(|\kappa|\)의 유한-step 추정 최대치는 \(1.69731\times10^{-6}\)이었다. 이를 정확한 연속 Thomson 선형 연산자의 결과와 동일시하지 않는다.

전체 시간 적분은 원 native half steps 뒤 endpoint electron density를 사용하는 **Lie split**이다. frozen collision의 정확한 지수해가 전체 scheme의 차수나 cumulative interval enclosure를 보증하지 않는다. feedback에서는 photon/guard interval을 point로 다시 설정한다. gas state와 장부는 유지되지만, 이전 photon enclosure는 이어지지 않는다. 새 run의 작은 `public_width`를 기존 history보다 정확해졌다는 증거로 사용하지 않는다.

## 실제 진화 결과

모든 표의 마지막 시각은 \(10^{11}\) s다. 아래 P/I의 분모는 **전체 photon intensity**다. PR199·200의 `P/scattered-in` source 비율과는 관측량의 분모가 다르다.

| 실험 | macro steps | 최종 max P/I | 최종 sky-integrated P/I |
|---|---:|---:|---:|
| BI, native 무산란 control | 160 | 0 | 0 |
| BI, degree4 collision | 160 | `5.335899157888835e-13` | `3.5884283591969985e-13` |
| BI, degree6 collision | 160 | `5.335922701949413e-13` | `3.5884286286698006e-13` |
| BI, degree4, dt/2 | 320 | `5.314446457628724e-13` | `3.574000518548488e-13` |
| FLRW, degree4 collision | 160 | `7.374611003217392e-23` | `3.758492202008377e-23` |

BI degree4의 누적 endpoint optical depth는 `2.049303471198702e-7`이다. `tau_weighted_photon_exposure_per_H=9.416750323202931e-9`는 \(\sum\tau_kN_k\) 진단량이며, 비선형 native adapter에서 직접 센 scattering event count로 부르지 않는다.

| 비교 | 최종 Q/U vector 상대 L2 차이 | 최종 max P/I 상대 차이 |
|---|---:|---:|
| degree4 대 degree6 | `2.0401466987858942e-5` = **0.00204015%** | `4.412388592969047e-6` |
| dt 대 dt/2 | `0.004054310007561125` = **0.405431%** | `0.004020447093419095` |

이 비교는 같은 최종 시각의 측정된 sensitivity다. continuum angular convergence나 엄밀한 시간 오차 상한은 아직 주어지지 않는다.

같은 dt의 무산란 control과 collision run에서 최종 \(x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},T\)는 출력 double precision에서 같았다. 광자 수·에너지의 차이도 각각 `4.16e-17/H`, `4.44e-16 eV/H`다. **이 실행으로 물질 이력의 유의한 Thomson 효과를 검출했다고 주장하지 않는다.** 편광의 생성·지속 수송과 native feedback 연결은 실제로 실행됐다.

## 원 실패 보존과 새 수치 검증

원본 128-ray tick142를 재계산한 값은 `0.041522777008573215`였고, 보존된 과거 값은 `0.04152277708926094`다. LSQ library·산술 차이에 따른 마지막 자리 변화가 있으나 동일한 **4.1522777% > 3% FAIL**이다. source bytes는 동일하다.

동일 tick142에서 PR200 교정을 적용한 q-frame degree4/fit 차이는 `0.0014846402630122617`, physical-tetrad degree4/fit 차이는 `8.490342400688301e-7`, physical degree4/degree6 차이는 `1.4377251114427907e-5`다. 각각 다른 식과 target을 명시하며, 과거 FAIL을 소급해 덮어쓰지 않는다.

새 구현의 실제 검증은 다음과 같다.

- **30/30 normal + 30/30 Python -O**: exact collision, 독립 Jones/Poisson 비교, semigroup, photon/energy conservation, PSD, Stokes sign, 매우 작은 optical depth, triaxial screen ODE, source clock, near-HI source arithmetic, adapter·guard 검증.
- 완결된 다섯 native 실험 모두 **두 accepted half-step을 구성한 각 macro endpoint의 I가 원 Rust와 일치**했고, 기록된 최대 transport parity residual은 **0**이다.
- native stage ledger 최대치는 다섯 실험 전체에서 `5.608713363539075e-16`; 원 gate `1e-12`를 유지했다.
- collision의 각 physical energy group photon conservation은 반올림 수준이며, Stokes cone과 joint guard condition \(0\preceq S_U\preceq10S_N\)를 검사했다.
- 별도 에이전트가 다른 icosahedral 격자의 explicit Mueller matrix exponential과 다섯 실험의 전체 raw data를 독립 검산했다. 생산자 module을 import하지 않은 all-hat scalar replay·GL8 screen transport·128×128 Mueller Poisson 계산을 사용했다. N/E raw inventory의 최대 상대차는 `4.22e-16` 이하였고 source electron density·optical depth를 독립 재계산했다. BI160의 마지막 편광에서 이전 상태를 통해 전달된 신호 비율은 약 **98.7525%**였다. 최종 검토 범위와 측정은 `INDEPENDENT_REVIEW.json`·`REVIEW.md`를 참조한다.

실행 중 두 구현 결함도 보존했다. 첫 실행은 `h`/`h_per_s` 필드 불일치로 native step 전에 종료됐다. 두 번째는 두 native trials 후 원본과 다른 redshift 식 평가 순서가 좁은 HI hat에서 증폭되어 parity 검사를 실패했다. 원 Rust의 scalar `q*q*exp(-2Ht)`와 sequential sum 순서를 맞추고 **기준을 바꾸지 않은 채** 교정했다. ratio 차이 `2.22e-16`이 near-HI hat coefficient 차이 `9.08e-12`로 증폭될 수 있음을 회귀시험에 넣었다. 실패 시도 2 paired trials / 6 endpoints는 완결된 960/2880 실험 수와 별도로 기록한다.

원 fixed-hat의 physical source support 실패도 그대로다. BI 160-step 최종 forbidden-support photon fraction은 **0.4199203797503485**다. 이 큰 spectral support 결함이 있으므로 현재 polarization 값을 물리적으로 인증된 original F08 prediction으로 승격하지 않는다.

## 판정과 다음 재개점

| 항목 | 판정 |
|---|---|
| frozen physical-quadrature polarized semigroup | derived + implementation-verified |
| 원 source clock·H/He·spectral grid의 지속 point receiver | implementation-verified + numerically checked |
| 정상/최적화 tests 및 실제 native runs | 실행 완료, 해당 범위 PASS |
| 물질 이력에 대한 검출 가능한 Thomson 변화 | unresolved; 이번 수치에서 분해되지 않음 |
| old q-frame 3% gate | FAIL 보존 |
| fixed-hat physical energy support | FAIL 보존 |
| 연속각도 수렴·전체 interval propagation·14 ledgers | unresolved / not certified |
| 원 owner 수용·production | HOLD |
| REI canonical / working / PhysicalFast / REC H5 | **28/88 · 33/88 · 4/7 · 0/313**, 모두 **+0** |

다음 과제는 동일 F08 source의 characteristic-energy 경로와 지속 편광 상태를 연결해 fixed-hat support 결함을 제거하고, photon energy/angle uncertainty를 collision·atomic sigma·gas root와 원 14 장부에 전파하는 것이다. BASS #331의 32-step characteristic interval chain은 해당 입력 근거이며, original owner 수용은 REI에 남는다. 별도 source·clock를 가져와 빈 연결을 채우지 않는다. 이번 bounded unit 이후의 실행은 `AUTO_NEXT=false`를 유지한다.

## 재현 및 산출물

`README.md`에 원 source-full ZIP, 빌드, exact commands, 다섯 case, 결과 생성 명령을 적었다. `results/RESULT.json`은 실제 과학 결과·source identity·고정 gates·raw file hashes를 담고 `WITNESS.csv`는 일부 시간 단면이다. 전체 spectral Stokes history, native endpoint witness, 실패 로그, 원 source archive는 source-complete backup에 보존한다. raw array를 새 public science claim으로 승격하지 않는다.

문헌과 직접 유도는 `THEORY.md`에서 구분한다. 기본 polarized collision·screen tensor와 observer convention은 Pitrou, *CQG* 26 (2009) 065006, [arXiv:0809.3036](https://arxiv.org/abs/0809.3036), Challinor, *PRD* 62 (2000) 043004, [astro-ph/9911481](https://arxiv.org/abs/astro-ph/9911481)을 확인했다. 이 파일에 제시한 finite-quadrature closed semigroup와 normalized native adapter 식은 이번 작업의 직접 유도다.
