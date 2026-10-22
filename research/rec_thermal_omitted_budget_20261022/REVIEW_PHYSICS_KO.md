# 물리 검토: 저장 궤적의 누락 열과정 예산

## 판정과 검토 범위

**PASS_SCOPED_IMPLEMENTATION_AND_FIXED_PATH_RESULTS.** 결과 경로는 results/budget_v1이고, 실행 source identity는 88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c다. 현재 구현·산출물에서 이 유한 후처리의 완료를 막는 물리적 결함을 찾지 못했다. Physical HOLD 등 기존 연구 상태를 해제하는 판정은 아니다.

검토자는 이 단위의 THEORY_KO.md와 SOURCES.json 작성에 참여했다. 아래 검토는 다른 담당자가 작성한 실행 코드와 산출물에 대한 독립 검산이며, 자신의 이론 문서를 독립적으로 심사했다는 뜻은 아니다. 새 runtime 모듈을 불러오지 않고 이전 thermal8 원시 NPZ의 \(Y,T,H,n_b\)에서 HG97 원식을 직접 평가했다. \(n_e\)와 입자수 \(\eta\)도 \(Y\)로 다시 계산했다. Compton 항은 동일한 원시 광자 모노폴과 기존 UV bin에서 별도로 계산했다.

새 ODE 적분은 0회다. 이전 126개 및 thermal8 IVP를 재실행하지 않았다. 검사한 상태는 8개 궤적의 872개 저장점이다. [기계 판독 검토 기록](evidence/PHYSICS_REVIEW.json), [독립 재계산](evidence/independent_physics/recompute_saved8.py), [산출물 대조](evidence/independent_physics/compare_budget.py), [독립 수치 배열](evidence/independent_physics/independent_fixed_path.npz)을 보존했다.

## 실제 대조 결과

각 새 budget NPZ와 최종 receipt의 파일 SHA, 실행 source identity 및 원시 궤적 SHA를 확인했다. 109점 소스, 다섯 계수, CI abundance source, 입자수 소스, 고정 경로 온도 강제항, 적분과 누적 배열을 대조했다. 독립 계산과의 최대 상대 차이는 다음과 같다.

| 대조 항목 | 최대 상대 차이 |
|---|---:|
| 순간 에너지 소스 | \(1.493\times10^{-14}\) |
| CI/CE 계수 | \(7.866\times10^{-14}\) |
| 고정 경로 온도 강제항 | \(1.698\times10^{-15}\) |
| 109 trapezoid / 55 trapezoid / 109 Simpson 적분 | \(3.286\times10^{-15}\) |

원식을 직접 계산하는 경로와 로그 영역에서 계산하는 구현 사이의 부동소수 차이 범위다. 원자계수 자체의 실험적 오차가 이만큼 작다는 뜻은 아니다. CI의 \(n_b I\cdot F\)와 병진열 손실의 상쇄, 전자 생성, 핵종·baryon 보존은 계약의 scaled \(10^{-13}\) 이내다. neutron/tritium abundance와 이들의 CI source는 정확히 0이다. 공급·미공급 native masks, HG 정확도 구간, 구간 밖 continuation, 부호와 SI 변환도 일치했다.

첫 후처리 전에 두 항목을 바로잡았다. CI gate는 동일한 사건수로 만든 항끼리의 항등적 상쇄 대신 \(n_b I\cdot F\)의 별도 gradient residual을 사용한다. Planck 기준선의 저장 에너지밀도는 그 기준선 power와 동일한 \(a_R T_{\rm ref}^4\)를 쓴다. 실제 Bianchi 광자 밀도는 기존 정규화를 유지한다. 현재 source identity에는 이 수정이 포함되어 있다.

## 핵심 물리 결과

다음은 네 Mao primary 궤적의 \(z=7.9637328\to2\), 109점 trapezoid 결과다. 양수는 gas로의 에너지 유입이다.

