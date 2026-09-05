# REC-DONOR-02C — work 스레드 실행 handoff

## 목적과 이번 checkpoint

`REC-DONOR-02C_TYPED_RESOLVED_NUMERICAL_ADAPTER` 하나를 구현하고 검증한 뒤 checkpoint한다. 기존 `COMSourceDepositionPlan`을 재구현하지 않는다. 실제 immutable 배열, 명시적인 source/target/channel identity, 고정-map action/JVP, 실행 결과를 묶는 작은 adapter만 추가한다.

이 문서는 실행 지시와 현재 상태의 checkpoint다. 새 adapter 코드와 새 RED/GREEN 실행은 아직 없다. 작성 스레드에서는 container.exec와 Python을 각각 한 번 시도했으나 process 시작 전에 ClientError가 발생했다. WolframContext도 MCP SSE HTTP404로 종료했다. 동등한 runtime probe는 중단했다. GitHub/Atlassian 쓰기와 로컬 runtime은 별도 경로다. 기존 GitHub-hosted 실행은 성공했으므로 모든 runtime이 불가능하다고 일반화하지 않는다.

사용자의 계속 진행 및 게시 승인 범위에서 REC 전용 격리 branch, scoped commit, non-force push, Draft PR, REC 관련 Jira/Confluence append-only 동기화를 수행한다. main/canonical/기존 evidence branch 수정, rebase/force-push, ready/merge, 다른 repository source 수정, provider 승격은 하지 않는다.

## 1. 정확한 기준점

```text
repository                 cosmosapjw-quantum/rec_bianchi
preferred local repository $HOME/Dropbox/bianchi/rec_bianchi
source PR                  61
source branch              research/rec-donor02b-explicit-map-probe-20260905-r1
source base commit         30576407d50e10b88a32b65a9510db61e4159e1b
source base tree           c9ceccb9a66162d4f76832b85756b8c66692895d
previous executed commit   6deb256753d91b8aa5f85a85a0786c02ea0670da
previous executed tree     0383fad8aac23c8c59d1867acfd5a0ccd578aced

unchanged COM component
src/full_bianchi_hyrec/trajectory/com_source_deposition.py
blob a3662cf399f14b7148d880266825be12baf934a0

unchanged affine-source module
src/full_bianchi_hyrec/physical_source_authority.py
blob 6d4f39d48993c4715f5002ba068e8dcf98336be3

handoff delivery branch
handoff/rec-donor02c-resolved-adapter-work-20260905-r1
handoff file
docs/handoffs/rec_donor02c_work_20260905/WORK_THREAD_PROMPT.md
```

처음에 최신 REC PR/branch를 한 번 읽어 동시 작업 중인 동일 adapter가 있는지 확인한다. 이미 존재하면 경쟁 구현을 만들지 않고 exact diff와 evidence를 읽어 재사용한다. 문서 head가 달라졌다는 이유로 기존 수치 evidence를 폐기하지 않는다. 다른 source 바이트를 위 pin으로 가장하지도 않는다.

전달받은 delivery commit을 pin한다. 위 source base의 직접 child이며 diff가 이 handoff 파일 하나인지 확인한 뒤 그 delivery commit에서 execution child를 만든다. 이 관계를 확인할 수 없으면 위 immutable source base에서 별도 worktree를 만들고 이 문서는 외부 instruction으로 사용하며 두 identity를 따로 기록한다. floating main은 사용하지 않는다.

권장 execution branch는 `research/rec-donor02c-resolved-numerical-adapter-20260905-r1`이다. 이미 존재하면 덮어쓰지 않는다. 기존 Dropbox checkout의 dirty/untracked 파일을 보존하며 switch/reset/clean/stash하지 않는다. 새 격리 worktree에서만 수정한다.

## 2. 완료된 작업은 재사용한다

