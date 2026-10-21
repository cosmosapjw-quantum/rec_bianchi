# REC → REI: 독립 matter/radiation z20→2 pilot의 저장 궤적 연구

연구 단위 `REC_TRAJECTORY63_20261021`, 2026-10-21. 이 문서는 최종 과학·코드 결과를 소유한다. 게시 commit, CI와 provider별 백업 반환은 별도 `DELIVERY.json` 및 마지막 PR117 보존 댓글을 따른다.

## 1. 결과와 이번에 선택한 작업

**독립 matter/radiation의 non-tilted LRS Bianchi I preliminary parameter sweep와 z20→2 진화 그림을 실제 저장 자료로 만들었다.** 최신 다른 작업에서 이미 완료한 REI unified Lane B 자료를 발견했으므로, 추가 적분 대신 175개 nominal 궤적을 정확히 결속한 소비자를 구현했다. 이 중 63개 축 궤적만으로 응답을 재구성하고, 112개 혼합 궤적의 153개 저장 epoch와 비교했다. 새 ODE, NCP 제출, benchmark는 각각 0이다.

이번에 새로 완료한 것은 `code/reduce_trajectories.py`, 독립 집중 테스트 8개, 그림 5종(PNG/PDF), 재현 가능한 관측량·residual 배열, 입력 및 실행 manifest, 독립 수학·코드 검토와 handoff다. 원래 warm C15 729-case 결과는 그대로 `complete_reused`이며 새 long-window response의 계수나 행으로 사용하지 않았다.

이 산출물은 **collisionless finite-L8 모델의 저장된 유한 격자에 대한 예비 결과**다. full cold H/He/UV EoR history, ODE 참해 오차, 시간 연속 전역 수렴, prospective 축 대체 solver의 인증은 포함하지 않는다. Physical `HOLD`, global convergence `NOT_RUN`, production `NOT_APPROVED`, 원 REC U5의 `HOLD_9_FAIL/HOLD_8_FAIL`, `CLOSED_HOLD_NOT_RESET`, `REI_activation=false`를 유지한다.

### 최신 근거에서 비교한 세 후보

| 후보 | 조사에서 확인한 사실 | 결정 |
|---|---|---|
| 저장 z4 state를 z2까지 연장 | 공유 REI 작업의 237개 tail이 이미 exit0, CASE_SET_EXHAUSTED로 완료 | 완료 결과를 재사용; 중복 제출 없음 |
| 새 long-window 자료에 축 응답 재구성 적용 | REC116은 warm endpoint 사후 비교이며, 새 175-grid의 전체 궤적 비교는 확인되지 않음 | **이번 단일 연구 단위로 선택** |
| HH128의 finite-L8 radiation 8→3 축소 구현 | exact matrix flow와 fallback이 이미 upstream에 존재 | 기존 구현·근거를 연결; 이 후처리에는 새 적분 상태가 필요 없음 |

초기 조사 문서의 continuation 권고와 후보 목록은 당시 snapshot이다. 최신 계약은 `CONTRACT_KO.md`와 이 표다. 최초 권고를 완료된 실행의 새 대기열로 해석하지 않는다.

## 2. 조사 범위, 권위와 재사용

가장 먼저 REC PR116과 REI PR213의 최신 반환, 보존 댓글, CI, 필수 보고서·DAG·handoff를 읽었다. REC116 HEAD는 `4cffa8a0abdb104a40cac17cfc65593bec909fb3`, tree는 `916132bd155140a9589c519a56ff2e80358e3434`이고 CI `39565947569`는 성공이다. 기존 `in_progress`는 역사적 snapshot이다. warm729의 result `c8e9f67aa031ffb33a9b0347bdea61dbb01fb746`, delivery `d32cd99fa19c65aa1ca63dbc8aab8741834270e8`, C15 owner `80825585f9fe31d2ee0d5af545ada3fa1f52be72`를 재사용한다.

추가로 REI 255, BASS 262, BASS_CR 168, WU088_HH 138의 총 **823개 branch ref**를 끝까지 열거했고, 2026-10-20 이후 갱신 PR 검색의 29개 제목·본문을 검토했다. 직접 의존하는 REI198/213/214, BASS177, BASS_CR91, HH128/129의 source와 결과를 더 읽었다. 모든 823개 branch의 모든 파일을 읽었다는 뜻은 아니다. `provenance/BRANCH_HEADS_20261021.json`과 `LATEST_SURVEY_KO.md`가 범위를 소유한다.

