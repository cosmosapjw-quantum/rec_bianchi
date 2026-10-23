# REC-HISTORY-01 독립 변경소스 검토

**판정: PASS_SCOPED. 동결된 boundary/history 단위의 과학적 완료를 막는
미해결 중대 결함은 없다. Parent REC-HISTORY는 PARTIAL을 유지한다.**

검토자: `/root/independent_review`. 원소스, 동결 계약, 구현, 별도 작성된
primary harness, 저장 출력 및 실제 PNG를 한 번의 연속 독립 검토에서 읽었다.
구현자나 harness 작성자의 판정을 정답으로 채택하지 않았고, 생산 코드를
수정하지 않았다. 검토자가 작성한 3개 추가 사례는 root의 중앙 controller가
한 번 실행했으며, 검토자가 원시 출력과 지표를 직접 확인했다.

여기서 unit은 `research/rec_history_boundary_20261023`, donor는
`research/rec_line_native_owner_20261023`다. GitHub expected-SHA 갱신,
최종 archive 및 Dropbox/Drive ACK는 root의 후속 delivery 절차이며,
이 보고서는 아직 실행되지 않은 publication의 성공을 증명하지 않는다.

## 1. 검토 대상의 고정 identity

REC 원소스 parent는 `a7c46fd8338971e2cefa776f5dd7b25a46974990`, root tree는
`dfa61d68aacfd3d3adc7ac5a5603f10e67349e3e`다. 별도 owner preflight는 해당
ancestry의 AGENTS 부재와 실제 branch/병렬 상태를 기록했다. 로컬 표현은
API로 확인한 source snapshot이며 Git checkout으로 오인하지 않았다.

| 대상 | SHA256 |
|---|---|
| 원 동결 계약 | `dc0e109608edddf458489066be4a1bae83bd2d89134535f2a0303c4c5efbcf35` |
| PREEXEC_ADDENDUM | `f522f5525dcf0f1abfe1c5987bb56c7fe350aa1af04213e5f2578b4b7ae9494f` |
| donor hydrogen.c | `421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b` |
| donor native CSV | `3a95862b9cd4f924d63020f39fc537b371133af6160e88c3409d8c69fc0c34b7` |
| donor PREPARED_BLOCKS.npz | `014ce6c467639b28086cfc1d6a70a09818544896b5d21e88508523bec111b9de` |
| history_boundary.py | `f0858a0ef231c62cf29c8d03ca769d3e9f8539a7809f890be5f4e22aa5fa0600` |
| run_history_checks.py | `608e1fb8e973387453775f170ca59109a9e5801bd2229939d7c3d09e86075f18` |
| native_oracle_build.py | `15c451cbfaa2f695441440fbc8ef257bc2f1c8e1047f74d179c693df5fedadfd` |
| 독립 tiny review script | `9ac7fe988ef39f627a3a425e89d736899e01f8b29cf3c99492f11c3f1972d57f` |

원 계약의 hash는 pre-review부터 primary 및 추가 검토까지 유지됐다.
네 가지 pre-code finding에 대한 addendum은 최초 과학 실행 전에 기록됐고,
어떤 오차 한계도 완화하지 않았다. 새 run은 LINE02 preparer나 이전
194개 checks, 6개 역사적 off-grid probe를 실행하지 않았다.

## 2. 원소스에서 독립적으로 확인한 물리·수학 계약

`hydrogen.c:401–543`에서 고정 thermodynamic/geometry 계수하에 history가
들어가는 항은 RHS다. Incoming 순서는 virtual311, Lyα, Lyβ이며,

\[
\delta F=M_*\delta X-B\delta u,\qquad
\delta X=M_*^{-1}B\delta u.
\]

실수준 두 행의 계수는 각각
`3*r0*x1s*1.664786871919931`과 `3*r*x1s`이고, virtual 행은
`Tvv0*x1s*(1-one_minus_Pib)`다. `one_minus_Pib`의 native branch를
저장 CSV에서 그대로 사용한다. Finite Lyα는 원 diagonal/source pair 및
해당 outgoing 경계만 바꾸며, diffusion/virtual/Lyβ/Lyγ 항을 중복 변경하지 않는다.
`source_at`는 증가분뿐 아니라 finite baseline source의 교체도 포함한다.

