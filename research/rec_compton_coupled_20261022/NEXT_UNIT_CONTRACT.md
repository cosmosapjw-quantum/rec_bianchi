# Next unit proposal: saved-state diagnostic equivalence and reuse

Status: **PROPOSED; IMPLEMENTATION_NOT_RUN; BENCHMARK_NOT_RUN; NEW_ODE = 0**.

2026-10-22에 완료된 Compton 8개 계산과 그 후처리를 근거로 한 다음 샌드박스 연구 단위의 제안이다. 이 문서 작성 중 수행한 것은 기존 영수증·배열·코드의 읽기와 유한 비교뿐이다. 아래 최적화 구현과 성능 실험은 아직 수행하지 않았다. 기존 8개 IVP 집합을 확대하거나 다시 적분하지 않는다.

작성자는 현재 단위의 `THEORY_KO.md` 작성자이다. 이 제안은 자신의 이론·향후 구현에 대한 독립 승인서가 아니다. 실제 후보 구현은 별도 검토자가 저장된 입력과 독립적인 계산 경로로 확인한다.

## 1. 다음 질문과 이미 확보한 계산

다음 질문은 **같은 물리 상태와 같은 진단을 유지하면서, 상태별 중복 계산과 중첩 격자의 재평가를 줄일 수 있는가**이다. 이번에는 새로운 열 과정, 새 광자 스펙트럼, 더 큰 IVP 표본보다 먼저 저장된 계산의 재현성과 실행 비용을 개선한다.

근거는 [최종 분석 영수증](results/analysis_v1/RESULT.json), [최종 수치 요약](results/analysis_v1/SUMMARY.json), [네 개의 수치 정밀화 비교](results/compton8/REFINEMENT.json)이다. 8개 사례는 `COMPLETE`, 모든 기존 사례별 검사는 통과했고 네 쌍의 정밀화 비교는 `PASS`이다. 이는 지정된 유한 사례와 저장된 표본에 대한 결과이다.

| 고정할 식별자 | 값 |
|---|---|
| Compton runtime identity | `c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac` |
| Analysis identity | `f824bdead1ce75b94f5102764184ea8dee2db71ecc06296dc7fa2ac9d71708c3` |
| 최종 분석 `RESULT.json` SHA-256 | `ed78cc97e045077666b869d818e3b0ea550b73848bd58051d99bc515c094082e` |
| 최종 분석 `SUMMARY.json` SHA-256 | `c04267f78b3c328b7e786dd2bbe818c19583bf8585c127c92147ab090374e502` |
| Campaign lock SHA-256 | `1ffa5aad2dd572a6184b4a020f542dfbdcaa25103b2ce6c6d10cce1ace725504` |
| Refinement receipt SHA-256 | `6b1783775c9c79fb5fa7c6d054eb2beb72afd461cd4708d79a5f082eedaa7061` |

사례는 두 seed `s03_m03_r03`, `s04_m04_r04`와 두 독점적 Compton 가지 `actual_hot`, `planck_reference`, 각각의 nominal/refined 조합이다. 같은 full63 상태와 같은 정확한 restart를 유지한다. 과거 열 계산과 원래 donor의 초기 구간도 기존 식별자로 재사용한다.

최종 8개 결과에서 $T(z=2)=8885.2208$–$8896.9615$ K이며, 대응하는 no-Compton 열 계산보다 1220.9181–1231.6258 K, 즉 12.0682–12.1740% 낮다. dense1025의 최고 온도는 11389.2997–11411.5263 K이다. 실제로 변화한 경로에서 선택한 Compton 열 전달의 Simpson 적분은 −2.1841256–−2.1676284 eV/baryon, 공통 UV Compton 항은 +$(6.38859\text{–}6.39089)\times10^{-5}$ eV/baryon이다. 이 값은 기존 경로에 사후 보정한 온도 추정이 아니라 현재 8개 결합 계산의 결과이다.

