# REC-H5-BACKGROUND-JET01 — fresh non-author C9 코드·알고리즘 심사

검토일: 2026-10-28. 실제 native reviewer ID: `/root/fresh_c9_code`.
적용 규약: 사용자가 지정한 `physmath-research-loop` 내장 1.0.0, C9.

## 1. 판정

**원 BGJET의 고정 소스 배경 interval packet은 `PASS_SCOPED`로 채택 가능하다. 저장 끝점 보충 packet도 원 packet과 연결하여 사용하는 범위에서 `PASS_SCOPED`로 채택 가능하다.** 이번 읽기에서 고정된 두 산출물의 포함 명제를 깨는 blocking 수식·구간 산술 오류를 발견하지 않았다. 아래 네 지적은 현재 hash로 고정된 증거를 무효화하지 않으며, 검증기를 다른 입력에 재사용할 때의 실패 처리·완전성·인계 계약을 명확하게 한다.

| 대상 | C9 판정과 실제 수용 범위 |
|---|---|
| 원 `background_jet.py` 및 원 packet | 지정된 October2012 non-CAMB, flat, constant-Lambda, 질량 없는 neutrino 배경의 represented-input exact-real 함수. 313 query 행에 연결된 89개 고유 좌표 구간에서 14개 배경 field의 point/whole-cell 포함 근거를 채택한다. |
| `audit_saved.py`와 끝점 보충 packet | 원 packet의 포함된 끝점 구간, 양의 혼합 정리, 정확한 유리수 교집합에 의존하는 세 field 보충 자료. `H_etaeta`와 `H_etaeta_over_H`의 더 좁은 whole-cell 구간을 채택한다. `H_eta` 폭은 동일하다. |
| native C 비교 | 저장된 940개의 동일 represented-z 비교와 고정 `512*2^-52` 기준의 통과 기록을 재사용한다. C 실행 전체의 반올림을 감싼 interval 증명으로 승격하지 않는다. |
| physical certificate | 기존 `0/313`, 모든 지정 physical 값 null, H6/H7 OPEN, L4 false, REI activation false를 유지한다. |
| 독립성 | 원본/보충 코드의 작성에 참여하지 않은 별도 native agent가 원자료를 읽고 식·알고리즘을 검토했다. 새 reviewer 입장은 실제로 수행했다. 서로 다른 모델의 실행 여부는 확인 가능한 metadata가 없어 주장하지 않는다. |

과거 `NOT_RUN_FRESH_NONAUTHOR`는 당시 기록으로 보존한다. 이 C9 보고서는 그 기록을 수정하지 않고 새로운 비작성자 검토 근거를 추가한다. 이 리뷰만으로 R6, C10 또는 전체 20단계의 완료를 대신 판정하지 않는다. 중앙 canonical은 **28/88, delta 0**, REI **33/88은 별도 집계**, `AUTO_NEXT_NODE=OFF`다.

## 2. 원자료 identity와 검토 방법

읽은 원본은 `/workspace/scratch/6b0500b5ac99/review_work/source`이다. 공급 ZIP의 실제 크기는 2,247,738 bytes이며 SHA-256은 다음과 같다.

`2d4a37afb6690af8c44f48b94b84ffabce823a878a31ddd2cc3464c1ed7b072b`

`REVIEW_SOURCE_MANIFEST.json`의 77개 기록에 대해 실제 local bytes/해시를 대조해 77/77 일치를 확인했다. 전체 결과와 파일별 hash는 동반 `READ_ONLY_INSPECTION.json`에 있다. 다음은 결론의 주요 의존 파일이다.

