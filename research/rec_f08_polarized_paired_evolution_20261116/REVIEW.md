# 독립 검토: 원본 F08의 지속 편광–HHe point evolution

검토일: 2026-11-16
검토자: 별도 agent `/root/thomson_theory`
결과: **SCOPED_RAW_ARRAY_REVIEW_PASS — 조건부 계산 결과의 독립 검증**
Production: **HOLD**. 원본 owner admission 및 canonical DAG 진전은 주장하지 않는다.

## 무엇을 독립적으로 확인했는가

원격 원자료의 다섯 실행을 직접 읽었다. 파일 위치는
`/home/cosmosapjw/research_runs/rec_f08_polarized_paired_evolution_20261116/results`
이다. 각 실행의 `stokes_history.npz`, `trajectory.csv`,
`RESULT.json`, 첫/마지막 native witness JSON 및 stderr에 대해
SHA256과 byte count를 새로 계산했다. 모든 identity와 상세 수치는
`INDEPENDENT_REVIEW.json`에 있다.

다섯 실행의 총 960 macro stages, 2,088,960 spectral/angular Stokes rows를
검사했다. Producer Python 모듈은 import하지 않았다. 검토 프로그램은 NumPy와
표준 라이브러리만 사용했고, 원격 파일을 변경하지 않았다. 이번 검토는 완성된
IVP를 다시 실행한 것이 아니라 원자료의 보존량·양성성·clock·관측량을
독립 재계산하고 선택된 실제 endpoint를 다른 구현으로 재현한 것이다.

구현의 독립성은 다음 세 곳에서 확보했다.

1. 각 case의 첫/마지막 macro step, 총 20 accepted native half endpoints를
   다시 계산했다. Producer의 bracketing shortcut 대신 원본의 **모든 hat를
   직접 평가**했고, 원래 scalar binary64 redshift/Jacobian 계산 순서를
   별도로 구현했다.
2. 편광 screen connection은 producer GL4 대신 **GL8** 적분으로 계산했다.
3. Collision은 producer의 닫힌 3×3 moment 지수해 대신 **128×128 방향쌍의
   explicit Jones/Mueller kernel과 Poisson 급수**를 사용했다. 실제 최대
   \(\tau=1.28411\times10^{-9}\)에서 3개 scattering 항 뒤의 Poisson tail weight는
   \(1.133\times10^{-37}\) 이하이다. 물리 quadrature는 알려진 moment 조건을
   독립 SVD least-squares 풀이로 재구성했다.

검토 스크립트 전체가 JSON의 `independent_audit_python_source`
필드에 포함되어 있어 같은 원자료에서 재실행할 수 있다. 최초 검토 시도의
NumPy boolean JSON 직렬화 오류와 수정도 실행 이력에 보존했다. 이 오류는
검토 결과의 출력 단계에서 발생했고 원래 simulation이나 원자료를 변경하지 않았다.

## 실제 결과

아래 값은 보고서의 수치를 채택한 것이 아니라 raw Stokes arrays에서 다시
계산한 마지막 물리 tetrad sky의 값이다. 모든 실행의 최종 proper time은
\(10^{11}\,\mathrm{s}\)다.

| 실행 | Steps | \(\Delta t\) (s) | 최대 선형편광 비율 \(P/I\) | \(\sum_i P_i/\sum_i I_i\) |
|---|---:|---:|---:|---:|
| BI native control, \(\sigma_T=0\) | 160 | 625000000 | 0 | 0 |
| BI Thomson, degree 4 | 160 | 625000000 | \(5.335899157888835\times10^{-13}\) | \(3.5884283591969985\times10^{-13}\) |
| BI Thomson, degree 6 | 160 | 625000000 | \(5.335922701949413\times10^{-13}\) | \(3.5884286286698006\times10^{-13}\) |
| BI Thomson, degree 4 | 320 | 312500000 | \(5.314446457628724\times10^{-13}\) | \(3.574000518548488\times10^{-13}\) |
| FLRW Thomson, degree 4 | 160 | 625000000 | \(7.374611003217392\times10^{-23}\) | \(3.758492202008377\times10^{-23}\) |

