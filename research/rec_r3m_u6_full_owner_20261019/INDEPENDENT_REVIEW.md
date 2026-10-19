# R3m 독립 검토 기록

두 검토 모두 이 세션에서 별도 agent가 read-and-run으로 수행했다. 기존 파일은 수정하지 않았다.

## 1. PR105 raw 대 receipt

대상 raw는 owner의 `rec_theory_runs/REC_R3K_OWNED_U6_20261018/evidence/`에 있다. receipt는 `research/rec_r3k_owned_validation_20261018/EXECUTION_001.json`이다.

- 일치한 항목:
  - pair16: 16 step, byte identity, legacy 0.323913188 s, owned 0.202954646 s.
  - pair128: 128 step, byte identity, legacy 2.452338713 s, owned 0.328992197 s.
  - smoke: 3 step, 1875 fields, 939 links, 21.577521 process-tree CPU s, same-h `PASS_PENDING_REVIEW`.
  - 두 점 fit의 A=0.18494928157142856, B=0.0011253352767857164를 재현했다.
- source binding은 모두 `bf590549737f738b21854b83df78dbdc67a2e1d3`다.
- verification.json 안의 모든 파일 hash(partial 6, history, binaries, native stdout/stderr, build logs, 수정 source 4)가 실제 파일과 일치했다.
- 확인할 수 없는 항목: receipt에는 raw 파일 hash가 기록돼 있지 않다. pair 배열 dump는 보존되지 않았다.
- 표현 차이: receipt 최상위 `NATIVE_SMOKE_PASS`는 raw의 `SMOKE_ONLY` / `PASS_PENDING_REVIEW`보다 강하다. receipt 내부 `same_h_status` 필드는 정확하다.

## 2. full 5210-step U6 같은-h 재계산

스크립트는 `review/check_full.py`, `review/check_hash.py`이고 출력은 `review/check_full.out`이다. 검토자는 상수와 표만 repo에서 import했다. 대상은 `HyRec2012Cosmology`, two-photon table, `START_IZ`/`RT_IZ`/`PREFIX_COLUMNS`다. verifier의 비교 함수는 호출하지 않았다.

| 검사 | 결과 |
|---|---|
| 행 수와 순서 (V/A 1,620,310, L 15,630, PV 5,203,963, PL 50,199, STEP 5,210) | PASS |
| 모든 값 finite | PASS |
| V/A/L gate max ratio가 receipt와 bit 일치: 1.7688723656877556e-05 / 0.01016409195990302 / 1.7690729538503825e-05. ratio>1 행 0 | PASS |
| prefix PV/PL gate max 1.12e-3/1.14e-3, ratio>1 행 0 | PASS |
| state xe 1.3229e-13, Tm 4.36e-16, RHS H 2.79e-14, T 6.32e-13, schur ≤1.6e-15 | PASS |
| iz 순서, coupled/post_saha flag, 종료 58389, END row | PASS |
| pilot128 NPZ 앞 16,861 열과 states/steps 바이트 일치 | PASS |
| partial bin = NPZ 열 PREFIX+0…PREFIX+5209 | PASS |
| 모든 NPZ member가 ZIP_STORED | PASS |
| hash 전부, profile/journal, exclusive+unattributed=측정 구간 (차이 0.0) | PASS |
| exit 0, caps(60/180/2 GiB/affinity [4]/BLAS1), process-tree 37.57 s | PASS |

판정은 `REVIEW_PASS`다. 범위는 같은-h backend/원본 C parity로 한정한다.

- 관찰: 평균광자 채널의 ratio는 V/L보다 약 575배 크지만 여전히 약 100배 여유가 있다. rounding 민감도에 따른 method 특성으로 보이며 code defect가 아니다.
- 한계: 공통 입력 source/thermal 검사는 5210개 중 42개 표본만 본다. 출력 전 구간은 stream 비교가 덮는다.
- 한계: peak RSS는 verifier 프로세스만 포함한다.
- 이 검토는 Python h/h2/h4 수렴, 수렴 차수, 오차 한계를 보이지 않는다. DLNA를 절반으로 줄인 C 빌드도 h-sweep 기준이 아니다.
