# rec_bianchi 연구 재개: 입사 복사에 대한 전자 변화율의 수반 응답

연구 단위: **REC-H5-ELECTRON-RESPONSE01**  
작성일: 2026-10-28  
소유 프로젝트: `cosmosapjw-quantum/rec_bianchi`  
범위: FULL / H_STEADY / He-neutral / xe=xHII / fsR=meR=1

## 1. 이번에 얻은 결과

선행 ELECTRON-FIELD01의 저장 계산점 132개에서 입사 복사 313개 성분에 대한 전자 변화율의 응답 벡터를 실제로 계산했다. 점마다 수반 선형계를 한 번 풀어, 모델별로 41,316개 응답 계수를 얻었다. 이 벡터는 고정된 열역학적 상태와 테이블에서 입사 복사 섭동이 전자 변화율에 전달되는 선형 함수를 제공한다.

동시에, 수학적 실수식으로 재구성한 source 계수와 기존 binary64 프로그램의 저장 source를 구별해야 하는 구체적 사례를 찾았다. 최초 모델은 수반 잔차·정밀도·독립 선형계 검산을 통과했지만, 저장 source와의 연결 검사에서는 9개 중 7개가 사전 기준을 넘었다. 이 실패를 보존하고, 원 코드의 연산 순서를 따른 binary64 source 재구성이 141개 기록의 44,133개 성분과 모두 비트 단위로 일치함을 확인했다. 그 재구성의 계수 prefix를 실수로 올린 별도 모델은 같은 source 연결 기준에서 9/9를 통과했다. 비트 일치의 대상은 마지막 곱셈·덧셈 반올림까지 수행한 source 재구성 경로이며, 실수 affine 모델 자체의 출력을 뜻하지 않는다.

따라서 이번 성과는 **명세한 두 실수 계수 모델의 incoming 응답 계산과, 그중 source-prefix 모델의 저장 native 자료 연결**이다. 전체 상태의 시간 미분이나 물리적 오차 상계가 완성되었다는 뜻은 아니다. 최초 실수식 모델의 source 연결 판정은 여전히 FAIL이다. 수치 근거는 `execution/C7_attempt001/RESULT.json`, `execution/C8_attempt001/RESULT.json`, `execution/C8_NATIVE_attempt001/{RESULT,MODEL_SUMMARY}.json`에 남겼다.

## 2. 재개 지점과 재사용한 근거

선행 단위의 과학 소스 commit은 `bc9fd57d41dcfc6aaa717bfd7f8e98846d10332e`이다. 이 재개 작업 중 다른 작업 흐름이 선행 단위의 C10 전달을 마쳤고, 최종 owner ACK는 `6cf3a19790b46aee4662be7048b49d47b628f39e`가 되었다. 후속 브랜치는 그 ACK 위에 쌓는다. 과학 입력의 기준은 처음 고정한 소스 commit과 해시 그대로다. 선행 단위의 C10과 중앙 반환을 이번 작업의 실행 성과로 세지 않았다.

완전 원본 ZIP `REC_H5_ELECTRON_FIELD01_C10_20261028_3e841711a381.zip`을 실제로 내려받아 16,076,171바이트, SHA256 `3e841711a3817dadfb46445ea22bcd1cf9e46aeb52d5270aca86333bd77c6ff2`, ZIP CRC를 확인하고 421개 member를 복구했다. 새 단위가 사용하는 입력 9개 파일, 합계 14,333,212바이트는 `INPUT_MANIFEST.json`에 원 member 경로·크기·SHA256으로 묶었다. 이 중 132개 primary writer와 9개 기존 incoming control이 수치 입력이다.

선행 원자료의 FH 132/132, xr 264/264, xv 41,052/41,052 bitwise parity와 native 풀이 잔차는 재사용한 근거다. 이번에는 native point 호출, 기존 producer, 전체 재결합 history 적분, 과거 캠페인을 다시 실행하지 않았다. 입력의 call_id/slot, 원 소스·라이브러리·테이블 해시, 물리적 phase와 단위를 검증한 후 새로운 수반 계산만 수행했다.

