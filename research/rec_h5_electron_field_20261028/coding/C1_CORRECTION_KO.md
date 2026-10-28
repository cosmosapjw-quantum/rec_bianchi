# C1 source locator 교정

중앙 DAG28/88(+0), 단위11/20. Actual capture schema를 읽으며 R2/R9의 한 source locator를 교정했다. Coefficient temperatures는 QSS_WRITES가 아니라 WRITES.jsonl(id,slot,coefficient_TM_eV,coefficient_TR_eV)에 있다. QSS_WRITES는 real/virtual 및 radiation incoming/outgoing arrays를 담는다. 원본 WRITES1149615bytes,SHA2566de4bc263b0a78fe09cd4cddfdb7fc8fb23792fdab314ea71e7a9d0667203a2a를 입력에 추가했다.

이 교정은 자료 이름과 결속 경로를 정확하게 한다. R1 contract/R5수식/물리scope/수용tolerance/기존source결과는 변하지 않는다. 이전R2/R9본문은 이전commit에 보존되며 현재본문의 파일명만 최소변경했다. C5 binder는 LAST_WRITERS 및 CALLS/QSS_WRITES/WRITES를(id,slot)로 맞추고 native_path의final_writer_coefficient_temperatures와 대조한다. 구현 전 발견·교정한 locator finding이며 fresh C9가 실제 closure를 확인한다.

최신 중앙HEAD66ef9a0147a0573b77e74e151dc280ba2bd4b64c의 HE-TANGENT13 병렬 변경을 확인했다. DAG28/88,88nodes17edges,native-path backlink가 유지된다. 새 owner unit은 기존중앙내용을 변경하지 않은 상태로 진행한다.
