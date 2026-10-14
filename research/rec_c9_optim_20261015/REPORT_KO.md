# REC C9: LRS Bianchi I 광자 수송의 실제 벡터화·병렬화·경량화 및 코드 검토

2026-10-15 KST. 이번 선택된 단계: PhysMath C9(실제 코드·물리·수치 표면 검토와 근거 있는 건설적 수정). 선행 REC R10 이론 사이클은 이미 완료되었으므로 새로운 R1–R10 이론 사이클을 자동으로 시작하지 않는다. 이 C9에서 필요한 한정된 유한 광자맵·source 양성·공변식은 새로 검사했다. User-requested local coding은 대화에서 직접 수행했고 별도 local Codex, native subagent, 서드파티 코드 수정 대행은 사용하지 않았다.

## 1. 실제 저장소와 재사용된 과학적 범위

- 실제 REC Python package `full_bianchi_hyrec`와 C8 positive-rate log interval 공급자. Parent upstream draft PR87 head b65a1d2a91e804387171dcfe2a4d2e51c3ed10c2.
- Bianchi I metric signature (-,+,+,+): ds²=-c²dt²+a²e^(-2b)(dx²+dy²)+a²e^(4b)dz². H=dot a/a, s=dot b, shear=(-s,-s,2s). 정상 비틸트 축대칭·고정 배경을 대상으로 한다. q_ref=0,±0.005,±0.01, a_ref=1/21, a_end=0.2. H²=H_FLRW²+s² 또는 명시된 SameH 진단을 사용할 수 있다.
- 독립 REI PR117 마지막 확인 head 0c9fd151b6e0aef9ee2414ed672364afa4a3dce1: REI는 이미 Rust의 threshold-aware q advance와 최적화된 병렬 SoA batch를 보유한다. 이번 REC 작업에서는 REI의 Rust 구현을 그대로 복제하거나 생산 solver/source, checkpoint, launcher를 건드리지 않고 **물리·수치적으로 독립된 빠른 Python oracle**를 개발했다. BASS_HE PR56의 따뜻한 HE18 second-cell 원자물리도 별도 lane으로 유지한다.
- Fleury, Pitrou, Uzan 2015 PRD91 043511의 공간 Killing 모멘텀 보존에 맞는 null-ray 해석적 구성. 비슷한 비LTE short characteristics와 양의 전파/공간·시간 오차 연구는 Lambert et al, Eur. J. Phys. 37 015603 (2016); Egger & Schlottbom, SIAM J. Numer. Anal.54 (2016) 등과 별도 분야인 점을 지킨다.

## 2. 실제 변경 코드

신규 `src/full_bianchi_hyrec/trajectory/axisymmetric_batched.py`: `AxisymmetricBianchiIBatchSolver`, `BatchIsotropicCoefficients`, `AxisymmetricBatchFaceResult`. `trajectory/__init__.py`에서 공식 import. C7 `CharacteristicAngularSolver`의 엄격한 **실제 모든 snapshot 노드·model/method identity** 검사를 constructor에서 재사용한다. 기존 scalar/generic tilted-Bianchi 수송 계산은 한 줄도 변경하지 않았다.

Face event (L_f,b_f,E_f,n_f)에서 임의 L의 ΔB=b(L)-b_f, ΔL=L-L_f,
R²=e^(2ΔB)(n_fx²+n_fy²)+e^(-4ΔB)n_fz²,
E/E_f=e^(-ΔL)R,
n_perp=e^(ΔB)n_fperp/R, n_z=e^(-2ΔB)n_fz/R.
이는 k_i=a exp(beta_i) E n_i의 보존과 일치한다. 분산/부동소수점 편향을 주장하지 않으며 실제 코드에서 전체 방향 벡터 정규화·원점/부분 구간·±q를 검사한다.

각 source midpoint에서 주파수 배열을 일괄 평가하고, positive source j>=0, opacity chi>=0에 대해 f_{i+1}=exp(-chi_i dt_i) f_i+j_i [-expm1(-chi_i dt_i)]/chi_i를 NumPy로 벡터화. chi_i=0은 연속 극한 j_i dt_i를 사용한다. 유한 Δt와 Δb는 **각 source 시간 구간당 한 번** C8 `interval_log` 적분하고 모든 ray/chunk에서 공유한다. 광자 자체는 해당 Bianchi I 범위에서 정확한 conserved-null-map을 사용하므로 scalar midpoint 방향 오차는 발생하지 않는다. 강한 optical opacity에서도 nonnegative finite occupation을 검증한다.