PR #60은 PR #58 구현과 PR #59 amendment를 결합해 실행 commit `b062befcea8cebe45eab3c6c23e9ddcaeb5541e8`에서 27/27 focused tests가 통과했다. PR #58의 과거 26/27 결과는 역사적 실패 그대로다.

PR #61은 기존 COM component를 explicit manufactured SI 배열로 실행했다. workflow `33940027916`, job `101235487962`; 72 action scalar와 72 fixed-map JVP scalar가 독립 Fraction 합과 이 유한 dyadic corpus에서 정확히 일치했다. number/energy 및 source/photon cG^a 비교, invalid-input 6개, normalization mutant 2개도 보존돼 있다. 이는 새 production adapter 또는 physical source admission이 아니다.

근거 파일:
- `docs/research/rec_donor02_reconciled/CLOSEOUT.json`
- `docs/research/rec_donor02b_deposition/CLOSEOUT.json`
- `scripts/probe_rec_donor02b_deposition.py`

PR61 artifact는 `9961501445`, GitHub-reported ZIP SHA256은 `9c5ee0e936a63ada772a0b652c6819516b7e66cff9241746d840332541169d8b`다. 독립 local ZIP rehash와 두 PNG의 rendered visual audit은 미수행이다. 새로 하지 않으면 그대로 미수행으로 남긴다. 일반 repository quick verifier는 별도 FAIL이며 full pytest는 실행되지 않았다. PR61 일반 run `33940027934`의 상세 원인은 다른 run의 whitespace 진단으로 자동 대체하지 않는다.

## 3. 먼저 읽을 파일과 정책 범위

```text
AGENTS.md
docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md
HANDOFF_PROMPT.md
docs/research/rec_donor02_contract_repair/CONTRACT_AMENDMENT.md
src/full_bianchi_hyrec/physical_source_authority.py
src/full_bianchi_hyrec/trajectory/com_source_deposition.py
tests/trajectory/test_rec_donor01_typed_physical_source_red.py
tests/trajectory/test_rec_donor02_source_safety.py
tests/trajectory/test_split_context_and_deposition.py
scripts/probe_rec_donor02b_deposition.py
```

root HANDOFF_PROMPT의 no-write/single-formal-run 조항은 거기에 지정된 역사적 REC-NEXT-03 replay용이다. 이번 별도 승인 작업에 확대 적용해 formal provisioning으로 돌아가지 않는다. 물리 face/provider 미승격, 단위/frame/source 경계, evidence 보존은 그대로 유지한다.

## 4. 허용 변경 경로

```text
새 production 파일 하나
src/full_bianchi_hyrec/resolved_source_deposition.py

새 focused test 하나
tests/trajectory/test_rec_donor02c_resolved_deposition.py

최소 checkpoint
docs/research/rec_donor02c_resolved_adapter/CHECKPOINT.md
docs/research/rec_donor02c_resolved_adapter/RESULT.json

hosted execution에 실제로 필요할 때만
.github/workflows/rec-donor02c-resolved-adapter.yml
scripts/run_rec_donor02c_resolved_adapter.py
```

기존 COM/affine production 파일, PR59 repaired assertions, 과거 runner/manifest/closeout/evidence는 수정하지 않는다. 패키지 refactor, __init__ 재구성, generic authority framework, third evolution backend를 만들지 않는다.

## 5. 새 adapter의 최소 계약

다음은 새 acceptance specification이며 이미 존재하는 public API라는 뜻이 아니다. 최종 이름/필드는 focused test에서 한 번 정한다.

