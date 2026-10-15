# Codex handoff: REC R3f / original HyRec H+He FULL NCP campaign

**실행 모드**: `physmath-research-loop`의 현재 과학 범위와 C5–C8 후속 실행. 사용자 승인된 원격 NCP를 사용하되, **원래 owner PC의 dirty checkout, 기존 NCP REI/REC task, checkpoint를 수정·삭제하지 않는다**. Codex는 실제 명령과 반환 파일을 확인하고, 유효한 결과만 별도 PR과 이중백업으로 게시한다.

## 목표와 권위

목표는 `rec_bianchi`의 **원본 HyRec October 2012 native-C H+He FULL FLRW**를 이미 source-verified된 REI-matched q=0 배경에서 독립 \(Y_{He}\) 97점으로 실행해 물리적 민감도와 finite-difference error를 검증하는 것이다. 이어지는 연구 DAG에는 source-physical initial photon history의 독립 Python FULL H+He 구현이 별도로 남아 있다. 이번 NCP 캠페인을 그 목적의 완결이라고 잘못 주장하지 않는다.

- `rec_bianchi` authoritative stack: PR #96 (`05e35be9f5788b3ea1708027f2c131ccd57985a5`), 그 위의 R3f published branch `research/rec-r3f-hyrec-full-yhe-ncp-20261016`. 이 브랜치 HEAD는 새로 `git fetch`로 확인한다.
- 원본 source immutable ZIP: `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`, SHA-256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
- 기존 원본 C FULL source stdout checksum: `6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400` (8,001 rows; `research/rec_r3c_rei_bridge_20261015/HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz`).
- 원본 REI scenario SHA `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`을 읽기 전용으로 보존. `rei_bianchi` PR150+는 읽기만 하고 mutation 금지.
- 빠른 local source-actual 49 case 결과와 test receipts는 `research/rec_r3f_ncp_yhe_20261016/`; source stdout byte-identity, 489 fast PASS/42 slow-deselected, native slow smoke PASS.

## 변경/중단 정책

- 기본 `(-,+,+,+)`, photon Thomson scattering rate \(c\sigma_T n_e\), 실제 모델 \(q=0\). \(n_e=x_e n_H\), source \(n_H\propto 1-Y_{He}\), \(f_{He}=Y/[3.97153(1-Y)]\). 고정 \(\omega_bh^2\)에서 \(\partial_Y\ln n_e=\partial_Y\ln x_e-1/(1-Y)\)이며 고정 recipient \(n_H\) 조건부 효과와 혼동 금지.
- 원본 소스는 압축 내부에 포함. `run_r3f_ncp_hyrec_yhe.py`는 표준 라이브러리만 요구하고 원본 C 파일을 변경하지 않고 새 temp dir에 추출·GCC 컴파일한다.
- **NCP 97-case는 아직 NOT_RUN**. Rust 1.99가 설치되었다고 보고받았으나 본 원본 C 경로는 Rust 설치와 독립이다.
- 동일 실패에 blind retry 1회 초과 금지. 첫 물리·빌드·환경 실패의 원문을 보존하고 원인에 따라 최소 수정한 새 namespace에서만 targeted rerun.
- `native_subagent`는 현재 ChatGPT 실행에서 제공되지 않았음. local Codex가 실제 native subagent 도구를 지원한다면 *역할이 다른* source review와 실행 검증을 1회 분리할 수 있다. 지원하지 않으면 단일 실행자로 진행하고 receipt에 명시한다.

## 단계 A: 로컬 fresh checkout과 게이트

**현재 dirty root/worktree에 `git reset`, `git checkout`, `git pull`, `git clean` 금지.** 사용자 프로젝트 checkout의 실제 상태를 읽어야 할 경우 읽기만 한다. 새 clone을 별도로 만든다.

```bash
set -euo pipefail
RUN_ROOT="$HOME/rec_theory_runs/REC_R3F_CODEX_20261016"
test ! -e "$RUN_ROOT" || { echo 'CREATE_ONLY_NAMESPACE_EXISTS'; exit 2; }
mkdir -m 700 -p "$RUN_ROOT"
git clone --single-branch --branch research/rec-r3f-hyrec-full-yhe-ncp-20261016 \
  https://github.com/cosmosapjw-quantum/rec_bianchi.git "$RUN_ROOT/checkout"
cd "$RUN_ROOT/checkout"
git log -1 --format='%H %s'
sha256sum -c <(printf '%s  %s\n' \
  48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27 \
  archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip)
PYTHONPATH=src:scripts OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -m pytest -q tests/research/test_r3f_yhe_scan.py tests/research/test_r3f_verify.py -m 'not slow'
```

