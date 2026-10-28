# 복사 가능한 다음 스레드 handoff

```text
$physmath-research-loop $scispace $exa $wolfram
rec_bianchi 중앙 연구스레드다. REC_HD_JOINT_INTERVAL01을 인수해라.
BRANCH=research/rec-hd-joint-interval-20261029
SCIENCE_ANCHOR=c5962e15989d18325e0fe263120715a63783d3ed
PREFIX=research/rec_hd_joint_interval_20261029
FINAL_HEAD_AND_SOURCE_ARCHIVE=이 prefix의 FINAL_DELIVERY_ACK.json 및 원격 PR 실제 HEAD에서 확인

먼저 CONTRACT.json, THEORY.md, CODING.md, DAG_DELTA.json, NEXT_NODE_CONTRACT.json,
review/FINAL_CODE_REVIEW.json, FINAL_DELIVERY_ACK.json을 읽어 identity를 확인하라.
이론 R1-R10과 코딩 C1-C10은 현재 scoped unit20/20 완료다.
중앙 canonical28/88(+0), REC actual313 physical0/313, H5 epsilon=null,
H6/H7 OPEN, L4_ready=false, REI_activation=false, production=HOLD를 보존하라.
PR153 original HEAD의 C9 오류는 역사적으로 보존했고, 수정은 이 자식 구현에서 검증했다.

이번에 실제 확보한 원 LAMDA hd.dat는2289bytes,
SHA256=0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb.
SOURCE ZIP에는 private_inputs/hd.dat로 보존된다. 공개 Git에는 raw source를 넣지 않았다.
전체36개 연속구간 검사와 exact primal witness 결과를 재사용하라.
필요충분 closed enclosure theorem 및 lambda_min9137862803786/174896229,
maxsegment(5,6), 원 nominal infeasible 및35HzFAIL7/8은 그대로다.
최소 scale은 출력자릿수 모형의 진단값이며 허용오차 교체가 아니다.

다음 단일 의무는 CDMS2011v2 원 .cat/.egy/.par/.fit/.lin 바이트와
LAMDA 변환 lineage 복원이다. 현 공식URL은 이번 실행에서HTTP503을 반환했다.
c003501.cat의2019 mtime는2011 authentic identity가 아니다. v3를 대입하지 말라.
원자료를 확보하면 hash/version/QN/units/TAG/uncertainty/변환근거를 매핑한 뒤
근거에 맞춘 source-choice proposal과 바뀐 의존성의 최소 검사만 작성해라.
완료된 원 native/IVP/9x9 stationarity 및 과거 전체suite를 재실행하지 말라.
서비스 실패를 물리/수치 오류로 바꾸지 말고, 현재 호스트 runtime은 새로 probe하라.
단계마다 원격 commit과 create-only Drive+Dropbox ACK를 남기고
(중앙완료/88)과(작업완료/20)를 별도로 표기하라.
```

선택적 재현은 SOURCE ZIP을 푼 루트에서 다음처럼 수행한다. 이미 검증된 입력에는 반복 실행이 필요 없다.

```bash
python3 research/rec_hd_joint_interval_20261029/joint_interval.py --lamda private_inputs/hd.dat --output replay/joint.json
python3 -m unittest discover -s research/rec_hd_joint_interval_20261029/tests -p test_joint_interval.py -v
python3 -m unittest discover -s research/rec_hd_print_precision_20261029/tests -p test_regression_repair.py -v
```

표준 라이브러리만으로 계산·테스트가 동작한다. 저장된 그림 재렌더링에만 matplotlib/numpy가 필요하다. raw 없이 Git fixture만 사용하면 `raw_verified_this_execution=false`가 정상이다. 공급자 최종 ACK는 저장 성공을 뜻하며 원격 전체바이트SHA 재다운로드 검증과 구별한다.
