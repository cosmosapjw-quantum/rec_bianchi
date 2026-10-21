# H/He/Li LRS Bianchi I: 실제 sandbox pilot 완료 보고

## 완료한 범위

새 **125-case parameter sweep과 별도 opacity-off control 1개**를 이 샌드박스에서 `z=20→2`까지 모두 적분했다. 각 case는 geometry/radiation 40상태, isotope-ion 21상태, optical depth 1상태와 193개 저장 시각을 갖는다. 본 계산 125개 중 첫 case는 적분·배열 저장 후 JSON 직렬화가 실패했으나 **재적분 없이 byte-identical 원 배열을 복구**했다. 이후 124개와 별도 control 1개가 완료됐다. 기존 warm729/175/unified237/U4B/HE29를 재실행하지 않았다.

이것은 **지정 온도·UV장과 21상태 photo/RR/DR number network의 유한 preliminary 모형**이다. 모든 알려진 불안정 핵종·음이온·분자·광핵반응·열수지·복사수송을 닫은 EoR 예측이라고 하지 않는다. Physical HOLD, global convergence NOT_RUN, production NOT_APPROVED와 원래 REC U5 HOLD는 유지한다.

게시: [REC PR119](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/119), `research/rec-rei-hheli-sandbox-20261021`. Stage A/B/C 확정 보존은 `stages/`에 있다. 과학·실행 산출물 HEAD는 `8509ef6ba713279134c98f9f47464aa879069755`, tree는 `15a8891913ae2a4a53654185d31929af1aef4050`이다. 원격 683개 파일의 blob SHA와 크기를 모두 대조했고, 해당 HEAD의 CI `39629774142`, `39629764139`는 SUCCESS다. 최종 문서 마감 HEAD/tree/archive/CI는 PR119 마지막 보존 댓글에서 확인한다.

## 최신 근거 조사

6개 관련 repo의 **1,060 branch와 824 all-state PR metadata**를 마지막 빈 페이지까지 조회했다. PR에 연결되지 않은 243 branch도 보존했다. 이는 당시 접근 가능한 목록의 전수 조회이며, 모든 commit의 모든 파일을 읽었다는 뜻은 아니다. 실제 선택한 source 33개는 commit과 바이트/Git blob hash를 대조했다. Dropbox 12 scoped listing에서 **4,317 metadata row**를 읽었으며, 이를 중복 제거한 고유 파일 수로 세지 않는다. 새 18개 후보와 실제 Li 계수 payload를 조사했다. Personal Context의 대화 조회는 실제 호출에서 unavailable이었으므로 모든 다른 대화를 열람했다고 하지 않는다. 첨부 네트워크 그림은 찾아 직접 확인했다.

| 새로 확인한 계보 | 이번 작업의 판단 |
|---|---|
| REC118 `99f5f4fb…` | 기존 full40 analytic tangent/Jacobian 재사용 |
| REI199 D9, source `407f2a30…`, delivery `cce008b3…` | 175×153 저장 budget의 근거만 재사용 |
| REI217/BASS179 ACCEL03, executed `39ae7c84…` | warm 제한 표본을 새 full-interval ODE로 세지 않음 |
| HH132 PHYS77 `04bc4a06…` | 첫 유한 구간의 근거를 global bound로 확장하지 않음 |
| HE84 HE31 `1c8a56aa…` | 준비된 momentum moment kernel 실제 도입 |
| CR94/95 | 같은 off-grid 4점은 unique129에 중복 가산하지 않음; metadata lag·줄바꿈 차이 보존 |
| REI150 `fd9a21c4…`, REI151 `8a4f5df4…` | Li RR/DR 계수와 Li I 1s+2s photo source 재사용 |

원래 비교한 세 후속 후보는 tangent-only NCP 실행, 완전 thermal/photonuclear 폐쇄, 유한 number network 결합이었다. 세 번째를 선택했다. 원자율과 실제 전자밀도가 geometry/radiation 계산에 연결되어, 이 샌드박스에서 완주 가능한 산출물을 만들 수 있었기 때문이다. 모든 source·공백·외부 CI 실패는 `provenance/UPSTREAM_SURVEY.json`, `INPUT_SURVEY.json`, `UPSTREAM_SOURCE_INTAKE.json`에 기록했다.

## 물리 계약

| 핵종 | 유지 전하상태 | 상태 수 |
|---|---|---:|
| n | 자유 중성자 | 1 |
| 1H, D, T | 각각 I–II | 6 |
| 3He, 4He | 각각 I–III | 6 |
| 6Li, 7Li | 각각 I–IV | 8 |
| 합계 | 전자는 전하중성에서 계산 | 21 |

