# REC-PB02 독립 검토

판정은 **confirmed — 선언된 one-temperature 점별 REC reference 구현과 조건부 angular Sobolev 연구 범위**다. 열린 blocking finding은 없다. 실제 REI 소비자 결속, 재결합 궤적, 일반 Bianchi radiation closure, 엄밀 구간 오차 인증은 이번 판정에 포함되지 않는다.

검토자는 구현·이론 원고를 직접 수정하지 않았다. 고정 HYREC-2 저자 소스의 `rec_TLA_dxHIIdlna`를 별도로 읽고, 새 Rust API·시험·실행 로그와 연구 설계를 검토했다. 추가로 원 C 함수와 Rust 공개 CLI를 세 개의 비평형 입력에서 직접 호출했다. 이전 게시 과학 suite를 검토자가 재실행하지 않았다. 검토 대상 28개 파일의 SHA-256은 `REVIEW.json`에 고정되어 있다.

## 수정하여 닫힌 finding

**IR-01: collapsed Saha와 유한 retained-shell 평형의 구분.** 최초 이론 문서의 한 온도 평형 서술은 유한 (x_2)를 보존하는 모형에도 일반적으로 적용되는 것처럼 읽혔다. (B=\exp[-E_{21}/(k_BT)]), (S=\Phi\exp[-\chi_1/(k_BT)]/n_H)일 때

\[
\frac{x_p^2}{1-x_p}=S
\]

는 (x_2\)를 핵수 보존에서 무시한 collapsed closure의 식이다. 유한 모형에서는 (x_2=4Bx_1), (x_1+x_2+x_p=1)을 동시에 써서

\[
\frac{x_p^2}{1-x_p}=\frac{S}{1+4B}
\]

를 얻는다. 수정된 이론·machine-readable 계약에 두 식이 명시되어 있으며, 실제 rate residual은 (S_{\rm rate}=\beta_PB/(n_H\alpha_B))를 사용한다. 새 Rust 시험은 synthetic (B=0.2)에서 세 retained RHS가 모두 0인 동시에 collapsed RHS는 0이 아님을 확인한다. 단순한 문구 수정 이상의 반례 검사가 있으므로 finding을 닫았다.

## 물리·수학 검토

- HYREC-2 pin `09e8243d0e08edd3603a94dfbc445ae06cafe139`의 원 함수와 비교해 (\alpha_B(T_m)), (\beta_P\propto\alpha_B(T_r)), shell 광이온화 (\beta_P/4), per-2p 탈출률의 shell 가중치 (3/4)가 일치한다. native source 함수는 명시적으로 (T_m=T_r)만 받으므로 two-temperature 유도를 native 실행 증거로 승격하지 않는다.
- proper SI density와 coefficient의 곱은 s(^{-1})이며, cgs↔SI 변환은 한 번만 수행한다. (dx/dz=-\dot x/[(1+z)H]) 부호가 맞다. source-rounded 상수와 별도 SI 상수 입력은 다른 profile로 유지된다.
- retained RHS의 사건별 핵수 보존과 charge (x_e=x_p)는 맞다. binding-energy identity는 열·광자 spectrum을 계산했다는 뜻이 아니다. prescribed bath의 reservoir 교환까지 포함한 총에너지 보존은 미주장이다.
- `frozen_escape_qss`는 고정 (R_\alpha)에 대해서만 finite-shell QSS를 푼다. 실제 (R_\alpha\propto1/x_1)를 상태 변화 때마다 재조립하는 nonlinear root와 구별된다. `closure_defect`는 같은 순간 (C)를 쓰는 정확한 항등식이며, (C)까지 collapsed source로 재계산한 완전한 두 모형 차이는 추가 항이 필요하다. README가 이 제한을 정확히 명시한다.
- (p(h)=h[1-e^{-a_S/h}]/a_S)에 대해 (p''(h)=-a_Se^{-a_S/h}/h^3<0)이므로 Jensen 부호가 맞다. (\langle h\rangle=H)와 (\langle(\sigma_{ij}n^in^j)^2\rangle=2\sigma_{ij}\sigma^{ij}/15)에서 제시한 2차 계수와 generic 3차 remainder를 얻는다. 모든 방향에서 양의 팽창, 등방 population/source, 국소 정상 Sobolev 가정이 필요하다.
- uniformly thick 극한의 직접 shear 상쇄 및 상대 잔차 (\le e^{-\tau_{\min}})는 제한된 모형 안에서 맞다. 고정 (H,n_1) 조건이므로 배경 팽창의 shear dependence까지 없앤다는 뜻은 아니다. finite-τ 그림을 실제 우주론 재결합 신호 크기로 해석해서는 안 된다.
- 시간 의존 QSS defect bound는 입력 변화율과 양의 이완률 bound를 **가정한 조건부 유도**다. 이 bound의 실제 interval 상수는 아직 계산되지 않았다.

