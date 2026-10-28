# R9 — 정식 결과와 구현 계약 연결

중앙 DAG28/88(+0), 단위 내용9/20. R1 CONTRACT의 정확도·범위·예산을 유지한다.

## 결과

고정된 original scalar point P와 initialized source tables에서, V와 Schur complement가 가역이면 explicit incoming u로부터 real/virtual departures X를 구하고
FH=-(c_0-Beta_0*xr_0+c_1-Beta_1*xr_1)/H
를 반환하는 source-equivalent point component를 구성할 수 있다. Incoming에 대한 실수 affine성, source scalar, history 경계와 He-neutral Fe=FH는 R5에서 유도했고 R6에서 독립 검토했다.

## 필수 API 의미

- 입력: 원 dispatcher binary64 xe,xHII,nH_cm3,H_s_inv,TM_eV,TR_eV,fsR,meR와 incoming_virtual311,incoming_Lyman2.
- Primary binding: FULL=3,H_STEADY,He-neutral,xe=xHII,fsR=meR=1. 기타 phase에 총전자 Fe를 붙이지 않는다.
- Incoming과 outputs xr/xv는 signed departures이다. 적법한 음수를 clipping하지 않는다.
- Context initialization은 original read_rates/read_twog_params를 사용하며 원 table 정규화·feature switches·allocator 초기화를 포함한다.
- Point call은 original ratio/rescale/reconstruct를 정확히 한 번 수행하고 원 populateTS_2photon와 원 solve/scalar의 연산 순서를 따른다.
- Point call에서 history interpolation, history integration, outgoing history writes, 파일 IO를 하지 않는다. Caller 입력과 initialized tables는 변하지 않는다.
- 출력: FH와 primary scope가 확인된 Fe=FH, xr2,xv311, coefficient temperature provenance, 원 coefficient block/source diagnostics, actual divisor diagnostics, status. Physical certificate 필드와 혼합하지 않는다.

C3에서 원 solver를 추가로 실행하지 않는 관측 방법을 확정한다. 후보는 original hydrogen.c를 불변 입력으로 남기고 generated build copy에 value-only observer를 넣는 방식이다. Native arithmetic을 재배열하거나 solver를 대체하는 변경은 허용하지 않는다.

## 저장 데이터와 식의 결속

LAST_WRITERS[slot]의 실제 call id와 CALLS/QSS_WRITES의 (id,slot)을 함께 맞춘다. CALLS의 dispatcher scalar hex가 출발점이며 QSS_WRITES의 coefficient temperature는 결과 provenance의 비교 대상이다. 선택한132개 writer의 completeness,phase,model,xe/xHII,fsR/meR,finite/domain을 확인한다.

원 native_path313 query와626 endpoint references는 reference map으로 보존한다. Geometric endpoints/query/exact alpha를 재계산하거나 rounding하지 않는다. 하나의 native writer가 여러 endpoint에 참조되는 것을 독립적인 새 scientific call로 세지 않는다.

## 수용 기준과 독립성

R1의512 eps64 S_F scalar parity 및4096 eps64 normalized block residual을 그대로 적용한다. Bitwise FH/xr/xv equality는 실제 count를 별도로 보고한다. Zero scale/denominator 처리도 R1을 따른다.

Independent residual은 C solver가 출력한 합성 residual을 신뢰하는 방식이 아니라, 저장된 block coefficients와 X를 별도 Python reconstruction에서 올바른 B/C 및 band 방향으로 결합해 계산한다. 이것은 solver와 독립적인 방정식 검산이며 coefficient assembly 자체의 새 물리 oracle는 아니다. 실제 coefficient source가 original인지는 byte identity/diff/source trace로 연결한다.

부호·단위·phase·shape·비유한값·잘못된 temperature provenance, incoming omission 및 block orientation을 구별할 필요한 control만 수행한다. Mutation 결과는 검증의 판별력을 보이는 데 쓰고 physical source 결과와 합치지 않는다.

## 실행과 인계

C1 baseline/input identity → C2 식/자료/함수 mapping → C3 numerical/observer design → C4 bounded execution DAG → C5 complete adapter → C6 contract controls → C7 one132-point primary → C8 independent reconstruction/precision/plots → fresh nonauthor C9 → C10 complete source/delivery.

실제 명령·compiler·source·input·result·cost·failure를 보존한다. Remote CAS의 reportedCPU0.06227s를60CPU 합계에 포함하며 local child에는 남은59.93773CPU를 사용한다. 기존 science 캠페인 예산과 결과는 재사용만 하고 새 point calls와 별도 계상한다.

이 구현은 physical0/313을 변경하지 않는다. 다음 full-state 단계는 실제 continuous coupled F,model discrepancy,e0,full-state norm,positive tube와 whole-domain defect를 별도로 공급해야 한다.
