# REC 보충 로컬 실행 반환

STATUS=PASS_SELECTED_LOCAL_LANE_NOT_FULL_CLOSEOUT
WORK_UNIT=REC_MULTI_BIN_AFFINITY_COMPATIBILITY_RESEARCH
SLICE=LOCAL_NULLSPACE_COMPLETION
REPOSITORY=cosmosapjw-quantum/rec_bianchi
RESULT_BRANCH=results/rec-multibin-local-20260907T070853Z

새 **4개 TestID / 16개 방향**을 로컬에서 한 번 실행했다. 모든 TestID PASS,
failure/error/skip 0, 실제 child returncode 0, wrapper exit 0이다.
PR79의 완료된 7개 그룹 / 84개 방향은 고정 Git readback으로 재사용했고
재실행하지 않았다. 새 11개 검사 실행, 전체 repository PASS 또는 물리 solver
승인으로 합산하지 않는다.

## 실행과 게시 identity

| 역할 | Commit | Tree |
|---|---|---|
| 실제 수치 실행 및 renderer | 9195f94bf308806ae6e9070f6175b500a1c2ef53 | 98577a94604efff77c24b89ee3a56a99fd478f16 |
| 고정 V2 delivery | 69fd88bce475fa57a3c2323bb3e939c35a76bf20 | 문서 전용 child; 실행 source와 구분 |
| 원격 readback을 완료한 결과 게시 | 7941bac2751778136322806e34b46320192f2d5f | fc6b6c304573e9819fe97def577d0b5a0435f0b8 |

V2 handoff Git blob은 `5b4b87fad9b7d2ccaa81e036555e1ca7e6d59a2f`와 일치한다.
이 반환문과 원격 확인 기록은 위 결과 게시 commit의 **문서 child**에 추가된다.
최종 반환문 commit/tree는 최종 응답과 이 문서의 immutable Git URL에서 별도로
고정한다. 어느 결과/반환문 child도 수치 실행 source로 부르지 않는다.

원격 결과 commit/tree와 31개 파일의 Git blob을 대조했고, PROCESS, RESULT,
CSV, stdout JSON wrapper, RENDER_RECEIPT는 Contents API로 실제 바이트도
다시 읽어 로컬과 일치함을 확인했다. [REMOTE_EVIDENCE_READBACK.json](REMOTE_EVIDENCE_READBACK.json)
참조. 모든 새 commit에 `[skip ci]`, 자기 branch에 non-force push를 적용했다.
Actions 실행·조회·다운로드·dispatch 0회다. 새 PR은 만들지 않았으며
기존 Draft PR79/80, main과 공유 source branch에 쓰지 않았다.

## 실제 실행 및 원본 자료

실행 interpreter는 `/home/cosmosapjw/cosmo_lab/.venv/bin/python`, Python 3.12.3이다.
NumPy 2.3.5, SciPy 1.18.0, SymPy 1.14.0, mpmath 1.3.0, Matplotlib 3.11.0의
실제 module 경로는 [syntax_environment.log](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/syntax_environment.log)에 있다.
설치·업그레이드 없이 기존 환경을 사용했다. 원래 Python 3개와 새
run_local/verify_nullspace/plot_supplement의 6개 `compile()` 검사는 모두 exit 0이다.
이는 수치 검증과 별도다.

```text
python -B run_local.py
  --expected-source 9195f94bf308806ae6e9070f6175b500a1c2ef53
  --python /home/cosmosapjw/cosmo_lab/.venv/bin/python
  --only supplement --out <RUN_ROOT>/evidence/attempt01
```

