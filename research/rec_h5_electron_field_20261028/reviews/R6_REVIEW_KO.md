# REC-H5-ELECTRON-FIELD01 — 독립 R6 이론 검토

**판정: pass_scoped.** 최종 R5의 explicit-incoming FULL electron point field 유도는 동결 계약의 실제 point 적용 조건 아래 닫힌다. 원본에서 독립적으로 구성한 블록 방정식, Schur 소거의 역대입, scalar source, incoming에 대한 실수 affine성, history 분리와 He-neutral 전자비율 해석이 R5와 일치한다.

이 판정의 대상은 조건부 실수 대수 명제와 원본의 정보 의존성이다. 새 adapter의 실행, 실제 132개 입력 결속, 내부 divisor 관측, binary64 parity와 nonmutation은 C단계에서 확인할 의무다. 이 검토의 새 scientific execution, native replay, point-kernel call, CAS 실행은 각각 0이다.

## 1. 검토자·방법·입력

검토자는 별도 agent인 /root/electron_r6_independent이며 R2–R5 및 새 구현의 저자가 아니다. 먼저 동결 CONTRACT와 원본 C 소스를 읽고 아래 식을 독립적으로 유도했다. 그 뒤 root가 완성한 최종 R2–R5를 읽어 대조했다. 1차 방법은 source의 사용·대입 위치 추적, 2차 방법은 블록 소거의 직접 역대입이며, 차원·부호·charge accounting을 별도로 확인했다. 작성자에게 전달한 사전 관측 사항은 matrix 방향, calloc 초기화, table normalization, affine 명제의 실수 범위였고 최종 R5에서 확인했다.

적용한 검토 규약은 physmath-research-loop 1.0.0의 RESEARCH_POLICY, THEORY_LOOP R6, EVIDENCE_AND_HANDOFF 및 RUNTIME_AND_LEGACY다. 요청된 독립성은 별도 비저자 검토자라는 역할이다. 호스트의 모델 표기는 직접 관측한 runtime model-id가 아니며 **runtime identity는 NOT_OBSERVED**로 기록한다. 다른 모델 계열을 사용했다는 주장은 없다.

Native SOURCE ZIP 전체의 크기와 SHA-256을 이 검토자도 직접 확인했다. 아래 원본의 ZIP member를 읽었으며, 이미 추출된 hydrogen.c/history.c/history.h는 해당 member와 byte-identical임을 확인했다. source는 수정하지 않았다.

| 입력 | 검토한 identity |
|---|---|
| Native SOURCE ZIP | 110654069 bytes; SHA-256 94b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c |
| 동결 CONTRACT.md | 7550 bytes; SHA-256 adfe324c6805a04d95f3d9801e37aa3ac1722fd7525004c79f3b1c79480f8c4e |
| 원본 hydrogen.c | 37471 bytes; SHA-256 421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b |
| 원본 history.c | 30963 bytes; SHA-256 8ffe38f0431fcd1ae04b55f855f36e8643b1c5eb33a947f581f95d628611f976 |
| 원본 hydrogen.h | 7837 bytes; SHA-256 e89a3a447928cbe31dc273c11c4a8bc7f7a8e297be4a11270e453c101f96ccba |
| 원본 hyrectools.c | 6001 bytes; SHA-256 beb97b6cee3b80cf74d58264da7087301865881d266de1c17dd472a08665bb79 |
| 원본 hyrec_params.h | 3764 bytes; SHA-256 cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2 |
| 최종 R5_DERIVATION_KO.md | 6935 bytes; SHA-256 4888335166daf05e8fb9922cf81b815a3579cfd96fc9176ac95777f8c70d226f |

원본 member의 공통 경로는 research/rec_h5_native_path_20261028/inputs/original/HyRec/이다. root가 알려 준 R5 게시 commit은 b2bc0f02734ec8218be9bb27320a77e8ab15a2be이며, 이 검토의 직접 identity 검사는 위 로컬 바이트에 대한 것이다. 원격 게시와 이중 백업의 ACK는 R6 수학 검토 범위에 포함하지 않았다.

survey/science/ELECTRON_FIELD01_R1_SCIENCE_CONTRACT_KO.md는 작성자 측 intake 제안으로 읽었다. 그 문서를 독립 승인이나 이미 수행된 수치 검증의 근거로 사용하지 않았다. R2에 적힌 문헌 검색·저장소 조사 coverage와 다른 단위의 판정도 이번 R6가 재검증한 결과가 아니다.

