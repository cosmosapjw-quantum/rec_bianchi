# 다음 대화용 고정 인계 — REC source synthesis

아래 블록을 복사할 수 있다. 마지막 전달 commit/source ZIP/provider ACK는 동봉된 delivery receipt를 우선한다.

```text
$physmath-research-loop로 cosmosapjw-quantum/rec_bianchi 연구를 이어가라.
먼저 고정 과학 판정과 계약을 읽어라:
https://github.com/cosmosapjw-quantum/rec_bianchi/blob/3678ce2ea24e0c2c57d156bde99a1c1fa1bccc47/research/rec_source_synthesis_20261027/ROOT_DECISION.json
https://github.com/cosmosapjw-quantum/rec_bianchi/blob/3678ce2ea24e0c2c57d156bde99a1c1fa1bccc47/research/rec_source_synthesis_20261027/CODING_CONTRACT.md
최초 인계:
https://github.com/cosmosapjw-quantum/rec_bianchi/blob/5dd414982c5c9ada97dfdfcc0b77cf83af86d66e/research/program_expansion_20261025/HANDOFF_KO.md

REC 완료 단위는 REC-SOURCE-SYNTHESIS-20261027, PR139:
https://github.com/cosmosapjw-quantum/rec_bianchi/pull/139
중앙 PR238:
https://github.com/cosmosapjw-quantum/rei_bianchi/pull/238
고정 중앙 DAG:
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/60b246beedf3536ecea0848aa74a23e4786eed58/research/orchestration_expansion_20261025/DAG.json

PR139의 마지막 FINAL_REPORT_KO.md/HANDOFF_KO.md와 delivery receipt를 읽어 source ZIP과 실제 Dropbox·Drive ACK를 확인하라.
각 노드 전에 최신 live HEAD·AGENTS·병렬 작업을 확인하되 완료 계산과 예산은 재사용하라.
원래 DAG는 working32/88, shared27/88, 이번 증가0이다. R/C20단계와 DAG88개를 혼합해 세지 마라.

이미 완료:
- 고정LAMDA parser:9levels,8radiative lines,collider2개,18pairs,54rates.
- 이전54DB/24LTE와 H5실제313query·626endpoint·314x313operatorbinding 재사용.
- 새HD24case+21controls PASS. exactsource delta와I=tanh(delta/2),
  D=expm1(-delta)/[-expm1(-xE)], independent80digit 및 두100digit검사.
- 원래35Hzgate7/8FAIL 유지. 온도50/100/200K 밖외삽·p/o-H2혼합 금지.
- 새history1240exactretimings+313Peanochords+30controls PASS,12causalrightskips.
  native-real clock과stored-geometric/roundedC를 구별.
- CODE_DECISION PASS. 구현참여없는 기존Astra reviewer재사용:
  새thread한도거절,priorR6context를 공개했고 fresh thread라 부르지 않음.
- GEO01원래111payload와S2/S3전달복구 완료; roots/matvec 재실행 없음.
- 새로컬통제CPU 측정합14.113983738초. WolframremoteCPU와일부metadata는UNKNOWN_NOT_ZERO.
- 이전실패·budget보존. 새총한도1020CPU초는이번단위용이며잔여를다음단위로이전하지마라.

물리 보류:
physical_epsilon=null,physical_outgoing_bound=null,physicalcoverage0/313.
ACTUAL_BOUND_INPUTS의state_enclosure/query_bounds는null.
실제F/Gcontinuousreconstruction,norm,initialerror,defect,modeldiscrepancy,L,
certifiedpositivetube,endpointK/reference,whole-cellphysicalcurvature가 필요하다.
엄격한E_upper<rho_lower유지. inverse-matrixrho를ODEtube로바꾸지마라.
H6/H7 OPEN,L4false,REIactivationfalse,globalphysicalcompletionnull.
PB01원primaryexit2실패와saved-vector8/8복구보존;patchedfullprimaryNOT_RUN.
전역CI는 RECquickverifierFAIL/pytestSKIP,central기존RustfmtFAIL/cargotestSKIP.
새표적과학검증PASS와구별하고현재PRcheck는다음merge전다시읽어라.

다음새단위는한도를먼저명시하고 actualphysicalH5producer의가장좁은구성
(F/Gsame-clockcontinuousreconstruction→actualdefect/stability/tube/curvature)을동결하거나,
same-fit고정밀HDsource deck을별도대안으로확보하라.
완료계산을재실행하지말고자료/백업을직접복구해사용하라.
Astra계약→lower-tier구현→구현과독립된검토를현재AGENTS대로수행하라.
각단계expected-SHA force=false게시,소스ZIP,Dropbox·Drive이중백업,
원래DAG계약보존 및 (완료)/(전체) 표기를이어가라.
백업·게시·필요한자동실행은기존사용자승인대로진행한다.
이 승인을 이메일/메시지발송이나자동merge로확대하지마라.
```

## 복구용 identity

| 입력 | SHA256 |
|---|---|
| LAMDA2289bytes |0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb|
| history35239470bytes |d4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1|
| SOURCE_CONTEXT220122bytes |5ccd8955bc9ea7484ddc1fca1dcf8b5a0a789e07c36ce0af3e692b959f002fe8|
| 기존HDparser |ef10b34e1891755334083340b84ff1e298151df720c13f008b3762505813e275|
| CODE_DECISION |ef280163d8a393c3a96bcb457e3781bf87dc5993b0fbb3341a0b4b86f13fc1de|

Source ZIP은 repo layout을 보존하고 privateLAMDA를 survey_literature/에 둔다.
복구 local HEAD는 R9일 수 있으므로 API 게시 HEAD와 같다고 가정하지 않는다.
기존dirty/untracked자료를 보존하고 필요한 고정자료만 회수한다.
archive 자체의 실제 ACK는 별도 delivery companion에 있으며 자기참조해시를 만들지 않는다.

