# LINE02 native Lyα 소스 분해 — 구성적 R2/R3/C2 반환

2026-10-23 KST. 원전 소스 읽기와 저장 입력 추출이다. 독립 검토가 아니다.
사용 skill context: `physmath-research-loop 1.3.0`, 부모 제공
`../skill_context/SKILL.md`, `POLICY_INTEGRATION.md`, `THEORY_LOOP.md` R2/R3,
`CODING_LOOP.md` C2를 실제로 읽었다. 추가 agent와 외부 API 호출은 0이다.
기존 campaign, native runtime, ODE/IVP, 행렬 solve는 모두 0이다.
아래 수는 원 CSV의 scalar/array를 읽어 분해한 것으로 새 우주론 궤적이 아니다.

## 1. 재사용 입력과 실제 코드 경로

Source pin은 REC114 `df95a074730ea0d13d609cf88d448f01f4a47ef1`이다.
`line_source_next_work/donor_source_reads/`의 원본 파일 bytes를 보존하고
동반 provenance SHA256과 읽은 파일 SHA256을 맞췄다. 각 byte 수, SHA256,
Git blob SHA1 및 원래 URL은 `SOURCE_PARTITION_FACTS.json`에 있다.
현재 remote HEAD의 최신성은 부모의 관련 PR delta 조사에 맡긴다.

| 실제 원본 파일/위치 | 구현된 내용과 이번 재사용 |
|---|---|
| `hydrogen.c` 44–46 | literal LYA_FACT, alpha/me rescaling |
| 437–464 | x1s=1−xHII, RLya와2p real diagonal/blue source |
| 469–477 | two-photon/Raman real↔virtual couplings |
| 482–526 | native diffusion, virtual optical-depth compression와 source |
| 569–618 | Tvv를 소거한2×2 Schur algebra |
| 667–716 | 이전시각 red-side history에서 incoming distortions 구성 |
| 730–799 | history→populate→real/virtual solve→xe_dot→history update |
| `primitive_trajectory.py` 260–270 | native escape/diffusion/Schur/history를 별도 owner로 보존 |
| 313–334 | native departure를 실제2s/2p population으로 복원 |
| 428–458 | frozen Mz−s 및 Mv residual/JVP |
| `original_hyrec_physical_flux.py` 402–532 | 저장 CSV parser |
| 688–717 | full313 matrix와 Schur block의 배열 방향 |

CSV는 META22,REAL2,TRR4,VIRTUAL311,TRV622,TVR622,TVV933 rows를 가진다.
Trr(2,2),Trv(2,311),Tvr(2,311),Tvv(3,311),sr2,sv311,xr2,xv311이 모두
있다. **CSV Tvr의 물리 행렬 방향은 transpose**다. Full block은
M=[[Trr,Trv],[Tvr^T,V]], V는 stored Tvv0/1/2 tridiagonal이다.
NVIRT311, native diffusion virtual index100…179, Lyα red neighbor139,
blue neighbor140이다. 통계적2p center는 real index1이며 virtual index가 아니다.

## 2. 추출할 최소 owner

x=x1s, y=xr[1], d=Dfplus_Lya, K=4.662899067555897e15 cm^-3,
fsR=meR=1인 현재 pin에서

r=K H/(nH_cm3 x) [s^-1],
b=3 r x d [s^-1 per H],
h_native=r y−b=r(y−3xd) [s^-1 per H].

**추출 대상은 Trr[1,1]의 +r와 sr[1]의 +b를 함께 묶은 한 항이다.**
real diagonal 전체, 전체 sr[1], diffusion, Lyβ/Lyγ 또는 Tvv를 제거하지 않는다.
원 C 코드는 Trr11=Beta1+R2p2s+r+sum(two/Raman losses)+A2p_up+A2p_dn이다.
현재 저장값의 분해는 다음과 같다.

| Trr11 부분 | s^-1 |
|---|---:|
| Beta1 | 144.40669400086173 |
| R2p2s | 777.6751644808554 |
| 직접 Lyα r | 1.0832181815556778 |
| two-photon/Raman virtual loss | 21.95945159319399 |
| 2p↔virtual diffusion loss | 7508.946123866815 |
| 저장 total Trr11 | 8454.07065212328 |

