# 원본 함수 실행의 부분 완료와 정확한 BASS 인증 blocker

최종 연구 상태: `PARTIAL_REC_API_AND_MATH_VERIFIED_BASS_AUTH_BLOCKED`.
전체 `PASS_BOUNDED_ORIGINAL_MODEB_RUNTIME_DIAGNOSTIC`은 성립하지 않는다.
`NO_PASS_REC_PHYSICAL_SPLIT`을 유지한다.

## 1. 수행 위치와 실제 원격 실행

이번 작업은 현재 대화가 직접 GitHub runner를 운영했다. 작업 스레드/local Codex 인계나 사용자 로컬 checkout 변경은 없다. 대화의 container/Python은 각각 한 번 process 시작 전 ClientError, WolframContext는 평가 전HTTP404였다. 새 실행 경로를 실제로 사용했으므로 모든 runtime이 막혔다고 묶어서 말하지 않는다.

PR: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/73
branch: research/rec-modeb-original-runtime-20260906-r1
부모 PR72: 823cf1c25abda5343be6020bbf0b5bedb131fc3e
부모 tree: 3f01f944ab8a89582b324e9fae37c760f893a80b

| 단계 | commit | tree | 실제 결과 |
|---|---|---|---|
| 최초 원본 전체 호출 소스 | f6d857afd15480e5b3a37ac99fac94d066d78e3d | e287e61a54b3d266e892073cf5a27a973785d55d | BASS Git fetch 인증 실패, 계산0 |
| 독립 REC 부분집합 소스 | 66dd777ed4d40e2cab6607b9ec7766d9ea02810f | c0cb15512fe219be8eab060279ca756b8c160335 | 실제 REC 원본 API 및 대수6개 통과 |

두 commit은 직접 부모로 이어진다. 이 closeout은 두 번째 실행 뒤 추가된 결과 문서다. 문서 child를 계산한 commit으로 부르지 않는다. 첫 실패를 expected RED 또는 후속 GREEN으로 재분류하지 않는다. 둘은 서로 다른 실행 범위다.

## 2. 최초 실패의 원인과 보안 경계

[run34022055292 / job101456308151](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34022055292/job/101456308151)의 전체 로그를 읽었다. runner/REC checkout/Python 설치는 성공했다. 이후 인증 없는 BASS fetch가 다음으로 실패했다.

```text
fatal: could not read Username for 'https://github.com': No such device or address
exit 128
```

직접 GitHub 저장소 metadata readback에서 BASS는 private로 확인됐다. 초기 workflow 작성 시 이 실행기 접근 조건을 확인하지 않은 것은 실행 설정 결함이었다. ChatGPT connector가 가진 읽기 권한이 REC의 Actions 환경에 자동 전달되는 것은 아니다. 대화의 GitHub 계정 권한 부재, 수식 오류, Rust 실패로 분류하지 않는다.

같은 인증 없는 fetch는 다시 실행하지 않았다. 비공개 원본을 공개 REC에 복제하거나, 토큰을 로그/파일/대화에 노출하거나, BASS 저장소·가시성을 변경하지 않았다. 최초 runner/checker/실패 기록을 보존했고 원본 BASS 검사의 성공 조건을 완화하지 않았다.

BASS 입력과 독립인 REC 검산은 별도 read-only workflow로 한 번 실행했다. 실패한 원본 workflow에는 재실행이나 PASS 표시를 하지 않는다. 부분 checker에는 original_bass_radial_calls=0, original_modeb_calls=0, full_original_diagnostic_pass=false가 고정되어 있다.

## 3. 실제 완료된 여섯 검사

[run34022456414 / job101457396115](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34022456414/job/101457396115)을 끝까지 읽었다. checkout과 workflow SHA는 모두 `66dd777ed4d40e2cab6607b9ec7766d9ea02810f`, trigger=push다.

실제 명령:

```bash
"$RUNNER_TEMP/rec-available-venv/bin/python" -B \
  docs/research/rec_modeb_original_runtime/check_rec_available.py \
  --out "$RUNNER_TEMP/rec-available"
```

