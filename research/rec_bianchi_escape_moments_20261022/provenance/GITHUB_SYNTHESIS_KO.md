# REC/REI 최신 GitHub 조사와 다음 물리 단위의 중복 검사

작성 시각: **2026-10-22 22:39 UTC**. 이 문서는 GitHub의 읽기 전용 조사 결과다. 과학 RHS, ODE, 기존 suite, benchmark와 NCP 계산은 실행하지 않았다. 원격 코드·PR·댓글도 수정하지 않았다.

## 1. 이번 조사에서 확정한 결론

다음 단위는 **기존 방향별 optical-depth donor를 그대로 사용하는 유한 광학깊이의 scalar/PSTF angular escape moment 축약**으로 좁힐 수 있다. 기존 저장소는 이미 방향별 optical depth와 정확한 spike jump/JVP를 제공한다. 이 부분을 다시 구현하거나 새 성과로 세면 중복이다. 이번에 직접 읽은 source/test/ownership 문서 및 제한된 default-branch 검색에서는 **Jensen/concavity, thick-limit scalar cancellation, finite-depth error bound와 escaping PSTF quadrupole을 한 단위로 인증한 결과를 찾지 못했다.** 이는 조사한 범위의 판정이며, 모든 branch의 모든 내용이나 외부 문헌에 대한 부재·독창성 증명은 아니다.

동시에, primordial recombination을 처음 도입하는 계획도 중복이다. REC에는 원본 HyRec/HyRec-2/RECFAST 비교, 독립 EMLA H+T 이력, 원본 FULL H+He의 source-native q=0 이력과 후속 refinement 연구가 이미 존재한다. **z~1100 primordial lane과 z20→2의 21-population low-z pilot를 구분해야 한다.**

또한 최신 REI222 안의 20261022 handoff는 successor 20261023 DAG로 이어졌다. 이전 문서의 N1/N5/N7 READY를 그대로 실행하면 이미 완료한 norm-hook pair, conditional finite-mass moment, saved-history D10 진단을 반복하게 된다.

## 2. 실제로 전수 열거한 메타데이터 범위

| 저장소 | Branch metadata | Open PR metadata | Closed PR metadata | Pagination |
|---|---:|---:|---:|---|
| rec_bianchi | **144** | **92** | **34** | branches 1–2:100+44; empty probe3. open 1–5:20+20+20+20+12; empty probe6. closed 1–2:20+14; empty probe3 |
| rei_bianchi | **263** | **207** | **14** | branches 1–3:100+100+63; empty probe4. open 1–11:20×10+7; empty probe12. closed1:14; empty probe2 |

총 **407 branch refs / 347 PR records**를 확보했고 branch name 및 repo별 PR number의 중복이 없음을 확인했다. 각 URL·page·returned count·client UTC는 `GITHUB_INVENTORY.json`에 있다.

이 숫자는 **메타데이터 열거**다. 모든 파일·댓글·비공개 대화·미게시 로컬 작업을 읽었다는 뜻이 아니다. 선택 PR 47개의 body를 수집하고, 실제 종합에 필요한 내용을 선별했다. 28개 primary source/document/license 파일과 9개 PR의 issue-comment collection을 추가로 읽었다. Review/inline-comment 전체 timeline은 조사하지 않았다. GitHub code search는 **default branch만** 검색하므로 feature-branch 전체 내용 검색으로 표현하지 않는다.

REI222의 실제 참조로 발견한 BASS_HE87, WU088_HH135, bass_cr97, bass181, vigilode79를 읽고 HEAD를 확인했다. 이 다섯 저장소 전체의 branch/PR pagination은 수행하지 않았다. 백업·대화 접근은 별도 조사 담당자의 결과와 함께 parent가 종합한다.

### 조사 중 발생한 동시 갱신