| 파일 | SHA-256 |
|---|---|
| `inputs/C5/code/background_jet.py` | `52e2ef1a95854b0f3b0ba4a7df942c8500d85b39b8e14e60d998ac8598103168` |
| `inputs/R2/vendor/interval80.py` | `9e9e86df600c2886076403aa39f7bcd20a9da2c7bda0abf88bfd0738fbd82bec` |
| `inputs/R2/inputs/SOURCE_CONTEXT.json` | `5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8` |
| `inputs/C7/evidence/primary001/BACKGROUND_PACKET.json` | `ef76dad7e592f5a9e9b3b1d6357c724cbca2a0359e16ce3977d14723cfdb6220` |
| `inputs/C5/code/reference_check.py` | `1c96e870c114f416199b93955042de592c692301d9f78218112ae0e5551dce01` |
| `inputs/C8/evidence/oracle001/ORACLE140.jsonl` | `e4a67b8b47dfd79bb4530f7e4b9b85e04b236a235bffc2b75e5eced7626e27c7` |
| `audit_saved.py` | `6ae0dc9dd74b0aa08e600a13783eac11f6bd3e19377bd471a50bb3be1dd0dcfb` |
| `audit001/TIGHTENED_BACKGROUND_PACKET.json` | `0c2c360f0917e05baf580cea4be41695e301742be82992e95ecbd2a6e9af1d62` |

실제 방법은 다음 네 가지다.

1. `REPORT_KO.md`, `REVIEW_CONTRACT.json`, 원/보충 이론 문서, API 계약, 실행 영수증·요약·budget ledger를 먼저 읽어 주장과 실행 범위를 분리했다.
2. 원 C Hubble 함수와 Python 모델/interval 구현의 식–코드 대응, 지향 반올림 경로, source binding, native bridge를 줄 단위로 추적했다. 보충 알고리즘의 끝점 선택·교집합·직렬화·실패 처리도 정적으로 추적했다.
3. 양의 혼합의 moment 미분과 interval 포함의 합성 논증을 직접 재구성했다. 기존 CAS의 잔차 0이나 기존 controller의 리뷰 상태를 이 검토의 대체 근거로 쓰지 않았다.
4. JSON/text의 읽기 전용 구조 대조로 원 query와 packet 행의 동일성, supplement binding 동일성, oracle의 index/label coverage, native input/stdout/comparison의 hex 표현 대응을 확인했다. 이것은 producer·oracle·끝점 수치 계산을 다시 수행하는 작업이 아니다.

원 `produce.py`, `reference_check.py`, native executable, 원 tests, `audit_saved.py`를 import하거나 실행하지 않았다. 기존 saved verifier도 실행하지 않았다. **과학 재실행 0, 새로운 numerical scientific function 평가 0**이다. 실제 그림의 새로운 시각 검사는 이 코드 심사 범위에 포함하지 않았으며 보존된 figure finding/repair 기록을 읽었다.

## 3. source와 exact rational binding

`background_jet.py`의 `native_parameters`, `model_from_parameters`, `load_locked`, `bind_query`를 원 `history.c`와 대조했다. `input.dat`의 앞 아홉 scalar를 `float`로 읽은 뒤 `Fraction`으로 변환하는 것은 원 `%lg`의 binary64 매개변수 해석과 대응한다. `CG`, `CN`, `HN`도 원 decimal literal의 binary64 표현을 `Fraction.from_float`로 고정한다. 따라서 이번 함수의 계수는 원 literal을 무한정밀도 decimal로 읽은 값이 아니다. 원 C 내부의 곱셈·합산 반올림을 그대로 수행한 값과도 구별된다.

원 C의 `rec_get_cosmoparam`은 `fsR=meR=1`을 직접 할당한다. 끝에 있는 입력 두 줄을 무시하고 같은 값을 넣는 harness/Python 동작은 이 소스와 일치한다. `okh2=0`, `w0=-1`, `wa=0`, T0/context 동일성, 양의 scale, nonnegative mixture가 명시적으로 검증된다. 원 Hubble 비-CAMB 식에서 곡률 항은 0, 암흑에너지 지수는 0이 되어 `R=r*u^4+m*u^3+Lambda`로 환원된다. 이 환원에 필요한 조건을 코드가 숨기지 않는다.

`nH0`는 원 C의 계산식을 새 exact-real 곱으로 다시 만들지 않고 SOURCE_CONTEXT의 binary64 표현을 authority로 삼는다. 원 packet의 `density_representation`은 그 값과 원 literal/입력의 exact-real 곱의 차이를 별도로 저장한다. 해당 차이를 삭제하거나 새 물리 uncertainty로 바꾸지 않는다.

