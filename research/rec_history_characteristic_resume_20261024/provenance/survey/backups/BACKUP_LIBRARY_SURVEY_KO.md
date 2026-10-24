# REC 다음 단위 R1 — 백업·Library 조사

관측 기준 시각: 2026-10-24 02:39:27 UTC. 이 보고서는 read-only 인수 조사다. 과학 실행, IVP, 과거 campaign 재실행, 외부 쓰기는 모두 0이다. **ADM01의 PARTIAL_AFTER_WORKSPACE_RESET와 원 primary 상세 행 소실 상태를 그대로 보존한다.**

## 판정에 바로 쓸 결과

1. ADM01 final ZIP과 outer companion receipt의 Dropbox ID·revision·size는 이전 검증값과 일치한다. final ZIP 전체 byte SHA/CRC 85개/manifest 84개 검증은 이미 완료된 증거를 재사용했으며, 큰 ZIP을 다시 다운로드하지 않았다.
2. 별도 **REC-HISTORY-02의 Stage A 원본**을 다시 확보했다. ZIP 686,043 bytes, SHA `ca748e1e9e3ee1c9fe2c82418221f0230998b97223b38d91c558ae3924a077da`; 현재 단일 GET의 크기·SHA·Dropbox content hash, CRC 15개, payload 14/14 size·SHA가 모두 PASS다.
3. 이 Stage A에는 **retarded Bianchi I characteristic + Wien 기준 보정 + 고정 셀 tangent + 조건부 오차 전파**의 계약이 이미 있다. 그 범위를 새로운 미소유 작업으로 취급하면 안 된다. 계약 작성자/현재 active owner ID는 없으며, 이후 사용 예산도 이 snapshot으로는 알 수 없다.
4. 명시한 검색 범위에서 새로운 동일 매개변수 history·독립 reference/endpoint uncertainty·정당화된 curvature bound는 찾지 못했다. 기존 실제 h2/h4 후보가 없다는 뜻이 아니며, 후보의 source/frame/query-domain 판정을 이번 조사에서 다시 계산하지 않았다.
5. Drive의 중단된 ADM01 final ZIP은 기존 folder·root listing·정확한 이름 검색에서 나타나지 않았다. 따라서 **과거 interrupted/no ACK의 UNKNOWN**을 유지한다. 모든 위치에서 부재한다는 결론이나 재업로드는 하지 않았다.
6. 새로 읽은 Drive BASS B3a 문서는 검토 전 four-force 참조 구현 자료다. 실제 REC history 결합과 독립 모델 검토는 NOT_RUN으로 적혀 있으므로, interpolation 인증자료로 승격하지 않는다.

## 최신 Dropbox 객체와 검증 수준

| 역할 | 실제 ID | revision | 크기 | server modified UTC |
|---|---|---|---:|---|
| ADM01 final ZIP | id:BSpOijBcT10AAAAAAD_6xg | 65e8b9f775c200af03d47 | 613327 | 2026-10-24T01:00:29Z |
| ADM01 outer receipt | id:BSpOijBcT10AAAAAAD_8LA | 65e8c566dbb700af03d47 | 13572 | 2026-10-24T01:51:38Z |
| HISTORY02 Stage A | id:BSpOijBcT10AAAAAAD_6tw | 65e88d1e896280af03d47 | 686043 | 2026-10-23T21:39:50Z |

현재 값은 [CURRENT_DROPBOX_IDENTITIES.json](CURRENT_DROPBOX_IDENTITIES.json)에 있다. 단순 listing, 현재 metadata, 과거 upload ACK, 전체 byte readback은 서로 다른 수준으로 유지한다. final ZIP의 현재 metadata 일치는 과거 whole-byte 증거 재사용 근거이고, outer receipt의 원 remote whole-byte GET은 여전히 NOT_RUN이다.

## HISTORY02의 정확한 예약 범위

원본은 [REC_HISTORY02_STAGE_A_20261024.zip](history02_stage_a/REC_HISTORY02_STAGE_A_20261024.zip), 추출된 계약은 [FROZEN_CONTRACT.md](history02_stage_a/extracted/rec_bianchi/research/rec_history_characteristic_20261024/FROZEN_CONTRACT.md)이다. 모든 원본 payload는 변경하지 않았다. [STAGE_PROGRESS.json](history02_stage_a/extracted/rec_bianchi/research/rec_history_characteristic_20261024/STAGE_PROGRESS.json)은 2026-10-23T21:39:14.733816Z에 R1–R5/C1–C4를 complete_contract_or_derivation, R6–R10/C5–C10을 pending으로 기록한다. 별도 LOOP 파일은 없고 단계 기록이 이 파일에 있다. 원 progress의 STAGE_A_PENDING은 패키지 생성 전 상태이며, 현재 실제 원본 존재/byte 확인은 외부 인수 receipt로 추가한다.