초기 snapshot에는 REC branch143/openPR91이었다. 마감 확인 중 **REC PR126**이 새로 게시되고 REI221이 metadata commit으로 이동했다. 초기 JSON을 `GITHUB_INVENTORY_INITIAL.json`으로 보존하고, REC open pages와 branch 경계를 다시 읽어 현재 숫자를 만들었다. REI221의 변경은 실제 compare API로 **추가 DELIVERY.json 한 파일 / 한 commit**임을 확인했다.

- [REC PR126](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/126): HEAD `12068893fab749ae1efb513563d0a86cc1cf649f`, `research/rec-diagnostic-c2-20261023`.
- [REI221 exact delta](https://github.com/cosmosapjw-quantum/rei_bianchi/compare/9620e1fcc4bdda76e0311206f614234926600381...73c5e00cac26b4efc782446975bd6b6762555997): 과학 head `9620e1fcc4bdda76e0311206f614234926600381` → 전달 head `73c5e00cac26b4efc782446975bd6b6762555997`. 기존 local-flow source/evidence는 변경하지 않았다.

서로 다른 시각에 조회한 collection이므로 원자적 repository snapshot은 아니다. 조회시각 이후의 새 게시까지 확인했다고 주장하지 않는다.

## 3. 필독 anchor와 최신 반환

| Anchor | 실제 읽은 현재 상태 | 재사용 판정 |
|---|---|---|
| [REC119](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/119) | HEAD `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`; 125main+1control=126, z20→2,193 nodes | 완료 결과 재사용 |
| [REC119 recovery comment6327410942](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/119#issuecomment-6327410942) | 원 ZIP 27,040,521B와685payload whole-byte/복구 PASS의 당시 증거 | 과거 ACK-only snapshot에 덮어쓰지 않은 additive receipt |
| [REC119 latest observed comment6334748621](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/119#issuecomment-6334748621) | THERM01 PR120의 별도8개 완료와 다음 source 입력 | 처음 요청된 recovery comment 이후의 실제 반환 |
| [REI220](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/220) | HEAD `8be7533cc97b3302bf42608699d6e8313ed6af8a`;62→33;127main+2oracle=129 | REC126과 다른 cohort |
| [REI220 latest observed comment6334748952](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/220#issuecomment-6334748952) | compact34/full63 THERM01 재사용 반환, 원 실패 raw local-only 명시 | 과거 실패 raw를 소급 보존되었다고 쓰지 않음 |
| [REC125 current DAG](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/b28b387fecd6cc71fddb98e95f336eba5f8a647f/research/rec_rei_thermal_compton_20261022/DAG.json) | HEAD `b28b387fecd6cc71fddb98e95f336eba5f8a647f`; science `407a280aff51abefc10374cb6e21c4224140328c`; THERM02 8/8 | 과학·그림·검토 완료; 새 ODE 불필요 |
| [REI222 successor DAG](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/b4b5d289aaad9ef167f683f19418b0ff87ed8425/research/orchestration_sandbox_20261023/DAG.json) | HEAD `b4b5d289aaad9ef167f683f19418b0ff87ed8425`; 20261023 scoped successor | 20261022 READY 문구보다 최신 |

선택 issue-comment 조회에서 REC119는6개, REI220은1개, REC114는2개, REC113은1개를 읽었다. REC125/124와 REI219/221/222는 그 조회시점에 issue comment0개였다. 이는 본문·review·파일의 미완료를 의미하지 않는다.

## 4. 완료 계산과 단위를 분리한 중복 방지 장부

| 단위 | 완료 범위 | 이후에 남은 것 |
|---|---|---|
| REC119 / REI220 | 각각126 /129개 low-z prescribed T/UV atomic pilot | 각각의 모델·행·계수·실행 회계 유지 |
| warm729 | 별도 완료 campaign | 재실행 없음 |
| REC120 THERM01 | 6nominal+1tight34+1full63=8,5–60eV,z20→2 | Li resonance/final ionic yields와 실제 source moment의 추가 입력 |
| REC121 | 별도8개 full63 5–200eV thermal restart | 기존 결과 재사용 |
| REC122 / REC123 | 같은8개 이력의 omitted-budget 및 독립 C saved-path kernel; 새ODE0 | 서로 중복된 Planck budget을 추가8해로 세지 않음 |
| REC124 | 별도8개 full63/logT Compton restart,z7.9637328→2,109 nodes | 그 campaign 완료;125와 다른 초기조건·band |
| REC125 THERM02 | 5nominal34+2tight34+1full63=8,z20→2,193 nodes,5–60eV | source-provider N1/N2 |
| REC126 C2 | **8기존cases×64savedstates=512**; source/profile/map/raw/figure/review | C3 공유 state-context API 설계는 HANDOFF_ONLY; 최적화·speedup 미실행 |
| REI219 atomic quotient / nuclear audit | 82 quotient+1independent atomic reference와 기존 controls;83saved atomic histories;18family34directed conditional passive network | all-bare/instant-thermalization 등 조건을 physical coupled isotope closure로 확대하지 않음 |
| REI219 bootstrap/thermal/providers | 공급된 순간 thermal ledger,6channelRR scalar adapter,3ground-targetDRfit scalar 평가 완료 | CI/CX,DR moments/cascades,spectral/daughter/feedback 의존성 |
| REI221 atomic sandbox |156baseline checks+별도2 manufactured onset checks;21state,J=B+u qᵀ;0cosmologicalIVP | source-qualified daughter/energy/fast-electron 입력 |
| REI221 local flow |103baseline checks,82arrays+별도96 repeated timing guards;순수H thermalRR와 prescribed-T beta+RR 완료 | thermal beta에는 electron/neutrino/recoil partition·stopping/escape 필요 |
| REI222 successorN1 | norm hook+한 matched30/33 pair,**2shortIVPs** 완료 | work counters는 serialization loss로 UNKNOWN |
| REI222 successorN5 | caller-supplied isotropic pseudo-Maxwell pair moment 모델 PASS_SCOPED | 실제 finite-mass differential transport 자료·reactive closure |
| REI222 successorN7 |35saved histories×153epochs D10,새IVP0 | 최초실패CPU UNKNOWN_NOT_ZERO,aggregate60s cap NOT_ESTABLISHED 유지 |

REC126의 C2는 과학 입력을 보존하는 진단 최적화 준비다. 현재 사용자가 물리·코드·그림을 benchmark보다 우선하므로, 이를 새 primordial/Bianchi 물리 결과로 바꾸어 세지 않는다. [C3 handoff 원문](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/12068893fab749ae1efb513563d0a86cc1cf649f/research/rec_saved_diagnostic_reuse_20261023/NEXT_STAGE_C3.md)은 새IVP0,원 RHS/Jacobian 불변과 두 독립 energy 합계·mask 보존을 요구한다.

REI221의 최신 [local-flow resume](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/9620e1fcc4bdda76e0311206f614234926600381/research/rei_coupled_local_flow_20261022/RESUME.md)은 total betaQ를 heat로 배정하지 않고 새로운 물리 energy partition부터 연결하도록 한다. 이전 PR본문이 atomic156 단계에 머물러 있었지만 실제9620 head에는 local-flow103+96이 이미 있었다.

## 5. Primordial recombination의 실제 도달점

### 기존에 완료된 구성

- [REC90](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/90),HEAD `99dbd883042bb60734f92cd424f2f91826d1ea48`: 원본HyRecC rate parity와 matched HyRec2/RECFAST 이력 비교.
- [REC91](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/91),HEAD `130775798c97c3af9baa4098f6b293f1f402b451`: 독립 EMLA2s2p H+T, z1600→600, source Sobolev를 포함한 q=0 구현. H-only/neutral-He heat capacity의 범위.
- [REC92](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/92),HEAD `98b9f3099fa12b80437531473c627998ff6c0d20`:311virtual+2Lyman incoming source history, axisymmetric Killing characteristic와 anisotropic Planck correction; FULL 자체의 q≠0 coupling은 별도.
- [REC93](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/93),HEAD `2c4627bf480a306f34bb35d0ec5a3d18182b170e`:2real+311algebraic virtual FULL source,80-bin banded Schur,original-C oracle.
- [REC99](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/99),HEAD `e6596cf6083c0a1f28a26700170c971a20244d23`:원본2012 q=0 H+He 전체 source-native grid 및8001출력행까지 독립 Python 이력. U5 averaged-spectrum9실패는 그대로HOLD.
- [REC108](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/108),HEAD `23e0a3a6c439a1f015aa8f7380f4eedf0b569df7`:saved-grid comparator와 predictor/error 분리. incomplete levels를 global convergence로 승격하지 않음.

### 최신 high-z frontier의 해석

REC114 PR본문/댓글의 U4A 뒤에도 descendant branch에 U4B 반환이 보존되어 있다. 최신125 head의 [U4B return](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/b28b387fecd6cc71fddb98e95f336eba5f8a647f/research/rec_r3t_u4b_20261021/NCP_RETURN_HANDOFF_KO.md)을 읽었다.

- U4A74411→74443 완료 후 U4B74443→74475의32accepted step도 한 번 완료.
- U4B 실행 source `a09e1d249d4cf4b706c09571fa7f231c8084c251`, exact tree `2186e9a53316b040bbfa6a02da09d9378b28baf0`.
- 이 범위 안에서 event/thermal/RT crossing 없음. U5/U6 자동 진입 없음.
- U4B systemd terminal CPU5.375101s는 관측값이며 전체allocation CPU/wall은 누락구간 때문에 UNRESOLVED.
- R3S도 이전 NOT_RUN 본문 뒤에 addendum으로5NCP jobs 완료와 exact-enum adjudication을 기록했다. [현재 handoff](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/b28b387fecd6cc71fddb98e95f336eba5f8a647f/research/rec_r3s_ncp_campaign_20261021/HANDOFF_KO.md)의 뒤쪽 addendum을 따라야 한다.

이 이력은 source-native parity의 실제 진전이다. q≠0 self-consistent full atomic/collision/Einstein recombination이나 global h/h2/h4 convergence 완료는 아니다. 동일 q=0 baseline,원래hold,기존 checkpoint를 반복하여 다음 새 연구로 세지 않는다.

## 6. 후보의 기존 구현과 새 질문을 정확히 분리

### 직접 재사용할 donor

고정 head: **REC PR114 `df95a074730ea0d13d609cf88d448f01f4a47ef1`**.

[hyrec_spike_transfer.py](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/df95a074730ea0d13d609cf88d448f01f4a47ef1/src/full_bianchi_hyrec/trajectory/hyrec_spike_transfer.py)는 이미 다음을 제공한다.

1. `tau_directional = tau_flrw * H / abs(minus_dlognu_dt)`.
2. 안정한 `-expm1(-tau)`로 source/incoming convex spike jump.
3. branch-fixed JVP.
4. zero frequency speed를 event localization 대상으로 처리하는 명시적 guard.

같은 head의 `hyrec_source_adapter.py`는 vector spike와 isotropic Einstein-line source도 이미 제공한다. `full_2012_atomic_source.py`는 원본 q=0 H를 사용하는 FULL source이며, `hmla_flrw.py`는 angle-dependent collision을 가정하지 않는다. 관련 source/test9개를 직접 읽었다. 기존 donor tests는 다시 실행하지 않았다.

| 전달 파일 | Bytes | Exact remote Git blob | SHA256 |
|---|---:|---|---|
| donor/hyrec_spike_transfer.py |4199|ade2cc6d3da852f444289d7c6f2e9132c8ca7c90|3d03c35299d529ecaac66f40f5fc78f14ec3099c057005762f112250ee19add9|
| donor/LICENSE |1075|1aa6800054695bbfc86dc68286157c851f1fc49d|bfb425597830af905d9b52262dc5fc56e436de05796f6638a78258adaa0b8760|
| donor/test_hyrec_spike_transfer_v068.py |3147|72ceb257c9bd366dcdb83e6d8b069b65e92c2d2a|4a079ab3be49c9e97145c91c6a0f7b883f7ef16f1c1b5ce66c8a95dc72b79862|

세 파일 모두 UTF-8 원문을 저장한 뒤 Git blob SHA1과 대조하여 **BYTE_IDENTITY PASS**다. License는 MIT, Copyright2026 cosmosapjw-quantum. 원문 license를 보존했다. 원본 HyRec C 코드 전체를 새로 가져오거나 그 전체의 라이선스를 대체했다고 주장하지 않는다.

### 기존 각도 결과와의 구별

[REI146](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/146),HEAD `c0ea467e334dc810280234b012377ba080869b28` 및 [REI149](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/149),HEAD `d5246c500522ffe4efe904f3206a60f9541c7dbd`는 positive Case-A escaped **bolometric radiation의 이후 Killing transport**에 대한 sharp angular pressure bounds와 conditional isotropic source의 small-shear 계수 등을 이미 계산했다. 새 line-escape 순간 angular weighting을 이 결과와 같은 것으로 세지 않는다. 나중에 source geometry를 연결할 때는 spectrum·birth·opacity 가정을 다시 맞춰야 한다.

### 이번 bounded novelty 검사와 적용 한계

default main `5a09f3797210284f83a1a1adb0e0092d1ac48475`에 대해 directional Sobolev,escape quadrupole,directional_optical_depth,concavity,escape_probability,Sobolev thick,Jensen,Sobolev PSTF,Sobolev angular average를 검색했다. 일부는 기존 donor/ownership 문서만 찾았고 concavity/Jensen/escape_probability/Sobolev PSTF 등은 결과0이었다. 검색은 semantic/index 범위의 관찰일 뿐, 모든 branch의 부재 증명은 아니다.

[원본 substitution firewall](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/5a09f3797210284f83a1a1adb0e0092d1ac48475/archive/expanded/Full_Bianchi_HyRec_C3B2A_substitution_audit_v0_28/SUBSTITUTION_FIREWALL.md)은 escape-compressed Tvv의 비가산성과 Sobolev/Lyαfeedback/diffusion/line-centre coupling을 함께 소유하는 교체 경계를 명시한다. [현재 descendant의 macro plan](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/b28b387fecd6cc71fddb98e95f336eba5f8a647f/docs/PR05C2_FULL_COUPLED_ADAPTIVE_PLAN.md)도 canonical Sobolev/A1s/Tvv를 유지한다. 따라서 새 작은 angular-moment unit은 **조건부 local-line 모델의 계산 단순화**로 먼저 성립시켜야 하며, 그 자체로 HyRec 전체 compressed sector를 교체했다고 쓰지 않는다.

## 7. 추천하는 실제 미완료 물리 노드

| 우선순위 | 질문과 재사용 | 새 결과의 최소 범위 | 현재 상태 |
|---|---|---|---|
|1: 선택 가능|위 directional-spike donor를 사용한 finite-tau scalar/PSTF escape moment|monotone expanding directions,positive supplied optical coefficient,isotropic source 가정 아래 angular mean의 concavity/thick residual와 escaping quadrupole을 판별·인증; source/units를 고정한 경량 oracle와 그림|읽은 범위에서 동일 단위 미발견. R1/R2 조사 완료; 수학/코딩 실행은 parent의 별도 선택범위|
|2: 기존 thermal lane의 다음 물리 입력|[THERM02 HANDOFF N1/N2](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/b28b387fecd6cc71fddb98e95f336eba5f8a647f/research/rec_rei_thermal_compton_20261022/HANDOFF_KO.md)|Li final charge/state/energy-resolved yield table 또는 실제 grey photon field의 recoil/induced spectrum과 radiation/Einstein ledger의 source contract|Li exact input MISSING_EXACT_INPUT; actual-field closure 입력 열림. 0ODE source work부터|

첫 후보는 현재 사용자가 요구한 Bianchi recombination 이론 단순화에 직접 연결되고, 완료된 IVP 없이 source-native donor를 재사용할 수 있다. 두 번째는 low-z thermal 축의 실제 열린 의무이며, total cross section을 ionic yield로 사용하거나 total betaQ를 heat로 넣는 것으로 닫을 수 없다. 여기서는 새 theorem/새 코드의 성립을 대신 판정하지 않았다.

## 8. 보존·게시 상태를 읽는 규칙

- REC119 원 ZIP whole-byte/685payload PASS는 해당 recovery receipt의 증거다. 이번 inventory에서 그 archive를 재다운로드하지 않았다.
- REC125 StageC의 Dropbox wholeGET/SHA/CRC/181payload PASS와 Drive ACK+size/whole-byteNOT_RUN은 서로 다르다.
- REI221 새 local-flow ZIP은43unit files+AGENTS44members,656958B,SHA256 `7dfa9af96ec08f8a95a14104509e7dc82271c6668c56d39a17b6a5fd9d461e45`. 원래 ZIP과 archive SHA가 달라졌지만 member bytes/modes 일치의 packaging-only 복구로 기록됐다. 양 provider ACK+size이며 whole remote GET은 NOT_RUN이다.
- REI219 bootstrap/thermal/provider shared archive20,634,190B의 현재 receipt도 ACK+size/wholeGETNOT_RUN이다. 이전 다른 nuclear/dossier ZIP의 whole-byte PASS를 여기에 옮기지 않는다.
- REI222 successorS1 archive2,080,062B,178entries는 양 provider ACK+size이며 wholeGETNOT_RUN이다.

세부 primary receipts와 선택된 source 원문은 `GITHUB_PRIMARY_READS.json`에 있다. 이 inventory 자체는 parent에게 로컬 산출물로 전달하며, Git/backup의 실제 새 게시와 그 영수증은 parent가 통합한다.

## 9. 완료 범위와 보존할 전역 상태

이번 child의 작업은 **R1 최신 상태·중복 inventory, R2 source/code 재사용과 bounded 후보평가**다. 새 R5 proof나 C5 implementation을 수행하거나, 이후 단계 완료를 선언하지 않았다. 과학 실행0,old-campaign replay0,remote mutation0.

**Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET; global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.**

완료 low-z 결과는21-population 조건부 atomic/thermal 모델이다. 원래 prescribedT/UV pilot,동적T THERM01/02,조건부 passive nuclear audit의 범위를 서로 덮어쓰지 않는다. 모든 핵종의 완전 핵반응망·완전한 열역학·Bianchi recombination closure가 완료되었다고 쓰지 않는다.

### skill_context_used

실제 읽은 버전은 **physmath-research-loop1.3.0**이며 경로는
`/root/.codex/plugins/cache/created-by-me-remote/physmath-research-loop/1.3.0/skills/physmath-research-loop/` 아래
`SKILL.md`,`STAGE_SELECTION.md`,`references/THEORY_LOOP.md`,
`references/SUBAGENT_MODE.md`,`references/POLICY_INTEGRATION.md`다.

선택된 R1/R2 경계를 지켰고, 완료된 계산을 source/provenance 재사용으로 연결했다. 바뀐 HEAD는 한 번의 구체적 delta 조사로 해소했으며, global scientific acceptance와 artifact/metadata identity를 분리했다. 다음 실제 유도·코딩·최종 게시 판단은 parent 소유다.

## 10. 실제로 연결된 일곱 저장소의 종합표

아래 HEAD는 **관측한 관련 PR의 HEAD**다. 각 저장소의 모든 branch 가운데 유일한 최신 science HEAD라는 뜻은 아니다. REC/REI만 branch 및 open/closed PR 목록의 pagination을 완료했다. 나머지 다섯 저장소는 REI222가 실제 참조한 PR/DAG와 뒤에 명시한 로컬 인계의 관련 ref로 한정했다.

| 저장소 | 실제 조회한 관련 PR와 HEAD | 완료되어 재사용할 범위 | 현재 남은 의무와 원문 확인 수준 |
|---|---|---|---|
| rec_bianchi | [126](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/126): `12068893fab749ae1efb513563d0a86cc1cf649f`; [125](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/125): `b28b387fecd6cc71fddb98e95f336eba5f8a647f` | primordial q=0/source lanes, REC126 cohort, 각 thermal8 campaign, C2 saved512 diagnostic | 실제 선택 source/DAG/handoff까지 읽음. C3는HANDOFF_ONLY; Li ionic yield와 actual radiation/source feedback 열림 |
| rei_bianchi | [222](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/222): `b4b5d289aaad9ef167f683f19418b0ff87ed8425`; [221](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/221): `73c5e00cac26b4efc782446975bd6b6762555997` | REI129, atomic156+별도2, localflow103+별도96, D10 saved35×153 | 실제 successor DAG/HANDOFF/DELIVERY까지 읽음. physical daughter·beta partition·stopping/escape 및 coupled closure 열림 |
| BASS_HE | [87](https://github.com/cosmosapjw-quantum/BASS_HE/pull/87): `96338b7d3c04b18e31a080e56b34985d31921104` | caller-supplied pseudo-Maxwell finite-mass pair model PASS_SCOPED | PR본문 직접 읽음; 최신HE35완료상태는 REI222 successor DAG를 통해 확인. 실제 calibrated differential transport와 outgoing reactive gain/STF는 열림. 추가HE36로컬확인은 아래에 별도 기록 |
| WU088_HH | [135](https://github.com/cosmosapjw-quantum/WU088_HH/pull/135): `6c3b12554288893d5d7e221d77be943324285ceb`; 로컬 인계로 발견한 [136](https://github.com/cosmosapjw-quantum/WU088_HH/pull/136): `951182dd59bbb59dba454bbaab78ad56d029355a` | D event-energy72+8+27+cycle; 별도PHYS80 fixed-density CI/CX22→4/1와3ODE 완료 | 두PR본문 직접 읽음. D source-qualified PI/RR number/heat moments와low-T CI source coverage 열림. PHYS81로컬S0를 final로 승격하지 않음 |
| bass_cr | [97](https://github.com/cosmosapjw-quantum/bass_cr/pull/97): `15fd250ab91574bd4f3348e91d739a15a6ed6005` | C22A/B 및 SW91 source-domain excitation diagnostic; CCC finite-core4는 owner DAG에서 재사용 보고 | PR97본문 직접 읽음. **newerCCC branch5750489는 REI222 DAG의REF_ONLY**이며 그 branch파일을 직접 재검증하지 않음. tail/CI domain 열림 |
| bass | [181](https://github.com/cosmosapjw-quantum/bass/pull/181): `797d66580448dad7fc41f2c2db31fe0eb37908bf` | exact affine33→30,21outputs/RHS/Jac 비교,새IVP0 | PR본문 직접 읽음. algebraic reduction이 physical source closure나production 승인은 아님 |
| vigilode | [79](https://github.com/cosmosapjw-quantum/vigilode/pull/79): `69e83044aacfb9a8fd2c6c3fb1146911beeedd79` | C99full33WRMSnorm; matched30/33pair의2shortIVPs | PR본문 직접 읽음; 최신N1완료는 REI222 successor DAG의원문을 통해 확인. work counters UNKNOWN 보존; solver 전체 재검증 없음 |

동일한 기계판독 표는 `SEVEN_REPOSITORY_MAP.json` 및 `GITHUB_INVENTORY.json:seven_repository_map`에 있다. 다섯 인접 repo의 branch/PR 목록을 전부 읽었다거나 조직 전체를 조사했다고 쓰지 않는다.

### 부모가 발견한 로컬 작업의 제한된 추가 조사

주요 GitHub collection 조사는 **2026-10-22 22:40 UTC**를 기준으로 닫았다. 그 이후 부모가 실제 존재를 알린 세 로컬 root에서 관련 HANDOFF/STATE/DAG 이름을 선별하고 **10문서만** 읽었다. 관련 source snapshot과 SHA256/bytes/mtime/read time은 `LOCAL_PRIMARY_READS.json`에 보존했다. 이 세 root의 과학코드 실행·수정은0이다. 원래 inventory의 조회시각을 소급 변경하지 않았다.

1. **BASS_HE HE36-RMB** — `/tmp/he32_resume_20261022/repos/BASS_HE/research/he36_reactive_moment_bridge_20261023/`
   
   첫 직접 조회는18/20이었고, **22:47:43 UTC에 보존한 DAG snapshot은19/20, C10대기**였다. R1–R10과C1–C9의 완료·게시·backup ACK는 해당 로컬 DAG의 보고다. C9기록commit은 `0f67cb8b34d84c56d993841e2b57392a040f097e`이며 이 조사에서 원격PR/backup전체bytes까지 재검증한 것은 아니다. 앞서22:46:03에 관측한 로컬detachedHEAD `16a424b7290f484c57e97c8ed74f81e6d2043782`도 따로 보존해 finalpublicationHEAD로 혼용하지 않았다.
   
   실제 읽은 handoff는 finite suppliedCCC source의 Maxwellian α–δ와 온도미분, incoming-loss κ₁/κ₂, resolved reactive-source interface의 구현·진단을 다룬다. 129온도diagnostic은 완료돼 있으며 이 child는 반복하지 않았다. **incoming incident-energy moment는 net common-gas CI cooling이나 outgoing reactive STF가 아니다.** Global DAG의calibratedfinite-mass transport(B1), reaction gain/qualifiedisotopes/daughter/stopping(B2), commonT/commonvelocityclosure(B3), coupledgas(B4), metric/sourcefeedback(B5)는 열려 있다. 이 물질 충돌 모멘트 진행은 photon line-escape ANGULAR01과 다른 단위다.

2. **WU088_HH PHYS80** — `/tmp/hh_phys79_work/WU088_HH/research/hh_phys80_sandbox_reduction_20261022/`
   
   저장된 publication/handoff가 PR136을 명시하므로 **22:46:24 UTC에 그PR본문과HEAD를 실제 조회**했다. 최종 `951182dd59bbb59dba454bbaab78ad56d029355a`,science `fd18c59796175191bdd5f9b7ab2981d5e92836fd`다. 22→4/1 fixed-density isolated CI/CX 환원과3ODE 및3verifiedresumeskip은 완료다. 이 별도3ODE를 REC/REI cohort나 ANGULAR01실행수에 합치지 않는다.
   
   PR본문은 최종ZIP `a4957818f64038bd32548d9ac6fc0557271ab4333f4a3c42b5a802cc11bf3464`,1,746,247B,144payload에 대해 양provider wholeGET/SHA/CRC/payload/Gitidentity PASS를 보고한다. 이 child는 그 실제 producerreceipt를 읽은 것이며 백업ZIP을 다시 다운로드하지 않았다. 다음은 low-T CI source coverage이고 D-specificPI/RRmatchedenergy와otherthermal/spectralclosure는 열린다.

3. **WU088_HH PHYS81** — `/tmp/phys81_work_20261023/WU088_HH/research/hh_phys81_atomic_nuclear_source_contract_20261023/`
   
   읽은 stage snapshot은**22:00:58 UTC의S0**로 boundedintake완료,derivation진행,code/verification/scientificexecution미시작이다. primary Bell 전사와positivity유도,finiteCIwindow/hazard와capturephoton/recoil의계약을 준비한다. 인계 자체가 “최신 상태 확인 없이S0를final로 해석하지 않는다”고 경고하므로, 현재이후remote완료여부는 **NOT_CHECKED**로 남겼다. 이root에는 사용가능한Gitmetadata가없었으며 localcontents를remoteHEAD로꾸미지않았다.

관측된 추가 단위 가운데 선택한 **finite-τ scalar/PSTF line-escape certificate와 같은 완료 단위는 발견되지 않았다.** 이는 실제 읽은 문서에 한정한 중복 방지 판정이다. 신규 source theorem의 국제문헌상 최초성이나 미관측branch전체의 부재 증명은 아니다.