`hydrogen.c:633–718`의 outgoing314→incoming313 라우팅, line gap의 세
upstream owner, Lyα/Lyβ blue input의 두 virtual owner가 구현과 일치한다.
Lyγ blue incidence는 prescribed thermal boundary다. 보간은 알려진 두
과거 열만 사용하고 최신 저장 endpoint도 엄격히 거절한다. Literal
`-log((1+z)*E_source/E_target)` 경로를 유지하여 다른 log 연산 순서의
roundoff를 native parity에 섞지 않는다. Thermal startup과 signed
departures를 유지한다. Query가 knot이면 nonzero query tangent를 거절하고,
values-only tangent는 허용한다.

국소 boundary는

\[
s=\frac{x_{r,p}}{3x_{1s}},\quad A=1-e^{-\tau/q},\quad
d_{\rm out}=d_{\rm in}+(s-d_{\rm in})A
\]

이며 `expm1`로 jump를 안정적으로 계산한다. JVP의 `x1s`, `tau`, `q`
항과 부호가 직접 미분과 일치한다. Reference occupation을 복원해 absolute
입력 및 source positivity를 검사하며, 음수 departure를 자르지 않는다.
Representable finite transformed depth의 logarithm은 transmission underflow
후에도 보존한다.

Native phase normalization은

\[
G_N=3\times10^6\,{\tt LYA\_FACT}\quad[\mathrm{m}^{-3}],\qquad
R=G_NHq(d_{\rm out}-d_{\rm in})
\]

다. `q=1`이면 `nH_SI*r0*A*(xr_p-3*x1s*d_in)`과 같다. 이는 동일한
photon event의 boundary 표현이며, atomic internal energy `-E21_J*R`와
radiation `+E21_J*R`를 한 번만 소유한다. Native `E32`, `E42`의 literal도
보존됐다. 현대 SI 상수로 재계산한 phase density와 native convention을
같다고 주장하지 않는다.

## 3. 실제 primary 출력과 독립 추가 검토

`results/attempt001/SUMMARY.json`, `checks.jsonl`, `raw_cases.jsonl`,
`raw_arrays.npz`, native C extraction/build 기록을 읽었다. **608/608
checks가 PASS_SCOPED이고 실패·fatal exception이 없다.**

| 고정 실행 항목 | 실제 수 |
|---|---:|
| Local finite-ray controls | 54 |
| Scalar interpolation/native C 비교 | 20 |
| 전체 313-link mapping 비교 | 1 |
| Local/scalar/history JVP directions | 12 |
| Frozen full-system directions | 3 |
| Dense RHS solves 전체 | 8 |
| Manufactured analytic-history queries | 48 |
| Invalid/owner cases | 20 |
| Deliberate mutations | 4 |
| 원 primary figures | 2 |

313 native mapping의 최대 차이는 정확히 0이다. Algebraically equivalent
query clocks 사이에는 최대 `8.881784197001252e-16` 차이가 실제 기록되어,
literal clock 경로를 유지할 이유도 확인된다. 세 frozen 방향의 최대
backward scaled residual은 `1.2096536618663131e-15`로 동결된 `5e-12`
한계보다 작다. 독립 80-digit history JVP 비교의 최대 scaled error는
`2.213865713526952e-16`이다. 실제 resolved-state 비교의 최대치는
`2.9518867082851968e-15`로 `5e-9` gate 이내다.

저장 native binary64 matrix는 Z-matrix이며, 독립 solve로 얻은 양수 witness의
최솟값은 `0.0044175127019473745`, 보수적 `Mv` 하한의 최솟값은
`0.9999999997256701`이다. 이 certificate는 명시된 binary64 dot-product
가정과 이 한 행렬에 조건부다. Manufactured incoming 두 방향의 envelope
비율은 약 `0.989385`와 `0.988807`이다. 이 결과로 실제 cosmological history
오차가 인증되지는 않는다.