모든 maximum \(P/I\) 재계산값은 해당 `RESULT.json` 값과
표시된 binary64 수준에서 같았다. Sigma-zero control의 모든 저장된 \(Q,U,V\)는
정확히 0이다. 모든 case의 circular polarization도 0이다. FLRW의 남는 선형편광은
위에 명시한 절대 크기의 수치적 null이다.

### 보존, 양성성, clock

- 모든 raw arrays는 유한하며, spectral·guard intensity는 음수가 없다.
- 개별 Stokes cone과 guard의 공동 moment 필요조건
  \(0\preceq S_U\preceq(10\,\mathrm{eV})S_N\)에서 양의 위반량은 0이었다.
- 전체 raw photon number와 native inventory의 최대 상대 차이는
  \(4.2162699418252194\times10^{-16}\)였다.
- 전체 raw energy와 native inventory의 최대 상대 차이는
  \(3.8076125248535353\times10^{-16}\)였다.
- CSV gas fractions, \(n_{H,0}=10^{-4}\,\mathrm{cm}^{-3}\),
  \(f_{\rm He}=0.083\), 각 case의 실제 \(H_i\), proper time으로 \(n_e\)를 다시
  계산했다. 저장된 \(n_e\) 및 endpoint
  \(\tau=c\sigma_T n_e\Delta t\)와의 차이는 모두 0이었다.
- 시간 배열은 \(k\Delta t\)와 정확히 같았다. 160/320 실행은 prefix 길이
  비교가 아니라 같은 최종 proper time의 refinement다.
- 첫/마지막 witness의 모든 spectral-group photon total은 collision 전후
  동일한 부동소수점 summation 허용범위 안에 있다. 관측된 최대 상대 차이는
  \(1.2698577848676436\times10^{-15}\)였다.

이는 필요한 범위의 직접 계산 결과다. 보존 장부가 point evolution의 보존성을
보여준다는 사실과 cumulative interval enclosure가 있다는 주장은 구별된다.

### 실제 feedback와 지속 편광

저장된 이전 post-collision state에서 마지막 두 native half endpoints를
재구성하고, endpoint gas의 동일 \(\tau\)로 독립 Mueller collision을 적용했다.

- 다섯 case의 첫/마지막 native half-step **intensity replay parity는 모두
  정확히 0**이었다. 전체 CSV 960개 단계의 producer parity 기록도 모두 0이다.
  독립 replay가 직접 검증한 범위는 이 중 10 macro steps/20 half endpoints다.
- BI 마지막 단계의 독립 collision \(Q/U\) 재계산과 저장값의 상대 \(L^2\)
  차이는 degree4/160에서 \(5.150638775836478\times10^{-15}\),
  degree6/160에서 \(9.920193078185587\times10^{-15}\),
  degree4/320에서 \(3.702167954654361\times10^{-15}\)였다.
- 마지막 step에 들어오는 \(Q/U/V\)만 0으로 바꾼 독립 대비 계산에서,
  이전 상태의 편광이 마지막 \(Q/U\) signal에 기여하는 norm 비율은
  degree4/160에서 \(0.987525228988001\),
  degree4/320에서 \(0.993743096453198\)이었다.

따라서 이 원자료는 매 tick 새로 만든 정적 source와 달리, 이전 편광을 실제로
수송하고 재산란한 결과를 담고 있다. \(I\)도 다음 원본 native trial에 들어간다.
이 결론은 scalar audit만 보고 추정한 것이 아니라 이전 저장 상태에서 실제
endpoint witness를 재현해 확인했다.

FLRW 첫 step에서는 독립 알고리즘 사이의 \(Q/U\) 차이가 절대
\(L^2=1.2493951940366065\times10^{-27}\), 상대 약 \(0.0348770550\)였다.
분모 자체가 numerical null인 이 값을 숨기거나 3% PASS로 바꾸지 않았다.
FLRW null은 위의 절대 편광 크기로 보고하며, BI의 유한 signal을 비교하는
method test와 구분한다. 기존 tick142의 3% quadrupole FAIL은 별도로 그대로 남는다.

## 동일 관측량의 method 및 time-step 비교

