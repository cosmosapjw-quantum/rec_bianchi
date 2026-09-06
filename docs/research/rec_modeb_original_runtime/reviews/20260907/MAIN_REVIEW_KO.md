# PR75 로컬 원본 호출 수령 검토와 읽기오차의 반응률 전달

판정: `ACCEPTED_BOUNDED_ORIGINAL_MODEB_RUNTIME_DIAGNOSTIC`.
과학적 상한: `NO_PASS_REC_PHYSICAL_SPLIT`.

## 1. 이번에 닫는 범위

주 대화가 GitHub 연결을 통해 Codex 결과 branch와 PR75를 발견하고 원본 호출의 반환문서·실행 기록·수치·수정 diff를 읽었다. 일반 PR 검색의 첫 결과에 PR75가 없었으나 결과 branch를 직접 읽어 실제 PR75를 확인했다. 따라서 검색 목록만으로 결과 미게시라고 결론내리지 않았다. 사용자에게 ZIP 재업로드를 요구하지 않았고, 같은 과학 계산을 재실행하지 않았다.

수령 source는 PR75의 `4f8284ffd59089bef5308a57d43155408ce002e1`, tree `9325fcdf9bd59735fb64d573b316fc0626a5a6b8`이다. 실제 수정 후 실행 source는 `c813bfc32b23e4d3148e3ed9318ec9276a746e0b`, tree `2fbb5562333f5e86e615a401f1a177f35f11ccbc`다. BASS 원본은 `9d1c702ddf58549a06b29965a3d1b790a0c23159`, tree `12ab5b477ff75b4fdfdb4bbc60e3864675fe0e3c`다.

원격 Git commit 객체에서 PR75 게시 commit의 첫 부모 `85a8c4632dd062ae201937c3647accd5d93f9733`와 두 번째 부모 c813bfc를 확인했다. 이는 인계와 실제 실행 source를 보존하는 결과 통합 commit이며 PR75가 main에 병합되었다는 뜻이 아니다. 수령 당시 PR75는 OPEN/DRAFT/UNMERGED다. 게시 commit을 실제 실행 source로 재명명하지 않는다.

수령 근거 디렉터리: `docs/research/rec_modeb_original_runtime/local_returns/20260906T143513Z/`.

실제로 읽은 핵심 자료는 RETURN_HANDOFF_KO.md, RETURN_IDENTITY.json, 수정 후 RESULT.json·unittest.log·PROCESS_RESULT.json·rust_run.stdout, ORDER8_OBSERVATIONS.csv, PATCH.diff, REGRESSION_RESULT.json, PUBLIC_COPY_MANIFEST.json의 정책/일부 항목이다. 원격 수정 commit 자체의 diff, PR 변경경로50개, 실제 checker의 import/컴파일/배열전달/검사 구간과 비공개 radial.rs의35–133행도 읽었다. 문서만으로 실행을 추정하지 않았다.

현재 대화의 container/Python은 각각 시작 전 ClientError였다. 따라서 전체 공개 manifest의 재해시, 원본 비공개 raw ZIP 검사, PNG 재렌더링, 독립 재실행은 하지 않았다. 로컬이 남긴 byte 검증 기록을 주 대화의 새로운 해시검사로 표시하지 않는다. 이것은 범위가 정해진 증거 검토이지 별도 제3자 독립 심사나 병합 승인도 아니다.

## 2. 원본 실행과 수리의 수용

수정 후 unittest.log는 원래 TestID8개 각각 ok, run8/failure0/error0/skip0을 기록한다. PROCESS_RESULT의 실제 종료코드는0, 경과시간은2.431564338초다. 최초 원본 실행도 같은8개를 통과했고 약5.954초였다는 실행 기록이 있다. 게시를 위한 새 실행은 없었다. 과거 독립 REC6개와 이번8개를 합쳐 새14개로 집계하지 않는다.

Rust 컴파일과 실제 binary 호출의 argv·exit0 및8개 JSON 출력이 존재한다. 검사기는 실제 rows[1]['value']를 REC net_action과 COM 입력에 사용한다. ModeBState는 실제 고정 모듈에서 생성·pack/set_from/q를 호출한다. shape carrier는 물리 구면 격자가 아니고 evolve/native sphere/full crate는 미실행이다. geometry 검사도 기호 대수이지 BASS geometry 함수 실행이 아니다.

c813bfc의 실제 Git diff는 check_original.py의 그림 블록만 변경한다(추가11/삭제2). 0 오차가 표시 하한10^-18에 놓였다는 설명·annotation·plot metadata를 추가했고, 기존8개 검사와 oracle/tolerance는 바꾸지 않았다. 공개 PATCH.diff와 실제 commit diff가 같은 변경을 나타낸다. 수령한 회귀 기록은 수치 checks와 native rows가 전후 동일함을 보고한다. 원본 RESULT의 visual_audit=NOT_PERFORMED는 유지되며, local Codex가 나중 PNG를 열었다는 별도 기록을 혼동하지 않는다. 주 대화가 PNG를 새로 열었다고 주장하지 않는다.

