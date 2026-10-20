# R3P 최적화 연구 완료 및 NCP 실행 인계

## 정확한 기준

- 저장소: https://github.com/cosmosapjw-quantum/rec_bianchi
- PR110: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/110 (draft, merge하지 않음)
- Branch: `research/rec-r3p-exact-acceleration-20261020`
- 실제 새16단계 및 전용 CI 코드 SHA: `e2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d`
- 이후 commit은 결과·백업·handoff 게시다. 최종 게시 HEAD와 ZIP producer/remote readback은 PR110의 최종 보존 receipt와 BACKUP_ACKS.json에서 대조한다. ZIP이 자기 자신의 해시나 업로드 이후 receipt까지 포함한다고 해석하지 않는다.

먼저 EVIDENCE.json, DAG.json, BACKUP_ACKS.json, REPORT_KO.md, receipts/STAGE2_CI.json, receipts/C9_FINAL_REVIEW.md, receipts/smoke16/verification.json 및 supervision.json을 읽는다. GitHub와 관련 백업에 이후 새 결과가 있는지 먼저 확인하고 완료 노드를 재사용한다.

## 완료한 연구와 실제 실행

백업 조사 후 PR104 이후 완료된 R3M full5210 및 R3O를 재사용했다. 새 full5210 적분은 하지 않았다. 완료 R3M의 saved stream 15개 대조는 판정/native arrays/diagnostic hashes가 모두 같았다. 첫 두 round가 주 분석이고, 세 번째 round의 마지막 worker는 inherited CPU limit 초기화 오류를 고친 뒤 원래 배정 한도 안에서 한 개만 재개했다. 실패와 수정 전후 hash를 보존했다.

주 분석 감사 CPU 중앙값은 legacy22.368621475초, cached20.258669566초, Rust1 10.027651230초, Rust2 9.926132620초, Rust4 9.888654041초다. Rust1 paired CPU ratio 중앙값은2.232513배다. 작은 표본의 관측이며 전체 production 가속률이 아니다. 별도9,952lane ratio의 NumPy/Rust/scalar 출력은 bitwise 같지만 그 API를 전체 spectral stream loop에 연결한 것은 아니다.

새 U5 smoke16은 원본 C 같은-h에서5,008 causal links/10,000 spectral fields를 검증했고 original-average failures=[]다. common-input oracle은 원래 두 sampled evaluation에서 PASS다. 전체 supervision CPU8.826414초/wall8.790703708초, exit=0, input/source identity=UNCHANGED다. 원래 verification=`SMOKE_ONLY`, same_h=`PASS_PENDING_REVIEW`, Python=`HOLD_CAP_BEFORE_RT_BOUNDARY`를 그대로 유지한다. 독립 후속 검토는 변경 source23개, frozen109개, 실제 영수증 연결을 확인했고 검토 범위의 남은P1/P2 없이 닫혔다.

로컬 Python214개 계약 검사와 Rust18개/C ABI가 통과했다. 같은 소스 GitHub Actions 전용 CI도214 PASS이고 일반 회귀 CI는968 PASS/102 SKIP/72 subtest PASS다. 중복 실행을 새로운 고유 테스트 수로 합산하지 않는다. 새 실제 실행은 ChatGPT sandbox, CI는 GitHub Actions다. NCP는 실행하지 않았다.

## 복구 identity

