# full63 Compton 드라이버 독립 검토

판정: **PASS_SCOPED_DRIVER_REVIEW**. 실제 재현한 네 실패를 root가 최소 수정한 뒤, 동일한 여섯 점검이 모두 통과했다. 이 판정은 채택한 유한 pilot의 드라이버 구현에 한정한다. 새 ODE 실행 결과나 전역 수렴, 방사선 에너지와 Einstein 계의 물리적 closure를 승인하는 판정은 아니다.

## 검토 대상과 독립성

검토한 `run_compton.py`는 root가 작성했고, `compton_system.py`는 별도 runtime 작성자가 구현했다. 이 검토자는 두 파일을 수정하지 않았다. 이 검토자가 이전 H/He 충돌 provider와 새 충돌 후처리 파일을 작성했다는 점은 공개한다. 충돌 후처리는 Compton ODE의 실행 의존성이 아니며, 그 구현의 독립 검토는 이 판정에 포함하지 않는다.

검토 후 실제 읽기 전용 `source_identity()`와 `load_inputs()`가 exit 0으로 완료되었다. runtime identity는 `c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac`이며 source 항목은 16개다. 두 seed의 기존 Mao nominal/refined 네 궤적과 donor 영수증·배열 결합, 각 초기 full63 벡터를 확인했다.

| 파일 | 검토 SHA256 |
|---|---|
| run_compton.py | e81220564d303467c08b1162dcd9bea8a365c8d689c64b00aeaac7378e0511b9 |
| compton_system.py | 1035690890e2665769e1692e81d49d4209366291b1c8f2345f973818678f9ae9 |
| FROZEN_CONTRACT.md | 5d7d27ade2c3924bc2df5b6b376a94aff3a788e36a7cab651ebcce03c55fcb92 |

## 실제 실패 재현과 수정 확인

실행 명령은 두 번 모두 다음과 같았다. 테스트 파일의 SHA256도 두 실행에서 동일하다.

```sh
python3 research/rec_compton_coupled_20261022/evidence/driver_review/test_driver_helpers.py
```

테스트는 실제 드라이버의 함수 본문을 AST로 분리해 synthetic fixture에 적용했다. 아직 고정되지 않은 runtime을 import하거나 ODE를 실행하지 않고, 해당 함수가 잘못된 입력·시간 상태를 어떻게 처리하는지 확인했다.

| 재현한 문제 | 첫 실행 | 최소 수정 후 |
|---|---|---|
| 빈 출력 목록도 재사용 검증을 통과 | ValueError가 발생하지 않아 실패 | 다섯 필수 NPZ를 정확히 요구해 통과 |
| dense1025가 빠진 부분 출력 목록 허용 | ValueError가 발생하지 않아 실패 | 누락·추가 목록을 거부해 통과 |
| 초기 누적 시간 좌표가 다른 refinement 비교 허용 | ValueError가 발생하지 않아 실패 | 초기 벡터 및 첫 저장 상태의 정확한 일치를 요구해 통과 |
| 마지막 refinement 진단이 예산을 넘겨도 COMPLETE 반환 | TimeoutError가 발생하지 않아 실패 | 최종 진단·저장 뒤 deadline을 확인해 통과 |

첫 실행은 exit 1, 1.694074329 s였으며 여섯 점검 중 네 실패와 두 통과가 있었다. 완료·실패·미완료 시도의 누적 시간 부과, native63 tolerance와 저장 grid 설정은 처음부터 통과했다. 수정 후 동일한 여섯 점검은 exit 0, 0.802472562 s에 모두 통과했다. 원래 실패 출력은 덮어쓰지 않고 `attempt_01_*`에 보존했고, 성공 출력은 `attempt_02_*`에 별도로 저장했다. 출력 목록뿐 아니라 COMPLETE 상태, 비어 있지 않은 identity, 정확한 64개 true admission gate도 실제 수정 코드에서 확인했다.

## 물리량·저장·재사용 경로

`actual_hot`의 에너지 밀도는 현재 적분 상태의 `raw[4]`와 현재 scale factor로 계산한다. 현재 Hubble 값에서 정의한 critical density나 photon number monopole, 기존 궤적의 보간값을 대신 사용하지 않는다. `planck_reference`는 별도로 정한 온도와 밀도를 사용하며, 두 CMB 후보를 동시에 RHS에 넣지 않는다. 두 분기에 같은 외부 UV recoil 및 thermal 항이 들어가고, 양쪽 CMB 후보와 UV 성분은 저장 진단에 남는다.

새 source는 온도 행에만 더한다. 온도에 반응하는 기존 이온 수 반응과 전자 opacity coupling은 full63 계를 통해 유지한다. 반대 방향의 bath source는 transfer ledger에 기록하며 photon hierarchy나 Einstein 에너지에 동적으로 적용하지 않는다. 상속된 진단의 명시적인 zero-bath 항도 새 gas source에 맞게 대체한다.

가스 에너지는 baryon당 `1.5 kB T eta + I·Y`다. 드라이버의 적분 source는 `(Qabs − Qescape + QC + QUVC)/(nb H)`이고 work는 `3 kB T eta`다. throughput은 각 source의 절댓값과 work의 절댓값을 사용한다. binding escape와 core/RR/DR escape를 새로운 항으로 중복 가산하지 않는다. 1025-node Simpson 잔차와 513→1025 차이를 구분하며, 저장 cumulative는 trapezoid라고 명시한다.

`t_eval` 없이 BDF를 실행하고 실제 solver accepted nodes를 먼저 보존한다. comparison109, accepted, dense513, dense1025의 배열과 진단·적분 함수·cumulative를 각각 남기며 네 집합 모두 admission을 받는다. 초기 full63 벡터는 기존 Mao nominal에서 정확히 복사하고 refined 초기 벡터와 일치해야 한다. donor z20에서 누적된 nonzero elapsed 좌표와 tau를 유지한다. endpoint는 부동소수점의 z==2 비교 대신 정확한 x==log(7)로 확인한다.

재사용은 현재 source·구성·초기 벡터·기존 입력 hash로 만든 case identity를 요구한다. 모든 필수 출력의 bytes/SHA와 gate 목록을 확인하며, campaign lock은 환경과 preflight binding도 고정한다. `require_preflight`는 현재 runtime identity와 근거 파일의 SHA를 다시 확인하므로 stale review 아래 수정된 소스를 실행할 수 없다. 원래 완료한 ODE를 다시 돌려 dense evidence를 복구하는 경로는 없다.

## 판정의 범위

시간 제한은 RHS, Jacobian, 저장 진단과 최종 완료 경계에서 확인하는 cooperative deadline이다. OS가 임의의 장시간 연산을 강제로 중단한다는 보장은 아니다. 중간 RHS 예외로 solver가 반환하지 못하면 마지막 RHS trial을 그 역할 그대로 기록한다. 이를 accepted node라고 주장하지 않는다.

admission은 보존된 네 표본 집합에 대한 검사다. 내부 Newton trial이나 연속 경로 전체의 양성 보증이 아니다. runtime 작성자의 source-bound Jacobian 점검은 별도 근거이며 이 검토에서 반복하지 않았다. 대수적으로 ledger가 균형을 이뤄도 실제 grey photon spectrum의 recoil/induced closure나 방사선·중력 backreaction이 해결되지는 않는다.

이 드라이버 검토의 새 ODE와 기존 IVP 재실행은 모두 0회다. 물리 상태는 HOLD, production은 NOT_APPROVED, global convergence는 NOT_RUN, REI activation은 false로 유지한다. 기계 판독 근거는 [REVIEW.json](REVIEW.json)에 있다.
