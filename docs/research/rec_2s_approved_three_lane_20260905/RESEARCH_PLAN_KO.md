# 승인된 2s 단일 복사장·두 광자 연구와 다음 한 비교

## 승인과 증거의 경계

사용자는 `/approve REC_2S_FULL_BOSE_SINGLE_FIELD_TWO_LEG_RESEARCH`를 명시했다. 원본 HyRec는 비교 기준으로 보존하고, 비평형 연구는 기존 완전한 Bose 쌍식을 하나의 광자 분포에 적용한다. 모델 선택을 다시 묻지 않는다. 이 승인은 물리 입력 인증, 실제 목표 격자·B·mu·각도 kernel, 생산 기본값, provider, merge를 승인하지 않는다. 과거 O1–O6 JSON은 수정하지 않고 OWNER_DECISION.json을 연구 선택의 추가 기록으로 사용한다.

PR #67의 기존 22개 항등식과 5개 테스트는 재실행 대상이 아니다. 최신 PR #68은 원본 구성원 조사와 조건부 O1 연구를 이미 실행했다. 기준은 완료 문서 commit `708a9b419a193713240ff3aaa674e6e612ddfb2b`, tree `b6bab967316518f48d3da9b7f192ff03241fd61f`다. 그 문서가 기록하는 실제 실행 source는 `6158bbf26f9f4aaccdb90c7c0c7bddaaaabe77fd`다. 이 인계문에서 그 과거 검산을 새 실행으로 합산하지 않는다.

## 다음 작업을 바꾸는 새 자료

기존 보관본에 `HyRec/two_photon_tables_hires.dat`가 있다. PR #68의 읽기 결과는 103017 bytes 및 SHA-256 `db201c729a38c7919172cf080c8ba44cdf8e6b131a6eaa8adcbc9e58fd4d0c93`를 기록한다. `HyRec/hyrec_params.h:68`에 관련 주석 설정이 있다. 아직 고해상도 표의 계수·정규화·동일 함수 응답 비교는 완료되지 않았다.