1. 실제 `COMSourceDepositionPlan`을 받는다. map/measure 해시만으로 실행을 허용하지 않는다.
2. source/channel 순서, target 및 angular sampling identity, hydrogen-rest frame, physical-second time basis와 SI 단위를 입력·결과에 연결한다. source/target/channel mismatch는 계산 전에 거부한다.
3. 실제 B, mu, target/source energies, weights/directions의 값·shape·dtype·정의된 순서를 digest에 반영한다. ID 문자열만 같고 배열이 다르면 같은 operator가 아니다. mutable input alias를 남기지 않는다.
4. `R[S]` 또는 `R[S,A]`와 같은 규칙의 tangent를 받는다. 스칼라를 여러 channel에 암묵적으로 복제하지 않는다. signed rate를 occupation으로 취급해 clip하지 않는다.
5. action은 기존 `plan.apply()`, JVP는 `plan.jvp()`를 호출한다. production에서 행렬 곱을 다시 구현하지 않는다. 독립 Fraction 합은 test oracle에만 둔다.
6. 기존 validation을 재사용한다. density/tangent는 bool, complex, nonfinite를 거부하는 명시적 scalar-domain control을 wrapper 경계에서 적용한다. COM core를 바꾸지 않는다.
7. 고정 B, mu, energies, directions의 partial JVP만 제공한다. moving-map/measure/event derivative를 지원하는 척하거나 입력을 조용히 버리지 않는다.
8. 성공한 호출 뒤에만 immutable output과 operator/input/output identity, action-vs-JVP 종류를 묶는 실행 receipt를 만든다. R/dR/n_H/dn_H 변화는 evaluation identity에 반영되고 operator identity는 timestamp/host path와 무관하다.
9. 한 번 적용은 한 평가 안에서 n_H/mu를 중복 적용하지 않는다는 의미다. 같은 입력의 재평가와 JVP는 허용한다. global consumed-bit, accepted-step counter, solver transaction ledger는 만들지 않는다.
10. 기존 unresolved hash-only `deposit_packet_rate()`는 계속 거부한다. 새 resolved numerical 경로는 별도다. 실제 연산 성공과 atomic-source 인증을 구별하며 이번에는 `physical_source_authenticated=false`, `provider_admitted=false`, `NO_PASS_REC_PHYSICAL_SPLIT`을 유지한다. caller flag만으로 인증을 true로 만들지 않는다.

## 6. 공식과 이미 실행된 fixture

고정-map 법칙:

```text
A[i,a]  = n_H/mu[i] * sum_s B[i,s] R[s,a]
dA[i,a] = 1/mu[i] * sum_s B[i,s] (dn_H R[s,a] + n_H dR[s,a])
```

n_H와 mu는 m^-3, B는 무차원, R은 H^-1 s^-1, occupation action은 s^-1이다. weights는 sum=1의 평균 measure다. cG^a는 (-,+,+,+) hydrogen orthonormal frame에서 네 성분 모두 W m^-3로 보고한다. 자연단위를 선언하지 않는다. c, hbar, k_B, 4*pi 인자를 임의 추가하지 않는다.

PR61의 manufactured fixture를 그대로 재사용한다:

```text
n_H = 2^20 m^-3
mu = (2^21, 2^22, 2^23) m^-3
E0 = 2^-60 J
E = (1,2,3)*E0
Es = (3/2,5/2)*E0
weights = (1/2,1/2)
directions = ((0,0,1),(0,0,-1))
B  = ((1/2,0),(1/2,1/2),(0,1/2))
B2 = ((3/4,1/4),(0,0),(1/4,3/4))
R  = ((2,-1),(4,3))
dR = ((1,2),(-2,1))
dn_H = n_H/4

A(B)  = ((0.5,-0.25),(0.75,0.25),(0.25,0.1875)) s^-1
dA(B) = ((0.375,0.4375),(0.0625,0.4375),(-0.0625,0.109375)) s^-1
A(B2) = ((1.25,0),(0,0),(0.4375,0.25)) s^-1
max(abs(A(B)-A(B2))) = 0.75 s^-1
```

두 map은 nonnegative이며 unit column sum과 같은 energy moments를 가진다. B2의 출력을 B와 같게 만들면 실패다. 두 operator digest는 달라야 한다. 어느 map도 물리 REC map으로 선택하지 않는다. 두 angular 채널은 full-sky reconstruction이나 universal two-direction approximation이 아니다.

