# Codex handoff — 완료 결과부터 재개

```text
REC PR119와 branch research/rec-rei-hheli-sandbox-20261021의 최신 HEAD/tree,
마지막 Stage C/최종 보존 댓글과 정확한 HEAD의 CI를 먼저 읽어라.
Repo: cosmosapjw-quantum/rec_bianchi
Unit: research/rec_rei_hheli_sandbox_20261021/
과학/실행 게시 HEAD: 8509ef6ba713279134c98f9f47464aa879069755
tree: 15a8891913ae2a4a53654185d31929af1aef4050
Stage C CI39629774142/39629764139 모두 SUCCESS; 이전 in_progress는 snapshot.
Stage C 원격683파일 blobSHA/크기 PASS, ZIP27031588B, local683payload PASS.
ZIP SHA256 9eae3389f83082488f5fbae09b1371994996c87f9e25956b38e81c64d9c31bd6
Dropbox id:BSpOijBcT10AAAAAAD_hnQ ACK/size PASS, whole-byte NOT_RUN.
문서 마감 commit과 최종 ZIP/CI는 PR119 마지막 보존 댓글에서 별도로 고정하라.
필독: README_KO.md, REPORT_KO.md, THEORY_KO.md, DAG.json,
results/SUMMARY.json, results/CONTROL_COMPARISON.json,
evidence/PIPELINE_LAST_RUN.json, INDEPENDENT_*와 stages/.

실제 새 sandbox main125 + 별도 opacity-off1 = 고유IVP126 완료.
전부 z20→2, 193시각, 62상태. 완료125/1을 재적분하지 마라.
main 첫1개는 적분/NPZ 완료 후 NumPy bool JSON오류가 나서 출력만 복구했다.
old results/pilot/의 실패/부분JSON/NPZ 보존; 정상결과 results/pilot_v2/.
remaining124 새실행 + control1 새실행. first solver counts/time unknown=null.
기존 warm729/175/unified237/U4B/HE29도 complete_reused, 대기열0.

code/run_all.py --execute --workers auto 는 hash일치 완료 결과를 재사용한다.
최종 실제 wrapper receipt:
evidence/pipeline_runs/21e53c08e56a4f02b2cdfebd38d769c4/RECEIPT.json
4단계exit0, main125/control1 complete_reused, 새worker0.
저장보고서만 재생성: python code/run_all.py
자원계획: python code/run_pilot.py --plan --workers auto --output results/pilot_v2
새 가정/모형은 새manifest/output/identity. 실패나 allocation 삭제/탈취 금지.

실제 sandbox CPUquota8/RAM8GiB/4workers였다. NCP실행0.
NCP64core/128GB라면 actual quota/load/RAM/shared reservation을 읽고 자동배분한다.
필요시 --peer-reservations /shared/reservations; 다른세션 존재는 전역veto아님.
상세benchmark/기존완료case 재계산을하지마라.

물리축 Sigma_F=[0,.003,.03,.15,.6], signedPm=[-.0005,-.00025,0,.0005,.001],
signedPr=[-.0012,-.0006,0,.0006,.0012]. Frobeniusnorm,
ortho diag(-s,-s,2s), kappa_t=8piG/c^2 for p[J/m3], H[s^-1].
total=abs(Pm+Pr), Pr=Pgamma+Pnu; norm합금지. half-contraction=F/sqrt2.

21states=n;H1/D/T I–II;He3/4 I–III;Li6/7 I–IV.
n/T initial0, chargefractions=null; 전자는charge neutrality.
photo+caseA RR+DR, prescribed T=100+11900Q, Q=.5[1+tanh((7-z)/.8)],
isotropicUV5–200eV E^-2.5. isotope전자율동일은근사.
CI/CX/음이온/분자/fullionic-yield/열수지/광핵반응폐쇄를완료했다고하지마라.
LiI 1s+2s source재사용; unresolvedcore에너지를heat로하지마라.
바리온pi=0, massivecollisionless matter별도; gamma만actualne Thomson.
fm=.1은전체Omega_m의10%를비바리온Vlasov에배정한다는뜻.
off tau는potentialelectroncolumn이며실제collision0.
testfluidenergymax2.1940642e-8은globaldynamicalerrorbound아님.

새independent code/result/control/plot검토는각scope를읽어라.
재사용tangent과atomiccore 저자의참여를새독립감사로중복세지마라.
StageB CI는EOF빈줄2개로실패했고형식만고쳤다. 최신HEAD CI별도확인.
최종ZIP은local전체payload검증, DropboxACK/size와wholebyte상태구별.

다음후보≤3개(thermal/ionic-yield closure,CI/CX,largersweep)를비교했고
다음1개는source-bound thermal/ionic-yield closure로선택했다.
새 source/energyledger/유한수용기준부터고정하며현재결과재실행하지마라.
매단계backup/publish/progress/nextDAG를기록하라.
PhysicalHOLD, globalconvergenceNOT_RUN, productionNOT_APPROVED,
REC U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, REI_activation=false 유지.
```
