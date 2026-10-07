# REC-Bianchi PB02 — 이론·코딩 연구 루프 실행 결과

2026-10-04. **순수 수소 one-temperature Peebles 참조 모듈을 실제 REC Rust crate에 추가하고, FLRW Peebles 점별 복원을 독립 실행 대조까지 완료했다.** REI의 재이온화 모형과 연결할 API·후속 작업을 별도 전달한다. REI production call-site 및 전체 재결합 history의 완료를 뜻하지 않는다.

## 네 스레드의 현재 위치

| 스레드 | 이번 검토에서 확인한 최신 진전 | REC 기준선에 주는 결론 |
|---|---|---|
| rei_bianchi | F00–F03 구현, 기존 FT06 저장 history, PB01·FLRW01 계약. 현재 FLRW02/F04 우선 | REC 참조 모듈은 사용 가능한 별도 lane. 현재 REI 우선순위를 바꾸지 않음 |
| bass_cr | Peebles shell 환원과 정확한 closure defect | 유도 재사용. CR-off인 순수 H 기준선의 선행조건 아님 |
| WU088_HH | 외부율·도함수·remainder·incoming moment, 저장 FT06 source-only 후처리 | HH-F1 application/F07 대기. HH-on 해의 감도와 혼동하지 않음 |
| BASS_HE | KF96 별도 source, RCT event/chemical ledger와 실제 제외 결속 | RCT를 제외하는 현재 순수 H 기준선의 선행조건 아님 |

최초 관측 branch/commit/blob 및 원문은 `survey/`에 있다. 게시 중 동시 진행된 REI 변경은 `publication/REI_RECEIVER_HANDOFF_KO.md`와 후속 갱신 기록에 반영한다. 이전 FT06에는 이미 제한된 prescribed-expansion·Case-A history가 있다. 이번 결과를 최초의 모든 종류의 history라고 부르지 않는다.

## 이론 루프에서 닫은 것

`theory_reference/PB02_SOURCE_BOUND_THEORY_KO.md`와 JSON 계약이 정의·유도·출처를 담는다. 순수 H에서 x_e=x_p, x_1+x_p+x_2=1, x_2s=x_2/4, x_2p=3x_2/4다. β_P와 β_shell=β_P/4, per-2p escape Rα, D=(Λ+3Rα)/4를 분리했다. 동일한 순간 rates에서 retained RHS와 collapsed-inverse Peebles RHS의 차이는 정확히

\[
\dot x_p^{\rm ret}-\dot x_p^{\rm P}
=-(1-C)\dot x_2-C\beta_P e^{-E_{21}/k_BT_r}x_2.
\]

실제 ground fraction으로 Rα를 조립하면 x2를 무시한 standard model과 C도 달라진다. 위 식은 양쪽에서 같은 C를 쓸 때의 closure defect이며, 완전한 두 모형 비교에는 C의 변화도 포함해야 한다.

독립 검토에서 finite retained-shell 평형과 collapsed Saha의 혼동을 발견해 수정했다. S=β_P B/(n_H α_B), B=exp(−E21/kT)일 때 retained 평형은 x_p²/(1−x_p)=S/(1+4B), collapsed 평형은 S다. synthetic B=0.2 시험이 그 차이를 실제 검출한다.

조건부 Bianchi 각도 연구도 수행했다. 등방 선원·populations, 비틸트, 고정 H와 n1, 국소 Sobolev closure, 모든 방향 h(n)=H+σ_ij n_i n_j>0에서 P(h)=h/a_S[1−exp(−a_S/h)]는 오목하다. 따라서 평균 탈출확률은 등방값 이하이고,

\[
\langle P\rangle-P(H)=-\frac{\tau_0e^{-\tau_0}}{15H^2}\operatorname{Tr}\sigma^2+O(\|\sigma\|^3/H^3).
\]

두꺼운 극한에서는 직접 shear 항의 각도 평균이 상쇄되어 평균 H만 남는다. 이 제한된 모형 내 결과를 일반 Bianchi 복사장·우주론 재결합 효과로 승격하지 않는다. 6축 평균은 이번 trace-free quadrupole의 2차 모멘트를 2.5배 과대평가한다.

## 코딩 루프와 실제 실행

기존 `rec_bianchi`의 `rust/rec_microphysics`에 `hydrogen_peebles` 모듈, 테스트, CSV probe를 추가했다. 기존 He/frame/screen 구현은 보존했다. Rust 1.94.1 / edition 2024이며 새 dependency는 없다.