원래 무인증 Actions의 BASS fetch exit128는 과거 실패로 보존한다. 로컬은 실제로 고정 BASS source에 접근하여 실행했으므로 그 장벽은 이 진단을 위한 미완료 항목에서 제거한다. Actions 인증이 수리되었다거나 비공개 BASS가 공개되었다고 말하지 않는다. PR73의 과거 부분결과는 지우지 않고 이 수용 기록으로 현재 완료 상태를 추가한다.

## 3. 실제 수치: 반올림과 읽기 근사

원본2점 Rust 읽기값은 powerlaw=2, Planck=0.25819888974716115다. 그 실제 출력으로 기존 REC가 반환한 순률은0.028175416344814574 H^-1 s^-1이며, 정확한 Planck control은0, tracked partial은-0.375다. 이 부분은 더 이상 독립 폐형식을 입력한 것만의 검증이 아니다.

| n_q | f 오차(q=1) | f 오차(q=2) |
|---:|---:|---:|
|32|3.752997912442879e-12|-2.3472464712644598e-11|
|64|1.2878587085651816e-14|-8.100927336348225e-14|
|128|0.0|-2.4054832200211723e-16|

이 표는 PR75의 ORDER8_OBSERVATIONS.csv를 읽은 결과다. K=8은 반경 보간의 stencil 설정이며 각도 multipole ell=8 검증이 아니다. 실제 binary64 weights/input_y에 대한80자리 dot 기준과 고정 gamma 경계를6개 사례 모두 통과했다. 이것이 연속 Planck 함수에 대한 보간오차를0으로 만든다는 뜻은 아니다.

특히 n=128,q=1에서 exp한 f는1로 반올림되어 저장된 f 오차가0이지만, 원본 Rust 출력의 ln_value는6.44829242085753762e-17이다. 따라서 '보간 자체가 상징적으로 정확함'과 'binary64 occupation 차이가0임'을 구분한다. 그림의10^-18은 표시 하한이지 측정 오차가 아니다. n=128,q=2의 비영점 오차도 남는다. 전체8차 수렴·다른 스펙트럼·다른 방향·꼬리 영역·물리 우주론 정확도는 이번 표만으로 인증하지 않는다.

## 4. 이번에 직접 유도한 반응률 오차 전달식

제조 비교의 a=1 s^-1, xu=1/16, xg=1/2, 축퇴도비1에서

Gamma/a = [1+fc+ft-7fc*ft]/16.

정확한 Planck fc=1, ft=1/3에 대한 읽기오차를 ec,et라 하여 fc=1+ec, ft=1/3+et를 대입하면 근사 전개가 아니라 정확히

Gamma/a = -ec/12 -3et/8 -7ec*et/16.

따라서 작은 읽기오차의 일차 민감도와 교차항을 분리할 수 있다. |Gamma|/a <= |ec|/12+3|et|/8+7|ec et|/16도 직접 따른다. 이는 제조 population과 고정 에너지에만 적용한 조건부 식이다.

PR75의 n=128 오차 ec=0, et=-2.4054832200211723e-16을 이 식에 대입하면 약9.020562075079397e-17 H^-1 s^-1다. 이 스칼라 대입은 현재 대화의 계산기에서 확인했다. 이것은 기록된 읽기오차를 정확한 다항식에 넣은 후처리 값이며, 해당8점 값으로 원본 REC net_action을 새로 호출해 관측한 값이 아니다. 근평형에서 직접 F-R의 binary64 subtraction은 별도 반올림이 추가될 수 있다. 다른32/64 수치에 대한 긴 계산기 요청은 결과가 반환되지 않아 새 실행 증거로 사용하지 않았다.

결론: K=8의 지정된 매끄러운 사례에서 읽기오차는 작아지지만, generic source의 정확한 detailed-balance 보존이 자동으로 보장되지는 않는다. 반대로2점 반례를 K=8의 실제 오차라고 확대해서도 안 된다. 새로운 보간법을 채택하기 전에 현재 읽기 정확도, 반응률 상쇄, 목표 표현의 보존조건을 분리해 비교해야 한다.

## 5. 다음 연결을 위한 고정-map 방향 미분 — 직접 유도, 구현 미승인

기존 연구의 조건부 후보 chi(f)=ln(1+1/f)를 유지하되 생산 default로 선택하지 않는다. 동일 scalar field의 y_i=ln f_i에서, source 다리 s의 고정 분율 B_is를 사용한다고 가정하면

chi_s=sum_i B_is chi(f_i), f_s=1/expm1(chi_s),
dchi_s=-sum_i B_is*dy_i/(1+f_i),
df_s=f_s*(1+f_s)*sum_i B_is*dy_i/(1+f_i).

