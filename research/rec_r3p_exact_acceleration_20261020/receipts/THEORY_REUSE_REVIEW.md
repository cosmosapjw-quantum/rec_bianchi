# REC R3P 이론·재사용 검토 — 원래 재귀를 보존하는 감사 가속

작성 기준: 2026-10-20 UTC. 외부 문헌·기호 계산 확인 시각 03:56 UTC. REC 기준 소스는 `368d87ad5de90dde74226ed109c3ba29d9607c84`이며, 아래 소스 판독은 작업 중인 파일 대신 이 커밋의 `git show` 결과를 사용했다.

후속 갱신: 같은 대화에서 부모가 전달한 정확 CPU 분수·Wolfram 결과/경고·PR110 Stage0·저장 stream 복구·Rayon staging 상태를 §6, §10.1, §11.1에 반영했다. 부모의 실행 보고와 이 하위 작업에서 직접 검산한 내용을 구분한다. 새 adapter의 독립 C9는 대기 상태다.

**판정: 기록별 순수 계산, 조건을 명시한 최대값 집계, 확정된 과거 이력의 읽기는 분할할 수 있다. 시간 적분의 독립성은 도출되지 않는다. R6는 아래 유도와 반례에 대한 검토이며, 부모가 작성할 후보 구현의 검토·승인·성능 측정은 `NOT_RUN`이다.**

## 1. R1–R2: 계약과 증거 범위

원래 HyRec October 2012 소스, 유효 간격 `h=4.245e-5`, 원래 atomic/thermal 연산자, H/T predictor memory 두 쌍, 단계 guard, `REI=false`를 유지한다. 기존 U5 h `HOLD_9_FAIL`, h2 `HOLD_8_FAIL`, 비용 `CLOSED_HOLD_NOT_RESET`을 승격하거나 재설정하지 않는다. 여기서 h2라는 기존 receipt 명칭도 같은 유효 간격을 가리킨다. 일반 수렴성, 전체 역사 검증, REC 가속률은 이 보고서로 성립하지 않는다.

적용한 정책은 요청 경로의 `physmath-research-loop/SKILL.md`, `RESEARCH_POLICY.md`, `THEORY_LOOP.md`, `CODING_LOOP.md`, `EVIDENCE_AND_HANDOFF.md`, `RUNTIME_AND_LEGACY.md`이다. 이번 범위는 이론·재사용·R6 수학 검토 및 handoff다. 저장소 수정, 후보 구현, 빌드, 테스트 실행, 적분 및 벤치마크는 하지 않았다. Exa 원문 검색, SciSpace 서지 검색, 공식 문서 판독, 고정 소스 판독을 실제 `Promise.allSettled` 동시 호출로 수행했다. 에이전트와 재귀 에이전트는 사용하지 않았다. NumPy/Numba/Rayon 문서 조사는 부모 작업과 중복하지 않았다.

부모의 [프로파일 intake][profile]를 재사용했다. 해당 문서 SHA256은 `a6db3d021fa5a51e351e82faa61c4c3d03dae3d15e809851d30c0b83de433da7`이다. 실행 커밋은 문서 HEAD와 다른 `d0e534b1f5b4bb20fe19875f6d502681b833470d`이다.

| 기존 측정: exclusive process-tree CPU | CPU 초 | 비중 |
|---|---:|---:|
| native-stream comparator | 21.409138 | 56.96% |
| owned integration | 5.837440 | 15.53% |
| common-input oracle | 3.661671 | 9.74% |
| 나머지 | — | 약 17.77% |

분모는 37.588099 CPU s, 별도 wall time은 42.119583 s다. inclusive integration 28.19%를 위 exclusive 항목에 더하면 중복이다. 이 수치는 새 측정이 아니다. 이미 완료된 U6 5,210단계와 저장된 원시 입력을 재사용한다. [프로파일 원자료][profile-raw]

### 고정 소스와 읽은 경계

| 파일·API | 이 보고서에서 확인한 역할 | SHA256 |
|---|---|---|
| [verify_r3i_h2_u6_rt_boundary.py][rec-audit] / `compare_native_stream` | 순서 검사, 원래 spectral gate, maxima, 원래 평균 실패/진단 기록 | `8f30859e99136a5a916ca046bf553c24943d798ef67e783cc295fb4ef9327b50` |
| [owned_flrw_history.py][rec-history] / `OwnedFLRWHistory.incoming`, `append` | q=0의 313개 과거 이력 보간, 승인 열의 단일 소유권 | `3e90e1bf3b9d8158197409b54ad429f3eecfe6643d5725cf5e0865e56cf8aab5` |
| [full_2012_atomic_source.py][rec-atomic] / `_original_escape_factors` | scalar libm, 취소를 포함한 원래 분기·산술 순서 | `1af383a2c596220561ef1c3be6a1bb755a68ee49f2428ed78cbbaf82c5f59578` |
| [primordial_2012_refined_start.py][rec-clock] / `HyRec2012Cosmology.redshift` | scalar `math.exp`로 원래 격자 계산 | `bd72cd1c35718d11a13aee0905babe0c74af4d941545e5245562fcb3a5630e77` |
| [verify_r3i_h2_u5_thermal.py][rec-ctypes] / `CombinedOracle` | 현재 Python 경계는 `ctypes.CDLL` | `0681b98a86f54719480fe0d1a8aca882c20b50d41d349f3d24676b1e5ef6a559` |
| [original_hyrec_r3i_h2_u6_rt_boundary_harness.c][rec-c] | `static rate_table`, `twog`, `loaded`, 지연 초기화 | `434c49364a3b0acb59f9d5fde64757fa4dcb019d3e7ff80bddd4295b3531c729` |
| [Rust ffi.rs][rec-ffi] | 원래 C 전역 상태를 보호하는 process-local `C_LOCK` | `4b561962b23f90cacaee11ba92180b3adefbe630e672a8a1c53febfbf0a0c501` |

## 2. R3–R5: 무엇을 독립 작업으로 분할할 수 있는가

### 2.1 재귀와 감사 함수의 구분

원래 적분은 상태·이력·단계 사건을 합친 상태 \(X_n\)에 대해

\[
Y_{n+1}=Y_n+h\,[1.25F_n-0.25F_{n-2}],\qquad
F_n=F(Y_n,H_{<n},\text{stage}_n;\theta)
\]

형태다. 원래 프로그램의 곱셈·뺄셈·덧셈 순서도 계약의 일부다. \(F_n\), 네 predictor memory, 원자 방출 열, thermal/stage guard가 다음 단계의 입력이다. 따라서 일반적인 서로 다른 시간 단계 \(n,n+1\)를 독립 작업으로 취급할 수 없다. U6에서는 input 53179부터 58389 직전까지의 원래 경계도 보존한다. [기존 owned 적분][rec-owned]

반면 이미 확정된 기록 \(R_i\), Python/C의 별도 이력, 고정 문맥 \(\theta\)가 주어지면 감사 map은

\[
E_i=G(R_i,\{H_j:j\in D_i\},\theta)
\]

로 쓸 수 있다. 다음 조건이면 임의의 **서로 겹치지 않는 target index 분할** \(I=\bigsqcup_q I_q\)이 같은 \(E_i\)를 낸다.

1. 읽는 모든 값·상수·배열 view가 작업 동안 불변이고, \(D_i\)의 모든 항목이 확정되어 있다.
2. 각 target의 쓰기는 서로 다른 슬롯에만 일어나며, shared cache의 게시도 완성된 값에 대해서만 이루어진다.
3. 원래와 같은 binary64 피연산자, 연산 순서, libm 구현, rounding/FTZ/DAZ/FMA 조건을 사용한다.
4. worker의 출력은 값과 원래 전역 ordinal을 가진 결과/오류 기록이다. 전역 예외·로그·단계 상태 변경은 원래 순서를 아는 coordinator가 수행한다.

**증명.** 각 \(i\)의 유한한 연산 그래프를 위상 순서로 보자. 입력 비트가 같고 각 연산의 의미가 같으므로 첫 연산의 출력 비트가 같다. 같은 귀납을 마지막 연산까지 적용하면 \(E_i\)가 같다. 서로 다른 target의 실행 순서는 이 입력 집합을 바꾸지 않는다. 아래 집계 정리를 더하면 최종 요약도 같다. 이 증명은 읽은 이력이 먼저 계산되어 있다는 전제이지, 그 이력을 만드는 적분 단계의 교환 가능성에 대한 증명이 아니다.

### 2.2 원래 spectral 식

기존 `V/A/L` 감사는 각 값 \(p_i\)(Python), \(c_i\)(C), 에너지 \(E_b\)에 대해 다음 순서로 계산한다.

\[
T_i=(k_B T_0)(1+z_i),\quad
B_i=1/\operatorname{expm1}_{\rm scalar}(E_b/T_i),
\]
\[
D_i=10^{-7}\max(|p_i|,|c_i|)+10^{-10}B_i,\quad
e_i=|p_i-c_i|/D_i.
\]