Drive의 관련 REC 폴더 12개 파일과 REI 폴더 최대100개 반환, Dropbox의 관련 두 폴더 끝까지의 목록을 조사했다. Personal Context 실제 호출은 unavailable을 반환했으므로 다른 모든 대화의 내용을 조사했다고 주장하지 않는다. 공유 작업공간 및 복원된 백업에서 최신 실제 실행 반환을 찾은 것이 이번 선택을 바꿨다.

| 기존 산출물 | 확인된 범위 | 이번 처리 |
|---|---|---|
| REC116 / REI213 | warm a=.1999→.2, gas12000K, 독립729; endpoint153/576 분석 | complete_reused; 새 long-window와 계수·행 분리 |
| REI198 | collisionless z20→4, 1231 histories | complete_reused; 해당 source/receipt를 보존 |
| REI214 / BASS177 | exact moment cache, pending-only executor, 완료729 registry | 중복 개발·중복 적분 없음 |
| HH128 | 같은 finite-L8 radiation의 exact8→3 representation, sector memory | source와 한계를 재사용 |
| BASS_CR91 | 독립3D27 z20→4 | 대체 근거로 조사, 새 선택에 행을 합치지 않음 |
| 최신 REI unified B1/B2 | B1=143new+35reused; B2=237 complete tails | 정확 raw/config/source를 동결해 소비 |
| REC U4B / HE29 | 기존 완료·검토 기록 | complete_reused; 재실행 없음 |

원 warm archive `REC_REI_AXIS153_FINAL_4cffa8a0_20261021.zip`의 복원된 1,002,866 bytes와 SHA256 `962f9434bf46009c44e1a4be886448f0b80fbcc263e1883181c4a90227f95db8`이 사용자가 준 identity와 일치했다. 과거 Drive49 payload 검증은 재사용하며, 과거 Dropbox 전체-byte readback `NOT_RUN`을 이번 다른 provider 조회로 소급 변경하지 않는다.

### 최신 입력의 정확한 소유권

원 physical source는 REI PR147 commit `3b85dedce84d37b3e165da00685a8a984950aafe`다. 새 실행 wrapper의 SHA256은 `a7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64`, z2 manifest는 `4f7e599ad9f082be59cbe2203a8b55b7bd9cb21fec9fde55a41afe53b9444853`이다. 조사 시점 PR199 remote HEAD `8b71c13e23202edfce1ee67fb2da552fefb9a583`에는 새 결과가 아직 없었다. 따라서 local frozen snapshot과 파일 SHA를 권위로 사용한다. 마지막 원격 게시 재확인은 `provenance/FINAL_UPSTREAM_PUBLICATION_CHECK.json`을 따른다. 원격에 존재하지 않는 commit 소유권을 만들지 않는다.

compact snapshot에는 **175 nominal+3 component guards=178 궤적**, 원 prefix/tail/raw/config/receipt, vendor source, 원 실패 이력과 audit가 들어 있다. 1,686개 payload, 31,925,390 bytes를 copy 전후 stat/size/SHA와 destination hash로 확인했고 변경 0이었다. snapshot manifest SHA는 `d7b147aa0293646b068e754a9bf03f2b8e47e3544b405a1ad5bfce366b34143e`, subset-selection SHA는 `53b6aae32baaf1d83e4d50db952fac7c635b05e65276acd484d6454914c28b5e`다. 원 MANIFEST/STATUS는 전체237의 문서이므로 byte-identical로 보존하고, 178개 subset은 별도 목록으로 정의한다.

## 3. 물리 규약과 유한 계약

normal orthonormal frame, metric signature (-,+,+,+), proper time t[s]를 사용한다.

\[
a_\perp=a e^{-b},\quad a_\parallel=a e^{2b},\quad s=\dot b,
\qquad \sigma_{ab}=\operatorname{diag}(-s,-s,2s).
\]

각 성분 A=m,r에 대해

\[
\pi^A_{ab}=\operatorname{diag}(-p_A,-p_A,2p_A),\qquad
p_A=(P^A_\parallel-P^A_\perp)/3.
\]

