# C5 — 작성한 구현과 실행 전 인계

상태: SOURCE_WRITTEN_NOT_EXECUTED. C5에서 완전한 source-point adapter와 관측 generator, binding, 독립 검증, bounded C6/C7/C8 entry를 작성했다. 새 코드를 import·실행·syntax check·compile하거나 테스트하지 않았다. 실제 compiler/수치/plot PASS는 주장하지 않는다. C5 actual publication과 dual ACK 뒤 root가 C6를 승인해야 하며 C7/C8도 각각 별도 승인한다.

## 실제 파일 변경

| 파일 | Bytes | 역할 |
|---|---:|---|
| code/electron_field.c | 5631 | original initializer/assembly/solve/scalar를사용하는side-effect-freepointboundary |
| code/electron_field.h | 1029 | explicit scalar/incoming C API와output ABI |
| code/generate_observed.py | 2158 | immutable원본에서header+3valuehook만삽입하는deterministicgeneratedcopy |
| code/independent_validate.py | 12044 | 별도worker가작성한Decimal80sparseMX-S/parity,40/80·savedmutation·savedplot |
| code/observer.h | 389 | 472-event fresh diagnostics와value-only observer 선언 |
| code/run_stage.py | 7928 | CPU/AS/wall/singlethread/processfamilywatchdog,actualCPU/callledger와failurepreservation |
| code/runtime.py | 14863 | 16inputlocks,saved132writer/626endpointbinder,ctypesboundary,hexraw/nonmutation |
| code/stage_worker.py | 9983 | C6compile/bind/controls,C7primary,C8independent+9controls및savedplotworker |

총8code files/54025bytes. 정확한작성물SHA256은coding/C5_IMPLEMENTATION_MANIFEST.json에기록했다. Original8개와capture7+native_path,원ZIP,과학문서는변경하지않았다.

## 실제 구현 경계

C API는FULL/H_STEADY/He-neutral/xe=xHII/fsR=meR=1,unitlabel,dispatcher-origin,sourceidentity,shape/finite/domain을nativecall전에검사한다. 원temperatureprelude를1회적용하고localincoming과calloc블록을사용한다. OriginalpopulateTS_2photon→originalsolve_real_virt→원FHgrouping을따르며FH=Fe는이primaryscope로만명명한다. Historypointer를받거나historyinterpolation/write/fileIO를호출하지않는다. Originaltableinitializer의정규화와macros를재사용하고point전후input/tablebytes를직접대조한다.

Generatedcopy는원hydrogen.cSHA를검사하고header1개와diag0/이미계산된denom/이미계산된det의3value-onlyhook만삽입한다.Outside231diagonal은adapter에서solve직전에읽는다.Point-scopedTLSpointer는원pointer로복원하고freshoutput에472events·values/kinds/indices·finite/zero/minabs/Schur를기록한다. Extraassembly/solve는없다. Generator자체도C5에서실행하지않았다.

Binder는capture002의LAST_WRITERS,CALLS,QSS_WRITES,WRITES를(id,slot)로결속하고native_path의동일writer·global/localindices·He-neutralendpoints와대조한다. Exactbinding/geometricendpoints/query/alpha를수정하지않고313mapping/626refs를저장한다. 이binding프로그램은C6에서만실행하도록작성했으며C5에서실행하지않았다.

모든point는CAPI호출직전/반환직후journal을남기고실제입력hex,actualoutputhex,build/library/source/tableidentity를즉시개별raw파일로보존한다. Nativefailure에서도이미반환된raw를버리지않는다.Primary/controlbatch는4MiB분할,각파일은5MiB미만으로작성한다. Kernel진입뒤반환이없는attempt는실제countUNKNOWN으로기록하고자동재시도하지않는다.

## 정확도와 control 계획

필수FHgate는512eps64*S_F,독립sparseblockgate는4096eps64이며zero-scale규칙을유지한다. FH/xr/xvbitwisecount는별도관측값이다. 독립validator는exacthex→Decimal.from_float→80digits로B/C및band방향을직접재구성하고sourceC의residual계산을신뢰하지않는다. C8은대표0/66/131의40/80비교와savedB/Cswap,bandswap,solutionmutation을수행하도록작성했다. 이는solver재실행이아니다.

C6는valid2newkernel과invalid24cases(22APIpre-native거부+2binding거부)를계획한다. C7는exact132newcalls다. C8은대표3점각zero,-u,2u의9newcontrolcalls를계획하므로initial143calls이며146cap이내다. Signedincomingcontrol은물리spectrumpositivity주장이아니다. C8control은frozenresidualgate를검사하고incomingresponse/affinesecond-difference를실측supplement로보고한다. 별도affinitynumericalgate를만들지않았다.

## 명령과 자원 계상

Unitroot에서root의단계별승인후명령:

    python3 code/run_stage.py C6
    python3 code/run_stage.py C7
    python3 code/run_stage.py C8

C6compileflags는gccC11/O3/no-fast-math/ffp-contract=off및PIC/shared이며actualcompilerpath/version/command/log를기록한다. Compilechild도worker의wait4user+systemCPU에포함된다. Worker는RLIMIT_CPU(정수ceil의perprocesslimit),RLIMIT_AS512MiB,wall30s,singlethreadenv를갖고,parent는/proc의livefamily+waiteddescendantCPU를관측해group을중지한다. 이watchdog은tick-resolutionguard이며정확한수학적aggregatehardcap이라고주장하지않는다. 실제wait4CPU는실패도ledger에더한다.

총60CPU에는R7remote0.06227을먼저계상한다.Local59.93773remaining과C6=10,C7=20,C8validate/controls=20,plots=10allocation의최소값으로childcap을clip한다. FinalcumulativeCPU/callguard를record/state저장전에판정해실패를True로기록하지않는다.146callcap을넘는plannedlaunch나unfinishedAPIunknown은launch전중단한다. Parent/network/model/metadata/packaging미관측비용은UNKNOWN_NOT_ZERO다. 기존/foreign예산은closed·nontransferable이다.

## 미실행·남은 gate

이번C5의generator/import/syntax/compile/tableinit/nativecalls/tests/scientificbinding/remote변경은모두0이다. 코드는정적원문대조로작성했고수치outcome·성능·compiler성공은미관측이다. Concretefailure가나오면raw와actualcharge를보존하고root에반환한다. C6/C7/C8재실행·repair는root의명시승인때만수행한다.

Nativeadapter/binder/resourcewrapper는/root/delivery_implementation(requestedgpt-6.1-sol),Decimalvalidator/plot은별도lower-tier/root/delivery_implementation/electron_decimal_validator(requestedgpt-6.1-terra)가작성했다. 두runtimeidentity는NOT_OBSERVED이며C9Astra는작성에참여하지않았다.

Canonical28/88+0,separateREI33/88,reference313/313,physical0/313;physicalquery/K/M2/defect/L/tube/e0/epsilon/outgoingnull,H6/H7OPEN,L4false,REIactivationfalse,AUTO_NEXT_NODE=OFF_AFTER_THIS_SELECTED_UNIT. 이pointfield는whole-cellcontinuousdefect/full-statephysicaltube를공급하지않는다.
