# 재개 후 중앙 게시 보존 intake

## 판정

**566f242b에서 닫힌 유한 연구 intake의 REC H5 판정은 그대로다.** 최신 지정 pin `fca9a31de961a85f14972550c1f4c35c4fc3e773`은 selected H I summary consumer의 좁은 결과를 추가했지만, REC 원래 313-query target의 같은 parameter/source/frame history, independent reference/endpoint uncertainty 또는 정당화된 temporal curvature bound를 공급하지 않는다.

이번 범위는 **게시 보존 및 바뀐 입력의 read-only 확인**이다. 전체 저장소·branch·Library·대화를 재조사하지 않았다. 새 science, IVP, 과거 replay, provider/Git mutation, science code edit는 모두 0이다. 복원 중인 REC REFINE01 owned unit은 변경하지 않았다.

## 게시 base의 정확한 식별자

| 항목 | 값 |
|---|---|
| repository | cosmosapjw-quantum/rei_bianchi |
| branch | research/orchestration-sandbox-20261022 |
| 현재 지정 commit / expected parent | fca9a31de961a85f14972550c1f4c35c4fc3e773 |
| 현재 commit의 parent | 98ca692b200227c51011bfbbe037daaccfc6f3eb |
| additive tree의 base tree | f4495397de2fddd7ee9a6533568bd4cc3c86b729 |
| 중앙 DAG Git blob | 56c015ccf8322bdd6ab5979a5be8ec1beb797c6f |
| 중앙 DAG bytes | 239544 |
| 중앙 DAG SHA256 | c405927b14c814e9a0566d1cde44ba4270b4720aded225c0292b17bb01dbf046 |

원문은 `DAG_latest_fca9a31.json`, API commit 정보는 `COMMIT_METADATA_fca9a31.json`, 게시용 요약은 `PUBLICATION_BASE_METADATA.json`에 있다. Root가 제공한 current pin을 읽었으며 다른 HEAD를 다시 추적하지 않았다. 실제 게시 시점의 expected-parent 충돌이 있으면 바뀐 소유자 관측만 보존하는 targeted read가 필요하다.

## 566f242b → fca9a31의 실제 변화

두 commit만 추가되었다.

- `98ca692b200227c51011bfbbe037daaccfc6f3eb`: REI-L0 publication closeout 및 다음 L1 static preparation boundary.
- `fca9a31de961a85f14972550c1f4c35c4fc3e773`: selected H I summary consumer admission과 다음 pressure interval의 실행 전 준비.

비교 목록의 변경은 모두 별도 REI owned path에 있다. 중앙 `assembly/DAG.json`, 중앙 return, root AGENTS 변경은 없다. 중앙 DAG는 이전 566f242b에서 읽은 것과 **exact bytes가 동일**하다. 따라서 original 40개 contract, 40개 plan_status, 17개 integration edge, authority, HE-X1, HE-ANG, CR N5 및 prospective REC patch 밖의 38개 node는 모두 보존되어 있다. `PRESERVATION_CHECK.json`에 이를 기록했다.

추가로 읽어 저장한 원문 여섯 개(두 시점의 중앙 DAG, PR224 donor DAG, HI ADMISSION/source binding, pressure README)의 Git blob 계산은 **6/6 exact match**다.

## 새 HI 결과를 읽은 범위와 REC 영향

새 [HI ADMISSION](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/fca9a31de961a85f14972550c1f4c35c4fc3e773/research/rei_source_pair_binding/hi_primary_20261024/ADMISSION.json)의 현재 decision은 **ADMITTED_SCOPED_SUMMARY_CONSUMER**다. source는 elemental ground-state H I, z=2.479, bath-frame rest target, prescribed isotropic scalar, no-deposition snapshot이며 photon support는 13.6–50000 eV다. source-owned independently rounded A/B/P/K moment summary를 보존하고 nonthermal energy/electron owner 및 fixed-moment analytic JVP를 다룬다.

Owner는 one-child/one-fixture 실제 결과와 별도 PASS_SCOPED 검토를 기록한다. 이 intake는 해당 계산을 재실행하지 않았다. 같은 commit에 남은 `SOURCE_BINDING.json`의 STATIC_PREPARED 상태는 준비 당시 snapshot이며, 현재 admission 판정은 이후 `ADMISSION.json`을 따른다. source-binding snapshot을 이유로 새 scoped admission을 되돌리지 않는다.

다음 한계는 현재 admission에도 명시되어 있다.

- physical secondary heat 및 global error bound는 null.
- raw-atom/common-measure source reconstruction과 source physical global error qualification은 이 단위의 결과가 아님.
- source consistency tolerance는 frozen criterion 부재로 NOT_EVALUATED.
- full original L1 physical validation은 NOT_ESTABLISHED.
- L4_ready=false.
- finite photon stock, transport, stopping/thermalization, isotope/line/Compton/finite-T/recoil 및 Einstein/cosmological trajectory를 admit하지 않음.

[다음 pressure README](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/fca9a31de961a85f14972550c1f4c35c4fc3e773/research/rei_source_pair_binding/hi_pressure_next_20261024/README_KO.md)는 finite positive energy measure에 조건부인 scalar pressure interval의 **정적 준비 완료·미실행** 상태다. 입력 moment/support에서 얻는 pressure 범위는 REC 시간 history의 곡률 상계가 아니다. physical uncertainty, stock time evolution, thermal temperature, calibrated equation of state, Einstein coupling도 공급하지 않는다.

따라서 새 REI owner 진척은 보존하되, REC original target의 H5 `INPUT_DEPENDENT_UNCALIBRATED`를 해소한 자료로 수입하지 않는다. REFINE01의 자체 결과와 원래 target의 calibration 의무는 부모의 실제 evidence에 따라 별도로 기록한다.

## PR224 관측을 안전하게 합치는 입력

PR224의 immutable donor commit은 `f0a92c2421ff186dabd20fac09378a97c195fd4f`, DAG blob은 `e58bab9693cdedaf7e79b69f31f2e8295a7e86f7`이다. 이 donor는 별도 unmerged observation이므로, 실제 current central DAG에는 아직 REC node의 `observations`가 없다.

`REC_PRIOR_OBSERVATION_DONOR.json`에는 donor의 **observations object만** 추출했다.

- REC-LINE02: 기존194 checks/202 rank queries/6 review probes와 original final receipt identity.
- REC-HISTORY: HISTORY01, ADM01, HISTORY02 reservation, 기존 limits/execution, HISTORY02R의 원래 evidence·budget·backup 상태.

현재 base의 `plan_status`는 REC-LINE02=`OWNER_DELIVERY_PENDING`, REC-HISTORY=`PROPOSED`다. 요청에 따라 두 값과 contract/authority/dependency를 그대로 유지해야 한다. Donor의 complete node나 donor 전체 DAG를 복사하지 않는다.

게시 patch는 실제 latest node의 observations에 위 donor object를 합치고, 복구된 부모 소유 REFINE01 결과를 새 관측으로 추가하면 된다. 기존 HISTORY01/ADM01/HISTORY02/HISTORY02R의 기록과 지출은 변경하지 않는다. Parent REC-HISTORY의 과학적 PARTIAL 및 H5 상태는 새 관측 안에 명시할 수 있다. 다른 38개 node와 기존 HE/CR 관측도 exact-preserve해야 한다.

## 보존 상태

Physical HOLD; REC_U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global_convergence NOT_RUN; production NOT_APPROVED; REI_activation=false; 최초 실패 REI raw HISTORICAL_LOCAL_ONLY를 유지한다. Science result나 budget을 reset 또는 재실행하지 않았다.
