# REC-HD | 2026 Neufeld 원천 HD 15준위 CMB 복사전달과 고준위 충돌률 외삽 민감도

2026-10-30 | 독립 부속 연구단위 | source-qualified exploratory, **production HOLD**

## 0. 원본 계보와 청구권

- 기준 저장소 `cosmosapjw-quantum/rec_bianchi`, 부모 PR #169 SHA `ca80a69908a86f659849487030c47f3bd711f311`.
- 이 연구의 경로: 독립 자식 `research/rec-hd-neufeld2026-cmb15-source-locked-20261030`. 부모의 이전 PR #168 HEAD `d2b1592f1b3f02e7db721fb89b57e19868532f07`은 immutable.
- **Original Neufeld 2026 v2**: `https://zenodo.org/records/21165907` (DOI 10.5281/zenodo.21165907); 네 파일의 실제 원본 바이트를 GitHub Actions (run 41032576146)로 회수했으며 게시 MD5와 일치. 원본 원시 ZIP은 Library와 Google Drive에서 다운로드 후 SHA256/바이트 비교 대상.
- `hd_lamda.dat`: 32,592 B; SHA256 `f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb`.
- `hd_lamda_altex.dat`: 32,684 B; SHA256 `66033b44196bf8a57735b9c541c4f1c8bc8585449050dfd91152e6444d8d73ac`.
- 표준 FITS: 2,174,400 B; SHA256 `0c7753e665c9b1c58c073c82181f94c26dc6ad0b2b92a763cb4e2e83e4e3d4a1`.
- 대안 FITS: 2,174,400 B; SHA256 `1fc3588b32e1423a5c56c68df43ee0385f38f62424615971857b403bf02d45de`.
- 충돌률 문헌: Y. Wan, N. Balakrishnan, B. H. Yang, R. C. Forrey, P. C. Stancil, “Rotational quenching of HD induced by collisions with H2 molecules,” *MNRAS* **488** (2019) 381–386, DOI 10.1093/mnras/stz1735. 저자가 계산한 J<=8 고유 결과와 Neufeld의 J>8 경험적 외삽을 분리.
- 최신 모델: D. A. Neufeld, “Excitation of Warm HD and H2 and Implications for the Interstellar Deuterium Abundance,” *ApJ* **1007**, 16 (2026), DOI 10.3847/1538-4357/ae851a. Appendix A는 외삽 두 형태가 관측된 HD/H2 abundance 추정치에 미치는 변화가 작다고 기술함. 이 연구의 **극단 고온 격자 조건의 최대 냉각률 차이 35.7%**는 그 주장을 반박하는 것이 아니라 다른 물리적 관측량과 조건 범위의 민감도다.

## 1. 이론 구성: 마스터 방정식과 해석

독립 Neufeld 2026 모델의 상태 J=0..14, E_J (cm^-1), g_J=2J+1, 14개 복사선 ν_{uℓ}, A_{uℓ}, 105개 para-H2 + 105개 ortho-H2 하향 충돌률 q_{uℓ}(T)를 원본에서 가져온다. OPR=3 -> para=1/4, ortho=3/4. 온도는 원본 .dat의 정확한 표본 T={100,200,300,400,600,1000,2000,3000,4000} K만 사용한다. 이를 억지 보간하지 않는다.

\[
 C_{u\ell}=n_{H_2}\bigl(q_{u\ell}^{\rm para}+3q_{u\ell}^{\rm ortho}\bigr)/4,
 \quad C_{\ell u}=C_{u\ell}{g_u\over g_\ell}
 \exp[-(hc/k_B)(E_u-E_\ell)/T_g].
\]

배경복사 T_b = 2.72548(1+z) K, n̄_ν=1/(exp(hν/k_B T_b)-1). 진공 자유 탈출(광학적 박막) 가정 아래

\[
 R_{u\ell}^{\rm rad}=A_{u\ell}(1+\bar n),\qquad
 R_{\ell u}^{\rm rad}=(g_u/g_\ell)A_{u\ell}\bar n,
 \qquad Lp=0,\ \sum_jp_j=1.
\]

L은 column-sum-zero의 마르코프 생성자. 복사전이 u→ℓ마다

\[
 \Lambda_{u\ell}= h\nu A_{u\ell}
 \bigl[p_u(1+\bar n)-p_\ell(g_u/g_\ell)\bar n\bigr].
\]

양수는 가스의 순복사 냉각, 음수는 배경복사로부터 순흡수. 이 \(\Lambda\)는 총 충돌 냉각/가열, HD 화학 반응에너지, 실제 우주론적 열이력 IVP와 동일하지 않다.