원본 ZIP은 저장소 archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip, SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`다.

검토된 U5 python_u5_thermal.npz SHA256은 `7aeec545cfc028e870d51e07d1fe3f052bd770d1eb4537568f5faa889bf6752b`다. 복구 capsule REC_R3L_REVIEWED_U5_CHECKPOINT.zip은79,241,895bytes, SHA256 `3b469781e937fa6a543a007088b73fb5b01a420261e9c4daa2d454cb3ae88106`; Drive ID `1oYwz16SYxVEV8PW44aygw8yE4X9CCX2I`, Dropbox ID `id:BSpOijBcT10AAAAAAD_QBA`다. 현재 연구에서 독립 전체 원격 readback 후 복구했다. 사용자에게 파일 준비나 수동 다운로드를 요구하지 말고 기존 NCP 경로 또는 허가된 연결 도구로 에이전트가 직접 복구·검증한다.

재사용 full raw REC_R3M_FULL5210_STORED_OWNER_RAW_001.tar.gz는232,521,236bytes, SHA256 `8cd5da29521b47d6b715dfa6889ae11d239ef430460deae97824ee32584b80b9`, Dropbox ID `id:BSpOijBcT10AAAAAAD_QGw`다. 세부 파일 hash는 AUDIT_COMPARISON과 원래 receipt에 있다.

새 raw REC_R3P_U5_SMOKE16_RAW_e2b39e33_20261020.tar.gz는148,406,351bytes, SHA256 `6876e568102476c4c7448f0dcbabcfe656399df37341862c6d3a92319be36369`다. 세 부분을 번호순으로 합치며 부분 hash/원격 ID는 BACKUP_ACKS.json에 있다. Drive·Dropbox·Library 각각 독립 전체 readback SHA가 PASS다. Drive 재다운로드 묶음 내부43개 파일도 SHA/크기가 모두 맞았다. Signed URL은 저장소에 넣지 않았다.

## NCP에 남긴 작업

현재 opt-in 경로의 구현·문서·경량 검증 코드를 완성해 push했다. NCP에는 rustc/cargo1.94.1과 C compiler를 사용한 오프라인 build, 환경에 따른 작은 호환성 수정, 허가된 실제 실행을 남긴다. Rayon1.12.0 및 여섯 registry package는 lock/checksum/license와 함께 vendor했다. 별도 solver나 새 의존성 버전을 선택할 필요가 없다.

새로운 플랫폼을 검증할 때만 새 allocation ID와 독립 output directory를 사용한다. 완료된 이 샌드박스16단계와 saved15개 대조를 완료 증거 수를 늘리기 위해 반복하지 않는다. public launcher는 smoke16 또는 pilot 최대128만 받는다. 새 full5210 allocation/admission은 없고 full mode를 열지 않았다.

공개 진입점은 scripts/run_r3p_u6_supervised.py다. 이 launcher가 수치 import 전 preflight부터 C컴파일, 적분, 감사, closeout까지60CPU초/180wall초를 감시하고 마지막 receipt write에2CPU초/3wall초를 남긴다. 메모리는 process별2GiB AS와50ms sampled worker/descendant RSS이며 parent를 포함한 정확한 aggregate limit이 아니다. inherited hard limit을 높이지 않는다. programmatic worker만 실행한 결과를 전체 감독 실행으로 기록하지 않는다.

에이전트가 실제 환경의 경로를 찾아 아래 옵션을 채운다. 사용자가 파일을 준비할 필요는 없다.

```bash
python -B scripts/build_r3p_rust.py --output <새_빌드_디렉터리>
R3P_BUILD_RECEIPT=<새_빌드_디렉터리>/build.json python -B -m pytest -q -p no:cacheprovider tests/trajectory/test_r3p*.py
python -B scripts/run_r3p_u6_supervised.py --checkpoint <검증한_U5_경로> --source-zip archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip --expected-commit <실제_깨끗한_checkout_SHA> --new-allocation-id <별도의_유효한_NCP_할당_ID> --evidence-dir <새_실행_디렉터리> --mode smoke --audit-backend rust --build <새_빌드_디렉터리>/build.json --block-columns 32 --history-container stored
```

소스가 달라졌으면 변경과 새 hash를 먼저 검토한다. build receipt는 실제 checkout의 실행 closure 및 library hash와 같아야 한다. 복구·소스·입력 hash, 최초 실패, 실제 자원 측정, 원래 verification 상태를 기록하고 단계별 백업/게시/DAG를 갱신한다. 새 실효 예산·복구 여유와 선행 검증 없이는 full U6나 production speedup 판단으로 진행하지 않는다.

## 유지할 과학적 상태

h=4.245e-5, 원래 atomic/thermal operator, predictor recurrence, causal/stage boundary와 같은-h gate를 보존한다. U5 원래 h=HOLD_9_FAIL, h2=HOLD_8_FAIL, 기존 비용=CLOSED_HOLD_NOT_RESET, REI_activation=false다. Python h/h2/h4 전역 수렴과 Bianchi/REI/CMB 예측을 승인하지 않는다. VigilODE pin `a21d573980f66fe02891bd216153443b5352f921`을 유지하며 upstream solver 결과를 REC의 성능이나 정확성으로 대체하지 않는다.

## 최종 코드·증거 보존

완료 snapshot은 `0b80913bf1c665cc4cfab6dfaa3ea35f815a482f`다. 전체 추적 파일3,410개를 담은 `REC_R3P_CODE_EVIDENCE_HANDOFF_0b80913b_20261020.zip`은122,092,525bytes, SHA256 `edccebf552671489f91e3ec2c31357fb901b73f90e0230d0cbe24a0b1f524521`다. 각 entry를 Git blob과 대조했고 세 저장소 독립 전체 readback SHA도 모두PASS다. Drive/Dropbox는3부분이며 Library는한개 완전한ZIP이다. 부분 hash/원격 ID는 BACKUP_ACKS.json에 있다.

원본 snapshot ZIP과 그 업로드 후 작성한 보존 metadata의 commit을 구분한다. 이 마지막 metadata와 최종 HEAD CI는 GitHub/PR110 Conversation에 결속한다. 원래 단계0/2 ZIP 자체의 readback은NOT_RUN이고 단계1 및 새 raw/최종 코드 ZIP의3저장소 전체 readback은PASS다. 후자의 검증으로 과거 단계의 독립 readback 이력을 소급 변경하지 않는다.
