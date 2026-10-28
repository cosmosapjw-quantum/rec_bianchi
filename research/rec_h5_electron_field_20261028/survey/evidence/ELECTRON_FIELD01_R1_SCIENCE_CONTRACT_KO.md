# REC-H5-ELECTRON-FIELD01: R1 과학 계약 제안

2026-10-28 UTC · `/root/survey_science_synthesis` · source intake/해석만 수행, 새 science 실행 0.

## 판정과 정확한 대상

**제안한 단위는 최소 실질 다음 연결에 해당한다.** 복원 원본의 실제 FULL electron RHS를 history-global-state와 분리된 함수로 공급한다. Native PATH01이 확보한 관측·저장값을 재사용하면서 downstream field 평가가 사용할 실행 경계를 만든다. QSS03 inverse-gain/정칙성 인증, 원 history 재적분, dense extension은 이 단위의 완료 조건에 넣지 않는다.

대상 함수는 `FULL_ELECTRON_POINT(P, I, tables) -> F_H, diagnostics`다. `P=(xe,xHII,nH,H,TM,TR,fsR,meR)`는 **원 dispatcher의 represented binary64 입력**이고, `I=(Dfplus[311],Dfplus_Ly[2])`는 해당 최종 writer가 실제 사용한 incoming occupation departure다. primary는 source-locked H_STEADY/He-neutral132개 최종 writer에 한정하며 이 분기의 total `F_e=F_H`다. H+He의 total source에는 별도 He RHS가 필요하다.

`F_H`는 무차원 `eta=ln(a)`에 대한 derivative다. `nH`는 cm^-3, `H`는 s^-1, `TM/TR`는 eV다. API가 Kelvin/m^-3를 받는다면 변환 wrapper를 별도 명명하고 원 native constants/연산 순서를 유지한다. 원 함수의 실수 수학적 표현과 binary64 실행값을 각각 기록하며, native parity를 exact-real enclosure로 승격하지 않는다.

## 정의역·존재 조건

모든 scalar·incoming은 유한값. `H>0`, `nH>0`, `0<=xHII<1`, `xe>=0`, `TM>0`, `TR>0`. Primary는 실제 source의 `fsR=meR=1`, `xe=xHII`, He-neutral branch로 동결한다. 일반 parameter 변화는 별도 extension이다. Native rescale 이후 `TR`는 원 table domain `[0.004,0.4] eV`, `TM/TR`는 `[0.1,1]` 안에 있어야 한다. 실제 original tables·energy grid·feature macros·rate interpolation을 byte identity로 결속한다.

`Dfplus`, `xr`, `xv`는 **signed departure**다. 비음수 요구를 걸지 않는다. `xr=(2s,2p)`, `xv=x1s*Dfnu`라는 원 semantics를 보존한다. 필요한 division denominator/삼대각 pivot/2x2 Schur determinant는 0이 아니어야 하며 산출물이 유한해야 한다. 이러한 point 적용 조건과 실제 numerical residual을 기록한다. 이번 단위는 coefficient box 전체의 nonsingularity나 inverse gain을 증명하지 않는다.

## 기준식과 계산 순서

원 prelude를 정확히 한 번 적용한다: `ratio=TM/TR; TR=TR/(fsR*fsR*meR); TM=ratio*TR`. **fsR=meR=1에서도 ratio roundtrip이 TM을 바꿀 수 있다.** QSS 기록의 rescale 이후 coefficient temperatures를 dispatcher 입력으로 재투입하지 않는다. Dispatcher/계수 temperatures를 출력 provenance에 함께 남긴다.

순서는 `explicit incoming → populateTS_2photon → solve_real_virt → F_H`다. 원 matrix orientation·제로 초기화/allocator 계약·summation order·1e-6 optical-depth branch·legacy exponential 표현·feature macros를 보존한다. 성능 개선이나 stable-escape 교체를 동시에 넣지 않는다.

`p=xHII`, `x1s=1-p`, `s=SAHA_FACT*TR^(3/2)*exp(-EI/TR)/nH`, `Delta=xe*p-s*x1s`에 대해

