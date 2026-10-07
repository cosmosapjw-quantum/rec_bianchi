# Task5 실행 기록

원문 복원 -> fixture/허용치 사전등록 -> Rust 시험 사전작성 -> BF/S source와 SI 장부 코드 작성 -> 독립 toy -> 정적 점검 순서로 진행했다. 원문/table/gross tolerance를 맞추기 위한 조정은 없었다.

Ruling: 사용자 승인된 no-compile 정책을 적용한다. Rust red/green은 local에서 관측하고 이번 작업은 CODE_AND_TESTS_WRITTEN_UNCOMPILED로만 기록한다.
Ruling: BB canonical energy와 다른 registry가 mixed ledger에 들어가지 않도록 combined assembler만 exact canonical registry로 제한한다. 기존 standalone BF 인터페이스는 유지한다.
Ruling: 기존 BB/pair 계산식을 재작성하지 않고 direction-bearing wrapper에서 원 kernel과 원 ordered-grid 검사를 사용한다. Pair moment wrapper는 tag1만 누적한다.
Ruling: 눈에 보이는 ledger 에너지/힘 잔차를 숨기거나 조정하지 않는다. 백업 실패가 생겨도 통과한 toy/code 작성 과정을 반복하지 않는다.

Toy 첫 실패는 SymPy Rational과 bool Kronecker 지시자의 곱 TypeError였다. 지시자를 int(0/1)로 변환하여 검사기만 수정하고 실패 로그를 보존했다. fixture/허용치/Rust source를 바꾸지 않았다.

다음 작업은 Task6의 독립 source parity harness다. Git candidate는 Task8에서 게시한다. G10/E1C 및 기존 scientific HOLD는 유지한다.
