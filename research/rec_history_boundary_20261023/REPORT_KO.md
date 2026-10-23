# REC-HISTORY-01 — native history 경계와 고정 상태 응답

> **전달 상태 갱신 (2026-10-23 18:49:46 UTC):** 과학·독립 검토는 PASS_SCOPED다. GitHub 쓰기 호출이 응답 없이 중단됐고 두 target branch의 실제 readback은 404다. 새 commit/PR 및 중앙 DAG 게시는 **미완료**다. R10/C10은 인계 준비 완료·게시 미완료로 기록한다. `delivery/PUBLICATION_STATE.json`이 이 전달 상태의 기준이다.

## 판정과 이번 단위의 기여

`REC-HISTORY-01`은 native scalar history의 소유권, 유한 Lyα outgoing 경계,
history 입력에 대한 고정 계수 응답을 연결한 유한 작업 단위다. Primary는
**608/608 checks**, 독립 검토의 추가 세 사례는 **14/14 checks**를 통과했다.
원 C와의 20개 scalar 보간 비교 및 313개 실제 연결 비교는 이 입력에서
차이가 0이었다. 과학 판정은 `COMPLETE_SCOPED_BOUNDARY`이며 부모
`REC-HISTORY`는 `PARTIAL`이다. 최종 검토는
[독립 검토 기록](evidence/independent_review/FINAL_REVIEW.md), 실제 Git/provider
전달은 별도의 delivery receipt에 연결한다.

이 결과는 기존 LINE02의 한 Lyα source 방향을 넘어, incoming 313개 채널이
실제 native RHS와 outgoing 314개 채널에 전달되는 경로를 명시한다.
실제 물리 history의 보간 정확도는 `INPUT_DEPENDENT_UNCALIBRATED`이며,
방향 의존 Bianchi 전파에는 별도의 geodesic·direction·frame 입력이 필요하다.
확인한 유한 경계 계약을 REC-FIELD의 source/interface 계약에서 재사용할 수
있으며, 이 두 입력 gate의 상태를 함께 전달한다.

## 1. 출처, 이전 결과와 최종 receipt

시작점은 사용자가 고정한
[중앙 인계](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17/research/orchestration_longterm_20261023/assembly/HANDOFF_rec_bianchi_KO.md)다.
실제 REC parent는 `a7c46fd8338971e2cefa776f5dd7b25a46974990`, tree는
`dfa61d68aacfd3d3adc7ac5a5603f10e67349e3e`였다. 해당 소스 경로에 적용되는
root/research AGENTS는 없었고, 병렬 branch/PR와 실제 HEAD를 조사했다.
기존 LINE02 branch 대신 별도 history branch와 이 디렉터리를 사용한다.

LINE02의 과학 결과는 재실행하지 않았다. 194 checks, 202 rank queries,
primary 2.077208039998368 s, 완료된 독립 검토를 기존 identity 아래 재사용했다.
이미 소비된 여섯 historical review probes와 raw 미가용 상태도 보존했다.
이전 allocation의 잔여 시간을 새 allocation으로 옮기거나 초기화하지 않았다.

