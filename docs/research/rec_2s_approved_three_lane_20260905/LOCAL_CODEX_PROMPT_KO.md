# local Codex 실행 인계 — 기본/hires 단일 복사장 응답

## 이번 작업

저장소 cosmosapjw-quantum/rec_bianchi에서 기존 수학 환경을 사용해 `REC_2S_BASE_HIRES_SINGLE_FIELD_RESPONSE_RESEARCH` 하나를 실행한다. 사용자 승인 `/approve REC_2S_FULL_BOSE_SINGLE_FIELD_TWO_LEG_RESEARCH`는 연구 경로 선택이다. production, B·mu·목표 격자·각도 kernel, 물리 입력 인증, provider는 승인하지 않는다.

운영자 위치 후보는 `$HOME/Dropbox/bianchi/rec_bianchi`다. 그 checkout의 dirty/untracked 파일을 삭제·stash·reset하지 않는다. 작업 스레드가 전달한 DELIVERY_SHA에서 별도 worktree를 만들고, 이 인계문 및 OWNER_DECISION.json이 그 exact commit에 포함되는지 확인한다. 인계의 고정 source 부모는 `708a9b419a193713240ff3aaa674e6e612ddfb2b` / tree `b6bab967316518f48d3da9b7f192ff03241fd61f`다. PR67까지 되돌아가 PR68 결과를 잃지 않는다.

실행 소스 작성·로컬 commit·bundle 생성은 가능하지만 원격 push/PR/Atlassian 쓰기는 작업 스레드의 책임이다. 같은 원격 branch에 두 작성자를 만들지 않는다.

## 범위와 필수 읽기

AGENTS.md, docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md, 이 인계와 같은 디렉터리의 RESEARCH_PLAN_KO.md와 OWNER_DECISION.json을 읽는다. 다음 실제 소스를 읽고 기존 코드를 재사용한다.

- src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py
- docs/research/original_hyrec_2s_input_trace/PROVENANCE.json
- docs/research/original_hyrec_2s_input_trace/SOURCE_EXCERPTS.txt
- docs/research/rec_2s_o2o3_comparison/RESULTS.json
- docs/research/rec_2s_o1_identifiability/ARCHIVE_INVENTORY_READBACK.json
- docs/research/rec_2s_o1_identifiability/CLOSEOUT_KO.md

root HANDOFF_PROMPT.md의 옛 REC-NEXT-03 전체검증은 이번 실행 대상이 아니다. 기존 140행 census, 원본 C/history, O2/O3 22개 항등식, 5개 pytest, O1 전체 구성원 조사를 반복하지 않는다.

새 소스/결과는 `docs/research/rec_2s_base_hires_response/` 아래만 둔다. 실행 로그·캐시·임시 출력은 Git 밖 전용 경로에 둔다. src/tests/archive, 원본 표, 과거 evidence와 owner JSON을 수정하지 않는다.

## 입력 무결성과 설정

archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip
SHA256 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27

HyRec/two_photon_tables.dat
SHA256 93d23871e21c40f5b72a6ef9acf3eb7be054735c8aee9401e455736c1d9d8cf9

HyRec/two_photon_tables_hires.dat
SHA256 db201c729a38c7919172cf080c8ba44cdf8e6b131a6eaa8adcbc9e58fd4d0c93

HyRec/hyrec_params.h
SHA256 cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2

사용할 bytes만 직접 읽고 검증한다. 전체 archive census를 재생하지 않는다. hyrec_params.h의 기본 설정과 주석 처리된 hires 설정, hydrogen.c의 read_twog_params, 원본 readme의 관련 설명을 대조한다. 파일명만으로 hires 행 수·NSUBLYA·정규화법을 단정하지 않는다. 이 설정이 source로 확인되지 않으면 미결정으로 기록하고 비교 가능 범위를 좁힌다.

기본값은 기존 OriginalHyRecTwoPhotonRamanTable로 읽는다. 고정 기본 loader의 NVIRT/NSUBLYA/member/hash를 바꾸지 않는다. hires용 연구 파서는 필요한 최소한만 새 연구 디렉터리에 작성하고, 기본 표에서 같은 파서와 기존 loader의 대응을 확인한다. 지원되지 않는 shape를 reshape나 padding으로 맞추지 않는다.

두 표의 원시 계수 합·정규화 인자·정규화 후 합을 각각 보존한다. 원본에 8.2206 s^-1로 맞추는 근거가 확인된 범위에만 그 정규화를 적용한다. 기본/hires에서 처리법이 다르면 서로 같다고 두지 않는다. per-bin DeltaE는 추정하지 않는다.

## 비교할 함수와 수치량

RESEARCH_PLAN_KO.md의 9개 제조 복사장과 네 시험함수를 그대로 사용한다. lambda in {2,8,32}, alpha in {-1/8,0,1/8}, u=E/E21, g=u(1-u), f=1/expm1(lambda*u+alpha*g), xg=1/2, xu=xg*exp(-lambda)다. 각 table의 실제 Et와 Ec=E21-Et에서 같은 f를 평가한다. 서로 다른 grid를 보간해서 맞추지 않는다.