H,s는 s^-1, p_A는 J/m³다. 이 proper-time/SI 규약의 계수는 \(\kappa_t=8\pi G/c^2\)다. signed full-Frobenius 좌표와 norm을 구분한다.

\[
S_F=\sqrt6\,s/H,\quad P_{A,F}=\sqrt6\,\kappa_t p_A/H^2,
\quad \Sigma_F=|S_F|,\quad\Pi_{A,F}=|P_{A,F}|.
\]

\[
P_{\mathrm{tot},F}=P_{m,F}+P_{r,F},\qquad
\Pi_{\mathrm{tot},F}=|P_{m,F}+P_{r,F}|.
\]

half-contraction norm \(\sqrt{T_{ab}T^{ab}/2}\)를 선택하면 표시된 모든 signed/norm 좌표를 \(\sqrt2\)로 나눈다. \(|P_m|+|P_r|\)는 total norm이 아니라 상계다. radiation은 signed gamma+massless-neutrino stress를 먼저 합한다. anisotropic work는 \(\sigma:\pi_A=6sp_A\)다.

Matter는 massive canonical Vlasov와 zero-stress cold dust, radiation은 photons+massless neutrinos다. source의 massive fraction .1, mass/T_ref=30, nominal L8, radial24×angular12, subcell Gauss3, DOP853 rtol3e-11/atol3e-13, ne_source=None을 유지했다. 이 수치는 source 계약이며 이번 후처리의 새 solver 설정이 아니다.

### 격자와 시간

| 초기 좌표 | 값 |
|---|---|
| S_F,i | 0, .0003, .001, .003, .01, .03, .1 |
| P_m,F,i | -.0003, -.0001, 0, .0001, .0003 |
| P_r,F,i | -.001, -.0003, 0, .0003, .001 |

초기 shear orientation은 양 또는 0만 포함한다. 진화 중 signed shear의 음수와 부호 반전은 보존한다. 175=7×5×5 중 매 S plane에서 m=0 또는 r=0인 9개, 총63개가 support다. 나머지112개는 비교 전용이다. 추가56 nominal과 전체6guards는 주 residual 통계에 포함하지 않는다. compact copy의3guards는 재현·provenance 목적으로만 보존했다.

공통 시간좌표는 \(x=\ln(a/a_\mathrm{ref})\), \(a_\mathrm{ref}=1/21\), \(\bar z=1/a-1\)다. 153 epoch는 원 z20→4의121점과 새 z4→2 tail32점으로 구성된다. join은 index120, x=ln(21/5), 마지막은 x=ln7이다. 모든175개 x,a 배열이 정확히 같았다. **같은 redshift에서 비교**하며 case별 H와 elapsed proper time은 각자 사용한다. 끝점 elapsed proper seconds 범위는 [9.759090211441186e16, 9.75955472966245e16]다.

## 4. 재사용식과 보증 범위

고정된 S_i와 x에서 signed 관측량 \(F=(S_F,P_m,P_r)\)에

\[
\widehat F(x;S_i,m,r)=F(x;S_i,m,0)+F(x;S_i,0,r)-F(x;S_i,0,0)
\]

를 적용했다. 혼합112개의 값은 predictor 구성에 들어가지 않는다. fitting coefficients=0, interpolation=0이다. support에서의 불필요한 x+y-y roundoff를 피하기 위해 그63개 출력은 원 support값을 정확히 재사용한다. 초기 축은 config의 nominal값으로 분류하고 실제 initial floating-point offsets를 clipping하지 않는다.