모두 통과해야 다음. 이어 변경분 의존성 검증을 위해 `PYTHONPATH=src:scripts python3 -m pytest -q -m 'not slow'`를 실행하고 실제 합계/exit code 기록. 다른 Python 버전이나 NumPy/SciPy dependency가 없다면 기존 checkout 준비 방법을 확인하고 환경 오류로 기록한다. Local source smoke는 C/GCC+stdlib로 독립 실행:

```bash
SMOKE="$RUN_ROOT/smoke_001"
test ! -e "$SMOKE"
python3 scripts/run_r3f_ncp_hyrec_yhe.py --mode smoke --workers 4 --output-dir "$SMOKE"
python3 scripts/verify_r3f_result.py --folder "$SMOKE" --expected-mode smoke
```

## 단계 B: source-only NCP stage 및 실제 64CPU 자원 확인

**NCP 접속 정보는 사용자가 로컬에서 제공한 SSH 경로를 사용하되 저장소/공개 문서에 실제 서버 주소나 비밀키 내용을 기록하지 말 것.** 환경변수 `NCP_SSH_TARGET`은 외부 shell session에서 정확한 `root@IPv4`로 설정한다. 사용자가 이번 대화에 제공한 대상이다. 아이덴티티 파일을 실제로 읽거나 복사해 출판하지 말 것.

권장 최단 경로: 이 응답에 함께 제공한 `REC_R3F_NCP_SOURCE_CAPSULE_20261016.tar.gz`를 직접 `scp`로 보내거나, fresh checkout에서 **다음 파일만** source tar로 포장한다:

- `scripts/run_r3f_ncp_hyrec_yhe.py`
- `scripts/verify_r3f_result.py`
- `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`
- `research/rec_r3c_rei_bridge_20261015/HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz`
- `research/rec_r3f_ncp_yhe_20261016/NCP_RUN_CONTRACT.json`

이 구성은 `REI` production source, checkpoints, private credentials, 수십 GB 저장소 이력과 무관하다. 이미 제공된 capsule 파일을 `$RUN_ROOT/REC_R3F_NCP_SOURCE_CAPSULE_20261016.tar.gz`로 복사하거나, 검증한 fresh checkout에서 다음으로 create-only 생성한다.

```bash
CAPSULE="$RUN_ROOT/REC_R3F_NCP_SOURCE_CAPSULE_20261016.tar.gz"
test ! -e "$CAPSULE"
cd "$RUN_ROOT/checkout"
tar -czf "$CAPSULE" \
  scripts/run_r3f_ncp_hyrec_yhe.py scripts/verify_r3f_result.py \
  archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip \
  research/rec_r3c_rei_bridge_20261015/HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz \
  research/rec_r3f_ncp_yhe_20261016/NCP_RUN_CONTRACT.json
sha256sum "$CAPSULE"
```

source archive는 반드시 **repo-relative** 멤버만 포함한다. 개인키, rclone 설정, `REI` 원본 checkout, 다른 태스크 출력은 포함하지 않는다. capsule SHA-256을 로컬에서 계산하고 기록한다. NCP에서는 새 태스크 공간을 **create-only**로 연다:

```bash
: "${NCP_SSH_TARGET:?Set NCP_SSH_TARGET outside repository from user-provided SSH address}"
SSH_KEY="$HOME/.ssh/ncp_key"
test -f "$SSH_KEY"
NCP_TASK=/root/REC_R3F_FULL_HHE_YHE_20261016_001
ssh -i "$SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=yes -p 22 "$NCP_SSH_TARGET" \
  "hostname; nproc; free -h; uptime; command -v gcc; command -v prlimit; python3 --version; /root/.cargo/bin/rustc --version 2>/dev/null || true; ps -eo pid,comm,%cpu,rss --sort=-%cpu | head -16; test ! -e '$NCP_TASK'"
ssh -i "$SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=yes -p 22 "$NCP_SSH_TARGET" \
  "umask 077; mkdir -m 700 '$NCP_TASK'"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=yes -P 22 \
  "$RUN_ROOT/REC_R3F_NCP_SOURCE_CAPSULE_20261016.tar.gz" \
  "$NCP_SSH_TARGET:$NCP_TASK/source.tar.gz"
```

진행 중인 `rei_bianchi`·다른 과학 계산이 CPU/RAM을 사용 중이라면 `--workers`를 16/24/32로 낮추고 사용 자원과 이유를 receipt에 기록한다. 이 시점에 기존 작업을 종료하지 않는다. 새로운 campaign wall budget은 처음 시작한 시간부터 기록하고 실패나 재개로 초기화하지 않는다.

## 단계 C: NCP 실제 실행과 검증

NCP에서 source archive의 SHA를 먼저 다시 읽는다. `tar -tzf` 리스트의 absolute path/`..` 항목이 없음을 확인한 다음 다음을 실행한다. 명령은 NCP에서만 실행해야 한다. `NCP_TASK` 변수는 NCP 셸에도 설정한다.

