# O2/O3 조건부 연구 실행·게시 기록

`PASS_CONDITIONAL_O2_O3_RESEARCH_NOT_PHYSICAL_ADMISSION`

`NO_PASS_REC_PHYSICAL_SPLIT`

## 정확한 실행과 범위

| 역할 | commit | tree |
|---|---|---|
| 고정 PR #65 부모 | e65ae5c211db4e3375e73410a404f0b23da084d4 | e12a4ae4ed17859e4625f80fb0fa86e83a034036 |
| 실제 연구 실행 소스 | c2ee9da5235e0cda6d582f156859801fc082bb34 | 3b2270b6acdeee157d486b432eeab06aa66d7f0d |

이 문서는 위 실행 소스의 문서 전용 자식이다. 이 문서를 포함한 publication commit을 새로 수치 실행했다고 주장하지 않는다. 최종 containing commit/tree는 PR #66의 원격 객체에서 확인한다.

[PR #66](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/66)은 PR #65 branch를 base로 하는 초안이다. 새로운 연구 branch만 사용하며 원본 branch, 생산 코드, 기존 테스트, 원본 표, 과거 증거는 변경하지 않는다. B, mu, 실제 population/packet state, 책임자 모델 선택, provider 상태도 변경하지 않는다.

## 실제 원격 실행

[실행 33950739514 / job 101264895293](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/33950739514/job/101264895293)의 상세 로그를 직접 읽었다. 실제 checkout과 workflow SHA 모두 `c2ee9da5235e0cda6d582f156859801fc082bb34`이다. checkout, 별도 가상환경 설치, 연구 스크립트, SHA256SUMS 확인과 산출물 업로드가 모두 성공했다.

실행 명령의 핵심은 다음과 같다. 출력·패키지 설치는 Git 밖의 RUNNER_TEMP 아래다.

```bash
"$RUNNER_TEMP/rec-o2o3-venv/bin/python" -B \
  docs/research/rec_2s_o2o3_counting_reference/verify_o2o3.py \
  --out "$RUNNER_TEMP/rec-o2o3-result"
```

실제 환경: Python 3.12.14, SymPy 1.14.0, mpmath 1.3.0, Matplotlib 3.10.3. 세 연구 패키지는 workflow에 버전 고정했다. 이 기록은 전이 의존성 전체의 재현 가능한 lock을 주장하지 않는다. 전체 설치 로그는 산출물과 GitHub job log에 남아 있다.

| 검사 | 실제 관측 |
|---|---|
| 기호 항등식 | 14개, 각각 잔차 0 |
| 정확한 유리수 반례 | 지정한 3종 검출 |
| 고정 CSV 진단 | 140개 중심점 × 3개 열적 에너지 = 420개 |
| mpmath 정밀도 | 80자리 |
| 최대 절대 항등식 잔차 | 8.236092143148846269e-84 |
| 새 diff의 공백 검사 | 통과 |
| 실행 전후 worktree | 깨끗함 |
| 원본 C / 생산 모듈 테스트 / deposition / trajectory | 이번 실행 없음 |
| 원본 표 추출·140행 생성 | 반복하지 않음 |
| 과거 테스트를 새 결과에 합산 | 하지 않음 |

14개는 pytest 사례나 독립 물리 모델 14개가 아니라 연구 스크립트의 기호식 14개다. 420개 역시 실제 우주론 상태나 순rate 실행이 아니라 지정된 열적 점유수 항등식의 유한 표본이다. 반례 3종은 잘못된 식에 대한 명시적 비영점 확인이며 생산 코드를 변조해 재실행한 3개 회귀시험은 아니다.

기호 검사 이름:

```text
stimulated_difference
native_Wien_null
full_Planck_null
native_Planck_residual
full_Wien_residual
native_departure
mixed_reference_defect
corrected_reference
full_pair_JVP
inverse_reference_JVP
Wien_reference_JVP
atomic_plus_photon_energy
two_leg_number
wrong_double_energy_defect
```

## 수치 및 대수 결과

흑체 companion과 동일한 lambda, population 조건에서:

```text
Gamma_F - Gamma_N = C*x_u*f_t
Gamma_N = C*d_u - D*d_b^P - D*x_g*(p-u)
```

두 식의 차이를 원본 버그라고 부르지 않는다. 원본 근사와 전체 점유수 쌍식은 서로 다른 모델이다. 기준장을 바꾸는 것은 근사를 제거하는 것과도 다르다.

유리수 합성 예에서 lambda=1 s^-1, u=1/4, v=1/2, x_g=8/9, x_u=1/9다.

| 검산값 | 정확한 결과 |
|---|---:|
| 원본식의 Wien 상태 | 0 |
| 전체 쌍식의 Wien 상태 | 1/18 H^-1 s^-1 |
| 원본식의 Planck 상태 | -2/27 H^-1 s^-1 |
| 전체 쌍식의 Planck 상태 | 0 |
| 기준장 보정 누락의 가짜 source | +2/27 H^-1 s^-1 |

두 광자를 모두 고에너지 위치에 배치하는 잘못된 두 배 처리의 사건당 에너지 오차는 `(2 E_b-E21)`이다. 실제 고정 중심점에서는 전부 양수이며 최소 `79685923023129/500000000000000 eV`, 최대 `5098490723023129/500000000000000 eV`다. 이는 채널 에너지 회계 반례이지 실제 사건률을 선택한 계산이 아니다.

열적 진단은 Planck 점유수에 대해 `f_t/(1+f_t)=exp(-E_t/Theta)`를 확인했다. 이는 전체 정방향 rate를 분모로 한 유도방출 생략량이다. 상세균형 근처 순rate의 상대오차 상한으로 사용하지 않는다.

| Theta (eV) | 140개 중심점의 최소 정방향 비율 | 최대 정방향 비율 |
|---|---:|---:|
| 0.1 | 5.14409361031816597716279523497e-45 | 3.21885317364145010674519185765e-23 |
| 0.3 | 1.72624706969769316401101276776e-15 | 3.18102480506400476899084532828e-8 |
| 1.0 | 0.0000372503953415146863824610267029 | 0.0056333938678881099242376787111 |

## 입력 식별과 불변 경로

```text
CSV Git blob
5303a7b202a91f2c6f4d5242e93c38b12b884eae

CSV SHA-256
02b03c94539548b9d057530b9054187cffef1ad88c1ec25f4932111df1c27d28

실행 스크립트 SHA-256
1e0d6cc4f5d6364996dec6e0011ad10d6895879a62b71467864d58dfb7b06867

부모와 같은 src subtree
c1d59c46a3031d91900dfc48fa5cdf1c06bbe72b

부모와 같은 tests subtree
9951f675e7cb243cbadbfe56e3e5ac87fda85873

부모와 같은 원본 2s 추적 자료 subtree
67d7d641389c45853743f1e8c210039341228bdc
```

위 값은 실제 hosted 스크립트의 출력에서 읽었다. 원본 ZIP을 이번에 다시 해시한 것으로 기록하지 않는다.

## 산출물과 시각 검토 제한

[산출물 9964731570](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/33950739514/artifacts/9964731570)

```text
이름 rec-2s-o2o3-research
파일 수 6
ZIP 크기 71587 bytes
GitHub 표시 ZIP SHA-256
5e3906c6b6a993779235048819a40aa807b2186eff3946cae92bf50eebfd38d3
만료 시각 2026-10-05T06:46:58Z
```

파일은 `RESULT.json`, `FORWARD_FRACTION.csv`, `FORWARD_FRACTION.png`, `FORWARD_FRACTION.svg`, `EXECUTION.log`, `SHA256SUMS`다. 로그가 닫힌 후 workflow가 최종 SHA256SUMS를 다시 만들고 5개 구성 파일을 실제 확인했다. 외부 ZIP digest는 업로드 로그와 GitHub API 값이 일치한다.

연결 도구를 통한 ZIP 다운로드는 성공했으나 로컬 파일 처리 도구가 process 시작 전에 실패했다. 따라서 이 세션에서 ZIP 재해시, 압축 해제, PNG 렌더링 시각 검토는 수행하지 못했다. 그림 생성은 성공했지만 `VISUAL_AUDIT_NOT_PERFORMED`다. 수치/축 의도는 정방향 상대 생략량이며 관측 예측이나 순rate 오차로 읽지 않는다.

연구 프로그램·결정 경계·결과 요약은 이 Git commit 계보에 보존한다. 원시 CSV/PNG/전체 출력 ZIP은 30일 산출물이며, 이 문서만으로 원시 산출물 전체를 영구 Git mirror했다고 주장하지 않는다.

## 별도의 일반 CI

[일반 실행 33950739475 / job 101264895186](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/33950739475/job/101264895186)의 새 상세 로그도 읽었다. 실제 소스는 같은 c2ee9da...다. 설치·committed-tree import·HyRec binary hash policy는 성공했고, `python scripts/verify_repo.py --quick`에서 exit 1, 전체 pytest는 건너뛰었다.

첫 실패는 기존 `artifacts/trajectory/pr05c2c1b2b1e1c_recovery/rec_local01_admission/evidence/MUTANT_drop_density_jvp.log:6`의 trailing whitespace다. 전체 실패 목록은 다음 7개 기존 경로다.

- 위 MUTANT_drop_density_jvp.log
- 같은 rec_local01_admission/preservation_inventory.txt
- docs/bianchi_program/FED_02_FOUR_REPO_SYNC_20260904/README.md
- docs/research/rec_continuous_causal_donor_r1/README.md
- docs/research/rec_source_dual_representation_r2/README.md
- docs/research/rec_source_dual_representation_r2/SCISPACE_LITERATURE_LOCK.md
- research/handoffs/rec_source_r5d_20260903/local_receipts/BASS_REC_SOURCE_R5D_V2_20260904T021026Z/README.md

연구 실행은 기준 부모 대비 새 경로만 추가됐음을 검사했다. 위 기존 파일들은 이번 diff에 없고, 새 연구 경로도 일반 CI의 실패 목록에 없다. 과거 파일을 수정해 숨기지 않았다. 연구 전용 성공과 저장소 전체 검사 실패를 분리한다. 이 문서 자식의 자동 CI는 별도의 실행이며 여기의 상세 원인을 그대로 새 실행 결과로 복사하지 않는다.

## Atlassian 게시와 재확인

REC 결과만 추가했고 실제 재조회에서 다음 내용을 확인했다.

- [BASS-19 댓글 10597](https://cosmosapjw.atlassian.net/browse/BASS-19?focusedCommentId=10597)
- [BASS-26 댓글 10598](https://cosmosapjw.atlassian.net/browse/BASS-26?focusedCommentId=10598)
- [FED-02 footer 28540930](https://cosmosapjw.atlassian.net/wiki/spaces/BA/pages/27492353?focusedCommentId=28540930)

Jira 상태는 In Progress로 유지했다. 공식 dependency와 다른 저장소 snapshot은 변경하지 않았다. Confluence 응답은 Markdown을 이스케이프한 본문으로 다시 제공했지만 의미 내용과 댓글 ID는 일치했다. 별도 페이지 서식 교정은 하지 않았다.

## 최종 범위와 다음 작업

이 연구는 두 모델의 차이, 기준장 변환, 고정 변수 JVP, 스칼라 사건/광자/에너지 장부의 조건부 유도·검산을 완료했다. 같은 작성자의 수학/코드 관점 감사이며 독립 심사 두 명이나 수정 후 독립 인증을 주장하지 않는다.

책임자 선택은 여전히 `owner_model_choice=null`이다. 제안은 원본 HyRec를 동결된 비교 기준으로 보존하고, 비평형 확장에서는 전체 점유수 쌍식과 서로 다른 에너지의 두 광자를 명시적으로 회계하는 것이다. 이 제안을 생산 기본값으로 승인하거나 실제 population/companion 상태를 정하지 않았다.

다음 단일 작업은 이 비교에 근거한 O2/O3 책임자 모델 선택이다. O1 원본 적분 구간, O4 목표 측도, O5 실제 분배 map, O6 각도/이동 미분의 미결정 사항은 그대로 남는다. 수치 어댑터 재작성, 실제 B/mu 선택, provider, BASS 연결, ready/merge는 하지 않았다.
