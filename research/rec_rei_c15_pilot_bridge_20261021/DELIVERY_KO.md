# 오늘의 첫 warm LRS + H/He Sigma-Pi pilot

REC→REI 기여를 위해 기존 C15를 source-pinned 방식으로 재사용해 sandbox에서25 signed 초기상태×16단계=400행을 실제 계산했다. 상세 benchmark는 실행하지 않았다. source/data 그대로 유지한 per-worker rate/PCHIP/quadrature cache, exact affine 초기 Pi 좌표변환, 독립 case 병렬화와 shared-resource admission을 구현했다.

**범위:** non-tilted LRS Bianchi I subset, a=.1999→.2, gas 초기12000K. 일반 비축대칭이나 cold z20→4 full EoR가 아니다. NCP 실제 신규실행0, independent native agent0, production 승인없음.

## Identity

실행 adapter SHA25639204e1381b20fa666d13663702acd5d24af17d5856b8d9063da2b54fb534579; 이후 동일 bytes를 a38c9b5eb77229cfc526cf8b1ff085b93e31e8cc에 게시했다. Git blob642f26a580eeb9b968b313a097b47c4f88982644 remote 대조일치. C15 science f6a1c10aa6d3f7252a9e68a77c2c4b62c41e77f0, 원archiveSHA256a159546829ff963b354b2c8feaa5da8b5536363f870ce6a4d3a966746d9c06a4.

## 정규화와 물리

sigma=diag(-s,-s,2s), pi=diag(-D/3,-D/3,2D/3), D=Pparallel-Pperp[J/m³]. 주좌표는 SigmaF=sqrt6|s|/H, PiF=sqrt(2/3)kappa_t|Dtotal|/H², H[s^-1], kappa_t=8piG/c²=c²kappa_E. 원 C15 KAPPA=kappa_t/3다. 기존 half-contraction 좌표는F/sqrt2로 별도 출력한다. stress 성분의 signed 합을 먼저 구하고 norm을 취한다.

같은 norm이어도 상대방향이 중요하다. signedSigma0={-.002,-.001,0,.001,.002}, signedPi0={-.0004,-.0002,0,.0002,.0004}. norm좌표만 보면9개다. 초기 gamma/nu A를 같게 두고 massive fraction.1, massive initial A0,m/T30을 고정한다. W(mu)=1+A P2(mu),-1<=A<=2이며, D=D_bias+(Egamma+Enu)A/5에서 Pi 목표를 affine inversion한다. H초기²=Hbase²/(1-SigmaF²/6)다. Pi를 시간 전체에서 상수로 유지하지 않는다.

## 실제 결과

10 minimal tests PASS. case024의 원본 uncached control과 cached JSON 전체 물리값이 정확히 같다. 최초 tuple/list 표현 비교실패를 기록하고 같은 JSON 표현으로 수정했으며 numerical tolerance 변경은0이다. 원본 control은 원인분해 포함 총2회16-step 실행;25새pilot에 합산하지 않는다. donor 파일변경0.

최대 초기좌표 오차Sigma4.3368e-19,Pi5.4210e-20. 최대number ledger1.6653e-16/H,energy ledger7.1054e-15eV/H. 장부오차는 시간정확도 상계가 아니다.

- origin: T_end12192.125411605837K,xHII=.4087130751130805,Sigma_end1.17059e-23.
- Sigma0=0,Pi0=+.0004: Sigma_end1.9992091837645154e-7.
- signedSigma0=.002, signedPi0=+.0004: Sigma_end.001998675935999921.
- 같은Sigma,반대Pi: Sigma_end.0019982760942793263.

LRS shear식으로 d(signedSigma)/dln a=-(3+dlnH/dln a)signedSigma+signedPi. 초기전단0의leading prediction Pi0 ln(.2/.1999)=2.0005001667e-7과 새수치값이 가까우나, 이것은수렴증명이나오차상계가아니다. 작은기체Pi-dependentcontrast는새수렴검증없이물리적으로분해가능하다고주장하지않는다.

실제3-worker run001 CPU7.6931s(parent lifetime+waited children),wall5.819605006s(postrestore),worker lifetimeRSS129040..130328KiB. 비교baseline이없으므로speedup NOT_MEASURED. No aggregate peak claim.

## NCP 공유 실행

다른Codex PID를globalveto로사용하지않는다. affinity/cgroup조상/현재idle/RAM을관측하고cooperativeCPU lease,BLAS1,per-workerAS2GiB로독립case만배치한다. nominal memory admission은1GiB/worker+15%여유이며hardaggregatecap은아니다. NCP에이식시관측자원에따라폭을줄이고task-owned outer300s timeout을적용한다. 비협조프로그램과CPU독점예약을확보했다고주장하지않는다. 현재25case라64worker를억지로띄우지않는다. 영가용자원만finite대기후pending으로남긴다.

## 재사용 조사

REC U4B deliverydf95a074/sourcea09e1d24의새74443→74475반환을읽고재사용했다. 전체allocation회계UNRESOLVED를warmREI진입의불필요선행gate로만들지않았다. REI PR141/C15를선택했고 PR147canonicalresponse 및 initialPi21342736은다른모델로구분했다. RUN19c9deb933/BRPERF01e4c81332는prepared-rate/cache/pool원칙만참고했으며C15rateowner를바꾸지않았다. PR198 backlog144/246 및 BASS_HE완료reference4+canary1은재실행하지않았다. branch/PR/백업metadata와관련source를조사했으며모든private대화·모든파일전수완료를주장하지않는다.

SciPy solve_ivp/DOP853와parallel_execution,Pythonconcurrent.futures공식문서를조회했다. SciSpace의Einstein–Vlasov문헌은초록수준이며점근정리를이pilot에적용하지않았다. Wolfram은contractions6s²,2D²/3,2sD,P2평균0/제곱평균1/5,양의A[-1,2],inverse표현을확인했다.

## 보존 및 다음 단계

Stage1 archive2090812bytes,SHA0e38d6817d9519a51734469cbe4e412b6759802d2baa273fa1eedd22d29df3f0. Drive1fZ0Do6ZIg9E9bNDARPXyObSAhW8rjph3의전체원격readback일치. Dropboxid:BSpOijBcT10AAAAAAD_fTw는completedACK+providercontent-hash일치,독립readback은현재DNS실패로미완료다. 최종source+raw25case+CSV+그림+보고서+Codex/다음대화handoff는PR115최종보존댓글에서연결한다. README나PASS문자열을독립감사로세지않는다.

완료된25case를먼저REI결과에import하고그림을사용한다. 새platform검증이나과학조건변경이없으면재실행하지않는다. 다음실질적과학단계는cold구간의source/thermaldomain과Qa정합을맞춘별도결합이다. warmrate범위밖을외삽해서fullEoR로이름을바꾸지않는다.