각 방향의 보존식:
`sum_i mu_i A_ia = n_H sum_s R_sa`,
`sum_i E_i mu_i A_ia = n_H sum_s Es_s R_sa`.

전체 moving-input 미분에는 `+n_H/mu*dB*R - A*dmu/mu`가 추가된다. PR61의 dmu/mu=1/2 진단은 누락 항 최대 0.375 s^-1을 보였지만 full moving JVP 구현은 아니다. Number/energy 보존으로 physical B 또는 detailed balance를 추론하지 않는다.

## 7. 실행과 검증

- [ ] Python/numpy/scipy/pytest 및 정상 package import를 확인하고 외부 venv와 실행 버전을 기록한다. 필요한 최소 설치만 한다. PR61 실행 환경은 Python3.12.3, numpy2.2.6, scipy1.15.3, sympy1.14.0, matplotlib3.10.3이었다. 다른 host의 Python patch/metadata 차이는 source identity 실패가 아니다. SciPy는 trajectory import chain에서 필요했던 실제 의존성이다. 이 작업에 BASS Rust/JAX는 필요하지 않다.
- [ ] 새 behavior의 최소 failing tests를 먼저 실행한다. syntax/import/setup 실패를 intended RED로 세지 않는다. 실행 경로가 정상이라면 RED 문서만 게시하고 끝내지 않는다.
- [ ] 위 경계만 구현하고 같은 focused tests를 GREEN으로 만든다. 한 번의 risk-scoped 검증, 필요 시 한 번의 targeted repair 후 checkpoint한다.
- [ ] 새 suite 명령 예시: `PYTHONPATH=src python -B -m pytest -q -p no:cacheprovider tests/trajectory/test_rec_donor02c_resolved_deposition.py`. PYTHONDONTWRITEBYTECODE=1, 외부 cache/output 경로를 사용하고 실제 명령/exit code를 기록한다.
- [ ] 기존 source 27개는 `TestRecDonor01TypedPhysicalSourceRed`와 `TestRecDonor02SourceSafety`를 각각 한 번 수집한다. imported class의 중복 수집을 성과로 세지 않는다. 기존 deposition test에서 직접 영향을 받는 action/JVP/보존/거부 검사를 재사용한다.
- [ ] exact A/dA/B2, density-tangent 누락 mutant, zero source, signed absorption, 잘못된 shape/단위/nonfinite, source/target/channel mismatch, input alias mutation, operator-vs-evaluation identity, 두 fresh process 결정적 hash, legacy unresolved refusal, 반복 평가, per-call duplicate normalization을 검사한다. 선언한 count만 복사하는 sham receipt는 금지한다.
- [ ] 원래 `probe_rec_donor02b_deposition.py`의 main은 src tree unchanged와 네 경로만 허용하는 historical gate다. 새 production child에서 그대로 재실행하거나 allowlist를 넓히지 않는다. parent evidence를 보존하고 scalar oracle/fixture만 새 test에서 필요한 만큼 재사용한다. 과거 frozen RED/reconciled runner도 새 child gate로 억지 사용하지 않는다.
- [ ] 새 실제 배열과 Fraction residual을 작은 plot/표로 남긴다. 0 residual을 log plot에서 숨기지 않는다. 실제로 PNG를 열어 읽은 경우에만 rendered audit을 완료로 기록한다. 기존 PNG를 검증 후 읽을 수 있으면 재생성 없이 open visual-review 항목을 닫는다. 시각 접근 불가를 numerical FAIL이나 visual PASS로 바꾸지 않는다.
- [ ] PHYS-MATH와 PHYS-MATH-CODE 관점 검토를 한 번씩 한다. 같은 executor가 했다면 independent review라 부르지 않는다. 독립 reviewer는 가능할 때 read-only 1회 이내다. broad suite/과거 whole-repo whitespace 정리는 섞지 않는다.

