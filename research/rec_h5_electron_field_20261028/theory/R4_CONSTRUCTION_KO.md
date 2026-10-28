# R4 — 표현 탐색과 작은 구성

중앙 DAG28/88(+0), 단위 내용4/20. 새 native field 호출0.

## 세 후보의 실제 차이

1. 저장된 FH 값을 읽기만 하는 provider는132점 reference를 제공하지만 다른 incoming을 입력할 수 없다. 이번 목표인 실행 가능한 field API를 충족하지 않는다.
2. incoming=0으로 고정한 국소 물질 함수는 구현이 작지만 원래 FULL 함수의 radiation feedback을 버린다. 원래 입력과 다른 식이므로 채택하지 않는다.
3. P와 incoming311+2를 명시적으로 받아 원래 block assembly와 solve를 실행하는 point API는 원 source의 정보 의존성을 보존한다. 저장된 incoming을 넣어 native point와 비교할 수 있고, radiation을 독립 입력으로 다룬다는 경계도 분명하다. 이 후보를 채택한다.

원본 history interpolation은 incoming을 만드는 upstream 연산이고 history write는 결과를 저장하는 downstream 연산이다. 이번 분리는 두 연산 사이의 실제 block solve와 FH scalar에 해당한다. 전체 coupled history ODE를 새로 완성했다고 부르지 않는다.

## 작은 구성으로 확인한 판별점

다음2변수의 순수 대수 예를 직접 푼다. 이는 source에서 추출한 우주론 상태가 아닌 구조 설명용 toy이다.

M=[[3,-1],[-2,4]], S=[1,2u], H=1, beta=1, c=1.
첫 식3r-v=1, 둘째 식-2r+4v=2u에서
v=(1/2)r+(1/2)u,
r=(2+u)/5,
v=(1+3u)/5.
따라서 F=-c+beta*r=(-3+u)/5.

u=-1,0,1일 때 F=-4/5,-3/5,-2/5이다. det(M)=10이므로 각 해는 유일하다. incoming을0으로 고정하거나 음수를 clipping하면 서로 다른 valid algebraic 입력의 결과를 합쳐 버린다. 이 예는 incoming 의존성 보존의 필요성을 보이며 physical positivity나 실제HyRec gain의 크기를 증명하지 않는다.

일반적인 원 source에도 같은 분리가 가능한지는 원본 coefficient와 source의 u 의존성을 전부 확인하여 R5에서 판정한다. 실수 affine성은 독립적인 식 검산에 쓰고, binary64 bitwise affine성을 요구하는 새로운 허용오차는 만들지 않는다.

## 다음 판별 검증

R5에서는 M(P)와 S0(P)+G(P)u를 구체적으로 작성하고 Schur elimination을 역대입한다. R7에서는 해당 Schur 및 scalar transformation의 symbolic identity를 실제 CAS로 확인한다. C7은 저장된132 actual writer points를 새 adapter에서 한 번씩 실행하고 source parity를 검증한다. C8의 작은 incoming control은 radiation을 누락한 구현이 실제로 구별되는지 확인한다.

선택하지 않은 두 표현은 각각 reference-only와 blackbody restriction으로 보존한다. 이 구분은 새로운 no-go 주장이 아니라 이번 API의 입력 계약에 관한 구성적 결정이다.