실행 결과: `Ran 6 tests in 0.052s`, failures=0, errors=0, skips=0, exit0. 독립된 물리 정리 여섯 개 또는 원래 계획한8개 중6개라는 집계가 아니라 실제 unittest 메서드6개다. 일부 메서드의 유한 JVP 사례·기호 잔차는 내부 검사로 따로 기록한다.

1. Fraction source/JVP와 SymPy 연쇄법칙: C=-3/4, dC=31/16, G=-3/32, dG=133/512, 일반 미분식 잔차0.
2. 변경 없는 PhysicalTwoPhotonRamanBin.net_action/paired_rates 호출. 정확한 Planck 입력에서 net0. 독립 폐형식1/sqrt15를 입력했을 때 net0.028175416344814574 H^-1 s^-1. 이 입력은 Rust 출력이 아니다.
3. 기존 paired.jvp의 지정된 세 상태 방향을80자리 기준과 비교. 최대 관측 잔차3.469446951953614e-18. 한 JVP는 tracked 미분-3/8, 다른 두 값은 결과 JSON에 보존.
4. 변경 없는 COMSourceDepositionPlan.apply 호출. 제조 분배의 occupation action은[0.04695902724135762,0.004695902724135762] s^-1. 광자수/n_H=0.05635083268962915, 에너지/(n_H E0)=0.08452624903444372. 원자+광자 에너지0이지만 비영점 가짜 변화는 남는다. hull 밖 에너지를 주장하는 제조 map은 ValueError로 거부됨.
5. 같은 물리 에너지의 q=(1,4), Jacobian 행합5/4, 로그 stencil 에너지5/2, 기하 Jacobian 상쇄를 정확 대수로 확인. BASS geometry 실행은 아님.
6. 조건부 Bose 변수 chi=log((1+f)/f)의 반응 affinity 항등식을 SymPy로 확인하고 제조 상태3개의80자리 엔트로피 생성 부호를 검사. source/reconstruction production 구현을 바꾸지 않음.

두 원본 REC blob은 실행 전후 실제 파일바이트로 검증했다.

```text
hyrec_two_photon_raman.py 26ddc41e24fadf0bdd19f1924e1a429d602d9c19
com_source_deposition.py a3662cf399f14b7148d880266825be12baf934a0
```

실제 module __file__은 둘 다 해당 checkout의 src 아래였고 초기/사후 Git status는 빈 문자열이었다. 현재 대화 컨테이너에서 재해시한 것이 아니라 실행기의 결과와 원본 로그에서 확인한 것이다.

환경: Python3.12.14, NumPy2.2.6, SciPy1.15.3, SymPy1.14.0, mpmath1.3.0. 사용자 로컬 설치를 수정하지 않았고 GitHub 임시 venv만 생성했다.

## 4. 수학적 해석과 허용 범위

실제 REC 쌍식에 제공한 값은 이전에 유도한 로그 읽기의 폐형식이다. 그러므로 이번 결과는 REC가 해당 값을 받으면 예상한 비영점률을 반환한다는 구현 증거이고, BASS가 실제로 그 값을 읽는다는 구현 증거는 아니다.

고립된 두 광자 반응의 같은 사건률 Gamma에 대해 각 분배 열의 합이1이면

sum_i mu_i C_i = 2 n_H Gamma.

따라서 Gamma!=0인 경우 number-conservative map만 바꿔 C 전체를0으로 만들 수 없다. 에너지 장부를 맞추어도 상세균형 오차를 고칠 수 없다는 기존 유도와 실제 COM 결과가 일치한다. 이것을 실제 물리 map/source의 오류로 승격하지 않는다.