`bind_query`는 a,b,q를 원 hex의 exact binary64 rational로 복구하고 `a<b`, `a<=q<=b`, `alpha=(q-a)/(b-a)`를 유리수 등식으로 검사한다. alpha를 부동소수점 tolerance로 검증하지 않는다. 원 producer와 oracle은 `a,b,q,alpha` 전체의 연결을 저장·대조한다. 이번 구조 검사에서는 원 context 313행이 packet의 `source_query`와 같고, 보충 313행의 binding 및 incoming index도 원 packet과 그대로 같음을 확인했다. exact alpha 산술의 실행 성공은 고정된 원/보충 실행 기록에서 재사용한다.

관련 위치: `background_jet.py`의 `rational`, `model_from_parameters`, `bind_query`, `load_locked`; `produce.py`의 row 구성 및 density bridge; `history.c`의 non-CAMB Hubble 및 cosmoparam 함수.

## 4. Decimal80 포함 산술

`interval80.py`는 사칙연산의 결과를 전역 default context로 계산하지 않고 명시적인 DOWN/UP context에 전달한다. precision은 80이고 exponent 범위는 `Emin=-999999`, `Emax=999999`다. Fraction 입력은 분자·분모를 정확한 Decimal 정수로 만든 후 아래/위 방향 나눗셈으로 둘러싼다. 음수는 `copy_negate`와 끝점 교환을 사용하므로 default precision에 의한 추가 반올림을 피한다.

곱셈은 네 끝점 조합의 아래/위 반올림 최소·최대다. 나눗셈은 0을 포함하는 분모를 거부하고 단조 감소인 reciprocal의 `[1/hi,1/lo]` 외피를 만든 뒤 곱한다. 이 정의는 양의 분모뿐 아니라 음의 분모에서도 적절하다. 원 배경에서는 R의 양의 lower bound를 추가로 검사한다. 유한성·subnormal 검사와 InvalidOperation/DivisionByZero/Overflow/Underflow/Subnormal trap을 두고 실패를 숫자 결과로 숨기지 않는다.

exp와 sqrt는 입력 구간에서 단조 증가한다. 각 끝점의 nearest 결과를 동일한 80자리 context의 `next_minus` 또는 `next_plus`로 한 칸 넓힌다. nearest가 올바르게 반올림된다는 primitive 계약 아래 정확한 값은 이웃 두 표현수 사이에 있다. exp(0), sqrt(0), ln(1)의 정확한 항등식은 직접 처리한다. 이 알고리즘은 단순히 exp/sqrt의 context rounding을 FLOOR/CEILING으로 지정하면 함수가 그 방향을 따른다고 가정하지 않는다. 일반 비정수 `Decimal.power`도 사용하지 않는다.

Python 공식 3.13 문서에서 Decimal의 정확한 생성, exp의 HALF_EVEN 반올림, 이웃 표현수 의미를 확인했고, General Decimal Arithmetic의 square-root 규정에서도 HALF_EVEN을 확인했다. 이는 primitive의 명세를 확인한 것이며 CPython/libmpdec를 새로 형식 검증한 것은 아니다. 본 고정 packet의 의미는 명시된 primitive trust boundary를 포함한다.