정의는 metric `(-,+,+,+)`, `eta=ln(a)`, normal-frame propagation direction `n=p/|p|`다. 관측방향 `-n`, 문헌의 conformal eta와 구분한다. 선택한 exact Bianchi I subclass는 `beta_i=b_i eta+const`, `sum b_i=0`, `a_i=1+b_i>0`이다.

```text
Delta = eta_t - eta_s
g_i = n_ti exp(a_i Delta)
D = ||g||
n_si = g_i/D
F(Delta) = ln D - Lambda = 0
Lambda = ln(E_s/E_t)
F' = sum a_i n_si^2 = q_s
Lambda/a_max <= Delta <= Lambda/a_min
```

LRS 관례 `beta=(-B,-B,2B)`는 기존 C9 Killing map을 재사용한다. generic Bianchi의 frame/curvature characteristic은 인터페이스 명세이고 새 cosmological history 적분은 범위에 없다.

Native HyRec의 저장량이 절대 occupation이 아닌 `d=f-W`, `W(x)=exp(-x)`이므로 계약은 다음 연결을 포함한다.

```text
d_in = H(eta_s,n_s) + W(x_s) - W(x_t)
T_s = T_t exp(Delta)
x_s = x_t exp(Lambda-Delta)
d_out = d_in + (xr_p/(3x1s)-d_in) [-expm1(-tau/q_t)]
q_t = sum a_i n_ti^2
```

이 온도는 선택된 reference owner이며 새 gas-temperature 해가 아니다. history 표현 `c0+v·n+n^T Q n`은 선언된 degree≤2 synthetic/control 인터페이스다. 실제 각도 spectrum의 저차 정확성을 주장하지 않는다. same-event number/energy ledger는 HISTORY01을 그대로 재사용하고 사건 사이 redshift work는 전파/장 소유자에게 남긴다.

계약의 조건부 bound는 root residual과 입력된 history uncertainty를 분리한다.

```text
eps_Delta <= eps_F/a_min
e_in <= e_H + [K_eta + K_n(a_max-a_min)/2 + 1/e] eps_Delta
        + e_reference_arithmetic
e_out <= exp(-tau/q_t) e_in
```

`e_H`의 실제 M2·endpoint·angular uncertainty는 외부에서 인수해야 한다. 유한 h4 배열에서 curvature bound를 추론하지 않는다고 명시되어 있다.

### 원본 source와 남은 구현

archive TOC에는 계약·예산·단계·provenance·h4 입력과 기존 donor Python 세 파일이 있다. **HISTORY02 신규 adapter, primary raw, review 결과는 이 archive에 없다.** 이는 archive 범위의 관측이며 다른 미검색 저장소/활성 세션 부재를 뜻하지 않는다.

| source | Git blob | SHA256 |
|---|---|---|
| axisymmetric_batched.py | 96a4769d46635ee33fc1f408d6645680383f842f | 68ba14db113cd376683cdeabeea141aaa53ce311daffcc3677f94ac48a1c47bc |
| axisymmetric_bianchi_i.py | eaabdc4fac25bab3f2f65e4f59ec360b76af8238 | 5296880dbf2d1b00e2810c969e6a0406b46f10acff04c794e8f718aff5813955 |
| characteristic_angular.py | c6676ee112a892bb558ab8aab670481617201c7f | 1fa89cdf0b2d0568f395444dc8212d325926572057950e55a52f8a0a469dcc53 |
| h4_numpy16_python_continuation.npz | f3d1d58563ea24bc34c977efc67106e1936cd5cc | b2489168155ad1a18a887a880eb0ca90376be5506c3c61d6bf06e9e70007c54c |

h4 입력은 119349 bytes이며 계약은 virtual311×24, Lyman3×24, states17, steps16, h=2.1225e-5를 기록한다. 이번에는 배열을 수치 실행하지 않고 원본 byte identity와 계약을 읽었다.

