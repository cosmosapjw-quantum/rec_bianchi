# REC-H5-BACKGROUND-JET01 — 별도 비저자 R6 이론 검토

검토자 task: `/root/fresh_r6_theory`  
선택 작업: 원 BGJET 이론·구간 kernel과 저장 종점 보충 정리의 독립 검토  
적용 규약: 사용자가 지정한 `physmath-research-loop` 내장 운영 규약 1.0.0, R6  
작성일: 2026-10-28 UTC

## 1. 판정과 검토 독립성

**원 BGJET 이론은 `pass_scoped`, 저장 종점 보충 이론도 `pass_scoped`로 판정한다.** 고정된 비-CAMB 평탄 배경의 정확한 실수 모형에서 부호, 차원, 미분식, 전체 셀 포함 논리가 일치한다. 보충 정리의 핵심인 \((H''/H)'\leq0\)를 아래에서 비음수 다항식으로 다시 유도했으며, 원 보고서의 moment 설명이나 CAS 잔차 0을 승인 근거로 대체하지 않았다. kernel 및 보충 변환의 이론을 막는 결함은 발견하지 않았다.

이 검토는 원 kernel, 원 packet, serial audit, 보충 packet을 작성하지 않은 별도 agent task에서 수행했다. 검토 입력은 원 불변 ZIP, 그 추출본 및 지정된 연구 정책이다. 새 보고서의 저자라는 사실과 검토 대상의 저자 여부는 구분한다. 실제 관측되지 않은 모델 식별자나 서로 다른 모델 사용 여부는 기록하지 않는다. 이번에 확보한 독립성은 **별도 task의 비저자 원자료 검토와 독립 유도**다.

두 판정은 다음 범위를 갖는다.

| 대상 | 확보한 결론 | 승계하는 전제 |
|---|---|---|
| 원 BGJET | 동결 계수의 배경 jet 식, 단조성, source convention 및 구간 합성 논리의 타당성 | 정확한 represented 입력과 명시된 Decimal primitive 계약 |
| 저장 종점 보충 | \(H'\) 증가, \(H''\) 및 \(H''/H\) 감소, 끝점 외피와 기존 구간의 교집합 포함성 | 원 저장 끝점이 같은 실수 함수와 같은 기하학적 좌표를 포함한다는 기존 생성 근거 |
| 저장 데이터 전체 행 | 이 검토에서는 기존 영수증을 재사용하며 생성·검산 코드를 정적으로 읽음 | 독립 C9의 실제 저장 자료 일관성 검사는 별도 작업 |

기존 10,681개 검사, 180자리 검산, reference/producer/native/oldtests는 재실행하지 않았다. 새 수치 평가, CAS 평가 및 과학 계산 child는 모두 0회다. 문서 읽기, 해시 산출, JSON 메타데이터 열람, 공식 산술 문서 확인과 본 검토 파일 생성만 수행했다. 과거 10,681 PASS는 과거 실행 근거로 보존한다.

## 2. 입력 identity와 유지 상태

원 ZIP은 `REC_BGJET_SAVED_ENDPOINT_REVIEW_20261028_2d4a37afb669.zip`, 2,247,738 bytes, SHA256 `2d4a37afb6690af8c44f48b94b84ffabce823a878a31ddd2cc3464c1ed7b072b`다. 실제 읽은 소스의 SHA256과 읽은 범위는 동반 `FRESH_R6_RECEIPT.json`에 기록한다.

| 핵심 자료 | SHA256 |
|---|---|
| `inputs/C5/code/background_jet.py` | `52e2ef1a95854b0f3b0ba4a7df942c8500d85b39b8e14e60d998ac8598103168` |
| `inputs/R2/vendor/interval80.py` | `9e9e86df600c2886076403aa39f7bcd20a9da2c7bda0abf88bfd0738fbd82bec` |
| 원 `BACKGROUND_PACKET.json` | `ef76dad7e592f5a9e9b3b1d6357c724cbca2a0359e16ce3977d14723cfdb6220` |
| `audit_saved.py` | `6ae0dc9dd74b0aa08e600a13783eac11f6bd3e19377bd471a50bb3be1dd0dcfb` |
| 보충 `TIGHTENED_BACKGROUND_PACKET.json` | `0c2c360f0917e05baf580cea4be41695e301742be82992e95ecbd2a6e9af1d62` |

사용자 고정 상태는 canonical 28/88, delta 0, 별도 REI 33/88, background reference 313/313, physical 0/313이다. physical query/K/M2/defect/L/tube/e0/epsilon/outgoing은 모두 null, H6/H7은 OPEN, L4와 REI activation은 false, AUTO_NEXT_NODE는 OFF로 유지한다. 원 scientific child CPU 15.403986초와 저장 audit child CPU 1.927305초는 각각의 과거 실행값이다. 새 과학 실행을 만들지 않았으며 예산 reset/transfer도 없다. 검토·문서·도구 서비스 전체 비용은 측정하지 않았으므로 `UNKNOWN_NOT_ZERO`다.

## 3. 원 source와 실수 모형의 결속

`inputs/R2/inputs/history.c`의 non-CAMB `rec_HubbleConstant`는 물질, 곡률, 암흑에너지, 광자, 질량 없는 neutrino의 밀도 항을 더한 뒤 원 normalization을 곱한다. 고정 `input.dat`은 \(\Omega_k h^2=0,w_0=-1,w_a=0\)을 주므로, 이 C 식의 **실수 산술 해석**은

\[
 u=e^{-\eta},\qquad \eta=\ln a,\qquad
 A=r u^4,\quad B=m_d u^3,\quad C=\Lambda_*,\quad R=A+B+C,
\]
\[
 r=c_\gamma T_0^4(1+c_\nu N_{\rm eff}),\qquad H=h_N\sqrt R
\]

가 된다. 여기서 \(m_d\)는 원 입력 `omh2`이며, 아래 확률가중 평균과 구별하려고 이름을 바꿨다. \(c_\gamma,c_\nu,h_N\)은 각각 원 literal `4.48162687719e-7`, `0.227107317660239`, `3.2407792896393e-18`의 binary64 represented 값이다. \(T_0,m_d,\Lambda_*,N_{\rm eff}\)도 원 `%lg` 입력에 대응하는 represented 값을 정확한 실수로 해석한다. 이 계수들의 곱·합은 실수 모형에서 정확하게 정의한다. C 중간 연산의 반올림까지 같은 객체로 취급하지 않는다. [원전: `history.c`, `input.dat`; 원 정식화: `inputs/R5/theory/THEORY_KO.md` 및 `inputs/R9/API_CONTRACT.json`.]

\(r,m_d,\Lambda_*\geq0\), 그 합이 양수이고 \(h_N,T_0,n_{H0}>0\)이면 모든 유한 실수 \(\eta\)에서 \(R>0\)이다. 따라서 이론적으로 사용한 함수와 모든 미분은 매끄럽다. 실제 구간 구현이 허용하는 유한 지수 범위는 별도로 적용한다. 배경 계수는 \(\eta\)에 따라 변하지 않는다는 가정이 필요하다.

\(\eta,u,R,m_d,\Lambda_*\)는 무차원이다. \(c_\gamma\)는 \(K^{-4}\), \(h_N\)은 \(s^{-1}\)이므로 \(H,H',H'',H'''\)는 모두 \(s^{-1}\)이다. \(g=H'/H\), \(g'\), \(q=H''/H\)는 무차원이다. 또한 \(T_R=T_0u\)와 그 \(\eta\) 미분은 K, \(n_H=n_{H0}u^3\)와 그 \(\eta\) 미분은 \(m^{-3}\)이다. proper time으로 옮기면

\[
 \frac{d}{dt}=H\frac{d}{d\eta},\qquad \dot H=H^2g.
\]

따라서 여기의 \(H''\)는 \(d^2H/dt^2\)와 다른 미분이다. 이 결론은 metric signature 선택에 의존하지 않는 스칼라 배경식 검토다.

\(n_{H0}\)는 `SOURCE_CONTEXT`의 저장 represented 값을 권위로 사용한다. C의 `11.223846333047*obh2*(1-Y)`를 실수 산술로 다시 평가한 값과의 차이는 원 packet의 `density_representation`에 별도로 있다. 이 차이를 지우거나 새로운 계수로 교체할 이유가 없다. `load_locked`와 `model_from_parameters`의 검사 조건도 이 모형과 일치한다. [소스: `background_jet.py`; 원 packet top-level metadata.]

## 4. 원 jet의 독립 유도

\(A'=-4A,B'=-3B,C'=0\)으로부터

\[
 R'=-(4A+3B),\quad R''=16A+9B,\quad
 g=-\frac{4A+3B}{2R},
\]
\[
 g'=\frac{R''R-(R')^2}{2R^2}
    =\frac{AB+16AC+9BC}{2R^2},\qquad
 q=g'+g^2,
\]
\[
 H'=Hg,\qquad H''=Hq.
\]

분자의 항별 전개로 \((16A+9B)(A+B+C)-(4A+3B)^2=AB+16AC+9BC\)를 직접 얻는다. 따라서 원 코드의 양의 분자 표현은 올바르며, 서로 비슷한 두 moment를 빼는 방식에 필요한 상쇄도 피한다.

독립적인 확률가중 해석에서도 같은 식을 얻는다. \(p_i=A_i/R\), \(n_i=(4,3,0)\), \(\mu=\sum_i p_i n_i\), \(v=\sum_i p_i(n_i-\mu)^2\)라 놓으면

\[
 p_i'=p_i(\mu-n_i),\quad \mu'=-v,\quad
 g=-\mu/2,\quad g'=v/2,\quad q=v/2+\mu^2/4.
\]

여기서 \(v=\sum_{i<j}p_ip_j(n_i-n_j)^2\)이므로 원 분자와 정확히 일치한다. \(0\leq\mu\leq4\)이고 \(v\geq0\)이므로 \(-2\leq g\leq0\), \(g'\geq0\), \(H''\geq0\)다. 이 유도는 `jet_u`의 모든 H 관련 반환식과 맞는다.

나머지 반환값도 직접 미분하면

\[
 T_R'=-T_R,\quad T_R''=T_R,\qquad
 n_H'=-3n_H,\quad n_H''=9n_H
\]

로 일치한다. `Gamma_bg_log_eta=-4-g`, `Gamma_bg_log_etaeta=-g'`의 부호는 \(T_R^4/H\)의 로그 미분에서 나온다.

열 전달식은 고정 \(b=1+f_{\rm He}\), 고정 \(C_T\), 미분 가능한 \(x_e(\eta)\), \(b+x_e\ne0\)에서

\[
 \Gamma=\frac{C_TT_R^4}{H}\frac{x_e}{b+x_e},\qquad
 \Gamma'=\Gamma(-4-g)
  +\frac{C_TT_R^4}{H}\frac{b}{(b+x_e)^2}x_e'
\]

이다. source의 \(Y=0.24\)는 \(f_{\rm He}>0\), 따라서 \(b>1\)을 주므로 물리 영역 \(x_e\geq0\)에서는 분모가 양수이고 \(x_e=0\)에서도 이 표현은 정칙하다. 이를 \(\ln\Gamma\)의 미분 자체로 읽으면 \(\Gamma=0\)에서 정의가 달라지지만, 코드의 두 반환 필드는 **배경 인자**의 미분으로 명명되어 있다. `history.c`의 `rec_dTmdlna`에는 별도 온도 분기도 있으므로, 향후 total thermal defect에 연결할 때에는 사용한 RHS 분기를 지정해야 한다. 현재 배경 공급자 판정은 실제 \(x_e'\)나 해당 분기 선택을 생성하지 않는다.

## 5. 보충 정리의 독립적인 다항식 증명

원 보충 문서의 moment 결과를 곧바로 전제하지 않고, 위 jet 식을 먼저 유리식으로 전개한다.

\[
 q=\frac{N}{4R^2},\qquad
 N=16A^2+26AB+9B^2+32AC+18BC.
\]

\(A'=-4A,B'=-3B\)를 직접 대입하면

\[
 N'=-128A^2-182AB-54B^2-128AC-54BC.
\]

따라서

\[
 q'=\frac{N'R+2N(4A+3B)}{4R^3}
 =-\frac{3A^2B+4AB^2+14ABC+64AC^2+27BC^2}{2R^3}\leq0. \tag{R6.1}
\]

모든 분자 계수가 비음수이고 \(R>0\)이므로 부호가 완결된다. 같은 분자는

\[
 4A(B+4C)^2+3B(3C-A)^2
\]

로도 쓸 수 있다. \(4-\mu=(B+4C)/R\), \(3-\mu=(3C-A)/R\)를 쓰면

\[
 q'=-\frac12\sum_i p_i n_i(n_i-\mu)^2
\]

가 되어 보충 문서의 식과 독립 전개 결과가 일치한다. 일반 moment 계산으로도 \(E[n^2]'=\mu E[n^2]-E[n^3]\)를 적용하면 같은 결론에 도달한다.

이제

\[
 H'''=H(gq+q')\leq0 \tag{R6.2}
\]

이다. \(H>0,g\leq0,q\geq0,q'\leq0\)을 각각 확보했으므로 곱의 부호에 숨은 전제가 없다. 따라서 \(H'\)는 비감소, \(H''\)와 \(q\)는 비증가한다.

### 엄격부등식과 등호

서로 다른 지수 성분 중 둘 이상이 활성화되어 있으면 (R6.1)의 분자는 양수이므로 모든 유한 \(\eta\)에서 \(q'<0\)이다. 하나의 지수만 활성화되면 \(q'=0\)이다. 한편 \(A+B>0\)이면 \(g<0,q>0\)이므로 \(H''>0\) 및 \(H'''<0\)이다. 따라서 순수 물질·복사에서도 \(q\)는 상수지만 \(H''\)는 엄격히 감소한다. 순수 \(\Lambda\)에서는 \(H\)만 상수 양수이고 \(H'=H''=H'''=0\)이다.

| 순수 성분 | \(g\) | \(g'\) | \(q=H''/H\) | \(q'\) | \(H'''/H\) |
|---|---:|---:|---:|---:|---:|
| 복사, \(n=4\) | \(-2\) | 0 | 4 | 0 | \(-8\) |
| 물질, \(n=3\) | \(-3/2\) | 0 | \(9/4\) | 0 | \(-27/8\) |
| \(\Lambda\), \(n=0\) | 0 | 0 | 0 | 0 | 0 |

모든 계수 0은 \(R>0\)에 위배되어 제외된다. 음의 계수는 가중치 양성을, 음의 지수는 \(q'\)의 제곱합 부호를 잃게 하므로 본 명제의 적용 조건에 속하지 않는다. 이 정확한 범위 제한을 불가능성·신규 no-go 주장으로 확대하지 않는다.

\(g'=v/2\) 자체의 단조성은 별도로 성립하지 않는다. 예를 들어 지수 \(0,n>0\)의 두 성분에서 양의 지수 가중치를 \(p\)라 놓으면 \(p'=-np(1-p)\),

\[
 g''=-\frac{n^3}{2}p(1-p)(1-2p)
\]

로 부호가 \(p=1/2\)에서 바뀐다. 이는 새로운 수치 시험이 아닌 해석적 조건 검사이며, 원 코드가 \(g'\)에 전체 셀 구간식을 사용한 이유와 일치한다.

## 6. 외향 반올림과 전체 셀 포함의 연결

### 원 구간 산술

`interval80.py`는 Fraction의 정수 분자·분모를 Decimal로 정확하게 받고, 나눗셈을 FLOOR와 CEILING으로 각각 시행한다. 합은 양 끝점, 곱은 네 모서리의 하향 최솟값·상향 최댓값, 나눗셈은 0을 포함하지 않는 분모의 역수 구간과 곱을 사용한다. 부호 반전은 `copy_negate`를 사용하여 조용한 정확한 부호 변경이다. 이들은 실수 포함함수의 표준 합성이다.

`exp`와 `sqrt`는 단조 증가한다. 각 입력 끝점에서 가까운 표현수로 반올림한 결과의 바로 아래·위 표현수까지 확장하면 정확한 함수값을 포함한다. Python 공식 문서는 `exp`의 정확한 HALF_EVEN 반올림, 정수·float의 정확한 Decimal 변환 및 이웃 표현수 연산을 설명한다. square-root의 HALF_EVEN 규칙은 Python 문서가 참조하는 General Decimal Arithmetic 규격에서 확인했다. [Python 3.13 Decimal 문서](https://docs.python.org/3.13/library/decimal.html), [General Decimal Arithmetic 1.70, square-root](https://speleotrove.com/decimal/daops.html#refsqrt); 확인일 2026-10-28.

이 검토가 채택하는 정확한 trust boundary는 **실제 런타임이 그 primitive 계약을 구현하고, 사용된 context의 precision·rounding·범위가 source와 같다는 것**이다. runtime 구현의 형식 검증이나 전수 검사를 새로 수행하지 않았다. 원 `THEORY_KO.md`도 primitive 정확성을 전제로 명시한다. 명시된 전제 아래 포함성은 확립된다.

NaN/Infinity, zero-denominator, overflow, underflow, subnormal은 실패 처리된다. 수학적 모형의 모든 유한 실수 \(\eta\)에서의 정의와 구간 구현의 수치 범위가 같다는 전제는 사용하지 않는다. source 범위에서 성공한 과거 결과를 보존하며 허용 범위를 벗어난 입력에는 포함구간을 만들어내지 않는 계약이다.

### 원 `whole_cell`

정확한 유리수 끝점 \(a<b\)에 대해 `I(ai.lo,bi.hi)`는 \([a,b]\)를 포함한다. 이 확대 구간에서 `jet_eta`를 합성 평가하므로 반환된 자연 구간식은 셀 전체를 포함한다. 같은 변수가 여러 번 나오는 의존성은 폭을 넓힐 수 있으나 포함성을 해치지 않는다.

원 코드가 \(H,T_R,n_H\)의 외피를 오른쪽 하한·왼쪽 상한으로 교체하고, \(g\)를 왼쪽 하한·오른쪽 상한으로 교체하는 것은 각각의 단조성으로 정당하다. \(g'\)는 원 전체 셀 구간을 유지한다. 더 좁힌 \(H,g\) 구간으로 \(Hg\), \(g'+g^2\), \(H(g'+g^2)\)를 다시 평가해도 포함성은 유지된다. 원 전체 셀 논리에 끝점 최대를 무단 가정한 단계는 없다.

### 저장 종점 보충

어떤 연속 함수 \(f\)가 \([a,b]\)에서 비증가하고 끝점 값이 \(E_a=[\ell_a,u_a]\), \(E_b=[\ell_b,u_b]\)에 각각 포함되면, 임의의 \(x\in[a,b]\)에 대해

\[
 \ell_b\leq f(b)\leq f(x)\leq f(a)\leq u_a.
\]

따라서 \([\ell_b,u_a]\)가 전체 셀을 포함한다. 비감소 함수는 \([\ell_a,u_b]\)를 사용한다. 이를 (R6.1)–(R6.2)에 적용하면 보충 코드의 방향은

\[
 H': [H'(a).lo,H'(b).hi],\quad
 H'': [H''(b).lo,H''(a).hi],\quad
 q: [q(b).lo,q(a).hi]
\]

로 모두 맞다. 저장된 유한 Decimal 문자열을 Fraction으로 읽는 변환은 정확하고, 기존 whole-cell 구간 \(J\)와 끝점 외피 \(E\)가 같은 함수의 전체 값을 포함하면 \(J\cap E\)도 전체 값을 포함한다. `audit_saved.py`의 `bounds`가 수행하는 `max(lo,oldlo)`와 `min(hi,oldhi)`가 이 교집합이다. 빈 교집합은 거부한다.

끝점은 `produce.py`에서 `jet_eta(a,model)` 및 `jet_eta(b,model)`로 생성되며 `points.L/R`에 저장된다. native z 비교는 별도의 `native_points` 필드다. 보충 코드는 전자를 읽으므로 clock을 바꾸지 않는다. binding의 \(a,b,q_{query},\alpha\)와 원 문자열을 보존하는 구조도 확인했다. 313개 행의 모든 저장 비교를 이 R6에서 새로 수행했다고 주장하지 않는다.

\(H'\) 폭의 변화가 1.0인 것은 구조상 설명된다. 원 코드의 양의 \(H\) 외피와 비양의 \(g\) 외피를 곱하면 하한은 왼쪽 \(H.hi\times g.lo\), 상한은 오른쪽 \(H.lo\times g.hi\)다. 이 조합은 바로 저장된 \(H'\) 끝점 외피와 같다. \(H''\), \(q\)의 과거 폭 개선 수치는 `audit001/SUMMARY.json`의 저장 결과로 보존한다. 그 수치와 313개 query의 180자리 점검은 위 전칭 포함 증명의 대체물이 아니다. 구간 폭이 양수여야 한다는 저장 audit의 검사는 이번 고정 packet에 대한 검사이며, 순수 \(\Lambda\)의 정확한 0폭 구간을 배제하는 수학적 전제로 쓰지 않는다.

## 7. exact-real, native, 물리 결합 범위

`jet_eta`는 정확한 represented \(\eta\)에 대한 \(u=e^{-\eta}\)를 평가한다. native harness는 저장 represented \(z\)를 받아 원 C의 중간 반올림을 포함한 H를 계산한다. 원 producer는 C 비교용 실수 식을 \(u_z=1+z_{represented}\)에서 평가하고, 기하학적 H와 그 값의 차이를 별도 bridge로 저장한다. 따라서 다음 세 대상이 잘 구별되어 있다.

1. 동결 represented 입력을 갖는 매끄러운 exact-real 배경 함수.
2. 같은 represented z를 입력한 native C의 유한 정밀도 결과.
3. 동결 배경 공급자가 아직 제공하지 않는 전체 coupled physical certificate.

고정 512\(\epsilon_{64}\) tolerance의 940개 C 대조는 저장된 point parity 근거다. 이 tolerance를 무한개 native point의 엄밀한 반올림 상계로 사용한 단계는 없다. geometric-native bridge 역시 initial error나 물리 불확실성으로 재명명하지 않는다. 배경 \(H''\)의 포함구간은 해당 스칼라 함수의 곡률 입력이며, full-state physical M2의 정의나 값은 이번 입력에 공급되어 있지 않다.

## 8. 발견 사항과 최소 교정

### F-R6-01 — 질의 행과 서로 다른 좌표 셀 수의 표현

- **대상:** `REPORT_KO.md`의 “313개 source cell” 표현과 보충 폭 통계의 `cells:313` 설명.
- **관측 근거:** 원 `inputs/C8/evidence/NUMERICAL_FINDINGS.json`은 `rows:313`, `unique_coordinate_cells:89`를 구분한다. 원 context/packet의 길이는 313개의 질의 결속 행이다.
- **영향:** 문구만 읽으면 313개 서로 다른 좌표 셀을 다뤘다고 이해할 수 있다. 실제 포함 증명, 각 행의 binding, 폭 통계 및 고정 reference 313/313은 그대로 유효하다.
- **최소 교정:** 이번 결과를 “313개 질의에 결속된 셀 레코드, 서로 다른 좌표 셀 89개”로 기술한다. 본 addendum에서 적용했으며 원 파일은 불변으로 유지한다.
- **분류/상태:** 비차단 보고 문구 명확화, `resolved_in_review_addendum`; 이론·수치·구현 실패로 분류하지 않는다.

다음은 원 오류로 세지 않고 본 검토에서 명시한 적용 조건이다: 단조성의 “증가/감소”에는 순수 성분에서 등호가 허용된다는 점, 열 전달식은 \(b+x_e\ne0\)와 고정 \(b,C_T\)를 쓴다는 점, 구간 계산은 Decimal의 정상 유한 범위와 primitive 계약을 승계한다는 점. 이들은 현재 고정 모형의 성공 결론을 바꾸지 않는다.

## 9. 인계 결과

원 이론 및 보충 이론에 대한 별도 비저자 R6 검토 증거가 생성됐다. 검토는 직접 유도, 양의 다항식과 제곱합 증명, 순수 성분·등호 분석, 원 source와 반환 필드 대조, 포함함수의 합성 및 정확한 교집합 논증으로 완료했다. 신규 scientific test가 필요할 만한 구체적 미해결 이론 위험은 발견하지 않아 허용된 예외 실행을 사용하지 않았다.

원 R6/C9의 과거 serial 미충족 기록, 원 실패 로그, 물리 미공급 상태와 예산 기록은 역사적 근거로 보존한다. 본 보고서는 현재의 R6 독립 검토 근거를 추가하며 전역 단계 수·canonical 수·물리 수용 상태를 변경하지 않는다. 새 strong no-go 또는 문헌 최초성 주장은 채택하지 않는다.

동반 영수증: `FRESH_R6_RECEIPT.json`. 원 source는 수정하지 않았고 출력은 `review_work/fresh_r6/`의 새 파일로만 기록했다.