실제 코드는 `math.expm1(float(energy)/tr)`이다. `V/A/L`은 finite 값과 finite ratio를 검사하고 `ratio > 1`에서 원래 실패 경로로 간다. prefix `PV/PL`은 별도로 `abs(py-value) > tol`을 사용한다. 이 두 callable의 검사식과 검사 위치를 그대로 대응시켜야 한다. 여기서 전제하는 성공 입력 영역은 유한한 피연산자와 양의 유한 tolerance를 가진다. 이 영역 밖의 정책을 새로 강화한다면, 이는 해당 입력에 대한 동작 변경으로 따로 기록해야 한다. [원래 감사 소스][rec-audit]

`maxima`는 xe, Tm, H RHS, T RHS, V, A, L의 **서로 다른 metric** 7개다. 하나의 공통 정규화식으로 모두 바꾸면 안 된다. 상태 비교와 RHS 비교의 floor·denominator·threshold는 기존 helper의 정의를 그대로 따라야 한다.

### 2.3 finite maximum의 분할 정리와 경계 조건

원래 방식으로 계산된 유한한 비음수 \(e_i\)에 대해

\[
M_k=\max\bigl(0,\{e_i:\operatorname{metric}(i)=k\}\bigr)
=\max_q\max\bigl(0,\{e_i:i\in I_q,\operatorname{metric}(i)=k\}\bigr).
\]

최대값 연산은 입력 중 하나를 선택하며 새 덧셈을 하지 않는다. 따라서 NaN과 zero 동률의 의미를 먼저 고정한 이 영역에서는 tree 형태를 바꿔도 선택된 수치값이 같다. `abs`와 양의 denominator가 만드는 zero는 +0이며, 기존 초기 accumulator도 +0이다. 이 사실을 사용하는 것과 임의 float 배열에 대해 `max`가 항상 비트 결합적이라고 주장하는 것은 다르다.

동률의 위치까지 출력할 경우에는 `(value, original_ordinal)`에서 큰 value, 같은 value이면 작은 ordinal을 선택한다. 이는 전순서에서의 선택 연산이므로 결합적이다. 원래 accumulator의 +0/빈 결과 의미를 가상 초기 원소로 포함해야 한다. 원래 결과에 없는 argmax 필드를 새로 직렬화할 필요는 없다. count는 검증된 상한 내의 정수 덧셈으로 집계하고 누락·중복 target을 별도로 검사한다.

**R6 반례: NaN, signed zero, sum.** 이번에 저장소와 무관한 작은 binary64 산술로 다음을 확인했다.

\[
\max(\max(1,\mathrm{NaN}),2)=2,\qquad
\max(1,\max(\mathrm{NaN},2))=1
\]

는 Python의 첫 원소를 유지하는 `max` 의미에서 성립한다. `max(-0,+0)`와 `max(+0,-0)`의 비트는 각각 `8000000000000000`, `0000000000000000`이다. Rust `f64::max`는 한쪽 NaN을 무시하고 같은 값의 ±0 선택도 임의일 수 있다고 공식 문서가 명시한다. 따라서 API 이름이 같다는 이유로 교체하지 않는다. [Rust f64 문서][rust-f64]

또한 \(a=2^{53},b=1,c=-2^{53}\)에 대해 binary64 `(a+b)+c=0`, `a+(b+c)=1`이다. 원래 합, norm, WRMS, compensated dot을 임의 tree로 바꾸는 것은 위 max 정리의 적용 대상이 아니다. 재현 가능한 새로운 합 알고리즘도 원래 순차 합과의 동일성을 자동으로 주지 않는다. [재현 가능한 합의 원 논문][sum-paper]

### 2.4 상태 기계와 실패 이력은 순서까지 보존

기록의 수학적 map이 독립이어도 원래 stream은 `PARAM → HE → NODE → THERMAL_EVENT → prefix → BASE → STEP/spectrum → END`의 상태 기계다. prefix는 열당 311 PV+3 PL, accepted step은 V311+A311+L3=625개다. fixed-width 구조를 쓰려면 tag, step, column, bin, 전체 개수까지 이 순서와 일치해야 한다. 단순히 숫자 625개를 읽었다고 의미가 확정되지 않는다. [원래 감사 소스][rec-audit]

텍스트를 Rust에서 새로 해석한다면 decimal token에서 binary64로의 변환도 입력 동일성의 일부다. 정상 원시 stream의 부호·지수·경계 값이 Python `float`와 같은 비트가 되는지 별도로 대조해야 한다. parser의 허용 문법과 잘못된 행의 오류 우선순위도 숫자 kernel의 증명만으로 보장되지 않는다.

원래 A 실패는 즉시 전체 실패와 같지 않다. 먼저 raw failure를 flush하고, 분리된 Python/C owner의 과거 이력으로 forensic 검사를 하며, 원래 gate FAIL과 decimal80/IEEE 보조 gate PASS를 모두 기록한다. 원래 실패 자체는 남는다. 최대 64개를 허용하는 해당 진단 경로에서 **65번째 A 실패는 진단 append 전에 중단**한다. V/L 실패, 앞선 malformed record, 이후 END 누락과의 상대 순서도 유지해야 한다.

worker는 뒤쪽 결과를 미리 계산할 수 있지만, 앞선 ordinal이 해결되기 전에 뒤쪽 예외·forensic 호출·출력 파일을 공개해서는 안 된다. bounded 결과를 원래 순서로 commit하면 기존 처음 실패와 진단 prefix를 재현할 수 있다. 전체 파일을 먼저 파싱하다 뒤쪽 parse 오류를 먼저 던지는 방식도 앞선 parity 실패를 가릴 수 있다. 실패 위치 비교에는 `(line, 원래 검사 순번)`이 필요하다.

4,096줄마다의 guard 위치, create-only 출력, raw/diagnostic flush 의미를 유지한다. 다만 CPU 제한 발동 위치는 실행 속도와 스케줄에 의존하므로 가속 전후 동일 줄에서 timeout할 것을 요구할 수 없다. 요구할 것은 같은 제한과 점검 정책, 유한한 speculative 작업 상한, 실패 시 남는 증거다. live process worker의 CPU가 아직 `RUSAGE_CHILDREN`에 합산되지 않은 구간까지 비용 장부가 포괄해야 한다.

## 3. 정확 캐시의 조건과 구체적 절감 가능한 작업

순수 함수 \(v=F(d_1,\ldots,d_m;\gamma)\)의 캐시가 정확하려면 key equality가 **모든 의미적 입력과 연산 문맥의 equality를 함의**해야 한다. \(\gamma\)에는 코드/libm/build, shape·dtype·배열 해석, 단계/owner epoch, floating-point 환경이 포함된다. 문맥이 캐시 객체의 수명 동안 고정이면 매 key에 반복 저장할 필요는 없지만, 그 바인딩을 명시해야 한다.

float는 값 비교가 아니라 필요한 경우 `to_bits`로 구별한다. 특히 +0과 -0은 `==`로 같지만 함수 결과나 분기에는 차이가 날 수 있다. NaN/비정상 입력과 실패한 결과를 성공 entry로 재사용하지 않는다. hash만의 일치는 수학적 동일성 증명이 아니다. 정확 비교가 필요하면 후보 검색용 hash 뒤 실제 bits를 비교하거나, 불변 객체의 확정된 소유권·세대를 사용한다. `errno`, floating-point exception flags, callback 횟수도 관찰되는 계약이면 생략되는 부작용까지 다뤄야 한다.

| 재사용 대상 | 충분한 바인딩·조건 | 보존해야 할 연산 |
|---|---|---|
| prefix 열의 z, T | 같은 cosmology, source grid/h, 열 index, scalar 함수 환경 | 원래 `(1+8000)*exp(-h*iz)-1`, 이어 `(kB*T0)*(1+z)` |
| 같은 step의 V/A Planck 값 | 같은 step 입력 z 비트, 같은 에너지 비트, 같은 scalar `expm1` | `float(E)/tr`, `math.expm1`, `1./…` 그대로 |
| 고정 source/target 에너지·행 인덱스 | 정확한 표, source-edge mapping, dtype 및 q=0 범위 | `_source_edges`, 현재 식으로 계산한 logratio 재사용 |
| gather된 광자 값 | 위 geometry + owner identity + 읽은 과거 셀의 bits/불변 세대 + j,z | geometry key만으로 값까지 재사용하지 않음 |
| 행렬 factorization | 행렬 모든 비트, shift, shape/대역폭, pivot 및 알고리즘 정책, 성공 여부 | 같은 LU·pivot·solve 산술을 사용할 때만 |

캐시를 만들며 식 자체를 재배열하지 않는다. 예를 들어 `E/tr`를 `E*(1/tr)`로, `c.redshift`를 인접 redshift의 곱셈 재귀로 바꾸는 것은 일반적으로 같은 binary64 함수가 아니다. prefix의 `c.redshift(RT_IZ+col)`와 spectrum의 `result.states[i]['z']`도 각각의 원래 입력을 사용한다. 수학적으로 같은 격자라는 이유로 두 경로를 섞지 않는다.