이 식은 dB=0인 경우뿐이다. 기존 log-f stencil이나 그 Jacobian의 단순 전치와 같은 연산이 아니다. f>0와 chi_s>0가 필요하고 경계에서 임의 floor를 만들지 않는다.

순사건률 Gamma=a[xu(1+fc)(1+ft)-g*xg*fc*ft]의 변화는

dGamma = [(xu(1+fc)(1+ft)-g*xg*fc*ft)]*da
+ a[(1+fc)(1+ft)*dxu-g*fc*ft*dxg
+ (xu(1+ft)-g*xg*ft)*dfc
+ (xu(1+fc)-g*xg*fc)*dft]

이며 여기서 g는 고정이다. a=0에서도 이 비나눗셈 표현을 사용할 수 있다. 두 다리의 같은 원상태 방향 dy를 모두 전달해야 한다.

고정 mu/B에서 D_ib=B_i,tb+B_i,cb라 두면

C_i=nH/mu_i*sum_b D_ib Gamma_b,
dC_i=1/mu_i*sum_b D_ib*(nH*dGamma_b+dnH*Gamma_b),
G_i=C_i/(H*f_i),
dG_i=dC_i/(H*f_i)-G_i*(dy_i+dH/H).

여기까지가 '읽는 단일 상태의 변화'부터 '같은 상태에 돌아가는 source 변화'까지의 조건부 JVP다. 이번 반환물은 이 합성 연산을 검사한 것이 아니며 새로 구현한 것도 아니다. 단위는 C_i와H가s^-1, G_i는무차원 tau당 값이고 nH/mu_i는무차원이다. 서명(-,+,+,+), 같은 수소 정지계, 고정 에너지/M/target을 가정한다. 상대 boost, moving-map/event, 수송, 실제 시간 적분은 포함하지 않는다.

다음 단일 연구는 `REC_FIXED_MAP_SINGLE_FIELD_READ_SCATTER_JVP`로 정한다. 이미 쓰던 제조2노드와 명시적인 고정 map/measure에서 이 전체 JVP를 독립 reference와 확인하고, 기존 log-f 읽기의 대조 결과를 보존한다. 실제 B·mu·원자자료·새 물리격자를 선택하는 작업이 아니고 새 photon solver를 만드는 작업도 아니다. 지금은 이 수식/범위를 고정한 상태이며 새 코드나 로컬 실행을 자동 시작하지 않았다. 현재 주 대화에서 가능한 유도·코드·실행을 우선하고, 실제 로컬 능력이 필요할 때만 Git 인계한다.

## 6. 문헌과 주장 한계

SciSpace에서 bosonic equilibrium와 보존·entropy의 구분에 관한 문헌을 검색했다. 반환된 Landau/플라즈마 논문을 이 photon 쌍반응 구현의 검증 근거로 쓰지 않았다. 직접 확인한 arXiv:1009.2748 초록은 질량·에너지 보존, entropy 불등식, 일반 Bose–Einstein 정상상태를 별도 구조로 명시한다. 전체 논문 재독이나 그 알고리즘의 채택은 아니다. 위 오류 전달식과 JVP는 현재 소스 정의에서 직접 유도한 것이며 해당 논문이 인증한 공식이라고 주장하지 않는다.

원문: https://arxiv.org/abs/1009.2748
반환 PR: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/75
실제 실행 source: https://github.com/cosmosapjw-quantum/rec_bianchi/commit/c813bfc32b23e4d3148e3ed9318ec9276a746e0b

## 7. 완료·미완료와 게시

이 검토의 완료는 PR73/74가 기다리던 고정 원본 component 호출 증거를 주 대화가 수령·검토하고 제한적으로 수용한 것이다. 과거 CI 인증 실패를 소급 바꾸지 않는다. 일반 CI의 이 결과 source 최신 로그는 이번 검토에서 읽지 않았으므로 과거 공백 실패와 동일 원인이라고 단정하지 않는다. repository-wide PASS나 merge/ready는 주장하지 않는다.

이 문서는 Codex 결과 branch를 직접 갱신하지 않고 PR75의 정확한 head 위 새 주 대화 검토 child에만 추가한다. 원본 결과49개, checker, private BASS source는 변경하지 않는다. 새 검사/호출/그림/manifest를 만들지 않았다. GitHub 기록과 REC Atlassian은 append/readback하며 공식 dependency/상태/다른 repo를 수정하지 않는다.

physical_source_authenticated=false; provider_admitted=false.
전체 BASS evolve, native sphere/각도 구적, 전체 physics split, 실제 p_star·mu·B, 연속 수렴과 분광PSTF 통합은 여전히 미완료다. `NO_PASS_REC_PHYSICAL_SPLIT`.
