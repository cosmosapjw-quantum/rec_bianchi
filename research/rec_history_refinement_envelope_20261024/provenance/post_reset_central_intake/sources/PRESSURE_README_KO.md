# 유한 양의 측도의 압력 구간과 원자 모멘트

**현재 상태: 정적 준비 완료, 실행하지 않음. 수치 admission은 발행되지 않았다.**

이 모듈은 root의 `next_pressure/THEORY_KO.md`와 `IMPLEMENTATION_CONTRACT.json`을 구현한다. 선택 HI source를 읽거나 재적분하지 않는다. 기존 L1 source, source card 및 실제 raw 결과도 변경하지 않는다.

## 변수와 조건부 해석

전자 운동에너지를 k, 같은 에너지 단위의 전자 rest energy를 M > 0이라 쓴다. 공급된 양의 유한 측도는 0 ≤ k ≤ L에 지지되고 N = ∫dν, U = ∫k dν이다. 등방적 scalar pressure moment는 Π = (1/3)∫k(k+2M)/(k+M) dν이다.

입력 측도가 Href당 입자 재고이면 U와 Π는 energy/Href다. 입력이 Href당 proper-time 주입률이면 energy/(Href s)다. 함수는 이 두 해석을 자동 변환하거나 혼합하지 않는다. 주입률 pressure moment만으로 현재 저장고의 압력을 알 수 없다.

모든 결과는 주어진 표현 입력을 갖는 양의 측도에 대한 조건부 수학적 값이다. physical uncertainty, 열화, thermal temperature, 유한 stock의 시간 진화, calibrated equation of state, Einstein coupling을 제공하지 않는다. 원자 입력은 호출자가 공급한 입력이며 qualified provider라고 주장하지 않는다.

## API

`pressure_interval.py`는 표준 라이브러리만 사용한다.

| API | 반환형과 의미 |
|---|---|
| `pressure_interval_from_moments(N, U, L, M)` | `PressureInterval`: 입력의 Fraction 표현과 sharp lower/upper, width, NR pressure, NR error upper bound |
| `pressure_moment_from_atoms(atoms, M, L)` | `AtomMoments`: `(weight, k)` iterable에서 정확한 N, U, pressure 및 M/L |

허용 숫자는 int, Fraction, 유한 float다. bool, 비수치, nonfinite, 음수 입력을 거부하며 M은 엄격히 양수여야 한다. N, U, L은 비음수이고 U ≤ N·L을 정확히 비교한다. 각 원자의 weight와 k도 비음수이고 k ≤ L이어야 한다. 잘못된 원자 pair 형태와 지원 밖 입력은 `DomainError`로 거부한다.

모든 수치 출력은 Fraction이다. float는 그 binary64 값의 정확한 표현으로 바꾸며 십진 표기를 원래의 정확한 물리 입력으로 재해석하지 않는다. tolerance나 최종 float 변환은 없다.

## 구간과 경계

N > 0일 때 구현 식은 다음과 같다.

- lower = U·(L+2M) / [3(L+M)]
- upper = U·(U+2MN) / [3(U+MN)]
- width = upper − lower
- nr_pressure = 2U/3
- nr_error_upper = U·L / [3(L+M)]

N = 0이면 domain 조건이 U = 0을 요구하고 upper의 0인 분모를 계산하지 않는다. L = 0이면 U = 0이어야 한다. U = 0인 유효 경계의 모든 pressure 결과는 0이다. M = 0은 이 경계에 포함되지 않으며 거부한다. 빈 원자 iterable은 유효한 영 측도다.

원자 route는 N = Σw, U = Σwk, pressure = (1/3)Σwk(k+2M)/(k+M)을 정확히 계산한다. 외부 원자 파일의 fetch, source qualification, quadrature 또는 단위 변환은 없다.

## 준비된 fixture

`focused_check.py`는 한 미래 fixture group으로 작성했으며 import, compile, 실행하지 않았다. root의 종이 위 기준 N=2, U=2, L=2, M=1에서 lower=8/9, upper=1을 비교하도록 준비했다. 원자 `(1,0),(1,2)`와 `(2,1)`은 각각 양 끝이고, `(1/2,0),(1/2,2),(1,1)`의 기준은 17/18이다. 이 값들은 계약에 주어진 해석적 참조이며 실행된 결과가 아니다.

별도로 작성한 원자 참조는 g(k)=k+M−M²/(k+M)을 사용한다. fixture는 영 경계, 빈 측도, U>N·L 거부, 양의 공통 weight scaling과 구간의 선형 동차성도 검사하도록 준비했다. donor 재적분, 기존 L1 실행 또는 기존 L0 suite를 호출하지 않는다.

## 미래 실행 제안과 정지 경계

`run_focused_once.py`와 `PROPOSED_EXECUTION.json`은 준비만 했으며 상태는 **NOT_AUTHORIZED**다. 별도의 새 배정 제안은 CPU soft=hard 1 s, launch-inclusive wall 5 s, 한 child, 자동 retry 0이다. 현재 L1에서 남은 배정은 전용하지 않는다. 실제 명령의 절대 경로와 source/fixture/runner SHA는 proposal에 기록했다.

parent는 candidate나 fixture를 import하지 않는다. 미래에 별도 승인된 실행이 있을 때 새 이 디렉터리의 `raw/attempt.json`을 독점 생성하며 raw stdout/stderr, CPU user/system, wall, exit, timeout, launch error를 남긴다. attempt marker는 재현성과 우발적 재실행 방지를 위한 것이며 security 또는 approval token이 아니다.

현재 새 pressure 단위의 scientific invocations는 0이다. CPU는 `NOT_MEASURED_NO_PRESSURE_SCIENCE_EXECUTION`, 수치 결과는 null이다. 요청 executor는 gpt-6.1-sol/high, 독립 관측 backend는 unknown이다. 다음 단계는 독립 읽기 전용 정적 검토이며 실행하지 않고 멈춘다.
