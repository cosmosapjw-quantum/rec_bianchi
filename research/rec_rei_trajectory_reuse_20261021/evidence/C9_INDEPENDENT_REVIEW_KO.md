# C9 독립 PHYS–MATH–CODE 검토

**판정: `PASS_SCOPED_INDEPENDENT_PHYS_MATH_CODE_REVIEW`. 미해결 차단 결함 0.**

검토자는 `/root/theory_literature`이며 reducer 구현자는 `/root`이다. 검토자는 reducer를 수정하지 않고 독립 테스트 8개와 저장 결과 감사 스크립트를 작성했다. 최종 검토 대상은 `code/reduce_trajectories.py` SHA256 `03596192ccd5602187549fb52734870b343aea6e1ca7f13d0df8d7e7b7c1c77a`, 테스트 SHA256 `639abdff416becf8978fc0f013c211d8a1bf1fb6fd2346a1da526e643f2b44d7`이다.

## 검토 범위

Collisionless finite-L8 source `3b85dedce84d37b3e165da00685a8a984950aafe`의 기존 175개 궤적을 사용한다. 63개 축 support로 112개 mixed history의 153 저장 epoch, z20→2를 비교한다. 초기 shear는 양의 orientation과 0만 포함한다. 공통 비교 좌표는 x=ln(a/a_ref) 또는 적색편이이고, 각 case의 elapsed proper time은 다르다. 새 ODE, NCP 작업, benchmark는 모두 0이다.

원자료의 부호 있는 성분은 S_F=sqrt(6)s/H, P_m=sqrt(6)κ_t p_m/H², P_r=sqrt(6)κ_t p_r/H²이며 κ_t=8πG/c²이다. 공통 normal orthonormal frame에서 σ=diag(-s,-s,2s), π_A=diag(-p_A,-p_A,2p_A)를 사용한다. Full Frobenius norm은 각 signed coordinate의 절댓값이고 half-contraction norm은 1/sqrt(2)배다. Radiation p_r는 gamma와 nu의 signed 합이다.

## 발견과 수정

첫 검토에서는 float cast 전에 complex 입력을 거부하고 raw clock/state와 각 관측 배열의 shape·finite·a,H 양수 조건을 명시해야 한다고 지적했다. 구현자가 해당 검사를 추가했다. 이 첫 발견에는 수정 전 실패 실행을 따로 주장하지 않는다.

후속 검토에서는 `Pi_matter_J_m3=NaN` 또는 `Sigma_F=NaN`일 때 normalization 비교의 NaN 때문에 예외가 발생하지 않는 구체적인 경계 결함을 재현했다. 중간 reducer SHA `15cc18c373d50d00a6cf27778616ffd981372259b9fe573d1fbcc45ba6913060`에서 **2개 subtest가 실제 실패**했다. 원문은 `C9_REMAINING_NAN_RED.json`에 보존했다. 최종 reducer의 134–139행은 `P_total`, `Sigma_F`, 세 SI stress 성분을 포함하여 모든 사용 scalar history를 real·finite·shape 검사에 넣는다. 수정 후 독립 실행은 **8개 테스트 PASS, exit 0**이며 원문은 `C9_FINAL_TESTS_GREEN.json`에 있다.

이 결함은 malformed 입력의 거부 경로에 관한 것이다. 선택된 실제 175개 입력의 관련 필드는 모두 유한 실수였고, 원래 결과와 두 차례 보강 후의 결과가 동일함을 별도로 확인했다.

## 구현 검토

- 68–74행: nominal m=0 또는 r=0인 support만 lookup에 복사한다. Mixed 관측값을 크게 교란해도 prediction이 정확히 동일한 테스트가 통과했다. Support는 x+y−y의 불필요한 반올림을 피하도록 원값을 정확히 재사용한다.
- 151행: raw s/H에서 signed shear를 구성한다. 저장 Sigma_F의 norm으로 예측한 뒤 부호를 붙이지 않는다. 부호 전환을 포함한 독립 fixture가 통과했다.
- 196–204행: matter/radiation signed 성분을 먼저 합하고 norm을 취한다. 초기 상쇄 fixture, reverse triangle 검산, 실제 saved-total 대조가 통과했다.
- 81–129행: source/manifest/raw identity와 완료 receipt, closure/resolution 일관성을 확인한다. 원본 raw 및 완료 계산은 수정하거나 재실행하지 않는다.
- 144–149행: 공통 x,a 배열을 요구한다. 서로 다른 elapsed proper clock은 허용·보존하며 동일 proper time으로 해석하지 않는다.
- 181–191행: 통계는 112 mixed cases에서 계산한다. Support의 자기재현을 별도 검증 성공으로 세지 않는다. Ratio는 전체 signal peak를 분모로 하며 순간 상대오차로 표시하지 않는다.