| 성분 | eV/baryon 범위 |
|---|---:|
| 실제 광자 에너지의 hot-electron Compton | −2.59186 … −2.57604 |
| 별도의 등방 Planck 기준 교환 | −2.57444 … −2.56969 |
| 외부 UV Compton 순가열 | \(+6.2316\times10^{-5}\) … \(+6.2336\times10^{-5}\) |
| H/He CI 병진열 이동 | \(-2.0649\times10^{-5}\) … \(-2.0446\times10^{-5}\) |
| 같은 CI의 결합 저장 증가 | \(+2.0446\times10^{-5}\) … \(+2.0649\times10^{-5}\) |
| 공급된 H I/He II CE 방출 | −0.00132215 … −0.00131222 |

현재 공급한 누락 성분 중 실제 광자 모노폴을 사용하는 Compton 항이 지배적이다. 그 크기는 같은 새 궤적·같은 구간의 기존 primary photoelectron 가열의 약 29.72–29.92%, RR 병진열 냉각의 약 3.13–3.16배, 팽창 work의 약 44.19–44.49%다. 따라서 다음 연구에서 Compton을 우선 결합할 실질적 근거가 있다. 기존 전체 \(z=20\to2\) prescribed 경로의 약 −19.7 eV/baryon 외부 요구량과는 경로와 적분 구간이 다르므로 같은 물리량으로 비교하지 않는다.

CI의 음의 병진열과 양의 결합 증가를 함께 더하면 총 gas 에너지에서 상쇄된다. 이를 방사 손실로 해석하지 않는다. 자유전자 증가를 포함한 전체 직접 강제항의 적분은 네 primary에서 약 −1.02955 … −1.02308이다. 이 값은 무차원 fixed-path forcing이다. 실제 \(\Delta\ln T\), 온도 감소율 또는 새 최종 온도로 바꾸지 않는다.

현재 여덟 궤적 모두 CI 정확도 구간 아래에 10/109점, CE 구간 아래에 3/109점이 있다. 같은 원식을 이어 평가한 CI의 continuation/boundary 에너지는 약 \(1.1\times10^{-7}\) eV/baryon 크기, CE는 약 \(1.2\times10^{-8}\) eV/baryon 크기다. 이 작은 채택식 기여는 구간 밖 계수의 실험적 정확도를 입증하지 않는다. 경계 구간은 양 끝점 기준으로 분류했고, 지원 구간 합과 나머지 합이 전체 trapezoid를 재현함을 확인했다.

## 해석 한계와 다음 행동

실제 광자장의 leading thermal Compton 항은 저장된 에너지 모노폴로 계산 가능하다. 완전한 CMB recoil·induced 교환은 저장된 수·에너지 모멘트만으로 닫히지 않는다. Planck 곡선은 자체 에너지밀도와 \(T_0/a\)를 가진 별도 비교이며 실제 비등방 스펙트럼을 복원한 값이 아니다. 두 Compton 곡선을 같은 총합에 더하지 않는다. UV의 낮은 점유수 근거는 기존에 채택한 외부 UV 스펙트럼에 한정된다.

109점 대 55점의 hot Compton 적분 차이는 약 0.00405 eV/baryon이고 109점 Simpson 차이는 약 0.00135 eV/baryon이다. 2.58 eV/baryon의 성분 크기에 비해 작지만, 이는 저장 격자에서의 진단이다. 사라진 dense trajectory를 재현한 검증이나 연속 적분의 엄밀한 오차 상한은 아니다. 작은 RR 경로별 예산 차이를 이보다 강한 연속 정확도로 승격하지 않는다.

He I CE/metastable, Li CI/CE, free-free, charge exchange, secondary electrons, 다중 photoionization, 복사수송 및 핵 에너지는 여전히 이 공급 범위 밖이다. 공통 Maxwellian \(T\), prompt escape, isotope electronic equality, test-fluid gas와 초기 prefix 계승도 유지된다. 후처리로 새 opacity·기하·stress 반응을 예측하지 않는다.

다음 행동은 **Compton 결합식과 photon 에너지 소유권을 명시한 새 유한 실행계약을 작성하는 것**이다. 실제 \(U_\gamma\)의 hot 항을 사용할 범위, recoil/induced correction의 추가 공급 또는 이름 붙인 근사, gas와 photon 사이 에너지 반작용을 계약에서 정해야 한다. 이 결과만으로 새 ODE 실행이나 완전한 열 closure가 이미 완료되었다고 간주하지 않는다.