현재 기록 수에서 도출되는 **호출 개수의 정적 감소**는 다음과 같다. 측정한 속도 개선이 아니다. [기존 소스·프로파일][profile]

- prefix 16,733열: redshift 호출 5,254,162회를 열별 16,733회로 줄일 수 있다.
- accepted step 5,210개: V/A에서 같은 311개 Planck 값을 공유하면 step당 `expm1` 625회가 314회가 된다. 1,620,310회의 중복 호출이며, post-step 부분의 49.76%다.
- prefix까지 포함한 Planck 호출은 8,510,412회에서 6,890,102회로 감소한다. 전체 해당 호출의 약 19.0391%이며 전체 CPU 감소율은 알 수 없다.
- 한 단계의 고유 Planck 값 314개는 binary64 payload 2,512 bytes다. 전체 시간×주파수 캐시를 만들 필요 없이 원래 순서의 bounded 작업으로 재사용할 수 있다.

독립 Python/C oracle은 계속 분리한다. 동일 물리 입력을 공유할 수는 있지만 후보가 계산한 원자 결과·이력·factor를 기준 oracle의 답으로 되먹이면 독립 비교가 사라진다. forensic의 Python owner와 C owner도 별도 namespace와 이력을 가져야 한다.

## 4. 인과적 history gather의 정확한 분해

### 4.1 현재 q=0 코드의 실제 식

`OwnedFLRWHistory`는 생성 시

\[
\eta_0=-\log1p(z_{start}),\qquad
\ell_b=\log(E_{s,b}/E_{t,b})
\]

를 저장한다. 승인 열 수 j에서 실제 계산은

\[
\eta_f=-\log1p(z_f),\quad\eta_{e,b}=\eta_f-\ell_b,
\quad x_b=\max((\eta_{e,b}-\eta_0)/h,0)
\]

후 `nextafter(j-1,-inf)` 상한으로 x를 제한하고

\[
k_b=\min(\lfloor x_b\rfloor,j-2),\quad w_b=x_b-k_b,\quad
L_b=(1-w_b)H_{s_b,k_b}+w_bH_{s_b,k_b+1}
\]

를 계산한다. active는 \(\eta_{e,b}\ge\eta_0\)이며, active 셀은 반드시 \(\eta_{e,b}<\eta_0+h(j-1)\), \(k_b+1\le j-1\)를 만족해야 한다. 비활성 q=0 prehistory는 0이다. 코드에는 원래 등방 angular 산술을 보존하는 **`L_b*1. + L_b*0.`**도 남아 있다. [원래 gather][rec-history]

원래 코드는 clock 일치에 작은 허용오차를 두므로, `eta_f`를 `eta0+j*h`로 대체하거나 `x=j-logratio/h`로 단순화할 권리가 생기지 않는다. 뺄셈·나눗셈 rounding 차이가 정수 경계에서 k를 바꿀 수 있다. 마지막 물리 구간 `[j-2,j-1)`에서는 k만 j-2로 제한하고 w를 유지해야 한다. x 자체를 j-2로 자르면 w가 사라져 다른 이력을 읽는다.

### 4.2 분할 조건의 증명

각 b의 읽기 집합은 active이면 \(D_{j,b}=\{(owner,s_b,k_b),(owner,s_b,k_b+1)\}\)이다. 313개 출력 b를 서로 겹치지 않게 나누고, 해당 j의 snapshot이 완전히 확정되어 있다면 각 보간은 다른 b의 출력에 의존하지 않는다. 따라서 §2.1의 연산 그래프 귀납이 적용된다. Lyman/virtual의 source-row 치환도 `_source_edges` 그대로 고정한다.

비활성점의 반환값은 0이지만 현재 `np.where` 경로는 먼저 안전한 과거 주소의 보간을 계산한다. 따라서 비활성 mask가 있다고 잘못된 주소나 미할당 halo를 넘겨도 된다고 가정하지 않는다. 실제 읽기를 유지하는 구현은 그 안전 주소까지 갖춰야 하며, 읽기를 생략하는 구현은 수치 결과·검사·관찰 가능한 부작용의 동등성을 따로 확인해야 한다.

이와 달리 시간 청크 \([j_0,j_1)\)의 새 적분에는 \(Y_{j_0}\), 네 RHS memory, 단계 사건, 모든 필요한 과거 셀이 필요하며, 그 중 일부는 앞 청크가 계산해야 한다. 전체 snapshot을 미리 저장한 뒤 **감사**하는 경우에만 여러 j를 독립 처리할 수 있다. 적분하면서 하는 경우는 현재 승인 frontier 이내의 gather/read 작업만 가능하다.

보간이 두 점이라는 사실은 시간 청크에 한 열의 halo만 있으면 된다는 뜻이 아니다. 필요한 열은 emission delay만큼 멀리 떨어져 있다. 청크 q가 요구하는 것은 정확히 \(D_q=\bigcup_{j,b\in q}D_{j,b}\)이다. q=0·고정 표에서는 지연을 이용한 유한 과거 범위를 별도로 증명할 수 있지만, 그 폭은 1이 아니며 원래 rounding·active 처리를 포함해야 한다. 공유 immutable 역사 또는 정확한 gather index 집합이 그 의존성을 만족시킨다.

현재 `OwnedFLRWHistory`는 문서상 single-threaded 객체다. `readonly_views()`는 owner 쓰기를 동기화하지 않으며 `.base`를 통한 변경도 차단하는 보안 경계가 아니다. 병렬 읽기를 도입하려면 append와 snapshot 수명 사이의 동기화가 별도로 필요하다. 원래 `append`는 모든 311/311/3 후보를 검증한 뒤 열을 쓰고 마지막으로 j를 증가시키므로, 부분 열을 승인된 것으로 게시하지 않는 조건도 유지한다.

## 5. scalar libm, 벡터 exp 및 취소 오차

### 5.1 원래 atomic escape 식의 민감도

현재 소스는 \(\tau\le10^{-6}\)에서 원래 2항 식

\[
P=\tfrac12\tau-\tau^2/6,\qquad S=\tau-\tfrac12\tau^2
\]

를 쓰고, 그 위에서는 scalar `math.exp(-tau)`의 결과 z로

\[
P_\tau(z)=1-(1-z)/\tau,\qquad S(z)=1-z
\]

를 그대로 계산한다. `_original_escape_factors`는 이 취소를 의도적으로 유지하며 `accurate_escape_factors`를 별도 함수로 둔다. 해당 scalar-C-libm 대조 테스트가 소스에 있으나 이번에 실행하지 않았다. [연산 소스][rec-atomic], [기존 테스트 소스][rec-atomic-tests]

벡터 함수가 \(z+\delta z\)를 반환한다고 하자. 실수 후처리식에 대해서는 정확히

\[
\Delta P=\delta z/\tau,\qquad\Delta S=-\delta z.
\]

\(P(\tau)=\tau/2-\tau^2/6+O(\tau^3)\)이므로 작은 양의 τ에서

\[
\frac{|\Delta P|}{|P|}\simeq\frac{2|\delta z|}{\tau^2}.
\]

exp 분기의 \(\tau\gtrsim10^{-6}\)에서 z는 1보다 조금 작다. 이 부근의 한 ulp \(2^{-53}\approx1.11\times10^{-16}\) 차이를 가정하면, 위 민감도는 \(|\Delta P|\approx1.11\times10^{-10}\), 상대 변화 약 \(2.22\times10^{-4}\)를 준다. **이는 가정한 한 ulp 오차의 대수적 민감도 예시이며, 이번에 어느 벡터 구현에서 그 차이를 측정했다는 뜻이 아니다.** 정확히 threshold인 τ는 작은-τ 분기다.

실제 후처리도 rounding하므로 \(\widehat P(z)=P_\tau(z)+\rho_z\)라 두면

\[
|\widehat P(z+\delta z)-\widehat P(z)|
\le |\delta z|/\tau+|\rho_{z+\delta z}|+|\rho_z|.
\]

따라서 단순한 transcendental ulp 보증만으로 최종 원자 항의 bit parity나 gate를 보증할 수 없다. 취소는 피연산자에 이미 있는 오차를 노출한다는 Goldberg의 설명과 같은 구조다. [Goldberg 원문][goldberg]

### 5.2 Planck tolerance에 대한 별도 경계

stream comparator의 Planck 값은 이미 scalar `expm1`을 사용한다. 이를 `exp(x)-1`, Wien 근사 `exp(-x)`, 새 Rust `exp_m1`, 다른 벡터 함수로 바꾸는 것은 같은 함수 호출을 캐시하는 것과 다르다. `exp(x)-1`로 바꾸면 작은 x에서 exp의 상대오차가 \(e^x/(e^x-1)\sim1/x\)만큼 증폭될 수 있다.

`expm1`의 두 구현이 d와 d+δd를 주며 \(|\delta d|\le\eta_d<d\)라면 실수 reciprocal 차이는

