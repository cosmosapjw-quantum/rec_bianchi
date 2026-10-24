# Astra 과학 판정 — HE-ANG-CCC-EXCHANGE

## 판정

현재 단위는 조건부 source-convention kernel과 실제 TP Table I 입력의 범위에서 PASS_SCOPED로 채택한다. R6와 C9의 최종 verdict는 각각 PASS_AFTER_CORRECTION이며, 현재 blocking finding은 없다. C9-01의 검사 척도 교정은 실제 targeted test_05 1회로 닫혔다. 커널은 변경하지 않았다. 최초 author 예시 산술 오류, 최초 14개 PASS가 해당 극소 remainder의 상대 정확도를 충분히 입증하지 못한 점, reserve 실행 전 잠금 오류를 모두 보존한다.

## 채택한 결과와 전제

같은 source/state의 raw CCC outgoing-momentum pair에서 U=|a|²+|b|², C=|a+(-1)^S b|², D=|a-(-1)^S b|²이면 2U=C+D다. Bray의 고정 v3 Eq.(26) 인쇄 부호와의 불일치는 그 버전·식에 한정한다. 원전 곡선이나 저널 버전의 오류를 추론하지 않는다. 이 adapter의 물리 해석은 정확한 equal sharing에 한정하며 raw amplitude 내부의 기존 direct/exchange 기여를 다시 추가하지 않는다.

위상 누락 intensity의 sharp 실수 범위와 지정한 복소 오차 disk의 결정론적 범위는 THEORY_KO.md의 전제하에 채택한다. 구현은 binary64의 검증된 근사 endpoint를 반환하며 directed-rounding 인증 구간이나 모든 입력에 대한 상대오차 정리를 주장하지 않는다. 이미 coherent 또는 spin-weighted인 입력의 정규화는 중복 적용하지 않는다.

실제 원전 입력은 Stelbovics TP S-wave singlet Table I의 8행이다. 이미 4CCC인 열의 원래 수치 문자열과 단위를 보존했고 printed BRM와의 비율만 계산했다. 새 CCC/BRM solve, full H angular dynamics, 경험적 물리 오차보정 또는 수렴률 추정으로 승격하지 않는다.

## 실제 계산과 비용

계획된 3회와 진단된 targeted reserve 1회, 총 4회 과학 child를 실행했다. 초기 14개 test method와 수리 후 영향받는 1개 method가 각각 실제 PASS다. 제조 phase control 65점의 관측 max identity residual은 8.881784197001252e-16이다. 실제 원전 표·제조 controls·그림은 구별되어 있다.

계측된 child+runner 구간 누적은 CPU 1.4100209999999999s / wall 1.4436621759814443s다. 정확한 부동소수 누적값의 권위는 RESOURCE_LEDGER.json이다. 새 단위의 계측된 구간은 CPU8/wall30 배정 안에 있으나, reserve 전 prelaunch parent CPU/wall은 UNKNOWN_NOT_ZERO이므로 완전한 end-to-end cap은 입증되지 않았다. 수리 예약은 사용 완료다. 이전 HE-X1/HE38/HE-ANG-CONTRACT/Hex/DDCS20/D10의 비용·실패·unknown을 보존하며 이전 배정을 전용하거나 초기화하지 않는다. 추가 과학 실행을 요구하지 않는다.

Wolfram evaluator는 1회이며 context call 1회를 별도로 기록했다. evaluator toolwall8.981s, body CPU0.066279s/wall0.066602s와 전체 remote CPU UNKNOWN_NOT_ZERO를 구별한다. 전제가 빠진 optional phase query의 경고 출력은 NOT_ADOPTED로 남긴다. SciSpace 조사와 원전 시각 대조를 근거로 사용했으며 문서 처리 비용을 과학 solver 비용0으로 바꾸어 말하지 않는다.

## 게시·인계로의 전이

PASS → C10 게시·복원본 전달로 진행한다. BASS_HE는 c8f5818c61d14872837abf7e9bc1a73c670ae25c 위 새 경로만 추가하고 PR94 branch를 base로 하는 draft PR을 만든다. 실제 expected SHA와 force=false를 사용한다. 중앙은 최신 관측 HEAD 5182d82c45454a4e8f19f2e5384a04a4ae35ed09의 CR N5 변경 및 C23E와 다른 owner의 결과를 보존하여 HE-ANG observation에만 새 subunit을 추가한다. 게시 직전에 HEAD를 다시 읽고 변동 시 최신 상태에 의미적 delta만 재적용한다. Merge와 activation은 수행하지 않는다.

실제 Git 게시·중앙 반환·Dropbox/Drive 백업 ACK가 있기 전 C10은 PENDING_DELIVERY다. R/C 완료율20/20은 이 단위의 기록에만 적용하며 전체 물리 목표 완료율은 null이다.

부모 HE-ANG은 SOURCE_INPUT_PENDING, physical_provider_admitted=false다. 다음 실제 입력은 HE-ANG-SOURCE-PAYLOAD의 source-consistent joint outgoing-electron law/amplitude/event payload와 count/spin/exchange/support/frame/recoil 계약이다. HE-X1의 경험적 각분포 보정, DDCS marginal의 event sigma/ion recoil 승격을 하지 않는다. 기존 C9-NB-01 partial mu_window theta metadata 의무와 중앙의 OPEN 의무는 그대로 남는다.