기준은 BI degree4/160이다. Physical-sky norm은 동일한 마지막 physical tetrad와
동일 degree4 observable estimator에 투영한 \(Q,U\)의 \(L^2\) norm이다.
Raw spectral norm은 energy와 direction을 모두 유지한다.

| 비교 | Physical-sky \(Q/U\) 상대 \(L^2\) 차이 | Raw spectral \(Q/U\) 상대 \(L^2\) 차이 |
|---|---:|---:|
| degree4/160 대 degree6/160 | \(2.008959200405911\times10^{-5}\) | \(4.453288116013549\times10^{-5}\) |
| degree4/160 대 degree4/320 | \(0.004054309946397159\) | \(0.0038994737733736335\) |

두 physical-sky 비교 모두 유지된 0.03 기준 이내다. 이 결과는 아래 범위에서
해석한다.

- Degree4/6 비교는 **같은 원본 q128**의 moment integration 방식 차이다.
  각도 node 수를 늘린 continuum convergence 검사는 아니다.
- 160/320 비교는 한 번의 time-step refinement다. 전체 방법은 Lie split이며,
  이 두 결과만으로 asymptotic order나 zero-step limit을 입증하지 않는다.
- 160/320의 마지막 gas 차이는
  \(|\Delta x_{\rm HII}|=1.4761871852675412\times10^{-6}\),
  \(|\Delta x_{\rm HeII}|=4.6521780872055274\times10^{-10}\),
  \(|\Delta x_{\rm HeIII}|=3.251987568120285\times10^{-11}\),
  \(|\Delta T|=0.03633134275878547\,\mathrm K\)다.
- Degree4/6 마지막 gas values는 이 실행의 저장 정밀도에서 동일했다.

## 유지되는 물리적 실패와 결론의 범위

가장 중요한 미해결 원본 문제는 **fixed-hat spectral support**다.
마지막 원자료에서 earliest-characteristic energy floor 아래에 놓인
photon fraction은 다음과 같다.

| 실행 | 금지된 support 아래의 마지막 photon fraction |
|---|---:|
| BI native control/160 | 0.41992037975020663 |
| BI degree4/160 | 0.4199203797503487 |
| BI degree6/160 | 0.41992037975034857 |
| BI degree4/320 | 0.41978913410031254 |
| FLRW degree4/160 | 0.4199226855533565 |

이 표는 NPZ의 마지막 spectrum과 guard에서 직접 다시 계산했다. 기준 floor는
BI에서 `13.686169985333072 eV`, FLRW에서 `13.686306847717237 eV`이며,
CSV에 보고된 fraction과의 차이는 최대 `1.6653345369377348e-16`이었다.
이 약 **41.99%**의 support 위반은 scattering을 끈 control에도 존재한다.
보존량 검사나 작은 degree4/6 차이로 이 원본 spectral defect를 해소했다고
판정하지 않는다. 이번 편광·gas 궤적은 이 fixed-hat 원본에 대한 조건부
수치 결과이며, physical spectral-support gate를 통과한 IGM 예측으로 채택되지 않는다.

또한 다음 상태를 보존한다.

- 원본 `S0_BI_ORIGINAL_HAT`, tick142,
  `PHOTON_NUMBER_QUADRUPOLE`의 상대 method disagreement
  \(0.04152277708926094>0.03\): **FAIL_RETAINED**.
- Native/physical 왕복 normalizer가 만드는 비선형 collocation closure:
  조건부이며 정확한 선형 continuum Thomson map으로 승격하지 않는다.
- Photon/guard intervals의 point 재설정:
  discarded widths를 포함한 누적 coupled interval 인증은 없다.
- Guard \(N/U\)의 joint PSD 검사를 통과했으나 energy-resolved polarized
  guard spectrum을 재구성한 결과는 아니다.
- Original owner admission: 주장하지 않음.
- Canonical DAG delta: **0**.
- Production: **HOLD**.

이번 독립 검토가 수용하는 성과는 원본 F08 photon–HHe clock과 데이터에 연결된
지속 편광 충돌 진화, 그 실제 원자료의 보존·양성성·null control 및 제한된
method/refinement 검증이다. 원본 실패와 외부 수용 상태는 그 성과와 함께 남는다.