선행 자료와 공개 이론의 관계는 분리했다. HyRec의 effective multilevel atom 및 virtual-state radiative transfer 구조는 Ali-Haïmoud와 Hirata의 논문 및 고정한 October2012 C 소스에서 가져왔다. 수반 항등식 자체는 표준 선형대수이다. 여기서 추가한 것은 해당 소스에 맞춘 313개 입력의 배치, writer에 결속된 실제 응답 자료, 반올림을 포함한 저장 출력 차이의 분해이다. [논문: arXiv:1011.3758v2](https://arxiv.org/abs/1011.3758v2), [선행 PR #146](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/146).

## 3. 수학적 대상과 유도

전자 점장의 독립변수는 고정된 물리점 P와 incoming vector u로 나눈다. 시간 변수는 eta=ln(a), FH=dxHII/deta이다. u는 311개 virtual incoming occupation departure 뒤에 Ly0, Ly1이 붙은 313차원 벡터이다. 상태 X는 2s, 2p 및 311개 virtual unknown이며 모두 무차원이다. 저장 band와 블록의 의미를 보존하여

\[
M=\begin{pmatrix}A&B\\C&V\end{pmatrix},\qquad
MX=a+Gu,\qquad F=d+q^TX,
\]

\[
q=(\beta_{2s}/H,\beta_{2p}/H,0,\ldots,0)^T
\]

로 쓴다. 실제 저장 C 배열은 2×311이며, 수학적 하단 왼쪽 C 블록은 그 전치이다. V는 311×311 삼중대각 행렬이다. M과 G의 단위는 s^-1, q와 J는 무차원, 수반 lambda의 단위는 s이다. nH는 cm^-3, H는 s^-1, 온도는 eV를 유지한다.

고정 P에서 M이 정확한 실수 행렬로 가역이면

\[
M^T\lambda=q,\qquad J=G^T\lambda
\]

이고,

\[
F(u+\Delta u)-F(u)=J^T\Delta u.
\]

이 관계는 이 affine 모델 안에서 유한한 signed 섭동에도 정확하며, incoming 방향의 2차 도함수는 0이다. 작은 섭동 전개에서 고차항을 버린 결과가 아니다. 단, binary64의 단계별 반올림 사상 자체를 미분했다는 뜻은 아니다.

구조화된 풀이에서는 Z=V^-T B^T와 Q^T=A^T-C^TZ를 사용한다. 311차원 삼중대각 풀이와 2×2 Schur 풀이로 lambda_r를 구하고, lambda_v=-Z lambda_r로 복원한다. 역행렬을 명시적으로 만들지 않았다. 이 특정 분해에는 V의 가역성과 선택한 소거 과정의 정확한 비영 pivot이라는 추가 전제가 필요하다. 일반 수반 정리에 필요한 M 가역성만으로 그 전제가 따라오지는 않는다.

저장 band가 lower[b]=V[b,b-1], upper[b]=V[b,b+1]이므로 전치의 band는 lowerT[b]=upper[b-1], upperT[b]=lower[b+1]이다. 같은 index에서 lower와 upper를 교환하면 다른 행렬이 된다. 이 오류는 실제 negative control로 검출했다. 정확한 비특이성이나 구간 전체의 inverse-gain을 이번 수치 pivot 관찰로 인증하지 않았다. 상세 유도와 독립 R6 판정은 `THEORY.md`, `reviews/R6_REVIEW.md`에 있다.

## 4. 두 source 모델을 구별한 이유

### 4.1 최초 실수식 모델 G_real

저장된 유한 binary64 계수를 정확한 실수로 올리고, 고정 C 소스의 광학깊이 branch를 따라

\[
\Pi(\tau)=\begin{cases}
(1-e^{-\tau})/\tau,&\tau>\theta,\\
1-\tau/2+\tau^2/6,&\tau\leq\theta
\end{cases}
\]

로 정의했다. theta는 소스 literal 1e-6의 정확한 binary64 값이다. source의 비영 incoming 계수는

\[
G_{2+b,b}=V_{bb}x_1\Pi(\tau_b),\quad
G_{1,311}=3k_LH/n_H,\quad
G_{0,312}=3k_LHk_\beta/n_H
\]

이다. Ly0는 2p, Ly1은 2s 행에 들어간다. kL과 kBeta는 각각 소스 literal 4.662899067555897e15와 1.664786871919931의 정확한 binary64 lift이다.

이것은 명세된 실수 모델로서 일관되지만, 저장된 native M과 다시 계산한 정확한 exp 기반 Pi를 조합한다. 따라서 native source와 얼마나 일치하는지는 별도로 검사해야 했다. 512 eps64의 사전 source 연결 기준은 1.1368683772161603e-13이었다. 실제 최대 정규화 차이는 2.50906774683486e-13으로, 2/9 PASS·7/9 FAIL이었다. 이 기준이나 원 결과를 변경하지 않았다.

### 4.2 추가 source-prefix 모델 G_prefix

원 C 소스의 binary64 연산 순서를 따라 a_b64=fl(Vbb*x1), omega64, pi_b64=fl(1-omega64)를 재구성했다. 새 virtual 계수는

\[
(G_{\rm prefix})_{2+b,b}=L(a_{b64})L(\pi_{b64})
\]

로 정의했다. L은 정확한 실수 lift이다. 두 lift의 최종 곱에 추가 binary64 반올림을 끼우지 않았다. Lyman 계수도 RLya와 3*RLya*x1, 이어 kBeta를 곱하는 원 소스의 순서를 지킨 prefix를 lift했다. 이 모델의 정의와 검사는 새 실행 전에 `MODEL_COMPARISON_CONTRACT.md`로 고정했다.

저장 source 자체를 재구성할 때는 virtual source의 fl(fl(a_b64*u_b64)*pi_b64)와 real source의 원 grouping을 사용했다. 132개 primary와 9개 control, 총 141×313=44,133개 성분이 저장값과 모두 bitwise 동일했다. 이는 이 host의 math.exp와 연산 순서가 이 저장 자료의 출력에 부합한다는 관찰이다. 저장되지 않은 과거 중간값의 비트가 모두 동일했음을 증명하거나 다른 libm 환경으로의 이식성을 보증하지는 않는다.

M과 q가 바뀌지 않으므로 이미 얻은 132개 수반 해를 그대로 재사용했다. 전체 수반 문제를 다시 풀지 않고 J_prefix=G_prefix^T lambda를 계산했다. 두 모델의 최대 scaled 응답 차이는 1.1486118771814051e-13이었다. 동일한 source 연결 기준에서 prefix 모델은 9/9 PASS이며 최대 차이는 3.0139416037426664e-17이다.

### 4.3 실제로 관찰한 상쇄 오차

최초 모델의 각 대표점에서 worst row의 광학깊이를 조사했다. 모두 theta 바로 위의 얇은 광학깊이 영역이었다.

| Writer / virtual bin | tau | 원 연산 순서 Pi의 상대 차이 | -expm1(-tau)/tau 진단의 상대 차이 |
|---|---:|---:|---:|
| 0 / 11 | 1.4530392948732e-6 | -2.6095319471e-11 | -6.3430307764e-17 |
| 66 / 12 | 1.8502639083716e-6 | +2.3963626516e-11 | -4.5287308691e-18 |
| 131 / 13 | 2.9644998341622e-6 | -6.8768927128e-12 | +6.0939721584e-17 |

이 값은 1-exp(-tau)의 내부 뺄셈이 작은 tau에서 유효숫자를 잃는 설명을 지지한다. 외부 1-(1-Pi)도 존재하지만, 이 worst-row 진단은 얇은 영역의 내부 상쇄를 가리킨다. expm1 비교는 원인 판별용이며 production HyRec을 패치한 결과가 아니다. 전체 재결합 history나 관측량이 이만큼 변한다는 주장도 하지 않는다. 원 실패와 진단을 함께 보여 주는 그림은 `execution/PLOTS_attempt002/source_bridge_comparison.png`이다.

## 5. 실제 검증 결과와 의미

| 검증 | 실제 결과 | 해석 |
|---|---:|---|
| 모든 점의 독립 수반 잔차 | 최대 2.6227162888490522e-79 | 사전 1e-60 기준 통과 |
| Decimal80/120, prefix | 최대 scaled J 차이 1.2432792090687374e-78 | 대표점 0, 66, 131 통과 |
| 독립 SciPy 수반 풀이 | 최대 scaled J 차이 3.2323150286676381e-14 | 별도 sparse 행렬 조립과 풀이; 1e-10 기준 통과 |
| SciPy 수반 backward residual | 최대 4.2246186208044063e-16 | 응답 차이와 별도로 기록 |
| Primal 방향 검산 | 9/9 PASS, 두 모델 각각 | 세 점에서 Ly0, Ly1, alternating virtual 방향 |
| 저장 FH 차이와 prefix 예측 | 9/9 PASS; 최대 절대 차이 2.7796350070524013e-13 | termwise scalar scale에 묶인 기존 기준 사용 |
| 저장 source 재구성 | 44,133/44,133 bitwise 동일 | 141개 기록에 한정 |
| G_real source 연결 | 2/9 PASS, 7/9 FAIL | 실패를 그대로 보존 |
| G_prefix source 연결 | 9/9 PASS | 동일한 512 eps64 기준 |
| 바뀐 수반 해 / 잘못된 전치 / Lyman 행 교환 | 세 오류 모두 검출 | 의미 있는 negative control |

수반 잔차는 elimination 코드를 반복하는 방식이 아니라 원 M의 좌표를 독립적으로 조립하여 M^T lambda-q를 계산했다. SciPy의 직접 sparse 풀이도 구조화된 Decimal Schur 풀이와 알고리즘이 다르다. 그러나 두 검산 모두 수치 검산이다. 작은 backward residual만으로 정확한 forward error나 전체 영역의 비특이성이 증명되지는 않는다.

저장 native control 9개는 세 점에서 각각 원 incoming 벡터를 0, -1, 2배 한 자료다. 따라서 각 점에서 rank 1 방향을 검사한다. 이를 313개 native 입력 열을 모두 독립적으로 시험한 것으로 세지 않았다. 전체 벡터는 source에서 유도한 G, 전 수반 방정식의 잔차, 추가 primal 방향 검산으로 지지된다.

저장 출력과 예측의 차이는 별도 항으로 분해했다. r_i=M X_i-S_i, r_lambda=M^T lambda_hat-q, e_i=FH_i-(d+q^T X_i), epsilon_G=(S_c-S_b)-G(u_c-u_b)라 하면

\[
\Delta FH-\widehat J^T\Delta u
=(e_c-e_b)+\widehat\lambda^T\epsilon_G
+\widehat\lambda^T(r_c-r_b)-r_\lambda^T\Delta X.
\]

각 항은 scalar 반올림, source 재구성, 저장 primal 풀이 잔차, 새 수반 잔차에 해당한다. prefix 모델의 항등식 closure 최대값은 약 2.2744e-75로 1e-60 기준을 통과했다. 이 항등식 자체는 임의의 lambda_hat에도 성립하는 대수적 회계이므로, 단독 정확도 검증으로 사용하지 않았다. source 연결과 수반 잔차를 각각 별도로 판정했다.

## 6. 응답의 크기와 연구에서의 용도

prefix 모델의 점별 ||J||_1은 2.061882971775384e15에서 2.193136787518652e15 사이였다. 대표점의 분해는 다음과 같다.

| Writer | z | Virtual 311개 합 | Ly0 | Ly1 | 전체 ||J||_1 |
|---|---:|---:|---:|---:|---:|
| 0 | 1133.880017 | 1.9341725913e15 | 4.7855326133e13 | 7.9855054324e13 | 2.0618829718e15 |
| 66 | 1106.091309 | 2.0370778735e15 | 5.0392672198e13 | 8.4131133988e13 | 2.1716016797e15 |
| 131 | 1099.998653 | 2.0572032546e15 | 5.0916479084e13 | 8.5017053830e13 | 2.1931367875e15 |

원 실수식 모델에서 저장된 모든 J 성분은 양수였고, prefix 계수의 양의 비율 변화는 이 부호를 보존한다. 이는 해당 132개 점에서의 수치 관찰이며 일반 영역의 단조성 정리가 아니다. 큰 수치는 occupation departure라는 입력 좌표의 크기와 함께 해석해야 한다. 이것만으로 물리적 불안정성을 선언할 수 없다.

명세한 정확한 실수 모델에서는

\[
|\Delta F|\leq\|J\|_1\|\Delta u\|_\infty
\]

가 성립한다. 따라서 후속 복사 계산이 incoming 오차를 제공하면 전자 성분으로의 전달을 계산하는 데 사용할 수 있다. 다만 현재 얻은 점별 근사 ||J||_1의 최대를 그대로 물리적 Lipschitz 상수로 넣으면 안 된다. 계수 영역, 역행렬 이득, 실제 incoming 오차, 상태 norm과 시간 결합을 추가로 묶어야 한다. 그림의 선은 저장 점을 시각적으로 연결하며, 시간 보간이나 구간 enclosure를 제공하지 않는다.

## 7. 독립 심사, 실행 비용, 추적성

비작성자 R6는 원 모델과 prefix 모델을 각각 검토했다. V 분해의 추가 조건과 native control의 rank를 명확히 하라는 두 지적을 반영한 뒤 수학적 범위를 PASS_SCOPED로 판정했다. 별도 C9는 최종 코드·입력·저장 출력·판정 기준·실패 보존을 검토했다. 리뷰어가 새 수치 실험을 수행한 것은 아니다. 알고리즘 독립 검산은 작성자의 실제 실행이고, 비작성자 심사는 그 소스와 근거를 독립적으로 검토한 것이다. 관찰되지 않은 runtime model family 다양성을 주장하지 않는다. 정확한 심사 대상 해시는 `reviews/*_RECEIPT.json`에 있다.

과학 실행과 저장 결과 그림 생성은 이 단위의 별도 60 child CPU초 예산에 누적했다. 실패한 C8도 포함한다.

| 실행 | 종료 | child CPU초 |
|---|---:|---:|
| C6 계약·negative control | 0 | 0.723611 |
| C7 132점 수반 계산 | 0 | 3.457219 |
| C8 최초 모델 검증 | 2: source 연결 실패 보존 | 0.949657 |
| C8_NATIVE 추가 모델 | 0 | 2.764407 |
| PLOTS attempt001 | 0 | 3.799706 |
| PLOTS attempt002: 범례 위치 수정 | 0 | 4.172248 |
| 합계 | | **15.866848 / 60** |

잔여 known child CPU는 44.133152초, 가장 긴 child wall time은 4.200538초, 최대 RSS는 227,340 KiB였다. 각 child는 wall 30초, address space 512 MiB, single-thread 환경으로 실행했다. 새 native 호출은 0이다. parent·모델·네트워크·metadata·packaging 비용은 UNKNOWN_NOT_ZERO이다. 선행 단위의 4.704676초 예산이나 native 호출 수를 이 단위로 이전하거나 초기화하지 않았다.

추적성 한계 하나를 명시적으로 남겼다. 최초 다섯 실행 receipt에는 실행 당시 코드·환경 해시가 없었다. C9 시점 snapshot은 현재 코드, Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, glibc 2.39를 기록하지만, 이를 과거 실행의 환경 관찰로 소급하지 않았다. 이후 wrapper에 사전 snapshot과 hash를 추가했고, 그림 attempt002부터 적용했다. C9는 이 한계를 숨기기 위한 과학 재실행을 요구하지 않았다.

wrapper의 잔여 예산 정수 경계 문제도 future-only로 개선했다. 기존 ceil(remaining), hard=cap+1 방식 대신 floor(remaining)-1의 보수적 한도와 soft=hard를 적용하고 부족하면 실행을 거절한다. 이전 wrapper를 보존했다. 현재 실측은 충분히 예산 안에 있으며, 이 변경을 엄밀한 연속시간 CPU governor의 증명으로 표현하지 않는다.

## 8. 다음에 필요한 연구와 현재의 물리적 경계

후속 full-P 미분의 기본식은

\[
dF=dd+(dq)^TX+\lambda^T[da+(dG)u-(dM)X]+J^Tdu
\]

이다. 이번에는 마지막 incoming 항의 계수를 구했다. 나머지 항을 얻으려면 P를 구성하는 변수, xe=p 제약에 따른 dxe=dp, table interpolation cell, feature 선택, 광학깊이 branch를 고정하거나 경계에서의 편미분·단측 미분을 정의해야 한다.

특히 G_prefix는 각 고정점에서 정의한 실수 affine extension이다. P를 바꾸며 binary64 prefix를 다시 계산하는 반올림 사상을 그대로 보통의 미분 가능한 함수로 취급할 수 없다. full-P provider는 계수를 생성하는 실수식 또는 명시된 매끄러운 국소 extension을 정하고, native 계산과의 차이를 별도로 관리해야 한다. 이번의 작은 source 연결 오차만으로 그 문제를 생략할 수 없다.

시간 residual을 구성하려면 실제 trajectory와 incoming 시간 미분, 전체 결합 F와 선택한 시간 보간함수가 필요하다. 물리적 오차 tube로 가려면 초기 오차 e0, 모델 차이, domain에서의 coefficient/inverse-gain enclosure, 전체 상태 norm과 유효한 안정성 상계가 더 필요하다. 후속 단계를 자동 실행하지 않았으며 구체적인 수학 명세는 `reviews/NEXT_STEP_THEORY.md`에 남긴다.

이번 단위로 canonical DAG 완료 수를 올리지 않았다. 상속한 상태는 **28/88, 증가 0**, reference **313/313**, physical **0/313**이다. 별도 REI의 33/88을 합산하지 않는다. physical query, K, M2, defect, L, tube, e0, epsilon, outgoing은 null이며 H6/H7은 OPEN, L4=false, REI activation=false이다. 이번의 J 또는 ||J||_1을 이 빈 물리량의 대체값으로 넣지 않았다.

## 9. 재현 및 자료 안내

`code/incoming_response.py`는 검증된 저장 기록을 읽어 구조화된 수반 및 두 G 모델을 계산한다. `code/study.py`는 독립 행렬 조립·검증·그림 생성을 수행하고, `code/run_bounded.py`는 누적 자원 기록과 실행 한도를 관리한다. 완전 SOURCE에는 immutable 입력, 모든 real/prefix 응답 JSONL, 실패·성공 결과, 리뷰, 그림, CSV와 manifest를 포함한다. GitHub에는 검토에 필요한 코드·문서·요약·작은 raw 검증 결과·그림을 게시하며, 큰 원자료 전체는 SOURCE를 사용한다.

기존 execution 디렉터리를 덮어쓰지 않는다. 원 실험을 다시 실행해야 할 구체적 사유가 생기면 입력 해시를 확인하고 새 attempt 번호와 명시적 예산을 사용한다. 단순한 재개에서는 저장된 검증 결과와 심사 기록을 먼저 재사용한다. 원 C8의 비영 종료는 의도적으로 보존한 과학 결과이며 숨기거나 정상 종료로 바꾸지 않는다.

이 보고서는 SOURCE에 포함되는 과학 기록이다. SOURCE 자체의 해시와 최종 GitHub·Drive·Dropbox ACK는 업로드 후 생성하는 별도 `delivery/FINAL_DELIVERY.json`과 최종 전달 보고서에 기록한다. 이 문서가 ACK를 미리 보증하지는 않는다.