| 검증 | 실제 결과 | 의미 |
|---|---:|---|
| 원본 crate의 새 API import | E0432 / exit 101 | 구현 공백 확인 |
| 새 H targeted tests | 20 PASS | 통계인자·보존·Saha·domain·부호·defect |
| 전체 crate regression | 108 PASS | 기존 88 + 신규 20 |
| 원저자 HYREC C ↔ Rust | 384점 PASS | 동일 PEEBLES/Fudge=1/one-T의 계수·RHS |
| 독립 Decimal 70자리 event oracle | 24점 PASS | retained conservation·defect·reduced RHS |
| 조건부 Sobolev 각도 적분 | 42점 / 95 checks PASS | Jensen 부호·2차 전개·각도 수렴 |

384점 대조에서 β_P 최대 상대차 1.79e−14, RHS 최대 flux-scaled 차 1.06e−14다. 미리 정한 허용치는 2e−12다. net RHS가 0에 가까울 때 정·역반응의 절댓값 합으로 정규화하여 cancellation을 처리한다. 24점 Decimal은 Rust 구현을 불러 계산하지 않고 별도 event stoichiometry를 사용한다. 이 값들은 numerical parity이며 원자 fit의 물리 오차 또는 구간 전체의 증명된 상계가 아니다.

원저자 HYREC-2 commit `09e8243d0e08edd3603a94dfbc445ae06cafe139`의 C 함수 `rec_TLA_dxHIIdlna`를 실제 컴파일해 사용했다. 전체 HYREC FULL/SWIFT history 실행은 아니다. 공개 원문에서 명시적 라이선스를 확인하지 못했으므로 upstream C는 패킷에 재배포하지 않고, exact hashes·수식 출처·독립 caller·검증 후 fetch/build 스크립트를 제공한다. 원래 목표인 외부 연구 우선 재사용을 유지하되 공개 열람과 무조건 재배포를 혼동하지 않는다.

복구한 Rust 실행환경의 초기 파일 불완전 추출과 C의 strict-C11 빌드 실패, GNU11로의 수정, 선택적 CAS 도구 부재도 evidence/review에 남겼다. formatter는 rustfmt 부재로 미실행이다. 실패를 삭제하거나 성공으로 기록하지 않았다.

## 다음 호출 순서와 두 연구 lane

1. `publication/REI_RECEIVER_TASKS.json`의 최신 우선순위를 따른다. REI 주흐름은 FLRW02/F04다. Peebles lane 재개 시 새 pure-H reference model ID와 source pin을 받고 실제 REI call-site에서 입력·output·실패 분류를 결속한다.
2. cosmology·초기조건·z 범위·thermal bath·solver·tolerance를 먼저 동결한 뒤 matched FLRW x_e(z)를 계산한다. pointwise parity를 history 수렴으로 대신하지 않는다.
3. 제한된 Bianchi 비교는 그 모형의 radiation/population closure가 승인된 뒤 진행한다. 이번 각도 그림은 그 전 단계의 local conditional diagnostic이다.
4. 원래 CR/HH/He 정밀 원자 연구, REC E1C native/COM, selected-He T4/Gate-I는 독립 확장 lane으로 보존한다. source/domain/application trigger가 생길 때 재개하며 이번 pure-H benchmark 완료를 그 gate의 통과로 전파하지 않는다.

기존 strict local error <2e−4, public width <2e−3 및 실패 구간 [160,161]의 2.124505e−4 기록을 보존한다. 무거운 스캔·Einstein-solved EoR·Δτ inference·전체 line transfer·He consumer admission은 실행/승인하지 않았다.

## 파일 안내

- `theory_reference/`: 유도, source lock, source fixtures, machine-readable contract.
- `coding/`: native 변경, 원저자 C caller, 재현 지침과 로그.
- `research/`: 사전 계획, 독립 parity와 각도 연구 실행기.
- `evidence/`: CSV, JSON, 그림, 환경 복구·원문 C 빌드 기록.
- `review/`: 독립 검토와 수정/판정.
- `survey/`: 네 스레드 및 REC snapshot/원문/identity.
- `publication/`: REC→REI handoff, low-cost 실행 DAG, 게시 영수증.

GitHub에는 실제 native source 위치와 이 연구 패킷의 문서를 함께 게시한다. Drive와 Dropbox에는 동일한 checksum manifest를 가진 core ZIP 및 읽기 쉬운 요약·handoff를 저장한다. 백업 판정은 업로드 ACK와 원격 파일 크기/metadata 확인 범위를 명시한다. 새 Dropbox 폴더는 `/BASS_DERIVATION_DOSSIERS_20260912/REC_BIANCHI_PB02_20261004_v1`이며, 되돌릴 때 이 새 폴더만 삭제하면 된다.
