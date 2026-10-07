# REI / REC 최신 상태 정찰 — 2026-10-04

읽기 전용 정찰이다. 게시된 시험 결과를 증거로 읽었으며 기존 과학 시험을 재실행하지 않았다.

| 저장소 | 실제 최신 전진 branch | HEAD | tree | PR |
|---|---|---|---|---|
| rei_bianchi | forward/rust-reion-kernels-20260922 | 67957715cf3336b89c27c1e59c33ca23098f8934 | f92a946b3256cccc3f268debd2d0ec463c9a43e5 | 83 draft |
| rec_bianchi | forward/rust-he-sources-20260922 | 5694a5c7ef487adc969f38ae9112b796396216ca | db4e061e723daf933e74013527068ebaffaa08f8 | 81 draft |

각 recursive tree는 truncated=false다. 두 선택 tree 모두 AGENTS.md 경로는 없다. main의 오래된 상태와 선택한 전진 branch를 혼동하지 않는다. branch 목록, 최근 commit 목록과 원문 문서는 하위 폴더에 보존한다.

## REI 증분

2026-10-04 23:08 KST의 PB01 commit은 Peebles FLRW 복원 조건과 현재 Case-A closure의 MODEL_SCOPE_MISMATCH를 이미 연구했다. 19개 기호 항등식, 135 scalar점, Saha 4점, finite mixing 6점, 강제 선형 QSS 4회, Sobolev 7점, 등방극한 4개, invalid-input 7개 결과가 게시돼 있다. 이를 새 계산으로 세거나 되풀이하지 않는다.

그 직전 283153da9842218662451b61843bcc859d3eeb12에서 F01 Rust atomic_provider 및 homogeneous_rates가 구현됐다. Grackle 18 계수와 Verner 3종을 연결했고, C 540점과 mpmath 24점 비교, 전체 55 tests PASS가 기록돼 있다. 최종 underflow 수정본은 Host가 닫았으며 두 번째 독립 재리뷰는 없었다. F00/F01/F02 완료이며 Codex 다음은 F03 결합 map다. derivative enclosure, actual nonlinear remainder, 물리 history admission은 HOLD다.

FT06에는 실제 제한된 연구용 시간진화가 있다. 45 unique saved pilot runs, 마지막 runner 49 solves, 최대 787 변수, 128 angular directions다. prescribed a_bar=exp(0.03s), s=t/1e13 s, beta=epsilon*(1/3,2/3,-1)*s, epsilon=.02, initial T=50000 K, nH=1e-4 cm^-3, Case-A, 20/35/70 eV delta lines다. 128방향 deltaT=+0.0216190194 K와 여섯 축 deltaT=-0.0228612997 K가 달라 M4 각도 정밀도 중요성을 보여 준다. 이것은 Einstein-solved cosmology도 물리적 EoR tau도 아니며 rigorous uniform error bound가 없다. 따라서 'history를 전혀 실행하지 않았다'는 전역 진술은 현재 틀리다.

PB01 다음 task는 REI-CHAT-PB02_SOURCE_BOUND_REDUCTION_CONTRACT다. 실제 retained level/radiation residual이나 REC-owner를 exact commit/path/blob에 연결해야 한다. Peebles C를 외부 주입한 scalar oracle만으로 현재 Case-A closure에서 복원됐다고 주장할 수 없다. 기존 F00 lock은 소급 치환하지 않는다. FT07은 사용자 우선순위 변경에 의해 deferred다.

## REC 증분과 구현 위치

REC 최신 branch는 9월 30일에 유한 tilt frame.rs와 physical screen.rs까지 추가했다. Cargo crate는 rust/rec_microphysics이며 Rust edition 2024, rust-version=1.94, 외부 dependencies 없음이다. lib.rs는 coverage/frame/he_singlet/ledger/screen만 공개한다. 이 selected Rust 경로에는 수소 n=2 residual 또는 Peebles 함수가 없다. 과거 Python/C HyRec 경로의 부재를 뜻하지는 않는다.

SCREEN_VALIDATION.json의 최신 결과는 기존 He 76 + frame 8 + screen 3 + doctest 1 = 88 tests PASS, fixed-input parity 251 records/3027 components/111 expected-error records, Decimal oracle 96 cases/3264 components다. 전체 재결합 궤적을 인증한 것은 아니다. selected-He의 기존 allow_consumer_integration=false 및 full T4 Gate I deferred를 유지한다.

기존 Python src/full_bianchi_hyrec/trajectory/primitive_rates.py는 October-2012 원 HyRec의 2s/2p effective rate tables를 source-order cubic interpolation으로 읽고 SI로 변환한다. Tr table domain 0.004–0.4 eV, Tm/Tr 0.1–1.0, beta array(2), R2p2s, primitive arrays(311)가 있다. 이 표는 기존 원 HyRec source에 결박돼 있으며 단순 case-B alpha 하나로 바꾸거나 DAlpha를 미분으로 오인하면 안 된다.

state/PROJECT_STATE.json의 98%는 2026-08-11 추정치다. 현재 완료율로 쓰지 않는다. 원 HyRec+COM full macro는 E1C single-owner replacement 문제를 유지한다. canonical native spikes 136..143와 COM overlap, crossing edges (135,136),(143,144), 외부 Schur/internal deposition/interface ledger를 동시에 닫아야 한다. 이 장기 경로를 새 pure-H reference module의 선행조건으로 만들 필요는 없다.

## 권장한 이번 경계

REC 기존 전진 branch에 별도 pure-H one-temperature thick-Sobolev retained-shell/QSS reference module을 추가하고 실제 Rust consumer API와 외부 독립 oracle를 연결한다. 원 selected-He API와 과거 E1C owner를 건드리지 않는다. beta_P와 beta_shell의 factor 4, per-2p Ralpha의 factor 3, thermal inverse, C가 작은 점, redshift sign, finite excited-population correction 및 QSS lag를 검증한다. Case-B coefficient와 상수의 external source identity는 별도 명시한다.

PB01의 x2<<1 모형과 실제 x1=1-xp-x2 retained shell의 차이는 명시적인 근사 차이다. 이 차이를 tolerance widening으로 숨기지 않는다. 표준 Peebles와의 비교는 동일 온도·밀도·background·alphaB·상수에서 한다. 총 recombination/continuum source와 shell-to-ground source를 동시에 구분하여 에너지 이중 계상을 막는다.

이번 목적에 적합한 publication target은 rec_bianchi / forward/rust-he-sources-20260922 / 기존 draft PR81다. REI에는 동일 branch PR83에 exact REC dependency candidate와 PB02 수령 문서를 추가하는 것이 자연스럽다. 실제 REI call site import가 없으면 connected-consumer PASS를 주장하지 않는다.

## Intake 검증

rec crate의 Cargo.toml/lock, src 6개, tests 3개 총 11개를 GitHub exact commit에서 가져왔다. 로컬 Git blob SHA-1 11/11이 GitHub file identity와 일치했다. 결과는 REC_CRATE_INTAKE_CHECK.json이다. 이 검사는 source byte identity이며 기존 테스트 재실행이나 과학적 인증이 아니다.
