# 복사 가능한 Codex/NCP 재개 프롬프트

아래 본문은 사용자의 사전 파일 준비 없이 전달할 수 있다.

```text
$physmath-research-loop를 사용해 rec_bianchi R3O 이후를 이어서 수행하라.
repo=https://github.com/cosmosapjw-quantum/rec_bianchi
PR=https://github.com/cosmosapjw-quantum/rec_bianchi/pull/109
branch=research/rec-r3o-grid-frontiers-20261019
tested_code=4512b19e5615fabcb80e0860dbf3bb3086fe01fb

먼저 실제 GitHub/Drive/Dropbox/Library 및 사용 가능한 NCP 실행 반환을
최신 조회하고 PR109 Conversation의 최종 archive-preservation receipt를
읽어 최종 HEAD를 확인하라. 기존 checkout을 보존해 fetch하거나 별도
checkout을 자동으로 준비하라. 사용자의 파일 다운로드·수동 명령 실행을
요구하지 말라. single-branch fetch refspec에서는 FETCH_HEAD만 갱신될 수
있으므로 explicit branch refspec과 실제 원격 SHA를 대조하라.

research/rec_r3o_grid_frontiers_20261019/ 아래의 EVIDENCE.json, DAG.json,
BACKUP_ACKS.json, HANDOFF_KO.md, receipts/RESUME_INTAKE.json,
receipts/RUST_CI.json, review/C9_RUST.md, review/C9_RUST_P3_CLOSURE.json,
rust/rec-hyrec-vigilode/README.md를 실제로 읽어라.

재사용: 원본 U4/U5, PR105 legacy/owned 실행 결과, PR107 h2 U6 5210-step,
PR108 comparator, R3O h2 16-step와 독립 h4 72893 He rows+8 FULL steps.
Rust/C 102 scalar byte parity와 전용17검사는 GitHub 4512b19e 소스에서
새 Cargo 빌드로 통과했다. 일반CI836PASS/20SKIP/72subtestsPASS.
과거 cached-library sandbox build와 fresh Cargo CI를 합치지 말라.

현재 목표는 NCP의 원본 소스 컴파일·작은 호환 수정·제한 실제 실행이다.
실제 현재 NCP 프로세스, 산출물, 남은 CPU/wall/memory와 복구 여유부터
확인한다. Rust1.94.1을 side-by-side로 선택하고 다른 연구의1.99 설치를
다운그레이드하지 않는다. 필요한 Python/NumPy 및 cc/ar를 자동 준비한다.
새 출력 디렉터리를 자동 선택한 뒤 저장소 루트에서 다음 경로를 수행한다:

python -B scripts/build_r3o_rust.py --output <새 build 디렉터리>
python -B scripts/verify_r3o_rust.py --build <build 디렉터리>/build.json
  --boundary-packet rust/rec-hyrec-vigilode/fixtures/r3m_u6_boundary.json
  --steps 16 --output <새 verify 디렉터리>
python -B scripts/verify_r3o_h4_start.py --mode start --steps 8
  --evidence-dir <새 h4 디렉터리>

위 줄의 디렉터리 선택·명령 조립은 네가 하며 사용자가 채우도록 요구하지
말라. 기본 build는 검토된 Cargo.lock과 압축 upstream source를 검증하여
자동 해제한다. registry access가 없는 경우만 기존 검토된 vendor를
--registry-vendor로 연결한다. source build 240CPU/480wall/3GiB,
Rust verification20CPU/60wall 제한을 임의로 늘리지 말라.

다음 h2 low-z full을 준비할 경우 검토된 R3M full raw를 기존 host/backup에서
직접 찾고 해시 확인한다. sourceZIP48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27,
NPZ5ceb99a7ed221f920460aa41188ce60a748332e854a75ee58362d3f10a360cd2,
CSV57ebca0157e956747059af4ae3d9dfb44a98157e58e6ffdbb917a520c3406c38,
verification1d55f1ff90a9fad7174ddc6022bbf957aeb4f683b7831ecbb63acd854d925b4b.
R3M backup Drive173QaPYquHnrWeS_Rxrb1rRPSk0VrGMmx,
Dropbox id:BSpOijBcT10AAAAAAD_QGw.
verify_r3o_lowz.py --mode smoke --steps 16을 현재 소스와 원본raw에서 통과한
뒤 실제 유효한 새 allocation 및 복구 여유가 있을 때만 --mode full로
153327-step을 진행한다. full_h4와 세 격자 완성은 별도 노드다.

고정 조건: h2=4.245e-5, h4=2.1225e-5, 원본 atomic/thermal operator,
입력 stage 경계와 네 predictor memories, 원본 same-h 기준.
원본h U5 HOLD_9_FAIL, h2 HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI=false.
원본 predictor=Y[n]+h*(1.25F[n]-0.25F[n-2]).
RODAS xe 차이는 원본same-h허용값의2.530216배이므로 탐색적 방법 비교다.
full h/h2/h4 수렴성·production speedup·Bianchi/REI/CMB 예측은 승인하지 말라.

VigilODE 최신tip b56bb19와 PR71최신64b98521을 이미 읽었다.
현재 검증 pin은 a21d573이다. ShiftedOperator의 새 typed-error 수정은
현재 fast 직접LU 경로 밖이며, 미래 matrix-free 경로를 붙일 때 별도로
반영·검토하라. upstream 전체 테스트나 새tip 빌드 완료를 가장하지 말라.

각 실제 단계에서 코드·입력·결과 before/after hashes, 실제 호스트·컴파일러,
CPU/wall/관측한 RSS 범위, 실패·미완료·실행하지 않은 항목을 기록하라.
완료 노드 재사용, 변경 코드 push, 독립 검토, DAG·백업·게시를 수행하라.
원격 upload ACK, producer SHA, 전체 readback SHA를 구분하라.
전체 진척 표와 복사 가능한 한국어 반환 handoff를 본문에 출력하라.
```