공식 근거: [Python 3.13 Decimal 문서](https://docs.python.org/3.13/library/decimal.html), [General Decimal Arithmetic v1.70: square-root](https://speleotrove.com/decimal/daops.html#refnumsqrt), 조회 2026-10-28.

## 5. 원 jet와 whole-cell 알고리즘

A=r*exp(-4η), B=m*exp(-3η), C=Lambda, R=A+B+C에서 직접 미분하면

- `g=H'/H=-(4A+3B)/(2R)`;
- `g'=(AB+16AC+9BC)/(2R^2)`;
- `q=H''/H=g'+g^2`;
- `H'=H*g`, `H''=H*q`다.

계수들이 nonnegative이고 합이 양수이면 R>0이다. `g'`의 양의 분자 형식은 `R''R-(R')^2`를 직접 빼는 연산보다 안정적이고 같은 항등식이다. 코드 `jet_u`의 u²,u³,u⁴ 구성, Tr/nH의 scaling 및 그 두 차수 η 미분, `Gamma_bg_log_eta=-4-g`, 그 미분 `-g'`가 이 식과 일치한다. η가 무차원이므로 H의 η 미분 단위는 s^-1로 유지된다.

원 `whole_cell`은 먼저 a와 b를 각각 outward rational interval로 둘러싼 뒤 `[a.lo,b.hi]` 전체에서 포함함수를 평가한다. 이어 H,Tr,nH의 감소와 g의 증가를 사용해 그 네 range를 끝점 외피로 좁힌다. g', H'', q는 전체구간 양의 식으로 남겨 두므로 표본 최댓값을 supremum으로 바꾸는 단계가 없다. 이후 H와 g의 더 좁은 범위를 곱하는 과정도 interval 포함을 보존한다.

원 H'의 interval은 H>0, g<=0의 endpoint product이며 이번 저장 입력에서 이미 새 H' endpoint hull과 같다. 보충 보고서의 0/313 strict improvement와 폭 비율 1.0은 이 구조와 일치한다. 원 보수적 q/H'' 폭은 오류가 아니라 dependency overestimation이다.

## 6. 보충 끝점 정리와 구현

p_i=A_i/R, n_i=(4,3,0), μ=E[n], μ2=E[n²], v=μ2-μ²로 두면 `p_i'=p_i(μ-n_i)`, `μ'=-v`, `μ2'=μ μ2-E[n³]`다. 따라서

`q=μ2/2-μ²/4=v/2+μ²/4`,

`q'=μ μ2-E[n³]/2-μ³/2=-E[n(n-μ)^2]/2 <= 0`.

또 `H'''/H=g*q+q'<=0`이고 `H''=H*q>=0`이다. 그러므로 H'는 증가하고 H''와 q는 감소한다. 이 증명은 n>=0을 실제 부호 단계에서 사용한다. 순수 Lambda를 포함한 0계수 경우도 R>0인 한 식이 정칙하다. g'=v/2 자체의 단조성은 여기에서 도출되지 않으며 보충 코드도 그 단조성을 쓰지 않는다.

`audit_saved.bounds`의 선택은 이 정리와 일치한다. H'에는 `[left.lo,right.hi]`, H''와 q에는 `[right.lo,left.hi]`를 선택한 다음 기존 whole-cell interval과 교집합을 취한다. 원 outward endpoint의 exact 함수값 포함과 위 단조성으로 endpoint hull이 전체 범위를 포함한다. 기존 interval 역시 전체 범위를 포함하므로 교집합도 전체 범위를 포함한다. 따라서 이 계산은 원 끝점 포함 근거를 승계한다. 새 high precision point 성공을 증명의 전제로 쓸 필요가 없다.

저장된 finite decimal 문자열을 Fraction으로 읽고, 선택·max/min·너비·비율을 exact rational로 계산하므로 교집합 단계의 반올림 손실은 없다. 보충 값은 decimal 문자열 대신 `numerator/denominator` 문자열이다. 보충 schema는 `BGJET_SAVED_ENDPOINT_SUPPLEMENT_V1`이며 원 packet을 완전히 대체하는 schema가 아니다. 소비자는 Fraction-aware parser로 읽고 `source_packet_sha256`가 일치하는 원 packet과 결합해야 한다. 기존 `Decimal(string)` loader에 그대로 넣는 경로를 승인하지 않는다.

보존된 `audit001/SUMMARY.json`의 폭 개선은 H''에서 1.2597665054–1.2622930837배, q에서 4.4910459666–4.5028331776배이며 두 field 모두 313개 query 행에서 strict하다. 이 숫자는 이번 리뷰에서 다시 산출하지 않았다. 원 전체구간 외피와 새 endpoint 교집합의 알고리즘 및 저장된 실행 identity를 검토하여 재사용한다.

## 7. 기준식·검증의 독립성과 실제 검사량

원 `reference_check.py`는 production 또는 interval80을 import하지 않는다. input.dat와 context에서 계수를 새로 구성하고, mpmath 140자리의 scalar H를 `mp.diff`하여 H',H'',logH의 두 미분을 만든다. 원 kernel의 양의 분자 알고리즘을 그대로 호출하지 않는 유용한 구현 독립성이다. 다만 입력 상수 해석과 물리적 배경 선택은 공통이므로 그것을 별도 모델 검토로 셀 수 없다. 140자리 float 결과는 rigorous interval oracle가 아니며 문서도 이를 point corroboration으로 한정한다.

보충 `reference`는 180자리 positive-mixture moment 식으로 세 값을 계산한다. 원 analytic derivative kernel과 표현을 달리하지만 같은 frozen model을 사용한다. 원 endpoint enclosure의 검증을 새로 독립 구현한 것은 아니다. monotonicity의 313회 부호 검사는 저장 q 위치에서 수행한 수치 sanity check이고 전체구간 단조성은 위 증명에서 나온다.

이번 구조 검사로 원 oracle 파일은 1,565행이며 각 313 query에 대해 L,Q,R,quarter,threequarter가 정확히 한 번씩 존재함을 확인했다. 원 summary의 **35,056은 point 수가 아니라 containment 판정 수**다. whole-cell 검사 `313*5*14=21,910`과 point interval 검사 `313*3*14=13,146`의 합이다. 원 보고서의 “35056-point evidence”는 이 의미로 읽어야 한다. 같은 좌표 구간을 공유하는 query가 있으므로 313행을 313개 고유 cell로 확대하지 않는다.

기존 보충 10,681개의 검사는 identity 12, shape 2, model 7, physical ceiling 10, binding 1,878, monotonicity 313, exact subset 939, fresh180 containment 939, positive width 939, saved oracle containment 4,695, saved native tolerance 940, pure limit 3, refusal 4로 나뉜다. 이 수치를 새로운 독립 검사의 개수로 합산하지 않았다. 새 리뷰의 실제 read-only 검사량은 별도 receipt에 기록했다.

native harness는 원 history.c를 include하여 H만 호출한다. 원 build 기록은 `-UCAMB`, `-ffp-contract=off`, 일반 binary64 경로를 사용하고 Hubble 호출 수는 940이다. producer는 geometry에서 선택한 z의 hex를 저장하고 동일 represented z의 exact-real H와 C H를 비교한다. geometry H(η)와 H(1+z_eval)의 signed bridge를 따로 저장한다. 이번 읽기에서 native input/stdout/comparison 각 940행의 z/H hex 대응을 확인했다. 원 summary의 최대 상대 endpoint 거리 약 1.96032e-16과 geometry-z bridge 약 1.68618e-16은 각각의 기존 기록으로 유지한다.

## 8. negative controls와 보존된 실패

원 tests의 18개 case에는 순수 matter/radiation/Lambda, 정확한 혼합점 variance, Tr/nH scaling, whole-cell 부호, source locks, curvature/dark-energy/T0 mismatch, 음수 또는 전부 0인 coefficient, 뒤집힌/같은 clock, query 밖 좌표, alpha mismatch, saved nH0 authority, physical nulls, nonfinite η, nonpositive u가 포함된다. 예전 controls 실행의 exit 0은 budget ledger에 보존되어 있다. 이 capsule은 controls stdout 전체를 포함하지 않으므로 여기에서 새로 18개 실행 성공을 관측했다고 쓰지 않는다.

보충 pure-limit 3개는 moment 항등식의 exact manufactured check다. supplement `bounds` 함수의 전체 test가 아니다. refusal 4개는 audit 자체의 `validate_model`에 rad<0, matter<0, hN=0, T0=0을 공급하는 검사이며 원 production refusal tests의 대체가 아니다. 이 구분을 유지하면 음성 대조의 실제 효력을 정확하게 기술할 수 있다.

보존된 RED는 kernel 미구현 시점에 `bg is None`으로 실패한 기록이다. 이를 현재 구현의 과학 실패로 해석하거나 성공 로그로 바꾸지 않는다. 원 figure의 gap fill-between 문제와 저장 자료를 이용한 단 한 번의 plot repair도 그대로 보존된다.

## 9. Findings — 대상, 근거, 영향, 최소 교정

### C9-F1 — 일반 재사용 시 evidence coverage를 PASS 조건에 강제하지 않음

**등급:** medium, 고정 snapshot에는 비차단. **대상:** `reference_check.py`의 `zip(ctx['queries'],p['rows'])` loop와 마지막 PASS 선택, `audit_saved.py`의 saved oracle/native loop.

**근거:** 원 oracle는 loop 전에 두 길이를 명시적으로 검사하지 않아 짧은 packet에서는 짧은 prefix만 검사하고 failures가 없으면 PASS를 만들 수 있다. 현재 원 saved verifier가 313행과 oracle bindings=313을 별도로 요구하므로 고정 패키지 전체에서는 이 결손이 보완된다. 보충 audit의 saved oracle loop는 index를 찾고 수치를 검사하지만 예상 1,565개의 `(incoming_index,label)` 집합, eta binding, oracle hash/summary를 자체 검사하지 않는다. native loop도 길이 940과 tolerance는 검사하지만 index/label/z의 기대 집합과 raw stdout 대응을 자체 강제하지 않는다.

**영향:** 변경된/잘린 입력에 검증기를 단독 재사용하면 point evidence가 누락되거나 중복되어도 PASS가 나올 수 있다. 현재 snapshot에서는 이번 독립 read-only coverage 및 raw hex 대조와 77개 manifest hash가 맞으며 이 실패 조건이 관측되지 않았다. endpoint 포함 정리 자체는 sample coverage를 전제로 하지 않는다.

**최소 교정:** 다음 verifier revision에서 loop 전에 정확한 shape/expected index-label 집합과 eta binding을 검사하고, oracle/네이티브 원본 파일의 hash 또는 raw 대응을 명시적으로 검증한다. 전부 다시 계산할 필요 없이 저장 자료 검증만 강화하면 된다. 이번 task는 원본 변경 금지이므로 수정은 하지 않았다.

### C9-F2 — FAIL을 결정하기 전에 supplement 파일을 발행함

**등급:** medium, 고정 PASS 실행에는 비차단. **대상:** `audit_saved.py`의 `check`, output 작성, 마지막 `if failures`.

**근거:** identity/shape/physical check는 실패를 배열에 누적한다. 루프가 계속 진행할 수 있으면 `TIGHTENED_BACKGROUND_PACKET.json`을 쓴 후 SUMMARY=FAIL을 쓰고 exit 2를 낸다. sidecar에는 자신의 acceptance status가 없다.

**영향:** 미래 실행의 소비자가 supplement 파일 존재만 성공으로 읽으면 identity가 다른 입력의 후보를 잘못 채택할 수 있다. 이번 실제 summary는 PASS, failures=[]이고 source/supplement/code hash 및 exit 0이 결속되므로 현재 결과의 무효 근거는 없다.

**최소 교정:** identity/model/shape 실패는 계산 전 종료하고, 실패 자료는 별도 diagnostic/candidate 이름으로 보존하며, accepted supplement는 모든 검사 통과 후 발행한다. 현재 소비 절차는 source hash+supplement hash+SUMMARY PASS+receipt exit 0을 함께 요구하도록 이 리뷰에서 수용 범위를 고정한다.

### C9-F3 — 보충 packet에 H6/H7 OPEN의 명시적 전달이 빠져 있음

**등급:** low, 연결된 sidecar 사용에는 비차단. **대상:** `audit_saved.py`의 physical ceiling 검사와 `tightened` schema; 실제 supplementary JSON.

**근거:** 원 packet에는 H6/H7가 모두 OPEN이나 보충 schema는 두 키를 생성하지 않고, audit의 physical ceiling check도 두 값을 확인하지 않는다. 아홉 physical null, physical coverage, L4, REI flag는 보충 파일에 있다.

**영향:** supplement만 읽는 소비자는 사용자 고정 OPEN 상태를 해당 파일에서 직접 확인할 수 없다. source packet hash가 연결되어 있어 현재 조합에서는 OPEN이 정확히 유지되며 null/false를 새로운 물리 성과로 바꾸는 동작은 없다.

**최소 교정:** 다음 schema revision에 `H6:'OPEN', H7:'OPEN'`과 엄격한 bool 검사를 추가하거나, sidecar가 원 packet의 상태를 상속한다는 소비 계약을 명시한다. 이번 리뷰는 후자의 조합 수용 규칙을 명확하게 남기고 원 bytes를 보존한다.

### C9-F4 — 새 15 CPU / 30 wall / 512 MiB 한도 실행의 wrapper가 capsule에 없음

**등급:** low, 보존된 과학 결과에는 비차단. **대상:** `AUDIT_RUN_RECEIPT.json`, `REPORT_KO.md`의 재현 안내, `audit_saved.py`, 원 `run_bounded.py`.

**근거:** 새 receipt는 `python audit_saved.py`와 limits/측정값을 기록한다. audit 본문에는 limit 설정이 없고 `resource` import도 한도를 적용하지 않는다. capsule의 원 runner는 AS 1 GiB/wall 120초의 다른 고정 한도를 사용한다. 새 cap을 실제 설정한 외부 wrapper의 코드/완전한 명령이 이 capsule에는 없다.

**영향:** 이 capsule만으로는 새 limit enforcement 과정을 독립적으로 재현하거나 확인할 수 없다. 저장된 child CPU/wall/RSS 기록은 그대로 재사용할 수 있으며 이는 함수값/interval의 수학적 오류를 뜻하지 않는다.

**최소 교정:** 이미 실행한 외부 wrapper/명령과 interpreter·dependency identity를 새 provenance 부록으로 연결한다. 원 계산 재실행이나 예산 reset은 필요 없다. 이번 receipt는 cap enforcement를 새로 관측한 것으로 쓰지 않고 역사적 실행 receipt가 기록한 값으로 구분한다.

## 10. 과학·실행·보존 축과 인계

**과학 축:** 원 frozen background의 식–코드 및 interval 포함 논증, supplementary monotone endpoint 논증을 비작성자 C9로 검토 완료했다. 기존 oracle/native 성공은 hash가 고정된 numerical corroboration으로 재사용한다. 아홉 physical 출력은 null이고 background reference 313/313과 physical coverage 0/313을 분리한다. full-state K, physical M2, defect, stability L, positive uniform tube, e0, epsilon, outgoing은 생성되지 않았다. Gamma의 실제 total xe'를 공급하지 않으므로 기존 thermal coupling의 그 입력 의무도 그대로다.

**실행 축:** 이번 리뷰의 source inspection과 구조 대조는 완료했고 새로운 과학 실행은 없다. 원 budget ledger의 measured child CPU 15.403986초, 보충 receipt의 1.927305초를 서로 다른 실행의 역사적 값으로 보존한다. 새로운 15초 배분으로 원 예산을 재설정하거나 전입하지 않았다. 이번 동반 read-only inspection의 직접 측정 CPU 0.063371024초는 그 metadata 검사 하나에만 해당한다. 그 외 리뷰·상위 process·remote·모델 비용은 `UNKNOWN_NOT_ZERO`다.

**보존 축:** local ZIP과 77개 manifest payload의 byte/hash 일치를 확인했다. 원 scientific source, packet, summary, receipt, 실패 로그를 수정하지 않았다. 새 보고서/receipt는 `fresh_c9`에만 만들었다. 이 subagent는 Git/provider를 변경하지 않았고 새로운 원격 ACK를 관측했다고 주장하지 않는다. 저장·최종 전달은 상위 작업의 별도 확인 대상이다.

수용 시 원 packet hash, supplementary hash, 기존 PASS summary와 exit 0 receipt, 이 fresh C9 기록을 함께 연결하면 된다. 새로운 science replay나 다음 node 실행은 이 검토의 후속 요구가 아니다. 네 finding은 변경된 입력/검증기 배포를 준비할 때 처리할 구체적 계약 보완으로 남기며, 고정 snapshot의 scoped 채택을 막지 않는다.
