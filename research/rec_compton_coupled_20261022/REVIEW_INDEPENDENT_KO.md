# Compton 결합 유한 pilot의 독립 검토

검토자: `compton_independent_review` · 2026-10-22

## 1. 판정과 범위

**동결된 full63 Compton pilot 8개, 그 저장 경로의 분석, `figures/v2`의 수치 자료와 PNG 표현에 대해 `PASS_SCOPED`로 판정한다. 현재 범위의 미해결 blocker는 없다.** 이 판정은 실제 완료된 두 seed × 두 독점적 복사 가지 × nominal/refined 조합에 한정된다. 물리적 상태는 `HOLD`, production은 `NOT_APPROVED`, global convergence는 `NOT_RUN`, `REI_activation=false`를 유지한다.

검토자는 Compton adapter·저자 시험·driver·두 analyzer·충돌 provider·이론·plotter를 작성하지 않았다. 작성한 것은 `evidence/independent_review/`의 검토용 계산과 영수증, 이 문서뿐이다. 독립 검토 중 새 ODE·과거 IVP·기존 전체 시험·renderer·archive restore를 실행하지 않았고 Git·원격 서비스를 변경하지 않았다. 아래의 새 계산은 저장 상태에서의 유한 차분·대수·배열·적분 재구성과 파일 식별 확인이다. `physmath-research-loop` 1.0.0 / approval 0.2를 적용했다.

단계별 판단은 [동결 실행 전 검토](evidence/independent_review/PREFLIGHT_REVIEW.json), [분석 실행 전 검토](evidence/independent_review/ANALYSIS_PREFLIGHT_REVIEW.json), [완료 결과 검토](evidence/independent_review/RESULTS_REVIEW.json), [v2 그림 검토](evidence/independent_review/FIGURE_V2_REVIEW.json)에 따로 보존했다. 초기 두 preflight 영수증을 결과 판정으로 덮어쓰지 않았다.

## 2. 검토 대상의 식별

| 대상 | 식별자 / SHA-256 |
|---|---|
| 동결 runtime | `c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac` |
| 분석 identity | `f824bdead1ce75b94f5102764184ea8dee2db71ecc06296dc7fa2ac9d71708c3` |
| `compton_system.py` | `1035690890e2665769e1692e81d49d4209366291b1c8f2345f973818678f9ae9` |
| `run_compton.py` | `e81220564d303467c08b1162dcd9bea8a365c8d689c64b00aeaac7378e0511b9` |
| 수정된 `analyze_compton.py` | `00b187504eaa9da8cbe43287339b4b71b276936dff9e7542b3f29d5405147ffc` |
| `analyze_collisions.py` | `acd7a1ed448d282cc4b102ecfd6d2043611caa3dfa480913e105c073ba0969a1` |
| `THEORY_KO.md` | `8d4b29518a69c7d60898e90df8833d9b0409e2c61e2afef68c95545d3b304cd3` |
| 분석 `RESULT.json` | `ed78cc97e045077666b869d818e3b0ea550b73848bd58051d99bc515c094082e` |
| 분석 `SUMMARY.json` | `c04267f78b3c328b7e786dd2bbe818c19583bf8585c127c92147ab090374e502` |
| v2 plotter | `1d80ee4c88fa78eb42f7f534c23101eaf72715f9a49ed09b14c316465ad6b039` |
| v2 figure manifest | `5ec6dd33045f194c195cce04b38b3a08bcab0012c3191b783c7597a0719a066e` |

상속된 열 source와 omitted-budget source의 identity는 각각 `dfd2ca42b7fb768f3e31e5a7cc3ab64a4aa8b422ef0c5b79b8852043b197ff2e`, `88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c`이다. [사전 source 확인](evidence/independent_review/source_verification_stdout.json)과 [최종 배열 확인](evidence/independent_review/saved_results_attempt_02_stdout.json)은 해당 소유 source, 기존 입력·출력 파일, 정확한 초기 상태와 donor84의 식별을 연결한다. 이번 검토는 원문 검색을 새로 반복하지 않고 동결된 문헌 provenance와 기존 source 자료를 재사용했다.

