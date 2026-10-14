# REC-BG-R9 2026-10-14: 유한 clock·전단 적분의 theory-to-native 연결

이번 호출에서는 `$physmath-research-loop`의 **R9만 선택**했다. R7B의 exact-real positive-rate Hermite 정리와 R8의 실제 102 accepted step error 진단을 최신 2026-10-14 BASS I–VII dossier 표기와 연결했다. 새 성과는 clock/shear local integral 계산식과 finite null energy/direction/Jacobian의 Lipschitz bound, 재사용 가능한 native interface contract, 독립 reference code + test다.

읽기 순서: `theory/REPORT_KO.md` → `theory/R9_DOSSIER_SUPPLEMENT.tex` → `contracts/REI_NATIVE_INTERVAL_INTERFACE.json` → `handoff/CODEX_HANDOFF_KO.md`.

로컬 검산: `python3 -m unittest discover -s code -p 'test_interval_reference.py' -v`; 추후 production integration은 이 테스트만으로 허가되지 않는다. 기존 archived dossier는 수정하지 않았으며 TeX fragment는 additive supplement다. SOURCE_IDENTITY, TEST_RECEIPT, NEXT_LOOP을 함께 확인하라.

이번 R9의 native subagent는 해당 dispatch tool 부재로 `NOT_RUN`. Wolfram 15.0.1의 새 symbolic residual 0은 확인했고, 현장 xAct 1.3.0은 로드 테스트로 버전을 확인했다. 신규 xAct projector 계산은 inline parser가 Global symbol shadow를 보인 뒤 안전 도구의 후속 호출 제한 때문에 완료했다고 기록하지 않는다. R7B/R8에 실제 저장된 xAct 검산과 혼동하지 않는다.
