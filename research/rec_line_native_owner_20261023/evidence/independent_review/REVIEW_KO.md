# LINE02 독립 검토 최종 판정 — 단일 R6 → C9 pass 완료

**재구성된 LINE02 frozen-state source adapter를 선언된 범위에서 수용한다. 현재 작업의 material blocker는 0이다.** 원전·수학의 독립 확인, 두 재구성 모듈의 정적 검토, 최초 fresh primary의 전체 저장 원증거와 실제 PNG 세 장의 확인으로 판정했다. 이 판정은 생산 배포 승인이나 전체 물리 closure가 아니다.

역사적 여섯 off-grid probe는 실제 도구 stdout에 남은 과거 관측으로만 보존한다. 그 전체 raw와 옛 구현 해시는 유실됐으므로 **재구성 코드의 numerical acceptance에 사용하지 않았다**. 이번 동일-pass 계속에서 추가 probe, solver 실행, 각도 quadrature와 primary 재실행은 모두 0이다.

## 1. 현재 검토 대상의 정확한 결속

| 파일 | 현재 SHA256 | Bytes |
|---|---|---:|
| `code/native_line_owner.py` | `96dbf48afa3a85e6a6d7f5a4affd03dec64f3647cbc6603fe7a55a51895d6197` | 17,870 |
| `code/run_line02.py` | `630261cd84ed3b5e58c2a5fd2b4792edbcab603b8781fa5fa718cfe2a5bb9e53` | 32,677 |

현재 파일, primary `code_snapshot`, 검토자가 보존한 정적 검토 snapshot의 bytes가 서로 일치한다. Primary 환경에 기록된 아홉 source/contract identity, attempt manifest의 모든 payload, plot manifest의 source/PNG/PDF hashes도 실제 파일과 대조해 불일치가 없었다. 원 immutable input/donor의 여덟 사전 pin 역시 복구 뒤 그대로다. `PRIMARY_EVIDENCE_INSPECTION.json`에 현재 읽은 행·배열 크기·원증거 집계·해시 결과를 기록했다.

실제 실행 receipt는 exit 0, science attempt 1, repeat 0을 기록한다. 네 BLAS/OMP 계열 thread 환경은 모두 1, timeout은 180초였다. Matplotlib의 읽기 불가 기본 cache 경고는 `/tmp` cache 사용으로 처리됐으며 과학 실행 실패가 아니다. `FAILURE` 파일은 없다. Attempt의 원본 파일은 검토자가 수정하지 않았다.

## 2. 새 primary 결과와 frozen acceptance

| 항목 | 실제 새 증거 | 수용 기준/의미 |
|---|---:|---|
| Primary checks | **194 / 194 통과** | 원 CHECKS 행과 요약 일치 |
| Owner controls | **7** | full313 reference 7, direct Schur2 reference 7 |
| JVP directions | **12** | baseline/half-line/blue-plus × 4; complex313 reference 12 |
| Angular source rows | **9** | native thick 3, synthetic finite quadrature 6 |
| Synthetic bound rank queries | **12** | 기존 여섯 synthetic case의 base+finite sub-evaluation |
| Invalid / mutation | **12 / 2** | domain·중복 owner 거부; energy sign 및 unmatched source pair 검출 |
| Plot rank samples | **183** | 세 loss control × 61 incoming-boundary 값 |
| Rank queries 전체 | **202** | 7 + 12 + 183 |
| Native runtime / IVP / historical replay | **0 / 0 / 0** | 동결된 algebraic 계산만 수행 |
| Primary elapsed | **2.07720804 s** | 해당 환경·해당 범위의 실측; 보편 speedup 주장 없음 |

Owner와 JVP의 full 313 원 배열을 읽었고, 저장 reference와 actual 배열의 차이를 집계한 값이 기록된 error fields와 정확히 일치했다. 이는 기존 저장 증거를 읽고 집계한 작업이며 새 입력·solve가 아니다.

| 수치 판별량 | 관측 최대 | Frozen limit |
|---|---:|---:|
| Rank/full real component error | `8.16418551131124e-15` | `5e-10` |
| Rank/full virtual component error | `7.716887860999565e-15` | `5e-10` |
| Full componentwise backward residual | `4.423318876663953e-16` | `5e-12` |
| Residual JVP scaled error | `2.7217633666152512e-14` | `5e-9` |
| Solved-state JVP scaled error | `3.3032991548635334e-12` | `5e-9` |
| Native tensor rotation discrepancy | `8.972059582075359e-18` | `5e-10 × C`, 현재 C=1 |