\[
\left|\frac1{d+\delta d}-\frac1d\right|
\le\frac{\eta_d}{d(d-\eta_d)}.
\]

여기에 각 reciprocal의 실제 rounding 경계를 더해야 한다. 이 bound는 동등한 비트를 증명하지 않는다.

일반적인 gate \(e=N/D\), \(D>0\)에 대해 \(|\delta N|\le\eta_N\), \(|\delta D|\le\eta_D<D\)이면

\[
\frac{N+\delta N}{D+\delta D}-\frac ND
=\frac{D\delta N-N\delta D}{D(D+\delta D)},
\]
\[
|\widetilde e-e|\le\frac{\eta_N+e\eta_D}{D-\eta_D}.
\]

실제 마지막 나눗셈의 rounding 차이는 추가 항이다. \(N=|p-c|\)라면 입력 변화에 대한 \(\eta_N\le\eta_p+\eta_c\); denominator의 max는 유한 실수에서 1-Lipschitz이므로 \(\eta_D\le10^{-7}\max(\eta_p,\eta_c)+10^{-10}\eta_B\)에 각 연산의 rounding 항을 더할 수 있다. 저장된 p,c를 그대로 두고 Planck 함수만 바꾸는 감사에서는 \(\eta_p=\eta_c=0\)이다. 원자 연산을 바꾸어 적분까지 바꾼 경우에는 그 가정을 사용할 수 없다.

\(\max_i|\widetilde e_i-e_i|\le\varepsilon\)이면 최대값 변화도 ε 이하이고, threshold 1과의 거리가 ε보다 크면 pass/fail 분류는 유지된다. 그러나 이번 계약은 원래 출력·진단·산술을 보존하는 것이므로 **분류의 여유만으로 변경된 max bits를 승인하지 않는다.**

### 5.3 외부 문헌으로 허용되는 결론

SLEEF 원 논문은 대부분 함수의 1-ulp/3.5-ulp 버전과 bit-consistent 버전을 구별한다. bit consistency는 같은 연산열, FMA 사용 여부의 구분, contraction 제어, 대응하는 scalar/vector 구현에 기대고 있다. 이것은 SIMD의 정확 출력 구현이 원리적으로 가능함을 보여 준다. 임의 SLEEF/vector exp가 현재 시스템의 scalar libm과 같다는 증거는 아니다. [Shibata–Petrogalli 원문][sleef]

Rust `f64::exp` 문서도 정밀도가 플랫폼·Rust 버전 등에 따라 달라질 수 있다고 명시한다. 같은 이름의 scalar 함수로 옮겼다는 사실만으로도 bit parity는 성립하지 않는다. 재사용 가능한 원칙은 **현재 scalar 호출의 결과를 재사용하거나, 원래 스칼라 구현과 같은 함수임을 해당 입력 영역·실행 환경에서 별도로 입증하는 것**이다. 현재 후보에 대해서는 그런 검증을 하지 않았다. [Rust 공식 문서][rust-f64]

## 6. Amdahl 상한: 정확한 측정 분수로 2.3232702643884배

같은 작업량과 같은 시간 측정량을 놓고 comparator 비중을 실제 CPU 장부의 정확한 분수로 둔다. 부모가 전달한 값은 기존 측정 초 21.409138/37.588099와 일치하며, 이 하위 작업에서도 `Fraction`으로 검산했다.

\[
f=\frac{21409138}{37588099}=0.5695722467901343\ldots,
\qquad a=1-f=\frac{16178961}{37588099}.
\]

comparator 전체의 해당 비용이 s배 줄고 새 overhead가 원래 전체 비용의 o배라면

\[
S(s,o)=\frac1{a+f/s+o},\qquad
S(\infty,0)=\frac{37588099}{16178961}=2.323270264388424\ldots.
\]

이는 고정 작업량의 직렬 비용을 남기는 Amdahl 모형을 이 프로파일에 대입한 **조건부 산술 상한**이다. 물리 문헌이나 VigilODE 벤치마크에서 REC 속도를 추론한 결과가 아니다. [Amdahl 원 논문][amdahl]

초판의 `625/269≈2.323420074349442`는 사용자 최초 제시 비중 0.5696을 정확한 값처럼 둔 근사 계산이었다. 아래 판정에는 정확한 측정 분수를 사용한다. 두 값의 차이는 프로파일 비중 반올림에 따른 것이며 새 성능 측정의 차이가 아니다.

| comparator 전체 비용 감소 s | 전체 S(s,0) | 정확한 유리수 |
|---:|---:|---:|
| 1 | 1 | 1 |
| 2 | 1.39818316 | 37588099/26883530 |
| 4 | 1.74574662 | 75176198/43062491 |
| 8 | 1.99352390 | 150352396/75420413 |
| 16 | 2.14580294 | 300704792/140136257 |
| 32 | 2.23101298 | 601409584/269567945 |
| 무한대 | 2.32327026 | 37588099/16178961 |

전체 2배의 필요조건은

\[
f/s+o\le\frac{5230177}{75176198}=0.0695722467901343\ldots.
\]

o=0이면 \(s\ge42818276/5230177\simeq8.186773794\)이고, s=16이면 \(o\le10216139/300704792\simeq0.03397398137\)다. 일반 목표 \(S_\star\)는 \(1/S_\star-a-o>0\)인 경우에만

\[
s\ge\frac{f}{1/S_\star-a-o}
\]

로 달성 가능하다. 어떤 이득이라도 있으려면 \(o<f(1-1/s)\)여야 한다.

**CPU와 wall time의 구분이 필수다.** 실제 f는 exclusive process-tree CPU 비중이다. 컴파일·캐시로 comparator의 총 CPU 작업이 s배 줄면 CPU 모형에 적용할 수 있다. 같은 일을 p개 worker에 나누는 것만으로는 총 CPU가 1/p가 되지 않으며, 대개 관리 비용이 더해진다. `s=p`를 wall-time 예측에 넣으려면 별도로 wall의 직렬/병렬 비중, 겹침, I/O, 실제 worker utilization을 알아야 한다. 기존 42.119583 wall s와 37.588099 CPU s의 차이를 무시하지 않는다.

또한 전체 comparator 중 실제로 병렬화되는 비중을 g라 하면 가속 가능한 전체 비중은 최대 fg다. 파싱, 순서 검사, 직렬 forensic, merge는 남을 수 있다. 그 경우 상한은 \(1/(1-fg)\)로 더 낮다. g는 현재 별도 측정되지 않았다. integration 15.53%와 common oracle 9.74%는 comparator만 바꾸는 계산에서 계속 남는다. CPU cap 개선에는 worker 수 증가보다 실제 작업 감소가 직접 연결된다.

## 7. process/thread 전송 비용의 손익분기

### 7.1 단위와 일반식

N은 **독립 map 대상 record 수**, c는 기존 map 부분의 record당 시간으로 둔다. 변하지 않는 parser·적분 등의 비용은 \(T_{other}\)다. B개씩 나누면 \(L=\lceil N/B\rceil\)개 청크다. 실제 계산 부분의 유효 개선률 r은 컴파일 효과, p개 worker, 불균형, lock 및 메모리 병목을 포함하되 전송 overhead와 중복 계상하지 않는다.

직렬화한 보수적 비용 모형을

\[
T_{seq}=T_{other}+Nc,
\]
\[
T_{par}=T_{other}+Nc/r+A+\alpha L+N\tau+M+I+H
\]

로 둔다. A는 worker 시작·초기화·고정 장착 비용, α는 청크당 제출/취합 비용, τ는 record당 추가 packing·serialization·전송·해석 비용, M은 최종 집계, I는 불균형·마지막 청크 지연, H는 중복 halo/과거 이력 전송 비용이다. 모두 선택한 동일 시간 단위로 사용한다. 기존 경로에도 있는 비용은 추가 overhead로 다시 넣지 않는다.

이 모형에서 손익분기는 정확히

\[
\boxed{Nc(1-1/r)>A+\alpha\lceil N/B\rceil+N\tau+M+I+H.}
\]

r≤1이고 overhead가 음수가 아니면 이 분할만으로 개선되지 않는다. 이는 특정 비용 모형의 판정이지 모든 가능한 가속 방법에 대한 no-go가 아니다.

### 7.2 청크 크기와 최소 작업량

B가 N을 나누고 \(K=A+M+I+H\)가 선택한 범위에서 고정/상계 가능하면

\[
D_B=c(1-1/r)-\tau-\alpha/B,
\qquad D_B>0,\quad N>K/D_B
\]

가 손익분기다. 나누어떨어지지 않을 때는 \(\lceil N/B\rceil<N/B+1\)을 이용한 충분조건 \(N>(K+\alpha)/D_B\)를 쓸 수 있다. K나 r이 N,B에 따라 변하면 그 의존성을 유지한 원래 부등식을 사용한다.

특히

\[
c(1-1/r)\le\tau
\]

이면 청크당 overhead를 0으로 만들더라도 record당 전송만으로 이득이 소진된다. 이 경우 B 증가가 해결책은 아니다. 반대로 나머지 overhead를 포함한 record당 잔여 여유가 양수일 때만

