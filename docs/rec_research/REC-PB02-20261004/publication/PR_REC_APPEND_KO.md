## REC-PB02 (2026-10-04): 순수 수소 source-bound 참조 모듈

REI의 Peebles 환원 검증에는 외부 원자 연구의 추가 완결보다 실제 REC 소스의 통계인자·escape·thermal inverse를 결속한 실행 모듈이 먼저 필요하다. 기존 `rec_microphysics`에 독립 `hydrogen_peebles` API와 CSV probe를 추가했다. `x2`를 유지한 event RHS, 동일 순간 rates의 정확한 closure defect, 명시적 frozen-escape QSS 및 pinned HYREC PEEBLES one-T 수식 profile을 제공한다.

실행 검증: 새 H 20개 / 전체 crate 108개 PASS, 원저자 HYREC C 384점 대조 PASS, Decimal 70자리 별도 event oracle 24점 PASS. 최대 RHS flux-scaled 차 1.06e−14 (사전 기준 2e−12). 조건부 국소 Sobolev 각도 연구 42점/95 checks PASS. 독립 검토의 finite-shell Saha 지적을 수정하고 재검증했다.

연구 패킷: `docs/rec_research/REC-PB02-20261004/README_KO.md`. 여기에는 exact source lock, 사전 계획, 코드·CSV·로그·이론·검토·low-cost LLM용 handoff가 있다. upstream C는 재배포하지 않으며 hash-verified fetch/build helper로 원문 reference를 준비한다.

현재 REI 우선순위 FLRW02/F04는 보존한다. 이번 완료는 reference module과 점별 환원 검증이다. REI call-site, matched cosmological history, 일반 Bianchi RT, 가열/광자 closure 및 엄밀 error certificate는 다음 단계다. 기존 He/Case-A/원자 장기 gate는 그대로다. 이 PR은 draft 상태를 유지한다.
