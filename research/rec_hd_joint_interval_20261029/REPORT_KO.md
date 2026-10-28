# REC_HD_JOINT_INTERVAL01 — 연구 결과와 인계

2026-10-29 KST. rec_bianchi의 PR153 다음 자식 단위다. 이론 R1–R10 및 코딩 C1–C10을 scoped20/20으로 마무리한다. 중앙 DAG는28/88(+0), REC actual313의 물리 검증은0/313(+0)이다. 최종20번째 commit·양쪽 provider ACK는 자기참조를 피하기 위해 SOURCE ZIP 밖의 FINAL_DELIVERY_ACK.json에 기록한다.

## 실제 진척

원 LAMDA hd.dat2289bytes를 공식 HTTP200 응답에서 복원했고 SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`가 기존 고정값과 일치했다. 원문에서 추출한9 term +8 photon literals는 PR153의 공개 전사값과 모두 같았다. 이번에는 원바이트를 읽은 실행과 전사 fixture만 쓴 실행을 결과 필드에서 구분한다.

행별 rounding 조건을 공동 준위의 필요충분조건으로 확장했다. delta_j=100c(w_j-w_(j-1))-10^9nu_j, r_j=100c q_w,j/2, s_j=10^9 q_nu,j/2를 Hz로 정의한다. 모든 p<q에서

    |sum_(j=p+1)^q delta_j| <= lambda [r_p+r_q+sum_(j=p+1)^q s_j]

이면, 그리고 그때만, 모든 준위를 동시에 만족하는 closed enclosure 해가 존재한다. 증명은 interval reachability와 shortest-path difference constraints 두 방식으로 제시했고, 실제 해 또는 위반 구간을 반환하는 Fraction 구현을 작성했다. 닫힌 끝점은 rounding tie 규칙을 포괄하는 enclosure이며, tie-to-even의 정확한 출력 원상이라고 주장하지 않는다. 원 ground term에도 출력 half-quantum을 허용하는 기존 모형을 유지했다.

원 source의36개 구간에서 정확한 최소 scale은 `9137862803786/174896229 = 52247.340357384149...`, 최대 구간은(5,6)이다. 원 lambda1은 공동 호환 불가이며 처음 비는 reachable interval은 J2다. 최소 scale에서 재구성한 primal witness의8개 등식 잔차는 정확히0이다. 이 배율은 printing 모형의 진단 거리이며 원35Hz 허용오차를 바꾸지 않는다.

별도 비저자 심사는 기존 parser가 Infinity를 허용하고 새 output parent가 없으면 실패함을 재현했다. 최소9행 추가/1행 변경으로 finite 검사와 output-parent 생성을 고쳤고, 원 유한8개 delta 및35Hz7/8FAIL을 유지했다. 과거 PR153 원HEAD의 결함은 기록으로 보존하며, 수정의 채택은 이 자식 코드 identity에만 적용한다.

## 검증 근거

- 독립 Wolfram exact rational36구간 계산과 Python 결과 일치.
- 비저자 독립 Bellman–Ford 이론 제어1152개 일치. 이는 새 알고리즘의 유한 판별 사례이고 일반 증명은 THEORY.md에 따로 있다.
- root 통합 실행: 새 공동 구간13개 +수정 회귀4개, 총17/17 PASS, 실제 exit0.
- C9 비저자 심사: 실제 API와 다른 구현의 새29개 scale 판정 일치; 정확한 최소 scale은 feasible, 그보다10^-12작으면 infeasible;12개 nonfinite header 제어 거부; 원2289bytes·SHA·17literals 확인. blocking0.
- root가 실제36구간 그림을 열어 확인했다. 디지털 연구 진단 범위로 채택했고90mm 단폭 인쇄는 별도 단순화가 필요하다. 정확한 값은 JSON에 보존된다.
- 원 native/IVP/9x9stationarity 및 과거 과학 full suite 재실행0. C++probe는 호스트 기능 근거이며 이 과학 결과의 검증 근거가 아니다.

root tests+actual-source command의 측정 child CPU0.262409s, wall0.266414s, 최대childRSS13952KiB다. code-worker 및 reviewer 측정은 개별 receipt에 있다. 초기1152이론제어와 plotting/control-plane 비용 일부는 미측정이며0으로 합산하지 않았다. /usr/bin/time가 없는 환경 오류는 Python resource 측정으로 해결했고, 과거 예산을 재설정하지 않았다. 성능 우위나 전체 프로세스 누적 cap 충족은 주장하지 않는다.

## 조사 범위와 현재 의존성

REC의 최신30PR 메타데이터, 원격172branch refs(신규 자식 포함), 의존성에 해당하는 HD PR149–153 원문·코드, 관련 BASS/HE/CR/WU/REI 최신40PR 메타데이터, 이전 최신 HD Dropbox objects와 Drive metadata, 관련 현재 대화 검색 및 제공된 executor·figure 지침을 확인했다. 다른 소유자의 결과는 reservation/context로만 사용했다. 모든 비공개 대화·백업 내부까지 전수 열람했다고 주장하지 않는다.

실제 중앙 정본은 rei_bianchi `research/orchestration-sandbox-20261022`의 commit `4824eec8526185b6b866a5e7e0dabdc624b5543c`, DAG git blob `83280906f45287b183fdbea4ede4d1fcfacc5770`,88nodes/17edges다. 완료28은 기존 owner admission count를 보존한 값이다. status 문자열의 COMPLETE 접두사만 세어 과학적 채택 수를 재정의하지 않았다. 중앙 원문 global_physical_completion=null과 REC0/313도 구분한다.

현재 CDMS 공식 원파일7요청은HTTP503을 반환했다. Exa 원파일 추출도 실패했으므로 CDMS2011v2 original byte identity와 LAMDA 필드별 conversion lineage는 미확보다. 공식 directory에서 .cat2019mtime와 나머지2011timestamps를 확인했지만 이것만으로 source 진본성을 결정하지 않았다. 공식 LAMDA 페이지의 v=1서술도 추가 진동준위의 물리 입력으로 채택하지 않았다. 실제 SciSpace/Exa 결과는 discovery/provenance로 보존했고, 원자료 검증을 대체하지 않는다.

다음 노드는 NEXT_NODE_CONTRACT.json의 CDMS_V2_SOURCE_RECOVERY다. 해당 rawbytes를 working source service에서 확보하고 version/QN/TAG/uncertainty/변환을 매핑한 뒤 source-choice proposal을 준비해야 한다. v3대입·35Hz완화·mismatch를열로대체·production승격은 수행하지 않았다. H5epsilon=null,H6/H7OPEN,L4=false,REIactivation=false,productionHOLD가 유지된다. 중앙 노드 신규 완료는0이다.

## 단계별 게시와 보존

각 단계는 실제 별도 원격 Git commit과 create-only cumulative ZIP을 생성했다. ZIP은 원2289byte donor를 private_inputs/hd.dat로 포함하며 CRC와 모든 payload size/SHA를 검사했다. Drive success 및 Dropbox completed ACK를 확인한다. 일시적인 Dropbox polling INVALID_ARGUMENT 뒤 inventory에서 object 부재를 확인한 동일 immutable ZIP 재전송은 receipt에 보존했다. 원격 전체 파일을 다시 내려받아 SHA를 확인하는 검사는 수행하지 않았다. 공급자 ACK·metadata와 로컬 ZIP 검증을 그 범위로 보고한다.

| 단계 | 작업 완료 | 중앙 DAG | 원격 commit | 저장 상태 |
|---|---:|---:|---|---|
| R1 | 1/20 | 28/88 | [c1f2172c](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/c1f2172c1c2414c82217009beb697373e2fdb02d) | Drive ACK / Dropbox completed |
| R2 | 2/20 | 28/88 | [1a1f3956](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/1a1f3956b8badd692de125c11659d70101fe4710) | Drive ACK / Dropbox completed |
| R3 | 3/20 | 28/88 | [caf9661d](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/caf9661d57e9a7c8c0200df4736d6f4191309b32) | Drive ACK / Dropbox completed |
| R4 | 4/20 | 28/88 | [53b976b2](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/53b976b2c8593be14f61ee0dee362bc340e781c3) | Drive ACK / Dropbox completed |
| R5 | 5/20 | 28/88 | [4561a388](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/4561a3881933f6d613746fd5b74693483494d312) | Drive ACK / Dropbox completed |
| R6 | 6/20 | 28/88 | [cff504dd](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/cff504dd9688d4da99e20206bf089358cd4d00ac) | Drive ACK / Dropbox completed |
| R7 | 7/20 | 28/88 | [6c070b43](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/6c070b43c381dda27f95f5e1671f8cce86973bd6) | Drive ACK / Dropbox completed |
| R8 | 8/20 | 28/88 | [07a92db8](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/07a92db8b1be9b21a9a17f9ab833ca39735997b0) | Drive ACK / Dropbox completed |
| R9 | 9/20 | 28/88 | [ead3f110](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/ead3f110ece8ff406c5298173e7f0652b7e93274) | Drive ACK / Dropbox completed |
| R10 | 10/20 | 28/88 | [506c456c](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/506c456ceacd9aa8146eb270b1b06b10f28f83af) | Drive ACK / Dropbox completed |
| C1 | 11/20 | 28/88 | [61b4b6d5](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/61b4b6d56ae1dde2288cdbe83239db5ef0186dcc) | Drive ACK / Dropbox completed |
| C2 | 12/20 | 28/88 | [ae2ba966](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/ae2ba966abf005ec69460021198c98edad4a340a) | Drive ACK / Dropbox completed |
| C3 | 13/20 | 28/88 | [8e3bc44f](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/8e3bc44f335dc9ef81e086fc4c01e9ebcf2bc150) | Drive ACK / Dropbox completed |
| C4 | 14/20 | 28/88 | [d1cb8537](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/d1cb853758c7f6c9b4906d8dc2b2bd728623f437) | Drive ACK / Dropbox completed |
| C5 | 15/20 | 28/88 | [03971283](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/03971283730b610c5e354bdd7be82b89dcfa353b) | Drive ACK / Dropbox completed |
| C6 | 16/20 | 28/88 | [2ed2410e](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/2ed2410ef3cd7e7c45548d6b15ffb48cfbac8b64) | Drive ACK / Dropbox completed |
| C7 | 17/20 | 28/88 | [85412166](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/85412166783d3a3579d20dd2760f013c893deff8) | Drive ACK / Dropbox completed |
| C8 | 18/20 | 28/88 | [dbfb9825](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/dbfb982597bc3a6d5cacb543ba7c5f3150eaa7a0) | Drive ACK / Dropbox completed |
| C9 | 19/20 | 28/88 | [c5962e15](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/c5962e15989d18325e0fe263120715a63783d3ed) | Drive ACK / Dropbox completed |
| C10 | 20/20 | 28/88 | [acfccec8](https://github.com/cosmosapjw-quantum/rec_bianchi/commit/acfccec8fa40ac4f77db118ced10e57f2ed8951f) | Drive ACK / Dropbox completed |

[이론](THEORY.md), [코딩 계약](CODING_CONTRACT.json), [실제 결과](results/JOINT_CERTIFICATE.json), [독립 검토](review/FINAL_CODE_REVIEW.json), [DAG 변경](DAG_DELTA.json), [복사 가능한 handoff](HANDOFF_NEXT_THREAD_KO.md)를 함께 사용한다.

공식 원자료: https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat ; https://home.strw.leidenuniv.nl/~moldata/HD.html ; https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/ .

최종 SOURCE: `REC_HD_JOINT_INTERVAL01_C10_20261029.zip`, 259327 bytes, SHA256 `972e2e31683a3947ab582a687a63a4c048b12f4086a6ad41345effc1d547fcc2`. [Drive SOURCE](https://drive.google.com/file/d/1QFX2LBJH4zKW7ZKEKNXHbzjTtydV5rBP/view?usp=drivesdk). FINAL_DELIVERY_ACK.json은20단계 전체 ACK와 게시된4개 코드파일의 실제 Git blob 일치를 기록한다.
