# 이론 R1–R10 / 구현 C1–C10 근거

physmath-research-loop workflow1.0.0, approval design0.2를 적용했다.
사용자는 sandbox 중심의 물리 유도·계산 단순화·코딩 연구와 기존 게시/백업
재시도를 명시적으로 승인했다. 단계는 증거의 의존관계이며 독립 작업은 병렬 수행했다.

| 이론 단계 | 실제 작업·근거 |
|---|---|
| R1 위치·계약 | 이전 omitted unit의 완료/복구 receipt, FROZEN_CONTRACT와 8IVP 범위 |
| R2 근거·재사용 | REC119/122, REI219/220 실제 head intake; Exa/SciSpace·원문; 옛 IVP는 identity로 재사용 |
| R3 주장·전제 | 실제 photon raw4와 독립 Planck bath, test-fluid 에너지, atomic n/T0 범위 명시 |
| R4 표현 탐색 | full63 유지, hot logT의 T 소거, 단일 추가 Jacobian 행, 고정계수 affine 해 |
| R5 구성적 유도 | THEORY_KO의 source·η 미분·중성 극한·gas/bath/work 식 |
| R6 독립 검증 | 실제 Wolfram26개 검사/경고, 저자9개 검사와 별도 전체63×63 Jacobian4개 |
| R7 판별 실행 | 새8IVP, 4refinement, 109/accepted/513/1025 저장 집합과 current-path source 예산 |
| R8 판정 | T종점 약12% 감소; fixed-path forcing과 실제 해 구분; 변수별 분기 resolution |
| R9 정식 결과 | REPORT_KO, 원시 배열/표/그림, 보존식·한계·다음0IVP 최적화 계약 |
| R10 종료·재개 | HANDOFF, DAG, 고정 Git snapshots와 실제 provider/restore/readback receipts |

| 구현 단계 | 실제 작업·근거 |
|---|---|
| C1 baseline | 정확한 기존 Mao 명목/강화 initial_state·109grid·source hashes |
| C2 식–코드 | ComptonFull63의 RHS62행·Jacobian62행; 기존 수·binding·opacity 소유권 유지 |
| C3 수치 설계 | logT/native63/BDF/analytic Jacobian, 기존 tolerance와 물리 sample gate |
| C4 DAG·자원 | 직렬 thread1, 240s/case·1200s campaign, create-only results와 영속 차감 |
| C5 구현 | compton_system/run_compton; UV2모멘트 초기화1회·compact H gradient |
| C6 코드 검증 | Jacobian756성분·36JVP, 실제 driver4실패→동일6PASS, analyzer6실패→동일6PASS+정상control |
| C7 과학 검증 | 국소 원장·gas first law·동위원소/전하·실제 소스·HG97 mapping 독립 재계산 |
| C8 수치·재현성 | 40caseNPZ, 24collision grids, 4refinement pairs, exact source/input/output identities |
| C9 독립 검토 | 저자와 분리된 preflight/analysis/results 검토, root와 독립 검토자의 실제PNG 확인 |
| C10 인계 | COMPLETE_SCOPED_COMPTON_PILOT; 다음 계약은 제안/미실행으로 표시 |

## 수정과 재사용

- 과학 실행: 새8IVP만. 기존 donor·thermal·omitted 단위는 수정하거나 다시 풀지 않았다.
- 코드 결함: 재사용 inventory/initial state/시간 한도 및 분석 input binding을
  실제 실패로 재현한 뒤 동일 검사로 교정했다. raw command/output/hash를 보존했다.
- fixture 교정: 초기 runtime2개 fixture 오류와 독립 결과 checker의 상쇄 잔차
  비교 오류를 소스/물리 gate 변경과 구별했다.
- 그림 교정: v1의 실제 symlog 눈금 겹침 및 cache 경고를 보존; v2에서 표시만 교정했다.
- 문헌 도구: WolframContext의 실패와 LanguageEvaluator의 실제 결과/경고를
  구별했다. 원문 날짜와 검색 ingest metadata를 혼동하지 않았다.
- 증거 재사용: 이전 출처·126donor+8thermal IVP와 provider 검사 중 변하지 않은
  항목은 해시로 재사용했다. 새로운 source·coupling·새 경로·결함을 판별하는
  검증만 수행했다. 지난 채팅 전체나 문헌 전수 열람을 주장하지 않는다.

strong no-go는 제출하지 않았다. 남은 spectral/backreaction/unsupported-channel
의무는 현재 유한 계산의 범위와 다음 물리 계약에 명시했다. Physical HOLD,
production NOT_APPROVED, global convergence NOT_RUN, REI_activation=false와
U5 CLOSED_HOLD_NOT_RESET을 유지한다. 최종 전달은 예측 상태가 아닌 실제
GitHub ACK·pinned archive·fresh restore·전체 Dropbox readback receipt로 판정한다.
