# REC PR152/153 독립 비저자 검토

검토자 `/root/independent_hd_review`, 2026-10-29 KST. 검토 기준은 PR153 실제 HEAD `67d8baa092f18b7c1bbf8dfe9e255f8b43b45998`와 이 tree가 포함하는 PR152 입력이다. 원 저자가 아닌 별도 실행자가 원문과 코드를 읽고 새 검산·제어를 수행했다. 작업 문맥을 전달받았으므로 blinded review로 부르지 않는다. 기존 scientific suite·stationarity·native·IVP는 재실행하지 않았다.

조건부 수학 결과 R6는 **PASS_SCOPED**다. PR153 C9는 아래 두 구현 결함 때문에 **CHANGES_REQUIRED**다. 원본 CDMS 2011 바이트와 물리 source 선택은 이번 검토로 해결되지 않는다. 중앙 DAG 28/88(+0), physical 0/313, H5 epsilon=null, H6/H7 OPEN, L4/REI=false, production HOLD를 유지한다.

## 독립 이론 검증

인쇄값을 `w=w*+e`, `nu=nu*+f`로 두면 `delta_print=delta_star+100c(e_up-e_low)-10^9 f`다. 최근접 반올림의 절대오차 `|e|<=0.5e-9 cm^-1`, `|f|<=0.5e-8 GHz`에서 `|delta_print-delta_star|<=100c*1e-9+5=34.9792458 Hz`를 얻는다. `delta_star=0`인 단일 에너지 가설에는 이 부등식이 필요하다. Python `Fraction`으로 입력 17개를 정확한 유리수로 새로 해석하여 PR153 공개 결과의 8개 부호 있는 delta와 완전히 일치함을 확인했다. 실패 행은 J2..J8, 최소 초과는 J8의 6830.010377 Hz다. 유한 소수에 대한 계산이며 측정오차나 역사적 진본성에 대한 추정은 아니다.

프린트 cochain은 `a_print=h*delta_print/(k_B T)`이고 PR151 photon-down/collision-up 방향과 반대 부호다. `h` 대신 `hbar`를 쓰면 `2pi`를 잃으므로 ordinary frequency 컨벤션이 필요하다. 단위는 `(J s)*(s^-1)/(J K^-1*K)=1`, T>0에서 순서가 보존된다. 정확한 프린트 cochain과 미지의 unrounded `a_star` 구간은 표기를 구분하는 것이 좋다(REV-A1).

9개 꼭짓점에 26개 marked edge의 connected graph이므로 incidence rank는 8, integral cycle 차원은 18이다. 각 photon edge와 별도의 collisional spanning-tree return path가 8개 독립적인 photon 투영 좌표를 만드므로 cycle-to-source map rank는 8이다. photon 투영이 0인 cycle들은 18개 collision edge만의 connected subgraph의 cycle들로 이루어져 차원은 18-9+1=10이다. 이는 임의의 특정 basis에서 10개 이름붙은 cycle이 0이라는 주장이 아니다. 저장 RESULT topology가 photon8+pH2 9+oH2 9, 각 collider의 2->0 edge 포함과 일치함을 직접 검사했다. 저자의 matrix-rank 실행을 반복하지 않고 spanning-tree/좌표사상 증명을 사용했다.

공유 level error 때문에 rowwise 필요조건은 joint sufficient 조건이 아니다. `e0,e1,e2 in [-1,1]`, 각 인접차 `e1-e0=2`, `e2-e1=2`는 각각의 bound=2를 통과하지만 합하면 `e2-e0=4`여서 joint 불가능하다. PR153이 이미 이를 명시하므로 현재 필요조건 정리에 대한 결함은 아니다. 새 joint interval solver가 필요하다면 이 반례가 검증 기준이 될 수 있다.

## 구현 지적과 최소 교정

1. **REV-F1 / medium / 재현성.** 공개 tree에는 `results/`가 없는데 handoff는 `python precision_audit.py --output results/print_precision_certificate.json`을 지시한다. `main()`의 `write_text` 전에 parent 생성이 없어 깨끗한 nested 경로 제어에서 exit1 `FileNotFoundError`를 실제 얻었다. 출력 parent를 생성하고 fresh nested 경로에서 실행하는 소형 regression으로 닫을 수 있다. 보고된 과학 수치는 그대로 둔다.
2. **REV-F2 / medium / 입력 검증.** `parse_spcat_line()`은 `frequency=Infinity`와 `uncertainty=Infinity`를 모두 실제 ACCEPTED로 반환했다. `frequency`, `uncertainty`, `elo`에 명시적 finite 검사 후 기존 range 검사를 수행하고 NaN/±Infinity를 거부해야 한다. SHA 고정은 임의 파일의 identity를 고정할 뿐 숫자의 유한성을 보증하지 않는다. 음수 TAG와 양수 TAG의 의미를 섞거나 원본 진본성으로 승격하지 않는 기존 설계는 적절하다.

두 결함은 현재 fixture의 8개 delta·35Hz gate를 바꾸지 않는다. 수정 후 새 CLI/nonfinite 제어를 재검토하면 PR153 C9를 이 제한된 구현 범위에서 닫을 수 있다. 원본 LAMDA raw와 CDMS v2 바이트를 이번에 읽지 않았으므로 그 admission은 별도 입력 의무다. PR152의 private-input 과학 suite와 원본 figure도 재실행·재열람하지 않았고 기존 보존 기록을 상속했음을 명시한다.

## 근거

`REVIEW_CHECKS.json`은 exact Fraction 결과, 원본 네 파일 SHA256, parser finite/nonfinite 제어, 새 경로 CLI command·stderr·exit code를 담는다. `GRAPH_INSPECTION.json`은 저장 RESULT SHA256 `9e5ab9eccc72009a7794c7beec4737f9afd0713b317fac61d65e3d8664e81d72`, 실제 26개 edge와 조합적 증명을 기록한다. 새 no-go/novelty를 주장하지 않고 기존 rounding bound를 해당 finite source에 적용한 불일치 진단으로 판정했다.
