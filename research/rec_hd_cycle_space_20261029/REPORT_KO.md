# REC-HD 26채널 순환 공간 분석 | 2026-10-29

**실제 산출물:** 원래 HD 26채널 멀티그래프에 대해 18개 독립 정수 순환을 구축하고, 8개의 분광 에너지 결함만이 유도하는 8차원 구동 및 공통 결함에 무관한 10차원 null 순환 부분공간을 정확히 분리했다. 원본 9×9 정상상태 계산 및 기존 수학 결과를 다시 실행하지 않았고 PR151 저장 결과를 그대로 재사용했다.

## R1–R2 위치·출처

- REC 최근 연구 HEAD PR151 `b10ab6e3c8f80dfcde27e3f1a6d454d730951009`에서 독립 자식 단위로 진행한다. 다른 별도 H5 PR148과 JOINT-TANGENT01, WU #152 HD reactive source R1, REI #256 검토, BASS #234 tau 연구 등은 별도 owner다. REC canonical 28/88, physical 0/313 시작·종료 동일.
- 원래 `LAMDA HD 2021-06-07` 2289-byte SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`; 이전 PR151 25117-byte RESULT SHA256 `e6e795921ee4af730edbdebd1faf52c7b902cc14e3d0c15ab56fba423b696881`. 두 파일은 ZIP에서 원본 바이트 해시검증 후 복구해 재사용.
- 신규 출처 발견: CDMS v2 2011년의 `https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/` HTML 디렉터리 index. `.egy`, `.par`, `.fit`, `.lin`, `.cat` 파일명이 확인되지만 직접 원문 bytes 획득은 실패했다. 특히 `.cat` index 수정일은 2019-02-25이므로 현재 보관 파일을 2011년 원본과 동일하다고 보지 않는다. LAMDA 변환 레시피 미확보. 기존 35 Hz original gate **J1 PASS, J2..J8 FAIL** 그대로.

## R3–R5 구성적 유도

Original 9 J states, radiative8, para-H2 collision9, ortho-H2 collision9, 총 **26개 형식적 표시 채널**의 `B∈Z^(9×26)` incidence를 구성한다. 파라-H2 인접 J쌍 8개를 spanning tree로, 나머지 18채널을 chord로 선택하면 `C∈Z^(26×18)` 는 정수 fundamental-cycle 기저로서 정확히 `BC=0`, `rank B=8`, `rank C=18`.

同온도에서 collision `u_e=−βΔE_e`, photon `u_e=−βε_e`와 준위 포텐셜 `φ_j=−βE_j`를 두면, `u=B^Tφ+D a`를 만족한다. 여기서 `a_J=β(ΔE_J−hν_J)`는 이전 PR151 photon-down/collision-up A_J의 부호 반대. `C^T u=(C^TD)a`, 선택한 tree의 좌표에서 `C^TD=[I8;0(10×8)]`. 따라서 **광자 vs 준위소스 불일치가 작용하는 최소 독립 차원은 8**, 원자료의 임의 8개 defect 전체에 대해 친화도 항상 0인 순환 부분공간은 10차원. 이것은 arbitrary 다른 기저에서 10개 좌표가 무조건 0이라는 주장이 아니라 **null 부분공간의 기저 불변 차원**이다.

## R6–R8 / C5–C9 실제 코드와 검사

100자리 mpmath에서 양의 채널별 up/down rate 로그를 직접 구성하였고 (T=50,100,200 K) × (n_p=n_o=10^3,10^6 cm^-3) 6개 저장 실험조건에서 `C^T u=M a` 를 검산했다. 최대 직접 순환 일치오차 **1.55853446116e−100**, 포텐셜 분해 최대 **4.57194956513e−100**, 기존 PR151 결과와의 최대 차이 **3.46336396868e−61**. 독립 `networkx` 그래프와 photon spanning tree, Decimal100으로 다시 세운 검증은 rank18, defect map rank8, 원·대안 cycle basis 결합 rank18 및 결함 수치 대조 PASS. **13/13 regression tests PASS.**

처음의 source degeneracy `1.0` int 파서 오류, SymPy integer JSON 변환 오류, 독립 대안기저에서 두 J2→0 chord의 기여를 빠뜨린 16개 기대치 오류는 실제 실패 기록으로 보존. 원자료·허용오차·35Hz gate는 바꾸지 않고 표현/테스트만 수리했다.

도표 `results/CYCLE_SPACE_SOURCE_DEFECT.png`는 저장값만 시각화하고 연속 온도곡선을 만들지 않았다. 실제 계측 시간은 RESOURCE_LEDGER의 모든 **중복제거된 7회 child receipt** (CPU ~12.05/30 s; wall ~9.28/90 s)에 있음. 비측정 웹/모델/connector 비용은 UNKNOWN_NOT_ZERO. Native subagent reviewer 부재에 따라 R6/C9 fresh nonauthor **PARTIAL**이며 numerical cross-method≠독립 물리모형 검토.

## 물리적으로 승인하지 않은 부분

이 연구는 finite marked graph의 exact topology와 합성 같은-T 두 에너지 열의 조건부 source obstruction 증명이다. 물리적 HD heating, 진동상태 인증, source uncertainty, 새로운 반응률, 분광 7개 실패의 보정, 과거 H5/H6/H7 coupling, cosmic IVP, L4/REI 활성화가 아님. 외부 CDMS 자료의 원본 bytes·source-to-LAMDA recipe가 준비되지 않은 상태에서 소스 선택을 시행하지 않는다. 26 ground +5 nuclear records, 102 formal charge requests, 621 missing process cells는 별도 H–Li 목록·provider 의무이며 이 그래프 26개 채널과 혼동 금지.

## 다음 이행 가능한 단일 행동

CDMS 2011 v2 보관 디렉터리의 실제 `c003501i.cat`, `c003501.egy`, `HD.par`, `HD.fit` 및 카탈로그 재생성 절차를 byte-SHA 고정하여 확보하라. `c003501.cat`의 2019 mtime 및 source 2026 v3와의 관계를 분리 확인한 뒤 9개 J상태·8개 복사선의 level origin, measured/predicted tags, uncertainty, source-choice를 독립 검토한다. 자료가 없으면 `HOLD` 보존. 새 원본이 없는데 35Hz 기준을 완화하거나 가상 재구성 ladder를 물리 모델로 채택하지 않는다. 현재 source obstruction 결과는 별도 재계산할 필요 없이 후속 소스 대조 검사에 재사용하라.