fsR=meR=1은 제조 진단용이며 실제 우주론 선택이 아니다. SI 에너지/주파수 변환은 기존 constant를 확인해 사용하고 nu=E_J/h를 지킨다. 반응은 기존 PhysicalTwoPhotonRamanBin의 실제 평가와 jvp에 위임한다. 독립 기준 계산은 별도 scalar 합/고정밀 계산이어야 한다.

각 해상도별로 S=sum Gamma, J[phi]=sum Gamma*(phi(ut)+phi(uc)), alpha JVP를 계산한다. phi=1,u,u^2,exp(-((u-3/4)/(1/32))^2)다. J[1]=2S, J[u]=S는 회계 검사이며 독립 분해능 검증으로 합산하지 않는다.

alpha 미분은 df/dalpha=-g*f*(1+f)를 두 다리에 넣는다. 독립 기준은 Gamma=a*xg*fc*ft*expm1(alpha*(gc+gt)) 및 그 미분이다. alpha=0의 값 소거와 alpha 방향 미분을 혼동하지 않는다. 온도·population·에너지를 움직이지 않는 방향 미분이다.

## 수학 패키지와 실행 예산

사용자는 local에 필요한 수학 패키지가 갖춰져 있다고 밝혔다. 설치/업그레이드/재활성화를 시작하지 않는다. 실제 사용하는 executable 경로·버전을 한 번 확인한다. Mathematica/Wolfram은 로컬 kernel을 직접 사용하며 실패한 ChatGPT MCP 연결을 되풀이하지 않는다. 기존 kernel/license 작업을 종료하지 않는다.

주 계산: Python/NumPy와 기존 module, 독립 SymPy 대수, mpmath 80자리/120자리 합.
보완: 로컬 Wolfram으로 신규 약형/alpha 미분 항등식 확인. Sage/Singular 또는 Lean/mathlib는 이미 준비된 환경에서 다른 독립 증거가 꼭 필요할 때 한 번만 사용한다. 모든 패키지를 의무적으로 돌리는 설치·검증 경쟁을 만들지 않는다. xAct 기하 계산은 이번 스칼라 문제에 필요 없다.

선택 도구의 실제 호출 실패는 별도로 기록하고, 주어진 정확한 유리수/고정밀 경로가 실행되면 계속 진행한다. 한 종류의 실패를 반복해 작업 전체를 잃지 않는다. 새 source를 실행 전에 commit하고 실제 tested commit/tree를 기록한다.

## 최소 검증과 판정

1. 기본 table 연구 parser와 기존 loader의 대응, hires 설정/정규화 source 근거.
2. 같은 f 정의·population·constants가 두 표와 두 다리에 사용됨.
3. 기존 paired API와 독립 고정밀 기준의 값/alpha JVP 대조.
4. 두 광자 number/energy 회계, alpha=0의 full Bose null.
5. raw/normalized response 모두 보존; 절대 차이와 양의 정·역률 척도로 나눈 차이, 소거율을 함께 보고.
6. alpha!=0 및 phi=u^2/국소 창 응답을 비교. 순률=0에서 상대값을 억지로 만들지 않음.
7. 80/120자리 재계산으로 reference roundoff 규모를 확인하고 기존 float 입력과 원본 십진 토큰 경로를 혼동하지 않음.
8. 기본/hires 차이에 합격 tolerance를 사후 설정하지 않음. 두 점으로 수렴 차수나 연속 상한을 주장하지 않음.
9. raw source/output identities, 코드 불변 경로, 실제 사용한 데이터의 해시를 보존.

새 함수 테스트와 계획서에 직접 영향을 받는 기존 함수만 검증한다. 전체 repository suite, Rust/JAX/BASS build, native history는 실행하지 않는다. 결과가 크거나 기대한 단조성을 보이지 않아도 숨기거나 map/계수를 조정하지 않는다.

## 그림과 반환물

수치 CSV와 절대/정·역률 척도 차이를 보여주는 작은 그림을 만든다. 기본/hires 곡선이 다르다는 사실과 고정밀 reference 잔차를 서로 다른 그림으로 분리한다. 물리량·단위·기본/hires 설정을 표시한다. 실제 PNG를 열어 확인하고 열지 못하면 미수행으로 기록한다.

반환: CHECKPOINT_KO.md, RESULT.json, 고정 CASES.json, 실행된 연구 checker, raw logs, 수치 CSV, PNG, SHA256SUMS, 실제 tested source를 복원할 Git bundle. 검사 항목 수는 실제 관측한 값만 쓴다. 과거 125개/22개/15개 증거를 이번 수에 합산하지 않는다. 반례/실패도 함께 보존한다.

로컬 문서 child를 수치 재실행으로 표시하지 않는다. 작업 스레드가 확인할 수 있도록 부모/실행 source/결과 commit을 나누고, 자체 commit hash를 같은 파일 안에 순환해서 넣지 않는다. source와 결과를 작업 스레드에 반환하고 원격 게시 없이 종료한다.

완료 분류는 PASS_BOUNDED_BASE_HIRES_SINGLE_FIELD_RESPONSE_RESEARCH 또는 실제 blocker다. 물리 입력·B·mu·각도·provider·연속 수렴은 미인증이며 NO_PASS_REC_PHYSICAL_SPLIT이다. 다음 모델 선택이나 생산 수정으로 자동 진행하지 않는다.
