# 기본/hires 단일 복사장 응답 연구 완료

`PASS_BOUNDED_BASE_HIRES_SINGLE_FIELD_RESPONSE_RESEARCH`

`NO_PASS_REC_PHYSICAL_SPLIT`

고정 9개 제조 복사장과 네 시험함수 비교를 모두 완료했다. 두 표는 다른 이산
전이율 측도이며 이번 결과는 연속 수렴·hires 정답·물리 입력 인증을 뜻하지 않는다.

## 실행 source와 결과 자식

| 역할 | commit | tree |
|---|---|---|
| 전달 부모 | f27b1ee0d6189ac49ccabe7c22db29bfa8da61ed | fae19f554a75daef1aa52ad022b9a512c1701ecd |
| Python 비교·새 pytest·초기 Wolfram 실제 실행 source | e6506c2434a9063d4e4a0a6a26c06aef7832ce52 | ce8ceb57d92ba9726b209cc7c48d328d6fb7ecb4 |
| Wolfram 저장만 수정한 재실행 source | 27cccfc94196583363a956ddf37bafce57873639 | 568c617a25a2a1e79ae3ceacb9db0aaa3e65b27c |

결과 commit/tree는 반환 ZIP의 RETURN_IDENTITY.json에 기록한다. 이 문서·결과
자식은 Python 수치 재실행이 아니다. RESULT.json은 원본 실행 JSON에 완료
메타데이터를 붙인 사본이며, 원본 bytes/hash는 ZIP의 execution/output/RESULT.json에
보존한다. source/test/archive 및 기존 승인·과거 증거는 그대로 유지했다.

## 원본 설정과 정규화

원본 ZIP 및 실제 사용한 6개 구성원의 SHA-256을 검증했다. 전체 구성원 census는
실행하지 않았다. header 기본/주석 설정, hydrogen.c:276–290, hydrogen.h:38 및
원본 readme를 대조했다. C reader는 두 설정에 같은 NSUBLYA 구간 정규화를 적용한다.

| 항목 | 기본 | hires |
|---|---:|---:|
| NVIRT / NSUBLYA | 311 / 140 | 1493 / 408 |
| 원시 2s 합 (십진 토큰, s^-1) | 8.2245807524349 | 8.224707551416 |
| 정규화 인자 (binary64) | 0.9995159932700859 | 0.9995005838942814 |
| 정규화 후 합 (NumPy, s^-1) | 8.2206 | 8.2206 |

기본 parser와 기존 loader의 전체 에너지·4채널 계수는 정확히 대응했다. hires를
기본 loader shape에 넣지 않았다. 표 고유한 에너지점에서 동일 f를 두 다리에
평가했으며 보간·padding·개별 DeltaE 추정을 하지 않았다. hires fsum 정규화 합은
8.220599999999997이다. 이는 float 합산 차이이며 별도 과학 실패로 확대하지 않는다.

## 실제 비교 결과

9사례 × 2표 × raw/normalized = 36개 조합. S를 포함한 응답 180행,
80/120자리 기준 360행, 기존 API bin 평가 9,864행, 기본/hires 차이 90행을 보존했다.
`RESPONSES.csv`에 S·네 약형·alpha JVP·정/역률·소거율·고정밀 잔차가 있다.
`BIN_API_INPUTS_OUTPUTS.csv`는 실제 binary64 API 입력과 두 광자 기여를 보존한다.

기본/hires 양의 비교 척도는 같은 시험함수의 두 표 정·역률 합의 산술평균이다.
순률이 0인 LTE에서 순률 상대오차를 만들지 않았다. 모든 차이를 결과 크기와 무관하게
보존했으며 작은 차이를 합격 조건으로 삼지 않았다.

| 관측량 | raw | normalized |
|---|---:|---:|
| 최대 절대 응답 차이 (H당 s^-1) | 2.39895708564e-6 | 1.16052807885e-6 |
| 최대 응답 차이 / 평균 양의 척도 | 2.55277004329e-6 | 2.19179714522e-6 |
| 최대 alpha JVP 차이 / 평균 양의 척도 | 2.11050678733e-5 | 1.81488636849e-5 |

최대 scaled 차이는 lambda=32, alpha=-1/8, 국소 창에서 나타났다. 최대 절대 차이는
raw에서 lambda=2, alpha=-1/8, phi=1이고 normalized에서 같은 사례의 phi=u^2다.
정규화가 모든 시험함수·복사장의 차이를 단조롭게 줄이지 않는다. S의 최대 scaled
차이는 raw 6.17684e-7에서 normalized 9.77138e-7로 증가했다.