두 복사 가지 사이의 차이와 각 가지의 no-Compton 대비 차이는 계속 분리한다. refined actual-minus-reference의 종점 온도 차이는 seed03에서 −0.392634 K, seed04에서 −10.707565 K이다. 두 seed의 온도·이온·광학 깊이 가지 차이는 관측된 정밀화 변화보다 크다. signed six-vector 전체의 가지 차이는 그렇지 않으며, stress-only는 seed03에서 그 비교를 통과하지 않고 seed04에서는 통과한다. 이 비교는 유한 정밀도 증거이지 전역 오차 상한이 아니다. 다음 실행 단순화에서 이 구분을 합치거나 작은 stress 신호를 새로 해석하지 않는다.

## 2. 측정된 병목: 적분 이후의 진단·저장

아래 시간은 기존 `results/compton8/*/RESULT.json`에 기록된 값이다. 새 성능 실험의 결과가 아니다.

| 사례 | 적분 wall s | 진단·저장 wall s | 사례 전체 wall s | 저장된 accepted 노드 |
|---|---:|---:|---:|---:|
| s03 actual_hot nominal | 6.9437 | 44.5259 | 51.7369 | 309 |
| s03 actual_hot refined | 6.7761 | 18.6640 | 25.5909 | 440 |
| s03 planck_reference nominal | 6.4525 | 12.7681 | 19.3639 | 309 |
| s03 planck_reference refined | 4.3681 | 66.6503 | 71.0871 | 440 |
| s04 actual_hot nominal | 6.3171 | 19.1082 | 25.5064 | 308 |
| s04 actual_hot refined | 9.2036 | 19.7285 | 29.0212 | 440 |
| s04 planck_reference nominal | 6.0870 | 40.0690 | 46.2345 | 308 |
| s04 planck_reference refined | 12.0313 | 27.5388 | 39.6754 | 440 |
| 합계 | **58.1795** | **249.0528** | **308.2164** | **2994** |

진단·저장이 사례 전체 시간 합계의 약 80.8%이다. campaign의 실제 청구 시간은 309.2018257 s로, 사례 시간 합계와는 다른 계측 범위이다. 각 사례의 시간 변동이 크므로 단일 사례의 비율을 안정된 속도 개선 예측으로 사용하지 않는다.

이후 별도 분석의 내부 계측은 56.8540823 s, 외부 프로세스 계측은 87.6827375 s이다([실행 영수증](evidence/analysis_execution/analysis_process.json)). 내부 collision 후처리 8개 시간의 합계는 49.9723552 s이다. 내부·외부 시간 차이를 현재 자료만으로 import, I/O 또는 특정 함수에 귀속하지 않는다. 다음 단위에서 그 경계를 측정한다.

현재 `run_compton.py:gather_set`은 각 상태에서 `sample`, `diagnostics`, `geometry.fields`, `geometry.normalized`를 각각 요청한다. 상속된 diagnostic 경로도 상태·열원·Compton 양을 다시 평가한다. 따라서 같은 $x,y$의 geometry와 number/thermal source에 대한 중복 호출이 코드상 확인된다. 다만 **Geometry가 가장 큰 단일 함수 병목이라는 프로파일 증거는 아직 없다**. 우선 계측할 대상이다.

저장 진단은 comparison109 872개, accepted 2994개, dense513 4104개, dense1025 8200개로 총 16170행이다. dense513의 점별 재평가를 없애면 이 중 4104행, 약 25.4%의 호출을 줄이는 구조가 된다. 이것은 호출 수의 감소량이며 wall-time 단축률이 아니다. collision 후처리의 세 격자에는 총 13176행이 있고 동일한 4104행의 중첩이 있다.

## 3. 중첩 격자의 실제 차이와 재사용 규칙

8개 사례의 기존 `dense_513.npz`와 `dense_1025.npz`를 직접 읽어 공통 위치를 비교했다. 모든 사례에서 x와 z는 `dense1025[::2]`와 bitwise 동일하다. 그러나 기존 driver가 `sol.sol`을 서로 다른 길이의 배열로 따로 호출한다. 실제로 저장된 모든 상태 성분이 bitwise 동일하지는 않다. 차이는 부동소수점 반올림 규모이다.