\[
F_H=-\frac1H\sum_{i=0}^1\left\{
n_H[s\,x_{1s}D\alpha_i+\alpha_i\Delta]-x_{r,i}\beta_i\right\}.
\]

`DAlpha_i=Alpha_i(TM,TR)-Alpha_i(TR,TR)`이며 `Beta_i`는 그 뒤 source detailed-balance factor를 곱한 photoionization coefficient다. Source는 `hydrogen.c::rec_HMLA_2photon_dxHIIdlna`, 함수 정의의 SHA256은 원 SOURCE lock에 결속한다.

원 dispatcher는 RHS 계산 뒤 현재 slot의 outgoing/average radiation history에 쓴다. 새 adapter는 과거 history interpolation을 호출하지 않고 explicit incoming을 읽으며, caller arrays·tables·전역 history·files를 수정하지 않는다. Radiation 출력을 제공한다면 fresh local arrays로 반환한다. F_e 공급에 필요하지 않은 history integration은 호출하지 않는다.

## Primary binding과 수용 기준

원 source ZIP identity는 `94b454c75b51f7c7af38126510cec609f5d7cfb2eb69ca78a491def54b31791c`, 110654069 bytes다. 실제 primary set은 source의 `LAST_WRITERS[slot]`, `QSS_WRITES.id/slot`, `CALLS.id/slot`을 일치시켜 고정한다. 단순 slot-only join이나 마지막 배열값의 암묵적 선택을 쓰지 않는다. 기대132개 집합·중복0·누락0을 source 목록에서 먼저 확정하고313 query/626 endpoint reference mapping을 보존한다.

**수용 기준을 첫 실행 전에 고정한다.** 같은 source 연산을 사용하는 wrapper의 1차 기대값은 saved native hex와 bitwise equality다. Toolchain 차이를 허용하는 추가 수치 gate가 필요하면 root가 최초 primary 전에 명시한다. F_H의 상쇄 때문에 `|F_new-F_saved|/|F_saved|`만 쓰지 말고 다음 source gross scale을 함께 기록한다:

\[
S_F=H^{-1}\sum_i\{n_H(|s x_{1s}D\alpha_i|+|\alpha_i\Delta|)+|x_{r,i}\beta_i|\}.
\]

`c*eps64*S_F` 같은 보조 gate의 `c`는 사전 선택이며 수학적 roundoff certificate와 구별한다. 실패 후 tolerance를 넓혀 원 gate PASS로 기록하지 않는다. Native parity 외에 선택된 독립 식/역대입 검산, 실제 block residual, dispatcher→coefficient temperature 대응, input/table nonmutation, malformed/nonfinite/domain/shape/foreign-source 거부를 확인한다. 검토는 변경 adapter와 실제 결과에 한정한다.

새 point FULL matrix/source 호출은 **새 field 검증 실행 수**로 센다. 원 producer/native full-history/reference/oldtests/QSS03 certificate 재실행은 0이다. Primary132개가 필요하다면132개로 명시하고 새 통제값·independent probes를 별도 기록한다.

## 출력·진전·다음 의존성

각 output은 source/table/adapter/toolchain identity, call_id/slot/phase, actual native z, input hex, rescaled temperatures, incoming identity, F_H hex, saved parity 및 numerical residual을 갖는다. 313 mapping의 affine slope와 native F_H의 차이는 **clock-tagged point diagnostic**이다. 기하학적 cell 전체의 `F_e` enclosure, continuous physical defect, initial/model error로 사용하지 않는다.

새로 확보하는 것은 실제 source-point F_e 공급자다. 다음 의무는 같은 history/phase reference 위의 whole-cell field enclosure 또는 native reconstruction의 continuous defect다. `physical query/K/M2/defect/L/tube/e0/epsilon/outgoing=null`, physical0/313, H6/H7 OPEN, L4/REI false, canonical28/88+0를 유지한다. R/C 완료·단계별 게시/dual ACK는 실제 산출물/수신 뒤 각각 기록한다.

모델 provenance: 요청 Astra 역할, 호스트 표기 GPT-6 Astra Pro; 별도 runtime model-id 및 다른 계열 독립성은 관측하지 않았다.