JVP absolute infinity errors는 residual `1.550963648536927e-25`, solution `1.3866695599588098e-31`이다. Native saved snapshot의 backward residual `3.066056354007571e-16`과 prepared baseline의 `3.317529480136552e-16`을 별도 기록했다. 원 snapshot을 정확한 algebraic zero로 부르지 않는다.

Native net source를 70자리 source-decimal 기준과 비교한 absolute error는 `1.8417336200692332e-30`, 허용량은 departure gross scale에 기초한 `2.1324187903834533e-26`이다. Net source 자체를 분모로 사용하지 않았다. Literal native LYA_FACT는 유지되며 modern SI hc 재구성과의 `-2.661653527580299e-7` 차이는 별도 source convention 차이로 남는다.

Owner controls의 최소 physical population은 `6.532410250609739e-15`, 최소 virtual total occupation은 `4.106457877721425e-19`, 최소 blue total occupation은 `7.709689027638636e-18`로 모두 양수다. 183 plot sample에서 최소 x2p는 `1.969132805840401e-14`다. Signed emission/absorption은 허용하되 clipping으로 positivity를 만들지 않았다.

## 3. 현재 물리·수학적 수용 범위

Native May-2012 코드의 direct Lyα owner는 Trr11의 `r0`와 sr1의 `r0 b0` 짝이다. Full replacement는 `M*=M+(r-r0)EEᵀ`, `s*=s+(r b-r0 b0)E`이며 다른 diagonal, mixing, two-photon/Raman, virtual diffusion, coupling blocks와 incoming history를 고정한다. Native Tvr 저장 모양과 물리 행렬의 전치, tridiagonal 위·아래 방향은 원 코드와 새 구현 모두 일치한다.

`K=Trr-Trv V⁻¹ Tvrᵀ`, `j=sr-Trv V⁻¹sv`에서 one-time preparation을 거쳐 source response를 scalar rank-one update로 계산한다. 실제 `gamma0=0.005045333040636401`, `cond2(K)=24.509360369477253`이고 line-removed host inverse가 nonnegative임을 원증거로 확인했다. eta margin은 전체 condition number의 대체물이 아니며 실제 source update마다 검사한다.

Residual와 solved-state JVP는 다른 모든 계수를 고정한 partial derivative다. Stable drive `D*=[D0-(1-gamma0)(b-b0)]/eta` 및 `1-gamma_base=(1-gamma0)/eta`는 같은 rank-one 해에서 도출된다. 새 primary는 이 구현으로 seven source controls, full313/Schur references, complex-step JVP를 실제 비교했다.

Number/energy ledger와 zero ionic/electron yield는 직접 bound-bound event에 국한된다. 전체 xe는 excited populations를 통해 간접 변할 수 있다. Native Wien/ground-opacity source와 LINE01 full Planck/stimulated operator의 off-equilibrium 차이를 유지하며 source constants와의 차이도 섞지 않는다. Angular PSTF는 주입률이며 저장된 radiation stress 상태가 아니다.

## 4. Finite-opacity bounds와 현재 분해능

Native optical depth는 `578353783.1996146`이다. 세 native event 모두 admitted thick C=1을 사용하고, triaxial/rotated scalar를 바꾸지 않으면서 tensor injection을 만든다. 실제 `log(delta)`는 isotropic `-578353783.1996146`, triaxial/rotated `-444887525.5381651`이다. 모든 propagated native bound는 `value=null`, `UNDERFLOW_USE_LOG`와 finite log를 보존했다. 이는 정확한 finite-depth correction이 0이라는 주장이 아니다.

각 synthetic base의 gamma와 `1-gamma*delta`를 사용한 conditioned bounds는 모두 양의 허용 branch에 있다. tau=.3 및 2의 네 case에서는 state와 flux bound가 기록된 arithmetic allowance보다 크며, 관측 차이가 bound+allowance 안에 있다. 예를 들어 tau=.3 isotropic flux 차이는 `3.1795492947933235e-21`, analytic bound는 `3.1795492959271782e-21`, allowance는 `3.0907761267127058e-28`이다. 큰 departure-gross allowance는 별도 진단으로 남기고 통과 허용량에 사용하지 않았다.

