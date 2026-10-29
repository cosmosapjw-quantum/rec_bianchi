# REC HD Sung 2022 측정 원전의 코딩 연구 계약

- **C1–C2:** PR163 `65c5c4c9105c9957418ff014d34e007e53a63b3b`, original source ZIP SHA `90ca686b37a15f69605b8f4aad1a259adfb94430474fd6fe8694a38d0365820d`를 immutable input으로 고정. 새 2022 Sung DOI Table4 4개 line center + H2 gamma/delta/S, 이전 직접 실측 5개를 source-kind 보존 하에 결합한다. 2011 CDMS raw/covariance NOT_ACQUIRED.
- **C3:** `Decimal(75)` Hz 정확 누적, `Fraction` exact incidence rank; 주파수 Hz에서 nominal minimax을 직접 계산해 불필요한 `cm−1→Hz→cm−1→Hz` Decimal tail을 막는다.
- **C4:** 고정 9 observed edges, 9 states, 4 photon rows, 12 pressure rows. O(9³) 작은 exact elimination, solver/IVP/HPC 없음.
- **C5:** `src/lab_cycles.py`, `src/figures.py` 구현. `data/LAB_INPUT.json`에 실험 숫자, published DOI, source 역할과 hold gate 보존. `evidence/RESULTS.json`, `SUNG4_SOURCE_PHYSICAL.csv`, `EXPERIMENTAL_CYCLES.csv`, `H2_PRESSURE_296K_CONDITIONAL.csv`, PNG 2개 생성.
- **C6:** Python unittest 19/19 일반/`-O` 및 compileall 실제 실행. 첫 실제 RED: Hz/파수 왕복 Decimal division 꼬리로 minimax equality 2개 실패. 원 입력·물리 gate 손대지 않고 Hz exact expression으로 수정, 초기 RED 로그 보존.
- **C7:** `C D=0`, rank 6, 3 components, 3 cycles, unit Hz/c, source-dependent A, H2 pressure shift negative R3, actual input guard를 대상으로 물리 검증. 공동 covariance 부재, Table4 fit uncertainties vs total systematics 구별.
- **C8:** exact Hz/minimax and deterministic 4 CSV/JSON outputs byte reuse. 수치 solver convergence나 속도 claim 없음.
- **C9:** 실제 별개 author 검토 NOT_RUN. 같은 세션 Wolfram/SymPy CAS는 독립 방법이며 별개 저자 심사가 아니다.
- **C10:** ZIP, stage evidence, explicit source census, draft PR, reproducible handoff. 원래 main/parent/prod 변경 금지.

재현:

```bash
cd REC_HD_SUNG2022_CYCLES_20261030
python src/lab_cycles.py
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q src tests
python src/figures.py
```

`native_subagent=NOT_RUN` (현재 host에 생성/수집 도구 없음); serial fallback 실행, 가상 child receipt 없음.
