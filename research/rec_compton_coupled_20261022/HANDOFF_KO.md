# 재개 지점과 실행 결과 인계

## 현재 결과

8개 새 Compton full63 IVP, 4개 refinement pair와 새 경로의 분석을 완료했다.
actual_hot 강화 해의 z=2 온도는 s03 8896.568827K, s04 8885.220909K다.
기존 대비 −12.080108%, −12.174009%; 현재 경로의 Compton 손실은
−2.1728161, −2.1841256eV/baryon이다. 과학적 해석·표·그림은 REPORT_KO.md에 있다.

Runtime identity:
`c89f576e2c7f15a0a1d0d3f96ce72de516245cbb83b5d4fbaeede342a76e86ac`

Analysis identity:
`f824bdead1ce75b94f5102764184ea8dee2db71ecc06296dc7fa2ac9d71708c3`

현재 사용 그림은 figures/v2다. v1은 실제 눈금 겹침과 실행 기록을 보존한
이전 출력이며 최종 보고서 그림으로 선택하지 않는다.

## 재개할 때 읽을 것

1. README.md, REPORT_KO.md, FROZEN_CONTRACT.md와 DAG.json.
2. results/compton8/CAMPAIGN_LOCK.json, REFINEMENT.json 및 execution의 두
   FINISHED.json. 새 IVP8개와 첫 경로 재사용1회를 구분한다.
3. evidence/PREFLIGHT_ADMISSION.json, 독립 preflight/analysis/results/visual
   검토와 실제 stdout/stderr/process receipts.
4. results/analysis_v1/RESULT.json·INPUTS.json·SUMMARY.json과
   figures/v2/FIGURE_MANIFEST.json. 입력·출력 byte/SHA를 확인한다.
5. NEXT_UNIT_CONTRACT.md. 제안은 저장 상태 진단의 동등성·계측과 중복 평가
   감소이며 새 IVP0개다. 기존 원자·열·Compton source의 물리적 가정을
   성능 최적화 중 바꾸지 않는다.

완료된 결과를 확인하려고 ODE나 기존 전체 테스트를 다시 실행하지 않는다.
원본 스냅샷의 복구는 archive manifest, Git blob/commit/tree, preflight 및
결과 identity를 확인하는 읽기 작업으로 끝낸다. 다음 후보 구현을 검사할
때만 바뀐 dependency에 맞는 새 유한 검증을 설계한다.

## 좌표와 물리 해석

Native63=geometry/radiation40+isotope ions21+tau+logT다. initial_state는
기존 Mao 명목 해의 정확한 첫 벡터이며 donor index84와 연결된다. x0는
0.8513356902116996, z0는7.963732801243163, 최종 x는ln7이다.
elapsed_Myr와 tau는 donor z20 이후 누적값을 유지한다.

actual_hot은 현재 photon raw4를 사용하고, Planck reference는 독립 bath다.
둘을 더하지 않는다. 외부 UV는 동일하게 포함한다. 반대 radiation 원장은
기체 소스 검산용이며 photon/Einstein에 적용하지 않았다. 중성자·삼중수소0은
선택한 원자 초기조건/연산자의 성질이고 실제 핵반응이 없다는 증명이 아니다.
REI219의 새 핵반응 dossier는 provenance/REMOTE_INTAKE에 기록된 별도 계약이다.

## 실행과 미완료 범위

Campaign 실제 차감309.202초/1200초, 최대 사례71.087초/240초다.
이번 allocation을 새 코호트 명분으로 다시 열지 않는다. 새 IVP8개 이외의
RR 대안, opacity-off, 핵반응 또는 parameter scan은 추가하지 않았다.

분기별 lnT·ion·tau 차이는 관측된 refinement보다 컸다. signed6 전체의
분기 차이는 두 초기조건에서 구별 미확보다. 응력만은 s03 미확보,
s04가 관측된 두 변화의 합보다 약1.99배 크다. 이를 전역 오차 보증으로
사용하지 않는다. CI/CE는 새 경로 진단으로만 평가했고 unavailable 채널과
구간 밖 정확도 의무가 남아 있다.

Physical HOLD / production NOT_APPROVED / global convergence NOT_RUN /
REI_activation=false / U5 CLOSED_HOLD_NOT_RESET을 유지한다.
GitHub 초안 PR은 https://github.com/cosmosapjw-quantum/rec_bianchi/pull/124 이며
PR122 위에 쌓인다. 최종 commit/tree, archive 및 제공자 ACK는 별도의
실제 전달 receipt가 소유한다. merge나 public Dropbox shared link는 만들지 않는다.