## 2. 상태 변수, 단위 및 원래 온도 경로

원본 hydrogen.c/h는 cgs+eV 단위를 명시한다. hydrogen dispatcher의 nH는 cm^-3, H는 s^-1이며 TM/TR 값은 k_B T를 eV로 표현한다. 원본 history.c의 hydrogen 호출부는 nH0(m^-3)에 1e-6(1+z)^3을 곱하고 Kelvin 온도에는 원 kBoltz를 곱한다. eta=ln(a)에 대해 d eta/dt=H이므로 시간당 source를 H로 나눈 FH는 eta당 무차원 비율 변화다. 원래 hPc=hc, kBoltz와 질량·에너지 상수를 유지하며 c, hbar 또는 k_B를 새롭게 1로 정규화하지 않는다.

P는 원 dispatcher의 represented binary64 입력이다. p=xHII와 x1=1-p를 원 source closure로 사용하며, xr[0], xr[1]는 각각 2s, 2p의 ground-state equilibrium에 대한 departure다. xv_b=x1 Dfnu_b이고 incoming도 occupation departure다. 원본 FULL의 solve 주석과 마지막 Dfnu_hist=xv/x1 대입이 이 해석을 직접 지지한다. 절대 population과 signed departure를 혼동하거나 음수 departure를 clipping하면 다른 문제를 푼다.

원 FULL 함수의 prelude는 다음 순서다.

    ratio = TM/TR;
    rescale_T(&TR, fsR, meR);
    TM = ratio*TR;

rescale_T는 TR을 fsR*fsR*meR로 나눈다. 따라서 fsR=meR=1에서도 ratio roundtrip을 생략하거나, 이미 변환된 coefficient TM/TR를 dispatcher 입력으로 재투입하면 binary64 경로가 달라질 수 있다. R3의 정의와 R5 §5는 원 dispatcher 값에서 이 경로를 정확히 한 번 적용하도록 명시한다.

## 3. 독립적으로 재구성한 블록과 source

원본 populateTS_2photon와 solve_real_virt의 실제 대입 위치에서 다음 방향을 얻는다.

\[
A_{ij}=\mathrm{Trr}[i][j],\quad
B_{ib}=\mathrm{Trv}[i][b],\quad
C_{bi}=\mathrm{Tvr}[i][b],
\]
\[
V_{bb}=\mathrm{Tvv}[0][b],\quad
V_{b,b-1}=\mathrm{Tvv}[1][b],\quad
V_{b,b+1}=\mathrm{Tvv}[2][b].
\]

따라서 M=[A B; C V], X=(xr,xv), S=(sr,sv)이고 위 real 행은 A xr+B xv=sr, 아래 virtual 행은 C xr+V xv=sv다. Trv와 Tvr의 C 저장 shape가 같아도 수학적 방향은 다르며 일반적으로 B=C^T가 아니다.

고정 P와 native initialization을 거친 tables에서

\[
s=\mathrm{SAHA\_FACT}(fsR,meR)\,
T_R\sqrt{T_R}\,e^{-E_I/T_R}/n_H,\quad
\Delta=x_e p-sx_1,
\]
\[
c_i=n_H(sx_1D\alpha_i+\alpha_i\Delta),\quad
R_\alpha=\mathrm{LYA\_FACT}(fsR,meR)H/(n_Hx_1)
\]

로 놓으면 원본의 incoming 사용은 다음 세 식으로 모두 소진된다.

\[
s_{r,0}=c_0+3R_\alpha x_1(1.664786871919931)u_{\mathrm{Ly},1},
\]
\[
s_{r,1}=c_1+3R_\alpha x_1u_{\mathrm{Ly},0},
\qquad
s_{v,b}=V_{bb}x_1(1-\omega_b)u_{v,b}.
\]

여기서 omega는 원본 one_minus_Pib다. tau>1e-6 분기에서는 1-(1-exp(-tau))/tau를, 다른 분기에서는 tau/2-tau^2/6을 사용한다. V의 대각 계산에는 별도로 tau>0 분기가 있다. Alpha, DAlpha, Beta, diffusion rate, tau, omega 및 M은 incoming을 읽지 않는다. 따라서 S=S0+G u이고 M은 u와 독립이다.