독립 검토는 primary와 다른 위험 지점의 **3개 추가 사례, 14개 checks**를
한 번 실행하여 모두 통과했다. 허용 최대 4개 중 나머지 한 개는 사용하지 않았다.

| 추가 사례 | 독립 기준과 결과 |
|---|---|
| Finite `tau=2` complex direction | 저장 primary native-C RHS/outgoing을 이용하고 real/imaginary 오차를 따로 비교했다. Imaginary 성분 소실 없이 source 최대 `2.4568080621836967e-16`, outgoing 최대 `3.2943459604747384e-16` scaled error. |
| Transparent direct Lyα pair | `tau=0`에서 직접 source·diagonal 제거, 다른 행·행렬 원소 보존, Lyα incoming 계수 0, outgoing passthrough를 확인했다. 해당 비교는 기록 정밀도에서 정확히 일치했다. |
| 음수 incoming의 physical reference | 양수 absolute occupations를 가진 음수 incoming/source 상태의 JVP가 80-digit 기준과 일치했다. 같은 상태의 zero reference는 거절됐다. Atomic-side number rate와 ledger의 scaled discrepancy는 `5.291823709076206e-17`이다. |

추가 사례는 **dense solve 0, C compile 0, old replay 0, IVP 0**이다.
`results/extra001/SUMMARY.json`, `checks.json`, `cases.json`, `raw_arrays.npz`
및 script identity를 보존한다. 원 native-C oracle 결과를 재사용했으며,
새 physical history를 만들어 추정하지 않았다.

## 4. Finding별 처리

| ID | Target / 영향 | 최소 수정과 최종 상태 |
|---|---|---|
| F1 | Native query clock의 다른 floating 연산 순서가 `1/h` slope로 증폭 | Optional `z_face` literal path 및 동일 eta0 적용. 전체 C mapping 오차 0. **CLOSED.** |
| F2 | Knot의 음수 query direction에 오른쪽 slope를 무조건 반환하면 잘못된 directional derivative | Nonzero query tangent를 `NONSMOOTH_QUERY`로 거절. 값 tangent는 유지. Primary guard 및 정적 branch 확인. **CLOSED.** |
| F3 | JVP/ledger에 reference를 전달하지 않으면 허용되는 음수 departure도 거절 | Optional reference 전달. Primary 음수 source와 독립 음수 incoming 검토 통과. **CLOSED.** |
| F4 | Finite `tau,q`라도 `tau/q` 또는 tangent intermediate가 overflow할 수 있음 | Transformed depth와 tangent finiteness를 명시적으로 검사. Overflow invalid control 통과. **CLOSED.** |
| F5 | 최초 `32eps*abs(M)abs(v)`는 최대313항 dot의 lower-bound 증거가 아님 | 보수적 `gamma_(2n+4)`, sumabs 오차, underflow reserve, outward rounding 도입. 실제 양수 하한 확인. **CLOSED.** |
| F6 | `rhs_real_statements`는 비인접 두 원문행을 붙였으므로 `exact_substring_of_source=false` | 원 BUILD를 유지하고 각 행의 byte identity·offset·SHA를 supplement로 확인. **CLOSED_WITH_SUPPLEMENT.** |
| F7 | 원 boundary PNG의 symlog 눈금 충돌 및 음수 tau 자동 범위 | 원 PNG 유지, 저장된54행만 재사용해 명시적 categorical 축으로 수정. 실제 수정 PNG 검토 통과. **CLOSED_WITH_PRESERVED_REPAIR.** |
| F8 | Primary controller의 sandbox/host PID 불일치로 live-session telemetry가 0 | 원 receipt 유지, 실제 작동했던 wall/RLIMIT/getrusage와 live-monitor 미관측을 구분. Host-session resolver 수정 후 후속 두 실행에서 live monitoring 확인. **DOCUMENTED_PRIMARY_LIMITATION; CORRECTED_FOR_LATER_ATTEMPTS.** |