## 3. 식·소유권·Jacobian

### 3.1 두 가지와 공통 UV 항

[$Y_j=s_j y_{40+j}$, $X=q\cdot Y$, $\eta=(1+q)\cdot Y$](code/compton_system.py)에 따라 $n_e=n_bX$이다. $K=\sigma_Tc/(m_ec^2)$로 놓으면 실제 hot-electron 가지는

\[
Q_h=-4K n_e k_BT U_\gamma,
\qquad
U_\gamma=\rho_{\mathrm{crit},J}\Omega_\gamma y_4/a^4
\]

를 사용한다. $U_\gamma$의 소유자는 현재 상태의 photon energy monopole이다. 과거 경로나 Planck 값으로 바꾸지 않는다. 독립적인 Planck reference는

\[
Q_r=4K n_e k_B U_r(T_r-T),\qquad
T_r=2.7255/a,\quad U_r=a_RT_r^4
\]

이다. 두 가지가 동시에 더해지지 않는 것을 확인했다. 공통 UV 항은 상속된 71개 bin의 동일한 number-flux convention과 두 moment로 만든

\[
Q_{\mathrm{UV}}=K n_e(M_{\mathrm{UV}}-4k_BT U_{\mathrm{UV}})
\]

이다. 계수·단위·bin·UV amplitude·전자 밀도는 기존 owner와 일치한다. [이론](THEORY_KO.md), [Compton source 기록](provenance/COMPTON_SOURCES.json), [독립 adapter 계산](evidence/independent_review/adapter_attempt_01_stdout.json)이 같은 소유권을 지지한다.

### 3.2 추가 log-temperature 행

추가된 항은 $g=XB/(H\eta)$로 쓸 수 있다. 따라서 종 조성에 대한 미분에는 $s_j$와 $q_j\eta-X(1+q_j)$가 모두 필요하다. 구현은 이를 포함하며 $X=0$에서 $X$로 나누지 않는다. geometry에 대한 $-g\,\partial\ln H$와 실제 가지의 직접적인 $y_4$ 미분도 있다. $H$의 비영 미분 열 1, 2, 4, 22를 별도로 확인했다. 실제 hot 항의 logT 직접 미분은 열용량 분모와 $Q_h\propto T$가 상쇄되어 0이며, UV·Planck 항의 역온도 의존은 남는다.

새 source는 RHS와 Jacobian의 행 62만 바꾼다. 첫 62개 행은 상속 구현과 정확히 같다. Compton 자체에 새로운 particle source나 binding source를 붙이지 않는다. 그러나 진화한 온도가 기존 재결합률을 바꾸고, 그 조성이 opacity에 반응하는 기존 결합은 유지된다.

독립 검토는 저장된 두 seed의 상태에서 두 가지를 모두 검사했다. 네 개의 완전한 $63\times63$ 유한 차분 Jacobian, 중성 상태의 21개 조성 미분, Hamiltonian에서 직접 계산한 $H$ 미분, UV bin 합, caloric 식과 transfer ledger를 포함했다. [실제 명령·종료·해시](evidence/independent_review/adapter_attempt_01_process.json)는 exit 0, wall 7.9067 s이다.

| 독립 확인 | 최대 차이 |
|---|---:|
| 완전한 Jacobian의 entry-scaled 차이 | $1.90774\times10^{-8}$ |
| source power 상대 차이 | $2.14230\times10^{-16}$ |
| caloric throughput 정규화 차이 | $1.45905\times10^{-15}$ |
| local transfer ledger 정규화 차이 | $2.84113\times10^{-16}$ |
| 중성 상태 조성 미분 정규화 차이 | $1.78941\times10^{-16}$ |
| $H$ 미분 절대 차이 | $1.16832\times10^{-11}$ |