이 구조에는 초기화가 포함된다. hyrectools.c의 create_1D_array는 calloc이며, 미기입 offdiagonal과 diffusion rate는 0에서 시작한다. diffusion 행의 lower=-Aup[b-1], upper=-Adn[b+1]이고 Ly-alpha 이웃에서는 upper[139]=lower[140]=0으로 절단한다. read_twog_params의 sub-Ly-alpha A2s normalization과 feature macros도 보존해야 한다. 최종 R5 §§2–3, §5는 이 조건을 정확히 포함한다.

## 4. Schur 소거의 역대입과 affine 정리

V의 diffusion 밖 대각 divisor, 원 Thomas 소거의 필요한 피벗, Q=A-B V^-1 C의 determinant가 0이 아닌 point를 가정한다. 그러면 원 solver의 실수 대수식은

\[
x_r=Q^{-1}(s_r-BV^{-1}s_v),\qquad
x_v=V^{-1}s_v-V^{-1}Cx_r
\]

이다. 독립 역대입으로

\[
Cx_r+Vx_v=s_v,\qquad
Ax_r+Bx_v=Qx_r+BV^{-1}s_v=s_r
\]

를 얻는다. 이 조건에서 V와 Q가 가역이므로 M의 해도 유일하다. 원본의 diagonal-dominance 주석을 전체 coefficient box에 대한 증명으로 대신 사용하지 않았다. 최종 R5 §3은 바로 이 point 조건을 전제로 삼는다.

원 scalar는

\[
F_H=-\frac{c_0-\beta_0x_{r,0}+c_1-\beta_1x_{r,1}}{H}.
\]

c_i는 s^-1, Beta_i도 s^-1이고 xr는 무차원이다. 재결합 source에는 음의 부호, photoionization departure에는 양의 부호가 붙는다. R5 §1의
c_i=nH[alpha_i xe p-alpha_i^eq s x1] 변형은 실수 대수에서 맞으며, 문서는 binary64 구현에 원 grouping을 유지하도록 별도로 요구한다.

real 두 성분을 선택하는 행렬 E를 사용하면

\[
F_H(P,u)
=-\frac{c_0+c_1}{H}
+\frac{\beta^T}{H}EM^{-1}(S_0+Gu).
\]

따라서 가역 조건이 유지되는 고정 P/tables에서 incoming에 대해 affine이다. 이 결론은 signed u를 허용하며 binary64 프로그램의 exact affinity나 P까지 변화시키는 trajectory의 affinity를 주장하지 않는다. R5 §4의 양화와 이 구분이 맞는다. R4의 2변수 toy도 직접 대입해 r=(2+u)/5, v=(1+3u)/5, F=(-3+u)/5임을 확인했으며, 그 예가 실제 HyRec gain이나 물리적 spectrum positivity의 근거로 제시되지 않은 점도 확인했다.

## 5. History 경계와 total electron 해석

원 rec_HMLA_2photon_dxHIIdlna는 온도 prelude, fplus_from_fminus, assembly, solve, FH 계산, history postwrite 순서다. incoming을 고정했을 때 마지막 history writes가 이미 산출한 FH에 역방향으로 영향을 주는 데이터 의존성은 없다. 그러므로 incoming을 직접 받고 fresh local 배열에서 원 assembly/solve/scalar를 수행하는 점 함수의 구성은 타당하다. table 초기화는 별도 context 작업이며 점 평가에는 다시 파일을 읽는 단계가 필요하지 않다. 구현의 실제 caller nonmutation은 C단계가 확인한다.

원본 history.c의 hydrogen-only 루프는 helium을 entirely neutral로 가정한다. rec_get_xe_next1_H는 xe_in을 xe와 xHII 양쪽 인자로 전달한다. instrumented history.c의 H_STEADY label은 이 루프에 붙는다. 이 label의 steady는 Tm closure이며 FH=0을 뜻하지 않는다. 따라서 실제 primary의 phase, xe=p 및 He-neutral 전제가 확인되면 Fe=dxe/deta=dp/deta=FH다. R5 §6은 그 입력 검증을 조건으로 남겼으며 다른 phase의 helium source를 흡수하지 않는다.

## 6. 동결 acceptance와 후속 검증 의무

동결 계약의 bitwise FH/xr/xv 일치 수는 실제 실행에서 관측해 보고할 항목이다. 이 R6에는 새 일치 수나 수치 PASS가 없다. 필수 scalar gate는