F6 supplement에서 `sr[0]`은 원 C line453, byte offset21502, 107bytes,
SHA256 `2f4edb467e83cb75afd59057cd5295c5ce0ce22a20db8029cefa49cb3411d380`다.
`sr[1]`은 line464, offset21908, 87bytes,
SHA256 `f2b662082b141a141f0d4d506f85c936c6d915b53d73b87a0224394fef26d9f0`다.
연결된194bytes는 원문의 한 연속 substring이 아니며, 두 행 각각은 byte-identical이다.
함수 및 나머지 연속 fragment의 exact-substring 기록과 구분해야 한다.

## 5. 실제 figure 검토와 자원 기록

원본 두 PNG와 수정된 boundary PNG를 직접 열었다. 최종 boundary figure는
6개 tau와 q/drive 구분이 읽히며, 수평 간격이 tau에 비례하지 않고 offsets가
겹친 controls를 분리한다는 점을 명시한다. 원 interpolation figure는 두
manufactured family의 오차·조건부 bound·physical calibration 미완료 문구가
선명하다. 원 수치 및 원 PNG를 수정하지 않았다.

| 최종 표시 그림 | SHA256 |
|---|---|
| `results/figure_repair001/history_boundary_controls.png` | `79a7a32af43fe96d9914c52c8b5bdaf13efd6d91f92b11cfb6d0c7a32bf76d3f` |
| `results/attempt001/history_interpolation_bounds.png` | `fdd2ca95e03be5bf713e9023f30a84d327985c78926250225d2664e8dbb1d021` |

중앙 inclusive receipt 기준 primary CPU는 `3.1535100000000003 s`, wall은
`3.0765686070008087 s`다. Figure formatting과 추가 검토까지 포함한 새 단위의
누적 CPU는 **`4.848191000000001 s`**, execution wall은
**`4.7365679680006 s`**다. 보고된 최대 per-process peak RSS는
**105380 KiB**다. 60CPU s / 180wall s / 1thread / 1GiB allocation을
재설정하지 않았다. 이전 LINE02의 시간·실패·hold ledger는 별도로 보존한다.

Primary의 live aggregate session RSS/CPU는 관측되지 않았다. 따라서 원
receipt의 live-monitor enforcement 문구를 primary에 대해 소급 입증된 것으로
인용하면 안 된다. 실제 wall timeout, per-process RLIMIT_AS/RLIMIT_CPU,
최종 inclusive getrusage는 남아 있고 충분히 작은 실제 비용이 기록됐다.
수정 controller의 figure/review receipts는 host session을 찾았으며,
`live_session_monitor_available=true`다. 이 제한은 과학 오차 gate와 별도로
`provenance/RUNTIME_OBSERVATIONS.json`에 남는다.

## 6. 승인 범위와 남는 parent 의무

이 검토는 R6/C9에 필요한 독립 changed-source 검토를 **이번 단위에 한해**
충족한다. Scope를 `COMPLETE_SCOPED_BOUNDARY`로 유지하여 publication할 수
있는 과학적 근거가 있다. 추가 optional 계산은 필요하지 않다.

다음 항목은 이번 판정으로 닫히지 않는다.

- 실제 retained history의 curvature/endpoint uncertainty 또는 같은 domain의
  finer/reference history: `INPUT_DEPENDENT_UNCALIBRATED`.
- 방향별 Bianchi characteristic의 energy/direction/frame provider와 scalar
  history와의 정당한 결합.
- Thermodynamic coefficient까지 미분하는 전체 cosmological Jacobian,
  field feedback, 새 native evolution/IVP 및 global convergence.
- Production admission과 REI activation.

따라서 parent REC-HISTORY는 **PARTIAL**, Physical은 **HOLD**, REC_U5는
**HOLD_9_FAIL/HOLD_8_FAIL**, 누적 gate는 **CLOSED_HOLD_NOT_RESET**,
global convergence는 **NOT_RUN**, production은 **NOT_APPROVED**,
REI activation은 **false**로 유지해야 한다. 완료된 LINE02 과학 결과와
별도로 확인한 final-delivery receipt를 같은 증거로 혼동하지 않는다.