## 검증과 수치적 한계

새 pytest 7개가 통과했다. 새 SymPy 항등식 8개와 같은 항등식의 Wolfram 확인이
모두 0이었다. 이 둘을 독립 명제 16개로 세지 않는다. 수치 checker의 2,817개 검사
레코드는 모두 통과했으며 독립 과학 명제 2,817개를 뜻하지 않는다. 과거 검사 수는
합산하지 않았다.

기존 API와 정확한 binary64 입력을 올린 120자리 기준의 최대 합계 scaled 잔차는
값 6.49332489179e-17, alpha JVP 1.00666734530e-16이다. 80/120자리 모든 보존 기준량의
최대 scaled 차이는 4.23344849437e-80이다. 이는 산술 roundoff 검사이며 표의 십진 토큰
불확실도나 연속 오차 경계가 아니다. 토큰 경로와 API 입력 경로를 분리했다.

alpha=0의 십진 제조 기준값은 정확히 0이며 alpha 방향 미분은 양수다. binary64 API
LTE 순률의 최대 양의 척도 비는 6.47172079386e-16이다. J[1]=2S, J[u]=S 및 원자·광자
에너지 회계가 확인되었지만 이 둘은 종속된 회계식이지 독립적인 분해능 검증이 아니다.

## 실행 환경·실패·검토

실제 Python은 /home/cosmosapjw/cosmo_lab/.venv/bin/python (Python 3.12.3,
실제 binary /usr/bin/python3.12)이다. NumPy 2.3.5, SymPy 1.14.0, mpmath 1.3.0,
SciPy 1.18.0, Matplotlib 3.11.0, pytest 9.1.1을 실제 사용했다. 경로는 ENVIRONMENT.json에 있다.
기존 rec_bianchi/.venv에는 이 패키지가 없어 그 관측도 반환물에 보존했다.
설치·업그레이드·재활성화는 하지 않았다.

Wolfram은 /opt/Wolfram/WolframEngine/15.0/Executables/WolframKernel, 15.0.0을 직접
호출했다. 첫 실행은 항등식 출력은 성공했지만 빈 $ScriptCommandLine으로 JSON Export가
실패했고 프로세스는 0으로 종료했다. 이 실패를 PASS 출력 파일로 취급하지 않았다.
읽기 전용 검토에서 같은 P1을 확인했고, $CommandLine 경로와 Export 실패 종료 처리를
한 번 수정한 뒤 한 번 재호출했다. 새 JSON 존재·파싱·passed=true·잔차 0을 확인했다.
음성 Export 경로의 추가 kernel 실행은 하지 않았다. 과거 kernel/license 작업은 종료하지 않았다.

PNG 4개를 실제 열어 확인했다. 기본/hires 응답 그림, 절대/양의 척도 차이 그림,
고정밀 산술 잔차 그림이 분리돼 있다. 시각 확인 bytes는 VISUAL_REVIEW.json에 있다.

## 반환·종료

원본 로그·실제 argv·환경·종료 코드는 Git 밖 전용 실행 경로와 반환 ZIP에 보존한다.
복원용 self-contained Git bundle 및 파일별 SHA256SUMS를 반환한다. ZIP SHA-256은
외부 sidecar로 제공한다. 복원 검증은 계산 반복 없이 Git 객체·tree 및 manifest를 확인한다.

전체 pytest, 기존 O1/O2/O3, 과거 5 pytest, 원본 C/history, Rust/JAX/BASS,
Sage/Singular/Lean/xAct는 실행하지 않았다. B·mu·물리 field/population·각도·provider는
미인증이다. 기존 checkout은 보존했으며 원격 push·PR·Atlassian 작성은 하지 않았다.

다음 한 행동은 작업 스레드가 반환물을 수령·검토하는 것이다. 이번 한 비교에서 종료한다.

포장 점검: 최초 git diff --check는 CSV의 기본 CRLF와 원문 발췌 공백 때문에 종료 2였다. Git 결과 사본만 LF/표시 공백으로 정리했고 CSV 모든 필드 동일성을 확인했다. 원본 실행 CSV·발췌·실패 로그는 ZIP execution/에 그대로 보존했다. 이는 수치 재실행이나 과학 실패가 아니다.
