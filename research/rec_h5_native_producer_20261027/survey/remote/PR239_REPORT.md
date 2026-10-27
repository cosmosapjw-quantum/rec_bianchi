# CR 적분 반환의 REI 진단 포트 연결
## 판정과 완료 범위

이번 유한 이론·코딩 단위의 과학 판정은 **PASS_SCOPED_INTEGRATED_DIAGNOSTIC_CONSUMER**다. CR PR107의 실제 24개 적분 사건 반환을 unchanged native25와 별도의 retained-photon 수·에너지 포트에 연결했다. 기준밀도 quotient/JVP, 적분 사건의 clock 불변성, 입자 수·에너지 보존, 명시적 endpoint reference 사상을 유도하고 구현했다.

새 검사는 한 번 실행됐다. 실제 24개 case/source 대안에서 5,264개 assertion이 모두 통과했다. 독립 code/raw 검토의 blocker는0이다. R1–R10/C1–C10의 단계별 실제 게시·백업은 STAGE_LEDGER.json과 delivery/STAGE_BACKUP_RECEIPTS.json을 권위 기록으로 사용한다. 이 보고서 작성 시점 이후의 최종 archive SHA/ACK와 포함 commit은 delivery/FINAL_DELIVERY_RECEIPT.json에 별도로 기록한다.

**원래 DAG: working32/88, central27/88, 이번 완료수 증분0.** REC-COUPLED는 constructive partial이다. 전체망/L4는 false이며 global physical completion은null이다. 단계20/20, 독립 assertion수, 원88노드 집계를 서로 바꾸지 않는다.

## 1. 재개와 최신 조사

기준은 PR237 최종 `ee6746ab172f862dddfdec63b59e5e3707b59eaa`다. 그 source ZIP과 delivery ZIP을 실제로 복구했고, 각각 SHA256/bytes/CRC를 확인했다. 과학 계산은 재실행하지 않았다.

초기 관측 경계는 2026-10-27 14:57:40 KST다. REI279개와 공급자1,101개를 합쳐 **7개 저장소의1,380개 branch metadata**를 pagination 끝까지 확인했다. REI PR236개 전체 목록과 공급자 최근PR300개를 읽었고, 후자는 지정 cutoff보다 오래된 항목까지 도달했다. 모든 branch의 파일 본문을 읽었다는 뜻은 아니다. 변경된 공급자 원문과 실제 연구 입력을 선택해 읽고 source byte identity를 확인했다.

지정 REI Dropbox 폴더211개 항목은 recursive pagination이 끝났다. Drive 지정 폴더는230개 반환과 exposed continuation 부재를 기록했다. 최근 Library 변경20개를 확인했고, 대화 검색에서 발견한 연구결과는 원본으로 대조했다. 모든 대화의 완전한 export 및 게시되지 않은 desktop 상태는 확보되지 않았다. 사적인 비관련 대화 원문은 이번 공개 source에 포함하지 않는다.

실행 직전 단회 갱신 경계는 **2026-10-27 16:26:51 KST**다.

| 공급자 | 실제 새 근거 | 이번 연결의 사용 |
|---|---|---|
| CR PR107 | science4e72c89b…, deliveryec463db0…; 224RHS·24exports·754checks; owner20/20 | 24개의 적분 count/energy와 source qualification을 직접 소비 |
| WU | f949c21c…의 분자 정수식·원전 범위 진전 | 물리 rate/Q/energy/named-consumer 활성화 권한은 별도 |
| REC | d6dbe39a…의 HD/history 진단 루프 완료; physical coverage0/313 | 원래 물리 bound/null과 REI activationfalse 보존; 중앙 반환PR238은 별도 draft |
| HE | ac6042a6… 유지 | 기존 caloric 계약·HE101 소진 예산 보존 |
| BASS | 009a1238… 전달·복구 metadata; 과학 sourceaf14fc72… 유지; DL2는 별도 편광 사전 | 기존 transport 범위와 물리 radii/finite absorption 의무 유지 |
| VigilODE | selectedGit72836e…와 별도 V8 archive650assertions, domain-only | domain 조건 근거 보존; 같은 REI history의 enclosure로 확대하지 않음 |

중앙은5abe0d19…의CR owner return을 반영한27/88이다. 새 working branch는 PR237 위에 있으며32/88은 중앙에 병합되지 않은 scoped 집계다. WU가 별도로 제시한 strict COMPLETE-prefix 집계18/88도 분류가 다른 값으로 보존한다.

