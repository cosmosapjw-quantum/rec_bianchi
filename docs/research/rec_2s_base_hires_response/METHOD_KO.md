# 고정 실행 범위

부모는 f27b1ee0d6189ac49ccabe7c22db29bfa8da61ed이며 변경 경로는 이 디렉터리뿐이다.
CASES.json의 9사례와 네 시험함수를 raw/normalized 기본·hires 표에 모두 적용한다.
S는 사건률, J는 두 광자의 약형이며 단위는 H당 s^-1이다. E21*J[u]는 H당 J/s다.
alpha 방향에서 에너지·온도·population·계수는 고정된다. fsR=meR=1, 통계가중치비=1은 제조 진단이다.

기본 loader를 그대로 사용한다. 별도 연구 parser는 각 행의 5열을 검증하고
원본 header의 기본/주석 hires 설정으로 shape를 확인한다. 2s 두 광자 구간은
각 설정의 첫 NSUBLYA행이다. 행 보간, padding, DeltaE 추정은 없다.
원본 read_twog_params의 공통 정규화를 사용하지만 C의 순차 합과 NumPy 합의
bitwise 일치를 주장하지 않는다. 기존 loader와 연구 parser의 기본 표 대응은 검사한다.

두 독립 기준 경로를 명시적으로 구분한다.

1. API-input-exact: 실제 API에 전달된 binary64 계수, population, 두 점유수와
   두 alpha 방향을 정확한 유리수 값으로 mpmath에 올려 scalar Bose식과 독립
   곱미분을 계산한다. 약형 가중치도 실제 float 입력으로 고정한다.
2. decimal-tokens: 원본 에너지·계수 및 hydrogen.h 상수의 십진 토큰으로
   보완 에너지를 정확히 구성한다. 같은 f를 두 다리에 평가하고
   a*xg*fc*ft*expm1(alpha*(gc+gt))와 그 미분으로 합한다.
   raw 정규화 인자는 이 토큰들의 고정밀 합에서 계산한다.

각 경로를 80/120자리로 계산한다. 두 경로 사이 차이는 table 정확도나 token
불확실도의 추정값이 아니다. float 변환·상수·population·함수 평가·정규화
반올림이 함께 들어가는 표현 차이다. 고정밀 decimal 결과도 원본 표의 유효숫자를
늘리거나 hires를 연속 해로 인증하지 않는다.

수치 검증 budget은 실행 전에 CASES.json에 고정한다. 값은 정·역률 합,
JVP는 네 곱미분 항 절댓값 합으로 나누며 순률로 나누지 않는다.
기본/hires 차이에는 합격 tolerance를 두지 않는다. alpha=0에서 exact 제조
기준은 0이지만 binary64 API 입력은 완전한 LTE 관계에서 반올림만큼 벗어날 수 있다.
J[1]=2S와 J[u]=S는 종속 회계 검사이고 독립적인 세 분해능 검증이 아니다.

허용된 검증은 새 parser 음성 사례, 고정된 새 alpha/약형 대수, 기존 API를
호출하는 전체 9사례 비교와 독립 scalar 기준이다. 기존 O1/O2/O3 checker,
그때의 5 pytest, 전체 suite, 원본 C/history, Rust/JAX/BASS는 실행하지 않는다.
읽기 전용 검토 한 번과 필요한 표적 수정 한 번을 상한으로 한다.

실행 source를 먼저 commit하고 그 commit/tree를 RESULT.json에 기록한다.
수치 실행은 Git 밖 출력 디렉터리에 쓰고 완료된 결과만 이 디렉터리에 복사한다.
결과 commit은 문서/결과 자식이며 이를 재실행 commit이라 부르지 않는다.
주장 상한은 PASS_BOUNDED_BASE_HIRES_SINGLE_FIELD_RESPONSE_RESEARCH 및
NO_PASS_REC_PHYSICAL_SPLIT. B·mu·물리 입력·각도·provider·연속 수렴은 미인증이다.
