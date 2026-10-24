# REC 저장소 R1/R2 source intake — 2026-10-24

## 결론과 다음 단위

게시된 REC의 최신 관련 결과는 ADM01 PR131, HEAD `c7cdabd871ab2ef6f722594ff063b8ce8550e6b4`다. 브랜치149개와 PR131개를 끝까지 열거했다. 최신 HISTORY01/LINE02/ADM01이 이미 닫은 조건부 보간식·frozen response를 반복하지 않고, root가 복구한 HISTORY02 StageA의 아직 구현되지 않은 **constant-shear diagonal Bianchi I retarded event, direction, Wien-reference map**을 별도 additive REC-HISTORY-02R로 잇는 것이 현재 가장 직접적인 다음 단위다.

이는 이론·구현 의존성에 대한 intake 제안이다. 이 조사에서 과학 실행, 시험, native runtime, IVP, 외부 변경은 모두0이다. Built-in PhysMath1.0.0의 R1/R2 source/research intake(Astra)를 사용했고, signature(-,+,+,+), c·ħ·k_B 명시와 기존 holds를 유지했다.

## 조사 범위와 exact inventory

| 목록 | 페이지 | 관측 개수 | 종료 근거 |
|---|---|---:|---|
| branches, per_page100 |100+49|149|page2가 짧은 마지막 페이지|
| all-state PRs, updated desc, per_page30 |30+30+30+30+11|131|page5가 짧은 마지막 페이지|
| open / closed |전체 PR 목록에서 분류|97 /34|별도 open endpoint의 첫30개만을 전체로 오인하지 않음|

[BRANCH_INVENTORY.json](BRANCH_INVENTORY.json)에149개 전체 이름·HEAD, [PR_INVENTORY.json](PR_INVENTORY.json)에131개 상태·head/base·날짜·URL, [RECENT_PR_BODIES.json](RECENT_PR_BODIES.json)에PR94–131의 실제 본문을 보존했다. 새 HISTORY02/Wien 이름의 브랜치나 PR132+는 이 목록에 없었다. 이는 게시된 metadata 범위의 결과이며 미게시 owner 작업의 부재를 증명하지 않는다. 모든149개 브랜치의 파일 전체를 읽었다는 주장은 하지 않는다.

실제 선택 HEAD의 root Git tree에는 AGENTS.md가 없고, root도 같은 HEAD의404를 별도로 관측했다. research와 선택 단위의 실제 경로 tree에도 AGENTS.md는 없었다. 다른 HEAD의 과거 정책 사본을 현재 정책으로 채택하지 않았다. source text는 connector UTF-8 사본이며 Git blob 메타데이터를 기록했다. 이번 intake에서 원 Git object와 바이트 일치를 새로 인증하지 않았다.

## 주요 최신 source pins

| 의무 / PR | 실제 HEAD | 읽을 경로 또는 결과 |
|---|---|---|
| ADM01 /131 |c7cdabd871ab2ef6f722594ff063b8ce8550e6b4|research/rec_history_input_admission_20261024/NEXT_INPUT_CONTRACT.md|
| HISTORY01 /130 |93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa|research/rec_history_boundary_20261023/THEORY.md, code/history_boundary.py, code/run_history_checks.py, NEXT_INPUT_CONTRACT.md|
| LINE02 /129 |a7c46fd8338971e2cefa776f5dd7b25a46974990|research/rec_line_native_owner_20261023/THEORY.md|
| LINE01 /128 |6d32330e7f45e7caa9840c558547880b7d28a069|Detached effective-line source; PR본문 재사용|
| ANGULAR /127 |5185c396b7e07076565ca2f5044a5ccd193e6ee1|Local finite-τ scalar/PSTF; PR본문 재사용|
| THERM02 /125 |b28b387fecd6cc71fddb98e95f336eba5f8a647f|research/rec_rei_thermal_compton_20261022/HANDOFF_KO.md|
| full63 Compton /124 |e6ecef7624e39bee66b39e09d99fe355f76e2eae|Separate late-time cohort; PR본문|
| h4 U4A/U4B /114 |df95a074730ea0d13d609cf88d448f01f4a47ef1|U4B NCP_RETURN_HANDOFF_KO.md는 최신ADM01 tree에서도 그대로 읽음|
| R3N /108 |23e0a3a6c439a1f015aa8f7380f4eedf0b569df7|research/rec_r3n_time_convergence_20261019/HANDOFF_KO.md|
| Python h2 /101 |b2ae286274fea1fbe24a8c981fc84456e0f181ae|research/rec_r3i_time_refinement_20261016/README.md; 더 최신 U5결론은ADM01에 있음|
| C h/h2/h4 /100 |320b8810aaf1acdaa90e2eca860cf70b9af1ef75|research/rec_r3h_u5_precision_20261016/03_SOURCE_C_REFINEMENT_AND_CAUSAL_GRID.md|
| scalar characteristic /19 |91e5eb07a9df8b8bd5360c0aaf2a62a02bb72129|구형 PR05B2 scalar accepted-history; 새HISTORY02와 동일 단위가 아님|
| fixed-map JVP /77 |4125f7f39b29b710ad6ca673520ae46a426b564f|Manufactured single-field paired/COM composition; native full thermodynamic Jacobian과 구별|