**NUM01 — 비차단 해석 제한:** tau=30의 isotropic/triaxial state와 scalar-flux 차이는 binary64에서 0으로 관측되며 해당 bound보다 arithmetic allowance가 크다. Raw의 `bound_above_roundoff=false`가 이를 정확히 표시한다. 따라서 이 두 case를 analytic-bound 수준의 분해능 있는 측정이나 정확한 0의 증거로 설명하면 안 된다. Tensor bound는 별도로 평가된다. 추가 실행이나 tolerance 변경은 필요 없다.

## 5. 실제 PNG 검사

세 PNG를 `view_image`로 직접 열었다. 각 PNG의 해시와 원 plot-data 연결을 `FIGURE_INSPECTION.json`에 보존했다. PDF 파일의 해시는 확인했지만 PDF raster review는 **NOT_RUN**이다.

- **Source partition:** 다섯 native diagonal contribution, 강조된 direct Lyα, 대응하는 loss/incoming departure와 작은 net source가 읽힌다. Log 축·단위·라벨에 잘림이 없다. Saved state의 양의 magnitude를 모든 상태의 양의 gross microscopic rate로 확대하지 않는다.
- **Affine response:** r/r0=.5,1,2 세 track과 b/b0=.8–1.2 구간, population response와 signed source의 부호 전환이 명확하다. Frozen blocks의 algebraic response이며 cosmological trajectory가 아니다.
- **Angular ledger:** 위는 여섯 synthetic finite-opacity control, 아래는 실제 scalar state의 세 energy/PSTF injection이다. Zero ionic/electron yield의 direct bound-bound 범위가 제목에 명시돼 있다. Number 값은 ANGULAR_LEDGER.csv에 있으며 energy와 선언된 E21로 연결된다.

**VIS01 — 비차단 표시 사항:** angular ledger의 좌하단 legend가 rotated radiation bar의 위쪽 일부와 겹친다. 다른 두 bar와 원 data에서 동일한 높이와 energy exchange가 확인되고 과학적 해석을 막지 않는다. 차후 그림을 수정한다면 saved data로 legend만 bar 바깥에 옮기면 된다. 새 과학 실행은 필요 없다.

## 6. 판정, 제한과 다음 행동

**수용:** 한 preserved snapshot의 exclusive native affine line pair, source-conditioned Schur/rank-one solve, frozen residual/parameter JVP, 직접 bound-bound 장부와 선언된 native-compatible angular injection. 현재 두 code hash에 결속된 새 primary evidence와 독립 수학·정적 검토 및 actual PNG inspection을 근거로 한다.

**수용 범위 밖:** coupled outgoing/incoming history 설치, native runtime replacement, 전체 background/history Jacobian, global convergence, all-nuclide ionic/thermal/spectral/metric closure와 production deployment. Strong no-go 결과를 새로 주장하지 않는다.

이 단일 R6/C9 검토는 완료됐다. 부모는 요청된 stage publication·backup·DAG·handoff를 이어갈 수 있다. 새 review cycle이나 추가 probe를 요청하지 않는다. 원 primary의 `figure_review=PENDING_ACTUAL_PNG_INSPECTION`은 실행 당시 immutable 기록으로 보존하고, 그 뒤 완료된 상태는 이 보고서와 별도 figure receipt가 제공한다.

`Physical HOLD`; `REC_U5 HOLD_9_FAIL/HOLD_8_FAIL`; `CLOSED_HOLD_NOT_RESET`; `global_convergence NOT_RUN`; `production NOT_APPROVED`; `REI_activation=false`; 과거 REI first-fail raw historical local-only를 모두 유지한다.

---

# 이전 복구 체크포인트 기록 — 현재 완료 판정은 위 본문

아래의 “대기”, “아직” 등은 복구 및 실행 전 시점의 역사적 상태다. 새 primary와 실제 PNG의 현재 검토 상태는 위 본문과 FINDINGS.json을 따른다.

## 현재 판정과 복구 범위

**이 파일은 유실 전 검토 내용을 실제 도구 기록에서 복구한 보고서다. 이전 파일의 byte identity를 주장하지 않는다.** 유실 전에는 R6 수학·원전·구현 대조와 독립 off-grid 검사 6개가 완료됐고, 도구 stdout은 모두 통과를 보고했다. 그러나 부모의 primary 원증거와 실제 PNG를 아직 읽지 않았으므로 C9 전체 완료 선언은 당시에도 없었다.