| 직접 비교한 양 | 8개 사례 전체 최대 절댓값 차이 |
|---|---:|
| native raw state / scaled ionic coordinates | $2.7755575615628914\times10^{-17}$ |
| $T$ | 0 K |
| 누적 Thomson $\tau$ | 0 |
| signed six-vector | $2.7755575615628914\times10^{-17}$ |
| 에너지 integrand | $3.0814879110195774\times10^{-33}$ J/baryon/x |

일부 이미 0에 가까운 상쇄 잔차는 자기 자신을 분모로 삼으면 상대 차이가 $O(0.1)$이 된다. 이를 유의한 열 전달 차이로 읽지 않는다. 잔차는 원래 에너지 throughput 정규화 또는 해당 단위의 절대 차이로 비교한다. 현재 배열이 갖는 이 반올림 차이 때문에 기존 513점 NPZ와 새로운 slice 제품의 해시가 같다고 주장할 수 없다.

제안한 규칙은 다음과 같다.

1. **동일 입력 상태 시험**: 기존 513점과 1025점의 각 raw state를 그대로 보존한 채, 새 진단 경로를 기존 경로·저장된 진단과 비교한다. 계산 재사용 자체의 영향을 먼저 분리한다.
2. **중첩 격자 시험**: dense1025의 x, raw state와 점별 진단을 한 번 계산한 뒤 `[::2]`로 새로운 513점 제품을 만든다. 원래 513점 제품과의 차이를 위 표처럼 별도로 보고한다. 새 제품은 자기 출처·해시를 가진다.
3. `cumulative_trapezoid`, Simpson 적분, endpoint energy audit, 각 격자의 극값·보존량·gate·sample count는 **513점 격자에서 다시 계산한다**. 1025점 누적 적분을 `[::2]`로 자르면 513점 trapezoid 규칙이 되지 않는다. 실제 기존 두 누적 배열은 8개 사례 모두 다르다.
4. CI/CE의 구간 support는 513점의 인접한 두 endpoint mask로 다시 만든다. 1025점의 구간 mask나 support 적분을 그대로 slice하지 않는다. 경계 구간과 analytic continuation을 합쳐 버리지 않는다.
5. comparison109와 accepted 노드는 일반적으로 dense1025의 부분집합이 아니다. 보간·반올림·근접 x 매칭으로 대체하지 않는다. 완전히 같은 x와 full63 입력 바이트가 확인된 경우에만 같은 계산 결과의 재사용을 허용한다.

이 문서의 읽기 비교는 `np.load(..., allow_pickle=False)`로 두 dense NPZ를 읽고 x/z의 `array_equal`, `raw_state - dense1025[::2]`, 진단·integrand의 성분별 차이를 계산했다. ODE나 기존 diagnostic 함수를 다시 실행하지 않았다. 이후 구현 단위는 이 비교 스크립트와 전체 입력 해시 목록을 자체 evidence에 보존한다.

## 4. 물리량을 보존하는 계산 구조

새 단위는 기존 연구 폴더 밖의 새 `research/rec_saved_diagnostic_reuse_<date>/`에서 작업한다. 과거 runtime·영수증·NPZ를 바꾸지 않는다. 다음 구조를 후보로 구현한다.

### 4.1 상태별 재료를 한 번 계산

하나의 호출 안에서 $x,y$, $Y$, $T$, $n_b$, geometry fields, number-network evaluation, thermal-source evaluation, Compton moments를 담는 명시적인 상태 자료를 만든다. 기존 owner의 함수와 상수를 호출하되, 같은 입력으로 여러 번 계산한 반환값을 각 진단 경로에 전달한다. 이미 한 번 생성한 71개 UV bin의 두 moment는 기존처럼 재사용한다.