예산 snapshot은 60 CPU s/180 wall s, 1 thread, 1 GiB이며 primary40/90, review10/30, repair10/60으로 분할한다. `executions=[]`, local spent0은 **체크포인트 당시 기록**이다. `WOLFRAM_SYMBOLIC.json`에는 별도로 두 대수 항등식의 `{0,0}` 결과와 timeConstraint20s가 있고 실측 CPU/wall은 없다. 따라서 이 snapshot의0을 모든 과거 계산의0이나 현재 미사용 잔여60/180으로 해석하지 않는다.

계획된 finite control 상한은 retarded96, tangent24, Wien32, composite24, actual-prefix24, invalid24, envelope24와 deliberate defects3이다. 구현·유한 검증·PNG2개·독립 검토·후속 전달이 남아 있는 계약이다. REI-L0의 다른 thread 경로/예산 예약은 명시적이며, HISTORY02 자신의 현재 active owner는 파일에 없다. Parent는 이 계약을 유지하며 complementary uncertainty/certificate 단위를 선택하거나 실제 owner 상태를 먼저 조정할 수 있다.

## 검색 coverage와 한계

Dropbox는 `/bianchi/rec_bianchi/20261016`의 직접98개·재귀138개를 실제 열거했고 `has_more=false`였다. 관련 global title query도 수행했다. 다만 `CHARACTERISTIC` 검색은100개 반환이며 날짜 filter를 넣어도 이전 날짜 항목을 반환했다. 이 응답을 날짜 filter가 완전히 적용되었다는 근거로 사용하지 않는다. 해당 폴더의 완전 열거와 각 항목의 실제 수정시각이 더 강한 범위 증거다.

Drive는 기존 folder `1Xo_yT9v4WQfPvv-GJdYJ2O2CD5s6bJ1k`의16개, root의 top_k500 안에서310개, ADM01 final ZIP 정확한 이름과 HISTORY02 변형 이름, 최근 history/recombination/characteristic/Wien 검색을 확인했다. 이 listing 도구는 continuation을 노출하지 않는다. 모든 Drive 파일의 전체 내용을 전수 검사한 것은 아니다.

Library는 Oct23 이후115개를 next_cursor=null까지 열거했고, 최근 일반 이름의 md/json18개에 relevant text find를 했다. 최신 이름 검색 REC_HISTORY02/REC-HISTORY-02/CHARACTERISTIC/WIEN은0개였다. 오래된 REC_HISTORY/REC_R3/REC_HYREC 제목 후보50개도 확인했다. 선택된 LINE02 handoff와 receipt는 전체 추출 텍스트를 읽었다. supplied attachments는 Library로 읽지 않았다.

LINE02 receipt의 재조립된 추출 텍스트 SHA는 기존 pinned 원 receipt와 같은 `140ce4227c907c2f4ae9c21989f98b9a5e6992082fb0307c8ff9dbaa51a1a0ad`다. 이는 저장된 텍스트의 원 receipt byte 일치를 확인하며, Drive whole-byte 확인으로 바꾸어 세지 않는다.

GitHub 전체 branch/PR·중앙 DAG·PersonalContext는 parent 담당이다. 이 자식 조사로 모든 대화 전문이나 모든 repo tree를 읽었다고 주장하지 않는다.

## BASS B3a 별도 관측

[보존된 Drive 텍스트](BASS_B3A_PRE_REVIEW_DRIVE_TEXT.txt)의 실제 ID는 `18hTBCoLnlKcOd1AlM48BkF6dyga0n7Xj-BiONxMAMlU`, 수정시각은 2026-10-23T22:11:51.573Z다. 문서는 cold elastic Thomson에 대한 rest-electron density와 four-force 연결, emission의 `alpha=-u·Q` 항을 구분한다. WL21 testgroups, covariance12, rest-frame6은 문서가 보고한 기존 결과다. 독립 모델 심사, BASS native adapter, 실제 REC history coupling은 NOT_RUN이다. 현재 텍스트를 읽었으며 과학 재현이나 source export byte identity 검증은 하지 않았다.

## 저장된 근거와 자원

[BACKUP_LIBRARY_SURVEY.json](BACKUP_LIBRARY_SURVEY.json)에 전체 결론·검색 조건·미해결 blocker를 구조화했다. 세 provider의 normalized metadata는 별도 inventory 파일에 있으며 계정/email/임시 다운로드 URL은 제외했다.

HISTORY02 단일 GET·hash·안전 추출 I/O는 CPU0.025487510s/wall0.355092277s, manifest hash I/O는 CPU0.002990134s/wall0.002990334s다. Provider 대기·문서 읽기·이 보고서 작성은 이 수치에 포함되지 않는다. 과학 budget은 실행하지 않았다.

