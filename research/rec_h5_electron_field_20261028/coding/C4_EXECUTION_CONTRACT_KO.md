# C4 — 실행 DAG, 명령, 자원 계약

중앙 DAG28/88(+0), 단위 내용14/20. 이 계약 뒤 C5구현을승인한다. Stage별게시와두provider최종ACK/size readback이완료되면다음stage로간다.

## 역할과 경로

Root Astra authority: frozen science/acceptance, failure classification, final admission. Lower-tier /root/delivery_implementation: implementation, bounded build/tests/runs,rawfacts. Requested executor gpt-6.1-sol; observedruntimeidentityNOT_OBSERVED. Fresh nonauthor /root/electron_c9_independent가finalcode/results를읽는다. Requestedreviewermodel gpt-6-astra; observedruntimeidentityNOT_OBSERVED.

Ownerrepo cosmosapjw-quantum/rec_bianchi,PR146,branch research/rec-h5-electron-field-20261028,immutable nativeparent29e8427fa02ae089b004bce13c3d29ef663c89b4. Allowednewpaths research/rec_h5_electron_field_20261028/**. Localunit /workspace/scratch/6b0500b5ac99/research_next_20261028/electron_field. 다른branch와원ZIP/source inputs는변경하지않는다.

## 구현 산출물

C5에서완전한pointAPI,deterministicobservation-sourcegenerator,pointdriver/binder,independentvalidator,minimalboundedstageentry를구현한다. Exactfilelayout은executor가단순하게선택하되publicentry는다음으로고정한다.

    python3 code/run_stage.py C6
    python3 code/run_stage.py C7
    python3 code/run_stage.py C8

Workingdirectory는unitroot이다. C6는한번의build,inputbinding및contracttests;C7는132-pointprimary;C8는savedoutputindependent80-digitresidual,대표3점40/80비교,필요한control및그림이다. C8의검증과plot은분리된boundedchild로실행할수있다. 명령과environment는rawreceipt에기록한다.

Build는원본hyrectools.c,generated-observedhydrogen.c,additiveadapter/driver만사용한다. History/main/captureframework/helium은linkentry에넣지않는다. Compiler는실제환경의gcc이며path/version을기록한다. Flags:
-std=c11 -D_DEFAULT_SOURCE -O3 -Wall -Wextra -Wpedantic -fno-fast-math -ffp-contract=off
및필요한include/PIC/sharedlinkflag를사용한다. Originalheader/table매크로는override하지않는다. Originalsourcewarnings는보존하고무관한warningcleanup을추가하지않는다. 추가ISA/fast-math/reassociation은사용하지않는다.

## 실행 DAG와 예산

C5 source complete → C6 compile/bind/contract → C7 rawprimary → C8 independentnumerics/controls/plot → C9 read-onlyindependentreview → C10source/delivery.

New scientificCPU cumulativecap60.0s. R7WolframreportedCPU0.06227s를이미계상했으므로localchildren총59.93773s이하이다. C6 build/testsinitialallocation10CPU;C7primary20CPU;C8independent/controls20CPU,plots10CPU를initialallocation으로사용하되각실행의hardlimit은실제남은cumulativebudget과의최솟값이다. Unusedbudget은같은unit내구체적repair에만사용한다.

모든localchild는RLIMIT_CPU와RLIMIT_AS512MiB,wall30s,단일threadenvironment를설정한다. OMP_NUM_THREADS/OPENBLAS_NUM_THREADS/MKL_NUM_THREADS/NUMEXPR_NUM_THREADS/VECLIB_MAXIMUM_THREADS는1. Timeout시childprocessgroup을종료하고실패stdout/stderr/resourceusage를남긴다. Actualchildrenuser+systemCPU를ledger에더하고,실패도차감한다. Parent/network/model/metadata/packaging의미관측비용을0이라고쓰지않는다.

Primary는exact132newpointcalls이다. C6validkernels최대2,invalidcontractcases최대24(사전거부시kernelcalls0). C8newcontrolkernels최대12이며대표점indices0,66,131을고정한다. 따라서initialnewpointcallcap146이다. C8의savedmatrixresidual/precision/mutation/plot은nativepointcall이아니다. 값의변화를사전예측한PASS로나타내지않는다.

## 실제 기록과 stopping rule

Rawprimary는hexvalues와callid/slot/sourceidentity를보존하고5MiB미만의파일여러개로나눌수있다. Rawresult/stdout/stderr는기존실패파일을덮어쓰지않는다. 결과요약은authoritativeR1/C3gate를사용하고원본bitwisecounts를보고한다.

Immutableinputmismatch,unexplainedparity/residualfail,resourcecap,phase/solver/closure변경필요시executor는원인자료를보존해root로반환한다. Root는한정된원인에대한최소repair를승인하고그영향검증만다시수행한다. Tolerancewidening이나oldcampaignrepeat는허용하지않는다. 추가review는구체적잔여finding에한정한다.

C9freshreview는diff,sourcebinding,실제472events,nonmutation,actual132parity/independentresidual,controls,resourceledger를대조한다. C10은completeinput/code/commands/results/figures/receipts를새sourcepackage로보존하고actualdualACK후닫는다. User가요청한현재unit은끝까지진행하며다음unit자동선택은OFF이다.