반환값은 호출 단위로 불변 취급한다. 값이 비슷한 온도·이온 상태를 같은 cache key로 묶지 않고, 전역적인 마지막 상태 cache로 branch/config/source가 섞이지 않도록 한다. 원래 signed Newton trial의 허용 범위와 물리 상태의 admission을 혼동하지 않는다. 이번 작업의 기본 검증 입력은 기존에 저장된 물리 상태이다.

### 4.2 에너지 검사의 독립성을 유지

비용을 줄여도 다음 두 gas-source 계산은 각각 유지한다.

\[
Q_{\rm gas}^{(1)}=Q_{\rm kinetic}+n_b I\cdot F,
\qquad
Q_{\rm gas}^{(2)}=Q_{\rm absorbed}-Q_{\rm escape}+Q_C+Q_{\rm UV,C}.
\]

첫 결과를 두 번째 결과에 그대로 복사해서 source residual을 0으로 만들지 않는다. 서로 공유할 수 있는 것은 같은 물리 상태와 공통 입력 재료이며, 서로 검증하는 최종 합계의 정의는 보존한다. Li core·RR/DR escape, binding reservoir, particle source와 외부 bath 부호도 기존 소유권을 유지한다. `math.fsum` 등 현재의 합산 순서를 보존하는 단순한 재사용을 우선한다.

### 4.3 점별 계산과 격자 연산을 분리

`evaluate_points`는 같은 상태에 대한 물리량과 mask를 반환하고, `assemble_grid`는 주어진 x와 그 점별 결과에서 보존량, 구간 support, quadrature, 누적 적분, gate와 metadata를 만든다. 전체 구조를 새 ODE solver에 곧바로 연결하지 않고 저장된 상태 배열로 먼저 검증한다.

CI/CE도 동일한 구조를 사용할 수 있다. 채널별 계수·사건률·binding/kinetic/particle 항과 native species 순서를 보존한다. underflow, source-domain 밖의 continuation, unavailable 채널은 서로 다른 상태이다. 속도를 위해 unavailable을 물리적 0으로 바꾸거나 continuation을 0으로 자르지 않는다.

### 4.4 이번 기본 후보의 경계

RHS, Jacobian, BDF, tolerance, rate fit, 물리적 열 source, state scale은 이번 기본 후보에서 변경하지 않는다. 이전 이론에서 얻은 affine Compton 정확해는 대수 검사 기준으로 남는다. 이 최적화가 frozen-coefficient splitting이나 새로운 coupled solver를 사용했다는 뜻이 아니다. 이후 RHS/Jacobian의 반복 계산까지 줄이려면 별도 변경 범위를 정하고 같은 정확한 상태에서 연산자 전체의 동등성을 먼저 확인한다. 저장 상태 검사만으로 미래 적분 경로의 동일성을 주장하지 않는다.

## 5. 유한 검증·벤치마크 순서

### A. 입력과 프로파일 기준 고정

8개 `RESULT.json`과 그 안의 trajectory, accepted solver nodes, accepted diagnostics, dense513, dense1025 해시를 검증한다. 분석·collision 제품도 각각의 영수증과 묶는다. source inventory는 이번 새 diagnostic 코드와 기존 runtime/analysis/data identity를 분리한다. 분석 코드의 변화 때문에 이미 완료된 ODE를 다시 실행하는 경로를 만들지 않는다.

계측은 동일한 Python/NumPy/SciPy 환경과 단일 numerical thread에서 한다. 첫 작은 프로파일은 두 branch·두 seed·두 정밀도를 모두 포함한다. 반복적인 source/geometry 계산, CI/CE 계산, quadrature, NPZ 압축·쓰기, 해시·읽기를 나누어 실제 비용과 호출 수를 기록한다. 중첩된 함수 시간은 inclusive/exclusive를 구분해 합계가 이중 계산되지 않도록 한다.

### B. 같은 상태에서 동등성 확인