Two/Raman 부분은 `−sum(Tvr[1,:])−A2p_up−A2p_dn`으로 저장 배열에서
분리했다. 합계의 약2e−12 차는 binary64 합산 수준이며 새 tolerance를
승인한 것이 아니다. 상세 scalar decimal70 추출은 동반 JSON에 있다.

r y=2.135162115662037351…e−14,
b=2.129675465104869176…e−14,
h_native=5.486650557168175221…e−17 per H per s다.
nH_SI=250.18675437302318×10^6 m^-3를 적용하면
R_native=1.372687295276845029…e−8 m^-3 s^-1이고,
E21=10.198714553953742 eV를 같은 event의 광자 에너지로 쓰면
E R=2.242990553943376501…e−26 J m^-3 s^-1다.

`r y`와 `b`는 departure 항이다. xr와 distortion은 signed일 수 있으므로
이를 항상 양의 microscopic gross down/up으로 명명하면 틀린다. 실제
population과 total occupation의 positivity는 baseline 복원 뒤에 평가한다.

## 3. 정확한 소유권 이동과 JVP 경계

e는313공간의 real2p index1 unit vector다. 다음 subtraction을 immutable
snapshot에서 **한 번** 생성한다.

M_off=M−r ee^T,
s_off=s−b e.

독점 새 소스 h_star를 사용한 잔차는
F_star(z)=M_off z−s_off+e h_star.
원본 h_star=r(z1−3xd)를 넣으면 모든 z에서 원본 Mz−s와 같다.
이는 reference snapshot해만 맞추는 조정이 아니라 항등식이다.
전단 q를 가진 새 소스는 먼저 이 source-compatible native mode와 구분해
계약을 고정한다. Duplicate ownership은 scalar boolean만 검사하지 말고
factory가 직접 baseline subtraction과 exactly-one insertion을 소유하게 한다.
Native diagonal/source를 남겨둔 채 e h_star를 더하는 경로는 거부한다.

현재 `PrimitiveTrajectoryProblem.native_jvp`와 같은 **frozen coefficient**
계약에서 independent변수는313 native departures z다. x,nH,H,TR,TM,
모든virtualcoefficients,incominghistory는고정이다.

J_star v=M_off v+e D h_star[v].

원본 source이면 Dh=r v1이며 J_star v=Mv다. 별도실험에서 incoming d를
독립boundary변수로 노출한다면 Dh=r(v1−3x δd), 그리고 여타 sv는 그대로
고정한다. 이는 전체historyJacobian이 아니다. x,H,nH,temperature방향의
전체 JVP는 원소별 rate/source/history계수의 미분을 추가해야 하므로 이번
frozen행렬 JVP에 포함된 것으로 표현하지 않는다.

## 4. Schur 축약에서의 최소 수정

V=Tvv matrix, W=Tvr^T, U=Trv라 놓으면
K_real=Trr−U V^-1 W,
c_real=sr−U V^-1 sv.

Lyα 항의 제거는 K_off=K_real−r e2 e2^T,
c_off=c_real−b e2다. V,U,W,sv가 고정이면 full block에서 owner를 이동한
뒤 Schur소거한 결과와 정확히 같다. 따라서 재사용 가능 인터페이스는
작은real2 공간의 rank-one update다. x_v=V^-1(sv−W x_r) 복원도 동일하다.
원본 frozen source 반환을 위해 여러 과거 원 solver를 다시 돌릴 이유가 없다.
후속 PR220 compact33 population계산과 이2+311 radiative algebra의 차원과
cohort는 다른 대상이므로 서로 바꿔 부르거나 실행 수를 합산하지 않는다.

## 5. History와 number/energy 연결

원 C는 현재 outgoing Lyα distortion을
 d_minus=y/(3x)
로 저장하고 다음 redshift step에서 이를 가장 가까운 아래virtualbin으로
전파한다. 현재 incoming d는 위virtualbin140의 **이전** history에서 온다.
따라서 다음 source-compatible crossing identity가 성립한다.

C_Lya=3x r [s^-1 per H per occupation],
h_native=C_Lya(d_minus−d).

