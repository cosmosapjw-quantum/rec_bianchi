# REC O1 연구 실행 완료 기록

## 실제 완료 범위

`PASS_BOUNDED_O1_IDENTIFIABILITY_RESEARCH_NOT_PHYSICAL_ADMISSION`

`NO_PASS_REC_PHYSICAL_SPLIT`

PR #67의 기존 O2/O3 비교는 다시 실행하지 않았다. 이 자식은 원본 보관본의 구성원 조사와 spike 자료의 식별 범위를 다루는 독립 연구다. 실제 실행에서 SymPy 항등식 15개가 모두 0이고 별도 Fraction 다항식 적분이 일치했다. 새 생산 소스나 물리 입력은 만들지 않았다.

## 정확한 실행과 게시 구분

| 역할 | commit | tree |
|---|---|---|
| 고정 부모 | dc9e9e9394eba314afa13e6db1b0811257e3be55 | a12bdda27717a9b0f7a182e86bf6c3d081087ecc |
| 실제 실행 소스 | 6158bbf26f9f4aaccdb90c7c0c7bddaaaabe77fd | 535ab51cfa18172ff970a81f97f2a95d7fe1d1d8 |

[전용 실행 33954237095, job 101274515257](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/33954237095/job/101274515257)은 정확한 push SHA를 checkout했다. 분리 환경 설치, 메모리 문법 검사, 원본 읽기, 수학 검산, 산출물 파일 해시 검사와 업로드가 모두 성공했다. 실제 소스 실행 당시 새 경로는 문서·검산기·workflow 세 개였다. 이번 완료 문서 자식은 같은 검산기나 workflow를 바꾸지 않으며, 그 문서 자식을 수치적으로 재실행했다고 주장하지 않는다. 최종 게시 commit/tree는 PR 본문과 원격 Git 객체에서 확인한다.

Python 3.12.14, SymPy 1.14.0, Matplotlib 3.10.3을 사용했다. 직접 로컬 container/Python은 시작 전 ClientError였고 WolframContext는 평가 전 MCP SSE HTTP404였다. 실패 경로를 반복하지 않고 읽기 전용 hosted 실행으로 진행했다. 사용자 Dropbox checkout은 접근하거나 변경하지 않았다.

## 정확한 수학 결과

제조 커널 k_plus/minus=1 +/- epsilon*(6x^2-6x+1)는 x in [0,1], 0<epsilon<1에서 양수다. 두 커널의 적분은1, 첫 모멘트는1/2지만 둘째 모멘트가 다르다. 제조 쌍반응 인자 F=1/4+x/2-x^2/2에 epsilon=1/2를 넣으면 다음 결과를 얻는다.

| 양 | 정확한 값 |
|---|---:|
| R_plus/A | 13/40 |
| R_minus/A | 41/120 |
| R_minus/A - R_plus/A | 1/60 |
| 공통 중심점 F(1/2) | 3/8 |
| 비중심 선형 예의 누락항 | 1/6 |

두 수학적 대안, 즉 영차·일차 자료만으로 일반 source가 결정된다는 주장과 확인되지 않은 무게중심에서 첫 모멘트 오차를 버리는 주장은 반례로 배제된다. 이것을 생산 코드에 변조를 주입해 실행한 테스트라고 부르지 않는다.

Lipschitz/C2 오차 경계는 문서의 가정하에 직접 유도했으며 위의 정확한 다항식 예에서 검산했다. 모든 연속 함수에 대한 별도 형식증명기를 실행한 것은 아니다. 실제 HyRec 커널을 역구성했거나 원본 수치 오차가1/60이라는 뜻은 전혀 아니다. 그림은 두 제조 커널의 모양을 나타낸다.

## 원본 구성원 조사에서 새로 확인한 다음 자료

ZIP과 기본 표의 고정 SHA-256이 일치했다. 디렉터리를 제외한 파일26개에 대해 이름·크기·SHA-256을 기록했다. 이 개수에는 Finder/macOS 메타데이터가 포함된다. C/header 및 지정 텍스트 확장자의 키워드 위치도 기록했다. PDF 구성원 내용 전체나 모든 생성기 가능성을 조사한 것은 아니며, 키워드 검색만으로 생성기가 어디에도 없다고 결론 내리지 않는다.

기존 보관본 안에서 다음 고해상도 표의 존재와 정확한 식별정보를 확인했다.

```text
HyRec/two_photon_tables_hires.dat
103017 bytes
db201c729a38c7919172cf080c8ba44cdf8e6b131a6eaa8adcbc9e58fd4d0c93
```