Jacobian의 entry scale은 $\max(1,|J|,|J_{FD}|)$이다. 이 검사는 아주 작은 모든 entry의 높은 상대 정확도를 증명하지 않는다. 그 한계를 포함해도 현재 추가 행과 상속 full63 결합에서 구체적인 미분 오류는 발견하지 못했다.

### 3.3 평형과 에너지 장부의 의미

Planck source의 $T=T_r$ 평형은 해당 source만의 대수 확인이다. 이 구간의 $T_r$는 원자율의 100 K 하한보다 낮으므로 전체 RHS의 유효 상태 또는 팽창·원자열까지 포함한 평형을 보이지 않는다. 전체 RHS가 지원되지 않는 온도를 거부하는 기존 동작은 유지된다. $E_0=0$의 source-level fixture도 실제 전체 geometry의 $E_0>0$ admission과 구별했다.

전체 gas store는 $u=3k_BT\eta/2+I\cdot Y$이고 팽창 work는 $3k_BT\eta$이다. gas, 반대 부호의 CMB/reference bath, UV reservoir, escape의 장부가 맞는다. 이는 Compton energy source가 photon hierarchy나 Einstein 에너지에 동적으로 들어갔다는 뜻은 아니다. 현재 계산은 명시적인 test-fluid 범위이다.

[Wolfram 기록](evidence/WOLFRAM_COUPLING.json)의 affine Compton 해와 미분 확인은 직접 유도와 맞는다. 해당 기록에 남은 `Power::infy`, `Infinity::indet` 경고와 context 호출 오류를 없었던 것으로 취급하지 않았다. 그 결과를 경고 없는 CAS 증명이나 전체 coupled integrator의 검증으로 승격하지 않는다.

## 4. 실행·분석 코드에서 실제로 교정된 결함

Driver 검토는 `rei_dependency`가 작성한 여섯 helper 시험의 실제 red→green 자료를 재사용했다. 최초에는 빈 output 목록, dense1025 누락, refinement 초기 상태 불일치, 최종 진단 뒤 deadline 확인의 네 결함이 재현되었고, 동결 driver에서는 동일 시험 여섯 개가 통과한다. 이 검토자는 helper 시험 작성자도 driver 작성자도 아니며, 통과 문자열만 읽지 않고 관련 구현과 입력 식별·유한 배정·실패 보존 경로를 확인했다. [원래 driver 검토](evidence/driver_review/REVIEW.json)가 실제 실행 이력을 보존한다.

분석 코드에서는 독립 검토가 다음 두 provenance 결함을 발견했다.

1. refinement의 `PASS`만 읽고 현재 source와 현재 pair hash에 묶지 않아 오래된 결과를 받아들일 수 있었다.
2. 폴더의 case label을 신뢰하고 receipt label·전체 specification·case identity·저장 branch를 확인하지 않아 다른 branch 또는 tolerance의 결과가 같은 이름으로 분석될 수 있었다.

[변경하지 않은 여섯 regression 시험](evidence/independent_review/test_analysis_bindings.py)은 실제 원본 analyzer에서 여섯 실패, 수정본에서 여섯 통과를 냈다. stale refinement, 잘못된 label, 자체적으로는 일관된 잘못된 branch·tolerance, 잘못된 case identity, 잘못된 저장 branch를 각각 검사했다. 전체 expected specification을 고정 입력·설정·초기 상태·runtime에서 다시 구성하고, 현재 `refinement_pairs`와의 정확한 일치 및 세 저장 격자의 branch를 요구하는 수정으로 닫혔다. 정상 synthetic fixture도 `COMPLETE`로 통과했다. [분석 preflight](evidence/independent_review/ANALYSIS_PREFLIGHT_REVIEW.json)에 원래/수정 source SHA, 동일 명령, exit, 실패 출력과 성공 출력이 연결되어 있다. 이 과정의 ODE 실행은 0이다.

