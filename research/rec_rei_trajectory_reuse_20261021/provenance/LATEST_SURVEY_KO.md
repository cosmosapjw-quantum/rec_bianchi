# REC 기여를 위한 최신 REI/BASS/BASS_CR/HH 조사
## 최종 갱신: 공유 작업공간의 z20→2 완료 반환 발견

초기 Git-only 조사 뒤, backup 담당자가 실제 공유 작업공간에서 최신 unified LaneB 완료를 찾았다. 이 갱신이 아래 초기 continuation 제안을 대체한다. 현재 선택은 **새 ODE 없이 완료된 z20→2 궤적의 anchored-axis residual 분석**이다.

- 읽은 원본: `/workspace/scratch/b7c8740ffe58/rei_unified_20261021/repo/research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021/`.
- B2 STATUS: exit0/CASE_SET_EXHAUSTED,237 unique completed (231 nominal+6 guards),SHA256 `7446b029432cedfbaa3199ec88990790dc98aff177fa2c6d840895241fc318f0`. 2026-10-21 10:43:47 UTC 생성 반환이다.
- B1 component manifest:175 nominal+3 guards,35 nominal source-bound old reuse. SHA256 `c8d57bf81833ee405b8be854166fb58022a960b7fe9e36aa11fa3c6a5ec00e95`.
- B2 manifest SHA256 `4f7e599ad9f082be59cbe2203a8b55b7bd9cb21fec9fde55a41afe53b9444853`.
- 선택175개 모두 RESULT=COMPLETED, raw SHA256=receipt, INPUT config=RESULT config를 실제 읽어 확인했다. 공통153x배열은 모두 정확히 같고 z4 join은 index120, x=ln4.2; 최종 x=ln7이다.
- nominal 축은 S_F=[0,.0003,.001,.003,.01,.03,.1], Pm=[-.0003,-.0001,0,.0001,.0003], Pr=[-.001,-.0003,0,.0003,.001]. 따라서63 support와112 mixed withheld histories를 비교할 수 있다. 모든 shear IC는0 또는 양 방향이므로 음의 초기 shear coverage라고 표현하지 않는다.
- case.reuse.original_case_id가 있으면 그 원ID의 B2 raw를 사용한다. actual float zero로 axis를 선택하지 않고 nominal requested coordinates를 사용한다. 초기 실현 offset은 S<=1.0408340855860843e-17,Pm<=4.472333961502706e-19,Pr<=6.505213034913027e-19이며0으로 덮어쓰지 않는다.
- `S_signed=sqrt(6)*s/H`를 구성한다. 저장Sigma_F는 norm, P_m/P_r는 signed full-Frobenius 좌표다. half좌표는 각각sqrt2로 나눈다. total은 signed합 후norm.
- 최신 peer source의 `plot_extension.py`는 component endpoint/진화/cancellation 그림이며 trajectory anchored-axis reducer는 구현되어 있지 않다. HH128은 z20→4 memory attribution으로 별도다.
- PR199 actual head는 `8b71c13e23202edfce1ee67fb2da552fefb9a583`로 조회됐지만 PR body는964b… snapshot을 가리킨다. 이 HEAD에서 unified/component source와STATUS를 직접 fetch하면404다. 따라서 **새 반환은 현재 공유 원본+해시 provenance이며, 그 시점 PR199에 이미 게시됐다고 주장하지 않는다**. 원 소유자의 다음 게시를 확인해 추후 Git identity를 결속한다.
- read-only schema 검토 기록: `TRAJECTORY_INPUT_SCHEMA_REVIEW.json`. 새 ODE/benchmark/NCP 0.

최종 후보 비교는 (1)완료175궤적의63축/112혼합 사후 residual 분석 **선택**, (2)warm729 history 분석 **유보:목표 구간에 직접 기여하지 않음**, (3)새 z4→2 실행 **기존237완료와 중복이므로 제출하지 않음**이다. 물리적HOLD와 원REC U5/globalconvergence/production 상태는 그대로 유지한다.

## 초기 Git-only 조사 기록 — 위 최종 갱신을 우선한다

조회일: 2026-10-21 KST. 이 기록은 실제 GitHub API 읽기와 정확 파일 취득에 근거한다.