`hyrec_params.h:68`에는 이 표를 선택하는 주석 처리된 설정이 있다. 기본 표 설정은51행이다. 이번에는 고해상도 표의 행 수·정규화·계수 차이·생성규칙을 조사하지 않았다. 원본 데이터 파일을 대체하거나 기본 입력으로 선택하지 않았다.

## DAG와 주장 범위 교정

(E_b,A_b)는 이미 Q[F]=sum_b A_b F(E_b)라는 이산 연산을 정의한다. 개별 I_b를 모른다는 이유로 이 이산식을 평가하는 모든 연구까지 중지할 필요는 없다. 그러나 연속 kernel·생성규칙·오차 경계와 실제 photon cell measure는 이 두 값만으로 인증되지 않는다. 생산 photon measure와 rate measure를 혼동하지 않는다.

처음 RESEARCH_KO.md는 다음 의사결정으로 O2/O3 책임자 선택을 제시했다. 이번 구성원 조사에서 원본 고해상도 표를 직접 확인했으므로, 다음 실행 가능한 단일 연구를 **기본/고해상도 표의 원본 설정·정규화·같은 시험함수에 대한 이산 응답 비교**로 좁힌다. 이는 새 자료를 근거로 한 연구 순서 갱신이지 O2/O3 선택을 대신하는 승인이 아니다. 두 해상도의 응답 차이는 측정할 수 있지만 그 자체로 연속 수렴이나 실제 우주론 history 정확도를 증명하지는 않는다.

O1–O6는 전부 UNRESOLVED이고 O2/O3 선택도 null이다. 실제 B·mu·개별 적분구간·우주론 상태·각도 kernel을 선택하지 않았다. source/test/archive subtree와 두 owner JSON blob이 부모와 동일함을 실행에서 확인했다. 원본 C/history·기존 O2/O3 검산·생산 pytest는 실행하지 않았다.

## 증거 보존과 시각 검토

[산출물9965821458](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/33954237095/artifacts/9965821458)은5파일,ZIP53609bytes다. GitHub 업로드 로그와 API가 모두 ZIP SHA256 `772035999f75be8914ac14cc9029cc970495903519a92d0b2bad783b0e43e826`를 표시한다. 보존기한은2026-10-05다. hosted 내부의 파일별 해시 검사4건도 모두 통과했다. ZIP을 이 대화의 로컬 공간에서 다운로드·재해시한 것은 아니다.

`EXECUTION_READBACK.json`과 `ARCHIVE_INVENTORY_READBACK.json`은 실제 디코딩된 로그 및 API 값의 의미 내용 사본이다. 원래 산출물 JSON과 직렬화 바이트가 같다고 주장하지 않는다. 원래 inventory SHA와 artifact digest를 별도로 보존했다. 계산기와 연구 문서, 결과 핵심값·전체 구성원 식별정보는 Git에 남으므로 산출물 만료와 구별한다.

PNG와 SVG는 생성됐지만 이 대화에서는 실제 이미지를 열지 못했다. 시각 검토 상태는 NOT_PERFORMED다. 독립 reviewer는 호출하지 않았고 같은 작성자가 수학·코드 관점을 나누어 점검했다.

## 일반 CI는 별도 실패

일반 검증33954258709/job101274572163의 디코딩된 새 로그를 읽었다. merge checkout은 `28a6b45783169accb849bffefd4e67274e9e50e6`이다. 패키지 import는 성공했으나 `python scripts/verify_repo.py --quick`이 기존7개 파일의 공백 검사에서 실패했고 전체 pytest는 건너뛰었다. 첫 경로는 `rec_local01_admission/evidence/MUTANT_drop_density_jvp.log:6`이다. 실패 목록의 파일은 새3파일 diff 밖이며 이번 작업에서 바꾸지 않았다. 전용 연구 실행은 통과했지만 전체 repository GREEN은 아니다. 이 완료 문서 자식에서 발생할 추가 CI의 상세 결과를 미리 추정하지 않는다.

## Atlassian 추가 기록

실제 추가 후 다시 읽어 확인했다.

- BASS-19 댓글10603, 상태 In Progress 유지.
- BASS-26 댓글10604, 상태 In Progress 유지.
- FED-02 page27492353 footer28704781.

REC 연구 결과와 PR 포인터만 추가했고 공식 dependency, 다른 세 저장소 snapshot, 상태, 물리 인증·provider·ready/merge를 변경하지 않았다.

## 종료

이 연구 실행과 자료 보존에서 종료한다. 다음 단일 연구는 원본 기본/고해상도 표의 설정·정규화·동일 시험함수 응답 비교다. O2/O3에 대한 책임자 선택은 병렬로 미결정 상태를 유지한다. 추가 하네스나 기존 어댑터 재구현으로 확장하지 않는다.
