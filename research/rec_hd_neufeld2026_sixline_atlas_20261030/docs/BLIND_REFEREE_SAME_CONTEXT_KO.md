# Blind-referee style 적대적 감사 (동일 주체, 진짜 별도 심사위원 아님)

- **A. 출처 정합성:** 부모 PR171 원본 4개 `.dat/.fits`와 270/3,780 CSV의 SHA256을 신규 실행 전에 실제 검사했다. 부모 source generator의 CMB 전이 원천값을 fresh re-execute하여 두 CSV를 `cmp`로 동일성 확인. 2026 고준위 collision extrapolation을 2011 CDMS v2 실험 주파수 대체로 승격하지 않음. 원본 `35 Hz FAIL7/8` 보존. **판정 scoped PASS**.
- **B. 에너지/부호:** 270조건 각각 14선의 합이 각 원본 모델 총 복사출력과 정합(최대 상대 residual <3e-14). Warm 120 조건의 여섯 선 모두 양의 순복사 출력. CMB 배경에서 순복사 출력은 observer total source-independent luminosity가 아니다. **판정 scoped PASS**.
- **C. 가짜 수치 민감도:** 전체 1,800 후보를 보존, 임의 기준 \(0.1\%,1\%,5\%,10\%\)에 따른 1,662/1,512/1,272/1,198 잔류 수치를 모두 보존했다. 이를 관측 감도/노이즈로 부르지 않음. 최대 약 101% 케이스의 네 최소 출력은 자체 기준 최고 출력의 약 2.51%. **판정 PASS (model filter only)**.
- **D. 퇴화 도전:** 1000 K, z=0, true n=1e6의 표준/대안 R9/R7 +100.98% 차이는 표준 모델의 n을 2.45788배로 변경하면 재현 가능. R9/R4 heldout 차이 -21.7557%는 일부 분리 단서이나 covariance가 없으므로 source identification/검출 통계는 NOT_ADMITTED. **판정 새 물리 counterexample 확보**.
- **E. 독립 계산:** 원본 네 파일의 고정 해시 + 270×2 source energy ledger, 기존 독립 원천 solver를 실제 재실행. 별도 SciPy dense linear solver 8 source conditions에서 M-matrix 해법과 점유수 최대차 1.81e-16, 주요 선 출력 최대 상대 1.38e-14. Wolfram 2-level 양쪽 n→0/∞ source 차이 정확 0 검산. **NUMERICALLY_CHECKED**, 하지만 다른 연구자 검증 아님.
- **F. 유효범위/측정:** source T 1000..4000K, 5 densities, z0/10/30/50/73/100, OPR=3, dustless optically thin stationary. R(9)/R(7) rest wavelengths 12.4718/15.0219 µm은 z0에서 MIRI-MRS 범위지만 z≥10의 관측 파장은 그렇지 않음. 실제 JOYS flux·거리에 대한 inferred likelihood 아님.
- **G. Git transport:** 기존 sibling R9/R4 브랜치에서 CSV reader adapter가 삽입한 `<PARSED TEXT FOR SHEET>`와 인덱스 열 때문에 게시 Git CSV가 byte-locked 원본과 불일치. 이번 결과 CSV를 그 Git 파일에서 불러오지 않았고 **원본 부모 PR171의 immutable source CSV를 사용해 새로운 로컬 CSV를 구성**. 신규 Git에는 code/theory/JSON/steps 위주로 게시하고 정본 수치 CSV는 전체 source ZIP에만 수록하는 것을 우선한다.
- **H. DAG/리뷰:** Canonical 28/88 및 REC physical 0/313은 전혀 변하지 않음. R6/C9의 외부 distinct-author 검토는 NOT_RUN. GitHub quick-workflow GREEN도 현 세션에서 입증 전엔 주장하지 않음. Source-only science claims conditional, production HOLD.

**종합:** `CONDITIONAL_SOURCED_PHYSICAL_OUTPUT_SCOPED`, 새로운 15준위 비LTE 선비율·퇴화 판별량. 거짓 강한 no-go 없음, 새로운 실험 데이터 없음, 다음 node 자동 시작 없음.
