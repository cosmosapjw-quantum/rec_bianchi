# 다음 REC 연구 인계 — HD/H5 실제 구현 이후

이 문서의 containing commit과 `delivery/PUBLICATION_RECEIPT.json`을 먼저 읽는다. 해당 receipt가 없는 science snapshot에서는 게시·백업 완료를 추정하지 않는다. 원 고정 인계서 `HANDOFF_KO.md`와 기존 owner PR137은 변경하지 않았다.

## 현재 정본

- repository: cosmosapjw-quantum/rec_bianchi
- branch: research/program-expansion-20261025, draft PR138
- 원 base: 5dd414982c5c9ada97dfdfcc0b77cf83af86d66e
- 원 owner PR137: ea89c97abeb7a663a813f00e9aadddaf0b32a6a9
- 시작 문서: RESULT_HD_H5_KO.md, CLAIM_GATES_HD_H5.json, DAG_HD_H5.json, EXECUTION_FREEZE_HD_H5.json
- 실제 review: review/INDEPENDENT_DECISION.json
- HD 코드 SHA256: ef10b34e1891755334083340b84ff1e298151df720c13f008b3762505813e275
- H5 코드 SHA256: a797c75ad987cdaadd3c7ffc08888c3ae09ab4b02700c4b028291c938e4225b2
- H5 producer contract SHA256: fa257842447137c7d22fac1ca85e2b0453cf061bb5b6b9108844244c9280c666

## HD 완료 범위와 다음 노드

고정 LAMDA HD2289bytes/SHA256
0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb
에서9levels/8lines/2colliders/18pairs/54rates를 실제 파싱했다.
WU34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad의 Species.from_record를 재사용했다.
원249compilerchecks는 재실행하지 않았다.

parser/literal/unit/domain과 별도DB54/LTE24검사는 implementation-verified다.
원35Hz sourcegate는 line1(J1→0)의8.2410162Hz만 통과하고 line2–8은 실패했다.
최대는 line6(J6→5)의1827572.5607572Hz다. 원공급자livebytes도 고정본과 같다.
전체HD 원계약은 HOLD_SOURCE_DISCREPANCY_UNQUALIFIED이며
require_energy_frequency_bridge는 실패선들을 거절한다.
Source decimal,35Hz,128epsilon64,원실패를 유지한다.
Collision은 정확한50/100/200K만 지원하고 p/o-H2를 섞지 않는다.
Missingpair는zero가 아니며 vibrationassignment와 physicaluncertainty는null이다.

다음 실행은 원 CDMS/LAMDA의 일곱 line provenance·준위와 주파수의 fit/version/uncertainty를 대조하는 source-resolution 단위다.
한 열을 임의 재계산하거나 tolerance를 키워 원gate PASS로 만들지 않는다.
원 table 공개mirror는 추가하지 않았고 exact URL/hash를 이용한localingestion을 쓴다.
공개출처: https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat
고정중앙copy: rei_bianchi641a725ada4be27473069c2c35005a94c2ab0248의 research/orchestration_expansion_20261025/authority/molecular/lamda_hd_20261025.dat.

## H5 완료 범위와 남은 물리 입력

실제 원history35239470bytes/SHA256
d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1,
313queries/626endpoints/Ks314x313를 연결했다.
원z1099.9986525171403,T0=2.728K,nH0=.18745798773143102m^-3,
eta=ln(a),prefix5127,nativeWiendeparture를 유지한다.
SOURCE_CONTEXT SHA256:
5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8.

b_repr=|storednominal−exact geometric interpolant|는 실제source표현차이이고
최대2.806325270875912e-28이다. 물리defect/tube/curvature로 대체하지 않는다.
epsilon=b_repr+(1−a)eL+a eR+M2(q−L)(R−q)/2.
Tube는E_upper<rho_lower를 요구한다. tube_radius.upper-only 입력은거절한다.
기존KS inverse-defect rho와 ODEtube반경은다른물리량이다.

조건부 유도와 소비기 구현은 독립 검토됐다. 실제continuousboundcoverage는0/313,
physicalepsilon/outgoingbound는null이다.
현재실제packet은BLOCKED_ACTUAL_BOUND_INPUTS를 반환한다.
부족한입력은same-source F/G·continuousreconstruction/retardedstateclosure,
fixednorm/initialerror,whole-domaindefect/stability/certifiedtube하계,
reference/endpointrepresentation/whole-cellcurvature와실제proof다.
각field와다음sourceproducer출발점은h5_input_binding/BOUND_INPUT_CONTRACT.json,
README.md를따른다. 입력이있어도CONDITIONAL_BOUND_CANDIDATE_REVIEW_REQUIRED이며
독립물리내용심사와observableerrorallocation후에만physicaladmission을판정한다.

## 재사용·예산·복구

완료PB01/KS01/THERMO01/RESP01/LINE02/PR124및기존campaign을 replay하지 않는다.
PB01원primary exit2/FAILED와savedvectorrepair8/8PASS,
patchedfullprimaryNOT_RUN을보존한다.
현재단위 cap HD90CPU s/H590CPU s/review+integration60CPU s,각wall600s,
RSS1GiB,1thread였으며실제사용량은각receipt에있다.
남은allowance를다음단위로자동전용하지않는다. 새실행은새input·한도·정지조건을먼저명시한다.
UNKNOWN_NOT_ZERO와CLOSED_HOLD_NOT_RESET을유지한다.

원PB01S2복구:69336495bytes,
SHA256b43ec958374bb8ba97073c46355dc26131a64261cd5004fa64e65c6565da00d1,
Dropboxid:BSpOijBcT10AAAAAAD_-Dw,
Drive1eHZ_wuG_4J_mgDrBvtRGe2QBpx_kpCAw.
이번단위source/input ZIP과새이중백업의정확한objectID/크기는delivery최종receipt를따른다.
자료는연결source에서직접복구하며사용자에게이미있는자료재업로드를요청하지않는다.

각새노드전에최신AGENTS·실제HEAD·병렬owner/PR·백업을확인한다.
변경의존성만검증하고구현위임·독립검토후expected-SHA/non-force로게시한다.
현재사용자는백업·게시자동실행을승인했다. 별도merge/activation은수행하지않는다.
전체물리완료율null,L4_ready=false,PhysicalHOLD,
REC_U5HOLD_9_FAIL/HOLD_8_FAIL,globalconvergenceNOT_RUN,
productionNOT_APPROVED,REI_activation=false를유지한다.