정확한 실제 argv/cwd/source/tree/시간/종료는
[PROCESS.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/evidence/attempt01/supplement/PROCESS.json),
[LOCAL_RETURN.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/evidence/attempt01/LOCAL_RETURN.json)에 있다.
child는 2026-09-07 07:10:05.563402–07:10:10.841983 UTC에 실행했고 timeout은 없다.
[TestID별 원본 unittest.log](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/evidence/attempt01/supplement/payload/unittest.log),
[원본 RESULT.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/evidence/attempt01/supplement/payload/RESULT.json),
[16행 CSV](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/evidence/attempt01/supplement/payload/ADDITIONAL_JVP.csv)를 보존했다.
원본 raw 경로는 `/home/cosmosapjw/research_runs/rec_multibin_supplement_nv9sfjkn`이다.
기존 checkout의 dirty/untracked는 실행 worktree에서 분리해 보존했다.

| 실제 TestID (`__main__.Checks.` 접두사) | 결과 |
|---|---|
| test_01_full_left_kernel_and_energy_dependence | PASS |
| test_02_actual_count_source_and_density_direction | PASS |
| test_03_stationary_manifold_and_four_right_null_vectors | PASS |
| test_04_missing_photon_axes_against_independent_primal | PASS |

새 source 복제·수치 source 수리·TestID/허용오차 변경은 0건이다.
[IDENTITY_CHECK.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/IDENTITY_CHECK.json)은 원래 Python 3개, src/tests/archive,
원본 표·입력, 이전 연구 및 workflows의 Git identity 불변을 기록한다.
빈 [SOURCE_REPAIR.diff](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/SOURCE_REPAIR.diff)는 수치/표시 source 변경이 없음을 뜻한다.

## 네 보존량과 kernel 관측

count 순서는 `(xu,xg,beta0*f0,...,beta4*f4)`, `beta=mu/nH`다.
네 좌영벡터는 다음과 같다.

```text
L0=(1,1,0,0,0,0,0)
L1=(2,0,1,1,1,1,1)
L2=(0,0,1,0,0,0,-1)
L3=(0,0,0,1,0,-1,0)
energy = L1/2 + (2^-30-1/2)*L2 - L3/4
```

두 표 모두 exact rational rank L=4, rank V=3이다. 실제 witness bin은
base `[0,1,16]`, hires `[0,1,34]`; rounded API stencil의 최대 `|LV|`는
둘 다 `2.220446049250313e-16`이다. 7개 count 변수의 이상적 nullity는 4이며,
에너지를 다섯 번째 독립 보존량으로 세지 않는다. Exact 유리수 증거와
binary64 잔차를 구분한다.

count 미분은 `beta*(dC-C*dnH/nH)`다. 실제 네 count 보존식과 JVP를 확인하고,
두 번째 항을 생략한 진단식이 고정 `1e-6` 검출 기준을 넘음을 관측했다.

| 표 / 읽기 | 최대 count-source 잔차 | 최대 count-JVP 잔차 | beta density 미분 생략 잔차 |
|---|---:|---:|---:|
| base / chi | 0 | 2.220446049250313e-16 | 0.0917349247581768 |
| base / log control | 5.551115123125783e-17 | 1.1102230246251565e-16 | 0.06067375045771051 |
| hires / chi | 2.7755575615628914e-17 | 3.3306690738754696e-16 | 0.09170457522150821 |
| hires / log control | 5.551115123125783e-17 | 2.220446049250313e-16 | 0.06066165036768523 |

고정 제조 비열적 정상상태 `chi=(0.5,0.875,1,1.125,1.5)`에서 원래 API의
7열 count Jacobian을 사용했다. `W^-1 L^T`의 네 우영벡터와 별도의
`(kappa,p,q,A)` 네 정상상태 접방향을 모두 검사했다.

| 표 | net event rate per H [s^-1] | 최대 right-kernel 잔차 | 네 접방향의 최대 bin 잔차 (kappa,p,q,A) |
|---|---:|---:|---|
| base | 3.361042616572825e-17 | 6.019896772778457e-16 | 7.209746973095204e-17, 4.289768658820805e-18, 1.5658921442211526e-17, 3.672855271951851e-17 |
| hires | 1.5737025127037646e-17 | 4.688876422902089e-16 | 7.245361157062312e-17, 9.59023286480393e-19, 6.490291900572396e-18, 3.160864265004778e-17 |