Geometry cache는 최대 4개 (tau_start,tau_end,n_step)의 고정 수치 격자만 보존하고 각 배열 및 mapping을 readonly 처리한다. source callbacks와 각 광자 occupation은 캐싱하지 않아 매번 독립적으로 계산한다. 저장 비용 O(nsteps), 업데이트 작업 메모리 O(chunk_size) + 최종 M-ray 출력 O(M). nsteps×M 대형 히스토리 행렬을 메모리에 저장하지 않는다.

병렬: `workers=1..32` 선택적 `ThreadPoolExecutor` chunk 처리, shared readonly geometry, deterministic output ordering. 입력 source/opacity 콜백의 thread_safe=True를 사용자가 명시적으로 주장해야 workers>1을 허용한다. 실제 worker path는 chunks>=2일 때만 실행된다. 이 컴퓨트에서는 병렬화가 오히려 느리므로 default는 1 worker. Python multiprocessing/CUDA/JAX/Numba 또는 native xAct 코드 변환은 **시행하지 않았다**.

## 3. 실제 오류 조사와 테스트

- 최초 새 모듈 누락 pytest collection RED, 구현 후 새 과학 검증 GREEN.
- 첫 geometry cache는 같은 사건 쌍에도 매번 새 연산을 수행해 `a is b` RED였다. 캐시/readonly 구현 후 GREEN. 4-slot memory cap/불변성 검사, callback 상태 변경 시 stale source 값이 재사용되지 않는 음성 회귀 모두 GREEN.
- 광자 키-모멘텀 원점, nonzero anchor/partial interval, signed q, SameH, 투명~optically-thick chi, scalar source 미분/수렴, cross-chunk exact equality, parallel result exact agreement, source mismatch와 음수값 거부, high precision 독립 mpmath70 shear 계산 테스트.
- 새로운 C9 전용 Python pytest **30 PASSED**. 최종 관련 REC background + C7 + C8 + C9 + causal-history 회귀 **100 PASSED, 2 SKIPPED**(명시적 --run-slow가 필요한 테스트). `python3 -m py_compile`와 Git diff--check는 별도 확인.
- 한정된 C9 CAS: Wolfram15.0.1 유한 광자 에너지·방향 사상의 합성 성질, 정확한 constant-source semigroup 및 clock perturbation generator 등 4개 잔차0. 실제 연구 PC Wolfram Engine15.0.0 + xTensor1.3.0 (-+++)의 Killing 대칭 미분 분해, source/positive-rate 미분 3개 잔차0. Killing 보존의 결론에는 **배경 Killing 장과 광자 geodesic 조건이 추가로 필요**하며, 단순 0 잔차만으로 전체 GR/원자반응 소스가 검증되는 것은 아니다.
- native subagent=NOT_RUN, 독립 모델/피어 리뷰=NOT_RUN. 단, 독립 mpmath70 적분과 실제 scalar reference 비교 및 Wolfram CAS는 각각 확인했다.

## 4. 측정한 속도·메모리·정확도

공통 배경 257 snapshot, nstep128, q_ref=.01, j=3e-20*(1+.2 sin(2L)+.02 ν/2.4e15) s^-1, chi=4e-17*(1+.1 cos(L)+.04 ν/2.4e15) s^-1. 실제 scalar solver와 batch solver를 생성/준비한 후 각각 3회 실행한 중앙값. **원본 scalar와 vectorized exact-Killing source occupation의 최대 상대차: 8.71795e-10.** 이 비교는 두 알고리즘의 bit-identity가 아니라 source-물리 대응 검사이다.

| N_ray | scalar median [s] | cold-cache batch [s] | warm-cache batch [s] | warm speedup |
| 8 | .463938 | .015502 | .004723 | 98.23x |
| 26 | 1.547466 | .015080 | .004494 | 344.33x |
| 64 | 3.959899 | .030297 | .004681 | 845.93x |

수치는 동일한 background와 source, nstep에 한정되며 준비·첫 cache 채움 비용은 warm-cache 중앙값에서 제외한다. 이미 C7의 일반 scalar null-ray 미분오차가 더 클 수 있다는 점에서 두 구현은 **같은 수치 방식을 비트 대 비트로 비교한 것이 아니다**. 광자 exact-geodesic map의 우수한 물리 기하 정밀도와 scalar transfer의 일치가 확인된 범위에서 속도를 비교했다.

병렬 성능: M=16,384, chunk4096 => 네 개 진짜 worker chunk를 사용함. 1 worker .057023 s, 2 workers .079315 s, 4 workers .126604 s: 2 workers가 1.39x 느리고 4 workers는 2.22x 느림. M=256 또는4096에서 같은 4096 chunk는 하나뿐이어서 workers=2/4 지정도 **실제 멀티스레드 branch가 아니다**. 그래서 batch는 기본 single worker로 채택했다.