## 5. 실제 8개 결과의 독립 재구성

[완료 결과 검사](evidence/independent_review/saved_results_attempt_02_stdout.json)는 각 사례의 정확한 다섯 NPZ·해시·64개 gate, 32개 retained set의 16,170개 상태 행을 확인했다. 이는 중첩 격자 등의 중복 행을 포함한 수이며 독립 표본 수가 아니다. 비교109·accepted·dense513·dense1025에서 종 scale, 중성자·삼중수소 원자상태의 정확한 0, baryon/isotope 보존, 온도·광학 깊이, photon/neutrino number monopole, 유한 angular 표본의 positivity, signed tensor 합을 재구성했다. 초기 상태와 과거 no-Compton baseline의 seed·정밀도·x-grid를 정확히 짝지었다. accepted solver node는 별도 저장된 accepted diagnostics와 같고 두 dense 격자는 중첩된다.

Compton power의 최대 독립 상대 차이는 $1.82098\times10^{-15}$이다. 현재 경로에서 $u$, 실제 source, work, Simpson 적분, throughput 정규화 잔차와 역반응 규모를 다시 계산했다. 과거 경로의 omitted budget를 현재 경로의 열 전달로 재사용하지 않았다.

아래는 refined 사례의 종점과 현재 경로 적분이다. $\Delta T$는 대응하는 기존 refined no-Compton 결과에 대한 차이이다.

| seed / 가지 | $T(z=2)$ K | $\Delta T$ K | $\Delta T/T_0$ | Compton eV/baryon |
|---|---:|---:|---:|---:|
| s03 / actual_hot | 8896.568827 | −1222.379944 | −12.080108% | −2.172816116 |
| s03 / Planck reference | 8896.961461 | −1221.987310 | −12.076228% | −2.170990387 |
| s04 / actual_hot | 8885.220909 | −1231.625843 | −12.174009% | −2.184125580 |
| s04 / Planck reference | 8895.928474 | −1220.918278 | −12.068170% | −2.167628561 |

8개 사례 전체에서 dense1025 first-law 잔차는 $7.51484\times10^{-6}$–$7.57897\times10^{-6}$로 동결 기준 $3\times10^{-4}$를 통과한다. dense513→1025 net integral 변화의 throughput 정규화 값은 $3.62141\times10^{-5}$–$3.63811\times10^{-5}$이다. comparison109의 거친 적분과 dense1025의 채택 검사를 같은 것으로 취급하지 않는다.

총 새 IVP는 8개이고 실제 campaign 청구 wall time은 309.2018257 s이다. 과거 IVP 재실행은 0이다. 이는 동결한 1200 s 배정 안의 완료이며, 반복 측정된 성능 benchmark는 아니다. 독립 결과 검사 자체는 exit 0, process wall 10.8279 s, 내부 배열 확인 4.80464 s였다. [실제 process 기록](evidence/independent_review/saved_results_attempt_02_process.json)이 source의 실행 전후 동일성을 포함한다.

첫 독립 결과 검사에는 검토자 자체의 비교 방식 문제가 있었다. 약 $5.97\times10^{-9}$인 accepted-node 잔차를 상대 오차만으로 비교하여 $1.27\times10^{-16}$의 절대 반올림 차이에서 멈췄다. 원래 script·실패·종료를 보존한 뒤 이 dimensionless 잔차의 receipt 비교만 절대 $2\times10^{-14}$로 고쳤다. 물리적 $3\times10^{-4}$ admission, runtime, analyzer, 입력과 결과는 바꾸지 않았다. [교정 근거](evidence/independent_review/saved_results_reviewer_correction_01.json)와 두 attempt를 모두 남겼다.

## 6. 정밀화와 가지 차이의 해석