전체 7×7 Jacobian은 RESULT에 있다. 이 결과는 제조 5-node / 해당 채널의
국소 검사다. 전체 물리 Planck 유일성, interior equilibrium 존재, 전역
수렴률 또는 시간 적분기 안정성의 증명이 아니다.

## 추가 photon 16방향과 그림

정규화 계수, 하나의 명시적 비평형 상태에서 두 표 × 두 읽기 ×
`y0,y2,y3,y4`의 16개 방향을 검사했다.

- 최대 scaled JVP 오차: `8.49796017985836e-17`.
- 최대 scaled primal 오차: `1.1210599110571854e-16`.
- 고정 scaled 허용치: `4096*epsilon = 9.094947017729282e-13`.
- 80/120자리 차이 최대: `3.55027848540387402878677e-72` < `1e-60`.
- 중앙차분 h=`2^-32`/`2^-36` 차이 최대: `1.035879669964794620384395e-20` < `1e-16`.

scaled 값은 테스트의 고정 수치 단위에서 `abs(error)/(1+abs(reference))`다.
고정밀 primal은 원래 독립 구현을 재사용했다. 16개의 방향 벡터 사례는
16개 독립 unittest나 전 정의역 검증을 뜻하지 않는다.

renderer는 이 성공 lane의 **저장된 CSV**와 RESULT/PROCESS만 소비해 exit 0으로
[90mm PNG](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/figures/attempt01/additional_jvp_90mm.png)와
[180mm PNG](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/figures/attempt01/additional_jvp_180mm.png)를 생성했다.
두 PNG를 Host Codex가 실제 열어 축·범례·잘림·겹침·축소 가독성을 확인했다.
90mm/180mm 모두 읽을 수 있고 잘림은 없다. y2와 일부 y4에서 가까운 값의
겹침은 CSV와 일치하며 marker/선형태와 범례로 구별된다. 선형 y축은 실제
0에서 시작하며 양의 log floor를 넣지 않았다. 이번 16개 기록값은 모두 양수다.

[RENDER_RECEIPT](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/figures/attempt01/RENDER_RECEIPT.json)의 세 입력 SHA256을
원본과 대조했다. 수치 검사 재실행 없이 렌더 1회, 표시 수리 0회다.
[VISUAL_REVIEW.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/VISUAL_REVIEW.json)은 별도 후속 시각검토 기록이다.
원본 RESULT/PROCESS/RENDER의 작성 당시 `visual_audit=NOT_PERFORMED`를 소급
수정하지 않았다. 이 그림은 binary64 오차 진단이며 grid-convergence,
물리 시간진화 또는 80자리 구현 정확도 그림이 아니다.

## PR79의 재사용과 미완료

재사용한 원래 결과는
[고정 OBSERVED_RESULT.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/0db9612b8c1fb2c6c8119f23138ff5efe54fcc06/docs/research/rec_multi_bin_affinity_20260907/OBSERVED_RESULT.json),
blob `a3244d115b7fc5f17b70a14af5aefc4c3b36aad3`다.
record-kind는 `STRUCTURED_READBACK_OF_HOSTED_JOB_SUMMARY_NOT_ORIGINAL_RESULT_BYTES`다.
원래 실행 source/tree는 `2e3b73972ee298d44efdfb10016e314f58b0bada` /
`471442ce757fde701340729cd1abde281fd0db01`이다. 그 기록의 7개 TestID PASS,
exit 0, 84개 방향 최대 오차 `6.4310422961310704e-15`를 재사용한다.
이전 결과의 Python 환경과 이번 로컬 환경은 동일 환경이라고 주장하지 않는다.
원래 계산 Python 3개와 보호 source/input bytes는 동일하다.

