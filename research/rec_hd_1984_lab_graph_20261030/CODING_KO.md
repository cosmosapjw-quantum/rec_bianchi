# REC HD: 1984+2022 실제 실측과 회전 photon 자료의 코딩 연구

- C1, C2: 부모 PR162 HEAD `4d60f74db02d7435add062eaefb15739e68c4b55`와 immutable full archive를 고정; 1984 3 primary published line centers와 2022 2 measured combinations를 source identity로 잠근다. 새 원본 `.fit` 바이트 확보는 BLOCKED_NO_RAW이며 old 35Hz gate는 변경하지 않는다.
- C3, C4: source catalog가 준위(파수), photon(주파수), Einstein A, ± reported laboratory uncertainty 필드를 각각 독립된 의미로 제공하도록 `Decimal` SI exact conversion; incidence matrix rank는 Python `Fraction` 소거법. 각 물리량이 요구하는 근사/units 명시. N=9, M=5, T=3, 저장 O(1) 정형 행, 비선형 IVP 없음.
- C5: `src/produce_atlas.py` 원전 DOI 및 literal 입력 핀 SHA 검증, 원래 PR161/162 frozen JSON 키·양자수 검증, 실측 5개 edge, 조건부 anchor 1개 및 9개 LTE, 3 photon E/λ/P, low-J 조건부 누적 준위를 생성. CSV/JSON과 `src/plot_science.py`의 3개 실측 기반 진단 그림 출력.
- C6: 처음 CSV writer는 2022 combo 레코드의 키만 헤더로 잡아 1984 photon 부가 키에서 `ValueError`; 분광 모델/데이터를 바꾸지 않고 전체 row key union으로 수정. `evidence/FIRST_FAILED_RUN.json` 보존. 일반 `python -m unittest discover -s tests -v` 15/15, `python -O` 15/15, `python -m compileall -q src tests` PASS.
- C7: 1984 R(3),R(5),R(6)의 quantum assignment, 2021 source A/ν, 2022 lab combination source, SI h/c/k_B and 2J+1, conditional LTE/optically thin spontaneous power physical interpretation 검산. 2011 .egy print cell vs true 2011 fit covariance 구분.
- C8: integer graph incidence/`Fraction`, Decimal(68)로 roundoff floor 분리. 실제 instrument/model covariance가 없는 상태에서 sigma/χ² 미산출; 2021 source frequency와 data residual은 정확 수치 대조만.
- C9: Wolfram method-level 독립 검산 수행, 실제 distinct-author R6/C9 NOT_RUN. 이에 대한 PASS로 잘못 승격하지 않는다.
- C10: 원래 source ZIP nested immutable, source map/hash, 실제 결과표, 테스트 로그, 3 PNG, stage ledger, next handoff를 포괄하는 아카이브 생성. source authority를 바꾸지 않은 add-only GitHub Draft branch를 목표로 한다.

## 재현

```bash
python src/produce_atlas.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q src tests
python src/plot_science.py
```

## Gates

`REC-EXP-SPECTRAL: PARTIAL` (1984 실측 세 선 새 입력), `canonical=28/88 (+0)`, `REC physical=0/313 (+0)`, `new scoped=18/20`, different-author R6/C9 NOT_RUN. Original 35 Hz `FAIL7/8`, H5 ε null, H6/H7 OPEN, L4=false, REI=false, production HOLD, AUTO_NEXT_NODE=false.