## 2. 실제 사건과 공급자 범위

사건은

```text
He4III(index12) + tagged fast electron
  -> He4II(index11,1s ground) + retained photon
```

이다. CR의 bath는 T=10000K, ne=.14cm^-3, nHeIII=.01cm^-3이며, HI/HII/HeI/HeII/HeIII=(.9,.1,.07,.02,.01)cm^-3다. Ground spontaneous, stationary heavy target/zero recoil, nonrelativistic scalar isotropic ensemble, conditional elemental-He→He4가 고정 가정이다. Photon native support는54.42…50000eV다.

실제 export의 nb, 노출시간, rate, instantaneous RHS, emission history, spectrum, physical heating은null이다. `finite_coupled_abundance_update=false`를 유지했다. 24개는 8개의 수치 case와3개의 source redshift를 조합한 대안이다.

입력을 다음과 같이 쓴다.

- A: 실제 적분 capture count [m^-3].
- K: 실제 fast kinetic removal의 양의 크기 [J m^-3].
- G: 실제 retained photon energy [J m^-3].
- I=54.42eV, eV_J=1.602176634e-19J.
- b>0: 소비자가 명시적으로 지정한 정규화 밀도 [m^-3].

입력G를 재계산값으로 덮어쓰지 않는다. 원래 공급자 조건 `|G-K-I A|/(|G|+|K|+|I A|)<=2e-13`을 검사한다. 누적 binding vector의 floating subtraction은 물리적 residual로 판정한다.

Source source_commit=b11b2e…는 이전 저장-chain 출처다. 실제 export가 포함된science4e72c89b…와 서로 구분한다. Exact export는91839bytes, SHA256c6da1e2f8a079c123ab218875c27bd6f5bc73beb5465832cc28a9275b455e1b1이다.

## 3. 구성과 보존식

native25 순서는 (Y[21],zeta,w_nt,w_ext,ell)이며 ell=log(T/K)다. 별도 photon 포트는 수와 에너지 두 성분이다. 직렬화27행은 진단 표현이며 새27state ODE client를 선언하지 않는다.

a=A/b, k=K/b, g=G/b라 두면

```text
DeltaY11 = +a
DeltaY12 = -a
Deltazeta = -a
Deltaw_nt = -k
Deltaw_ext = 0
Deltaell = 0
retained photon port = (a,g)
```

이다. 다른 species와 row0,5,6은 정확히0이다.

Native charge q11=1,q12=2이므로

```text
sum DeltaY = 0
q . DeltaY = -a
Delta(q.Y-zeta) = 0
Delta[(1+q).Y-zeta] = 0
B . DeltaY + Deltaw_nt + Delta w_gamma
   = (-I A-K+G)/b
```

다. 같은He4 isotope를 보존하므로 핵종 수와 baryon 질량이 보존된다. Thermal electron·particle count와 선택 모델의 thermal energy increment가0이므로 logT increment도0이다. Retained photon은 별도 포트가 한 번 소유한다. Signed external-transfer ledger w_ext의 의미는 유지된다.

## 4. 정규화 미분과 시간좌표

일반 interface 방향 dA,dK,dG,db는 signed finite 값이다. 예를 들어

```text
d(A/b) = dA/b - A db/b^2
```

이며 K와G에도 같은 quotient를 적용한다. 이들은 입력 moment의 interface derivative이며 공급자가 제공하지 않은 물리 파라미터 sensitivity를 의미하지 않는다.

일반 energy residual의 derivative도 반환한다. 보존 tangent의 조건은 dG=dK+I dA다. 이 조건 밖의 방향에서는 계산된 비영 residual derivative를 그대로 유지한다.

b=beta*r에 대해 density-like행0…23,25,26만 reference로 변환한다.

```text
DeltaX = beta DeltaZ
dDeltaX = beta dDeltaZ + dbeta DeltaZ
db = beta dr + r dbeta
```

이때 직접 proper-volume/r 사상과 일치하며 beta 의존성이 상쇄된다. logT24행은 밀도로 정규화하지 않는다.

적분 사건은 clock 변환에 불변이다. dη/dt=H일 때 연속 RHS의1/H와 delta-function의 H Jacobian이 상쇄된다. 따라서 적분 increment의 H derivative는0이다. PR237의 continuous RHS 변환은 그대로 유지하며 현재 진단 사상과 호출 종류를 구분한다.

변하는 reference의 별도 fixed-volume endpoint algebra는