\[
B>\frac{\alpha}{c(1-1/r)-\tau-K/N}
\]

같은 청크 하한을 검토할 수 있다. tail 때문에 이 식은 B|N인 단순 모형의 결과다. 숫자 c,τ,α,A는 측정하지 않았으므로 특정 worker 수나 청크 크기를 최적이라고 지정하지 않는다.

전송 payload가 record당 v bytes, 유효 bandwidth가 W라면 \(\tau\)의 한 부분은 v/W이며, serialize/deserialize·복사 CPU는 추가된다. Python Queue/Pipe는 객체를 직렬화한다. 공유 메모리는 이러한 복사를 줄일 수 있지만 immutable 보장이나 소유권·동기화를 자동으로 제공하지 않는다. [Python multiprocessing][multiprocessing], [SharedMemory][shared-memory]

### 7.3 겹침, 대역폭 및 저장 공간

feed와 계산이 겹치는 구현은 위 합산 모형보다 빠를 수 있다. A가 모든 작업에 앞선 공통 초기화 단계인 모형에서는 최소한

\[
T_{par}-T_{other}\ \ge\ A+\max\left(T_{feed},\frac{\sum_q W_q}{p},\max_q W_q\right)
\]

라는 하한을 확인한다. \(W_q\)는 청크 q의 계산 시간, \(T_{feed}\)는 한 coordinator가 필요한 정보를 생산·전송하는 시간이다. 이는 merge/drain의 일부까지 제외한 하한이며 성능 보장이 아니다. 어떤 자원이 실제 critical path인지 측정하기 전에는 모든 비용을 /p로 나누지 않는다.

gather의 H는 각 청크의 실제 \(D_q\)로 계산해야 한다. 청크마다 growing prefix 전체를 복사하면 target은 독립이어도 누적 전송이 커진다. 필요한 read-only history를 한 번 장착하거나 sparse gather payload를 제공할 수 있는지에 따라 전혀 다른 모형이 된다. thread는 주소 공간을 공유하므로 pickle 비용이 없어도 bandwidth·cache miss·false sharing·할당 비용은 남는다.

동시에 살아 있는 청크 수를 Q, record당 작업 공간을 v_w라 하면

\[
M_{resident}\ge M_{history}+M_{fixed}+QBv_w+M_{reorder}.
\]

따라서 B의 손익분기 하한과 메모리·guard latency가 정하는 상한이 함께 만족되어야 한다. 무제한 futures 제출은 bounded independent chunks 계약과 맞지 않는다. stream 결과는 성공 시 metric별 작은 요약으로 축약할 수 있지만, 실패 ordinal·정확한 진단 재생에 필요한 payload를 버려서는 안 된다.

위 메모리 식은 서로 겹치지 않고 동시에 살아 있는 버퍼의 payload 장부다. OS의 실제 RSS나 process별 공유 페이지의 합을 예측하는 식으로 사용하지 않는다.

### 7.4 lock이 있는 thread 분해

계산 중 λ 비율이 하나의 C 전역 lock 아래 직렬이라면, 다른 병목이 없는 이상화된 계산 가속도

\[
r_{thread}\le\frac1{\lambda+(1-\lambda)/p}
\]

다. 이것은 §6의 comparator 외부 직렬 비용과 다른 내부 제한이다. pure Rust 감사 kernel이 C 전역 상태를 전혀 읽지 않으면 그 kernel의 λ는 별도로 평가할 수 있다. 원래 C 호출을 그대로 thread로 감싸는 경우에는 lock이 사라지지 않는다. process는 주소 공간을 나누지만 초기화, 이력 전달, 메모리 복제와 비용 장부의 부담을 새로 가진다.

## 8. CFFI 경계의 R6 수학·소유권 조건

CFFI 공식 문서는 GIL-enabled Python에서도 C 호출 전에 GIL을 해제한다고 명시한다. 따라서 GIL은 C 자료의 동시 접근을 보호하지 않는다. C library 자체가 thread-safe인지, 전역 lock 또는 객체별 lock이 필요한지를 따로 판단해야 한다. [CFFI Thread Safety][cffi-thread]

현재 조사한 REC의 Python oracle은 `ctypes.CDLL`이며, CFFI 후보가 이미 존재한다고 주장하지 않는다. Rust 경계는 별도로 process-local `C_LOCK`으로 초기화를 포함한 원래 C 전역 상태를 보호한다. C harness의 `loaded` 지연 초기화와 static table도 확인했다. 초기화만 직렬화했다고 모든 연산의 thread safety가 증명되지는 않는다. [현재 Python 경계][rec-ctypes], [C 전역 상태][rec-c], [Rust 경계][rec-ffi]

부모가 CFFI/다른 FFI를 쓰면 다음을 확인해야 한다.

| 조건 | 필요한 이유와 통과 의미 |
|---|---|
| ABI·길이·dtype·alignment·stride 일치 | 311/311/3 또는 고정 record 폭과 실제 버퍼가 일치해야 한다. 잘못된 해석은 병렬성 이전의 다른 함수다. |
| 입력 lifetime 및 불변성 | C가 읽는 동안 Python/다른 worker의 resize, write, free가 없어야 한다. `const` 선언만으로 외부 alias를 봉쇄하지 않는다. |
| 출력의 단일 쓰기 소유권 | worker별 disjoint output 또는 명시적 동기화; 실패 시 부분 결과를 승인하지 않는다. |
| 모든 C 전역 상태의 목록 | lazy init, table mutation, static scratch, CWD 의존 파일, callback, 내부 thread 등을 조사한다. 각 객체 lock과 전역 lock은 동등하지 않다. |
| callback·오류 경로 | Python callback이 GIL을 재획득하거나 lock을 다시 잡는 경로, 예외 뒤 lock/버퍼 해제가 필요하다. |
| libm·FP 환경 | worker의 rounding 및 FTZ/DAZ, FMA/contraction, symbol binding이 baseline 계약과 맞아야 한다. |
| process 경계 | 시작 방식과 worker별 초기화가 명시되어야 한다. 살아 있는 thread/lock을 가진 process의 단순 fork를 안전하다고 가정하지 않는다. |
| worker 종료와 비용 | 실패·취소 뒤 다른 worker가 버퍼를 쓰지 않도록 수명과 종료를 동기화하고 live-child CPU까지 제한한다. |

CFFI의 cdata/포인터는 소유 객체의 수명과 구분된다. 빌린 포인터가 호출 뒤 탈출하거나 내부 배열의 keepalive가 사라지는 설계는 불변 입력 정리의 전제를 깨뜨린다. 공유 메모리의 close/unlink 시점도 모든 소비자의 사용 종료와 연결되어야 한다. [CFFI using][cffi-using], [SharedMemory 수명][shared-memory]

이 표는 thread safety의 **검토 조건**이며 현재 작성 중인 코드의 safety 판정이 아니다. 반복 실행이 우연히 같은 결과를 냈다는 사실만으로 data race 부재를 입증하지 않는다.

## 9. VigilODE의 정확 kernel 재사용과 방법 변경의 경계

앞서 완료한 [VigilODE intake][vigilode-intake]의 고정 snapshot을 재사용한다. 그 파일 SHA256은 `7cf3cb29c62774dd4a50ae88aeaca6167494a40541100c48aef44ddffd8506d3`이며 GitHub snapshot은 2026-10-20 02:48:54 UTC다. 아래는 그 시점까지 직접 읽은 소스·공개 실행 증거다. 이 이론 보고서에서 live head를 다시 조사하거나 새 실행을 시작하지 않았다.

### 9.1 정확한 source identity

| 대상 | commit |
|---|---|
| REC 현재 pin | `a21d573980f66fe02891bd216153443b5352f921` |
| 당시 main | `8d0c79184e09efb5bdadc24a6315c60a71a44264` |
| development tip | `c03ca90f19a9e64ba7751c069325a48b54b39c2e` |
| [PR73][pr73] head | `3c0157910076ce552283c831c2be000c66671fab` |
| [PR74][pr74] head | `15c43ce76734d0a560fcec5909ac49f1e6f2d347` |
| [PR75][pr75] head | `6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a` |
| midcheck의 사용자 지정 초기 head | `aa0b9cbf33be81ca23e01b67b39fbb86a816a135` |
| midcheck의 intake 시점 최종 공개 head | `e0ea8b640448ca6990adc1bf9fc53c04d51d527f` |
| 최종 midcheck 실제 측정 source | `aaa8116cbb20842eb5ebe308939670f6dd93bb0a` |

main은 pin보다 오래된 계열이다. development tip의 integrator/krylov 핵심은 pin과 같고, 읽은 core 수치 소스 차이는 `operator.rs`의 explicit shifted matrix 구성에서 panic성 `expect`를 typed error 전파로 바꾼 부분이다. 이를 새 REC kernel 가속으로 보지 않는다. PR75는 PR74 위에 쌓였으며 PR73 kernel이 모두 포함된 통합 개선판이라고 가정할 수 없다. [비교 근거와 source URLs][vigilode-intake]

