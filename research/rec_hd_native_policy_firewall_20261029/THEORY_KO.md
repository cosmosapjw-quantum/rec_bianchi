# REC_HD_NATIVE_POLICY_FIREWALL01 | 이론 연구 R1–R10

2026-10-29 KST. Owner REC; frozen parent PR #156 `8806a4f757d916b6cf040625be931a66e2f0f6fe`, tree `7254269c5f8bcb198638f542d2d4545ecd647d20`. NEW results are source-scoped, not physical-source choice or production.

## R1, R2. 목표와 문헌·원본 맥락

기존 PR156의 selected 9-file matrix보다 넓은 rec_bianchi tree에서 HD LAMDA 실제 소비자 `research/program_expansion_20261025/hd_adapter/lamda_hd.py`를 발견. Git blob `632a8a094e7eedd24a1ec3132fec20765d6e39da`. 해당 함수는 실제 `line_coefficients`, `einstein_B`, `thermal_line`로 인쇄 주파수 ν_P를 소비한다. `require_energy_frequency_bridge`는 독립적으로 존재하지만 `line_coefficients`의 default 호출 경로에서는 호출되지 않는다. 연구용 관측량 계산과 matter–photon source 결합 승인 사이에는 명시적인 조건을 추가할 필요가 있다.

LAMDA HD `hd.dat` (2021-06-07) 2289 bytes SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`. CDMS v2 Dec2011 원바이트 미확보, 공식 archive index만 확인. 현행 CDMS v3 Aug2026 설명은 v2가 현저히 개정되었다고 명시하며, v2와 동일시할 수 없다. LAMDA HD page에는 v=1까지라는 설명이 있으나 원본 9개 J 라벨의 진동상태 배정에 대한 사용자 검증은 보류한다. Drouin et al. (2011), Cozijn et al. (2022), CDMS Müller et al. (2001/2005)는 출처 이해에 쓰되, 원본 v2 필드와 2022 관측을 자동 혼합하지 않는다.

## R3. 물리 계약

Signature (-,+,+,+), local matter frame, ordinary frequency. h=6.62607015e-34 J s, c=299792458 m s^-1, k_B=1.380649e-23 J K^-1. ν_E=100c(w_u−w_l), ν_P=10^9 ν_print,GHz. ν_E−ν_P의 35 Hz 고정 반올림 gate는 8선 중 1선 통과, 7선 실패. 이는 spectroscopic measurement uncertainty와 다르다.

연구용 line-source 객체와 matter–photon coupled source로 physical admission된 객체를 구별한다. 후자에는 원본 source pin + 그 전이의 owner-owned `require_energy_frequency_bridge` 통과 + 이후 독립 physical source-choice gate가 추가로 필요하다. 최초 두 조건의 통과도 물리적 출처 인증을 의미하지 않는다.

## R4–R5. 주파수 정책에 따른 정확한 라인 계수 변환

동일한 Einstein A_ul, population (n_u,n_l), g_u/g_l, 같은 국소 matter frame, 동일한 주파수당 정규화된 선형상 φ_ν *값* 및 α_ν≠0을 고정한다. J_ν에 작용하는 Einstein B 관례에서는

\[
B_{ul}(\nu)=A_{ul}c^2/(2h\nu^3),\quad B_{lu}=(g_u/g_l)B_{ul},\quad
j_\nu=(h\nu/4\pi)n_uA_{ul}\phi_\nu,\quad
\alpha_\nu=(h\nu/4\pi)(n_lB_{lu}-n_uB_{ul})\phi_\nu.
\]

정책에 따라 ν′=ν+δν>0, r=ν′/ν를 택하면

\[
\frac{B'_{ul}}{B_{ul}}=r^{-3},\qquad
\frac{j'_{\nu}}{j_{\nu}}=r,\qquad
\frac{\alpha'_{\nu}}{\alpha_{\nu}}=r^{-2},\qquad
\frac{S'_{\nu}}{S_{\nu}}=r^3,
\quad S_\nu=j_\nu/\alpha_\nu.
\]

작은 ε=δν/ν에서 민감도는 (-3,+1,-2,+3)ε. 동일한 profile **값**을 고정하는 이 조건부 결과는 PR155의 고정 Doppler velocity-width에서 *각자의* 선중심 φ∝ν^-1일 때 j_peak∝ν^0, alpha_peak∝ν^-3인 항등식과 모순되지 않는다. 진동자 강도 A, pop, frequency-grid sampling, profile width, stimulated emission 정책 등을 동시에 바꾸면 이 정리는 적용 불가. 또한 ν_E≠ν_P인 mixed model을 주파수만 바꾸어 에너지 장부를 복구한다고 주장하지 않는다.

### Source-energy ledger 보존

\[
\mathcal Q_{m+\gamma}=h\sum_{u\ell}(\nu_P-\nu_E)R_{u\ell}.
\]

추가 heat term을 만들지 않는다. 최대 절대 per-event coefficient는 J6→5의 1.210962399179234431758e-27 J/event (PR156에서 재사용). 물리 열생성률·관측 불확실성 아니다.

## R5 추가: 공분산 미확보 시 SD의 가능한 범위

같은 joint spectroscopy fit에서 upper/lower term 에너지 주변 표준편차 σ_u,σ_l(cm^-1)가 주어지고 유한한 분산·양의 준정부호 공분산만 가정하면

\[
100c|\sigma_u-\sigma_l|\le \operatorname{SD}(\nu_E)
\le 100c(\sigma_u+\sigma_l),
\]

이는 \(\operatorname{Var}(w_u-w_l)=\sigma_u^2+\sigma_l^2-2\operatorname{Cov}(w_u,w_l)\)와 Cauchy–Schwarz에서 직접 유도. Gaussian/independence 가정 불필요. 실제 CDMS .egy 원자재와 fitting covariance 미확보여서 이 범위는 **실제 측정 오차**도, confidence interval도 아니다. 35Hz gate의 보정 또는 완화에 쓸 수 없다.

## R6–R10. 판정과 연결

- R6: 같은-context 수식·부호/단위 검토 + Wolfram symbolic은 수행. 진짜 별개 저자·subagent 검토 `PARTIAL_NONAUTHOR_NOT_RUN`.
- R7: Wolfram stateless kernel에서 exact ratios, covariance extrema, synthetic rate residual 항등식 0 확인. Python 19개 단위 검증 및 독립 Fraction/Decimal synthetic 변형 7개.
- R8: 연구용 HD callsite 추가 증거와 유도된 conditional ratios를 `SCOPED_DERIVED`로 채택. 실제 데이터 승인 불가.
- R9: source-byte-pinned 오직 opt-in `guarded_line_coefficients` interface를 컴퓨터 형태로 지정. 기존 함수 또는 기본 production path 수정 불가.
- R10: 아래 CODING_KO.md, RESULT.json, STAGE_LEDGER.json과 HANDOFF_NEXT_THREAD_KO.md에 고정.

남은 핵심: 2011 CDMS v2 byte+SHA+QN/TAG/uncertainty, LAMDA lineage 및 전체 native/generated dynamic call graph, 실제 별개 저자 R6/C9. 중앙 DAG 28/88(+0), REC physical 0/313(+0), source35Hz FAIL7/8, H5 ε=null, H6/H7 open, L4/REI false, production HOLD.

### 1차 출처
- https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/
- https://cdms.astro.uni-koeln.de/classic/general
- https://cdms.astro.uni-koeln.de/cgi-bin/cdmsinfo?file=e003501.cat
- https://home.strw.leidenuniv.nl/~moldata/HD.html
- https://github.com/cosmosapjw-quantum/rec_bianchi/blob/8806a4f757d916b6cf040625be931a66e2f0f6fe/research/program_expansion_20261025/hd_adapter/lamda_hd.py