현재 `PROBE_RAW.json`과 `STABLE_DRIVE_PROBE_RAW.json`의 전체 배열·Decimal80 reference 문자열·당시 구현 해시는 **유실됐으며 재생성하지 않았다**. 두 raw 파일의 숫자를 다시 계산해서 옛 원증거로 꾸미지 않는다. 이번 복구에서 과학 실행과 추가 probe는 모두 0이다. 사용한 여섯 probe의 예산은 그대로 소진된 상태다.

복구된 것은 두 probe script의 실제 tool-call 본문, 두 stdout의 실제 read-tool 반환문, 별도로 출력됐던 P3의 일부 수치와 counter, 실행 session의 exit-0 반환 기록이다. 첫 script는 9082 bytes이며 유실 전 `ls` 반환값 9082 bytes와 같다. 당시 script SHA256은 출력되지 않았으므로 이 사실만으로 원본 byte identity를 인증하지 않는다.

`native_line_owner.py`와 `run_line02.py`의 변경 전·후 SHA256은 당시 raw JSON에 썼지만 도구 출력에 노출하지 않았다. 따라서 **정확한 옛 구현 해시는 현재 알 수 없다**. 새로 복구한 구현에 옛 probe 결과를 byte-bound PASS로 붙이지 않는다. 향후 부모 primary 실행은 실제 복구 구현의 새 identity에 결속해야 한다.

## 살아 있는 실제 실행 기록

| 역사적 실행 | 보존된 도구 증거 | 상태 |
|---|---|---|
| 최초 P1–P4 | exec session 73909, exit receipt `9cf0d7`, stdout read `2e2875` | exit 0; stdout 전체 pass |
| stable-drive P5–P6 | exec session 21796, exit receipt `25ade5`, stdout read `67accb` | exit 0; stdout 전체 pass |
| P3 별도 읽기 | 선택한 bound/event/counter fields를 실제 반환한 도구 출력 | `RECOVERED_P3_PARTIAL_OUTPUT.json`에 부분 복구 |

두 stdout 파일의 숫자는 실제로 반환됐던 텍스트에서 옮겼다. `RECOVERED_EXECUTION_RECEIPTS.json`에는 이 구분과 새로 복구한 파일의 hash를 기록했다. 이 새 hash는 복구 파일의 identity이며 유실 전 원본 hash를 대체하지 않는다.

부모가 복구한 입력과 donor 여덟 파일을 단순 byte-hash로 읽어 확인했고 모두 이전 도구 출력에 있었던 원 pin과 일치했다. 여기에는 원 CSV, May-2012 `hydrogen.c/.h`, 원 loader·native·trajectory 코드, spike donor와 ANGULAR01 코드가 포함된다. 이는 복구 확인이며 새 probe 실행이 아니다. `skill_context_used/`의 실제 사용 버전 1.3.0 네 문서는 부모가 복구한 제공 경로에서 다시 복사했다. 유실 전 skill digest는 도구 출력에 없으므로 새 파일 해시와 구분한다.

## 유실 전 R6 검토에서 확인한 내용

독립 검토자는 이 unit의 구성에 참여하지 않았고 새 하위 reviewer를 만들지 않았다. 원 `hydrogen.c`, 원 CSV, 원 loader와 행렬 조립 코드, 계약·이론, 변경 구현을 직접 읽었다.

1. **독점 native pair.** `populateTS_2photon`은 real 2p diagonal에 `r0=LYA_FACT H/(nH x1s)`를 더하고, 같은 real source에 `r0 b0`, `b0=3 x1s Dfplus_Lya`를 넣는다. `M* = M + (r-r0) EEᵀ`, `s* = s + (r b-r0 b0) E`가 해당 두 항만 교체한다. Beta, mixing, two-photon/Raman, 2p↔virtual diffusion과 `Trv/Tvr/Tvv`, 다른 source, frozen incoming history는 남는다.

2. **행렬 방향.** Native `Tvr[i][b]`는 virtual 방정식의 real i 계수이므로 full matrix에 `Tvr.T`를 넣는다. `Tvv[1,b]=V[b,b-1]`, `Tvv[2,b]=V[b,b+1]`로부터 scipy band shift가 나온다. 옛 probe script는 CSV에서 full matrix/source를 직접 조립해 byte equality를 검사했고 stdout의 전체 pass는 이 조건도 포함했다. 전체 raw matrix는 유실됐다. 비대칭 virtual block 관찰은 당시 보고서와 원 코드 읽기에 남아 있다.