전자 수는 `ne=nb q·Y`, abundance는 `Y_i=n_i/nb`다. n/T 초기 inventory는 0이므로 실제 pilot의 decay flux도 0이다. 별도 frozen-generator 검증은 nonzero n/T decay map을 검사했다. 전하분율은 고정 초기 isotope inventory로 나누며 진단에서 재정규화하지 않는다. 0 inventory인 n/T 분율은 null이다. H/D/T, He3/4, Li6/7의 electronic rate 동일성은 명시한 근사다.

유지 과정은 photoionization, case-A RR, DR와 명시한 decay map이다. CI/CX, secondary ionization, 음이온·분자, thermal fusion, complete ionic/Auger/fluorescence yield는 이 실행 밖이다. 낮은 T에서 정의되지 않은 CI를 외삽하지 않았으며 그 생략 오차가 작다고 인증하지 않는다.

UV는 optically-thin local-frame isotropic 외부 reservoir로 5–200 eV, photon-number spectrum E^−2.5, 71개 threshold-split bin을 쓴다. late Gamma_HI=10^−12 s^−1, `Q(z)=[1+tanh((7−z)/0.8)]/2`, `T=100+11900Q K`를 지정한다. 관측에 fit한 EoR history가 아니다. 200 eV source에서 대상 primordial nuclei의 MeV photonuclear 채널은 활성화하지 않는다.

Li I은 64.39 eV 위에서 1s+2s 단면을 합한다. 한 흡수 사건을 q→q+1로 놓는 것은 명시한 coarse-graining이다. primary electron, ionic threshold, 미해결 core excitation을 분리해 보존하며 전체 absorbed energy를 heat로 간주하지 않는다.

### Tensor 정의

Orthonormal frame, signature (−,+,+,+), `sigma=diag(−s,−s,2s)`, `pi_A=diag(−p_A,−p_A,2p_A)`다. 시간은 초, stress는 J m^−3이다.

\[
\Sigma_F=\sqrt6|s|/H,\quad P_A=\sqrt6\kappa_t p_A/H^2,
\quad\kappa_t=8\pi G/c^2.
\]

\[
\Pi_m=|P_m|,\quad \Pi_r=|P_\gamma+P_\nu|,\quad
\Pi_{total}=|P_m+P_\gamma+P_\nu|.
\]

Signed tensor 성분을 먼저 더한다. Half-contraction norm은 Frobenius/√2다. 바리온은 공통 T의 등방 이상기체라 `pi_b=0`이며, 별도 massive collisionless component가 matter stress를 공급한다. `fm=0.1`은 **전체 Omega_m의 10%를 비바리온 Vlasov 성분으로 배정**한다는 뜻이다. 나머지 dust에 바리온을 포함한다. Dynamic radiation은 CMB photons+massless neutrinos이고 외부 등방 UV의 anisotropic stress는 0이다. 실제 원자망의 ne는 photon Thomson 항에만 들어간다.