네 nominal/refined 쌍은 모두 동결 기준을 통과했다. 최대 $|\Delta\ln T|$는 $4.132\times10^{-7}$ 미만, 최대 conditional fraction 차이는 $2.592\times10^{-8}$ 미만, 최대 $|\Delta\tau|$는 $4.326\times10^{-11}$ 미만, signed six-vector 차이는 $5.686\times10^{-9}$ 미만이다.

각 metric에서 refined branch 차이를 두 가지의 관측된 nominal/refined 변화 합과 비교했다. [독립 배열 계산](evidence/independent_review/saved_results_attempt_02_stdout.json)의 판정은 다음과 같다.

| metric | s03: branch / 정밀화 변화 합 | s04: branch / 정밀화 변화 합 | 유한 비교 판정 |
|---|---:|---:|---|
| $\ln T$ | 약 302 | 약 1954 | 두 seed 모두 branch 차이가 큼 |
| conditional ion fraction | 약 626 | 약 1962 | 두 seed 모두 branch 차이가 큼 |
| 누적 $\tau$ | 약 81.1 | 약 270.6 | 두 seed 모두 branch 차이가 큼 |
| signed six-vector 전체 | 약 $4.96\times10^{-5}$ | 약 $3.95\times10^{-4}$ | 두 seed 모두 분리되지 않음 |
| shear를 제외한 stress 5개 | 약 0.236 | 약 1.99 | s03은 분리되지 않음; s04는 차이가 큼 |

signed six-vector에 shear를 포함한 결과와 stress-only 결과를 합치면 결론이 달라진다. 특히 s04 stress-only의 비가 약 2인 것을 엄밀한 오차 분리나 전역 수렴으로 읽지 않는다. 두 복사 가지의 차이도 실제 anisotropic 광자 스펙트럼의 모델 불확실성 상한으로 읽지 않는다.

현재 경로의 $\max |Q_C|/(HU_\gamma)$는 약 $(5.2253\text{–}5.2723)\times10^{-7}$이고 x 적분은 $(3.4378\text{–}3.4740)\times10^{-7}$이다. 작게 측정된 교환 규모는 현재 test-fluid 근사를 설명하는 자료이다. 누락된 복사 역반응의 보편적 오차 상한은 아니다. Planck 가지에서도 분모는 실제 $U_\gamma$이므로 reference source의 비교량이라는 해석을 유지한다.

## 7. 새 경로 위의 충돌 진단

모든 8개 사례의 109·513·1025 격자에서 native $Y$, $T$, $n_e$, $\eta$, $H$를 현재 결과와 일치시켰다. [고정 HG97 source table](../rec_thermal_omitted_budget_20261022/data/HG97_COLLISIONAL_SOURCE.json)의 cgs 식과 SI 변환을 별도로 구현하여 확인한 최대 계수 상대 차이는 $7.86550\times10^{-14}$이다. 이는 provider를 다시 호출해 같은 계산을 반복한 검사가 아니다.

CI는 kinetic energy에서 canonical binding energy로 같은 크기를 옮기므로 직접적인 총 gas-energy 전달은 상쇄된다. 한 전자를 추가하는 particle 항은 logT forcing에 남는다. H I CE에는 HI/DI/TI, He II CE에는 해당 두 He isotope의 단일 이온 상태가 들어간다. supplied CE의 방출은 optically thin escape로 계산된다. 이들 진단은 이번 ODE에 적용된 CI/CE source가 아니다.

actual_hot refined 경로에서 CI kinetic 진단은 s03 $-1.660207\times10^{-6}$, s04 $-1.619936\times10^{-6}$ eV/baryon이며 binding 값은 반대 부호이다. H I CE는 각각 $-2.377255\times10^{-4}$, $-2.336070\times10^{-4}$ eV/baryon이다. 이는 새 경로에서 supplied 과정의 크기를 보여 주며, absent 채널의 작은 효과를 증명하지 않는다.

