# A_REC_EPOCH01 결과

독립 Astra 검토는 `PASS_SCOPED`다. 검토는 저장된 whole-history arrays와 source identity를 재계산했으며 새 HyRec 실행은 하지 않았다.

원본 October-2012 HyRec의 동일 input.dat·우주론·원자상수·복사·헬륨 cutoff·Peebles 처리를 유지하고 DLNA만 8.49e-5에서 4.245e-5로 절반화했다. 각 전체 history에서 z=20과 z=15.9를 동시에 추출했다. 과학 실행은 정확히 2회이며 각 exit=0, 과학 프로세스 합산 wall은 1.633596638초다. 추가 과학 실행이나 repair는 없었다. 접근 가능한 bounded-work harness 규칙 파일이 없어 HARNESS_UNAVAILABLE을 기록했다.

현재 결과는 PASS_SCOPED이고 독립 Astra 검토는 PENDING이다. 온도는 실제 Tm [K], xe는 ne/nH이고 H는 s^-1, 수밀도는 m^-3이다. 정련 결과에서 z=20의 Tm=9.39687908718226 K, xe=0.000204588262898049, ne=0.35517513145095936 m^-3이며 z=15.9의 Tm=6.1372311858930955 K, xe=0.00019954000421506553, ne=0.18054856527962435 m^-3이다. 전체 값과 ln(a), 보간 지지점은 baseline.json/refined.json에 저장했다.

정련 상대차는 z=20에서 xe/ne 1.764993e-7, Tm 1.005125e-7이고 z=15.9에서 xe/ne 6.304660e-7, Tm 1.066407e-7이다. 사전 고정 허용치 1e-4를 모두 만족한다. 독립 4-node Lagrange 복원의 최대 scaled 차이는 2.716731e-16으로 64eps=1.421086e-14 이하다. 전체 105859/211717 native node의 유한성, 전자분율 범위, 양의 온도, ln(a) 좌표를 확인했다. 전체 ln(a),xe,Tm 배열은 native_history.csv로 보존했다.

잘못된 epoch·우주론·Tm/Tgamma 출력·헬륨 매핑·과도한 정련차·DLNA를 거절하는 검사를 포함해 targeted tests 8개가 통과했다. 명령·exit·stdout·stderr·원본 archive/input/effective member/driver/runner/helper SHA는 evidence에 있다. 테스트를 두 번 수행했으며 마지막 테스트 실행 receipt를 저장했다; 과학 실행 수는 이에 영향받지 않는다.

헬륨 의미는 neutral-after-original-HyRec-cutoff이며 잔여 헬륨 이온화의 물리적 추론은 하지 않는다. 한 번의 시간간격 절반화가 continuum/global 모델 오차를 증명하지 않는다. Bianchi IC 채택, 저온 후속 물리 provider 연결, CR history, 전역 과학 admission은 HOLD다. 다음 전이는 독립 검토 후 별도 우주론/배경 매핑과 저온 provider 계약에 이 두 epoch를 제공하는 것이다.

재현 명령은 `python3 research/a_rec_epoch01_20261011/run_epochs.py --output NEW_DIRECTORY`이다. 기존 evidence를 덮어쓰지 않는다. 재현은 새 과학 실행 2회를 시작하므로 현재 작업의 추가 재현은 승인 전 실행하지 않는다.