## 8. Runtime 실패 처리

로컬 process가 시작되지 않으면 다른 실행 경로 한 개만 검사한다. 동등한 pre-execution 실패 두 번 뒤에는 중단한다. 수학 FAIL도 테스트 PASS도 아니다.

GitHub 쓰기와 hosted 실행이 가능하면 이 작업용 workflow 한 개를 사용할 수 있다. exact source SHA checkout, persist-credentials=false, contents=read로 제한한다. `runner.temp`를 job-level env에서 사용했던 과거 오류를 반복하지 않는다. shell step의 RUNNER_TEMP와 외부 output을 쓴다. setup/tests exit를 분리하고 artifact를 실패 시에도 보존한다.

work 스레드에서도 막히면 `BLOCKED_BY_RUNTIME`과 실제 오류를 남기고 멈춘다. 새 승인 요청이나 하네스 재설계를 반복하지 않는다. 다른 process/Wolfram license/GUI를 종료하거나 수정하지 않는다. optional CAS 부재를 이 adapter의 선행 blocker로 만들지 않는다. 실행 가능한 Fraction/SymPy 근거의 정확한 범위를 기록한다.

## 9. 게시와 종료 기준

source base, delivery commit, 테스트 당시 code tree/파일 hash, executed commit, 최종 documentation commit을 구별한다. 테스트 당시 uncommitted였다면 그렇게 적고 committed-head execution으로 재명명하지 않는다.

최대 PASS 분류는 `PASS_REC_DONOR02C_RESOLVED_NUMERICAL_ADAPTER_NOT_PHYSICAL_ADMISSION`이다. 미실행은 NOT_EXECUTED/BLOCKED, 실제 실패는 구체적인 FAIL이다. authenticated kernel, physical split, provider-ready, repository-wide all-green을 주장하지 않는다.

새 execution child만 commit/non-force push하고 Draft PR로 보존한다. remote parent/tree/변경 경로를 readback한다. 기존 branch를 덮어쓰지 않는다. source/semantics 충돌은 보존하고 멈추되 timestamp-only drift로 전체 연구를 재시작하지 않는다.

Atlassian REC-only append 대상:
`cloud=e1cd4b3d-2781-4a6f-9f58-e35aa48753db`, `BASS-19`, `BASS-26`, FED-02 page `27492353`.
기존 PR61 기록은 issue comments 10580/10581, footer 28573697이다. 삭제/덮어쓰기 없이 새 exact head, 실행 여부, 결과와 next action을 추가한다. status/official dependency links/다른 repo snapshots는 변경하지 않는다. 쓰기 불가 시 결과와 게시 body를 보존하고 미게시를 명시한다.

최종 보고는 실제 구현, 실제 시험, 미실행 항목, remote 링크, 남은 물리 blocker, 정확히 한 next action을 제시한다. 통과 뒤 후보는 physical source/channel 및 실제 map의 owner-resolved intake이며, 이번에는 그 후속 물리 작업을 실행하지 않는다.

## 10. 참고자료의 범위

SciSpace 검색과 arXiv:1011.3758v2, arXiv:0803.0808v2의 공개 초록을 대조했다. radiation/atomic-population 결합과 resonant two-photon/Raman transfer는 moment-conserving 행렬 선택과 별도 물리다. 원 논문 전체 감사나 새 physical kernel 유도를 했다는 주장은 없다. 문헌은 method/scope 참고일 뿐 배열 인증의 authority가 아니다.

첨부 Paper I/II의 static coarse-graining을 transport closure로 바꾸지 않는다. 옛 BASS R5 로그의 jax/bianchi_rustcore 부재는 이 REC component의 실패나 필수 설치 목록이 아니다.

현재 durable 결과는 PR60 source protocol과 PR61 manufactured COM probe다. 새 adapter는 아직 없다. 최소 구현-검증-checkpoint 한 번이 이 handoff의 목적이다.
