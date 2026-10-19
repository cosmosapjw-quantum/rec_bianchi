# R3O: VigilODE 재사용과 Rust 패키지 선택

## 백업에서 먼저 확인한 결과

추가 요청에 따라 rec_bianchi와 VigilODE의 관련 브랜치, PR, 실행 및
백업 목록을 먼저 대조했다. 실제 수, 파일 정체성, 조회의 한계는
`receipts/EXPANDED_INTAKE.json`에 있다. 목록의 업로드 시각을 새로운
물리 실행 시각으로 해석하지 않았다. 다른 REI 연구의 임시 보존
아카이브는 존재와 정체성만 기록했으며, 전체 내용을 읽었다거나
rec_bianchi checkpoint로 채택했다고 주장하지 않는다.

VigilODE의 새 V2 벤치마크는 2,700개 시도 중 2,639개 ok,
54개 refused, 7개 solver_failure를 기록했다. 그러나 ok인 2,639개
모두가 요구 정확도를 만족한 것은 아니다. `R_up <= 1`인 것은
2,329개다. 따라서 실행 종료, 요구 정확도, 계산 비용을 별도 필드로
다뤄야 한다. 과거의 결과 행 수 또는 잘린 출력 때문에 빈 오차 집계가
0으로 보일 수 있는 위험도 읽었으므로, 새 비교기는 요청 시각과
출력 상태의 개수·차원·유한성을 먼저 확인해야 한다.

V2의 특정 Prothero–Robinson 사례에서는 직접 출력 격자 오차와
dense output 오차가 크게 달랐다. 이 근거로 이번 제한된 RODAS
진단은 출력 시각을 직접 소유하고, dense output이나 전체 궤적의
오차 보증을 가져오지 않는다. 기존 VODE/Diffsol 비교와 공유 VM
시간은 정확도·호스트 조건이 맞는 production speedup 증거가 아니다.
관련 HE29 연구의 23개 합성 Schur 사례 역시 실제 HyRec 원자 연산자
치환 검증으로 확대하지 않는다.

직접 읽은 프로젝트 근거:

- [VigilODE PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71)
- [고정 개발 커밋 a21d573](https://github.com/cosmosapjw-quantum/vigilode/tree/a21d573980f66fe02891bd216153443b5352f921)
- `receipts/EXPANDED_INTAKE.json`의 실제 원격 보존 파일과 본문 조회 기록

## 고정 소스와 패키징

선택한 코드는 `claude/nice-dijkstra-208xq0`의
`a21d573980f66fe02891bd216153443b5352f921`이다. 이 정체성을 저장소의
default main이나 벤치마크 실행 당시의 `8a8bd409...`와 혼동하지 않는다.
초기 122개 파일에 원본 integrators/build.rs를 추가한 현재 123개 파일의 Git blob을 원격 트리와 실제 비교해 일치시켰다.
core, krylov, integrators의 수치 소스는 수정하지 않았다.

배포용 아카이브는 `rust/vendor/vigilode-a21d573-three-crates.tar.gz`다.
원본 MIT 라이선스와 계수 fixture를 포함한다. workspace에서 CLI와
fair-ab 두 멤버만 제외한 것은 패키징 변경이며, 원본 Cargo.toml도
`Cargo.upstream.toml`로 보존한다. 파일별 SHA256, Git blob, 변경 범위,
아카이브 해시는 `rust/VIGILODE_SOURCE.json`에 있다.
upstream의 전체 테스트·선택 기능이 패키징되거나 이번에 실행됐다고
주장하지 않는다.

## 이번 목적에 맞는 패키지 선택

| 후보 | 실제 제공 기능과 적용 판단 |
|---|---|
| VigilODE core / integrators / krylov | `CoreError`, 작업 계수, 엄격한 오류 척도, 행렬·LU, 관측 시각을 가진 RODAS5P API를 재사용한다. 적용 코드·실행 결과는 별도 Rust evidence로 봉인한다. |
| faer 0.24.4 | 이미 VigilODE가 사용하는 선형대수 의존성이다. 부분 pivot LU를 통한 선형계 풀이와 잔차 검증 경로를 재사용한다. 2×2에서의 성능 우위를 주장하지 않는다. |
| serde / serde_json | 형식화된 checkpoint·실행 receipt를 위한 기존 의존성을 재사용한다. 수치 상태의 정확한 비트 보존 여부는 별도로 검사한다. |
| diffsol 0.17.1 | BDF, SDIRK/ESDIRK, 사건 검출, checkpoint 기능을 확인했다. 후속 독립 방법 비교 후보로 남기며 이번 원본 predictor 경로의 대체 의존성으로 추가하지 않는다. |
| ndarray-npy 0.9.1 | NPY/NPZ 읽기·쓰기 기능을 확인했다. 이 작은 상태 교환에 배열 직렬화 의존성을 추가할 필요가 없어 채택하지 않는다. |

공식 문서상 faer는 중·대형 행렬을 주 대상으로 하며 낮은 차원에 대한
일반적인 최적 선택을 약속하지 않는다. 이번 선택 근거는 기존 구현의
재사용과 중복 의존성 억제이며, 측정하지 않은 가속 주장이 아니다.

2026-10-19에 실제 읽은 1차 문서:

- [faer 0.24.4](https://docs.rs/faer/0.24.4/faer/)
- [diffsol 0.17.1](https://docs.rs/diffsol/0.17.1/diffsol/)
- [ndarray-npy 0.9.1](https://docs.rs/ndarray-npy/0.9.1/ndarray_npy/)
- [serde_json 1.0.151](https://docs.rs/serde_json/1.0.151/serde_json/)

## 두 수치 경로의 서로 다른 질문

원본 고정 간격 경로는 상태와 네 미분 메모리를 Rust가 소유하고,
검토된 원본 C atomic/thermal 연산자를 호출한다. 여기서 확인할 것은
동일한 C 입력으로 시작한 원본 C 갱신과 Rust의 상태·메모리 바이트
일치다. Python의 독립 궤적 비교에는 기존 같은-h 허용값을 적용한다.
이것은 원자 물리 전체를 Rust로 번역했다는 뜻이 아니다.

RODAS5P 경로는 수치 방법이 다르므로 `EXPLORATORY_METHOD_COMPARISON`이다.
시간 의존성을 가진 HyRec 연산자를 autonomous 전용 `FastSmall`에
그대로 넣지 않는다. 명시적 시각, Jacobian 및 partial-t를 제공하는
일반 API를 사용하거나, 실제 checkpoint에서 동결한 affine 문제라면
그 동결 조건과 해석해를 명시해야 한다.

일반적인 정규화 `u = D^{-1}Y`, `x=ln(a/a_start)`를 사용하면

\[
g(x,u)=D^{-1}F(x,Du),\qquad
J_u=D^{-1}J_YD,\qquad
\partial_x g=D^{-1}\partial_x F.
\]

여기서 D는 진단 구간 시작에서 고정한다. Jacobian의 수치 차분이나
다른 적분기의 허용오차를 원본 predictor의 같은-h 기준으로 바꿔
읽을 수 없다. 그 진단이 성공해도 기존 U5 hold, 전역 수렴성 hold,
production 비용 비교, REI=false 상태는 그대로 유지한다.

## 실제 제한 실행과 현재 단계

샌드박스 `build_002`는 원본 C와 새 Rust 호출자를 실제 컴파일했다.
VigilODE 의존 라이브러리 자체는 과거 `8a8bd409...` 빌드의 read-only
산출물을 재사용했다. 선택한 수치 소스의 바이트 일치, Cargo fingerprint
의존 관계 및 연결 대상 해시를 확인했다. 이는 의존 라이브러리를
`a21d573`에서 새로 컴파일했다는 주장이 아니다. 첫 `build_001`은
링커의 메모리 할당 실패였고, 수치 실행 실패로 분류하지 않는다.

`verify_001`은 별도 파생 checkpoint 패킷에서 다음을 실제 수행했다.

| 항목 | 결과와 범위 |
|---|---|
| Rust 원본 predictor 대 원본 C | 16개 수용 갱신, 초기 상태 포함 17×6=102개 스칼라 비트 일치 |
| 독립 Python 대 C/Rust 같은-h | xe 최대 상대 차이 7.4344e-14, Tm 2.4969e-16; 기존 허용값 유지 |
| VigilODE 비자율 EMLA 진단 | 16개 수용 step, 16개 시도, 17개 직접 출력, 225개 source callback |
| faer 2×2 검사 | 선형계 잔차 1.2507e-16, 직접 2×2 식과 같은 해 |
| 의도적인 1-attempt 제한 | 실제 첫 수용 출력과 작업 계수를 남기고 실패 종료 |
| 의도적인 callback 실패 | 실패한 시도와 callback 계수를 보존하며 실패 종료 |

RODAS5P와 Python 원본 predictor의 차이를 기존 같은-h 허용값으로
나눈 값은 xe에서 최대 **2.530216356**, Tm에서 **0.014734336**이다.
xe는 기준 1을 초과한다. 출력 완료와 callback/선형계 검사가 통과했다는
진단 결과를 원본 방법의 같은-h 동등성으로 해석하면 안 된다.
두 방법은 갱신식과 checkpoint 미분 메모리의 사용이 다르며,
이 제한 비교만으로 어느 방법이 연속 물리 해에 더 정확한지 결정할
수 없다. 그림은 실제 초기 출력까지 포함한 17개 데이터를 사용한다.

파생 패킷은 각 lane의 상태 둘과 미분 메모리 넷을 담고, 전체 원본
NPZ/CSV/receipt 해시를 보존한다. 부모가 전체 원본 결과를 독립적으로
다시 읽어 native/Python 각각의 6개 binary64 값을 확인했다.
작은 패킷은 전체 생산자 아카이브를 대체하는 원본 파일로 표시하지
않으며, `review/RUST_BOUNDARY_PARENT_READBACK.json`에 이 범위를 명시한다.

Rust 독립 C9 감사에서 세 P2 수정과 제한된 수치 근거의 검토가 끝났다.
초기 GitHub Cargo 빌드는 배포 아카이브에서 원본 integrators/build.rs가
빠져 수치 실행 전에 실패했다. 원본 바이트를 추가한 v2 패키지의
수정된 소스는 4512b19e의 실제 GitHub 새 Cargo 빌드와 16-step 검증을 통과했다. 실행 코드와 이후 build-wrapper
수정의 관계는 `EVIDENCE.json`에 구분한다. 새 Cargo 경로는 검토된
Cargo.lock을 그대로 사용하며 build 중 lockfile을 다시 생성하지 않는다.

## 소스 빌드 보정과 실행기 종료 조건

v2 아카이브는 731,431 bytes, SHA256
`77c03b85844909b45428bfafd066d2403cb6f7f1870b8a68d705c4bfd1e7aca4`다.
첫 CI 실패 아카이브는 전체 원격 readback SHA 일치를 확인해 보존했다.
`review/VIGILODE_PACKAGING_CLOSURE.json`과 `review/C9_RUST.md`에
정체성과 검토 범위가 있다. 이 패키징 수정은 수치 소스를 바꾸지 않는다.

실행기는 완료 시 입력·산출물 해시 작업까지 측정한 후 최종 receipt
쓰기 여유를 남기지 못하면 거절한다. CPU는 완료 자식의 실제 사용량과
실행 중 프로세스 트리를 추적하며, RSS는 50ms 표본이므로 정확한 peak로
표시하지 않는다. Cargo.lock은 입력으로 고정하고 `--locked`를 사용한다.
보정된 16개 계약 검사는 1.766172 CPU초, 물리 step 0으로 통과했다.
부모가 추가로 CLI를 2–32 step으로 한정해 1-attempt 실패 검사의 전제를
명시했다. 기본 16 step은 같으며 별도 parser 거절 검사가 통과했다.

## 재개 후 새 실행과 최신 upstream 검토

`receipts/RUST_CI.json`은 GitHub push 코드 4512b19e의 새 Cargo 빌드와
17개 전용 계약 검사, 실제 16-step을 기록한다. Build153.660120 CPU초,
수치·제어1.743074 CPU초이며 원격 artifact의 전체 SHA가 일치했다.
같은 코드의 일반 CI는836PASS/20SKIP/72subtestsPASS다.20skip 중16개
Rust 계약 검사는 위 전용 환경에서 실제 통과했으며 나머지4개는 상속됐다.

중단 후 최신 tip b56bb19와 PR71의64b98521을 다시 읽었다. 새 tip의
ShiftedOperator nonfinite 오류전파 수정은 실제 중요한 수정이다. 그러나
현행 R3O fast factor는 I/(h gamma)-J를 자체 버퍼에 구성하고
InPlaceZeroSkipping으로 풀며 ShiftedOperator를 호출하지 않는다.
별도 faer probe도 DenseMatrix.sub의 오류를 직접 전파한다. 이것은
해당 소스 경로의 정적 판단이며 새 tip 전체를 실행한 결과가 아니다.
현재 수치 pin은 a21d573으로 유지하고, 미래 shifted/matrix-free 경로에는
그 수정을 요구한다. 새 triage smoke의 PROMOTE/PRUNE 분류는 잠정적인
계측 파이프라인 확인이며 HyRec 생산 승인으로 옮기지 않는다.

PR71의 달성오차 정합 비교·보존된 초기 비트 FAIL·전체 상태 읽기 검산을
읽었다. core Cargo/crates tree는 a21과 같은 것을 직접 대조했다.
Robertson/HIRES/van der Pol과 공간 Brusselator의 비용 순위가 다르며
공유 호스트라는 제약이 있다. 관련 원문, HE29 합성검사와 REI C11
실제 NCP 반환은 receipts/RESUME_INTAKE.json에 소유 프로젝트별로
기록했다. REC checkpoint와 연구 완료 수에는 합산하지 않았다.
