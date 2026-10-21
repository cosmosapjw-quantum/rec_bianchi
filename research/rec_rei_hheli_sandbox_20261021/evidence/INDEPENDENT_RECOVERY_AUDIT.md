# 첫 결과의 직렬화 실패와 data-only 복구: 독립 감사

판정: **PASS_IO_ONLY_COMPATIBLE_DATA_RECOVERY**. 이 판정은 `INDEPENDENT_RECOVERY_AUDIT.json`에 지정한 byte/hash에 적용된다.

첫 `s00_m02_r02`는 전체 z20→2의 193개 저장 노드와 trajectory.npz를 만들었으나 RESULT의 NumPy boolean JSON 직렬화에서 실패했다. 원래 `results/pilot`의 claim, 실패 traceback, empty temporary report, NPZ, FROZEN, RUN 기록 6개는 독립 사전 hash와 모두 일치하며 보존되어 있다. 원 namespace에 COMPLETE/RESULT를 뒤늦게 덮어쓰지 않았다.

Stage B 보존 ZIP에서 이전 coupled.py를 직접 읽어 원 FROZEN의 SHA `09a3325c584b895f8c1de44d3b64a458ec7e27f8eec843c7e15aa246a6088d47`과 일치함을 확인했다. 새 SHA는 `e3005323ea085251f14262dac5671fd93d1e31d20b9dc877ca64146b58ac509f`다. 두 Python module에서 `atomic_json` 함수만 제거한 **전체 AST가 정확히 동일**했다. import, 상수, class, RHS/Jacobian, 진단, integrator 호출, run_case가 포함된다. 수정은 NumPy scalar의 `.item()` JSON 변환뿐이다. source byte identity를 주장하지 않으며, 수치 계산 경로가 같은 I/O-only 변경으로 구별한다.

모든 frozen scientific input을 대조한 결과 변한 파일은 coupled.py 하나였다. case 설정과 나머지 파일 SHA는 동일하다. 새 `results/pilot_v2` 첫 case의 NPZ는 원 NPZ와 152,815 byte 전체가 동일하며 SHA256은 `7dfd1ec7618a44588756d6a1dd01959a089ccb431d6b7623b0708480acffac89`다. old execution identity `854462ff0e533217ae41f571fb222c9493a668649698f6a3e21724ed5ff230b3`와 새 compatible delivery identity `25ea4617c21fbe785cea490d157d2a0bbaac954d7a8f791b12ae79b939e04db8`를 독립 계산해 RESULT/RECOVERY/COMPLETE와 대조했다.

복구 코드는 solver를 호출하지 않고 저장 상태의 193개 진단을 재평가했다. CoupledSystem의 RHS/Jacobian 진입점 호출은 0이며 재평가된 진단의 최대 scaled 차이는 0이다. 진단 내부에서는 atomic algebraic rate와 Jacobian 계산이 수행되므로 “모든 원자 RHS 산술조차 0회”라는 의미로 확대하지 않는다. 검토자 자신은 scientific module을 import하지 않고 NumPy로 배열·hash·identity를 대조했다. 검토자 새 ODE/RHS 실행은 0이다.

복구 RESULT는 13개 유한 gate를 재평가해 참으로 저장했고 COMPLETE→RESULT→NPZ hash chain을 만족한다. 첫 solver의 nfev/njev/nlu/wall time은 직렬화 실패로 신뢰할 반환이 없으므로 null/UNKNOWN을 유지했다. 이 값을 추정하거나 이후 실행의 수치로 대체하지 않았다.

독립 저장 배열 확인: shape 193×62, z=20→2.0000000000000004, 모두 유한, 최소 scaled population 0, baryon 정규화 최대 차이 8.88e-16, τ_T(z=2)=0.06934076357187009, trace-energy fraction 최대 2.1941e-8, photon/nu의 energy/number 129-angle minima 1. 기존 n/T population은 정확히 0이다. 이 값은 저장 데이터의 확인이며 새로운 ODE 정확도 인증은 아니다.

현재 나머지 124개의 새 case는 별도 실행 중이다. 이 감사는 복구된 한 case에만 적용하며 아직 전체 campaign과 그림의 통과를 선언하지 않는다. `Physical HOLD`, `global convergence NOT_RUN`, `production NOT_APPROVED`, 원래 REC U5 HOLD를 유지한다.