**정확한 두준위 판별식:** \(x_g=\Delta E/k_BT_g\), \(x_b=h\nu/k_BT_b\)이고 \(n_b=(e^{x_b}-1)^{-1}\)이면, 양의 충돌·복사율에서 방사에너지의 부호는 \(\mathrm{sgn}(e^{x_b-x_g}-1)\)에 따른다. ν=ΔE/h인 일치된 선 모형에서만 정확히 \(\mathrm{sgn}(T_g-T_b)\)가 된다. Wolfram과 SymPy가 잔차 0으로 대수 검증함.

**소스 주파수 한계:** Neufeld `.dat`의 A/frequency와 인쇄된 준위에너지에서 유도한 ν_E는 최대로 **43.99609375 Hz** 다르다. 따라서 T_g=T_b에서 완전한 15준위 수치복사량이 엄밀히 0임을 주장하면 안 된다. 동일 온도 4개와 밀도 4개의 조합에서 보존한 두 소스의 최대 |Λ_net/Λ_spont|는 약 **2.2876×10^-12**였다. 이는 CDMS2011 v2 owner **원본 35 Hz FAIL7/8**을 해결하거나 재해석하는 근거가 아니다.

## 2. 실제 생성 데이터 1: 공식 FITS 전수 비교

- 각 FITS: 161개 T ×111개 n ×15준위 = **17,871** 조건; 원본 endian(>f8), NaN 유지, 6 HDU, FITS CHECKSUM 필드, 실제 SHA 검증.
- 표준 FITS NaN 항목 **18,868**, 대안 FITS **17,736**. Wolfram의 일부 `Import` 경로는 NaN을 0으로 오인시킬 수 있으므로 IEEE NaN 직접 보존.
- **13,532** 공통 조건에 15개 전준위 유한값; 나머지 **4,339** 조건은 NaN이 하나 이상이므로 합계 복사냉각 비교 **PARTIAL**, 알려진 양수 합만 lower bound로 기록.
- 두 `.dat`의 210개 source collision row 중 정확히 **54개**가 다르며, 모두 upper J>=9 영역. 원래 Wan2019 J<=8 입력에는 차이가 없다.
- 공통 완전 조건에서 표준 대비 대안의 총 자발복사 출력 상대 차이 최대 **+35.699985%**, T=3981.0717055349733 K, n=1,258,925.4117941686 cm^-3. 표준 2.314779980209179e-25 W/HD, 대안 3.141156096613036e-25 W/HD.
- `evidence/NEUFELD2026_ORIGINAL_17871_CELLS.csv`와 JSON에서 모든 셀의 원본값/NaN 마스크/하한 또는 15준위 정식 계산 구분을 재현 가능.
- 이 모델 비교는 저자가 사용한 원본 'computed' populations이며 새 관측 데이터나 실험 측정은 아니다.

## 3. 실제 생성 데이터 2: CMB 결합 독립 결과

- 원본 표준 `.dat`로 4 gas T ×4 n ×6 z = **96** 개 CMB 결합 15준위 정상상태, **1,344** 개 photon energy flow의 자발방출/유도방출/흡수/순 출력 기록. `evidence/NEUFELD2026_15LEVEL_CMB_96_STATES_1344_LINES.json`.
- 독립 표준 대안 비교: 9개 source T ×5개 n ×6개 z = **270** 공통 조건, 소스별 270개(총 540개) 양의 정상상태, **3,780** 전이별 대응쌍(소스별 3,780, 총 7,560개 광자 출력). `evidence/CMB15_STANDARD_VS_ALTEX_270_STATES.csv`, `...3780_LINE_PAIRS.csv`.
- 공통 CMB 격자의 최대 상대 냉각률 변화 **+35.738666%**, T_g=4000 K, n_H2=1e6 cm^-3, z=100. 표준 **2.204457132742227e-25** W/HD; 대안 **2.9923007073755505e-25** W/HD; ΔΛ=**+7.878435746333234e-26** W/HD.
- 최대 차이의 고준위(J_u=9..14) 전이들의 ΔΛ 합계 **+8.556238783617573e-26** W/HD (총 ΔΛ의 108.6%). 저준위(J_u=1..8) 합계 **-6.778030372843403e-27** W/HD (-8.6% 상쇄). 이는 고준위 충돌률 수정의 간접 저준위 개체수 재배치까지 포함된 결과.
- 270개 조건에서 두 소스 사이의 냉각/가열 부호 불일치 **0**. 최대 정상상태 residual ~6.13e-16 s^-1, 모든 점유수 ≥0, 정상화 각각 1 within 2e-12.
- 커다란 차이는 극단적으로 높은 T의 15준위 전체 복사출력 예측. 저온 CMB J1 line의 원래 35 Hz source qualification과 다른 관측량이다.

## 4. Blind-referee-style 적대 감사 (동일 저자, 독립 심사 아님)

이 세션에는 실제 native distinct-author subagent 생성 도구가 없어 R6/C9 external reviewer는 **NOT_RUN**. 대신 같은 세션에서 원본 신원과 물리 함의에 대한 적대적 한 번의 검토 및 다른 알고리즘 검산을 수행:

