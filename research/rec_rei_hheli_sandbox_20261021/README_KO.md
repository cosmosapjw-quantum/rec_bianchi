# REC → REI H/He/Li sandbox pilot

이 단위는 PR118 다음의 **최적화 코딩 → 물리 → 결합 코딩** 연구 루프다. 새 125-case sweep과 별도 opacity-off control 1개를 이 샌드박스에서 z=20→2까지 모두 완료했다. 각 case는 62상태와 193개 저장 시각을 갖는다. 실제 결과와 한 명령 실행 방법은 [REPORT_KO.md](REPORT_KO.md)에 있다.

게시: [REC PR119](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/119), branch `research/rec-rei-hheli-sandbox-20261021`. 과학 모형은 아래의 유한 preliminary 계약이며 완전한 thermal/radiative EoR 폐쇄가 아니다.

## 선택한 다음 단계

1. 기존 tangent-only NCP 실행: 이미 준비되어 있으나 이번 요청의 H/He/Li 범위를 충족하지 않는다.
2. 완전 열·복사·광핵반응 폐쇄: isotope별 에너지 모멘트와 일부 광단면/반응 계수 의존성이 아직 남는다.
3. **선택:** 기존 canonical FV Einstein–Boltzmann 방정식을 재사용하고, 21개 핵종·전하 상태의 실제 광이온화·재결합 네트워크를 동적으로 결합한 sandbox preliminary pilot.

## 유한 계약

- non-tilted LRS Bianchi I; 평균 redshift `z=20 → 2`; 독립변수 `x=ln(a/a_ref)`.
- 핵종 `n, 1H, D, T, 3He, 4He, 6Li, 7Li`. 전하 `0..Z` 전부, 총 21개 상태. 전자밀도는 전하중성으로 계산한다. 그림에 빠진 Li IV와 6Li를 포함한다.
- isotope electronic equality는 명시적 근사다. 원생 동위원소별 원자율이라는 주장은 하지 않는다.
- 유지하는 원자 과정은 광이온화·RR·DR. 낮은 온도의 CI를 source 밖으로 외삽하지 않는다. 이 유한 과정 선택은 CI 생략 오차가 작다는 인증이 아니다.
- 원자율 정의역 안의 외부 지정 `T(z) >= 100 K`, 외부 지정 UV장을 사용한다. 완전 냉각/가열·복사 수송을 닫은 EoR 예측이 아니다. 필요한 순외부 에너지 공급은 별도 장부로 진단한다.
- 원자망의 실제 `n_e`가 CMB photon Thomson 항에 들어간다. neutrino에는 Thomson 항이 없다.
- 바리온은 공통 온도의 등방 이상기체로 `pi_b=0`. 별도 collisionless 비바리온 물질이 `pi_m`을 공급한다. `pi_r=pi_gamma+pi_nu`; 지정한 등방 UV의 비등방 응력은 0이다.
- thermal/ionization/UV 에너지는 test-fluid 근사로 Einstein dust budget에 되먹이지 않는다. 실제 에너지 비를 저장한다. 에너지 모멘트를 RR number rate에서 임의로 만들지 않는다.
- `sigma_ab=diag(-s,-s,2s)`, `pi_ab=diag(-p,-p,2p)`, orthonormal frame, `(-,+,+,+)`. Frobenius `Sigma=sqrt(6)|s|/H`, `Pi_A=sqrt(6) kappa_t |p_A|/H^2`, `kappa_t=8 pi G/c^2` for SI energy-density stresses. Half-contraction 값은 Frobenius/√2다.
- signed matter/radiation을 먼저 합한 후 total norm을 취한다. 상쇄를 유지한다.

## 재사용과 보존

REC116 warm729 축분해, REC117 175 trajectory, PR118 tangent, HE29/U4B 및 다른 완료 결과는 재실행하지 않는다. 새 원자 결합·새 넓은 초기축은 별도의 prospective case identity를 갖는다. 실패·기존 allocation은 삭제하지 않는다.

기존 `Physical HOLD`, `global convergence NOT_RUN`, `production NOT_APPROVED`, REC U5 HOLD 및 `REI_activation=false`는 유지한다. 단계 완료는 이 유한 preliminary 모형의 코드·산출물에 한정된다.

## 진행

Source survey, 최적화 parity, 물리 R1–R10, 결합 코딩 C1–C10, 125+1 실제 계산, 저장 결과·그림 검토를 수행했다. 현재 게시/보존 상태는 `DAG.json`, `stages/`와 PR119 최종 댓글에 있다.

```bash
cd research/rec_rei_hheli_sandbox_20261021
python code/run_all.py --execute --workers auto
```

완료한 125+1은 hash를 확인하고 재사용한다. 저장 요약·그림만 만들려면 `python code/run_all.py`를 쓴다. 정상 결과는 `results/pilot_v2`; `results/pilot`은 최초 JSON 출력 실패의 보존 기록이다. 원 데이터·코드·재현 의존성은 이 폴더 안에 있다. [그림 캡션](figures/CAPTIONS.md), [전체 요약](results/SUMMARY.json), [Codex handoff](CODEX_HANDOFF_KO.md), [다음 스레드 handoff](NEXT_THREAD_HANDOFF_KO.md)를 함께 제공한다.