\[
|F_H^{new}-F_H^{saved}|\le512\,\epsilon_{64}S_F,
\]
\[
S_F=H^{-1}\sum_i\left[
n_H\left(|sx_1D\alpha_i|+|\alpha_i\Delta|\right)
+|x_{r,i}\beta_i|
\right]
\]

이며 S_F=0이면 차이가 정확히 0이어야 한다. 분모를 |FHsaved|에만 의존시키지 않아 cancellation이 큰 source 비교에도 의미 있는 원 항의 크기를 기록한다. 별도 독립 block 재구성에서

\[
\max_k\frac{|(MX-S)_k|}
{\sum_l|M_{kl}X_l|+|S_k|}
\le4096\,\epsilon_{64}
\]

를 요구하며 분모가 0인 행의 분자는 정확히 0이어야 한다. 이 두 임계값은 사전 numerical parity·잔차 수용 기준이다. rigorous floating-point enclosure, 전방 오차 또는 inverse gain bound로 읽지 않는다.

다음 항목은 조건부 R5 증명을 막지 않으며 C3/C7/C8/C9의 실제 증거로 닫아야 한다.

| ID | 남은 구현·실행 의무 | 이번 판정에서의 처리 |
|---|---|---|
| C-OBS | native 내부 divisor와 Schur determinant를 연산 순서 변경 없이 관측할 방식 결정 및 검사 | 실제 방식 미결정. 별도 build copy의 read-only observer hook은 후보일 뿐이며 R6가 구현을 승인하지 않음 |
| C-BIND | LAST_WRITERS와 CALLS/QSS_WRITES의 (id,slot)을 결속하고 실제 132개 writer, 626개 endpoint mapping, phase 및 온도 provenance 확인 | 기대 집합을 계약으로 유지; 이 검토에서 새로운 입력 조립·평가 없음 |
| C-NUM | bitwise 수, 512 eps64 S_F scalar gate, 독립 4096 eps64 block residual, 모든 유한값·정의역 조건 확인 | NOT_RUN by this reviewer |
| C-PURE | 입력·tables·history nonmutation 및 잘못된 단위·rescale·phase·incoming 누락 등을 식별하는 control | source dependency는 확인; 구현의 실제 결과는 후속 검토 |

## 7. 대조 결과와 수용 범위

| 검토 항목 | 최종 문서와 원본의 대조 결과 |
|---|---|
| scalar source와 부호·단위 | R5 §1이 원 FULL 식과 일치 |
| incoming 전 사용 위치 | R5 §2가 real 두 항과 virtual diagonal 항을 모두 포함 |
| block 방향·초기 0·Ly-alpha interface | R5 §3이 원 assembly와 solve 호출 순서에 일치 |
| nonzero 조건과 해의 유일성 | 조건부 Schur 역대입이 닫힘; 전체 box 주장 없음 |
| 고정 P의 실수 affine성 | R5 §4가 필요한 독립성과 적용 범위를 명시 |
| 원 temperature path·history 분리 | R3 및 R5 §5가 원 함수의 데이터 의존성을 보존 |
| H_STEADY/He-neutral Fe=FH | R5 §6이 정확한 branch와 실제 입력 확인 조건을 명시 |
| parity·residual의 의미 | R1/R3/R5가 numerical 진단과 물리적 certificate를 구분 |

검토한 논증에서 blocking 오류는 발견하지 못했다. 사전에 전달한 orientation, 초기화, table normalization 및 affine 범위 관측은 최종 R5의 해당 절에서 해결되어 있다. 내부 divisor 관측의 구체적 구현은 정확히 후속 C 의무로 남아 있다. 새로운 strong no-go 주장은 없으므로 NG1–NG7에 의한 새 배제정리 채택은 적용 대상이 아니다.

**유지되는 상태:** canonical 28/88, 증가량 +0; physical 0/313; physical query/K/M2/defect/L/tube/e0/epsilon/outgoing는 모두 null; H6/H7 OPEN; L4=false; REI activation=false. QSS03의 coefficient-box nonsingularity·inverse gain과 thermal 단위의 별도 R6/C9는 이 판정에 포함하지 않는다. 이 검토는 최종 R5의 조건부 source-point 유도에 대한 pass_scoped이며, 전체 coupled field나 physical tube의 채택을 뜻하는 상태 변경을 만들지 않는다.
