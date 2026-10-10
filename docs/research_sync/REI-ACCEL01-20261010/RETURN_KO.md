# REI-ACCEL01 repo별 반환 — rec_bianchi

2026-10-10. A_REC에서 선택 epoch에 맞는 residual electron/temperature IC를 실제 source에서 내보내십시오. PR82 z5.807 cold HyRec endpoint를 z20 IC나 Bianchi I provider로 재해석하지 않습니다. 이번 reduced baseline은 Q_i=0과.001 민감도를 명시했으며 이는 residual electron 계산의 대체가 아닙니다. 기존 Peebles/He 소스 및 원 연구의 검증 범위를 유지합니다.

실제 계산: mean-volume z20→4+, 최종14개 경우×16384steps. FLRW z50=7.32839548, z90=6.28138267, tau_segment=.03744182127. r_i=.1의 delta tau=-2.61122e-5. 독립판정 PROMOTE_SCOPED_REDUCED_HISTORY; full native CR/RCT/HH/thermal HOLD.

[중앙 보고서·DAG·재개파일](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/7530e0239a4d30e99bfeba68d4b4ddc0b78a2c18/research/broad_history_20261010) · [REI draft PR104](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/104).

본 repo의 마지막 실제 source pin: `b1213b09cab2c8d30678ae29a948ab7ad92d030f`. 이번 commit은 연구계획/입력 포인터만 additive로 게시합니다. 생산 연산자·gate나 기존 owner branch는 변경하지 않습니다. 다른 비공개 채팅 스레드의 실행 ACK가 아닙니다.

다음 node: A_REC. 변경 없는 옛 suite를 반복하지 말고 해당 node의 실제 source/코드/출력을4시간 단위로 checkpoint하십시오. 전체 원자 연구 완료로 해석하지 마십시오.