### 9.2 실제 재사용할 수 있는 파일·API

| source/API | 재사용할 원칙 | 원래 REC에 대한 제한 |
|---|---|---|
| PR73 [exact_band_cache.rs][vig-cache] / private `ExactBandCache::{matches,record}` | finite shift의 bits와 모든 행렬 entry bits를 비교하고 성공한 factorization만 재사용; 실패 때 invalidate | 같은 h만으로 hit를 인정하지 않는다. shift는 `1/(h*gamma)`다. 차원·대역폭·pivot 정책이 workspace에 묶인다는 전제도 필요하다. |
| PR73 [rodas5p_fast.rs][vig-fast] / `BandedKernel::{FixedWidth2,FixedWidth2ExactCache}`, `integrate_rodas5p_fast_banded_observed_with_kernel` | l=u=2에서 같은 pivot tie·교환·산술 순서를 보존하는 specialization | REC의 311+311+3 **record 폭**과 LU의 대역폭 2는 다른 개념이다. 원래 atomic의 80-bin tridiagonal 및 2×2 Schur 계산을 이 LU로 교체할 근거가 아니다. |
| pin [parallel.rs][vig-parallel] / `ParallelExecution::{sequential,rayon,map_ordered,try_for_each_ordered_mut,apply_operator_rows}` | bounded local pool, 독립 index 작업, index 순서 출력 | 이미 pin에 있다. 출력 순서 보존은 FP sum·오류 발생 순서·원래 trace 보존을 자동으로 보장하지 않는다. |
| pin [matrix.rs][vig-matrix] / `DenseMatrix::matvec_into`, `LuFactorization::{new,solve,solve_rows}` | 이미 존재하는 dense matrix/LU의 API 참고 | 새 head의 추가 이득이 아니다. 원래 합을 compensated dot/faer 순서로 바꾸는 것은 별도 parity 문제다. |
| PR75 [residual_first.rs][vig-lazy] / `coupled_step_residual_first` | 실제 필요한 시점까지 JVP 등 작업을 미루되 같은 입력·잔차·epoch 유지 | 아이디어는 재사용 가능하지만 coupled homotopy/Newton 적분 자체는 원래 REC 재귀와 다르다. |
| PR75 [fallback.rs][vig-fallback] / `coupled_or_sequential_budgeted` | candidate 단계 budget과 실패를 명시하는 구조 | candidate의 JVP cap은 fallback 및 전체 wall/CPU 상한이 아니다. |

정확 source hash: PR73 `exact_band_cache.rs`의 Git blob은 `498f09e04adc33886cb61b3fa1c433f020262d45`, SHA256은 `7edfcbb9762be4d3dd6bdef38814397aa49524921902665b8c232ea5f697918b`이다. PR73 `rodas5p_fast.rs` blob은 `7aa2e546e1f62ba2ca9e9fbe3f789f1492c2e515`, SHA256은 `5a7789d16699c27484b869a1208c53534ee101de81077270d9ed7d3dbed707e0`이며 pin의 같은 파일 SHA256은 `911a740b89b9558ec124fa3d5da851ab02ee4d144b523a9279d0ff772c254651`이다. pin `parallel.rs`의 blob은 `ffdfb1cef258ed43586db0323eb0e7f9de27dd53`, SHA256은 `b1216fcb5a5352a0f51422d089caa9343cda1d13fefbf94146b1b171b8431d92`이다. [원 intake][vigilode-intake]

PR74 coupled solver는 autonomous identity-mass/JVP, shared projection basis, homotopy Newton과 full-space residual screen을 쓴다. 동시에 실행하는 stage callback은 **같은 고정 iterate에서 독립인 호출**이다. 시간 단계가 독립이라는 뜻이 아니다. REC 진단계의 명시적 시간 의존성과도 전제가 다르다. projection, 새로운 solver, compensated dot, 새로운 step size, 다른 escape 식은 이번 원래 방법 요구하에서 이식 대상이 아니다.

### 9.3 새 공개 실행 결과의 실제 범위

| 공개 실행 | 관측 결과 | 경계·해석 |
|---|---|---|
| PR73 run `39304607635`, 측정 source `f8e89b70528da8490fbe1febf0b0ede9ff84a01e` | 324/324 state/time bit 비교. brusselator127 parent/fixed2 ratio 1.05044, family CI [1.04775,1.05554]. diffusion127 dyadic129 cache ratio 1.11808 [1.10632,1.12377], factorization 134→8, J 134 유지 | 특정 upstream 행렬·출력에서의 증거. nonlinear cache 0-hit는 fixed2보다 느렸다. workspace 660s timeout과 과거 ledger 문제는 별도 남았다. [결과][vig73-results] |
| PR74 run `39349031422`, 측정 source `1e4a993874d6930ea2bb41bb0ff7392f21c33df7` | few-mode n=12288,h=.001: 1→4 worker ratio 2.0765 [2.0202,2.1531] | coupled 4-worker 6.172241ms, sequential matrix-free 5.53202ms. 상대 stage 병렬 이득이 전체 방법 우위를 뜻하지 않는다. [결과][vig74-results] |
| PR75 run `39355449893`, 측정 source `f08d152a35fb2db748692570969cb1723c287c26` | 같은 few-mode에서 eager/lazy 1-worker ratio 1.4117 [1.3969,1.4241], 27 stage/output/embedded bit 비교, JVP 59→35, RHS 25 유지 | 4-worker lazy 7.7376035ms와 seq-MF 7.709782ms. cap64 chain 음성대조는 transaction 1.0023865→10.754173ms로 악화. budget만으로 전체 이득을 보장하지 않음. [결과][vig75-results] |
| 최종 midcheck run `39360536475` | 39 configurations×8 blocks=312 valid timing cells, cell당 5 repeats. 26 matched/4 diagnostic pairs, readback PASS. few-mode96 h=.001 eager/lazy ratio 1.1968794, 관측 block 범위 [1.1508696,1.2359819] | 한 CPU affinity, sequential coupled executor라 병렬 확장 증거가 아니다. 범위는 CI가 아니다. fast/banded 비교는 이미 pin에 있는 `BandedKernel::Slices`를 사용한다. [SUMMARY][mid-summary], [AUDIT][mid-audit], [PAIRS][mid-pairs] |

midcheck의 few-mode96 세 방법에서 보고한 경험적 error upper 값은 `9.704178605535321e-13`이다. 그러나 Diffsol/lazy 12.0928, DVODE/lazy 2.45337의 큰 비율은 각각 오차비 약 10,960 및 702,680의 **unmatched** 비교다. matched 기준은 frozen target의 1.1배 이내 및 관측 error ratio≤2였다. brusselator200의 fast/banded paired ratio 4.9692649, 관측 범위 [4.9125755,5.3594819]도 해당 문제의 수치 방법 비교이며 REC 감사 가속에 전용할 수 없다. [midcheck 실제 pairs][mid-pairs]

초기 midcheck `39359950752`는 source pin 누락으로 build 전 exit128, 다음 `39360079278`는 312회 측정 뒤 `len(pairs)>30` 검사에서 30쌍 때문에 audit FAIL이었다. 최종 `>=30` 수정 후 `39360536475`는 전체 새 실행을 했다. 실패 기록을 지워 성공으로 합산하지 않는다. [이전 intake의 실패·최종 실행 추적][vigilode-intake]

upstream root와 companion crate는 MIT, copyright (c) 2026 cosmosapjw-quantum이다. 실제 복사 시 저작권·허가문을 유지한다. 원래 HyRec 및 외부 비교 solver 의존성의 license/출처는 각각 별개다. [upstream LICENSE][vig-license]

## 10. R6: 이번 유도 검토와 구현 후 음성대조 기준

### 10.1 이번에 실제로 완료한 수학 검토

독립성은 별도 검토자 인원이라는 뜻으로 사용하지 않았다. 같은 결론을 **연산 그래프 귀납, 분할/선택 연산 증명, 실패 반례, 별도 계산 엔진**으로 교차 확인했다.

| 항목 | 수행한 검토 | 현재 판정 |
|---|---|---|
| 순수 per-record map 분할 | dependency별 입력 비트 동일성에서 출력 동일성 귀납 | 전제하에서 성립 |
| finite max와 tie | 최대 원소 선택 및 ordinal 전순서의 결합성; 초기 +0 포함 | 전제하에서 성립 |
| NaN/±0/합의 위험 | Python binary64의 세 작은 반례 실제 계산 | 반례 확인; 후보 테스트 아님 |
| causal gather | 정확한 두 source index, active/미래 guard, 마지막 구간 w 보존을 고정 소스와 대조 | 승인 snapshot에서만 분할 가능 |
| 취소 및 gate perturbation | \(\delta P=\delta z/\tau\), reciprocal 차이, 분수 차이 직접 유도 | 주어진 입력오차·rounding 항 조건하에서 성립 |
| Amdahl와 손익분기 | 초판 Wolfram exact algebra 및 후속 부모 결과; 정확 측정 분수를 Python `Fraction`으로 별도 검산 | §6의 정확 분수로 갱신; 부모의 symbolic 결과는 전달 출처 명시 |
| 새 Rust/CFFI 후보 source·binary | 이 보고서의 검토 입력으로 제공·고정되지 않음 | `NOT_RUN / NOT_REVIEWED` |
| 새 REC 정확성·성능·수렴 | 실행하지 않음 | `NOT_RUN` |

