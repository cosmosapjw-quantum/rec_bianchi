# R3 — 주장·전제 정렬

중앙 DAG28/88(+0), 단위 내용3/20. 이 문서는 source-point 수학 명제와 binary64 구현 수용 조건을 구분한다.

## 정의

독립변수 eta=ln(a), p=xHII, x1=1-p, 총 전자비율 xe. 원본 dispatcher 입력을 P=(xe,p,nH,H,TM_in,TR_in,fsR,meR)로 쓴다. Primary는 FULL/H_STEADY/He-neutral/xe=p/fsR=meR=1이다. 원본 순서 ratio=TM_in/TR_in, TR=TR_in/(fsR^2 meR), TM=ratio*TR를 한 번 수행한다. source의 실제 floating grouping을 그대로 둔다.

u=(u_v[0..310],u_Ly[0..1])는 원본 history interpolation이 계산해 저장한 signed occupation departure이다. 평균 radiation, outgoing radiation 또는 절대 occupation과 같지 않다. xr=(2s,2p)와 xv[311]도 원 source의 equilibrium departure이다.

s=SAHA_FACT(fsR,meR)*TR*sqrt(TR)*exp(-EI/TR)/nH,
D=xe*p-s*x1,
c_i=nH*(s*x1*DAlpha_i+Alpha_i*D).
c_i는 i=2s,2p에 대한 recombination/ionization source이고 단위는 s^-1이다. Beta_i는 s^-1, Alpha_i와 DAlpha_i는 cm^3/s이다. FH=-(c_0+c_1-Beta_0*xr_0-Beta_1*xr_1)/H는 eta당 무차원 비율 변화이다.

## 조건부 수학 명제

원래 tables/초기화/feature macros를 고정하고, CONTRACT.md의 scalar domain에서 모든 계수가 정의되고 유한하다고 하자. V의 원래 elimination pivots, diffusion 밖의 diagonal과 2x2 Schur determinant가 0이 아닌 point를 대상으로 한다. 이 조건은 이번 단계의 전제이며 전체 coefficient box에 대한 증명은 아니다.

M=[A B; C V], X=(xr,xv), S=(sr,sv)로 정의한다. A_ij=Trr[i][j], B_ib=Trv[i][b], C_bi=Tvr[i][b]. Trv와 Tvr의 저장 shape가 같아도 수학적 위치는 전치 관계의 block 위치이며 두 값 자체를 서로 교환하지 않는다. V의 row b는 diagonal Tvv[0][b], lower Tvv[1][b], upper Tvv[2][b]이다.

고정 P에서 M은 u에 의존하지 않고 S=S0+G u이다. 따라서 실수 대수에서 X=M^-1 S0+M^-1 G u이며 FH도 u에 대해 affine이다. 이 명제는 P까지 함께 바꾸는 global affine 주장도, binary64 결과가 정확히 affine라는 주장도 아니다. 실제 source assembly를 대조한 구성적 증명은 R5에 둔다.

같은 scalar 입력·table 초기화·incoming·branch·연산 순서로 history interpolation을 생략하고 assembly/solve/scalar만 호출하면 원본 point 계산 경로를 재현할 수 있다. 원본의 scalar가 계산된 뒤 수행하는 history write는 이미 산출된 FH를 바꾸지 않으므로 point API에서 제외할 수 있다. 이를 numerical parity와 caller nonmutation으로 검증한다.

## Primary charge accounting

원본 history의 H_STEADY 분기는 'Helium assumed entirely neutral; Tm fixed to steady-state'에 해당한다. 여기서는 xe=p이므로 dxe/deta=dp/deta=FH. H_STEADY라는 표기는 Tm closure이며 FH=0을 뜻하지 않는다. He가 남은 다른 phase에서 Fe=FH라고 주장하려면 helium derivative가 추가로 필요하므로 이번 primary에서 제외한다.

## 구현에서 확인할 별도 조건

원본 source가 사용한 binary64 입력을 정확히 결속한다. 새132점에서 FH/xr/xv bitwise count를 실제 보고하고, 필수 FH acceptance는 R1의512 eps64 S_F, independent block residual은4096 eps64로 고정한다. Residual은 계산된 block 방정식에 대한 backward diagnostic이며 forward error나 inverse-gain 인증이 아니다. 원래 내부 divisor 관측 방식은 C3에서 연산을 바꾸지 않는 제한된 방법으로 결정한다.

626 endpoint references는132 native writer에 대한 반복 참조이다. 이를626개의 독립 실행으로 세지 않는다. Native eta와 geometric eta가 다르면 slope 차이는 clock tag가 있는 point diagnostic이며 whole-domain defect로 승격하지 않는다.

## 남은 의무

R4는 explicit incoming 분리와 대안의 판별을 구성한다. R5는 source-level affine/block/side-effect 경계를 유도한다. 실제132점 binding·새 adapter 실행·표현 오차·nonmutation은 C단계의 필수 의무로 남아 있다. Physical0/313과 모든 physical certificate null을 유지한다.