바리온 thermal/ionization/UV energy는 test-fluid 진단이며 Einstein source에 되먹이지 않는다. 순 gas input Q_net와 Q_net−Q_photo_abs를 기록하지만 heater와 escaping emission을 각각 정하지 않는다. 유도·정의·source URL은 [THEORY_KO.md](THEORY_KO.md)에 있다. 원 논문/저자 계수는 [Verner photo](https://www.pa.uky.edu/~verner/photo.html), [Verner recombination](https://www.pa.uky.edu/~verner/rec.html), [Badnell RR](https://amdpp.phys.strath.ac.uk/tamoc/DATA/RR/)와 고정한 REI150/151 source를 재사용했다. Exa·SciSpace 조회와 Wolfram CAS 반환은 provenance/evidence에 보존했다.

## 실제 물리축과 결과

초기 축은 A 계수의 이름만 바꾼 것이 아니라 실제 physical coordinate를 역변환한 5×5×5 직교격자다.

| 축 | 초기 값 |
|---|---|
| Sigma_F | 0, 0.003, 0.03, 0.15, 0.6 |
| signed P_m | −0.0005, −0.00025, 0, 0.0005, 0.001 |
| signed P_r | −0.0012, −0.0006, 0, 0.0006, 0.0012 |

초기 연속 각도의 distribution weight 해석적 하한은 massive 0.2219021905, radiation 0.5724291672다. 전체 궤적은 193시각×129각도 positivity를 확인했으며, 전 시간·연속 각도의 정리로 부르지 않는다.

| norm | 모든 저장 시각의 최대 | z=2 최대 |
|---|---:|---:|
| Sigma_F | 0.6 | 0.0319948953 |
| Pi_m | 0.001 | 2.67386958e−5 |
| Pi_r | 0.00186853058 | 5.64421920e−4 |
| Pi_total | 0.00230576098 | 5.90738993e−4 |

대표점 `(Sigma0,Pm0,Pr0)=(0.15,0.0005,0.0006)`의 z=2 결과는 Sigma=0.00782949250, signed Pm=4.09911393e−6, signed Pr=−4.29799491e−5, total norm=3.88808351e−5다. HII≈0.9999977933, HeIII≈0.9996268641, LiIV≈0.9917345354, LiIII≈0.008262602573이며 ne≈6.0029238893 m^−3다. 이 분율은 지정 T/UV와 source 근사의 조건부 결과다.

저장된 강한 상쇄 `s02_m04_r01`, z=13.58019768에서 Pm=+4.72284802e−4, Pr=−4.72439336e−4다. **total norm=1.5453371e−7**, norm 합=9.4472414e−4다. 작은 total은 각 component가 작다는 뜻이 아니다.

별도 opacity-off control은 대표점의 초기 상태·source·193시각을 유지하고 photon collision만 끈 신규 IVP다. z=2에서 on−off signed photon stress 차이=8.71376580e−7, Sigma 차이=4.87039272e−7이다. On의 photon/radiation/total norm은 off보다 각각 3.35825%, 1.98676%, 2.19159% 작다. 고정 tolerance에서의 저장 비교이며 수렴 오차 인증은 없다. Off의 저장 tau는 **potential electron column**, 적용 collision amplitude는 0이다. 직접 Thomson 항이 없는 matter/nu의 차이는 공유 geometry를 통해 생긴다.

## 실제 그림·데이터

| 산출물 | 읽는 내용 |
|---|---|
| [01 evolution](figures/01_shear_stress_evolution.png) | 125개 전체 범위·중앙값·대표 Sigma 및 분리 stress |
| [02 sweep](figures/02_physical_parameter_sweep.png) | endpoint와 z≈8, 2의 signed 단면 |
| [03 isotope/ion](figures/03_all_isotope_ion_fractions.png) | 모든 유지 H/He/Li 전하상태, Li IV, n/T=0 |
| [04 diagnostics](figures/04_atomic_opacity_energy_diagnostics.png) | ne, tau, 지정 T/UV, gamma/nu, energy ledger |
| [05 control](figures/05_opacity_control_response.png) | 실제 on/off와 signed 차이 |

동일 stem PDF 5개와 CAPTIONS.md도 제공한다. `results/SUMMARY.json`은 전체 수치, ENDPOINTS.csv는 125행, SPECIES_ENDPOINTS.csv는 2,625행, REPRESENTATIVE_EVOLUTION.csv는 193행이다. 모든 raw NPZ와 COMPLETE/RESULT receipt를 포함한다. Heatmap 사이를 보간해 검증했다고 하지 않는다.

## 최적화·검증·자원

HE31 prepared momentum kernel의 고정 packet/weight/계수를 한 번 준비해 vectorized moment를 계산한다. 24×12×Gauss3=2592 packet과 L=8 방정식은 그대로다. Geometry fields를 RHS·opacity·Jacobian에서 재사용한다. 원자망은 작은 generator와 vector 연산으로 표현하며 isotope 규모로 population을 적분한다. `J=G_photo+D+ne R+nb(RY)q^T`의 전자 feedback rank-one 항과 geometry/opacity cross derivative를 포함한 62×62 analytic Jacobian을 BDF에 제공한다. 거대한 momentum-space Jacobian을 만들지 않는다.

| 검증 | 실제 범위 |
|---|---|
| 최적화 parity | 81 frozen state, 7 gate PASS; moment scaled 차이 최대 1.11e−16 |
| 원자 core | 21 check PASS; 모든 21-column Jacobian, frozen generator/energy 분해 |
| 전체 결합 | 3 state, 15 direction PASS; scaled JVP 차이 최대 1.45e−7 < 2e−6 |
| dispatcher | 13 operational check PASS |
| 본 계산 | 125개 모두 13개 finite gate PASS, 24,125 저장 시각 독립 판독 |
| 대조 | 별도 1개, 17개 독립 판독 check PASS |
| CAS | generator, trace-free norm, cancellation, gas-energy 항등식 확인 |

최대 baryon residual=1.5543e−15, isotope scaled residual=2.3283e−15, 최소 scaled population=0이다. tau(z20→2)=0.0692155865–0.0693407679. 최대 thermal+ionization+UV/critical-energy 비=2.1940642e−8이며 이는 **누적 dynamical error bound가 아니다**. Friedman residual은 H를 정의한 같은 algebraic constraint 점검이므로 독립 수렴 증명으로 세지 않는다.

상세 benchmark/scaling campaign은 0이다. 관측된 124-case launcher wall=26.1862초/4worker, control launcher=1.90723초/1worker다. 이전 구현 대비 speedup으로 표현하지 않는다. 첫 case의 solver counter/time은 알 수 없어 null로 남긴다.

실제 sandbox는 CPU quota8, RAM8GiB였다. NCP64/128이라고 가정하지 않았다. Auto dispatcher는 affinity/quota, 1분 load, 가용 RAM과 공유 reservation을 읽고 독립 case를 배분한다. 각 worker의 BLAS/OpenMP는 1 thread다. 큰 host의 상한은 63worker이며 부하·예약·RAM에 따라 줄어든다. 다른 세션의 존재 자체는 veto가 아니다. Atomic claim과 완료 hash를 사용하고 기존 allocation/실패를 삭제하지 않는다. 이번 NCP 실행은 0이다.

## 한 명령 실행

실제 환경은 Python3.12.14/NumPy2.3.5/SciPy1.17.0/Matplotlib3.10.8이다. source·계수·원 결과가 이 폴더에 있어 별도 REI checkout이나 네트워크 조회 없이 실행한다. 환경 준비가 필요한 곳에서는 `python -m pip install -r requirements-runtime.txt`를 사용한다.

```bash
cd research/rec_rei_hheli_sandbox_20261021
python code/run_all.py --execute --workers auto
```

완료한 125+1은 hash 확인 후 재사용하고 미완료 case만 제출한다. 정상 output은 `results/pilot_v2`다. `results/pilot`은 최초 출력 실패의 역사적 증거로 보존했다. 저장 결과만 다시 요약·그림화하려면 `python code/run_all.py`, 자원 계획만 보려면 `python code/run_pilot.py --plan --workers auto --output results/pilot_v2`를 실행한다. 공유 host는 `--peer-reservations /shared/reservations`를 사용할 수 있다.

최종 one-command 실행은 `evidence/pipeline_runs/21e53c08e56a4f02b2cdfebd38d769c4/RECEIPT.json`: 4단계 exit0, main125/control1 complete_reused, 새 worker0. `PIPELINE_LAST_RUN.json`도 같은 완료를 기록한다. Runtime의 진척은 각 단계마다 원자적으로 저장된다. frozen source가 달라지면 기존 output에 섞지 않고 새 계약·경로를 써야 한다.

## 감사·실패·보존과 다음 단계

첫 case의 NumPy-bool JSON 오류는 old claim/실패/부분 JSON/NPZ와 함께 보존했다. Serializer만 바꾸고 다른 모든 scientific AST 동일성을 독립 검토한 뒤 원 배열의 byte-identical 복사와 저장 상태 진단으로 receipt를 만들었다. 새 integrator/RHS/Jacobian entry-point 호출은 0이다. 저장 진단 내부의 atomic rate/Jacobian 산술은 수행했다. Unknown solver counters를 만들어 넣지 않았다.

독립 신규 코드 reviewer는 재사용 PR118 tangent의 과거 저자라 그 dependency까지 새 독립 리뷰했다고 세지 않는다. 물리 결합 reviewer는 원자 코어 저자라 원자 코어까지 독립 감사했다고 세지 않는다. 각 범위를 evidence에 명시했다. 두 provenance 파일의 EOF 빈 줄로 실패한 Stage B CI도 STAGE_B_CI_FINDING.json에 보존했고 과학 source 변화 없이 고쳤다. 최종 HEAD CI는 PR 완료 receipt를 따른다.

각 stage Git snapshot과 SHA256 ZIP을 보존한다. Local ZIP 전체 payload readback과 Dropbox ACK/크기, 원격 whole-byte readback은 별도 상태다. 원격 whole-byte를 읽지 않았으면 NOT_RUN을 유지한다.

다음 후보는 (1) source-bound thermal/ionic-yield closure, (2) CI/CX 추가, (3) 같은 모형의 더 큰 sweep이다. **(1)을 다음 DAG로 선택**한다. 지정 T/UV와 Li inner-shell yield의 한계를 먼저 줄여야 물리 예측을 발전시킬 수 있다. 새 source·energy ledger·유한 수용 기준을 고정하고 현재125+1을 재계산하지 않는다. 원래 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI_activation=false는 이 작업으로 해제되지 않는다.