초판에서 이 하위 작업이 직접 수행한 경고 없는 Wolfram 후속 실행 결과는 반올림 비중 0.5696에 대한 `625/269`, `712/87`, `500/233`, `17/500` 및

`((D*dN)-(dD*N))/(D*(D+dD))`,

`N*(-alpha/B+c-c/p-tau)-A`

였다. 첫 실행의 removable-singularity limit 계산에는 `Power::infy` 경고가 있어, 경고 없는 유리수/기호 재계산과 직접 Taylor 전개로 근거를 정리했다. 이 초판 계산 이력은 보존하되 현재 Amdahl 값은 §6의 실제 측정 분수로 대체했다. 단순 exact arithmetic에서 `(2^53+1)-2^53=1`인 것과 binary64 순서 반례의 0/1을 혼동하지 않았다. 수행한 것은 식 검산이며 REC 벤치마크가 아니다.

**부모가 후속 전달한 실제 Wolfram 결과.** 다음은 부모 실행 보고를 그대로 분리해서 기록한 것이다. 해당 WL 세션의 raw log를 이 하위 작업에서 새로 조회하거나 재실행하지 않았다.

| 부모가 전달한 식·결과 | 적용 가능한 결론 | 적용되지 않는 결론 |
|---|---|---|
| `Reduce[d>1 && Ceiling[d]<2,d,Reals] -> False` | 실수 d>1이면 Ceiling[d]≥2. 정수 j에 대해 정확 실수식 floor(j-d)+1=j-Ceiling[d]+1≤j-1 | binary64로 계산한 j-d의 floor가 자동으로 같은 인덱스라는 결론 |
| `(cs+cm+ck/w<ck)==(cs+cm<ck*(1-1/w)) -> True`, 양의 가정 | 같은 비용 모형의 정확 실수 부등식 재배열. 양의 cs,cm,ck에서는 이득에 w>1이 필요 | 비용 수치의 측정 정확성, 실제 worker 효율, float 경계에서 두 predicate의 bitwise 동등성 |
| ordered finite-real `Max` associativity `-> True` | 유한 실수 최대값의 결합성 | NaN/±0의 처리, argmax tie, per-record 산술, 로그·실패 순서의 동등성 |
| `p=21409138/37588099`, ceiling `2.3232702643884`; s=2/4/8에서 `1.39818316/1.74574662/1.99352390` | §6의 유리수 계산과 일치 | REC 새 측정 속도 또는 wall-time 예측 |

**부모 WL 경고:** `MinValue::lpsub`, `MaxValue::lpsub`가 발생했다고 전달받았다. 전체 경고 본문·발생 위치는 이 메시지에 제공되지 않았다. 이를 경고 없는 solver certificate로 표현하지 않으며, `True/False` 출력은 명시된 실수 영역의 항등식/조건 판정으로만 기록한다. 기존 하위 작업의 `Power::infy`와 부모의 `lpsub`는 서로 다른 실행의 경고다.

실수/float 구분을 위한 추가 **합성 산술 반례**를 이 하위 작업에서 계산했다. j=4, d=`nextafter(1,+inf)`=`0x1.0000000000001p+0`이면 d>1이고 ceil(d)=2다. 정확한 j-d는 `13510798882111487/4503599627370496`으로 floor=2이지만, binary64의 `4.0-d`는 3.0으로 반올림되어 floor+1=4=j가 된다. 이는 실제 REC 에너지 표의 delay에서 발생했다는 관측이 아니다. 정확 실수의 Ceiling 판정만으로 기존 미래 읽기 guard·clamp·rounding 검증을 제거할 수 없다는 반례이며 새 적분/후보 테스트가 아니다.

### 10.2 후보가 고정된 뒤 적용할 판정표 — 아직 실행하지 않음

| 음성대조·경계 입력 | 검출하거나 보존해야 할 결과 |
|---|---|
| 모든 spectral 입력 중 한 값/에너지/온도 한 bit 변경 | 정확 cache가 필요한 경우 miss; 비교 결과는 frozen scalar가 정한다. |
| 같은 index에 다른 checkpoint, table, owner 또는 epoch | 오래된 cache entry가 hit하면 실패. Python/C owner 혼용도 실패. |
| NaN/±Inf, NaN이 첫/중간/마지막 원소인 chunk | 원래 admissible 입력·검사 경로에 따른 nonfinite 처리; NaN 무시 max로 통과시키지 않음. |
| ±0, 같은 max의 여러 index, 빈 chunk | +0 초기값, 동률 witness, 빈 결과 의미를 보존. bit 검사와 수치 equality를 구별. |
| 순서가 다른 합 `[2^53,1,-2^53]` | 원래 합을 새 tree/compensated sum으로 바꾼 경우 감지. max 정리로 합을 정당화하지 않음. |
| unknown/duplicate/missing/reordered tag·bin·step | 최초 오류 ordinal, counts, BASE/STEP/END 제약과 raw 진단 prefix 일치. |
| decimal rounding 경계, subnormal, ±0, 지수 표기·잘못된 token | 정상 token의 Python/Rust parse bits 일치와 잘못된 행의 원래 오류 순서 확인. |
| 여러 chunk의 서로 다른 오류, 앞쪽 parity/뒤쪽 parse 오류 | 완료 순서와 관계없이 frozen scalar의 처음 오류를 공개. |
| A 실패 0,1,64,65개와 중간 V/L 실패 | 원래 gate FAIL 유지; 65번째의 중단 위치, forensic owner 및 flush 순서 보존. |
| `tau` threshold의 아래/동일/위 이웃, 깊이 `1.592053136706244e-6` | 기존 source test의 scalar-libm 분기와 결과를 별도로 대조; 새로운 안정식 대체를 승인하지 않음. |
| gather j=2, prehistory, 마지막 `[j-2,j-1)`의 0<w<1 | 정확 두 인덱스와 w, q=0 zero prehistory, source-row 매핑 유지. |
| 필요한 과거 셀 하나 변경, 현재 열/미래 열에 sentinel | 필요한 과거 변경 반영; 현재/미래 읽기 거절. 두 점 보간이라는 이유로 얕은 halo를 가정하지 않음. |
| append 중 오류·capacity 끝·clock mismatch·미완료 source 열 | 부분 열 승인 금지; 원래 guard 및 predictor memories 보존. |
| thread 수·chunk B·마지막 짧은 chunk·작업 완료 순서 변화 | per-record bits, maxima, counts, status, 진단 bytes 동일. 제한 범위에서만 대조. |
| CFFI alias 변경/수명 종료/동시 초기화/worker 예외 | 동기화와 소유권 근거를 source에서 먼저 확인; 단순 반복 일치로 safety를 선언하지 않음. |
| CPU guard·worker crash·취소·slow first chunk | bounded 대기/메모리, 살아 있는 worker의 CPU 포함, 처음 실패 및 이미 flush한 증거 유지. |

이 표는 신규 테스트 코드를 작성하라는 이번 하위 작업의 수행 기록이 아니다. 부모가 후보 commit/build를 고정한 후 시행할 차등 검증의 판정 기준이다. 원래 scalar auditor를 독립 baseline으로 유지하고, 기존 저장된 stream/NPZ를 입력으로 쓰면 완료된 5,210단계 적분을 다시 돌릴 필요가 없다.

## 11. R8–R10 handoff

부모의 compiled Rust fixed-width spectral audit와 bounded 독립 청크 방향은 다음 **조건부 계약**에 부합한다. 기존 순서 parser/guard/forensic coordinator가 입력 의미와 실패 순서를 소유하고, worker는 이미 확정된 record와 불변 문맥의 순수 수치 map만 수행한다. 최대값은 finite-domain 및 tie 규칙을 고정해 집계하며, scalar libm·원래 산술을 유지한다. causal geometry는 고정 입력까지만 캐시하고 시간 재귀와 단계 사건은 원래 순서로 진행한다.

정확 cache pattern과 독립 callback scheduling은 VigilODE에서 가져올 수 있는 재사용 근거다. RODAS/coupled projection/Newton, 새로운 합/escape 식, 다른 h는 이 계약의 구현 최적화가 아니다. upstream의 bit 일치·실행 시간은 그 source와 문제 범위의 증거로만 유지한다.

현재 상태를 명확히 남긴다: **수학 유도·출처 조사 완료 / 새 후보 구현 검토 미수행 / 새 벤치마크 미수행 / REC 신규 numeric PASS·가속·전역 수렴 주장 없음.** 기존 U5와 cost HOLD는 유지한다. 부모의 backup intake는 반복하지 않았다.