모든 PR URL과 추가 source pin은 SURVEY.json에 있다. 읽은 파일의 exact path, URL, Git blob은 SOURCE_READS.json 및 sources/에 있다. 고정 authority는 계속 `rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`다. 최신 중앙 관측 HEAD/후속 draft를 이 고정 권위로 바꾸지 않는다.

## H5에서 이미 끝난 것과 실제 남은 입력

HISTORY01 THEORY §3은 엄격한 causal-prefix 보간과 fixed-cell tangent를, §5는313 incoming 채널 전체의 source·population·314 outgoing 반응을 이미 정리한다. 구현 `code/history_boundary.py`의 Git blob은 **1aa7f134c332bc4596372df18c7c47306260ecfc**이며, interpolation_envelope가

`e_u = M2 h² α(1−α)/2 + (1−α)e_left + α e_right + arithmetic`

를 제공한다. `run_history_checks.py`의 Git blob은 **e3245eb3feb0b38e60eb82eeef6df7d57b6a85da**다. 여기에는 제조 exp/cos history의48개 query와 endpoint rounding, exact frozen Z-matrix의 양의 comparison witness 및 두 제조 input 방향에 대한 조건부 envelope가 이미 있다. THEORY Git blob은 **277cfe128c963d0d60099d6489a00f1bec0cb3ba**다. 이608+14검사나 LINE02의194검사를 다시 돌릴 필요가 없다.

실제 calibration의 필요한 입력은 ADM01 NEXT_INPUT_CONTRACT 그대로다. Target face z=1099.9986525171403,313 native source query z=1100.092189396162…1133.87330719964. Target T0=2.728K,nH0=0.18745798773143102m⁻³와 실제 U5 T0=2.7255K,nH0=0.18971712352134673m⁻³가 다르다. U5의 face-causal prefix10277에서313/313 covered라는 결과와 uncertainty admission은 다른 gate다. endpoint/reference/curvature uncertainty는 여전히 미제공이다.

Photon column은 input state g, accepted thermal state는 g+1에 속한다. 최신 strict endpoint, signed departure와 normal frame, source grid identity를 유지해야 한다. Same-h parity, 두 격자 차이, sampled second difference 또는 다른 물리 parameter history의 임의 rescaling을 physical error bound로 승격하지 않는다. 검토한 게시 lane에는 이 동일-domain·동일-parameter outgoing-reference와 그 자체 uncertainty를 새로 공급하는 결과가 확인되지 않았다. 전체 가능한 provider에 대한 부재나 no-go를 뜻하지 않는다.

R3h의 원본 C h/h2/h4는8001개 xe·Tm/Tr 출력의 실제 time-step sensitivity다. z1100 local empirical order는 보고되지만 transition 부근 signed reversal이 있고, 이것은 retained314 outgoing spectra의 endpoint uncertainty 증거가 아니다. R3N comparator도 실제 Python h2 단독자료의 INSUFFICIENT_LEVELS를 명시한다.

h4 U4B는 원 실행 source a09e1d249d4cf4b706c09571fa7f231c8084c251로74443→74475의32 accepted steps를 끝냈다. Scoped same-h/common-input/native/split restart 결과를 재사용할 수 있다. U5/U6·event crossing·global convergence는 그 실행에 포함되지 않았다. 그 반환문의 resource accounting unresolved 부분도 그대로 남긴다.

## Characteristic·Jacobian ownership과 재사용할 코드

현재 c7cdabd... source에는 이미 두 종류의 characteristic API가 있다.

- `src/full_bianchi_hyrec/background/characteristics.py`, blob **f71ec2607daac808b871279ad0893d4653169343**: normal-frame 에너지·방향 순간 미분과 finite-tilt Doppler/aberration. 이는 공간 connection과 frame rotation도 받는다.
- `src/full_bianchi_hyrec/trajectory/characteristic_angular.py`, blob **c6676ee112a892bb558ab8aab670481617201c7f**: accepted-history midpoint geometry API와 frozen-background RK4 frequency-face API를 구별한다. LRS prescribed source의 exact geometric clock binding도 있다. 두 API는 서로 다른 initial-boundary-value problem이다.
- `src/full_bianchi_hyrec/trajectory/direct_thermodynamic.py`, blob **47b13e3e9f7c3c1e2b179b15e7103c3ef3f4c8b1**: COM–KHW reciprocal conductance의 fixed-topology inverse-temperature interpolation이다. Native313 전체 M,B,O,P 및 departure-coordinate thermodynamic Jacobian을 닫는 코드로 해석하지 않는다.

