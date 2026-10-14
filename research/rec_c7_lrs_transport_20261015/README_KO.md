# REC C7: 축대칭 Bianchi I의 실제 광자/방출·흡수 source 수송 검증

선택 단계 C7만 진행. 이전 REC C5/C6가 만든 실행 가능한 LRS Bianchi I background supplier를 REC의 실제 CharacteristicAngularSolver에 연결했다. Einstein–HyRec 전체 backreaction 또는 REI 과학적 admission은 발급하지 않는다.

## 실제 변경과 물리식

메트릭 ds²=-c²dt²+a²exp(-2b)(dx²+dy²)+a²exp(4b)dz², signature (-+++), H=ȧ/a, s=ḃ, shear=diag(-s,-s,2s). 기하 특성은 원 REC normal_frame_characteristic을 그대로 사용한다. f의 방출·흡수 식 df/dt=j-χf를 적분할 때 기존 solver는 dt≈dτ/H_mid를 적용했으며, 새로운 opt-in interval_source는 고정된 실제 a1,a2에 대해 dt=∫d ln(a)/H를 직접 적분하여 전달한다. 기존 기본 동작은 변경하지 않는다. Hydrogen 비틸트 frame/Thomson source convention도 변경하지 않는다.

코드: src/full_bianchi_hyrec/trajectory/characteristic_angular.py 옵션 interval_source, tests/trajectory/test_axisymmetric_bianchi_i_physical_transport.py 신규 물리 테스트, scripts/validate_axisymmetric_transport_c7.py 신규 독립 CLI.

Source binding은 선언 해시만 검사하지 않는다. 일치해야 하는 model/schema/branch/해시와 함께 각 snapshot 노드의 실제 H, sigma, deceleration q, N, A, frame rotation, beta, D0_beta를 원래 normal-comoving Bianchi I의 물리식에 대조한다. 첫 구현이 내부 H 2% 변조를 해시만으로 놓치는 실패를 실제 RED test로 관측했다. 모든 노드 검사 후 동일한 fixture가 거부됨을 GREEN으로 확인했다. 다른 Bianchi branch 또는 source mismatch는 fail closed.

## 실제 수치 결과

구간 a=1/21→0.1, initial occupation f0=.0015, 상수 j=3×10^-20/s, χ=4×10^-17/s, 65 snapshot 노드, 64 transport steps. 해석해 f2=f0 exp(-χΔt)+(j/χ)(1-exp(-χΔt))와 비교.

q_ref=0: 기존 midpoint-H 상대차 +8.99921837e-6, 신규 source-bound +6.66133815e-16.
q_ref=+0.01: 기존 +8.99999728e-6, 신규 +6.66133815e-16.
q_ref=-0.01: 기존 +8.99999728e-6, 신규 +6.66133815e-16.

해석해가 같은 배경 dt를 이용하므로 이 계산은 clock–source 연산자 연결 검증이지 dt 자체에 대한 새 독립 인증은 아니다. dt 정확도는 선행 C5/C6 R8 원시 102-step/60자리 기준 계산에서 별도 비교했다.

충돌 없는 광자 검산(1025 snapshots/512 midpoint steps, μ_face=.43, q=.01): 상대 초기 에너지 오차 3.15327098e-10, μ 절대 오차 -9.75044323e-10, 보존 Killing 공간운동량 k_i의 상대 잔차 1.08270359e-9, Liouville occupation 변화 0. 정확한 finite null map과 원 REC time-dependent characteristic solver를 비교했다.

시간 의존 제조 source: j(L)=3e-20[1+0.1sin(3L)]/s, χ(L)=4e-17[1+0.03cos(L)]/s. 독립 SciPy DOP853에서 df/dL=(j-χf)/H를 풀었다. 64,128,256 steps 실제 REC 특성 적분 오차: 7.60584827e-10, 1.90163786e-10, 4.75420311e-11. 수렴 비율 3.99963,3.99991이며 scoped 2차 accurate source quadrature를 지지한다. 강성 source/전체 수치 불확실성은 미검증.

추가 근거: 실제 Bianchi volume (ae^-b)^2(ae^2b)=a^3, n_H∝a^-3, 정상 source j=χf0, q 반사, FLRW 극한. Wolfram 15.0.1은 여섯 상징 항등식 잔차 0; 연구 PC Wolfram Engine15.0.0+xTensor1.3.0은 signature -+++ covariant current/product 네 잔차 0. xCoba/Full Einstein/HyRec 검증은 아니다.

## 검증, 명령, 다음 단계

실제 RED: 존재하지 않던 interval_source 인자; 신규 API 뒤 GREEN10. 두 번째 RED: 가짜 중간 H 변조 통과; 전체 노드 검증 수리 후 GREEN13.

REC repo 루트 명령:
python3 -m pytest tests/trajectory/test_axisymmetric_bianchi_i_physical_transport.py -q
python3 -m pytest tests/background tests/trajectory/test_characteristic_angular_solver.py tests/trajectory/test_axisymmetric_bianchi_i_physical_transport.py tests/trajectory/test_causal_characteristic_history.py -q
PYTHONPATH=src python3 scripts/validate_axisymmetric_transport_c7.py --out /ABS/NEW/SCIENCE_RESULTS.json

최종 타깃 회귀: 53 PASS, 2 slow SKIP. 완전한 HyRec/cosmological reionization 계산, native REI Rust binary/trajectory 실행, production source migration, 독립 agent scientific review/subagents는 NOT_RUN. REI AX08 실행 프로세스/AX11, AX12 DAG를 변경하지 않는다.

다음 단계 C8: source/geometry/opacity의 이산·근사 오차 분해, 정련·성능·resource 실측, 작은 dt와 time-dependent stiff source의 독립 uncertainty. 이 C7 결과만으로 full scientific admission을 변경하지 않는다.

주요 출처: Fleury, Pitrou & Uzan, PRD91 043511 (2015), https://doi.org/10.1103/PhysRevD.91.043511 ; Higham, Accuracy and Stability of Numerical Algorithms (2002); REC v0.52 실제 소스. Original scientific novelty unverified.