이는 anchored/cut-HDMR의 저차 응답 구조와 연결된다. 아이디어 자체를 새 이론으로 주장하지 않는다. 이번 기여는 이 특정 signed Einstein–Vlasov 결과의 source-bound 전체 궤적 비교다. Rabitz & Aliş(1999)의 [원전 정보](https://doi.org/10.1023/A:1019188517934)를 사용했고, Exa와 SciSpace로 발견한 문헌은 원전 연도·범위로 정정했다.

exact finite-closure response가 m,r에 대해 C²이면 미적분학 기본정리로

\[
R=F-\widehat F=\int_0^m\int_0^r\partial_m\partial_r F(x;S_i,u,v)\,dv\,du
\]

가 성립한다. 음의 m,r도 oriented integral로 처리한다. 별도로 uniform mixed derivative bound B가 확보되어야 \(|R|\le |mr|B\)를 전역 상계로 사용할 수 있다. 이번에는 B를 측정하거나 인증하지 않았다.

저장값을 \(\widetilde F=F+e\)로 쓰면

\[
\widetilde R=R+e_{mr}-e_{m0}-e_{0r}+e_{00}.
\]

따라서 저장 residual은 물리·finite-model interaction과 네 궤적의 ODE/roundoff/초기실현 차이를 함께 포함한다. 작다는 사실만으로 참해 오차나 matter-radiation 비결합을 결론내리지 않는다. 현재153시점 최대값은 그 저장시점 집합의 최대다.

norm 변환에는 정확한 reverse-triangle 관계가 있다.

\[
\big||P_m+P_r|-|\widehat P_m+\widehat P_r|\big|
\le |R_m+R_r|\le |R_m|+|R_r|.
\]

이는 실제 signed 저장 residual로부터 norm 차이를 제한하는 대수적 bound다. ODE global error bound가 아니다. 일반 C² 항등식은 직접 유도했으며, Wolfram은 polynomial identity=0, stored-error relation=0, real reverse-triangle=True, counts={63,112,26775,17136}를 실제 반환했다. 원 CAS 입력·출력은 `evidence/TRAJECTORY_CAS.json`에 있다.

REC116의 미래153축+90sentinel=243-case 제안은 계속 `NOT_SUBMITTED`다. 정확 sentinel 반례를 보존하며, 이번63-support 연구로 그 미검사486개를 인증하지 않는다.

## 5. 실제 결과

전체175×153=26,775 case-epochs 중 validation 통계는112×153=17,136 mixed stored points에서 계산했다. supports의 자기재현을 별도 예측 검증으로 세지 않는다.

| signed 관측량 또는 파생 norm | 전 저장 궤적 최대 절대 차이 | 최대의 z | z2 끝점 최대 차이 |
|---|---:|---:|---:|
| S_F | 9.40056251721652e-9 | 4.24499381839779 | 8.12263482370028e-9 |
| P_m,F | 8.582762394605706e-9 | 9.12513693522705 | 2.13015333929086e-9 |
| P_r,F | 1.1057774095034681e-8 | 6.69032672815144 | 6.54093978231986e-9 |
| P_total,F | 1.9152545950075223e-8 | 7.87707155302417 | 8.67109312160225e-9 |
| Pi_total,F | 1.9152545950075223e-8 | 7.87707155302417 | 8.67109312160225e-9 |

shear 최대의 초기 좌표는 (.001,+.0003,+.001), Pm/Pr/total 최대의 초기 좌표는 (0,-.0003,-.001)이다. 실제/예측/차이의 전체 배열과 각 최대 case/epoch/RMS는 `results/TRAJECTORY_ANALYSIS.npz`, `results/SUMMARY.json`, `MIXED_TRAJECTORY_COMPARISON.csv.gz`에 있다. total 최대는 내부 epoch에서 생겨 endpoint만으로 전체 차이를 대표할 수 없다.

큰 S_i=.1 기준으로 모든 residual을 나누면 작은 shear 사례의 중요도가 가려질 수 있다. case별 해당 궤적의 peak|S_F|로 나눈 최대 discrepancy 비율은 7.597183466443014e-5다. 이 값은 (0,-.0003,+.0003)의 peak|S_F|=3.69014027314e-5, peak discrepancy=2.8034672672e-9에서 얻었다. 이는 case-peak scaling이며 zero-crossing에서의 pointwise relative error가 아니다. source 수치 정확도의 보증으로 사용하지 않는다.

### 초기 상쇄가 이후의 상쇄를 보장하지 않는 실제 사례

초기 (S_i,P_m,i,P_r,i)=(0,+3e-4,-3e-4)의 total norm은 roundoff 수준인1.0842e-19다. 동일 저장 궤적의 z2에서

\[
S_F=-3.1459590562\times10^{-5},\qquad
P_m=+5.7965531696\times10^{-6},\quad
P_r=-3.9844807585\times10^{-5},
\]

\[
P_\mathrm{tot}=-3.4048254416\times10^{-5},\qquad
\Pi_\mathrm{tot}=3.4048254416\times10^{-5}.
\]

저장된 total norm은 z≈9.49499에서7.4181204912e-5의 최대를 가지며, |S_F|는 z≈4.37196에서3.6901920052e-5의 최대를 가진다. 이 사례의 전 저장 구간 total reconstruction discrepancy 최대는5.7436124760e-9다. 반대 부호의 초기 조합도 별도 유지했고 비선형 모델의 정확 대칭을 가정하지 않았다.

또한 S_i=.1, P_m,i=P_r,i=0 사례의 z2에는 S_F=.00512716139113, P_m=-3.30682790499e-6, P_r=-8.01096158391e-5가 저장되어 있다. 초기 stress0을 모든 시간의 stress0으로 해석하지 않는다. 위 결과는 해당 collisionless finite closure의 예비 동역학이다.

### 그림 읽기

1. `01_signed_sector_evolution_z20_z2`: S_i=0인 baseline, matter-only, radiation-only와 두 상쇄 조합의 signed shear/matter/radiation history.
2. `02_finite_grid_endpoint_response_z2`: S_i=0,.003,.1의 실제 비균일5×5 초기 성분 격자에서 z2의 ΔS 및 signed Pm/Pr. ΔS는 같은 초기 shear의 stress-free baseline 대비 값이다.
3. `03_mixed_trajectory_absolute_residual`: 112 mixed에서 각 epoch의 median/p95/max 절대 residual. 1e-18 아래 선형인 symlog로0을 보존하며 display floor를 쓰지 않는다.
4. `04_signed_cancellation_and_total_norm`: signed합 후 norm과 sector norm 합의 차이, 실제/재구성 total norm discrepancy와 대수적 bound. 아래 두 곡선은 이 표시 scale에서 겹친다고 명시했다.

5. `05_norm_evolution_and_endpoint_pilot`: 요청한 비음수 Sigma/Pi의 직접 표시. 상단은 같은 5개 대표 case의 세 norm 이력, 하단은 전체175개 z2 endpoint의 (Sigma,Pi_m), (Sigma,Pi_r), (Sigma,Pi_total)다. initialSigma7값을 색으로 구분한다. symlog 선형 경계는 norm y=1e-10, endpointSigma x=1e-6이며 실제0과중첩을보존한다.

5개 PNG를 작성자가 직접 검토했고 별도 root도 실제 열어 확인했다. 과학적 캡션, 축 방향 z20→2, z4 join, common-redshift/다른 proper-clock, 초기 비균일 격자, signed/norm 구분을 확인했다. 그림 작성자의 자기검토를 독립 코드 감사로 세지 않았다.

## 6. 최적화·경량화·벡터화와 외부 재사용

이번 적용은 불필요한 과학 실행을 제거하고 저장 응답을 작은 배열로 투영하는 데 집중했다.

| 적용 또는 연결 | 구체 변경·근거 | 주장 범위 |
|---|---|---|
| 완료된 과학 계산 재사용 | exact case/config/source/raw receipt로175개 연결, same-case pending0 | 새 물리 적분0; 절약 CPU시간의 수치 추정은 하지 않음 |
| 40state→3 observable 투영 | raw40state를 검사하되 유지 배열은 signedS/Pm/Pr | 원 closure나 physics state를 바꾸지 않는 후처리 경량화 |
| 축 basis 분리 |63×153×3 support float만 predictor lookup에 복사 | mixed자료 perturbation이 predictor를 바꾸지 않음 |
| NumPy 배열 연산 | epoch/channel arithmetic·total/norm·metric을 배열 연산으로 처리 | 실제 source에 구현; baseline 대비 speedup 미측정 |
| npz 수명·입력 검증 | allow_pickle=False/context manager; 한 case씩 읽고 SHA/config/shape/finite/common clock 검사 | 유한 입력의 provenance/자원 안정성 |
| 내부 thread1 | OMP/BLAS/MKL/NUMEXPR/VECLIB thread1 | 과도한 중첩 threading을 피함 |
| upstream cache/executor 재사용 | REI214/BASS177의 exact moment cache와 pending-only 실행기 | 새로운 중복 runner 구현 없음 |
| upstream finite-L8 exact flow | HH128의 E=exp[(b-bi)M]Ei,5radiation좌표제거 | 기존 finite system의8→3; 새콜리전모형에 일반화하지 않음 |

실제 표현 크기만 비교하면 175×153×40 float64는8,568,000 bytes, 175×153×3은642,600 bytes다. 이는 선택한 배열의 요소 수 비교이며 전체 프로세스 메모리 절감 측정이 아니다. 예측 support payload는231,336 bytes다. 최종 NPZ에는 actual/predicted/시간/좌표/provenance가 추가로 들어간다.

future에서175개 대신63개만 적분한다면 case 수 기준64% 감소가 가능한 형태지만, **이번에는 그 solver 대체를 채택하거나 제출하지 않았다**. 아직 없는 모델·구간·오차 허용기준에 이 수치를 speedup/정확도 보증으로 이전하지 않는다.

외부 문헌은 [Heinzle & Uggla(2006)](https://arxiv.org/abs/gr-qc/0512031)의 Bianchi-I Vlasov 배경, [Rabitz & Aliş(1999)](https://doi.org/10.1023/A:1019188517934)의 응답 분해 위치, [NumPy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)/[load](https://numpy.org/doc/stable/reference/generated/numpy.load.html)와 [SciPy expm](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.expm.html)의 공식 문서를 확인했다. 제3자 코드 본문을 복사하지 않았고 기존 NumPy API와 사용자 소유 upstream source를 실제 재사용했다. 최신 공식 문서 버전과 runtime NumPy2.3.5/SciPy1.17.0을 구분한다. 새 reducer는 SciPy에 의존하지 않는다.

## 7. 실제 실행, 최소 검증과 독립 감사

최종 reducer SHA256은 `03596192ccd5602187549fb52734870b343aea6e1ca7f13d0df8d7e7b7c1c77a`, test SHA256은 `639abdff416becf8978fc0f013c211d8a1bf1fb6fd2346a1da526e643f2b44d7`다. Python3.12.14, NumPy2.3.5로 실제 실행했다.

집중 테스트8개가 통과했다: additive response/정확 support 재사용, 알려진 시간의존 mixed polynomial, held-out perturbation에 대한 prediction 불변성, signed shear와sum-before-norm, malformed/duplicate/incomplete grid, real/finite input, common-redshift와다른 proper-clock, raw identity와보조필드 NaN 거부. manufactured fixture이며 실제 과학 완료 case 재적분은 없다.

독립 agent는 complex→float silent cast, 보조 시계/상태의 finite guard, SI stress/Sigma의 NaN 비교 우회 문제를 찾았다. 실제 fixed input에는 해당 불량값이 없었다. 세 경계를 fail-closed로 닫았고 red 증거와 최종 green을 남겼다. 최종 postprocessor로175개의 저장자료를 다시 줄여 이전9개 배열과 SUMMARY가 정확히 같은 것을 확인했다. 이 재실행은 ODE가 아니라 guard 변경의 영향을 확인하는 유한 후처리다.

독립 결과 auditor는 reducer를 import하지 않고175 raw를 모두 다시 읽었다. signed projection, scalar support-only prediction,63support exact reuse, 최대값과위치 및endpoint maxima가 저장 output과 정확히 일치했다. 새로운 독립 C9는 이번 consumer만 소유한다. 과거 REC116의 C6 independent review `NOT_RUN_TOOL_NOT_EXPOSED`를 소급 변경하지 않는다.

| 관측치 | 최종 실행 반환 |
|---|---:|
| wall time | 2.157518469 s |
| process CPU time | 2.054803190 s |
| process lifetime peak RSS | 30,388 KiB |
| 검증에 읽은 선택 raw bytes | 13,637,766 |
| 새 IVP / NCP / benchmark | 0 / 0 / 0 |

시간 범위는 import 후 main의 input 검증/투영/분석/output이다. peak RSS는 process lifetime 기준이다. 별도 baseline, 반복 timing, 병렬 scaling을 하지 않았으므로 speedup/메모리 절감률은 `NOT_MEASURED`다. 원 결과를 만든 최초 reducer 및 중간 guard 버전의 receipt와 parity도 보존한다. `results_final/EXECUTION.json`은 최종 코드 실행, `results/TRAJECTORY_ANALYSIS.npz`는 실제 그림 입력이며 `FINAL_GUARD_PARITY.json`이 둘을 결속한다.

## 8. NCP 64CPU/128GB와 공유 작업

다른 Codex 세션 존재를 중지 조건으로 사용하지 않았다. 세 독립 agent가 조사·수학/코드검토·backup/그림을 분담했고 완료된 다른 세션 결과를 실제 읽어 작업 중복을 제거했다. 이번 후처리는 단일 프로세스로 유한자료를 처리해 즉시 완료되므로64개 worker로 쪼갤 새 독립 case가 없다.

NCP 호스트 최대 사양은 새 작업의 자동 allocation이 아니다. 향후 새 finite contract로 미완료 case가 생기면 기존 cooperative executor에 case ID/source 계약을 등록하고, 실제 affinity/quota/available CPU, MemAvailable, disk 및 다른 lane의 lease를 읽어 작업 수를 정한다. 수치 내부 thread1, 작은 pending chunk, 완료 receipt에 따른원자적 재개, 각lane의사용량과실패기록 보존을 유지한다. 기존 cap/debit나 owner 상태를 reset하지 않는다. 새 전체 프로젝트 병렬화 도구를 중복 구현하지 않는다.

이번 세션에서 Desktop Commander의 실제 원격 실행 probe는 monthly usage paused라는 service error를 반환했다. 지침에 따라 재연결/반복 호출하지 않았다. sandbox에는 지정 NCP SSH key가 없었다. direct git proxy 실패는 GitHub connector로 해결했다. 이 연결상태는 다른 세션 때문인 veto가 아니며 NCP가 바쁘다는 추정도 아니다. 이미 필요한 raw와완료반환이 확보되어 해당 제한이 그림·후처리 완료를 막지 않았다.

## 9. 판정과 연구 루프 종료

| 축 | 이번 단위의 판정 |
|---|---|
| 수학 | 조건부 C² rectangle identity 직접 유도; signed/norm 부등식과CAS 확인; uniform bound 없음 |
| 수치 | 17,136 mixed stored points 비교와독립 대조 PASS_SCOPED; ODE 참해 정확도·전역수렴 인증 없음 |
| 구현 | 최종8 focused tests PASS; independent code/result audit에서 발견사항 수정·닫힘 |
| 성능 | 배열/재사용 구조 구현; speedup/병렬 scaling NOT_MEASURED |
| 메모리 | 최종 RSS30,388KiB관측; baseline 절감 비교 NOT_MEASURED |
| 물리 | HOLD; collisionless preliminary 해석만 |
| Production | NOT_APPROVED |

R1–R9와C1–C9는 이 유한 단위의 범위에서 완료한다. R10/C10은 실제 게시·backup ACK/readback에 따라 `DAG.json`과`DELIVERY.json`으로 닫는다. strong no-go는 새로 제안하지 않아 NG1–NG7은 해당없음이다. continuous/global error, physical closure 확장, prospective solver 대체는 열린 과학 의무로 유지한다.

다음 대화는 먼저 최신 owner publication과현재 전달receipt를 읽고, 이 unit을 `complete_reused`로 연결해야 한다. 729/175/237/U4B/HE29를 완료검증 목적으로 다시 적분하지 않는다. 새 과학질문이 생기면 최대3후보에서하나를 고르고 source·구간·closure·resolution·수용기준을먼저 고정한다. 단순 status 확인이면 read-only provenance reconciliation까지만 수행한다.

## 10. 재현 명령과 인계

최종 archive를 풀면 `intake/unified_z2_20261021`와`rec_bianchi/research/rec_rei_trajectory_reuse_20261021`가 같이 있다. 아래 명령은 필요할 때의 재현 절차이며 자동 재실행 대기열이 아니다. 기존 output을 덮어쓰지 않도록 새 output path가 필요하다.

```bash
python rec_bianchi/research/rec_rei_trajectory_reuse_20261021/code/reduce_trajectories.py \
  --snapshot intake/unified_z2_20261021 \
  --output /tmp/rec_trajectory63_new_output
python -m unittest discover \
  -s rec_bianchi/research/rec_rei_trajectory_reuse_20261021/code \
  -p test_trajectory_reuse.py -v
```

그림 재생성의 정확 CLI와환경변수는 `evidence/PLOT_REVIEW.json` 및 `NORM_PLOT_REVIEW.json`의 실제 실행 명령을 따른다. `CODEX_HANDOFF_KO.md`와`NEXT_THREAD_HANDOFF_KO.md`는 각각 실행 환경 및 새대화에 붙여넣기 가능한 독립 문서다.