published-domain mask와 analytic continuation, coefficient underflow, unavailable 채널을 따로 확인했다. support 적분은 같은 격자의 인접한 두 endpoint가 모두 fit 범위일 때만 지원 구간으로 분류하는 양의 trapezoid 규칙이다. s03 actual_hot refined의 CI는 1024개 중 680개 지원 구간이며 continuation/boundary 몫이 절대 throughput의 약 5.73%이다. H I CE는 1002개 지원 구간이며 그 밖의 몫은 약 $7.55\times10^{-7}$이다. composite 항의 더 엄격한 AND mask를 개별 채널의 uncertainty와 혼동하지 않는다. Li CI/CE, He I CE는 계속 unavailable이며 물리적 0으로 치환되지 않는다.

## 8. 실제 그림과 수치 자료

검토자는 `figures/v2`의 실제 PNG 세 개를 원래 해상도로 열어 보았다. `v1`은 교정 이력으로 남아 있고 최종 시각 판정 대상은 `v2`이다.

| 그림 | 독립 판정 |
|---|---|
| `01_temperature_response.png` | baseline·두 가지·온도·백분율·시간 방향을 읽을 수 있으며 독립 Planck reference의 의미가 명시됨 |
| `02_energy_transfers_and_audit.png` | v2의 symlog 눈금 겹침이 해결됨. gain/loss, 현재 모델 항과 omitted CI/CE, binding/kinetic 상쇄, 누적 trapezoid 곡선과 Simpson endpoint가 구별됨 |
| `03_branch_vs_refinement.png` | branch·각 정밀화·합의 구분, log 축, stress-only의 shear 제외, 유한 비교의 한계가 명시됨 |

그림 manifest의 입력 34개와 출력 13개를 해시로 확인했다. 별도 검사는 NPZ 58개 array, 다섯 CSV의 218·28·3076·4·8개 행을 모두 실제 입력과 대조했다. gas-balance 곡선과 endpoint를 source·work에서 다시 구성한 절대 차이는 최대 $7.47846\times10^{-17}$이다. [그림 수치 확인](evidence/independent_review/figure_data_attempt_01_stdout.json)과 [실제 process](evidence/independent_review/figure_data_attempt_01_process.json)에 exit 0 및 SHA가 있다. PDF 파일의 바이트와 manifest binding은 확인했지만 별도 PDF rasterization을 시각 검토했다고 주장하지 않는다.

## 9. 이전 전달 기준의 재사용 확인

이전 omitted-budget 단위의 완료 영수증을 읽고 보존된 local 파일 및 Dropbox 전체 readback 파일을 다시 해시했다. [읽기 전용 확인](evidence/independent_review/previous_delivery_stdout.json)은 다음 연결을 확인한다.

- local final commit `3a5a853abb2eb0f67650288aa1cee82c576f9ffc`와 remote `04c0b10c1f1ec38d57c751369c553b638979e453`가 기록한 root tree는 `712f2c0ba224fbb902ec8b38f1fa1f53b4c5b4b7`로 일치한다. 보존된 GitHub acknowledgment는 PR122를 draft/open/unmerged로 기록한다.
- 최종 ZIP은 44,847,883 bytes, SHA-256 `22922660598f5f808427b5776962db232c143892474c02864a22423d4157bad7`, payload 888개와 manifest를 합한 889개 entry이다. 보존된 fresh-directory restore audit의 23개 check가 모두 PASS이며 source identity와 이 archive에 묶여 있다.
- ZIP·integrity sidecar·restore audit의 현재 local 파일과 보존된 다운로드 파일이 각각 기록된 크기·SHA-256·Dropbox content hash와 같다. 과거 영수증의 provider completed acknowledgment 및 HTTP200→EOF 전체 readback과도 일치한다.