### 11.1 부모의 후속 실행·준비 상태 — 전달 증거

다음은 이 대화에서 받은 부모의 상태 보고다. 이 하위 작업은 GitHub/Dropbox/ACK를 다시 조회하거나 전체 raw를 재다운로드하지 않았다. source HEAD를 임의로 확장하거나 아직 없는 review 결과를 붙이지 않는다.

| 항목 | 전달받은 사실 | 검토 상태 |
|---|---|---|
| Stage0 [PR110][rec-pr110] | abbreviated SHA `73f201c`, pushed, 3 ACK | 부모 제공 상태. main 최종 adapter의 C9 승인과 구분 |
| Rust/Rayon | 새 `Rayon 1.12` 라이브러리가 실제 staging됨 | 후보 source/build를 이 하위 작업에서 검토하지 않음; 독립 C9 대기 |
| R3M full raw 복구 | Dropbox 실제 다운로드 232,521,236 bytes; SHA256 `8cd5da29521b47d6b715dfa6889ae11d239ef430460deae97824ee32584b80b9`; prior ACK와 일치 | 부모가 보고한 실제 복구·hash 대조. 이 하위 작업의 별도 readback 아님 |
| 전체 saved stream 대조 | 약 8.5M record의 complete stream을 비교할 계획; prefix+V/A/L spectral field 행만 8,510,412개이며 control 행도 유지 | 계획. 완료/PASS로 표기하지 않음 |
| 새 실행 범위 | 기존 full 적분 재실행 없이 저장 stream 재사용; 새 smoke는 16-step만 원래 cap 안에서 | 부모 계획. 이 하위 작업은 실행하지 않음 |
| adapter | 구현 검토 대기 | main 최종 독립 C9는 별도 후속 단계 |

기존 저장 입력이 복구되었다는 사실은 향후 차등 감사의 입력 준비를 뒷받침한다. candidate의 전체 record bits·maxima·counts·진단 bytes가 일치한다는 결론은 실제 대조 결과와 고정 source/build가 나온 뒤에만 추가한다. 16-step smoke도 전체 적분 수렴이나 production 가속을 대표하지 않는다.

## 12. 출처

외부 참고문헌은 아래 원 논문 또는 공식 문서의 직접 판독에 한정했다. SciSpace의 서지 결과 자체를 정량 보증으로 쓰지 않았고, SLEEF와 재현 가능한 합은 각각 저자 원문/ACM 페이지에서 확인했다. 버전이 고정되지 않은 공식 문서는 2026-10-20 조회본이며 대상 runtime과 동일하다고 가정하지 않는다.

- Gene M. Amdahl, *Validity of the Single Processor Approach to Achieving Large Scale Computing Capabilities* (1967): [원 논문 PDF][amdahl]. 사용 범위: 남는 직렬 비용을 가진 고정 작업량 모형.
- David Goldberg, *What Every Computer Scientist Should Know About Floating-Point Arithmetic*, ACM Computing Surveys 23(1), 5–48 (1991), DOI [10.1145/103162.103163](https://dl.acm.org/doi/10.1145/103162.103163): [Oracle 수록 원문][goldberg]. 사용 범위: rounding, 취소, 연산 순서.
- Naoki Shibata, Francesco Petrogalli, *SLEEF: A Portable Vectorized Library of C Standard Mathematical Functions*, IEEE TPDS 31(6) (2020), DOI [10.1109/TPDS.2019.2960333](https://doi.org/10.1109/TPDS.2019.2960333): [arXiv 원문 v1][sleef]. 사용 범위: ulp 정확도와 명시적 bit-consistent 구현 조건.
- Ahrens, Demmel, Nguyen, *Algorithms for Efficient Reproducible Floating Point Summation*, ACM TOMS 46(3), Article 22 (2020): [원 논문 페이지][sum-paper]. 사용 범위: 새 재현성 알고리즘과 원래 순차 합의 차이.
- [Rust f64][rust-f64]: `max`, `maximum`, `to_bits`, `exp`의 공식 의미. REC toolchain의 실제 구현 검토를 대체하지 않는다.
- [CFFI Thread Safety][cffi-thread], [CFFI using][cffi-using]: GIL, library reentrancy, cdata 소유권·수명.
- [Python multiprocessing][multiprocessing], [SharedMemory][shared-memory]: 직렬화·process 시작·공유 메모리 수명. 특정 Python start-method 기본값에 의존하는 설계는 제안하지 않았다.

[profile]: PROFILE_INTAKE.md
[profile-raw]: ../../rec_r3m_u6_full_owner_20261019/receipts/full5210_stored/full5210_stored.r3l_profile.json
[rec-audit]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/scripts/verify_r3i_h2_u6_rt_boundary.py
[rec-history]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/src/full_bianchi_hyrec/trajectory/owned_flrw_history.py
[rec-owned]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/src/full_bianchi_hyrec/trajectory/primordial_2012_owned_u6.py
[rec-atomic]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/src/full_bianchi_hyrec/trajectory/full_2012_atomic_source.py
[rec-atomic-tests]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/tests/trajectory/test_full_2012_atomic_source.py
[rec-clock]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/src/full_bianchi_hyrec/trajectory/primordial_2012_refined_start.py
[rec-ctypes]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/scripts/verify_r3i_h2_u5_thermal.py
[rec-c]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/scripts/c_harness/original_hyrec_r3i_h2_u6_rt_boundary_harness.c
[rec-ffi]: https://github.com/cosmosapjw-quantum/rec_bianchi/blob/368d87ad5de90dde74226ed109c3ba29d9607c84/rust/rec-hyrec-vigilode/src/ffi.rs
[rec-pr110]: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/110
[amdahl]: https://www.cs.cmu.edu/~18742/papers/Amdahl1967.pdf
[goldberg]: https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html
[sleef]: https://arxiv.org/html/2001.09258v1
[sum-paper]: https://dl.acm.org/doi/10.1145/3389360
[rust-f64]: https://doc.rust-lang.org/std/primitive.f64.html
[cffi-thread]: https://cffi.readthedocs.io/en/stable/overview.html#thread-safety
[cffi-using]: https://cffi.readthedocs.io/en/latest/using.html
[multiprocessing]: https://docs.python.org/3/library/multiprocessing.html
[shared-memory]: https://docs.python.org/3/library/multiprocessing.shared_memory.html
[vigilode-intake]: VIGILODE_INTAKE.md
[pr73]: https://github.com/cosmosapjw-quantum/vigilode/pull/73
[pr74]: https://github.com/cosmosapjw-quantum/vigilode/pull/74
[pr75]: https://github.com/cosmosapjw-quantum/vigilode/pull/75
[vig-cache]: https://github.com/cosmosapjw-quantum/vigilode/blob/3c0157910076ce552283c831c2be000c66671fab/crates/rodas5p-integrators/src/exact_band_cache.rs
[vig-fast]: https://github.com/cosmosapjw-quantum/vigilode/blob/3c0157910076ce552283c831c2be000c66671fab/crates/rodas5p-integrators/src/rodas5p_fast.rs
[vig-parallel]: https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-integrators/src/parallel.rs
[vig-matrix]: https://github.com/cosmosapjw-quantum/vigilode/blob/a21d573980f66fe02891bd216153443b5352f921/crates/rodas5p-core/src/matrix.rs
[vig-lazy]: https://github.com/cosmosapjw-quantum/vigilode/blob/6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a/crates/vigilode-coupled/src/residual_first.rs
[vig-fallback]: https://github.com/cosmosapjw-quantum/vigilode/blob/6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a/crates/vigilode-coupled/src/fallback.rs
[vig73-results]: https://github.com/cosmosapjw-quantum/vigilode/blob/3c0157910076ce552283c831c2be000c66671fab/research/banded_exact_reuse_20261020/RESULTS.md
[vig74-results]: https://github.com/cosmosapjw-quantum/vigilode/blob/15c43ce76734d0a560fcec5909ac49f1e6f2d347/research/coupled_native_20261020/runs/39349031422/REPORT.md
[vig75-results]: https://github.com/cosmosapjw-quantum/vigilode/blob/6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a/research/coupled_economy_20261020/runs/39355449893/REPORT.md
[mid-summary]: https://github.com/cosmosapjw-quantum/vigilode/blob/e0ea8b640448ca6990adc1bf9fc53c04d51d527f/research/midcheck_20261020/runs/39360536475/SUMMARY.json
[mid-audit]: https://github.com/cosmosapjw-quantum/vigilode/blob/e0ea8b640448ca6990adc1bf9fc53c04d51d527f/research/midcheck_20261020/runs/39360536475/AUDIT.json
[mid-pairs]: https://github.com/cosmosapjw-quantum/vigilode/blob/e0ea8b640448ca6990adc1bf9fc53c04d51d527f/research/midcheck_20261020/runs/39360536475/PAIRS.json
[vig-license]: https://github.com/cosmosapjw-quantum/vigilode/blob/6c945b6c6e0e024d8f733c21da8d35fbcc3c5f2a/LICENSE