모든 16170개 저장 진단 행에 대해 새 계산을 원래 raw state에 적용하고 기존 물리량·진단과 비교한다. 원래 두 dense 격자의 반올림 차이를 먼저 없애거나 입력을 합치지 않는다. comparison109와 accepted 노드의 원래 상태·출력 순서도 유지한다. CI/CE의 세 격자 13176행에 대해서는 기존 채널별 자료와 mask·보존량·forcing을 비교한다.

단순 재사용에서 기대하는 목표는 같은 입력의 점별 결과가 그대로 일치하는 것이다. exact equality 여부와 성분별 절대 차이를 모두 기록한다. exact가 아닌 차이가 있으면 서로 다른 단위의 성분을 한 norm으로 숨기지 않고, 해당 물리량의 scale과 원래의 정밀화 변화에 비추어 분리해 조사한다. 기존 admission 임계값은 완화하지 않는다. 작은 상쇄 잔차를 자기 자신으로 나눈 상대 오차는 통과 판정에 사용하지 않는다.

모든 gate의 이름·결과, source mask, unavailable/underflow 표시는 보존되어야 한다. 잔차가 갑자기 정확히 0이 되는 경우에도 독립적인 식을 복사해 버린 것이 아닌지 확인한다. 여기서 식·단위·소유권 오류가 발견되면 성능 비교에 앞서 그 실패 자료를 보존한다.

### C. 중첩 격자 제품 재구성

그 다음에만 1025점으로부터 새 513점 제품을 만든다. 점별 입력의 알려진 차이와 계산 경로의 차이를 분리해서 보고하고, 513점의 모든 격자 연산을 다시 수행한다. 저장된 accepted 노드 전체의 검사 범위를 줄이지 않는다. continuum이나 미저장 Newton trial의 positivity를 새로 인증한 것으로 표현하지 않는다.

### D. 쌍을 맞춘 성능 비교

작은 timing corpus는 8개 사례당 최대 64개 상태, 총 최대 512개로 고정한다. 각 사례의 시작·끝, 최고 온도, 최대 source/ledger residual, source-support 경계의 양옆을 먼저 포함하고 남은 자리를 x에 고르게 배치한다. 선택된 인덱스와 실제 중복 제거 규칙을 manifest에 저장한다.

기준과 후보에 각각 같은 warm-up을 한 번 적용한 뒤 순서를 교대로 바꾸는 쌍 비교를 세 번 수행한다. 별도로 전체 corpus의 후보 재생성을 한 번 수행한다. CPU time, wall time, peak memory, 함수 호출 수, 파일 크기와 출력 해시를 함께 기록한다. 프로세스 전체 시간과 내부 계산 구간의 시간을 같은 열에서 비교하지 않는다.

성공 기준은 물리적 동등성과 측정된 계산량·시간의 개선이다. 임의의 두 배 속도 목표나 새로운 물리적 promotion gate를 만들지 않는다. 개선이 작거나 환경 변동보다 작으면 그대로 보고하고, 계측 결과가 가리키는 다음 병목까지만 제안한다.

### E. 유한 자원과 종료

제안한 실행 예산은 단일 worker·단일 numerical thread, 저장 상태 동등성·프로파일·쌍 비교·파일 검증을 합해 **최대 600 s의 활성 wall time**이다. 기존 진단·분석 내부 시간 약 306 s를 근거로 한 유한 작업 배정이며 물리 정확도의 기준이 아니다. 60 s 이하의 작업 묶음으로 진행하고 경계에서 협력적 deadline을 확인한다. 실패·재시도 시간도 같은 배정에서 차감한다.

새 IVP와 과거 IVP 재실행은 모두 0이다. 실행 진입점에 ODE 호출 금지 guard를 둔다. source/input identity 불일치, schema 손실, 보존량·에너지 소유권 오류, mask/gate 변경 또는 배정 소진 시 그 상태와 원인을 기록하고 해당 후보의 검증을 멈춘다. 이때 과거 결과를 덮어쓰거나 검사를 생략해 성공으로 만들지 않는다.