기존 structured readback의 같은 제조 상태에서 nodal entropy율은
base chi `+0.00028173611409276625`, log control `-0.0002603135345552853`,
hires chi `+0.00028167186474992016`, log control `-0.0002601446373071536` s^-1이다.
log read-proxy는 각각 `+0.0005270804852294076`, `+0.0005284552517908059`다.
Delta_eff는 base `0.02238493049350998`, hires `0.02237953745029886`이다.
원시 계수 합은 `8.2245807524349` / `8.224707551416` s^-1,
정규화 합은 `8.2206` / `8.220599999999997` s^-1이다.
이 수치는 이번 새 계산이 아니며 bin별 원본 CSV 바이트 수령을 대신하지 않는다.

원래 7개/84개를 재실행하지 않았고 과거 네 결과 문서를 이 branch에
병합했다고 주장하지 않는다. 제한된 기존 로컬 경로 검색에서 PR79 원본
ZIP/PNG를 찾지 못했다. 전체 filesystem 부재 판정은 아니다.
**역사적 raw artifact 바이트 수령, 전체 member manifest 인증 및 원래 두 PNG
시각검토는 미완료**다. 새 PNG를 역사적 artifact 복구본으로 부르지 않는다.
Actions로 자료를 조회하거나 회수하지 않았다.

## 최초 실패, 수리 및 review

이번 numerical/syntax/render 실패는 없다. 원본 최초 실행 결과를 그대로 보존했다.
게시 전 `git diff --cached --check`는 raw stdout 끝의 빈 줄 하나 때문에
exit **2**였다. [최초 출력](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/PUBLICATION_DIFF_CHECK.stdout)과
[PACKAGING_REPAIR.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/PACKAGING_REPAIR.json)을 보존했다.

raw stdout의 공백을 제거하지 않고
[stdout.log.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/evidence/attempt01/supplement/stdout.log.json)에 UTF-8
문자열로 가역 보존했다. `content.encode('utf-8')`가 로컬 원본 바이트와
완전히 같고 original SHA256/byte 수가 일치함을 확인했다. 나머지 원본 로그,
PROCESS/RESULT/CSV/PNG와 원래 manifest는 byte-identical이다. raw manifest의
stdout 항목은 이 문자열을 원래 경로로 복원한 뒤 검증한다. 최상위 SHA256SUMS는
실제 게시 파일(wrapper 포함)을 검증하는 별도 포장 manifest다.
복원 바이트와 원래 manifest를 재검사했고 공백 검사는 후속 exit 0이다.
공백 gate 제외·수치 테스트 재실행·허용오차 변경은 하지 않았다.

[독립 read-only 과학/source 검토](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/INDEPENDENT_REVIEW.md)는 1회 PASS,
범위 내 CONCERN/FAIL 0건이다. reviewer는 새 numerical/render 실행을 하지
않았으며 관측 증거와 수학·source를 검토했다. review-of-review는 하지 않았다.
[VALIDATION_MATRIX.md](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/7941bac2751778136322806e34b46320192f2d5f/docs/research/rec_multi_bin_local_completion_20260907/local_returns/20260907T070853Z/VALIDATION_MATRIX.md)에 항목별 한계를 구분했다.

## 남겨 둔 과학적 경계

NO_PASS_REC_PHYSICAL_SPLIT
physical_source_authenticated=false
provider_admitted=false

현재 수용 상한은 제조 고정-grid 다중-bin affinity/JVP 및 네 kernel 보존량이다.
실제 B/mu·physical source/provider, 전체 repository/solver, BASS evolution,
원본 C/history, 이동 map·각도/편광·시간진화와 물리 수렴은 검증하지 않았다.
다음 연구 `REC_TARGET_GRID_REFINEMENT_WITH_FIXED_REFERENCE_MEASURE`는 시작하지 않았다.
주 대화는 이 고정 결과를 읽고 별도로 과학적 수용과 다음 연구를 판단한다.
