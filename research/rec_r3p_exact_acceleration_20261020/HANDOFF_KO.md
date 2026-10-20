# R3P 단계 2 — 실제 U5 smoke 직전

정확 source commit의 공개 진입점은 `scripts/run_r3p_u6_supervised.py`다. `run_r3p_u6_audited.py` CLI도 같은 supervisor로 위임한다. `--mode smoke --audit-backend rust --build <오프라인 build.json>`으로16단계만 원본C와 검증한다. 원래U5 checkpoint hash, 원본sourceZIP hash, h=4.245e-5, operator/stage/REI 조건은 고정이다.

소스와 입력 hash 검사, C컴파일, 적분, 감사, closeout까지60CPU/180wall/2GiB와2CPU/3wall receipt reserve에 포함한다. 새 full allocation은 없다. 실제smoke는 이 단계의 source commit 고정 뒤 수행하며 아직PASS로 기록하지 않았다.

저장된R3M 전체감사는15개모두 verdict/native history/diagnostic hash가 같았다. 원래두round10개가주분석이고, 마지막자원초기화오류를 고친뒤 한개만재개한 세번째round는 별도descriptive자료다. 총263.522928CPU초/300초. Ratio9,952lane도scalar/NumPy/Rust bitwise일치, 실제bounded측정2.829587CPU초다. 상세결과는REPORT_KO.md와receipts에 있다.

현재로컬검증은Python58+82+72+2사례, Rust18사례,C ABI PASS다. 독립C9의문법/우선순위설명과전체자원범위보완을반영했다. 최종C9followup과현재코드CI는뒤영수증으로확정한다. stage0/1은세저장소업로드ACK가있고stage1은세원격전체readbackSHA도PASS다. stage2업로드ACK와sourcecommit은뒤BACKUP_ACKS/Conversation에결속한다.

U5 h HOLD_9_FAIL, h2 HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI=false 유지. 새전역수렴/production speedup/Bianchi/REI/CMB 예측을승인하지않는다.