완료물은 입력 manifest, 새 diagnostic 모듈, 실제 benchmark command와 환경, 동일 상태 차이 배열, nested-grid 차이 배열, gate/support 비교, 단계별 timing과 호출 수, 독립 검토 기록이다. 읽기 비교와 실제 후보 실행의 상태를 각각 표시한다. 본 제안 작성 시점의 후보 실행 상태는 `NOT_RUN`이다.

## 6. 계속 남는 물리적 소유권과 후속 연구

실행 단순화의 성공은 아래 물리적 계약을 완성하지 않는다. 각각 실제로 확장할 때 별도의 source contract를 만든다.

### 6.1 실제 grey 광자의 recoil·induced 항

`actual_hot`은 현재 photon energy monopole가 정하는 leading hot-electron 항을 사용한다. 일반 recoil과 stimulated Compton 항에는 grey 에너지·수 monopole만으로 정해지지 않는 스펙트럼 또는 occupation의 추가 정보가 필요하다. $T_{\rm ref}=2.7255/a$와 $a_R T_{\rm ref}^4$는 독립적으로 선택한 Planck reference의 소유물이다. 실제 anisotropic 광자가 그 분포를 가진다고 해석하지 않는다.

후속 물리 단위는 선택할 occupation 또는 최소 spectral moments, angular dependence와 closure, Thomson/nonrelativistic 유효 범위, 극한·평형 검사와 source identity를 먼저 명시한다. 실제 grey 자료로 식별되는 항과 모델로 보충한 항을 구분한다. 이번 두 가지의 차이는 실제 스펙트럼 불확실성의 일반적인 상한이 아니다.

### 6.2 bath 장부와 동적 역반응

현 계산은 full63의 opacity 반응을 포함하지만 Compton 에너지 전달의 반대 부호를 photon angular/spectral hierarchy나 Einstein 에너지에 적용하지 않는다. local transfer ledger가 닫히는 것과 동적으로 닫힌 복사·물질·중력 방정식은 서로 다른 확인이다.

현재 저장 경로에서 $\max |Q_C|/(HU_\gamma)=(5.2253\text{–}5.2723)\times10^{-7}$, x 적분은 $(3.4378\text{–}3.4740)\times10^{-7}$이다. 이는 제한된 test-fluid 계산에서의 교환 규모이다. 누락된 복사 역반응의 전역 오차 상한이나 자동 승격 조건으로 사용하지 않는다. Planck branch의 이 비율도 선택한 reference source를 actual $U_\gamma$로 정규화한 비교량이며 실제 CMB 에너지 전달을 복원한 값이 아니다.

동적 역반응을 추가하는 후속 계약은 적절한 angular/spectral collision moments, 반대 부호의 radiation energy source, Einstein source와 cosmological/anisotropic work의 일관성을 함께 유도해야 한다. 현재의 opposite bath 적분만 photon energy history로 바꾸지 않는다. 명시적인 test-fluid 제한 아래 현재 연구를 지속하는 것은 허용된다.

### 6.3 CI/CE 및 다른 원자 과정

현재 8개 새 경로의 dense1025 trapezoid 진단에서 H/He CI의 kinetic 기여는 $-(1.6199\text{–}1.6647)\times10^{-6}$ eV/baryon이며 binding 저장은 같은 크기의 양수이다. CI의 총 gas-energy 직접 전달은 0이지만, 전자 수와 입자 수를 바꾸므로 온도 방정식의 particle 항은 남는다. H I CE의 signed escape는 $-(2.3361\text{–}2.3820)\times10^{-4}$ eV/baryon, He II CE는 $-(7.9368\text{–}8.5893)\times10^{-17}$ eV/baryon이다. CI+CE의 고정 경로 logT forcing 적분은 약 −$9.9609\times10^{-5}$에서 −$1.0139\times10^{-4}$이다. **이 forcing은 새 온도 경로의 예측 변화가 아니다.**