CSV의 d_minus=7.6840819558108666e−15와 원 y/(3x)는 저장정밀도에서맞는다.
이 frozen source event의 number ledger는
(dn_2p,dn_1s,dn_gamma)=nH_SI(−h,+h,+h),
energy ledger는 (du_internal,du_gamma,du_kinetic)=nH_SI E(−h,+h,0)다.
이 bound-bound channel의 ionic/freeelectron yield는0이다. 그러나 전체
native xe_dot은 excited state algebra와 recombination/photoionization을
통해 간접 변하므로 전체 freeelectron evolution이0이라는 뜻이 아니다.

반면 사전에 계산된virtual escape/collision 항의합은 물리적 photon-cell
수로 바로 바꿀 수 없다. `original_hyrec_physical_flux.py`는 실제incoming,
average,outgoing occupation을 써서 별도phase-space crossing을 구성한다.
Virtualproxy에 그냥 nH를 곱해 radiationdensity로 해석하지 않는다.
Diffusion/recoil ledger는 이 직접 Lyα event ledger와 별도로 유지한다.

## 6. native와 LINE01의 차이, 그리고 source constant

Native population은 x2p=y+3x exp(−E21/TR)로 복원한다. `y`가 x2p가아니다.
Dfplus는 total occupation이아니다. Native직접항은 ground-state opacity와
Wien/departure compressed source를 사용한다. LINE01은 total Planck
boundary와 stimulated opacity, actual upper population을 사용하는 detached
유효line이다. 두것을 단순동일source라고 주장하면 안 된다.

Native `hPc=1.239841874331e−4 eV cm`를 E21로 나눈λ는 literalLYA_FACT를
상대2.22e−16 이내로 재현한다. 현대 exactSI h,c,eV에서 재계산한 hc는
1.2398419843320026e−4 eVcm이고 같은8π/(3λ³)가 native보다
**2.66165352758e−7 작다.** 이는 source상수규약 차이로 입력에 명시해야한다.
Source-parity 항에는 native literal계수를 쓰고 에너지SI출력에는 명시한
E21 eV→J conversion을쓴다. 근현대상수일치의물리모델교정은 별도변경이며
그 차이를 roundingtolerance로 감추지 않는다.

## 7. 가능한 source-compatible 각도확장과 한계

Ground-opacity convention에 한정해 bareA card를 별도확정하고
τ=A/r로정의하면 ρ=τ B(τ,S)는 원native directescape를finite-depth각평균으로
확장하는 한 방법이다. h_star=rρ(y−3xd), tensorinjection=nH E rτQ(y−3xd).
Thicklimit에서 tracefreeS와 isotropicincident에대해ρ=1,
τQ=2S/15이므로 scalarnative는그대로이고PSTFinjection을얻는다.

하지만 nativepin 자체에는 이 τ를복원하는bareA21가없다. 외부atomiccard와
기존LINE01 effectivecoincident2p가정을명시해야한다. Finiteextension의
outgoingdirectional값은 d+(y/(3x)−d)(1−exp(−τ/q))다. 이값은 native
thickhistory공식y/(3x)와일반적으로다르다. 따라서 frozenincoming과
진단output의bounded실험은가능하지만 nativehistory를그대로둔complete
coupledruntime교체로확대할수없다. 이의무는 다음leaf로기록한다.

## 8. 현재 최소 구현 제안과 명시적 열린 입력

1. 보존CSV를source고정parser로읽고full/residual및Schur필요block을노출한다.
2. `native_exact_owner` 모드로 직접Lyαdiagonal/bluepair만exclusive이동한다.
3. 같은packet으로number/energy/optionalPSTFoutput과frozenJVP를반환한다.
4. 필요하면별도`native_wien_finite_escape`모드를명시적atomiccard와도메인으로
   한정하고sourceexactmode와분리한다. Parent가생산행수·수용기준을실행전고정한다.
5. 저장state기준algebraidentity,일부off-equilibriumstate,d=0/음의distortion
   가능영역,duplicateowner,wrongfullbackgroundJVP를가장작은검사로판별한다.

CSV에는 history전체, causal interpolation timeindices/weights, 각도별incomingfield,
fullbackgroundcoefficients의derivatives, actualradiationstressstate가없다.
Complete native residual은source-bound frozen313공간에한정된다. 미완Liionic
yield,핵daughter/전자/중성미자/recoil/stopping및metricfeedback을채워주지않는다.

Physical HOLD, REC U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET,
global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false,
첫실패 REI raw historical local-only를 유지한다.
