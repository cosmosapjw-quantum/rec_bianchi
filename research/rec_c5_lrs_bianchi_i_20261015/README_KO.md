# REC C5/C6: 실행 가능한 축대칭 Bianchi I finite-clock 배경 모듈

선택 coding 단계: C5(실제 구현) + C6(타깃 로컬 실행 검증), 2026-10-15 KST.
핵심은 `src/full_bianchi_hyrec/background/axisymmetric_bianchi_i.py`를 실제 REC Python 패키지에 추가하고, 정식 `background/__init__.py`에서 export한 것이다. 이전 R7B–R9 증보만 반복하지 않는다.

## 물리 범위와 정확한 의미

`ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2`, `L=ln(a/a_ref)`, `s=db/dt=q_ref H_F(a_ref)(a_ref/a)^3`. `PhysicalDensityFixed`에서 `H²=H_F²+s²`, `SameHDiagnostic`에서는 `H=H_F`을 사용하는 명시적 counterfactual이다. 두 경우 `dt/dL=F=1/H`, `db/dL=sF`. `t_ref_s=0`은 a_ref 절편의 경과 proper seconds 원점이며 절대 나이가 아니다. 기본 선택값 a_ref=1/21, a_end=1/5, H0=67.4 km/s/Mpc, Ωm=.315, Ωr=9.2e-5, ΩΛ=1-Ωm-Ωr은 native REI 원 source expression과 대응한다.

구현은 동일한 F cubic-Hermite positive-rate approximation을 1024 또는 2048개 고정 cell에서 사용한다. 매 호출 `a1,a2`의 실제 binary64 endpoint로 `ΔL=log1p((a2-a1)/a1)`를 계산하고 cell마다 `Δt`와 `Δb`를 직접 적분한다. `Δb`는 s가 지수적으로 변한다는 사실을 이용해 작은 지수 모멘트의 22항 Taylor 수치 급수를 사용한다. 정확한 노드·미분 조건의 R7B ideal bound는 존재하지만 **이 구현의 모든 binary64 연산까지 검증된 rigorous bound라고 주장하지 않는다.**

`snapshots(eta_grid)`로 `BackgroundSnapshotSequence`의 정식 배열을 생성한다. N=A=Ω(frame)=β=0, sigma=diag(-s,-s,2s), q_dec=-1-(1/H)dH/dL이다. `normal_frame_characteristic` 및 기존 snapshot consumer에서 실제로 읽을 수 있도록 연결했다. `axisymmetric_photon_map`은 collisionless finite null energy, direction, solid-angle Jacobian만 제공한다. Recoupled full HyRec chemistry, Einstein anisotropic stress backreaction, true observer tau or polarized Thomson은 현재 제공하지 않는다.

## 실제 실행 계약

REC 저장소 루트에서 시스템 Python (NumPy·SciPy·mpmath·pytest 설치)으로:

```bash
python3 -m pytest tests/background -q
python3 -m pytest tests/trajectory/test_primitive_trajectory.py tests/trajectory/test_causal_characteristic_history.py tests/trajectory/test_accepted_parent_provenance.py -q
PYTHONPATH=src python3 scripts/validate_axisymmetric_clock_bridge.py \
  --input /ABS/R8/SAMPLED_STEPS.csv \
  --summary /ABS/R8/SAMPLED_STEP_SUMMARY.json \
  --out /ABS/NEW_REC_CLOCK_BRIDGE.json
```

원본 R8 fixture를 실제 연구 PC에서 사용한 실행: 102 선택 native accepted step; 각 source의 source SHA256과 원 R8 저장 60자리 적분을 그대로 참조. 신규 REC source의 최대 상대 차는 약 4.996e-14로 고정 component gate 1e-9보다 작았다. Native `ZERO/SHEAR_PLUS/SHEAR_MINUS` saved clock의 24/102 단기 간격 1e-8 초과가 이 새 공급자에서는 모두 해소되는 수치 진단이다. REI 원 checkpoint나 binary를 수정한 것은 **아니다**.

Python 테스트 결과: 신규 15개 geometry + 3개 CLI=18개, REC background 전체 34개 PASS, 기존 trajectory 최신 재검증 16 PASS·2 SKIP(slow), 앞선 선택된 실행에서는 18 PASS가 관측됨. 첫 `.venv/bin/python -m pytest` 호출은 별도 pytest 미설치로 exit 1이었으며 시스템 `python3`를 사용해 테스트했고, package 또는 system 환경을 변경하지 않았다. 한 targeted test 명령의 존재하지 않는 파일 경로도 실패로 기록했으며, 올바른 실제 3개 테스트 파일로 재실행하여 18 PASS. 장시간 전체 solver/cargo/HPC suite는 사용자가 이번 범위에서 요구한 작은 실제 실행과 구분해 NOT_RUN.

Wolfram 15.0.1: finite redshift generator/angle Jacobian/Hermite cell integral 수식 4개 잔차 0. local Wolfram Engine 15.0.0 + xTensor 1.3.0: 정상 관측자 공간의 단위방향 흐름, shear-energy contraction, scalar convective product rule 3개 영잔차; xCoba NOT_RUN. Native subagent 도구가 제공되지 않아 NOT_RUN.

## 다음 REC/REI 실행

REC의 기존 v0.52 Bianchi II 검증 경로는 그대로 유지. 새 Bianchi I는 source-bound **prescribed background supplier**이며 이전에 검증되지 않은 REC full Bianchi-I/HyRec provider로 자동 분류하지 않는다.

독립 실행 중인 REI Codex의 AX08/11/12와 `BACKGROUND_EXACT_CACHE_001`·`TEMPERATURE_RATE_TABLE_001` 구현 권한은 그대로 둔다. 새 REC interval 수치를 REI 생산 Rust로 이식하려면 별도 finite authority, native changed-method identity, gas/photons/ledgers/accepted & rejected step의 실제 overlap와 refinement가 필요하다. 이미 통과한 REI `BACKGROUND_TABLE_001` stable interval 방식이 첫 비교후보이다. Reuse R8 reference selected-step data; 새 binary identity 없이 역사적 checkpoint를 재활용하거나 기존 producer가 새 방법을 썼다고 relabel하지 않는다.

실행 스크립트는 output overwrite를 거부한다. Missing or mismatched case/source identity는 ValueError/비영 종료. 실제 새로운 숫자는 `research/rec_c5_lrs_bianchi_i_20261015/RESULTS.json`과 별도 private evidence package에 기록한다.

참조 문헌: Fritsch–Carlson (1980), Higham (2002), Fleury–Pitrou–Uzan PRD91 043511 (2015), 기존 REC R7B/R8/R9. 신규 문헌 최초성은 주장하지 않는다.