M=16,384 벡터 batch의 Python tracemalloc peak ≈3,299,806 bytes, M=65,536에서는 ≈13,184,886 bytes. 이 측정은 Python 추적 객체 할당만 포함하며 전체 프로세스 RSS/드라이버/native library memory의 보수적 상계는 아니다. 실행 비용의 완벽한 HPC weak/strong scaling 인증도 아니다.

## 5. 다음 실제 작업

이 C9 연구는 현재 모델에 대한 실제 과학·코드 리뷰 및 성능 변경을 완료했다. 외부 독립 reviewer가 없음을 명시하는 **SCOPED_C9_WITH_EXTERNAL_REVIEW_NOT_RUN**로 종료한다. 선행 REC 이론 R10은 닫혀 있으며 이번에는 새로운 이론 R1–R10 사이클을 시작하지 않았다.

다음 사용자 요청에서 C10은 수정된 성능·물리 주장에 대해 release/admission을 결정하고 immutable source/target/return receipt를 정리한다. 추가 확장은 full non-LRS Bianchi, tilted fluid, full HyRec atomic collision/reionization, observational null-cone optics에 대해 별도의 실제 설계·테스트 없이는 확대하지 않는다. REI native Rust rate table/AXBI AX11 AX12 또는 대형 NCP 전체 병렬 이력은 이 성과로 변경되었다고 주장하지 않는다. 

최소 로컬 명령:
- `python3 -m pytest tests/trajectory/test_axisymmetric_batched_c9.py -q`
- `python3 -m pytest tests/background tests/trajectory/test_axisymmetric_batched_c9.py tests/trajectory/test_axisymmetric_bianchi_i_c8_numerics.py tests/trajectory/test_axisymmetric_bianchi_i_physical_transport.py tests/trajectory/test_characteristic_angular_solver.py tests/trajectory/test_causal_characteristic_history.py -q`
- `PYTHONPATH=src python3 scripts/benchmark_axisymmetric_batch_c9.py --out /NEW/BENCH.json`
- `PYTHONPATH=src python3 scripts/assess_axisymmetric_batch_c9.py`

참고 원전: Fleury, Pitrou, Uzan, Phys.Rev.D 91 (2015) 043511 DOI 10.1103/PhysRevD.91.043511 ; Egger & Schlottbom, SIAM J. Numer. Anal.54 (2016) DOI 10.1137/15M1051336 ; Lambert et al, Eur. J. Phys.37 015603 (2016) DOI 10.1088/0143-0807/37/1/015603 ; Higham, Accuracy and Stability of Numerical Algorithms (SIAM, 2002).


## 6. 최신 재검산·REI 상태 수정 (2026-10-15)

최종 검산 때 C9 단위 30 PASS, REC background+C7+C8+C9+기존 causal history 100 PASS/slow 2 SKIP를 다시 실행해 로그에 보존했다. 별도 시스템 Python에서 패키지를 바로 import한 최초 명령은 editable install도 PYTHONPATH도 지정하지 않아 ModuleNotFoundError(exit 1)였다. 프로젝트의 src 레이아웃대로 **PYTHONPATH=src**를 명시한 import는 exit 0이고, py_compile도 exit 0이다. 이 에러는 물리식이나 구현 결함이 아니라 명령 환경의 누락이며 최초 실패 영수증은 유지한다. 또한 read-only 저장 geometry cache의 source 콜백은 변경 후에도 새로 평가한다는 회귀 검사를 포함했다.

2026-10-15 KST 약 08:39에 확인한 REI PR117 공개 HEAD는 129627969dae18958ceef520c197bfa8b20b8888. AX07 scoped 완료, AX08 원본 signed family 진행 중, AX11/AX12 PENDING, scientific admission NOT_ISSUED. 앞서 C9 source 검토에 사용한 REI commit 0c9fd151b6e0aef9ee2414ed672364afa4a3dce1는 threshold-aware q transport와 SoA 연구 증거의 **그 당시 실제 부모 소스**이며 이후 PR HEAD와 구분된다. 진행 중인 REI PLUS recovery나 원격 러스트 native 파일에는 이번 REC C9에서 write하지 않았다.

다음 실제 단계는 REC C10의 bounded release/merge readiness 판정이다. 이번 archive/PR은 source 및 numeric readiness이고 full-HyRec source, reionization abundance, observer optical depth, production native Rust scientific admission은 여전히 아니다.
