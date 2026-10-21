# Codex / next-chat compact handoff

$physmath-research-loop

REC PR115 research/rec-rei-c15-pilot-bridge-20261021의최신HEAD와최종보존댓글부터읽어라. 목적은오늘REI non-tiltedBianchiI의첫예비그림이며상세benchmark는요청하지않았다. 다른최신branch/세션결과를먼저확인하고완료된REC U4/R3S와geometry-onlysweep를반복하지마라.

원C15 archive는Stage1/최종묶음의 inputs/C15_SOURCE.zip, SHAa159546829ff963b354b2c8feaa5da8b5536363f870ce6a4d3a966746d9c06a4이다. 실제adapterSHA39204e1381b20fa666d13663702acd5d24af17d5856b8d9063da2b54fb534579, 게시commita38c9b5eb77229cfc526cf8b1ff085b93e31e8cc와동일bytes다.

이미sandbox에서25signed초기상태×16단계=400행을완료했다. warmgas12000K,a=.1999→.2,LRSsubset,Frobeniusnorm과half-norm/sign둘다출력한다. Pi는초기조건이고subsequent동적으로진화한다. massivefraction.1,m/T30,initialA0, gammaA=nuA인2Dslice다. 원본cacheOFF/cachedJSON전체물리값일치와10minimaltests를보존한다. fresh native independent agent감사는없다.

Stage1: Drive1fZ0Do6ZIg9E9bNDARPXyObSAhW8rjph3,Dropboxid:BSpOijBcT10AAAAAAD_fTw,2090812bytes,SHA0e38d6817d9519a51734469cbe4e412b6759802d2baa273fa1eedd22d29df3f0. 최종archive는추가댓글의ID/SHA를따르라. 사용자의수동재업로드를요구하지말고연결계정에서복구한다.

첫행동은결과수용이다. run001,endpoint/historyCSV,그림을REI하위연구폴더에hash/provenance와함께import하고draftPR로게시한다. warm결과를cold20→4/일반비축대칭/production으로승격하지마라. 다른세션의81/625geometrycase와서로다른source/closure를같은데이터로병합하지마라.

새NCP실행이필요할때만승인된localSSH를사용한다:
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p22
키내용출력금지. hostname/affinity/cgroup/RAM과완료receipt를현재확인한다. 타Codex존재를중지조건으로사용하지않고다른process를kill/pause/renice하지마라.

필요한단일boundedplatformpilot명령:
timeout --signal=TERM --kill-after=10s 300s python pilot.py --archive inputs/C15_SOURCE.zip --output <new-unique-output> --max-workers 64 --reserve-cpus 2 --steps 16 --leases /tmp/rei_shared_pilot_leases --run

실제경로/새allocation은Codex가정한다. timeout은이번taskprocessgroup만대상이다. max64는상한이고grid는25개다. 현재idle/quota/memory에맞춰폭을줄이며cooperativelease는비협조작업에대한exclusive보장이아니다. nominal1GiB와hardAS2GiB를구분하고여유가작으면낮은동시성을쓴다. BLAS1,순차causal이력,원tolerance를유지한다. matching완료결과는재사용한다.

검사는python -m unittest test_pilot.py 정도만실행하고benchmark/대규모수렴을새로요구하지마라. plot_results.py는이미있는run001만읽으므로적분없이그림을복원할수있다. 새코드·결과·DAG를commit/push,create-onlyDrive/Dropbox백업하며ACK와whole-readback을구별한다. oldUNKNOWN_NO_ACK는보존한다. REC PR115를merge하지마라.

마지막에는EXECUTED/REUSED/NOT_RUN/BLOCKED, source/tree/hash/argv/exit,7축판정과다음ChatGPTRETURNHANDOFF를반환한다. fullstellarQa,newtime/angularconvergence,production은미완료로유지한다. cold-EoR연결은temperature/sourceowner범위를먼저맞추는별도연구이며warmrate외삽으로대체하지마라.
