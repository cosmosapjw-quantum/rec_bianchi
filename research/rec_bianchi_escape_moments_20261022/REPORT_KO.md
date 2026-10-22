# ANGULAR01: Bianchi 재결합의 국소 탈출확률 모멘트 축약
작성: 2026-10-22 UTC. 물리→코딩 순서, physmath-research-loop 1.3.0.
새 우주론 IVP=0, 기존 완료 계산 재실행=0.

## 1. 이번에 얻은 물리

고정된 등방 선 방출원과 모든 방향의 양의 팽창률을 가정하면,
유한 광학깊이의 평균 Sobolev 탈출확률은 같은 H와 선 계수를 가진
등방 값보다 커지지 않는다. 충분히 두꺼운 선에서는 평균을 H/C_S로
줄일 수 있지만 탈출확률의 사중극 모멘트는 2 sigma/(15 C_S)로 남는다.
그 평균과 텐서의 절대오차를 같은 최소 방향 광학깊이로 제한했다.

따라서 물리적으로 허용된 경우에만 각도 적분을 생략하는 코드가 가능하다.
이 단위는 광자 방출 순간의 확률 모멘트이며, 완전한 재결합 이력이나
물질/복사의 stress tensor, 전 우주 열역학적 폐쇄를 계산한 것이 아니다.
수식의 모든 전제와 완전 유도는 THEORY.md, 실행 전 기준은
FROZEN_CONTRACT.md에 있다.

## 2. 최신 결과를 종합한 선택
REC/REI의 접근 가능한 branch와 PR metadata는 407 refs/347 PR까지
pagination했으며 관련 source, DAG, handoff와 연결된 다른 5개 repo를 읽었다.
이것은 모든 branch의 모든 blob을 읽었다는 뜻이 아니다. Personal Context는
unavailable이었고 Drive dossier 목록은 1000건 제한을 만났으므로 과거 대화와
백업 전체의 완전한 전수 검토를 주장하지 않는다. 상세 범위/시각은
provenance/GITHUB_SYNTHESIS_KO.md 및 BACKUP_SYNTHESIS_KO.md에 기록했다.

이 종합으로 중복 후보를 제외했다.

- REC primordial HyRec/RECFAST/HMLA/FULL q=0와 방향별 spike donor가 이미 있다.
- REC119의126과 REI220의129는 별도 low-z cohort이며 합산하지 않는다.
- REC125 THERM02의별도8IVP는 이미 끝났고 exact복구 및 최종187Gitblob 대조도 끝났다.
- 새 REC PR126은 8기존case×64=512저장state의 C2진단이며 새IVP0이다.
  PR번호126과 REC119의실행수126은 서로 다른 식별자다.
- REI221의 최신73c5e00...은 metadata-only이며 기존 atomic/local-flow 결과를 재사용한다.
- REI222 successor DAG의 N1/N5/N7을 오래된 READY문구로 다시 실행하지 않는다.
- HE36 incoming-loss 모멘트, HH PHYS80 CI/CX축약과3ODE는 별도 결과다.
  PHYS81의 읽은 로컬 S0를 최종 완료로 올리지 않았다.

그 위에서 선택한 새 질문은 **기존 방향별 연산자의 각도 모멘트를 어느
범위에서, 얼마의 오차로 줄일 수 있는가**다. 관련 source에 동일 단위를
찾지 못했다는 bounded no-match가 선택 근거이며, 학술적 최초성 주장은 없다.

## 3. 원전과 코드의 실제 재사용
변경하지 않은 donor는 REC114
df95a074730ea0d13d609cf88d448f01f4a47ef1의
`hyrec_spike_transfer.py`이며 MIT license와 함께 vendor/에 보존했다.
SHA256=3d03c35299d529ecaac66f40f5fc78f14ec3099c057005762f112250ee19add9.
20개 새 scalar reference는 실제로 원본 class를 호출했다.
벡터 경로는 같은 expm1 감쇠식을 사용한다. beta=A/tau는 여기에 추가한
균일 source optical-depth 평균이라는 물리 전제를 분리했다.

