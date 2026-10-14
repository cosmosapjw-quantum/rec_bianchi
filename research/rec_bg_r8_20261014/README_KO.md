# REC_BG_R8_20261014

선택 단계 `R8` 결과 판정. **실제 종료된 native accepted step을 기준으로 short-interval clock subtraction 문제를 진단하고, 전 단계 positive-rate interpolation theorem의 생산 채택 범위를 구분했다.**

먼저 `theory/R8_REPORT_KO.md`, `results/MEASURED_STEP_DIAGNOSTIC.json`, `results/GLOBAL_CLOCK_CONDITIONAL.json`, `handoff/CODEX_HANDOFF_KO.md`, `SUPPLIER_DAG_OVERLAY.json`을 읽는다.

검산(인터넷/solver 없음):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s code -p 'test_r8_clock_budget.py' -v
python3 code/r8_clock_budget.py
```

실제 source 읽기 재현은 원본 local raw source의 exact SHA256을 보유한 REI PC에서만, 새 output 경로로:

```bash
python3 code/audit_saved_steps.py --repo-root /path/to/rei_bianchi --out /some/new/empty/research_output
```

이는 chemistry 실행이 아니라 selected102 native step read-only scan + mpmath60자리 geometric quadrature다. 완전한 private 원본 102행 및 local xTensor stdout는 Dropbox의 `BASS_DERIVATION_DOSSIERS_20260912/REC_BG_R8_NATIVE_STEP_EVIDENCE_20261014.zip`에 별도 보존했다. 메인 공개 연구 패키지는 원본 전체 native history CSV를 포함하지 않는다. Publication/backups, run status, source identity and scientific admission are separated.