1. **SOURCE_SUBSTITUTION**: 2011 CDMS v2와 2026 HD catalog, Neufeld/Wan 모델을 뒤섞지 않음. 두 원본 `.dat/.fits` 해시·HDU·NaN·원래 54개 변경행을 고정.
2. **NAN_FAKE_POPULATION**: NaN을 0 log-population으로 바꾸면 없는 high-J 대규모 인구를 만드는 위험 차단. 공통 완전 셀 13,532에만 총 냉각률 비를 부여.
3. **LARGE_RELATIVE_RATIO_FROM_NEAR_ZERO**: CMB 넷 출력이 0 근처면 상대 오차가 과장. 원본 절대 차이와 기호를 별도 보존, 인공적 통계 sigma/p-value 부여하지 않음.
4. **DETAILED_BALANCE_MICRO_DEFECT**: 인쇄된 ν–ΔE gap 최대 44 Hz가 T_g=T_b 정확 net-zero theorem에 영향을 주는 것을 실측, 모형의 실제 소스와 엄밀한 일치 에너지 이상화를 구분.
5. **MODEL_VS_EXPERIMENT**: 17,871 온도·밀도 격자는 Neufeld 논문 계산 자료이지 독립 관측 17,871개가 아니다. 저자 관측 HD/H2 inference 결과에 고온 한점 냉각률 35.7%를 기계적으로 운반하지 않음.
6. **INDEPENDENT_ALGORITHM**: SciPy LU와 원래 M-matrix solver를 몇 개 소스 기초 상태에서 교차검산. Wolfram/SymPy 2준위 복사수지 기호 항등식 잔차 0. 동일 모델 사용자라 독립 수학 교차검사로만 표기.
7. **PREEXISTING_CI_FAILURE**: PR169 `verify-durable-backup` GitHub CI는 과거 `rec_source_synthesis_20261027` 파일의 whitespace/blank lines 때문에 실패한 것을 원격 job log에서 확인. CI PASS 아님; 이 스레드에서는 역사 데이터 대량 변경하지 않음.

**새 strong no-go 없음**. 청구 허용은 두 고정 외삽 입력에 대한 독립 조건부 물리 결과까지. H5 ε= null, H6/H7 OPEN, L4 false, REI activation false, production HOLD, AUTO_NEXT_NODE=false.

## 5. 실행·재현


a. 저장한 원본을 안전한 컨테이너에서 제공한 후 프로젝트 루트에서 아래 명령을 실행.

```
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
python -m compileall -q src tests
python src/compare_original_fits.py --input source/zenodo_v2 --output evidence
python src/hd_cmb15.py --source source/zenodo_v2/hd_lamda.dat --output evidence/NEUFELD2026_15LEVEL_CMB_96_STATES_1344_LINES.json
python src/compare_cmb_altex.py --source source/zenodo_v2 --output evidence
python src/source_frequency_audit.py --source source/zenodo_v2 --output evidence/SOURCE_FREQUENCY_BALANCE_AUDIT.json
```

b. 원본 전체 ZIP CRC와 SHA manifest를 재검증.

c. GitHub Draft PR에서 source input, code, results and ledger 복원. 원본 세부 `.dat/.fits` Git 본문은 이 새 연구 패키지에 포함. 원본 2011/CDMS blob의 역사 신원은 부모 PR169에도 보존.

## 6. 확인된 DAG 및 다음 행동

| 영역 | 종료 상태 |
|---|---|
| 현재 추가한 source CMB15/extrapolation auxiliary | 1/1 scoped COMPLETE (conditional physical calculation) |
| 새 연구 R1..R10/C1..C10 | 18/20 scoped; R6/C9 다른 저자 감사 NOT_RUN |
| REC canonical DAG | **28/88** (+0) |
| REC physical DAG | **0/313** (+0) |
| 원본 HD 35 Hz | **FAIL7/8** |
| REC-EXP-SPECTRAL | PARTIAL, 9 measured edges / rank 6 / 3 cycles |
| 생산 | HOLD / NO_MERGE / AUTO_NEXT_NODE=false |

다음에 필요한 별도 원천은 Keeyoon Sung 외, “The rotational spectrum of HD broadened by H2 at temperatures between 100–296 K”, *J. Quant. Spectrosc. Radiat. Transfer* 295 (2023) 108412, DOI 10.1016/j.jqsrt.2022.108412 의 **원 실험 spectra 및 R(0)–R(3) 주파수 중심 공동 공분산/교정계측 기록**. CDMS 2011 v2 SPFIT 파라미터의 **full-precision `.var`/correlation**도 필요. 공개 논문과 Git 원본에는 없다. 사용자가 직접 반드시 준비해야 하는 자료는 현재 없음. 저자 또는 실험 데이터 관리자에게 공동 fit/오차상관 원자료를 요청하면 본격 observational GLS gate가 진전될 수 있음.
