# REC HD | 296 K 조건부 Voigt opacity scientific coding loop

코드 SSOT: `src/voigt_opacity.py` (SciPy `voigt_profile`, `quad`), `src/figures.py`, `tests/test_voigt_opacity.py`. 입력 SSOT는 실제 부모 PR164 백업 ZIP 안의 `data/LAB_INPUT.json`을 원형대로 복사한 `data/LAB_INPUT_PARENT_PR164.json`. 2022 Sung 원본 출력의 공개 렌더 텍스트이며 원 스캔 또는 원 실험 raw는 아니다.

- **C1–C2:** 실제 4개 measured center, S, γ_H2, δ_H2 literal을 유효성 검사하며 296 K, pressure/HITRAN-reference column contract를 고정. 이전 35Hz 원 게이트 및 photon/source energy와 독립.
- **C3–C4:** `ν̃(cm^-1)`, `γ(cm^-1)`, `N_ref(molecule cm^-2)`, `S(cm/molecule)`, `V(cm)`를 SI 도플러와 결합한다. 수치오차는 64-bit float `voigt_profile` 및 `quad`, truncation은 profile 출력 window만의 문제이며 원 시스템 열역학의 오차가 아니다.
- **C5:** 고정 실험 입력에서 36개 physical conditional cases, 7,236개 spectral points, 3개 science figures 생성. 적분 예시의 analytic tail inequality 포함. No new real measurement, no producer overwrite.
- **C6:** 이번 세션 `python -m unittest discover -s tests -v` **15/15 PASS**, `python -O ...` **15/15 PASS**, `compileall` PASS. 입력 S 변조는 `-O`에서도 명시적 ValueError. `src/figures.py`에서 별도 그림 3개 생성, 실제 시각검수.
- **C7:** positive τ, 0<T≤1, π/Voigt normalization, independent Wolfram peak, Gaussian/Lorentz limits, column linearity, area/finite-window W inequality.
- **C8:** SciPy double floating integration tolerances; no MPFR rigorous enclosure or Rautian fit claim. Direct physical-accuracy significance is unavailable because original spectrum and systematic covariance are missing. Performance speedup is not sought.
- **C9:** Different-author reviewer NOT_RUN. Wolfram symbolic/independent method is different software but not different author review.
- **C10:** All code, raw-inherited source ZIP, scientific CSV, figures, tests, stage records, complete ZIP packaged. Git publication and cloud receipts are separate from local verification and do not prove scientific admission.

재현:

```sh
cd REC_HD_VOIGT_OPACITY_20261030
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q src tests
python src/voigt_opacity.py
python src/figures.py
```

기존 LOCK: parent PR164 HEAD `e050b97b7d5c6c0929062fafd7333e0164112399`, central `28/88`, REC physical `0/313`, 35Hz `FAIL7/8`, H5 epsilon null, H6/H7 open, L4=false, REI=false, production HOLD; no main/parent/source/default mutation.