```text
xplus = (rminus*xminus + Delta n)/rplus
dxplus = (rminus*dxminus + xminus*drminus + dDelta n)/rplus
         - xplus*drplus/rplus
```

다. 이 식을 실제 미제공 시간 이력으로 적용하지 않았다. 연속밀도의 기존 convention도 보존한다: dotr+3Hr=Rr, dotn+3Hn=S, Fx=(S-xRr)/r와 그 full quotient derivative. Rr를 단순 dotr로 바꾸지 않는다.

## 5. 실제 검사와 수치 결과

한 번의 capped 실행을 수행했다. 새로운 provider solve·source projection·spectral quadrature·ODE는0이다. PR219 bootstrap, 기존83, GRID044 opacity, PR221 conditional, PR233/235/236/237의 유지된 근거를 재사용했다.

| 검사 | 관측 최대 | 동결 기준 |
|---|---:|---:|
| 실제 source energy |1.2031443924538344e-16|2e-13|
| Algebra/Decimal/reference/endpoint |1.681255923043035e-16|2e-14|
| Native binding+fast+retained energy |1.4992796638549268e-16|2e-14|
| Mixed JVP vs centered FD |1.127517777594486e-10|2e-8|

검사 수5,264는 24개 대안에 대한 row별 assertion이다. Decimal50 값648행, JVP648행, 두 step의FD1296행, exactzero504행, reference288검사, endpoint1296검사, capacity96검사,192개의 오류 signature 등을 포함한다. FD는 각 대안의 한 mixed 방향과 h=2e-4,1e-4에 한정된다. 같은 사전 row-unit 척도를 사용했으며 max(1,tiny) floor를 쓰지 않았다. Full-Jacobian 또는 전 이력 인증은 주장하지 않는다.

누락된 fast 수, retained photon의 w_ext 이중 계상, 잘못된 thermalization, db/dbeta 누락,1/H 적용, endpoint drplus 누락, logT rebase 오류는 단위별 signature로 구별된다. 이는 오류 signature 검사이며, 별도 수정 solver 전체를 실행한 것으로 기록하지 않는다.

실제 z2.479,R80,N2048 원자료는 다음과 같다.

| chi | A [m^-3] | K [J m^-3] | G [J m^-3] |
|---|---:|---:|---:|
|1.5|4.771037369249283e-12|3.1650673192199686e-30|4.4763957994064925e-29|
|3|2.5685395097196222e-12|2.2109226306054705e-30|2.4606134822300983e-29|

b=1.4e6m^-3는 소비자 normalization fixture다. 원 공급자의 미제공 recipient nb를 이 값으로 채웠다고 해석하지 않는다. 상세 진단 벡터는 implementation/attempt01/ACTUAL24_MAPS.md/json에 있다.

## 6. 그림과 독립 검토

delivery/figures/CR_INTEGRATED_DIAGNOSTICS.png/pdf는 저장된24개의A와48개의FD residual만 사용한다. 점은3개의 source-z 대안이고 겹침을 피한 가로 offset을 축에 명시했다. 실제 이력선·uncertainty band·spectrum은 구성하지 않았다. 기존 source/진단 계산은 그림 작성에서 호출하지 않았다.

Root가 PNG를 실제로 읽었고, 독립 visual 결과는 review/VISUAL_REVIEW.json에 결속한다. 그림의4초 CPU 상한은 초과했고 PLOT_RECEIPT의within_limits=false를 보존한다. 유효한 saved-data 그림을 재사용하고 다시 렌더링하지 않았다.

C5는 별도 code-read PASS_SCOPED_PREEXEC, C9는 실제8개 raw identity·criteria를 읽은 PASS_SCOPED_CODE_AND_RAW다. 검토자는 이론에 기여했지만 consumer/checker/runner를 작성하지 않았다. 코드 실행자는 요청된gpt-6.1-sol override가 수락된 별도 agent이며, 내부 runtime model의 독립 attestation을 주장하지 않는다.

## 7. 자원·실패·예산

과학 childCPU.281091, wrapperCPU.045367678, tail.05를 합친 charge는 **.376458678 CPU s**다. Wall.305686018s,RSS12800KiB,exit0,stderr0bytes이며 frozen scientific resource bounds 안이다.

기존 누적 비용은 초기화하지 않았다. Main595.225063/600와NO_MORE_IVPs, HE101reserve0,V6closedlease, CR6.988054525/30의 별도 owner 예산을 보존한다. Working AGENTS가 승인한 원10/30 대비50%미만 temporary14.9/44.5만 사용했고, 단위 종료 때 원래 cap10/30으로 복원한다. 누적액이 원 cap보다 큰 사실도 유지한다.