CI 에너지의 support는 총 1024개 구간 중 676–680개이며, analytic continuation 또는 경계 구간에 귀속된 절대 throughput은 약 5.71–5.75%이다. H I CE는 1002–1003개 구간에서 support를 갖고, 나머지 구간의 throughput 비율은 약 $(4.27\text{–}7.55)\times10^{-7}$이다. 이 숫자는 채널별 실제 support의 중요성을 보여 준다. 여러 채널의 mask를 모두 AND한 composite 항에서는 유효한 개별 채널 기여까지 보수적인 continuation 구분에 들어갈 수 있으므로, 그 composite 비율을 전체 물리 불확실성으로 읽지 않는다.

기존 자료가 제공하지 않는 Li CI/CE와 He I CE는 unavailable 상태를 보존한다. H/D/T와 He isotope의 전자율 공유, 경험적 rate threshold와 실제 binding-energy owner의 차이, 구간 양 endpoint support 규칙도 유지한다. Li의 다른 rate table을 온도 영역 밖으로 조용히 외삽하지 않는다. free-free, charge exchange 등 현재 포함하지 않은 과정도 작은 H/He 진단만으로 일반적으로 배제하지 않는다.

이 과정들을 결합하려는 후속 단위에서는 number source $F_{\rm CI}$, $n_b I\cdot F_{\rm CI}$, kinetic loss, $\dot\eta_{\rm CI}$와 CE escape를 동시에 같은 이벤트 장부로 연결해야 한다. 현재의 작은 유한 예산은 우선순위 근거이며 모든 미래 경로에 대한 무시 가능성 증명이 아니다.

### 6.4 현재 상태의 유지

full63의 정확한 zero neutron/tritium은 선택된 원자 네트워크와 초기 상태의 계약이다. 실제 우주에서 핵 생성이 0이라는 주장이 아니다. 별도 REI 핵반응망은 수입하지 않는다. 기존 `physical=HOLD`, `production=NOT_APPROVED`, `global_convergence=NOT_RUN`, `REI_activation=false`, `U5=closed/HOLD` 상태를 실행 성능 개선만으로 변경하지 않는다.

## 7. 코드·문헌의 근거와 독립 검토

후속 구현이 읽을 현재 경로는 [driver](code/run_compton.py), [Compton adapter](code/compton_system.py), [analysis](code/analyze_compton.py), [collision helper](code/analyze_collisions.py)이다. 현재 SHA-256은 각각 다음과 같다.

```text
run_compton.py       e81220564d303467c08b1162dcd9bea8a365c8d689c64b00aeaac7378e0511b9
compton_system.py    1035690890e2665769e1692e81d49d4209366291b1c8f2345f973818678f9ae9
analyze_compton.py   00b187504eaa9da8cbe43287339b4b71b276936dff9e7542b3f29d5405147ffc
analyze_collisions.py acd7a1ed448d282cc4b102ecfd6d2043611caa3dfa480913e105c073ba0969a1
```

복사 source의 식·단위·상수·한계는 [현재 이론](THEORY_KO.md)과 [Compton provenance](provenance/COMPTON_SOURCES.json), 충돌 source의 계수·지원 구간은 [이전 source 자료](../rec_thermal_omitted_budget_20261022/data/HG97_COLLISIONAL_SOURCE.json)를 재사용한다. 원문 근거는 [Scott–Moss 0902.3438v2](https://arxiv.org/abs/0902.3438v2), [Sazonov–Sunyaev astro-ph/9910280v3](https://arxiv.org/abs/astro-ph/9910280v3), [Hui–Gnedin astro-ph/9612232](https://arxiv.org/abs/astro-ph/9612232)이며, 이번 실행 비용 제안을 위해 출처 검색을 새로 반복하지 않았다.

현재 이론의 Wolfram receipt는 경고가 동반된 대수 확인이다. 성능 제안이 그 이력을 경고 없는 CAS 증명으로 바꾸지 않는다. 후속 독립 검토자는 실제 새 후보의 수치·mask·장부와 실행 증거를 확인하고 자기 판정을 별도 기록한다. 제안 작성자나 후보 구현자의 자체 검사를 독립 검토로 표기하지 않는다.
