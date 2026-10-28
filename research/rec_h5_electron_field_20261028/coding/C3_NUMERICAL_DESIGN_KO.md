# C3 — 수치 설계와 관측 방식

중앙 DAG28/88(+0), 단위 내용13/20. Scientific implementation/execution은 아직 not_run이다.

## 연속식·closure·이산화·실행 순서

대상은 HyRec May2012의 effective real/virtual-state closure와311-bin radiation 이산화이다. 새 시간적분·새 closure·새 interpolation을 도입하지 않는다. 명시적인 incoming을 고정해 원 source의 point algebra를 평가한다.

원본 table initialization → dispatcher input provenance/domain 확인 → 정확한 temperature prelude → zero-initialized fresh block → original populateTS_2photon → original solve_real_virt → 원 scalar grouping → fresh diagnostics/result → 해제 순서를 사용한다. 원본 source의1e-6 branch, cubic rate interpolation, diffraction/diffusion band와featuremacros를 유지한다. 이 문서에서 diffraction은 사용하지 않으며 실제 알고리즘 대상은 source의 frequency diffusion이다.

Storage는 source/input identity와 hex binary64 values를 보존한다. Output의 physical query/K/M2/defect/L/tube/e0/epsilon/outgoing에 결과를 채우지 않는다. New source-point results는 별도 이름으로 기록한다.

## Actual nonzero divisor 관측: 선택 완료

Original hydrogen.c를 불변 입력으로 보존하고 deterministic generated build copy를 만든다. Allowed native-body 변화는 observation header 선언과 아래3개 value-only hook insertion뿐이다.

1. solveTXeqB의 첫 diag[0] division 직전에 이미 존재하는 diag[0]를 관측한다.
2. 기존 denom assignment 바로 뒤에서 그 denom을 관측한다.
3. 기존 Schur det assignment 바로 뒤에서 그 det를 관측한다.

Tvv가 solver에서 바뀌지 않는다는 source 사실을 이용해 diffusion 밖231개 diagonal은 adapter entry에서 한 번씩 읽는다. 세80-pivot Thomas solve에서240개, outside231개,Schur1개로 총472events/point가 예상된다. Actual count,finite 여부,zero 여부,min absolute value 및Schur값을 기록한다. 이 관측은 coefficient-box 인증이 아니라 실행한 point에서의 native divisor 확인이다.

Observer는 arithmetic argument/array를 변경하지 않고 값을 복사하거나 진단 count/minimum만 갱신한다. Point-scoped thread-local diagnostics pointer를 entry에서 저장하고 모든 반환 경로에서 복원한다. 원 arithmetic grouping/solver/loop/summation order는 바꾸지 않는다. 추가 assembly/solve0이다. Generated diff와 실제count는C9검토대상이다. Hook에따른 compiler spill 변화가능성이 있으므로bitwisecount를미리약속하지않고frozen numericalgate를사용한다.

## 입력/오류 처리와 purity

Caller의 dispatcher inputs와signedincoming은 read-only이고,legacy비constsignature에는localcopy를전달한다. Table context는 originalinitializer로만들고 point마다reload하지않는다. Context arrays를전후대조해nonmutation을확인한다. Temperature provenance label은dispatcher여야하고coefficient-stage자료의재투입은binding/API경계에서거부한다.

NaN/Inf,shape불일치,H/nH/temperature비양수,범위밖ratio/TR,xHII>=1,음수xe,foreignmodel/phase/speciesbinding등을nativecall전에구별한다. Primary에서는fsR=meR=1과xe=xHII를확인한다. Signedincoming에는양수조건을추가하지않는다. 적법한arbitraryincoming이물리적spectrumpositivity를갖는다는주장은없다.

## 독립 residual와 정확도 판단

원 coefficient arrays A,B,C,V,sr,sv와 X를 exacthex로저장한다. 별도Python검증은B=Trv,C_bi=Tvr[i][b],Vlower=Tvv[1],Vupper=Tvv[2]를명시적으로재구성한다. 소거/Schur알고리즘을재실행하지않고 MX-S를직접계산한다. Sparseband를사용하므로132점의검증량은O(132*311)이며denseinverse를구하지않는다.

Authoritative acceptance는 Decimal80으로 represented binary64 coefficient/input/output을읽어 scalar S_F 및block residual을평가한다. Source가이미계산한s,x1,Delta,Alpha,DAlpha,Beta,H,nH를저장하여다른exp/interpolation경로를섞지않는다. Exacthex→exactfloat→Decimal.from_float 변환을쓰고,곱/합의workingprecision을80decimaldigits로고정한다. C8의40/80비교는대표점3개에만적용해이진표현에서잔차재구성의정밀도의존성을확인한다. 이것은rigorousintervalroundoffcertificate가아니다.

필수gate는512eps64*S_F와4096eps64,zero-denominator규칙으로변하지않는다. FH/xr/xvbitwisecounts는별도로보고한다. Smallresidual만으로forwarderror/inversegain/physicaltube를주장하지않는다.

## 필요한 판별 control

원 inputjoin에 대해 wrongcallid/slot,coefficient-origin,잘못된unitslabel,nonfinite,domain,foreignphase,shape를구별한다. 실제api는적법한signedincoming을허용해야한다. C8에서미리정한첫/중간/마지막nativepoint를사용해incomingzero/perturbation의응답을측정한다. Exportedmatrix의B/C교환·band교환·X변경을independentresidualvalidator에넣어잘못된식이구별되는지확인한다. 재계산이필요없는mutation은savedoutputs에대해서만수행한다.

그림은132점FH/sourceparity및normalizedresidual을실제rawdata로작성한다. Root가생성그림을직접읽고수치요약과대조한다. Plot은검증값을설명하며과학수용기준을대체하지않는다.