원본 ZIP: `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.

기본 표 SHA-256: `93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9`.

이 기록은 기존 원격 실행의 출처다. 현재 대화에서는 ZIP을 다시 추출하거나 해시하지 않았다. 고해상도 행 수·NSUBLYA·구간 경계는 아직 추정해서 쓰지 않는다.

## 단일 목표

`REC_2S_BASE_HIRES_SINGLE_FIELD_RESPONSE_RESEARCH`

두 원본 표 각각의 설정·정규화·채널 의미를 확인한 뒤, 동일한 양의 스칼라 복사장 함수와 동일 population을 각 표의 고유한 중심점에서 평가한다. 두 표를 같은 격자로 보간하지 않는다. 새 물리 map이나 photon-cell measure는 필요하지 않다. 이것은 고정된 두 이산 전이율 측도의 반응 비교이며 시간 진화나 연속 커널 복원이 아니다.

기본 loader는 NVIRT/NSUBLYA와 기본 member/hash가 고정되어 있다. 고해상도 자료를 311행 형식에 억지로 넣거나 상수를 변경하지 않는다. 원본 header/readme와 reader를 읽고 별도의 작은 연구용 파서를 작성한다. 기본 파서 결과는 기존 loader와 대조하고, 고해상도 설정은 원본 근거가 확인된 범위까지만 적용한다. 설정이나 정규화가 불명확하면 그 항목을 미결정으로 반환하되 행 수를 추측하지 않는다.

## 수학적 계약 — 직접 유도, 아직 새 실행 검증 없음

고정 에너지·스칼라·비편광 2s 채널에서 E_t+E_c=E21, E_t>E21/2다. r은 기본/고해상도 표를 가리킨다. 두 에너지 값은 같은 함수 f에서 읽는다.

Gamma_(r,b) = a_(r,b) [x_u(1+f(E_c))(1+f(E_t)) - x_g f(E_c)f(E_t)].

계수 a는 원본에서 정규화 근거가 확인된 구간 적분 전이율이며 단위는 s^-1다. Gamma는 H당 s^-1다. 원본의 C_b,D_b를 bare a 대신 넣지 않는다. 생산 식은 기존 PhysicalTwoPhotonRamanBin을 호출하며 연구 기준식만 독립적으로 계산한다.

무차원 시험함수 phi와 u=E/E21에 대한 두 광자 약형은 다음이다.

J_r[phi] = sum_b Gamma_(r,b) [phi(u_t)+phi(u_c)].
S_r = sum_b Gamma_(r,b).

따라서 J_r[1]=2 S_r, J_r[u]=S_r, 실제 광자 에너지율은 E21 S_r다. 원자 상위준위 변화율은 -S_r, 바닥준위 변화율은 +S_r다. 이 회계는 각도별 운동량 교환·반동·우주 팽창을 포함하지 않는다.

### 총합만 맞으면 잘못된 확신을 줄 수 있다

두 표를 같은 8.2206 s^-1 합으로 정규화하는 것이 원본 설정으로 확인된다면, 상수 시험함수의 일치는 정규화로 강제된다. 또한 J[1]과 J[u]는 같은 S에 대수적으로 종속된다. 이를 서로 독립인 세 해상도 검증으로 세지 않는다. phi=u^2와 국소화된 시험함수도 필요하다. 두 광자 약형은 phi(u)+phi(1-u)를 보기 때문에 반사된 두 창 함수만으로 독립 정보를 늘렸다고 주장하지 않는다.

### 고정 제조 복사장 묶음

실제 우주론 입력이 아닌 제조 예제를 비교 전에 고정한다.

lambda = E21/(k_B T) in {2,8,32}; alpha in {-1/8,0,1/8}.
u = E/E21; g(u)=u(1-u).
f_alpha(E) = 1/expm1(lambda*u + alpha*g(u)).
x_g=1/2; x_u=x_g*exp(-lambda).

fsR=meR=1은 이 제조 진단의 기준 상수 선택일 뿐 생산 우주론 파라미터가 아니다. 원본 eV를 기존 SI 변환으로 바꾸고, 주파수 API에는 nu=E_J/h, h=2*pi*hbar를 사용한다. 자연단위를 암묵적으로 적용하지 않는다.

0<u<1에서 지수는 u[lambda+alpha(1-u)]>0이므로 f>=0이다. 두 다리는 반드시 같은 alpha·lambda·함수 정의를 공유한다. alpha=0은 Planck/LTE control이고, alpha!=0은 같은 하나의 분포의 비평형 변형이다.

z_t=lambda*u_t+alpha*g(u_t), z_c=lambda*u_c+alpha*g(u_c)를 사용하면

Gamma = a*x_g*f_c*f_t*expm1(alpha*(g(u_c)+g(u_t))).

이는 위 쌍식의 독립적으로 유도한 소거안정 기준형이며 생산 코드 대체가 아니다. alpha=0에서 Gamma=0이다. alpha 미분은 df/dalpha=-g*f*(1+f)를 기존 JVP API에 전달하고, 두 다리의 연쇄법칙을 함께 적용한다. LTE control에서

dGamma/dalpha = a*x_g*n_c*n_t*(g(u_c)+g(u_t))

로 환원된다. 이 방향 미분은 온도·에너지·population을 고정한 alpha 방향이며 LTE manifold를 따라 움직이는 미분과 다르다.

시험함수는 phi in {1,u,u^2,exp(-((u-3/4)/(1/32))^2)}로 고정한다. lambda/alpha/창 폭을 결과를 보고 조정하지 않는다. 필요가 발견된 추가 실험은 별도 후속으로 남긴다.

## 실행 전 고정할 판정 규칙

1. 기본/hires 설정과 단위가 동일한 비교 의미를 갖는지 먼저 확인한다. 서로 다르면 정규화 차이와 해상도 차이를 섞지 않는다.
2. 80자리와 120자리 기준을 대조하고 입력의 십진 토큰 불확실성과 계산 반올림을 구별한다. 기존 binary64 API는 그 실제 입력을 정확히 고정한 별도 기준과 비교한다.
3. 정·역반응 상쇄 때문에 순률로만 나눈 상대오차를 사용하지 않는다. A_plus=a*x_u*(1+f_c)*(1+f_t), A_minus=a*x_g*f_c*f_t를 별도 보존하고, 양의 척도 sum_b(A_plus+A_minus)와 절대 잔차를 함께 보고한다. 척도가 0이면 상대량을 null로 남긴다.
4. 기본-hires 차이의 작음을 성공 조건으로 정하지 않는다. 큰 차이도 유효한 연구 결과다. 두 해상도 비교는 연속 수렴 차수·상한의 증명이 아니다.
5. phi=1,u의 회계 항등식, alpha=0 소거, alpha JVP의 독립 대조를 수행한다. 기존 식의 오류를 관측하면 근거를 보존하고 이번 문서 연구에서 production을 고치지 않는다.
6. 원시 A2s 합·정규화 계수·정규화 후 합을 둘 다 보고한다. 합을 맞춘 뒤에만 비교하여 원래 정규화 불일치를 숨기지 않는다.
7. 읽기 전용 보조 검증 한 번과 필요한 표적 수정 한 번 뒤 checkpoint한다. 결과를 안정적으로 해석할 수 있으면 추가 gate를 만들지 않는다.

## 삼분할 책임과 반환

대화 스레드: 승인·모델 의미·주장 범위·다음 한 작업. 계산한 적 없는 값을 PASS로 세지 않는다.

작업 스레드: 최신 source 조사, 허용 경로 고정, local Codex 인계, 반환 bundle/manifest/실행 근거 검토, 단일 원격 작성자로 게시·Atlassian append. 장시간 CAS 실행을 흉내 내거나 local 결과를 중복 재생하지 않는다.

local Codex: 기존 수학 환경과 격리 worktree에서 작은 연구 검산기를 작성·실행한다. 실행 소스 commit을 고정하고 로그·수치·그림·실패·환경 버전을 원본으로 보존한다. 원격 push/merge/Atlassian 수정이나 모델 재선택은 하지 않는다. 로컬 source commit/bundle은 허용한다.

다른 스레드나 Codex로 자동 전달되었다고 주장하지 않는다. 실제 전달은 사용자가 고정 인계문을 실행할 때 시작된다.

## 출처와 현재 실행 상태

원본 수치 이산화의 문헌: Ali-Haimoud와 Hirata, arXiv:1011.3758v2, 인쇄 13쪽, V A 식 (66)-(67). 대화에서 PDF 페이지를 확인했다. 이 문헌은 별도 October-2012 hires 파일의 정확한 값·설정을 인증하지 않는다.

저장소 근거: PR #65 원본 2s 추적, PR #67 O2/O3 비교, PR #68 ARCHIVE_INVENTORY_READBACK.json 및 CLOSEOUT_KO.md. 이전 검증을 이 문서의 새 수치 실행으로 표시하지 않는다.

이번 대화의 container/Python은 각각 시작 전 ClientError, Wolfram 연결은 평가 전 HTTP404였다. 새 수치 검사·그림·로컬 파일·package availability PASS는 없다. 사용자는 local의 수학 패키지가 갖춰졌다고 명시했으므로 재설치를 기본 작업으로 넣지 않는다. SciSpace 검색은 원문 탐색에만 사용했다.

한계: B,mu,실제 field/population,개별 적분구간,각도·편광 kernel,연속 수렴,provider,생산 연결은 미승인/미인증 상태다. NO_PASS_REC_PHYSICAL_SPLIT.