LINE02 THEORY는 JVP가 TR,TM,x1s,nH,H,virtual blocks, incoming history를 고정한다고 명시한다. HISTORY01 역시 thermodynamic 방향의 δM,δB,δO,δP 및 departure-coordinate 미분을 별도 의무로 남긴다. THERM02의8개 IVP는 z20→2,193nodes,compact34,T0=1000K의 다른 cohort다. 실제-grey spectral/Einstein backreaction 및 Li exact yield도 열려 있다. 이들 이름의 “thermal”을 primordial native Jacobian 완료나 새 owner reservation으로 합치지 않는다.

기존 시험을 재실행하지 않도록 TEST_REUSE_MAP.json에 exact blob과 test names를 기록했다. 핵심은 local boost/direction derivative, scalar history transaction/JVP, constant-coefficient transfer JVP, numerical geometry refinement다. 새 exact retarded-root/Wien map의 finite controls와 중복되는지 항목별로 구별하여 최소 추가 부분만 선택하면 된다. 이 조사에서는 기존 tests를 읽기만 했다.

## HISTORY02R의 안전한 이어가기

Root의 현재 backup intake에 따르면 HISTORY02 StageA는15개 파일, SHA prefix ca748e1e9e3e…이며 exact constant-shear diagonal Bianchi I retarded root·direction·Wien offset·tangent·conditional envelope를 이미 유도했다. 새 code/results는 그 capsule에 없고, 남아 있는 별도 reservation은 REI-L0라고 전달받았다. 이는 **parent가 직접 읽어 전달한 결과**이며 이 subagent가 provider capsule을 다시 내려받아 확인한 것은 아니다.

따라서 다음 단위는 StageA 원본을 보존하고 현재c7cdabd...에서 별도 additive REC-HISTORY-02R로 previously unimplemented map을 구현·유한 확인하는 것이다. 기존 HISTORY01 boundary/JVP와 S0 exact evidence는 재사용한다. StageA의60CPU/180wall, spent0@21:39Z snapshot을 이후 실행이 없었다는 증거로 사용하지 않는다. Root가 제시한 새 invocation20CPU/60wall, IVP0의 계약은 별도로 동결하며 이 intake의 실행은0이다.

완료 가능 주장도 제한한다: 선택된 prescribed diagonal metric과 normal frame의 characteristic/Wien-reference adapter 및 그 유한 검증. Actual H5 physical history calibration, full thermodynamic Jacobian, coupled thermal/radiation/metric evolution, global convergence와 production approval은 이 단위가 자동으로 닫지 않는다. 다른 owner의 REI-L0·field·Jacobian source를 수정하지 않는다.

## PR131 자동 CI의 실제 실패 분류

HEAD c7cdabd...의 verify-durable-backup push run40051595217 및 PR run40051600230은 failure다. 두 job metadata에서 setup·install·import smoke는 success, `python scripts/verify_repo.py --quick`는 failure, `pytest -q`는 skipped다. PR job120745269339의 기존 로그를 읽어 committed_feature_range whitespace gate와 exit1을 확인했다. 실제 feature_base는 e6b64e0df25d0b1db7cf8b776866db0afc14721e다.

실패 경로에는 과거 ANGULAR/LINE/HISTORY 경로뿐 아니라 PR131이 새로 복사한 provenance source5개도 있다. 따라서 “전부 과거 파일만의 문제” 또는 “환경 실패”라고 분류하면 부정확하다. 저장소 whitespace/delivery gate 실패로 기록하고, 새 ADM01 물리 결과의 실패나 repository-wide PASS로 해석하지 않는다. CI를 새로 시작하거나 보존 source를 공백 정리하지 않았다. 상세는 WORKFLOW_PR131_CLASSIFICATION.json에 있다. Push raw log는 추가로 읽지 않았으므로 그 구체 문자열까지 동일하다고 주장하지 않는다.

## 보존 상태

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false; first_failed_REI_raw HISTORICAL_LOCAL_ONLY를 유지한다. ADM01은 reset 뒤 exact-recovered SUMMARY와 source/caller contracts를 보존했으나 원1252 detailed rows/queries/controller files/old figures는 미복구임을 그대로 인계한다. 새 survey나 다음 adapter의 성공이 이 과거 보존 범위를 소급 변경하지 않는다.

