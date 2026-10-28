# REC-HD-MULTICHANNEL-AFFINITY01 | 이론·코딩 연구 결과 2026-10-29

**판정: `PASS_SCOPED_SYNTHETIC_MARKOV_DIAGNOSTIC` / 원본 HD 분광 `FAIL_7_OF_8` 및 source-choice `HOLD` 유지.**

## 최신 입력과 중복 계산 방지

현재 연구 브랜치는 마지막 REC PR#150 `aa190310e148dc9657cead0301ebf1916bf6e627`를 보호된 기준으로 사용한다. 이미 검증한 2,289 byte HD 소스 SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`와 지난 PR#150의 24개 Kirchhoff 결과를 다시 사용한다. 별도 예약된 REC PR148 132-point electron / JOINT-TANGENT01, WU PR152 R17 HD reactive rates R1(실제 데이터 미확보), REI PR252 UVB tilt S0와 결합/덮어쓰기를 하지 않았다.

관련 7개 고유 저장소(`rec_bianchi`, `rei_bianchi`, `WU088_HH`, `BASS_HE`, `bass_cr`, `bass`, `VigilODE`)에서 열린 PR 최신 30건(가능한 범위), default branch 최근 commit 다섯 건, 2026-10-28 중심 인계를 대조했다. `BASS`와 `bass`의 대소문자 URL은 동일 저장소 취급한다. 이전 대화 인계에는 일부 최근 상태가 있었으나 모든 작업 스레드의 미노출 원문/로컬 미게시 변경을 직접 검사했다고 주장하지 않는다. 이 세션 로컬 `/mnt/data`에는 타 저장소 `.git` 작업 트리가 없으며 runtime `PYTHON_PASS` 확인. 두 기존 SOURCE의 Drive+Dropbox size readback 성공을 재조회했다. 원격 내용 SHA256 재다운로드는 NOT_RUN.

## 새 유도와 원본 9×9 계산

원래 고정 LAMDA 소스에서 9 rotational J states / 8 radiative lines / para/ortho-H2 각각 9 downward collisional pairs를 얻었다. 실제 2→0 충돌선이 존재하므로 radiative 0↔1, 1↔2와 삼각형을 이루어 두 종류의 출처 에너지 숫자가 동시에 있을 때의 cycle-affinity를 구성할 수 있다.

- 2-edge loop: `A_J=-h[c100(w_J-w_(J-1))-ν_J]/(k_BT)` (ν는 Hz로 변환). 두 충돌 partner는 같은 T에서 동일한 부호·친화도.
- 3-edge triangle `0→1γ,1→2γ,2→0coll`: `A_tri=-A_1-A_2`.
- 기존 Kirchhoff 비율 K의 새 정확 항등식: `K=(exp(A_J)-1)/(1-exp(-ΔE_J/(k_BT)))`. Wolfram `FullSimplify` 결과 정확히 0.
- 채널별 rates와 원본 A 및 collisional q를 사용하여 모든 T={50,100,200} K, 시험밀도 `n_p=n_o=10³,10⁶ cm⁻³`의 6개 조건에서 9×9 정상상태 확률분포를 계산했다. 지정 밀도는 **수치 실험 조건**이며 실제 재결합/재이온화 시나리오로부터 얻은 값이 아니다.

| T (K) | n_p=n_o (cm⁻³) | 형식적 σ/k_B (s⁻¹ per synthetic molecule) |
|---:|---:|---:|
|50|10³|9.45214643045×10⁻²³|
|50|10⁶|7.97264065721×10⁻²²|
|100|10³|8.50303839188×10⁻²²|
|100|10⁶|7.18173136949×10⁻²¹|
|200|10³|1.34581720506×10⁻²¹|
|200|10⁶|1.41223356244×10⁻²⁰|

**σ는 오직 synthetic Markov network의 형식적 Schnakenberg 생산 진단**이다. 실제 온도 이력이나 물리적으로 일관된 진동/회전 소스의 엔트로피 생산률이 아니다. 원래 소스의 불일치가 가상의 두 동온 bath 결합 시 artificial circulation을 만드는 것을 입증한다. `ν=ΔE/h`로 변경한 **별도 negative-control** 모형에서는 균형 분포가 해석적 Boltzmann 분포와 일치하고 σ≈0이지만, 이 대조 입력을 실제 원자료 보정으로 채택하지 않는다.

## 실행·독립 수치검증

- 90-digit mpmath 6/6 stationary PASS. Maximum direct-rate cycle-affinity abs error `1.03047436239e-89`, maximum steady generator abs residual `1.02766092071e-95 s^-1`, previous saved 24 Kirchhoff values maximum abs difference `3.10692852415e-79`.
- Original vs synthetic equal-energy entropy rates: 6/6 source σ>0, 6/6 synthetic σ near zero (`~10^-155` to `10^-184` in saved outputs), not physical bounds.
- Independent implementation (`independent_validate.py`): NumPy Float64 six 9×9 systems versus mpmath populations maximum abs difference `8.32667268469e-16`, Decimal100 raw-literal affinity difference `3.46336396868e-61`. This is **different numerical method on the same declared source**, not independent physical review.
- `test_multichannel.py`: 10/10 targeted tests; source SHA/row labels/collider types/2→0 edges/corruption/unsupported temperature/polarity/triangle/gate guards.
- Figure reads saved RESULT only, plots discrete sampled temperatures/levels without continuous interpolation. No raw LAMDA file is duplicated into public Git due to unresolved licensing; it is carried in user-authorized private SOURCE backup.

## Status and remaining work

Canonical `28/88 +0`; physical `0/313`; H5 epsilon null, H6/H7 OPEN, L4=false, REI activation=false, production HOLD. WU H-Li 26 ground+5 nuclear,102 formal requests ≠ active physics; 621 missing process cells stay null. Fresh R6/C9 native nonauthor reviewers `NOT_RUN_TOOL_NOT_EXPOSED`; source archive CDMS2011 version2 `.cat/.egy/.par` `NOT_ACQUIRED`. This new conditional math/coding output is completed, **not** the original HD energy-resolution gate.

Next scientific operation: acquire original CDMS v2 catalog/term-energy/fit numeric files and source-to-LAMDA transformation procedure with immutable bytes, uncertainties and J-identity; only then propose an evidence-backed replacement, fixed 35Hz gate, and scoped thermal recheck. Avoid automatic new main merge, native IVP and rollback/replay of previous H5 or HD campaigns.