## 독립 저장 결과 대조

`audit_trajectory_results.py`는 reducer를 import하지 않는다. 175개 source raw를 모두 읽어 signed projection을 독립 계산하고, Python scalar 연산으로 모든 case·epoch·component의 축 재구성을 다시 계산했다.

| 대조 항목 | 결과 |
|---|---:|
| Raw에서 만든 actual projection과 저장 actual의 최대 차이 | 0 |
| 독립 scalar prediction과 저장 prediction의 최대 차이 | 0 |
| Support 63개 원값의 정확 재사용 | PASS |
| 실제 사용 source 배열의 real·finite 검사 | PASS |
| Saved Sigma_F와 abs(sqrt(6)s/H)의 최대 차이 | 4.163336342344337e-17 |
| Original·intermediate·final의 9개 NPZ 배열 및 SUMMARY | 모두 동일 |

최종 NPZ SHA256은 `239595a3313a68e0125ec7b333b8d515c3fd5d6d8ec115fbef2496d3b18428b9`이다. 독립 대조 파일과 최종 결과의 전체 NPZ bytes도 동일하다.

| Signed 채널 | 153 epoch 최대 절대차 | 최대 위치 z | z2 최대 절대차 |
|---|---:|---:|---:|
| Shear | 9.40056251721652e-9 | 4.2449938184 | 8.122634823700282e-9 |
| Matter | 8.582762394605706e-9 | 9.1251369352 | 2.130153339290858e-9 |
| Radiation | 1.1057774095034681e-8 | 6.6903267282 | 6.540939782319864e-9 |
| Total | 1.9152545950075223e-8 | 7.8770715530 | 8.671093121602252e-9 |

끝점보다 큰 잔차가 중간 시점에 존재한다. 따라서 이번 궤적 비교는 끝점 비교에서 보이지 않던 시간 의존 정보를 제공한다. 이 숫자는 특정 저장 표본의 차이이고 ODE 참해 오차나 continuum 최대가 아니다.

## 수학적 의미와 유지되는 한계

고정 x와 초기 shear에서 exact finite-model parameter response가 C²라고 조건부로 가정하면, 축 재구성 잔차는 R=∫₀ᵐ∫₀ʳ F_mr(u,v)dvdu이다. 직접 FTC 유도와 Wolfram 보조 검산은 `TRAJECTORY_THEORY.md`와 `TRAJECTORY_CAS.json`에 있다. 저장값에는 solver·roundoff·initial calibration-realization 오차가 있으므로 R_saved=R_exact+e11−e10−e01+e00이다. Uniform mixed derivative bound 또는 ODE error bound를 얻은 것이 아니다.

Norm에는 정확한 reverse-triangle 관계가 적용된다. 특히 total norm 차이는 |R_m+R_r| 이하이며 다시 |R_m|+|R_r| 이하이다. 이 관계는 signed 저장 잔차로부터 norm 차이를 제한한다. 참해의 수치 오차 인증으로 바꾸어 쓰지 않는다.

새 C9 독립 검토는 이 reducer와 고정 입력 snapshot에만 적용된다. 역사적 PR116의 `C6_independent_code_review=NOT_RUN_TOOL_NOT_EXPOSED`를 소급 변경하지 않는다. 그림의 직접 시각 검토는 별도 PLOT_REVIEW에 기록되어 있고, 이 문서는 그림 작성자의 시각 검토를 독립 검토로 재명명하지 않는다.

**Physical HOLD, global convergence NOT_RUN, production NOT_APPROVED, 원래 REC U5 HOLD_9_FAIL/HOLD_8_FAIL 및 CLOSED_HOLD_NOT_RESET, REC REI_activation=false를 유지한다.**