```bash
set -euo pipefail
NCP_TASK=/root/REC_R3F_FULL_HHE_YHE_20261016_001
cd "$NCP_TASK"
tar -tzf source.tar.gz | head -35
mkdir -m 700 stage
tar -xzf source.tar.gz -C stage
cd stage
sha256sum archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip
python3 scripts/run_r3f_ncp_hyrec_yhe.py --mode ncp --workers 48 \
  --address-limit-gib 2 --wall-limit-s 120 \
  --output-dir "$NCP_TASK/results/full97_001" \
  > "$NCP_TASK/NCP_RUN_STDOUT.log" 2>&1
python3 scripts/verify_r3f_result.py \
  --folder "$NCP_TASK/results/full97_001" --expected-mode ncp \
  > "$NCP_TASK/NCP_GATE.log" 2>&1
```

인증 및 source가 일치하지 않거나 한 case라도 실패하면 `NOT_ADMITTED`다. zip/sha log, compiler version, stdout+stderr, CPU affinity, 모든 결과를 보존하고 scientific PASS로 포장하지 않는다. `RUN.json`의 field-specific derivation과 모든 `SOURCE_DERIVATIVES`를 읽어 local 49-case와 numerical consistency를 비교한다. 48-worker speedup은 같은 입력 7개 control의 측정값으로만 보고하며 전체 97개 case science wall을 별도로 기록한다. NCP 97개는 local49의 수치적 결과와 범위가 다르므로 wall-time 비율을 64배 속도 향상이라 주장하지 말 것.

## 단계 D: 결과 회수·이중 백업·GitHub 게시

NCP에서 새 `NCP_RETURN_001.tar.gz`를 create-only로 생성한다. Source immutable ZIP과 science results/log, `REI_BRIDGE_CONTRACT` 관련 문서, manifest 및 실제 host/command/clock/CPU/메모리 설명을 포함한다. archiving 대상에 비밀키·환경 변수 원문·다른 task의 source·checkpoint가 포함되면 중단한다. 소유자 PC로 `scp` 후 로컬과 NCP archive hash 비교. 

- Dropbox: `dbx:bianchi/rec_bianchi/20261016/R3F_NCP_001/` (create-only)
- Google Drive: `gdrv:rec_bianchi_research_backups/20261016/R3F_NCP_001/` (create-only)

로컬에 연결된 기존 `rclone` remotes를 사용하고 `rclone copyto --immutable`, `rclone cat remote/path | sha256sum`으로 **각각 독립 readback**을 검증한다. 한 provider가 실패하면 `BACKUP_PARTIAL`을 정확히 기록하고 다른 provider의 성공을 취소하지 않는다. 기존 백업을 덮어쓰지 않는다.

새 PR을 `research/rec-r3f-hyrec-full-yhe-ncp-20261016` 위의 별도 NCP evidence branch에서 open(draft)하고 결과 JSON/CSV/plot의 tracked 범위와 원본 archived download path를 연결한다. 새 commit/tree SHA, PR link, two cloud provider IDs/paths, 각 remote SHA/byte length, science gate와 unresolved blockers를 `NCP_RETURN_HANDOFF.json`으로 저장한다. 원본 REI scenario/production는 절대 변경하지 않는다.

## 성공/실패 기준과 후속 원 연구

성공: 97개 original-C source run PASS; baseline original raw C science-equivalent ≤1e-9 (가능하면 byte-identical, 단 byte mismatch만으로 물리 FAIL 단정 금지); 8,001행×97, serial/parallel control byte parity; 1,581행 민감도 CSV와 불변식 검증; 두 원격 백업의 hash/size verified; PR에 실제 증거 게시. 실패/부분 실행은 완전한 error traceback, hash, 상태, 후속 최소 조치를 반환한다. 

이 실험을 REI CMB 광학깊이 예측으로 승격하지 않는다. 다음 물리 코드 목표는 **실제 초기 photon spectrum 및 H+He species를 가진 독립 Python HyRec FULL 적분의 원본 C production history convergence**, 그다음 사용자 승인된 고-z Bianchi 동역학과 `rei_bianchi`의 fresh q0 initial-condition 민감도 검사다.

반환값: `CURRENT_SOURCE_SHA`, `LOCAL_TEST_SUMMARY`, `NCP_HOST_AND_CPU`, `NCP_EXECUTION_STATUS`, `NCP_CASES`, `SOURCE_BASELINE_GATE`, `DERIVATIVE_GATE`, `NCP_RESULT_FILES_AND_SHA256`, `DROPBOX_UPLOAD_AND_READBACK`, `GDRIVE_UPLOAD_AND_READBACK`, `GITHUB_COMMIT_AND_PR`, `NEXT_MINIMAL_EXECUTABLE`, `ERROR_CLASSIFICATION`. 본문에 개인 키 내용을 포함하거나 사용자의 디바이스 로그를 그대로 붙이지 않는다.
