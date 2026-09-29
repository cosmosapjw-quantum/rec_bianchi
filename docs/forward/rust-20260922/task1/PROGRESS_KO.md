# Task 1 실행 기록

승인 범위: 2026-09-23 대화의 “작업을 승인할게. 첫번째 단계를 실행해줘.” 계획 Task 1만 실행한다.

Ruling: 출판은 계획 Task 8의 미검증 코드 후보 게시 시점에 묶는다. Task 1은 source/state 문서 overlay를 만들고 durable backup으로 보존하며 별도 코드 후보 commit을 만들지 않는다. 따라서 두 commit 기본 단위를 불필요하게 늘리지 않는다.

Ruling: 현재 컨테이너에는 rec_bianchi Git checkout이 없고, 이번 git ls-remote는 DNS exit128이다. Connector read로 branch를 고정하고 로컬의 검증된 delivery bytes를 비-Git baseline으로 사용한다. origin/branch/dirty-state가 존재한다고 꾸미지 않는다. GitHub를 볼 수 없다는 뜻이 아니며 Rust runtime에 대한 판정도 아니다.

Ruling: A6 manifest의 ./ prefix를 첫 reader가 처리하지 못했다. 경로 해석만 POSIX-normalize한 후 26/26을 확인했다. 입력 ZIP/manifest/source bytes는 변경하지 않았다. 실패는 reader implementation 오류이며 atomic-source hash 불일치나 물리 오류가 아니다.

Ruling: archived V2 lock와 Git V3 lock은 다른 문서다. V3를 읽은 내용으로 복원하고 Git blob SHA를 확인했다. 공통 원문 10개 SHA/size는 모두 일치한다.

Ruling: WU29의 CHIANTI 수치 문장을 raw 파일에서 수정하지 않는다. A1의 명시적 supersession을 lock에 추가한다. 더 넓은 raw T4 low-domain 표기는 보존하되, 없는 numerical partial rows는 admission하지 않는다.

Task 1: source bytes restored; static mapping and pending state complete in local overlay. No compiler/no source parity/no kernel repair in this work unit. 원격 branch/PR와 legacy logs는 변경하지 않았다.

다음은 Task 2이며 계획을 다시 생성하거나 Task 8/9로 건너뛰지 않는다.