3. **Schur 및 rank-one 식.** `W=V⁻¹Tvrᵀ`, `u=V⁻¹sv`, `K=Trr-Trv W`, `j=sr-Trv u`에서 시작해 `v=K⁻¹e`, `eta=1+(r-r0)v_p`로 두면 `x*=x0+v[(r-r0)(b0-x0p)+r(b-b0)]/eta`, `z*=z0-W(x*-x0)`가 수정된 방정식을 만족한다. eta 양의 margin과 전체 행렬 condition number는 별개다. 저장 snapshot의 미세 잔차와 준비된 algebraic baseline도 구분한다.

4. **JVP 범위.** 임의 상태 residual derivative는 `M* dX + E[(X_p-b)dr-r db]`, solved derivative는 `(w/eta)[(b-X_p)dr+r db]`다. 다른 block과 TR·TM·x1s·nH·H 및 history를 고정한 partial derivative다. 전체 cosmic/history Jacobian을 제공하지 않는다.

5. **Angular bound.** Tracefree shear로 `<q>=1`이며 `epsilon=<q exp(-tau/q)> <= delta=exp(-tau/qmax)`다. `gamma>=0`, `gamma delta<1`에서 rank-one denominator를 포함한 state/flux bound가 나오고, `||PSTF(nn)||F=sqrt(2/3)`로 tensor bound가 나온다. 큰 tau의 floating underflow와 정확한 0은 다르며 log를 보존한다.

6. **물리 장부와 규약.** 한 signed bound-bound event의 `(dn2p,dn1s,dngamma)=nH(-J,J,J)`, `(duinternal,dugamma)=E nH(-J,J)`가 닫힌다. Ionic/electron yield 0은 이 event에만 적용된다. 전체 native xe는 excited population으로 간접 반응할 수 있다. Native Wien departure/ground-opacity 표현과 LINE01의 full Planck/stimulated source는 별개다. Native literal 계수와 현대 SI hc 재구성의 약 `-2.66165e-7` 차이는 roundoff로 숨길 수 없다.

## 실제 stdout에 남은 역사적 수치

| Probe | 반환된 관측 |
|---|---|
| P1: r/r0=.37, b/b0=-.0001; arbitrary-state mixed JVP | Real/virtual error `8.33983298694066e-15 / 8.570360575459755e-15`; backward `5.099791958037935e-16`; residual/solution JVP `3.170200145336864e-16 / 4.774777559581859e-15` |
| P2: r/r0=1.73, b/b0=1.0273; absorption | Real/virtual error `1.680490550051676e-14 / 1.708184365180355e-14`; backward `1.4916798937519385e-16`; residual/solution JVP `3.636703341719292e-15 / 4.133279312112923e-14` |
| P3: tau=1.7, rotated shear | Independent 4608-node rule과 C/D 차이 `8.881784197001252e-16 / 2.892565178889611e-15`; state/flux/tensor bound+allowance 조건 pass |
| P4: tau=1100, S=diag(-.5,.2,.3) | stdout pass; script 조건은 delta와 세 bound 모두 `UNDERFLOW_USE_LOG`, `value=None`, finite log |
| P5: tau=1.1, S=diag(-.27,.08,.19) | Stable flux의 Decimal80 direct2 비교 상대 차이 `2.945161863355711e-14 / 2.930654233381625e-14`; finite 차이 `2.0651563179386107e-21`, bound `2.6829105398353963e-21`, allowance `3.090775441980927e-28` |
| P6: r=2.37e8, b=1.031 b0 | 변경된 r-only solved JVP의 Decimal80 direct2 비교 scaled error `2.639411587952865e-15` |

초기 네 case의 stdout elapsed는 `0.11056711700803135 s`다. 추가 검사 elapsed 원값은 출력되지 않아 복구하지 않았다. 역사적 검토 수는 case 6, full313 real solve 2, complex solve 2, Decimal80 direct2 solve 3, rank query 8, preparation 2다. Primary 실행·native runtime·IVP·과거 campaign replay는 0이었다. 이 수는 새 계산 수가 아니다.

## OBS01의 역사적 해결과 현재 증거 한계

