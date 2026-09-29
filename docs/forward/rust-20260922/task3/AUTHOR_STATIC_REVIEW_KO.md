# Task3 작성자 정적 검토

검토 범위는 BB의 입력→kernel→적분→spectral output과 해당 tests/example 호출부다. 독립 reviewer/컴파일/수치 parity 승인이 아니다.

원문 B/J의 anti-commutator 순서 및 BB의 transpose 부재, WP one-owner, per-node F, angular weight single ownership, J/C의 screen 분리와 delta_J/에너지 단위가 코드에 반영됐는지 확인했다. 신규 경계에서 기존 Task2 검사를 호출하고 source matrix에는 PSD를 요구하지 않는지 확인했다. Empty/zero/invalid mode의 동작 및 overflow 오류 경로에 시험을 작성했다. 이 입력은 파일/network/eval/unsafe가 아닌 fixed-value 연산이다.

12개 작성 시험의 존재와 component reference·수식 대응을 확인했지만 실행 정확성은 local 검증 전까지 미판정이다. Public API 변경이므로 기존8+3 call site를 이행했다. 전체 consumer census, formatter/type 검사와 exact candidate의 source parity는 local task에 남긴다. Historical FD JVP 수치나 과거 PASS를 새 커널에 승계하지 않는다. Task6에 정의한 독립 reference-scale gate는 여전히 전체 구현이 필요하다.

BB 외 source suffix와 기존 table/constant/density guard는 byte-preserved다. Pair shortcut과 독립 물질 four-force assembly를 아직 수정하지 않았으므로 이 포트를 완료로 판정하지 않는다. Task3를 더 감사하는 새 단계 대신 다음 명시된 Task4로 진행한다.
