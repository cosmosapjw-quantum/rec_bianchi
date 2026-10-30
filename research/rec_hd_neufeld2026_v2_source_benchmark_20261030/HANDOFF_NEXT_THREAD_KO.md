# REC HD Neufeld 2026 Source Benchmark | 다음 대화 인계

프로그램: `cosmosapjw-quantum/rec_bianchi`; 현재 단위 `REC_HD_NEUFELD2026_V2_SOURCE_BENCHMARK_20261030`. 원본 parent PR #168 HEAD `d2b1592f1b3f02e7db721fb89b57e19868532f07` 고정. 해당 본래 브랜치는 수정하지 않는다. 현재 새 단위의 최종 PR 번호/HEAD는 생성 후 `FINAL_DELIVERY_HANDOFF_KO.md`에 기록한다.

원본 자료는 GitHub 자식 브랜치 `research/rec-hd-neufeld2026-source-benchmark-20261030`의 `research/rec_hd_neufeld2026_v2_source_benchmark_20261030/source_originals/`에서 복원한다. 정확 원천 2026 `hd_lamda.dat` SHA-256 `f07f36fd56fe351fe4032235abbc863319b652838e635cd76bbf09664ce099cb`; 원본 FITS SHA-256 `0c7753e665c9b1c58c073c82181f94c26dc6ad0b2b92a763cb4e2e83e4e3d4a1`. FITS는 remote hash+10 selected cell만 저장되었고 전체 FITS 바이너리를 이 ZIP에 넣었다고 주장하지 않는다.

새 실험 원천이 아니라 원래 2026 Neufeld source 모델의 non-LTE 재현. 15개 levels, 14개 Einstein A, 105 para + 105 ortho H2 collision edges, 9 source T nodes, 5 H2 densities -> 45 model cases. SI 정확 상수와 2026 FITS 재현 컨벤션(1.4388 K cm) 각 45: 90개 물리 계산, 컨벤션당 photon line 630행. 원본 FITS 100 K의 5개 밀도 셀에서 max population absolute diff `4.3450842923675737e-10` (1.4388) vs `6.413771957425318e-6` (SI exact). 이 사실에서 내부 소스코드 사용 상수를 단정하지 않는다. 原 J1 2021 vs 2026 원천 충돌률 36 matched rows 및 10 cooling model cases.

내부 코드: `src/neufeld15.py`, `src/j1_rate_comparison.py`, `src/cdms_2011_fit_covariance.py`, `src/fetch_verified_sources.py`; `python -m unittest discover -s tests -v` 및 `python -O -m unittest discover -s tests -v` 각 12/12 PASS; `compileall` PASS. JavaScript/Mathematica 원본 완전 입력 계산과 로컬 Python synthetic/2level 테스트를 구분한다. 다른 저자 R6/C9 NOT_RUN, native subagent NOT_RUN.

초기·최종 DAG는 canonical `28/88`, REC physical `0/313`, REC-EXP-SPECTRAL PARTIAL 9/rank6/cycle3, historical owner 35 Hz FAIL7/8, H5 epsilon null, H6/H7 OPEN, L4=false, REI activation=false, production HOLD. `AUTO_NEXT_NODE=false`, NO MERGE, NO SOURCE DEFAULT MUTATION. New scoped benchmark 1/1 does not count toward canonical/physical DAG.

후속 자료: 원본 Neufeld v2 full FITS의 network-capable materialization과 NaN 보존 검산 확장; CDMS2011 SPFIT `.var` full-precision covariance 확인; Sung joint systematic/line-center covariance 확인; distinct-author R6/C9; owner-reviewed scientific admission. 새 노드 자동 시작 금지.
