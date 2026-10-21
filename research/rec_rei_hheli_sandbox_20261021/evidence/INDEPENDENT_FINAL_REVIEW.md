# 최종 독립 검토 — H/He/Li 조건부 sandbox pilot

판정은 **PASS_SCOPED_NO_BLOCKING_DEFECT_FOUND**다. 이번 새 프로젝트의 atomic/coupled/dispatcher/reducer/plot/wrapper 작성과 분리된 agent가 실제 소스, 저장 배열, 보고서와 최종 PNG를 검토했다. 검토자는 이전 PR118 tangent dependency를 작성했으므로, 그 재사용 dependency 자체에 대한 독립 검증으로 확대하지 않는다. PR116의 역사적 C6 미실행 상태나 기존 REC U5 HOLD도 소급 변경하지 않는다.

## 실제 결과 및 검토 범위

| 항목 | 독립 확인 |
| --- | --- |
| 새 main sweep | 125개 고유 case, 각각 193개 저장 시점의 z=20→2 전체 궤적 |
| 별도 control | 같은 초기 상태·공통 source의 opacity-off 1개 고유 IVP |
| 최초 case 복구 | 18개 점검 통과; 원 실패 기록 보존, NPZ byte-identical, writer 외 scientific AST 동일; ODE 재실행 없음 |
| Main 저장 배열 | 모든 125 case의 identity/RESULT/NPZ가 앞선 독립 감사 이후 불변; 기록된 13개 gate 모두 true |
| Control 저장 배열 | 17개 점검 통과; 6개 signed 성분 끝점/최대 차이와 ne, Y, 분율 차이를 독립 산술로 재확인 |
| 최종 보고서 | 18개 점검 통과; endpoint 수치 5,375개, species 2,625행, 대표 궤적 193행 전체 필드, global extrema 222개와 매 시점 extrema 일치 |
| 최종 시각 산출물 | PNG 5개 직접 열람; PNG/PDF/caption 총 11개 해시 일치; PDF 직접 렌더링 검토는 미실행 |
| 실행 wrapper | 최종 4단계 exit 0; main 125 + control 1 모두 complete_reused; 새 worker 0; 첫 wrapper receipt도 보존 |

최초 main IVP는 궤적을 완주한 뒤 JSON의 NumPy bool 직렬화에서 실패했다. 보고서 writer만 수정하여 기존 NPZ를 복구했고, 그 case의 실제 solver counter와 wall time은 UNKNOWN으로 남겼다. 전체 고유 IVP는 main 125 + distinct control 1 = **126**이다. 독립 검토 자체의 ODE/RHS/Jacobian 호출은 0이며, NCP 실행·benchmark·기존 729 재계산도 없다.

## 소스·물리 계약

새 core의 SI 단위, Frobenius/half-contraction 규약, matter/radiation signed 합 후 norm, 21종 stoichiometry, 전자 밀도 rank-one Jacobian, geometry coupling 및 photon-only Thomson 적용을 읽기 전용으로 검토했다. `κ_t=8πG/c²`는 J/m³ 응력에 적용한다. Radiation에는 photon과 collisionless neutrino를 구별한다. Opacity-off control의 τ는 전자 column의 potential 값이며 실제 photon collision 적용 계수는 0이다. Matter와 neutrino의 전체 궤적은 geometry를 통해 간접 변화할 수 있다.

Li I의 1s/2s absorption provider를 사용하되 각 흡수의 q→q+1 전하 수율은 명시적 조건부 coarse-graining이다. 검증된 Auger/형광/열화 수율로 주장하지 않는다. 1s primary photoelectron, valence ionization cost와 unresolved core energy를 구분하며, `net_required_gas_input`과 `bath_minus_escape`도 RR heating으로 오인하지 않도록 분리한다.

최종 reducer `db25849a…`는 ionic fraction을 **고정 초기 isotope inventory**로 나눈다. 이전 current-total 분모의 코드·보고서는 별도 보존했고, 새 정의는 그림과 독립 raw-array 감사에 일치한다. Control의 최대 fraction 차이는 `4.364064665196565e-12`다. 이것은 미세한 차이의 물리적 유의성 인증이 아니다.

## 남는 한계와 판정

T와 UV는 외부에서 지정하고 gas/UV energy는 test-fluid 진단으로 취급한다. CI/CX, 음이온, 분자, photonuclear 및 fusion은 이번 유한 closure 밖이며 생략 오차 상한은 없다. Isotope별 상태는 따로 추적하지만 electronic rate의 isotope 동등성은 모형 근사다. n/T의 초기량과 전체 저장량은 0이며 populated decay history를 보여주지 않는다.

193개 저장 시점과 129개 각도의 positivity 점검은 연속 시간·각도의 보장이 아니다. Algebraic Einstein consistency gate 역시 독립적인 동역학 정확도 검증이 아니다. 모든 그림은 finite pilot의 저장 궤적과 실제 paired control을 보여주며, 참해 오차·global convergence·측정 speedup을 주장하지 않는다.

**Physical HOLD, global convergence NOT_RUN, production NOT_APPROVED, REC U5 HOLD_9_FAIL/HOLD_8_FAIL 및 REI_activation=false를 유지한다.** 로컬 검토는 원격 게시·최종 CI·백업 전체-byte readback을 독립 확인한 것으로 주장하지 않는다. 각 소스와 단계별 감사 파일의 실제 SHA256은 동명 JSON에 고정했다.