별도로 보존한 작업 제한 초과와 실패는 다음과 같다.

- 복원 extraction.184582739CPU가 그 작업의.15 예상 상한을 넘었다. Source복원은 유효하며 과학 실행0이다.
- C9 read-only metadata 분류의 O(n²) scan 등을 포함한 기존.20 reservation subtotal은.229571720CPU였다. 초과.029571720을 추가 계상하고, 다음 closing metadata.25는 별도 prospective reserve로 기록했다.
- 그림 processCPU4.972565719, tail포함5.022565719가 지정4CPU cap을 초과했다. 전체 presentation 누적 상한과 별도로 실패를 남겼다. Font-cache 경고가 있었지만 원인별 시간 기여는 측정하지 않았다.
- 그림 script 작성 중 한 번의 parsing failure는 renderer 시작 전에 발생했다. 미측정 비용은UNKNOWN_NOT_ZERO다.
- DAG의 단회 metadata 갱신은 .154160372 CPU로 .06 예상치를 초과했다. 실제 비용은 closing .25 reserve에 포함하며, 원88개 노드·17edges 보존 검사를 한 번 수행했다.
- 독립 DAG 의미검토63/63은 통과했다. 검토 knownCPU.214802957은 .03 예상치를 넘었고, 두 번째 closing metadata 실제합계.380893178이 .25 예약을 넘었다. 초과.130893178만 추가 계상했으며 final root metadata.05를 별도로 예약해 planning known+reserve14.477120760을 유지한다.
- R3 Dropbox의 async source fetch 실패 후 동일 고정 ZIP을 다시 전송해 completion ACK를 받았다. 과학 source와 계산은 바뀌지 않았다.

최종 알려진 subtotal·explicit reserve와 archive cost는 BUDGET_STATUS.json과 최종 전달 영수증에 있다. 모든 도구·LLM·network·시작/종료·과거 미측정 비용을 포함한 전체 비용이 인증됐다는 뜻은 아니다.

## 8. 게시·백업·DAG와 다음 연구

새 branch는 research/rei-cr-integrated-return-20261027, draft PR239다. 각 단계에 expected-SHA/non-force commit과 immutable ZIP, Drive/Dropbox completion ACK를 기록한다. 단계 checkpoint는 중복 압축을 줄이는 incremental snapshot이며 이전 archive identity를 포함한다. 최종 source ZIP은 재현에 필요한 전체 소스를 담는다. 최종 metadata의 자체 ZIP hash/ACK는 만들어진 뒤 별도 Git receipt로 기록해 자기참조를 꾸미지 않는다.

DAG 변경은 중앙CR_N5의 새 owner return과 REC-COUPLED의 별도 crIntegratedReturnContract를 연결하는 범위다. 이전 selectedRuntimeContract/thermalAssimilationContract, 원88개ID·17edges·nested contracts·원 budget/gate를 유지한다. Central에32/88을 덮어쓰거나 merge하지 않았다.

다음 직접 연구점은 **실제 donor/recipient 상태와 일치하는 proper-time injection/history 계약**이다. 실제 recipient nb와 지원되는 source history를 받은 뒤 integrated diagnostic을 rate 또는 finite abundance update와 연결한다. Retained photon은 spectrum/measure와 opacity·transport가 추가로 필요하다. CR capture hazard를 physical stopping/thermalization nu로 사용하지 않는다. 같은 source/시간 범위의 BASS finite absorption/error radii와 VigilODE native client·tube residual/Jacobian/rounding 의무를 이어간다.

## 원전과 기록

- CR PR107 science: https://github.com/cosmosapjw-quantum/bass_cr/tree/4e72c89b714431eb4c6ae07def777bbf72a5ae4c/research/cr_heiii_ground_rr_20261027
- REI 기준 PR237: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/237
- Mao, Kaastra & Badnell(2017), A&A599A10, https://doi.org/10.1051/0004-6361/201629708. RR count와 kinetic-loss moment, Maxwellian thermal 가정의 맥락.
- Kotelnikov & Milstein(2019), https://doi.org/10.1088/1402-4896/ab060a. Abstract-level contextual intake.
- 실제 SciSpace/Exa 읽기 범위와 Wolfram 코드·출력: theory/SOURCE_FINDINGS.md/json 및 SYMBOLIC_CHECKS.json.