이번 확인의 새 network read와 restore는 모두 0이다. 현재 원격 서비스를 새로 조회한 판정이 아니라 이미 확보된 완료 전달 증거의 재사용 판정이다. 이전 restore 검토자가 collision provider와 archive builder도 작성했다는 disclosure를 유지한다. 그 restore는 복원 증거이며 독립 물리 유도의 대체물이 아니다. 이번 Compton 단위의 최종 원격 게시·백업은 별도 전달 영수증으로 확인해야 한다.

## 10. 남은 범위와 다음 단위

현재 증거가 확인한 것은 지정된 source equations의 구현, 유한 도함수·저장 상태 검사, 실제 여덟 coupled 경로, source-bound 분석과 수치 자료이다. 다음 주장은 이 증거로 확정되지 않는다.

- 실제 grey photon의 recoil/induced spectral closure 및 angular/spectral collision moments.
- photon·matter·Einstein 에너지의 동적 역반응 해와 그 전역 오차.
- 지원되지 않는 원자 채널과 fit 범위 밖 continuation의 물리 정확도.
- 미저장 solver trial 또는 continuum 전체의 positivity, global convergence, production 적합성.

[다음 단위 제안](NEXT_UNIT_CONTRACT.md)의 저장 상태 진단 재사용은 이 제한과 양립한다. 원래 입력의 반올림 차이를 숨기지 않고, 새 513점 제품에서는 quadrature·누적 적분·구간 support를 해당 격자에서 다시 계산해야 한다. 두 독립 gas-source 식을 같은 값의 복사로 바꾸면 안 된다. 제안의 구현과 benchmark는 아직 `NOT_RUN`이며 이번 검토가 미실행 성능 개선이나 새 물리 결합을 승인한 것으로 읽지 않는다.

구체적으로 발견한 driver·analyzer 결함은 보존된 실패와 동일 회귀 검사로 닫혔다. 실제 결과와 v2 그림에서 새로운 blocker는 발견하지 못했으며, 남은 물리 범위는 위와 같이 명시적으로 열려 있다.

## 11. 최종 보고 문서의 주장 대조

`REPORT_KO.md`, `HANDOFF_KO.md`, `STAGE_C.md`, `LOOP_EVIDENCE_KO.md`를 완료 결과·검토 근거와 대조했다. `NEXT_UNIT_CONTRACT.md`의 구현·benchmark 미실행 표시도 확인했다. 최종 문서의 과학적 주장에 수정이 필요한 blocker는 없다. [문서 검토 영수증](evidence/independent_review/DOCUMENT_CLAIM_REVIEW.json)이 읽은 문서의 정확한 SHA를 소유한다.

보고서에 새로 자세히 제시된 Li7IV/Li6IV의 최대 조건부 분율 위치, 누적 tau와 restart 이후 증가량의 서로 다른 분모, 같은 경로의 Planck-minus-actual source 분해, CI/CE의 continuation throughput, 실제 시간 합계는 [추가 배열 대조](evidence/independent_review/document_facts_attempt_02_stdout.json)로 확인했다. 최대 분율 위치는 두 seed 모두 $z=6.8572165443$이며 전체 기체 전자분율과 구별하는 보고서 해석이 맞다. 최종 시간 합은 사례 전체 308.2163685 s, 적분 58.1794596 s, 진단·저장 249.0527757 s로 서로 다른 계측 범위를 정확히 구별한다.

이 보조 확인의 첫 attempt는 최종 count를 읽는 검토자 코드가 `accepted_nodes`를 잘못된 `solver` 하위 key에서 찾아 `KeyError`로 끝났다. top-level key로 고쳐 동일 계산을 완료했으며 실패 script·출력·교정 기록을 보존했다. 앞선 source 확인의 경로 정규화 오류도 당시 process 기록에 남아 있다. 이들은 검토 보조 코드의 오류이며 과학 source·저장 결과·물리 gate의 변경이 아니다. 전체 판정과 동결된 검토 파일 목록은 [FINAL_REVIEW.json](evidence/independent_review/FINAL_REVIEW.json)에 연결한다.
