# 조사 후속 종합 — 구현 진행 중의 최신 변경

조사 기준 snapshot은2026-10-28T09:00:44UTC의GitHub관련17repo inventory이다. 이후같은17repo의updated-desc PR목록을다시읽고모두그cutoff이전까지도달했다. 우리의PR146외에아래변경을확인했다. PR본문과추가로읽은source/status파일의확인범위를구별한다.

| 최신 항목 | 실제 읽은 근거와 확보 범위 | 이번 REC 단위에 대한 판단 |
|---|---|---|
| Central PR222 HEAD66ef9a0147a0573b77e74e151dc280ba2bd4b64c |새DAGblobac459abd24d5e6f9b8813d84d2a6fd1afe2a5f87과AGENTS직접읽기;HE-TANGENT13 local13/17 |canonical28/88,88nodes17edges,nativebacklink유지. 병렬내용보존 |
| REI PR243 HEAD48c5656c3ff396edf61390214c40cbdcc203f172 |PR본문,RUN_REPORT_KO.md,RUN_STATUS.json직접읽기.17상태201시점그림과별도n/T257시점조건부저장이력 |동일배경의ionic/nonthermalcoupledsource가아님. 기존IVP0회재실행,canonical28/88와working33/88별도 |
| BASS PR225 HEAD5e7b9e30961304870360f05c7447f66b9887ffd0 |PR최종본문. Frozen-reset conditionalfinitehorizonresponse와정확rationalremainder,18/20,distinct-authorR6/C9 NOT_RUN |후속conditionalerror방법후보. 실제RECcoupledF/modelerror/norm/tube공급으로취급하지않음 |
| BASS PR226 HEADaca22f4b7287b642d65caf2c820b681b76ab1309 |PR본문. Prescribedstaticlapse에서localinversefield/collisiontransport와12targetedtests;독립modelreview NOT_RUN |다른physics/state/clockfixture. RECsourcepointfield의대체입력이아님 |
| BASS_CR PR114 HEAD3230790ebeb2657c3a222a2bdc1d043b7d745492 |PR본문. Conditionalatomwiseenergy-sumsupport의R1/20시작;actualK/kernel/physicalnative25 null |현재선택unit와중복하지않고stateboundmissing유지 |
| WU PR150 HEADbb960c3c293c34b4567873fb4328143b16301e59 |R13closeout본문과0e6282010665bc9075e073cfd144c226d29e449b의SCIENTIFIC_ADMISSION.json직접읽기 |20/20,local27/42의syntheticconditionalaffineforcing/integralbound. ActualHD/state/density/clock미공급;central/physicaldelta0 |

REI PR243의추가자원은해당owner기록을따른다. Main595.225063/600 NO_MORE_IVPs는변하지않고,임시planning/presentation상한18/55는원래10/30으로복귀했으며기존charge를reset하지않았다. 이번REC새60CPU예산과합산/이전하지않는다. REI의조건부n/Tstock을다른ANGTHERM01ionictrajectory에임의로붙이지않는다.

## 백업 목록의 후속 완결

이전에남아있던실제cursor를재개해모두terminal에도달했다.

| 목록 | 이번재개페이지/반환항목 | 결과 |
|---|---:|---|
| Dropbox htt_base |51/30472 |terminal |
| Dropbox rei_bianchi |57/27367 |terminal |
| Dropbox rec_bianchi git자료 |6/3416 |terminal |
| Dropbox 원/bianchi recursive |202/107070 |terminal;104088기관측/중복,2982신규 |
| Drive Bianchi/CMB/thermal검색 |4/399,1/36,3/253 |모두terminal |
| Library Bianchi/REC/REI/VigilODE검색 |24/2384,43/4291,18/1756,3/245 |모두terminal |

Dropbox중복은fileid(없으면path),Drive/Library는각query의기존id를기준으로제거했다. 서로다른snapshot과겹치는query를단순합산해총파일수로부르지않는다. 이번재개에서새rate-limit오류0이다. 과거htt_base/rei실패원인UNKNOWN및실제로관찰된별도RATE_LIMITED기록은그대로보존한다.

Drive list_folder에는후속token/완결신호가없다는한계가남는다. Searchterminal은ZIP전수목록의증명이아니다. 다른대화는검색으로접근했고모든원문transcript를열수있는API는제공되지않았다. 목록전수확인과모든archivebytes/모든branch과학내용전수검증을동일시하지않는다.

## 선택 unit의 유지

새자료중ELECTRON-FIELD01의원sourcepointcomponent를이미대신제공하거나동결된R5수식을무효화하는근거는확인되지않았다. 따라서현재한unit을끝까지진행한다. 위진술은읽은자료범위의판단이며전역자료부재나strongno-go가아니다. Completedscience는재사용하고동일캠페인을다시돌리지않는다.

## 중복 제거한 보존 목록

survey/inventory의whitelist보존본은Git17repo/1823branch/1099distinctopenPR,Dropbox122004,Drive1568,Library7045고유metadata를담는다. 초기Git열린PR1100은수신rows수이며BASS PR127이두페이지에중복되었다. 1100수신rows와1099distinctPR을구분한다. 새PR146및조사후delta는별도GITHUB_DELTA_AFTER_090044.json에보존한다. ZIP/원문전체검증이나실제백업ACK로이metadata를대체하지않는다. Snapshot생성CPU5.576s는metadata비용이며과학60CPU계정에숨겨넣거나전체세션비용0으로취급하지않는다.