조건부 entropy 연구는 동일한 비음수 에너지 재현 분율을 chi 읽기와 number 분배에 사용하고, 단위 축퇴도 원자 두 상태와 고정 measure/density를 가정한다. affinity=log(F/R)이면 생성률은 (F-R)log(F/R)>=0다. SymPy로 그 affinity 항등식을 확인했으며, 제조 nonthermal 두 경우에서 각각0.19018666951100566815와0.00940241820615037182, thermal control에서0이었다. 일반 entropy 불평등의 증명은 단조 log의 대수에 근거하고, 유한 세 사례가 일반 정리의 증명은 아니다.

문헌 탐색: SciSpace 검색과 원 논문 arXiv:1009.2748 초록을 확인했다. 해당 보존·entropy·Bose 정상상태 방법론은 이 분리의 배경이지 이번 REC 코드나 chi 재구성의 인증이 아니다. 전체 논문을 새로 읽었다거나 그 알고리즘을 채택했다고 주장하지 않는다.

## 5. 증거 보존

[원본 결과 artifact9985952784](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34022456414/artifacts/9985952784): RESULT.json, unittest.log, SHA256SUMS의3개 파일, ZIP2348bytes.
GitHub upload log와 artifact metadata가 같은 SHA256을 보고한다.

`e7697d71fdd7bda506afc285f7bfde91c4ff36eac2161544046113ec6542e375`

보존 만료 metadata는2026-10-06T08:39:47Z다. 현재 대화에서 ZIP을 다운받아 재해시하지 않았다. 영구 Git 문서인 OBSERVED_RESULT.json은 로그에서 읽은 값의 구조화된 사본이며 원본 ZIP/RESULT와 byte identity를 주장하지 않는다. 원본 source/checker와 오류 발생 workflow도 Git에 남아 있다.

새 그림은0개, 시각 검토도0회다. 전체 원본 실행 뒤에 만들 예정이던 order8 그림을 REC-only 결과로 대체하지 않았다. 같은 작성자가 수학/구현 범위를 점검했으며 제3자 독립 감사는 수행하지 않았다.

## 6. 별도의 일반 CI

같은 source의 [일반 PR run34022458746 / job101457402658](https://github.com/cosmosapjw-quantum/rec_bianchi/actions/runs/34022458746/job/101457402658) 로그도 읽었다. 실제 checkout은 PR 검사용 merge ref `901fb720803b42e0b70fc4eefb2f57118457d860`이며 실제 병합을 뜻하지 않는다. 설치/import smoke/HyRec binary-hash 정책은 통과, quick verifier는 feature_base `e6b64e0df25d0b1db7cf8b776866db0afc14721e` 이후 누적 공백 검사에서 실패했다. 첫 경로는 기존 MUTANT_drop_density_jvp.log:6이다. 전체 pytest는 skipped다.

실패 목록의7개 경로는 기존 evidence/README/문헌기록이며 이번 추가 경로는 그 목록에 없다. 이 branch는 기존 파일을 수정하지 않았으며 전체 merge tree를 이번에 별도로 복원한 것은 아니다. 일반 CI 전체PASS를 주장하거나 이 연구에서 과거 공백을 수정하지 않는다. 이후 결과문서 child에 발생하는 자동 CI는 별도 실행이며 같은 원인이라고 미리 단정하지 않는다.

## 7. 다음 한 작업

미완료는 BASS의 원본 radial.rs와 ModeBState를 승인된 읽기 인증이 연결된 실행 환경에서 실제 호출하는 것 하나다. 현재 작성한 check_original.py와 driver의 고정 expected/tolerance를 유지한다. 별도 GitHub App/최소 읽기 자격증명 또는 이미 접근 권한이 있는 runner가 필요하며, 비밀 값을 대화나 저장소 파일에 넣지 않는다. BASS의 private 상태를 public으로 바꾸지 않는다.

기존 REC 부분 결과는 재실행을 필수로 만들지 않고 재사용할 수 있다. source/math 연구를 새 계획으로 되돌리거나, 미실행 BASS 항목을 완료로 바꾸지 않는다. BASS 생산 코드, 물리 B·mu·실제 state 입력·provider·moving-map/event·accepted-state·merge/ready는 미수행이다.
