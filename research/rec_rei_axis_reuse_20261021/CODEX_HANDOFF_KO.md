# Local Codex / NCP: 완료 pilot 재사용과 독립 성분 후속 작업

$physmath-research-loop

현재 REC PR116 및 REI PR213의 최신 source/receipt부터 읽어라. REC branch는 research/rec-rei-axis-reuse-20261021, reducer 실제source hash는453eee672e2a6d78bf0f76aa42f5453e68c1066cc561f5fe547be9e30e01e457, 코드/결과게시d2c0fbb5fa06dfc37db57876bb130ef8a4fa8a5d다. 최종문서HEAD는PR116에서읽고실행source와혼동하지마라.

REI729-case결과c8e9f67aa031ffb33a9b0347bdea61dbb01fb746, 배송d32cd99fa19c65aa1ca63dbc8aab8741834270e8를complete_reused로연결하라. C15owner80825585f9fe31d2ee0d5af545ada3fa1f52be72는변경하지않는다. 실제코드/입력CSV는전체archive또는Git+검증된upstream백업에서직접복구하라. CSV SHA256 c322453eed4c4c236ff19501ea6eca50353d6ebecc604a6cab9647b3a090255c. 사용자에게수동SSH/SCP/재업로드를요구하지마라.

목표: matter/radiation 별도pilot 그림과응답을소비하고, 실제미완료후속물리만실행한다. 완료된729,625/606,REC U4A/B,HE29reference/canary와기존benchmark를중복실행하지마라. warmC15와collisionless z20→4의행/계수를합치지마라. 현재729의재계산대기열은0이다.

1. 공개코드/저장CSV를읽는153축응답은approximation후보다. 576혼합끝점의사후비교는완료됐다. support153+sentinel90 설계는NOT_SUBMITTED이며보편적오차보증이아니다. 정확한반례는sentinel_counterexample.py에있다. 486예측값을exactsolver결과로표시하거나physicalgate를대체하지마라. 새source/시간범위/closure/resolution을채택하려면새유한계약과오차판정기준을먼저고정하라.

2. pi_m와pi_r를별도상태/출력/장부로유지하라. 같은normal tetrad와H에서S=sqrt(3)s/H, P_A=(8piG/c²)D_A/(sqrt(3)H²), 공개Sigma=|S|,Pi_A=|P_A|. total은signedtensor합후norm. half-contraction와Frobenius, kappa_t와kappa_E, massive matter와massless neutrino를혼동하지마라. 등방gas stress0은이closure의명시적가정이다.

3. 새실행이실제로필요할때기존SSH를사용하라:
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
키내용을출력하지말고현재host/affinity/cgroup/CPU quota/RAM/disk/기존lease와case receipt를읽어라. 이전ChatGPT 도구quota를localCodex의SSH실패로상속하지마라.

4. 다른Codex세션또는과학PID가있다는이유만으로전체작업을중지하지마라. 기존sharedexecutor의협력lease를재사용하고가용slot에독립case만배정하라. workers<=min(ready cases,사용자가승인한최대값,실제가용CPU slot,가용RAM으로허용되는case수). coordinator와다른lease의예약분을빼고같은case/source/config중복은차단하라. case내순차causal업데이트는유지하고 BLAS/OMP/MKL/NUMEXPR/Rayon내부thread1을기본으로한다. 자원0이면boundedwait/저장결과분석으로진행하며다른프로세스를kill/suspend하지마라. 준비immutable cache와compile산출물은identity일치할때만재사용한다.

5. REC reducer의60CPU/180wall/2GiB를다른REI/HElane의계약으로복사하지마라. 각lane고유cap·누적debit·deadline은보존하고새scope의유한allocation을명시하라. 같은작업의예산초기화와무제한자동retry금지. 상세benchmark는추가하지말고필요한물리/반례검사만수행하라.

6. 새코드의독립검토는이전producer감사와별개다. 이ChatGPT회차는12unit PASS+정확반례1+CAS+직렬검토이며새독립agent감사는NOT_RUN이다. Codex에서독립검토가가능하면그범위만수행하라. 결과를새branch/draftPR에게시하고stage별create-only백업ACK와실제readback을구분하라. PR merge/reset/clean/forcepush금지.

반환: 새로발견한receipt,실제source/tree/input/binary와명령/exit,EXECUTED/REUSED/NOT_RUN/BLOCKED,실제관측CPU/wall/RSS범위,그림/원시CSV,독립검토범위,DAG,PR/CI,provider별보존. 7축판정과다음ChatGPT handoff를포함하라. fullEoR/globalconvergence/physical HOLD,production NOT_APPROVED 및 REC원U5 HOLD는유지한다.