중앙의 `final_delivery_receipt_pending`은 고정 인계 당시 상태다. 담당자의
[최종 전달 comment](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/129#issuecomment-6360118229)와
실제 companion receipt를 확인했다. Receipt SHA256은
`140ce4227c907c2f4ae9c21989f98b9a5e6992082fb0307c8ff9dbaa51a1a0ad`이고,
최종 ZIP은 1,290,105 bytes, SHA256
`0aa14797b32c910d94d7fcdbd42f1aea1c4d13d6bea536a89e8282f86d6e4db4`다.
현재 Dropbox와 Drive metadata/size가 일치한다. Dropbox whole-byte·CRC·102
payload 확인은 담당자의 완료 기록을 재사용한다. Drive는 ACK+size 수준이며
whole-byte readback은 `NOT_RUN`이다. 두 provider의 근거 수준을 합쳐서
새 byte-readback 성공으로 표시하지 않았다.

실제 읽은 원전은
[native hydrogen.c](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/a7c46fd8338971e2cefa776f5dd7b25a46974990/research/rec_line_native_owner_20261023/vendor/hydrogen.c),
동일 pin의 hydrogen.h, retained CSV 및 이미 준비된 PREPARED_BLOCKS.npz다.
입력·소스 83개의 Git blob 대응은 [SOURCE_IDENTITY](provenance/SOURCE_IDENTITY.json)에
기록했다. C oracle은 원 함수를 추출했으며 실제 recombination runtime은
실행하지 않았다. 두 real RHS 원문 행은 서로 떨어져 있어 연결 fragment
자체가 연속 substring은 아니다. 각 행의 byte identity와 위치는 독립 검토의
[source supplement](evidence/independent_review/results/extra001/SOURCE_STATEMENT_SUPPLEMENT.json)에 있다.

## 2. 경계식과 광자수·에너지 소유권

Metric signature는 `(-,+,+,+)`이며 local non-tilted orthonormal frame을 쓴다.
Occupation과 departure는 무차원, 고유시간은 s, native 에너지는 eV다.
`TR_eV`는 `k_B T_r`의 eV 표현이며 energy ledger는
`E21_J = E21_eV × 1.602176634×10^-19 J/eV`로 변환한다.
현대 SI phase density는 `E^3/(π^2 ℏ^3 c^3)`로 두 편광을 포함한다.

`x=x1s>0`, `s=xr_p/(3x)`, `u=τ/q`, `q>0`라 두면

\[
T=e^{-u},\qquad A=-\operatorname{expm1}(-u),\qquad
d_{out}=d_{in}+(s-d_{in})A.
\]

`τ≥0`에서 투명 한계는 `d_out=d_in`, 두꺼운 한계는 `d_out=s`다.
Transmission이 underflow해도 `log T=-u`는 유한 값으로 보존한다.
물리적 허용 조건은 native Wien 기준 `f_W=exp(-E21/TR_eV)`에 대해
`f_W+d_in≥0`, `f_W+s≥0`이다. 음수 departure 자체는 허용되며 clipping하지 않는다.
수치 검증의 reference occupation은 명시한 manufactured fixture다.

Native 정규화는

\[
G_N=3\times10^6\,\mathrm{LYA\_FACT},\qquad
r_0=\frac{\mathrm{LYA\_FACT}\,H}{n_{H,cm^{-3}}x},\qquad
R=G_N Hq(s-d_{in})A.
\]

`LYA_FACT=4.662899067555897×10^15 cm^-3`를 그대로 사용한다.
`q=1`에서는 정확히

\[
R=n_{H,SI}r_0 A(xr_p-3x d_{in})
\]

가 되어 LINE02의 atomic event rate와 경계 광자수 flux가 같은 사건을 센다.
`R>0`이면 원자 내부 에너지는 `-E21_J R`, 복사 에너지는 `+E21_J R`다.
흡수에서는 부호가 함께 바뀐다. Outgoing occupation 저장은 이 복사 사건의
경계 표현이며 두 번째 가산 radiation source를 만들지 않는다.
각방향에서 `q`는 flux weight에도 필요하다. 방향 평균을 사용할 때는
`<q A(s-d_in)>`을 적분해야 한다.

Native `G_N`과 현대 SI phase density의 약 `2.66×10^-7` 상수 convention
차이는 기존 LINE02의 구분을 유지한다. 이를 parity tolerance 안으로 숨기거나
한쪽 정규화를 다른 쪽으로 바꾸지 않았다. 서로 다른 에너지 경계 사이의
retarded transport는 redshift work와 dilution을 포함하는 transport 문제다.
그 에너지 차이를 추가 gas heating으로 배정하지 않는다.

## 3. 실제 native history 연결과 미분

원 C는 outgoing `virtual311, Lyα, Lyβ, Lyγ`의 314개를 저장하고,
incoming `virtual311, Lyα, Lyβ`의 313개를 소비한다. Lyγ blue는 prescribed
thermal boundary다. Virtual139의 upstream은 Lyα red, virtual270은 Lyβ red,
virtual310은 Lyγ red이며, Lyα/Lyβ blue의 upstream은 각각 virtual140/271이다.
나머지는 바로 위 virtual bin의 red edge를 읽는다.

Scalar clock은 `η=ln a`이고 수학적으로
`η_emit=η_face-ln(E_source/E_target)`이다. 엄격한 C parity에는 원 연산 순서
`-log((1+z_face)*E_source/E_target)`를 사용한다. 두 동등 표현의 binary64
query 차이는 이번 fixture에서 최대 `8.881784197001252×10^-16`이었다.
이 차이를 보간 오차 gate의 완화로 처리하지 않고 원 clock 순서를 맞췄다.

시작 전 또는 `iz<2`이면 thermal departure 0을 반환한다. 그 외에는
`η_emit < η0+h(iz-1)`가 필수다. 최신 저장 endpoint와의 등호도 거부한다.
`k=floor((η_emit-η0)/h)`, `α=(η_emit-η0)/h-k`로

\[
I[d]=(1-\alpha)d_k+\alpha d_{k+1},\qquad
\delta I=(1-\alpha)\delta d_k+\alpha\delta d_{k+1}
+\frac{d_{k+1}-d_k}{h}\delta\eta_{emit}
\]

를 쓴다. 구현의 이 JVP는 grid origin/spacing을 고정한다.
기준 grid 자체를 미분할 경우의 `δη0`, `δh` 항은 THEORY의 일반식에 있으며
이번 API의 입력이 아니다. 매듭에서 query tangent가 0이 아니면
`NONSMOOTH_QUERY`로 거부한다. Array-value tangent는 그대로 정의된다.

Thermodynamic/geometry 계수를 고정하면 `M`은 incoming `u`에 독립이고,
RHS는 `s_base+B u`다. 실제 원문의 비영 계수는

\[
B_{2s,\beta}=3r_0x(1.664786871919931),\quad
B_{2p,\alpha}=3r x,\quad
B_{b,b}=T_{vv,0,b}xP_b.
\]

Native thick convention에서 `r=r0`이며 finite Lyα에서는 `r=r0 A(τ)`다.
기존 Lyα diagonal/source pair를 이 값으로 교체하고 outgoing도 같은 `A`로
바꾼다. Virtual diffusion/feedback owner는 원 C에 남는다.
`P_b`, small-depth branch, `E32/E42` literal도 native convention을 유지한다.

고정 계수 outgoing을 `O X+P u`로 쓰면, 해당 `M*`가 가역인 범위에서

\[
\delta X=M_*^{-1}B\,\delta u,\qquad
\delta d_{out}=(OM_*^{-1}B+P)\delta u,\qquad
\delta u=I\delta h_{past}+I_{query}\delta\eta.
\]

이것이 이번에 구현·검증한 history 응답이다. 온도·밀도·opacity·geometry가
변하는 방향에는 `δM, δB, δO, δP`와 departure 기준의 변화가 추가된다.
그 전체 thermodynamic/cosmological Jacobian은 후속 작업이다.

## 4. 오차 경계와 물리 calibration의 구분

각 cell에서 `|d''|≤M2`가 성립하면 보간 remainder와 endpoint uncertainty는

\[
e_u\le\frac12M_2h^2\alpha(1-\alpha)
+(1-\alpha)e_k+\alpha e_{k+1}
\le\frac18M_2h^2+(1-\alpha)e_k+\alpha e_{k+1}
\]

로 제어된다. 국소 source가 고정된 line 경계의 input multiplier는 `T≤1`이다.
Population 반응을 포함하면 전체 `OM*^-1B+P`를 거쳐야 하므로 `T`만으로
전체 coupled sensitivity를 제한할 수 없다.

이번 native binary64 `M`에서는 off-diagonal이 비양수이고 양의 비교벡터
`v=M^-1 1`에 대해 roundoff를 포함한 `Mv` 하계가 양수였다.
`min v=0.0044175127019473745`, `min lower(Mv)=0.9999999997256701`이다.
대각 scaling 후 엄격한 row diagonal dominance가 얻어지므로 이 표현된
고정 Z-matrix는 nonsingular M-matrix다. 따라서 `l≤Mv`, `l>0`이면

\[
|M^{-1}b|\le v\max_i\frac{|b_i|}{l_i}
\]

를 사용할 수 있다. Dot-product roundoff는 `γ_(2n+4)`와 `n=313`,
sum-of-absolute-products의 rounding, underflow reserve 및 outward
`nextafter`를 포함했다. Native 두 방향의 비교 경계 비율은 각각
`0.9893851592798474`, `0.9888073882842935`였다. 이 certificate의 대상은
표현된 native matrix와 명시한 RHS다. Finite `τ=2`의 응답은 별도 방향
검증으로 확인했으며 그 matrix의 전 범위 inverse bound를 추가로 주장하지 않는다.

`exp(0.7η)`와 `2+cos(1.3η)`, 세 spacing, 여덟 cell fraction으로 만든 48개
query는 알려진 곡률 아래의 경계를 모두 만족했다. 저장된 최대
`error/(envelope+arithmetic)`는 `0.9993726459433282`다.
이 수치는 manufactured history에 대한 검증이다. 실제 재결합 history에는
동일 source/frame/에너지·시간 범위의 reference 또는 정당화된 곡률·오차
증인이 필요하다. 기존 실제 history 후보와 admission 공백은
[입력 inventory](provenance/HISTORY_INPUT_INVENTORY.json)에 따로 기록한다.

## 5. 실제 실행과 독립 검토

| 검증 | 실제 수행 | 결과/최대 scaled error |
|---|---:|---|
| Local finite boundary | 6 τ × 3 q × 3 drive = 54 controls | outgoing `5.904893590378962e-17`; 허용 `128 eps64` |
| Native scalar interpolation | 20 controls | C와 차이 0; 허용 `64 eps64` |
| Native routing | 313 channels, manufactured history 1개 | C와 차이 0; future sentinel 미참조 |
| JVP | 12 directions | 최대 `2.213865713526952e-16`; 허용 `5e-9` |
| Frozen full-system response | native 2 + finite τ=2 1방향 | backward 최대 `1.2096536618663131e-15`; 허용 `5e-12` |
| Dense RHS solves | 8 | 사전 cap 8 이내 |
| Analytic interpolation envelope | 48 queries | 모두 통과 |
| Invalid/owner | 20 | 명시한 오류 거부 |
| Deliberate mutations | 4 | transfer 부호, 정규화, future read, 이중 source 검출 |
| 독립 추가 검토 | 3 cases / 14 checks | 전부 통과; 추가 solve/compile 0 |

608은 assertion 수이며 서로 다른 물리 모델 608개를 뜻하지 않는다.
실제 과학 primary는 한 번이다. 추가 세 사례는 complex source/outgoing의
실수·허수 성분, `τ=0`의 source/diagonal 제거, signed departure의 reference
전달과 atomic-side ledger를 확인했다. 검토자는 원 C, 유도, 실제 코드,
raw 결과 및 PNG를 읽고 같은 한 차례의 changed-source review를 완료했다.

그림 두 개는 primary의 저장 행에서 생성했다. 최초 경계 그림은 symlog
눈금이 겹쳤으므로 원본을 보존하고 54개 저장 행만 다시 표시했다.
대표 그림은 [수정된 boundary controls](results/figure_repair001/history_boundary_controls.png)와
[interpolation bounds](results/attempt001/history_interpolation_bounds.png)다.
두 그림은 실제 열어 검사했다. 추가 scientific case는 0이다.

## 6. 자원·환경·보존

동결 allocation은 새 작업 전용 CPU 60 s, execution wall 180 s,
1 thread, RSS 1 GiB다. Primary 90 s timeout을 사용했다.

| 실행 | CPU charge s | Wall s | 역할 |
|---|---:|---:|---|
| primary001 | 3.153510 | 3.076568607 | import·C compiler 자식 포함 |
| figure_repair001 | 1.531904 | 1.500661846 | 저장 행 표시만 수정 |
| review001 | 0.162777 | 0.159337515 | 독립 세 사례 |
| 누적 | **4.848191** | **4.736567968** | 이전 budget과 합치거나 reset하지 않음 |

최대 관측 child RSS는 105,380 KiB다. Primary 내부 timer 2.594744 CPU s보다
외부 inclusive charge를 budget의 기준으로 채택했다. Primary의 live-session
monitor는 host/sandbox PID namespace 차이 때문에 0을 보고했다. 원 receipt를
그대로 보존하고 해당 enforcement 문구의 한계를 기록했다. Wall timeout,
per-process RLIMIT_CPU/RLIMIT_AS, 종료 후 inclusive getrusage는 유효했다.
후속 controller는 host child session을 찾아 monitor가 실제 작동했다.
이 metadata 교정으로 과학 검증을 다시 실행하지 않았다.

Python과 C++ 실제 capability probe는 성공했다. Git clone의 network proxy
실패는 source snapshot+GitHub API 방식으로 해결했다. mpmath가 없다는 실제
import 실패 후 전용 `/tmp` 경로에 1.3.0을 설치했고, 시스템 package를 바꾸지
않았다. NumPy 2.3.5, SciPy 1.17.0, matplotlib 3.10.8, Python 3.12.14 및
실제 C compilation 명령을 보존했다. 코드·동결 계약의 실행 당시 snapshot,
원 C fragment, raw JSON/NPZ, 실패/환경 관측, resource receipt를 함께 전달한다.

## 7. 재개점

R1–R10/C1–C10의 이 유한 단위 근거는 [LOOP_PROGRESS](LOOP_PROGRESS.json)에
대응시킨다. 부모 DAG와 claim gate는 [GLOBAL_DAG](GLOBAL_DAG.json),
[CLAIM_GATES](CLAIM_GATES.json)에서 분리한다. 다음 작업은
[NEXT_INPUT_CONTRACT](NEXT_INPUT_CONTRACT.md)의 실제 history uncertainty와
directional characteristic 입력 admission이다. 새 IVP와 old campaign replay는
이 계약의 허용 범위에 포함되지 않는다.

Physical `HOLD`, REC_U5 `HOLD_9_FAIL/HOLD_8_FAIL`,
`CLOSED_HOLD_NOT_RESET`, global convergence `NOT_RUN`, production
`NOT_APPROVED`, `REI_activation=false`를 유지한다. 새로운 strong no-go는
주장하지 않는다. 미완료 항목은 구체적인 입력·미분·coupling 의무로 남긴다.