초기 P3의 flux analytic bound는 `2.8601212560731456e-21`인데 rounded-state subtraction을 위한 allowance는 `2.059246244310254e-19`였다. 그래서 numerical pass를 bound 수준의 분해능 있는 측정으로 읽으면 안 된다고 기록했다.

이후 구성자는 `D*=[D0-(1-gamma0)(b-b0)]/eta`와 `1-gamma_base=(1-gamma0)/eta`를 적용했다. 검토자는 두 동치식을 직접 확인하고 P5/P6의 새 입력에서 변경된 경로를 표적 대조했다. P5의 arithmetic allowance가 analytic bound보다 충분히 작아져 당시 OBS01은 해당 경로에서 해결됐다고 판정했다. 현재는 그 실제 stdout과 script가 남아 있고 전체 Decimal80 원문과 구현 해시가 유실된 상태다. 이 증거 수준을 넘는 재현성 주장은 보류한다.

## 남은 동일-pass C9 작업

부모가 복구 구현으로 처음 수행할 primary 결과의 실제 code hash·counts·실패 raw·수치 결과를 읽고, 실제 PNG 세 장을 연다. 이 작업은 아직 수행되지 않았으며 다음 부모 요청에서 같은 pass로 이어간다. 새 reviewer, 추가 off-grid probe, 기존 여섯 probe 재실행을 하지 않는다.

복구 자료의 결손은 **역사적 관측의 전체 원증거·코드 결속 한계**다. 올바르게 새 identity를 붙인 bounded primary 실행 자체를 막는 이유는 아니다. 수학·원전 검토와 실제 도구 출력의 역사적 관측을 유지하되, 새 구현에서 이미 검증됐다고 선판정하지 않는다.

## 보호 상태

`Physical HOLD`; `REC_U5 HOLD_9_FAIL/HOLD_8_FAIL`; `CLOSED_HOLD_NOT_RESET`; `global_convergence NOT_RUN`; `production NOT_APPROVED`; `REI_activation=false`를 유지한다. 과거 REI first-fail raw는 historical local-only다. Full history 및 all-nuclide ionic/thermal/spectral/metric closure는 이 local adapter의 검토로 완료되지 않는다.

## 복구 구현의 정적 연결 — 같은 pass의 계속

현재 재구성된 `code/native_line_owner.py` 380줄을 실제로 읽어 위 수식과 연결했다. 현재 SHA256은 `96dbf48afa3a85e6a6d7f5a4affd03dec64f3647cbc6603fe7a55a51895d6197`이며 이 파일의 실제 bytes를 `rebuilt_code_snapshot/native_line_owner.py`에 보존했다. 독점 pair, Tvr 전치와 band 방향, Schur/rank-one 식, 두 JVP, stable drive, channel ledger와 bound/log 표현이 검토한 수학에 맞다. AST segment hash를 원 recipe와 추가 대조하는 경로도 확인했다. `r0` 산술은 `LYA_FACT*H/(nH*x1s)`로 쓰였으며 원 `LYA_FACT*H/nH/x1s`와의 binary64 연산 순서 차이는 새 primary source-decimal 검증에서 실제로 판단할 항목이다. 이름·출력 key가 바뀐 새 구현이므로 보존한 역사적 probe scripts의 실행 호환성이나 원 byte identity를 주장하지 않는다.

이 정적 확인에서 새 material defect는 발견하지 않았다. `run_line02.py`와 처음 실행될 primary 원증거·실제 PNG는 아직 미검토이며 수치 PASS를 선판정하지 않는다. 추가 probe는 0이다.

### 재구성 runner의 정적 확인

`code/run_line02.py` 604줄, 32,677 bytes, SHA256 `630261cd84ed3b5e58c2a5fd2b4792edbcab603b8781fa5fa718cfe2a5bb9e53`를 실제로 읽었다. 동결된 owner7/JVP12/angular9/bound용 rank12/invalid12/mutation2/plot183 범위와 full313·directSchur·complex313 reference, 70자리 source-decimal 기준, 물리 positivity, paired-owner mutation, counts 및 immutable attempt/failure capture가 연결된다. 수용 tolerance를 느슨하게 하지 않았고, saved-state angular event와 solved-state bound를 구분한다. `prior_review_inherited_as_test=false`로 옛 probe를 새 numerical acceptance에서 제외한다. 현재 추가 material defect를 찾지 않았다. 이 결과는 정적 확인이며 primary 결과나 PNG를 읽은 것으로 표시하지 않는다.