[HyRec-2](https://arxiv.org/abs/2007.14114)의 유효 원자 구조와
[공식 코드](https://github.com/nanoomlee/HYREC-2)의 H 사용 위치를 확인했다.
line escape, d/dln(a) 시간 변환, diffusion/feedback의 H는 역할이 다르므로
함수 입력 H 전체를 H_n으로 대체하지 않는다.
[Chluba–Sunyaev](https://arxiv.org/abs/0810.1045) §3.2 식(35b)와
[Hirata–Forbes](https://arxiv.org/abs/0903.4925)의 방출/흡수 profile,
완전 재분배, 고립된 선, 준정상성 가정을 source boundary로 사용했다.

최신 확인 [Li–Zheng2026](https://doi.org/10.1093/mnras/stag1223)은 유한 cloud의
geometry/recoil/velocity-gradient 수송이므로 fitting식을 primordial Bianchi
계수로 바로 이식하지 않았다. Exa5회/요청결과26개, SciSpace1회/10행,
Wolfram evaluator2회 성공 기록을 보존했다. WolframContext의 오류는 별도
ERROR로 남겨 성공 수에 넣지 않았다.

## 4. 유도와 계산식
국소 orthonormal frame에서
\[
S_{ab}=\sigma_{ab}/H,\qquad t=C_S/H>0,\qquad
q(\mathbf n)=1+S_{ab}n^an^b>0,
\]
\[
\beta(\mathbf n)=\frac{1-e^{-t/q}}{t/q},\quad
B=\langle\beta\rangle,\quad
Q_{ab}=\left\langle(n_an_b-\delta_{ab}/3)\beta\right\rangle .
\]
S는 실대칭 tracefree이며 각도평균은 정규화된4pi평균이다.
Q는 탈출확률의 PSTF moment이다.

q에 대한 함수 b(q)=q(1-e^{-t/q})/t는
\[
b''(q)=-t e^{-t/q}/q^3<0
\]
이고 <q>=1이므로 Jensen으로 B<=beta(t)를 얻는다.
작은 shear에서는
\[
B=\beta(t)-\frac{t e^{-t}}{15}\operatorname{tr}S^2+O(\|S\|^3),
\]
\[
Q=\frac{2[1-(1+t)e^{-t}]}{15t}S+O(\|S\|^2).
\]
즉 평균의 첫 변화는 이차, 사중극의 첫 변화는 일차다.

qmax=1+lambda_max(S), r=exp(-t/qmax)라 하면
\[
B_0=1/t,\quad Q_0=2S/(15t),
\]
\[
0\le B_0-B\le r/t,\qquad
\|Q_0-Q\|_F\le\sqrt{2/3}\,r/t.
\]
B>=(1-r)/t이므로 실제 평균 B로 정규화한 오차도 제한된다.
\[
\frac{|B_0-B|}{B}\le\frac r{1-r},\qquad
\frac{\|Q_0-Q\|_F}{B}\le\sqrt{2/3}\frac r{1-r}.
\]
동결 epsilon=1e-8에서는 t/qmax>=18.420680753952364가 충분하다.
이것이 AUTO분기의 근거다. 이 상계는 국소 Sobolev식 안의
thick 치환 오차이며, partial redistribution/time memory/라인중첩의
물리 오차나 floating-point interval certificate가 아니다.

등방source 조건은 실질적이다. 방출원에 tracefree E의
w(n)=1+E_nn이 있으면 thick 평균은
[1+2 tr(ES)/15]/t로 바뀐다. 등방source의 선도 평균 상쇄를
임의 비등방 방출원이나 incoming field로 확장할 수 없다.

## 5. 실제 계산과 물리적 판별
9개 shear spectrum × t=10^-8..10^3의45점 = 405개 새 parameter row를
단 한 번 계산했다. 각 row에 일반2D 64×128 및128×256 규칙을 비교했다.
LRS는 별도의1D 64/128 적분과 대조했다. 독립 lab-frame 회전 oracle9개,
약한 shear4개와 scalar/input 검사를 별도로 기록했다.

대표값은 원래 attempt001의 저장배열에서 읽었다.

| S의 선택 | t | B | 같은 t의 등방 beta | 상대 평균 억제 | Q의 Frobenius norm/B |
|---|---:|---:|---:|---:|---:|
| LRS s=1.8 |1|0.5087173388|0.6321205588|19.52210196%|0.1672853208|
| triaxial(-.97,.27,.70) |1|0.5828811940|0.6321205588|7.78955282%|0.1059060786|
| triaxial(-.4,-.2,.6) |1|0.6189318955|0.6321205588|2.08641582%|0.0411034296|
| LRS s=1.8 |1000|0.0010000000|0.0010000000|roundoff수준|0.2939387691|

19.52%는 이 finite grid에서 관측한 최대 평균 **탈출확률** 억제다.
우주의 전자분율이나 재결합률 전체가 그만큼 변했다는 의미가 아니다.
두꺼운 선에서는 평균의 shear효과가 사라지는 동시에 정규화된 사중극은
약0.29394로 남는 예를 직접 확인했다. 원배열의1e-15규모 음의 Jensen gap은
부동소수점 잔차로 보존하고 물리적 증가로 해석하지 않았다.

AUTO는405점 중61점에서 해석식을 선택했다. 해당점은 일반 nominal
8192개의 각도 node 대신 폐형식을 사용한다. 이 수는 분기와 연산구조
절감이며 wall-time speedup benchmark가 아니다. 나머지344점은 원래
finite-depth 적분을 유지했다.

## 6. 검증과 실제 실패의 처리
첫 실행은1.718181322초, peakRSS32.496MiB에서405행을 모두 저장했다.
89개 standalone검사(그중 donor20개)는 모두PASS였다.
N64↔128 관측 차이의 최대는 B/정규화3.70693e-15,
Q_F/정규화8.74551e-15였고 동결기준1e-8보다 작았다.
LRS1D↔2D 최대차는 B2.16840e-15,Q6.02647e-15였다.
AUTO와reference 최대 관측차는 B7.08042e-10,Q4.77377e-10이다.

원 attempt001의 exit1/FAIL은 그대로 보존했다. 얕은 등방5점에서
(1/t−B)<=exp(-t)/t를 큰수끼리 비교해 반올림이 등호를 깨뜨렸다.
물리식이나 수용기준을 완화하지 않고 동치인
B + slack >= -expm1(-t/qmax)/t로 검사 표현을 고쳤다.
slack=2e-12 beta_iso의 동결값은 변경하지 않았다.
실패한5개 저장행의 재판정5/5PASS를 기록했고 나머지400개 기존PASS를 재사용했다.
전체405계산 또는 새quadrature를 반복하지 않는다.
최종 판정과 원FAIL의 연결은 results/attempt_001/FINAL_DECISION.json에 기록했다.

실행 전 독립 검토가 찾은 세 경계결함도 원코드/실패자료를 보존하고
한 수리 episode에서 수정했다: 큰t에서15t의overflow,
작은 nonzeroS제곱의underflow를exactzero로오인,
복소수LRS축의허용이다. 물리적 기준의 변경은 없다.
이후7개 off-grid 독립 적분의 최대차는 B8.55e-10,Q5.75e-10으로 통과했다.
이는 405생산grid와 별도이며 새로운 우주론IVP가 아니다.
독립 검토의 최종 판정은 PASS_AFTER_TARGETED_REPAIRS이며 열린 지적은 0건이다.
최종 PNG 3개와 실제 렌더한 PDF 3개를 확인했다. branch_map의 라벨 겹침은
그 그림의 PNG/PDF만 저장 CSV로 다시 그려 해결했고, 이전 그림과 renderer도 보존했다.
전체 기록은 evidence/independent_review/REVIEW.md와 REVIEW.json에 있다.

## 7. 다음 전체목표까지의 연결
현재 unit의 A/B/C와 큰 목표의 의존성은 DAG.json/GLOBAL_DAG.json에 있다.
다음 계산은 source-owned resolved line의 population/Einstein계수/에너지와
이 B,Q를 연결하는 계약부터다. 기존 HyRec compressed Tvv/feedback/diffusion
sector와 같은항을 두번소유하지 않도록 정확한row를 먼저고정해야 한다.

low-z축의 Li 최종 charge/state/energy yield,
actual radiation spectrum의 recoil/induced source,
물리적 daughter와 electron/neutrino/recoil/stopping 자료,
양방향 radiation/thermal/Einstein closure는 열린 별도 의무다.
그 후의 전역 수렴과 production승인도 완료되지 않았다.

Physical HOLD; REC U5 HOLD_9_FAIL/HOLD_8_FAIL; CLOSED_HOLD_NOT_RESET;
global convergence NOT_RUN; production NOT_APPROVED; REI_activation=false.
REI 최초 실패raw의 historical local-only 보존범위는 유지한다.


## 8. 단계별 게시·보존과 완성도

| 단계 | 완성 범위 | Git checkpoint | 백업 판정 |
|---|---|---|---|
| A | 최신 접근 가능 조사, 원전, 유도, 실행 전 수용 기준 | ac22ea90827e34b25aabe95d8c63618c915411ab | Dropbox/Drive 업로드 ACK 및 size PASS |
| B | kernel, 단 1회 405점 실행, 원 FAIL과 저장 5행 수리 | 503c90b96bf3090127dec6b0edf81c747d9d5193 | Dropbox/Drive 업로드 ACK 및 size PASS |
| C | 그림 3종, 독립 검토 1회, 결과 보고서, DAG, handoff | 이 문서를 포함하는 최종 PR127 HEAD | 커밋 후 실제 영수증을 PR127와 완결 패키지에 기록 |

A ZIP SHA256: eaf2f2abe6e26ae86c947a94f0260ccaf983bbdd4e15816d9627f76154b514a4.
B ZIP SHA256: 35462c4aaa7e4043e57e778ad03ee0bb9da818fb8f665bce4aa7827027869085.
A/B의 remote whole-byte readback은 NOT_RUN이다. 업로드 ACK/size를 전체-byte
일치로 올리지 않는다. C의 최종 Git/백업 판정은 게시 이후 생성되는 영수증을 따른다.

이번에 동결한 과학 산출물은 A/B/C 3단계 중 3단계를 완료했다. 이는 국소 연산자
단위의 완성도이며, 전체 Bianchi 재결합의 물리적 폐쇄 비율이 아니다. 전체 목표는
GLOBAL_DAG.json의 열린 source 및 coupling 의무로 표시하고 임의의 백분율을 붙이지 않는다.

그림은 [평균 억제와 오차 상계](figures/attempt_001/physical_bounds.png),
[남는 사중극](figures/attempt_001/surviving_tensor.png),
[AUTO 허용 영역](figures/attempt_001/branch_map.png)에 있다.
각 PDF와 그림에 실제 사용한 CSV 및 per-figure hash를 함께 제공한다.
[HANDOFF_KO.md](HANDOFF_KO.md)는 다음 대화에 그대로 복사할 수 있다.
