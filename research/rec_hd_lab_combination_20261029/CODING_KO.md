# REC HD 실제 실험 입력의 코딩 연구 (C1–C10)

**소스:** 2022 EPJD/PRA 2개 실험 combination frequency + 2021 LAMDA 계열 PR156 frozen public RESULT blob `5a99c9e31604347cf756abb4ab3ea1a134238e0d`. Full 2011 CDMS 원바이트 미확보. 실제 A 값 8개 행은 이전 소스 전사이며 정확한 출력 주파수/준위에 대응하지만 이번에 새 파일을 내려받은 것은 아니다.

- **C1–C2** 정확한 목표: 실험 두 조합 차이와 source photon/term-energy의 두 종류 잔차를 정량화. Source role 분리, 원래 35Hz 그대로, production source update 없음.
- **C3** 신호 모델: 정수 Hz와 `Fraction`으로 불필요한 반올림 없는 차이/복원. `Decimal(80)`로 SI 광자 에너지/파장/Einstein A photon power, Boltzmann ratio. 불확도는 입력의 타입·출처만 유지하고 공분산 부재를 보존.
- **C4** 리소스 범위: 고정 8개 source lines + lab 2 points, 50/100/200 K, no solver/nonlinear IVP, O(8).
- **C5** `src/physical_data.py`는 8개 source photon νP, level νE, Einstein A를 개별 원문 literal과 비교; 실험 데이터 DOI·양자준위·수치·측정오차를 엄격 비교. `MEASUREMENT_RECONCILIATION.json`, `PHOTON_PHYSICAL_TABLE.json`, `.csv` 출력. `src/plot_physical_data.py`로 실험 잔차, 실험 기준 LTE, 역사적 source photon power 세 그림.
- **C6** 정규 unittest 19/19 PASS, optimized Python -O 19/19 PASS, `python -m compileall -q src tests` PASS. Negative fixtures는 A, source level-energy νE, 실험 ν20 tampering 거부. `unittest`는 raw 2011 data 재다운로드 증명이 아니다.
- **C7** 물리 근거: EPJD (2022) §3.2의 공개 실험 수치와 PRA (2022) 초록의 원실험 데이터를 검증하고, 주파수 간 telescope identity 및 SI dimension 점검. LTE 값은 *측정 우주론*이나 *실제 collisional non-LTE 해*가 아니다. Model uncertainty/covariance missing.
- **C8** fixed data의 정확 정수/고정 precision 변환으로 roundoff가 실험 잔차 생성 원인이 아님을 확인. 실험 불확도와 역사적 catalog fit 불확도 혼동 방지. 이 범위의 계산은 수치해석 solver 성능 요구 대상이 아니며 CPU speedup 미주장.
- **C9** 현재 환경 원격별개저자 reviewer NOT_RUN. Wolfram 독립 기호/정수 계산은 독립 수단이지 별개 author review가 아니다.
- **C10** source role, raw not acquired, test output, plot QA, DAG overlay 및 production HOLD를 copyable handoff로 패키징. 과거 PR159는 손대지 않는다.

재현:

```bash
cd REC_HD_LAB_COMBINATION_20261029
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q src tests
python src/physical_data.py
python src/plot_physical_data.py
```

DAG: canonical **28/88**; REC physical **0/313**; 신규 실험 독립 제약 **2개 확인**; 이번 scope **18/20 (R6,C9 partial)**; 원본 35Hz **FAIL7/8**. **CDMS 2011 v2 원바이트 NOT_ACQUIRED**, H5 ε null, H6/H7 OPEN, L4 false, REI false, production HOLD. **AUTO_NEXT_NODE=false**.
