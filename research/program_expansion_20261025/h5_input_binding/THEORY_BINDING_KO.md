# H5 조건부 유도와 실제 source 좌표의 결속

## 재사용한 결과

중앙 독립 심사는 `DERIVATION.md`의 고정 norm, almost-everywhere Gronwall
부등식, forward/backward orientation, native-channel endpoint 변환과
whole-cell interpolation 나머지를 `PASS_DERIVED_SCOPED`로 승인했다. 이 단위는
그 명제의 가정과 입출력 관계를 구현하며 실제 물리 가정을 새로 가정하지 않는다.

`eta=ln(a)`는 dimensionless clock이다. 고정 양의 state scale `S`에서
`||v||_S=||S^-1 v||_infinity`를 쓴다. 재구성 `x_h`는 연속이며 각 구간에서
절대연속이고, 원 source target `x`는 같은 source/domain의 equation을 따른다.
Source/model mismatch가 있으면 그 scaled bound `b`를 defect `d`에 더한다.

일정 상계 `L>=0`, `d>=0`, `b>=0`가 선언된 전체 구간에서 성립하면,
positive path-length `s=sigma(eta-eta0)>=0`에서

`E(s)=exp(Ls)e0+(d+b)(exp(Ls)-1)/L` (`L>0`),

`E(s)=e0+(d+b)s` (`L=0`)

가 성립한다. `L,d,b,e0`가 비음수이므로 `E(s)`는 단조 증가한다. 재구성 주위의
uniform open safe tube radius의 인증 하계 `rho_lower>0`에 대해 마지막 필요한
endpoint에서 `E_upper(s_max)<rho_lower`를 검사하면 이전 경로의 같은 scalar
bootstrap 부등식도 성립한다. 반경의 상계는 이 포함 관계를 보장하지 않는다.
공급자 proof는 동일 재구성·고정 norm·eta domain에서 최소 `rho_lower` 반경의
전체 tube를 덮어야 하며 경계 equality도 거절한다.
이 수치 검사는 tube 내 존재·연속영역 상계에 대한 공급자 증명을 소비한다.
파일 존재와 metadata만으로 그 증명 내용을 승인하지 않는다.

각 endpoint의 native history radius는 `e_side=K_side E_side+bG_side+rep_side`다.
`K`의 단위는 native channel/scaled state이며, `bG`, endpoint representation,
epsilon의 단위는 dimensionless occupation departure다. `M2`는 channel/eta²다.
Proper-time derivative를 사용할 경우 source-matched clock 변환이 먼저 필요하다.

## 실제 nominal input의 표현 반경

고정 PB01 source의 실제 저장된 knots `L,R`, query `q`, 샘플 `Y_L,Y_R`와
nominal incoming `u`를 원 binary64의 정확한 유리수로 읽는다. 다음을 정의한다.

`a=(q-L)/(R-L)`, `I_h=(1-a)Y_L+aY_R`, `b_repr=|u-I_h|`.

`a`는 저장된 eta knots의 geometric weight다. Native 코드의
`(q-eta0)/dlna-floor(...)`로 얻은 binary64 weight와 연산 순서가 다를 수 있다.
실제 `u-I_h`를 그대로 결속하면 weight 차이, 합산 반올림과 nominal anchoring을
한 번만 계수한다. 새 arbitrary tolerance는 필요하지 않다.

Exact target history의 endpoint error가 `e_L,e_R`, 전체 cell의 곡률 상계가
`M2`일 때 삼각부등식과 기존 interpolation remainder는

`|u-y(q)| <= b_repr + (1-a)e_L + a e_R + M2(q-L)(R-q)/2`

를 준다. 이는 실제 nominal value가 단순 symbolic interpolant와 일치하지 않는
경우를 원 유도에 명시적으로 연결한 것이다. `b_repr`를 endpoint radius에 다시
더하지 않는다. 물리 query coordinate 자체의 uncertainty/retiming은 별도다.

원 자료를 읽어 결속한 결과 `b_repr`의 최대 exact 값은
`2125323597749/7573333069425850157122243222373270552576`이다.
그 근거는 `SOURCE_CONTEXT.json`의 실제 313개 행과
`SOURCE_BINDING_SUMMARY.json`이다. Physical `e0,d,L,rho,K,bG,M2`는 아직 없으므로
이 표현 반경만으로 epsilon을 채우지 않는다.

## 유한 exponential 상계와 출력

`x=Ls>=0`를 `z=x/2^k<=1`로 줄인다. `t_n=z^n/n!`, `N=48`로 두면

`exp(z) <= sum_(n=0)^N t_n + t_(N+1)/(1-z/(N+2))`.

Tail의 연속 항비가 `z/(N+2)`보다 작거나 같으므로 이 상계는 exact rational로
계산할 수 있다. 양변을 `2^k`번 거듭제곱하는 것은 비음수에서 단조이므로
`exp(x)` 상계가 된다. 현재 구현의 지원 범위는 `x<=64`이며 초과는 typed
unsupported 결과다. 이 범위는 물리 제한이 아닌 유한 구현 범위다.

독립 검토에서 `x=63.5`의 exact fraction을 그대로 문자열로 만들 때 Python의
integer-string 길이 한계에 걸리는 실행 결함이 확인됐다. 내부 유리수는 유지하고
출력에만 exact integer division을 적용한다. 64유효자리 decimal grid에서 상계는
ceil, 하계는 floor를 사용하므로 반올림 방향의 증명이 명시적이다. 원 코드와
독립 failure는 보존하며 원 source, physical tolerance, conditional theorem은
변경하지 않았다.

## 남은 물리 의무

현재 검토한 원 source records와 중앙 H5 계약에서 physical defect, stability,
tube, curvature 및 초기/reference error는 모두 미공급이다. 원 source의
retarded radiation history를 포함한 정확한 연속 state/closure와 `G`를 공급해야
한다. 한 순간의 thermodynamic Jacobian이나 matrix inverse residual은 이 연속
문제의 stability/defect 증거를 대신하지 않는다.

완료된 원 trajectory/KS/PB01을 재실행하지 않고, actual 313-query geometry,
endpoint samples, nominal values와 기존 K_s intervals까지 연결했다. 공급자
packet이 준비되면 새 input만 동결하여 이 소비기에 넣고 외부 proof 내용과
science tolerance를 독립적으로 평가한다. 이 결과는 새 no-go 정리가 아니며
기존 조건부 구성의 실제 적용 준비다.