## 조사 범위와 결과
- 현재 공개·접근 가능한 branch refs **823개**를 페이지 끝까지 열거했다: REI255, BASS262, BASS_CR168, WU088_HH138. 원목록은 BRANCH_HEADS_20261021.json.
- 2026-10-20 이후 updated PR 검색은 REI8/BASS4/BASS_CR7/HH10의 **29개**를 반환했다. 제목·현재 body를 검토했으며 직접 의존하는 PR198/213/214, BASS177, CR91, HH128/129의 head와 구체 자료를 추가 읽었다.
- 이 범위에서 z20→2 완료 결과/해당 신규 branch는 발견되지 않았다. 비공개 대화나 모든 branch 파일의 전수 열람을 주장하지 않는다.
- 직접 git ls-remote는 현재 proxy connect 실패였으며 GitHub connector로 정확 파일을 읽었다. 이는 GitHub 접근 부재가 아니다.
- 이 서브작업은 ODE/benchmark/NCP 실행0, 원격 변경0이다.

## 최신 권위와 재사용
| 대상 | 실제 현재 identity | 완료된 범위 | 다음 작업에 기여 |
|---|---|---|---|
| [REI213](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/213) | delivery d32cd99fa19c65aa1ca63dbc8aab8741834270e8; result c8e9f67aa031ffb33a9b0347bdea61dbb01fb746 | warm C15 a=.1999→.2, independently split729; history47385 | COMPLETE_REUSED; warm endpoint reducer 비교는 유지 |
| [REI214](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/214) / [BASS177](https://github.com/cosmosapjw-quantum/bass/pull/177) | REI58a8c3ef10a11c8b28e9c77c956d00f445ea0ac1; BASSc0a3df9c7509ab3526ae336e8fc29170431cd3a1 | ACCEL01 exact moment cache; completed729 registry; pending-only executor;25tests+29review probes | 동일 cache/작업 재사용 구현을 중복 개발하지 않는다 |
| [REI198](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198) | head8bd35af5f11c7ea5945b656be1c013d1c1933498; science b140170ce0c58159368b6b81be49ac35ca764851 | collisionless reflection-even LRS z20→4, radiation slice625+matter600+mixed6=1231 histories;80015samples | 원8-state raw terminal에서 z4→2 continuation 가능 |
| [BASS_CR91](https://github.com/cosmosapjw-quantum/bass_cr/pull/91) | document b78a943e5d7ae341bbfe84f742a06a4ac36d0e43; science659c94312eb9c12ebb987de934459c12a63d67b0 | 원40state z20→4 independent3D27grid;26new+1reused;101samples each | 가장 작은 실제3D long-window continuation seed |
| [HH128](https://github.com/cosmosapjw-quantum/WU088_HH/pull/128) | 92f5ab9dba531ebe05909dcb77d3740d2c68c580; treecf7636614a7b5a95e8d511560fad41e3e7dd523e | finiteL8 radiation5좌표를 exp[(b-bi)M]Ei로 제거해8→3; saved1231 histories sector-memory 분석 | source/OWNER_LOCK, radiation_flow.py 정확 재사용 |
| [HH129](https://github.com/cosmosapjw-quantum/WU088_HH/pull/129) | 조회 중251ca2c…에서b76fd4b5d0dfe4850ebde66a8a10f78402d36c00로 진전 | 과거 standalone fallback의 보존·배송 복구; source ODE0 | 현재 과학 권위는 HH128; fallback으로 덮어쓰지 않는다 |

REI198는 scoped Python 결과PASS와 workspace cargo fmt failure/tests skipped를 별도 기록한다. REC116 independent-agent review NOT_RUN의 역사적 기록도 이 조사만으로 변경하지 않는다. 원 REC U5 HOLD/REI_activation=false/physicalHOLD/globalconvergenceNOT_RUN/productionNOT_APPROVED 유지.

## 후속 후보 최대3개와 선택
1. **선택 권고: 기존 독립3D27 trajectories의 z4→2 continuation.** BASS_CR91의 정확 f0/parameters/state를 재사용하고 z20→4를 다시 풀지 않는다. 원40state를 그대로 쓰면 새3state 오차규준 비교 의무도 최소화할 수 있다. 새 seed/history 범위를 계약으로 동결하고 초기·최종 signed tensor, half/full norm, positivity/finiteness, 두 꼬리 경로의 최소 정합 검사를 수행한다. 이 결과는 collisionless pilot으로 발표한다.
2. REI198 원8state의 선택된 two-slice/mixed cases를 z4→2 이어 푼다. source를 바로 재사용하기 쉽고 그림을 만들기 빠르지만3차원 독립 grid는 아니다. 기존 1231 전체를 다시 풀 이유가 없다.
3. warm729 저장 trajectory에 REC축분해 분석을 확장한다. 후처리 재사용 장점은 있으나 z20→2 목표에 직접 기여하지 않으며 HH128의 memory attribution과 상당 부분 중복한다.

## continuation의 필요한 수학·코드 계약
원 x=ln(a/a_ref), a_ref=1/21을 유지하면
x_start=ln(21/5), x_end=ln7이다. b,s 또는 q=s/h_ref, proper-time 누적좌표, 모든 radiation moments를 원 z4 endpoint에서 이어야 한다.
CanonicalMomentumFV.moments(x,b)는 원 z20 canonical f0를 사용하므로 **a_ref와 b gauge를 재설정하지 않는다**. per-case A_m으로 원 distribution weights/normalization을 정확 구성한 후 original x,b를 입력한다. 새 초기축 inversion으로 원 state를 대체하지 않는다.
finiteL8 radiation flow는 E'=b'ME이고 M이 고정된 경우
E(x)=exp[(b(x)-b_start)M]E_start를 사용할 수 있다. 이것은 기존 closure와 같은 finite system이다. warm C15 UV/Thomson에는 적용할 수 없다.
원8→3 helper는 초기화/0→xmax를 하드코딩했으므로 source bytes를 보존한 외부 continuation wrapper가 필요하다. 원 full40은 source.fields에서 x<=source.xmax guard가 있으므로 SourceLock의 a_end만1/3으로 확장하되 a_ref/cosmology/h_ref/f0를 유지한다. 변경된 endpoint/time interval은 새 contract identity다.
matter/radiation의 signed pi_s를 합산한 뒤 norm을 취한다. fullFrobenius=sqrt2×half; kappa_t=8piG/c², H[s^-1], stress[Jm^-3]. 두 component 별 anisotropic work도 유지한다.

## 복원·파일 준비
정확 upstream 파일10개를 local agent_survey/owner/와 agent_survey/radiation_flow.py에 취득했다. 모든 파일은 live Git blob SHA1 및 크기가 일치한다. SOURCE_MANIFEST.json에 각 URL/blob을 기록했다.
- pilot.py SHA256 4cf3db0a6d2bc4803e87dcffe422faa3ebe9478bf23a16e02a9f16fe5c2e4400
- component_pilot.py SHA256 e2ce8b440765be3a728d8127a4f1085dbc304cabcaa7a5d4e892f92ccabd801e
- HH radiation_flow.py SHA256 d944f1de2339fbbf08135fe0f9ed061aefc52784b2509d530e4e1d95ed9c3b3b
원7파일 source hash는 HH OWNER_LOCK의 hashes와 일치한다.
Git의 REI198 new_sweep에는 endpoints/run/summary/plots가 있으나 raw cases directory는404다. raw NPZ는 backup에서 복원해야 한다.
- REI full parent+component archive: REI_BIANCHI_MATTER_RADIATION_FINAL_20261021.tar.gz,37945383bytes,SHA2562c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d, Drive1i6x-HcPTctzSQwsxkET-CfTGfjpC-Dx7, Dropboxid:BSpOijBcT10AAAAAAD_fYA. 이전 실제 dual whole-readback 근거가 있다.
- CR27+parent archive: BASS_CR_C21LM_RESEARCH_DELIVERY_20261021T082802Z.zip,17539759bytes,SHA256e0592be2859b7db606ec5a2ca008015c5ab02a3b2ff09fdd97fafe209cfe167a, Librarylibfile_9ec015516fd48191bf149640f43bea7a, Dropboxid:BSpOijBcT10AAAAAAD_fqQ. Library full bytes verified; Dropbox ACK/size; DriveUNKNOWN_NO_ACK.

## 공유 자원와 범위
기존 ACCEL01 pending-only executor/HH74 resources cooperative leases/CR91 CPU55-aware runner를 재사용한다. 최대64CPU/128GiB는 실제 할당이 아니며 실제 affinity/quota/freeCPU/RAM/공동lease에 맞춘다. innerBLAS/OpenMP1, 타 세션을 veto로 쓰지 않고 fitting chunks를 배정한다. 과거 V12 cap/debit나 다른 lane 실패를 재설정하지 않는다.
Full cold EoR/Thomson/native HHe/source Q/전역 수렴은 독립 후속으로 남는다. 이 선택의 실제 성과는 재사용된 z20→4와 새 z4→2로 연결된 명시적 collisionless 그림이다.

