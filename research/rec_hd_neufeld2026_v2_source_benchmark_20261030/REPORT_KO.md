# REC HD: Neufeld(2026) 원본 15준위 source benchmark (2026-10-30)

**프로젝트** `cosmosapjw-quantum/rec_bianchi` · 부모 <https://github.com/cosmosapjw-quantum/rec_bianchi/pull/168> HEAD `d2b1592f1b3f02e7db721fb89b57e19868532f07` (불변). 본 단위는 원본 소스 획득과 실제 HD 물리 데이터 재현을 우선하는 추가 독립 연구 브랜치이다.

## 1. 실제 근거 데이터와 새 산출물

- 공식 Neufeld(2026) Zenodo v2 원본 HD `.dat` **32,592B**, MD5 `c45c4740011df579a973a7c336c5bc22`, SHA-256 `f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb` 실제 확인. 원본 15개 HD J-level, 14개 spontaneous emission A/f pairs, para-H2/ortho-H2 각 105개 collider transition, 9개 원래 온도 노드. 고 J(>8)는 소스 저자의 외삽, 측정이라고 부르지 않는다.
- Neufeld FITS 원본 **2,174,400B**, 공식 MD5 `3fffb1591b0f96b254210ed54599667a`, SHA-256 `0c7753e665c9b1c58c073c82181f94c26dc6ad0b2b92a763cb4e2e83e4e3d4a1` 원격 커널 검증. 전체 161×111×15 grid; **원본 FITS의 로컬 백업/전체 Git 게시까지 완료한 것은 아님.** 원본 10개 selected grid cell의 과학값과 이 중 T=100 K 5개 검산을 Git에 보존.
- 2021 Leiden LAMDA 원본 `hd.dat` 2,289B, 2011 CDMS historical SPFIT `.fit/.par/.lin/c003501i.cat/.egy` 전부 공식 서버 실제 바이트 SHA 확인 후 Git blob으로 저장. 2019 수정된 `c003501.cat` 또는 2026 v3을 혼동하지 않는다.
- 2021 Flower/2026 Wan 원본에서 **36 matched rate rows**, **10 J1 원천 비교 물리 출력**, 원본 2026 소스 기반 **45개 15준위 정상상태 물리 조건 × 정확 SI 및 원본 FITS 재현 컨벤션 = 90개의 구별된 계산**, 각 컨벤션에서 **630개 spontaneous line powers**. 모든 45조건의 nonnegative population, sum p≈1, master equation residual 검증.

## 2. 주요 수치 결과 (source-bound 계산)

원본 2026 FITS `T=100K, nH2={100,1e4,1e6,1e8,1e10} cm^-3`의 준위점유수를 별도 M-matrix solver로 계산하였다. `J=0..6` source-available 비교에서 SI exact `hc*100/k_B=1.4387768775039336 K cm` 사용시 최대 점유수 절대차 `6.413771957425318e-6`; `1.4388 K cm` 사용시 `4.345084292367574e-10`. 이로부터 source-generation conversion convention에 관한 *reproduction-supported inference*를 얻지만 저자코드 동일성은 미확인이다. 두 컨벤션의 total radiation power 변화 최대 상대크기는 선택 45격자에서 `4.53215527270745e-5`.

2021 Flower→2026 Wan의 source-matched J1 de-excitation q는 OPR3에서 100K `2.7e-11`→`2.310275e-11 cm^3/s`, 200K `3.9e-11`→`3.451475e-11`; corresponding critical `A/q`는 100K `2015.56`→`2355.58 cm^-3`, 200K `1395.38`→`1576.73`. 독립 2-level vacuum J1 line spontaneous power at `nH2=1e4 cm^-3`: 100K `3.94349294e-29`→`3.87863371e-29 W/HD` (ratio 0.983553), 200K `5.60233551e-29`→`5.56524930e-29 W/HD` (ratio 0.993380). 15-level reference model and J1 two-level simplification are **different model scopes**.

`HD.fit` printed parameter standard deviations and correlations give rounded **approximate** parameter correlation matrix min eigenvalue `1.084863573e-5`, condition number `4.03721350e5`. Full exact historical SPFIT `.var` covariance **NOT_ACQUIRED**, Sung between-line covariance **NOT_ACQUIRED**; cannot invent sigma / chi-square.

## 3. 이론–구현–검증 연결

이론: `C_down = n [(1-f_o)q^p + f_o q^o]`; `C_up=C_down (g_u/g_l) exp[-100 hc(E_u-E_l)/(k_BT)]`; stationary `L p=0`, `1^T p=1`. Source n-level Markov generator positive normalization via `-L_TT w=L_T0` M-matrix. Zero external CMB and optically thin spontaneous-line luminosity per HD `Σ p_u A_ul hν_ul`. `src/neufeld15.py` implements exact source file SHA256 lock, LAMDA parsing, rate assembly, M-matrix and emission ledger, and produces 45×2 physical case data given the historical original `.dat` file in a clone with network or already checked-out Git source. Source access instructions are in `README_REPRODUCE.md`.

실제 검증: Wolfram original 15-level one-case stationary solver and JS V8 source-original 45×2 physical cases with M-matrix positivity and 5 author FITS comparisons executed; new standalone Python code passes **12/12** synthetic+J1 source-derived contract tests under normal and `python -O`, `compileall` PASS. The local container had no external network, so **Python full 15-level original data-run is NOT_RUN in this container**; its full 15-level source-matched output is proven by the separately executed JS tool computation and Git numerical evidence, not falsely relabeled Python-run. One author model in two languages is not distinct-author R6 or C9.

## 4. DAG 및 보호 계약

Original 2011 CDMS owner source 35Hz **FAIL7/8** unchanged. `REC_EXP_SPECTRAL` **PARTIAL, 9 measured equations, rank 6, 3 cycles** unchanged. Canonical **28/88 (+0)**, REC physical **0/313 (+0)**, owner H5 epsilon `null`, H6/H7 `OPEN`, L4 `false`, REI activation `false`, production `HOLD`. A separate scoped `NEUFELD2026_ORIGINAL_SOURCE_BENCHMARK=1/1` is supported by input acquisition, 36 rate comparisons, 45 physical samples, FITS 5/5 source match; this is **NOT a canonical or owner REC physical DAG completion**.

## 5. 이어할 일

Neufeld original full FITS must be copied into the persistent archive if complete source-inclusive reproduction of the 161×111×15 grid is required; independent same-author benchmark has only five checked 100K cases, and more source points with true NaN preservation can be checked. Retrieve full-precision CDMS2011 SPFIT `.var` or equivalent provenance if available and Sung raw experimental cross-line calibration covariance. Examine whether the `1.4388 K cm` convention comes from original Neufeld solver via published code before attributing it. Need distinct-author R6/C9 and owner consent for any future production use. **No merge, production change, original gate relaxation or auto next node.**