## 실행 증거와 독립성

| 증거 | 검토 결과 | 해석 |
|---|---|---|
| 새 Rust targeted tests | 20 PASS, exit 0 | 잘못된 factor-4/factor-3 대조, finite partition, 보존, domain, redshift, source fixture |
| 전체 crate 통합 로그 | 108 PASS, exit 0 | 기존 88개와 새 20개; 새로운 물리 궤적 검증 횟수로 세지 않음 |
| pinned author C 대 native Rust | 384점 PASS | 실제 원 `rec_TLA_dxHIIdlna` 호출; coefficient 최대 상대차 (1.80\times10^{-14}), RHS gross-flux 정규화 차 (1.06\times10^{-14}), 사전 기준 (2\times10^{-12}) |
| 독립 Decimal event oracle | 70자리, 24점 PASS | 네 사건의 stoichiometric column으로 세 RHS·보존·closure defect를 계산 |
| 검토자 별도 source spot check | 3점, 15성분 PASS | 실제 C/Rust CLI 직접 호출; 최대 상대차 (4.21\times10^{-15}) |
| angular 수치 연구 | 42점, 95검사 PASS | 32→64 quadrature 최대 차 (3.34\times10^{-16}); Jensen·M4·약한 shear 계수 |

finite point 회귀검사와 독립 원 함수 실행은 완료되었으나 continuous domain의 uniform proof는 아니다. 한 온도 Saha 영점만으로 (C)-factor를 검증할 수 없으므로 원 함수 계수 대조와 의도적 factor 오류 검사가 별도로 있는 것이 적절하다. 여섯 축 quadrature는 M2가 맞더라도 M4에서 (5/2) 배의 작은-shear 오차 계수를 만들 수 있다는 수치 반례가 적절하다.

고정 부모 crate의 `lib.rs`를 제외한 기존 10개 파일은 byte-identical임을 검토자가 확인했다. 기존 He/frame/screen source와 admission flag는 이 변경으로 바뀌지 않는다. native 공개 API와 CLI 호출은 실제 실행되었지만 REI production call site 연결은 아직 없다.

원 upstream C/header는 `/tmp/rec_theory_source_cache`에 있으며 배포 패킷 밖이다. source pin·hash와 독립 작성 caller, 문헌 수식의 별도 구현만 게시한다는 정책이 명시되어 있다. 공개 열람 가능성과 조건 없는 재배포 허가를 혼동하지 않았다. 추가 replay helper는 고정 다섯 파일의 크기·SHA-256을 확인한 뒤 외부 cache에서 GNU11로 빌드하며, offline build exit 0 증거를 검토했다.

## 환경 문제와 종료

원 C의 최초 `-std=c11` 빌드는 `M_PI` 부재로 실패했고, 원 소스 변경 없이 `gnu11`로 복구했다. Rust formatter는 도구 부재로 미실행이다. 검토자의 선택적 SymPy 자동 검산은 두 기존 Python runtime 모두 dependency 부재로 실행하지 못했으며 `OPTIONAL_CAS_ATTEMPT.json`에 남겼다. CAS PASS는 주장하지 않고, 직접 대수 검토와 별도 native/original-C 실행을 판정 근거로 썼다. 실제 고정밀 oracle는 mpmath가 아니라 표준 라이브러리 Decimal이다.

이 범위의 독립 검토는 종료한다. 추가 반복 감사 없이 exact reviewed payload를 게시할 수 있다. 후속 과제는 실제 REI adapter 결속과 matched scalar history이며, 기존 Case-A authority나 historical failure를 새 pointwise PASS로 소급 변경해서는 안 된다. 앞으로의 원격 commit/ref 및 백업 ACK 확인은 게시 담당 단계의 증거로 별도 기록한다.
