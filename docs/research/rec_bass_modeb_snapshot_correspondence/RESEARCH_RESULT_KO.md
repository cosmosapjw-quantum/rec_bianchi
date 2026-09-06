# REC–BASS Mode B 고정 상태 대응: 현재 대화의 수학 연구 결과

작업: `REC_BASS_MODEB_FIXED_SNAPSHOT_CORRESPONDENCE`.
판정: `DERIVED_AND_SCALAR_CHECKED_NATIVE_EXECUTION_BLOCKED`.
과학적 상한: `NO_PASS_REC_PHYSICAL_SPLIT`.

## 1. 이번에 실제 수행한 것

사용자는 다른 작업 스레드/local Codex로 넘기지 않고 현재 대화에서 연구를 수행하라고 지시했다. 메모리의 전역 규약과 REC의 `docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md`를 읽고, 소스 읽기 → 수학적 유도 → 정확한 반례 → 가능한 계산기 수치대조 → 이 checkpoint 순서로 진행했다. 완료된 PR70의 기본/고해상도 비교, pytest7, 원본 ZIP과 bundle의 전체 검사를 재실행하지 않았다. 새 인계문이나 생산 구현은 만들지 않았다.

현재 대화에서 container와 Python은 각각 한 번의 admission 호출이 프로세스 시작 전 ClientError로 실패했다. WolframContext와 실제 WolframLanguageEvaluator도 각각 커널 평가 전 MCP SSE HTTP404로 실패했다. 따라서 새 Python/Fraction/SymPy 실행, Rust 컴파일/원본 함수 실행, native 테스트, 그림 생성은 0회다. 다른 스레드나 local Codex에 실행을 위임하지 않았다.

아래 대수는 직접 유도다. 선택된 폐형식의 소수값은 실제 web calculator 결과로 확인했다. 계산기는 Python/Rust/CAS가 아니며 precision 설정·원본 라이브러리 호출·독립 프로그램 실행을 인증하지 않는다. 식별자나 증거가 없는 PASS를 만들지 않는다.

## 2. 고정 소스와 읽은 범위

REC 부모: `84205ab6a9b4e6d51097a82ec15da4deedfefc41`.
부모 tree: `6f89ef4b871015912596200ba9aec3f2b2999c63`.
부모는 원격 Git commit 객체에서 tree와 함께 읽었다. PR70의 open/draft/unmerged 상태도 읽었다.

BASS 조사 기준: `9d1c702ddf58549a06b29965a3d1b790a0c23159`.
그 기준의 tree locator: `12ab5b477ff75b4fdfdb4bbc60e3864675fe0e3c`.
이것은 기존 수신 계열의 고정 소스 기준이며, 모든 branch의 최신 head 또는 생산 연결 승인이라는 뜻이 아니다. 이번에는 BASS 전체 재감사를 하지 않았다.

| 저장소/파일 | GitHub가 반환한 blob | 이번 읽기 범위 |
|---|---|---|
| BASS bianchi/q/modeb.py | 4df8421ab81459a448fff174286a03d1d38423c3 | 30–125: lnf, pack/set_from, logq, lnGhat, 초기 함수 |
| BASS _rustcore/src/kinetic/radial.rs | ec946fced75e80201d516d1368c77eee87afd5b2 | 1–145: 격자·시프트 스텐실·로그 보간·꼬리 |
| BASS _rustcore/src/kinetic/comoving.rs | a29b12b5e7b0d529bddaf9eac53cfdb984ddaa84 | 134–181: 물리 방향 배율, 각도 Jacobian, 모멘트 |
| REC src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py | 26ddc41e24fadf0bdd19f1924e1a429d602d9c19 | 1–210 및335–파일 끝: source 단위, paired class, degeneracy, net/JVP |
| REC src/full_bianchi_hyrec/trajectory/com_source_deposition.py | a3662cf399f14b7148d880266825be12baf934a0 | 1–파일 끝: B/measure 검증, apply/JVP, 장부 |
| REC docs/quality/PROGRESS_FIRST_IDENTITY_POLICY.md | 50c722e2b5fe437401444054427579eadb92a9e2 | 전체 |
| REC AGENTS.md | 374340473e6cd5061f74df776872b8e300b4d21a | 전체 |

이 blob 값은 connector의 응답이다. 전체 checkout이나 로컬 byte 재해시를 수행했다고 주장하지 않는다. 모든 기존 파일은 읽기 전용으로 다뤘다. 새 두 결과 파일만 부모 위 별도 child에 보존한다.

## 3. 정의와 가정

서명은 (-,+,+,+). h=2*pi*hbar를 유지한다. c, hbar, k_B를 생략하지 않는다.

진단은 수소 정지계와 평가 tetrad가 같고, 고정된 비특이 M, 고정된 source 에너지와 격자, f>0, H_phys>0에서 수행하는 조건부 수학이다. 이동 프레임·event·수송·시간 적분은 포함하지 않는다. 상대속도가 있는 경우 에너지 Doppler만 넣어 완전한 충돌항 변환을 얻었다고 주장하지 않는다.

j는 반경 노드, a는 방향, s는 광자 다리 또는 source channel이다. y_aj=ln f_aj. BASS의 기하학적 mu는 혼동을 피하여 s_a=|M qhat_a|로 쓴다. REC의 mu_i는 m^-3 단위의 photon measure다.

내부 q가 무차원 좌표일 때 물리적 운동량 눈금을 p_star>0로 둔다. 이것과 scalar occupation의 편광/축퇴 정규화는 조건부 입력이며 실제 owner 값을 이번에 지정하지 않는다. 이 명시적 조건 아래 p_phys=p_star M q, E_aj=c p_star s_a q_j다.

원본 paired class는 occupation이 아니라 수소 원자당 packet rate를 반환하며, 실제 B와 mu를 적용해야 df/dt가 된다. 아래 단일 eta/kappa fixture는 이미 occupation source 단위의 제조식이지 원본 A2s 값을 그 단위로 재명명한 것이 아니다.

## 4. A — 저장 배열과 source 좌표/JVP

소스의 ModeBState는 y=ln f를 방향 우선 a*n_p+j 순서로 저장한다. pack에서 광자 배열은 offset25부터이며 set_from도 같은 분할을 쓴다. REC COM의 출력은 (energy,angle) 순서의 C=df/dt다. 전치만으로 동일한 상태 변수가 되지 않는다. 실제 pack/unpack 호출은 이번에 실행하지 않았다.

같은 기준계에서 dtau=H_phys dt이면

S_y=(dy/dtau)_REC=C/(H_phys f).

f>0, H_phys>0에서 전미분하면

dS_y=dC/(H_phys f)-S_y*(dy+dH_phys/H_phys),
dy=df/f.

검산 경로를 하나 더 쓰면, C=eta(1+f)-kappa f인 제조 source에서

S_y=[eta/f+eta-kappa]/H_phys,
dS_y=[(1+1/f)deta-dkappa-eta*df/f^2]/H_phys-S_y*dH_phys/H_phys.

두 식은 dC=(1+f)deta-f*dkappa+(eta-kappa)df를 대입하면 정확히 같다. 그 차이를 CAS로 계산한 것이 아니라 항을 직접 전개해 동일함을 보였다.

고정 fixture:
f=2; eta=1/4 s^-1; kappa=3/4 s^-1; H_phys=4 s^-1;
df=1/8; deta=1/2 s^-1; dkappa=-1/4 s^-1; dlnH_phys=1/8.

따라서
C=-3/4 s^-1,
dC=3/2+1/2-1/16=31/16 s^-1,
S_y=-3/32,
dS_y=31/128+9/512=133/512=0.259765625.

변환 도함수에서 -S_y*dy를 빼먹으면 130/512, -S_y*dlnH를 빼먹으면127/512, 둘 다 빼먹으면124/512다. 이는 구현 mutant를 실행한 결과가 아니라 누락된 식의 정확한 반례다. 과거 13/16 fixture는 변경하지 않는다.

### 독립적인 경로 매개변수와 중앙차분 폐형식

f(eps)=2+eps/8, eta(eps)=1/4+eps/2,
kappa(eps)=3/4-eps/4, H(eps)=4+eps/2로 두면 위 방향과 eps=0에서 일치한다. |eps|<=1/1000에서 필요한 양의 영역이 유지된다.

G(eps)=(-3/4+31eps/16+3eps^2/32)/(8+3eps/2+eps^2/16).

정확한 대수 정리로

[G(eps)-G(-eps)]/(2eps)
=(4256-5eps^2)/(16384-320eps^2+eps^4).

정확한 미분값과의 차이는

eps^2*(40000-133eps^2)/[512*(16384-320eps^2+eps^4)]
=(625/131072)eps^2+O(eps^4).

실제 계산기가 반환한 값:

| eps | 중앙차분 폐형식의 값 | 133/512와의 소수 차이 |
|---|---:|---:|
| 1/1000 | 0.25976562976837164 | 4.768371641983293e-9 |
| 1/10000 | 0.2597656250476837 | 4.7683690329591855e-11 |

이것은 중앙차분 폐형식을 계산기로 수치 평가한 것이다. Python에서 함수 두 번을 호출한 실험, AD 검증, Fraction 실행 또는 Rust source JVP의 검증이라고 부르지 않는다. 긴 지수/직접차분 표현의 일부 계산기 요청에는 결과가 반환되지 않아 그 요청을 증거로 쓰지 않았다.

### 실제 fixed-map COM 식과의 연결

mu와 B를 고정하면 C_i=n_H/mu_i * sum_s B_is R_s이므로

dS_y,i=n_H/(H_phys mu_i f_i)*sum_s B_is dR_s
+S_y,i*(dn_H/n_H-dH_phys/H_phys-dy_i).

원본 COM jvp의 density 항을 보존하면서 로그/시간 chain을 추가하는 식이다. 실제 B,mu를 넣어 이 결합을 실행한 결과는 아니다. 움직이는 B나 mu의 미분을 이 fixed-map 식으로 대체하지 않는다. f=0은 로그 좌표 밖이며 임의 floor를 선택하지 않는다.

## 5. B — 공변 격자와 측도

e_a=M qhat_a/s_a,
w_phys,a=w_com,a |det M|/s_a^3.

같은 물리 에너지 E_source를 읽는 위치는

q_source,a=E_source/(c p_star s_a).

M=diag(2,1,1/2), qhat_x=(1,0,0), qhat_z=(0,0,1), E_source=2c p_star이면 q_x=1, q_z=4다. 같은 q=2는 각각4c p_star와c p_star여서 동일 원자 에너지에 대한 읽기가 아니다. 이 두 방향은 좌표 반례이지 구면 구적의 인증 격자가 아니다.

편광 하나당 f가 명시적인 g_gamma개 동일 내부 상태를 대표한다고 가정하면

dn_gamma=(g_gamma/h^3)f d^3p,
d^3p=p_star^3 |det M| q^3 dlnq dOmega_q.

따라서 로그 q 사다리꼴에 해당하는 조건부 nodal number weight는

W_aj=(g_gamma p_star^3/h^3)|det M| w_com,a t_j q_j^3 Delta lnq.

단위는 m^-3. p_star^3/h^3는 m^-3이며 나머지는 무차원이다. 에너지 모멘트는 sum W_aj E_aj f_aj이고 단위J m^-3다. 수 측도에서 s_a^3는 각도 Jacobian의 역인자와 상쇄되고, 에너지에는 s_a가 하나 남는다. M=I에서는 통상적인 log-momentum 구적 형태로 돌아간다.

이는 정의된 구적의 대응이지 연속적분의 유한 노드 정확성이나 실제 photon cell 인증이 아니다. 변환된 w_phys의 유한합이 정확히4pi라고 강제하지 않는다. 원본의 w_com 합4pi와 REC의 합1 각도 평균을 혼동하지 않는다. W는 각도 인자까지 포함하므로 REC mu_i에 바로 넣을 배열이 아니다.

REC COM은 E_i와 mu_i가 각도축에 공통인 분리형 입력을 사용한다. 일반 비등방 M에서 E_aj는 방향에 의존하므로 ModeB 배열의 단순 transpose는 그 정의역과 일치하지 않는다. 공통 물리 에너지 재격자화 또는 일반화된 목표를 선택하는 일은 이번에 하지 않는다.

## 6. C — 원본 radial.rs 알고리즘의 정확한 수작업 전개

이 절은 원본 source의 정적 대수 전개다. 컴파일 또는 함수를 실제 호출했다고 주장하지 않는다.

q_nodes=(1,4), lnq_nodes=(0,ln4), n=2,
dln=ln2, order=2로 고정한다.

원본 shift_stencil의 연산을 순서대로 쓰면

k=max(2,2)=2,
s=dln/dlnp=1/2,
base=floor(-s)=-1,
frac=-s-base=1/2,
j0=-(k/2-1)=0,
offsets=(-1,0), xs=(0,1), weights=(1/2,1/2).

apply_shift_log의 출력 i=1은 입력 인덱스0,1만 읽으므로

y_out[1]=(y_in[0]+y_in[1])/2.

출력 i=0에서는 외삽이 사용되지만 선택한 내부 질의 i=1에는 영향을 주지 않는다. 따라서 이 한 결과는 Wien/PowerLaw 꼬리 선택과 무관하다. 기본 k_rad=8의 정확도에 대해 아무 수치 결론도 내리지 않는다.

### 읽기 Jacobian 전치를 photon 분배로 쓰는 반례

고정 L에서 f_s=exp(sum_i L_si ln f_i)이므로

A_si=d f_s/d f_i=f_s L_si/f_i.

L=(1/2,1/2), f_nodes=(1,4)에서는 f_s=2,
A=(1,1/4), sum A=5/4.

A^T를 단위 packet의 number fractions로 삼으면 수가1이 아니라5/4가 된다. 반대로 L^T는 수는1로 보존하지만 E_nodes=(E0,4E0), E_source=2E0에서 에너지 기대값이(5/2)E0여서 틀린다. 이것은 기존 COM의 승인된 map이 틀렸다는 뜻이 아니다. 아직 없는 연결에서 두 자동 구성이 모두 정당화되지 않음을 보인 것이다.

## 7. D — 로그 보간된 Planck 상태의 정확한 두 광자 반례

고정 제조 조건:
E_nodes=(E0,4E0), Et=2E0, Ec=E0, E21=3E0,
k_B T=E0/ln2, a=1 s^-1, xg=1/2, xu=1/16,
upper_to_ground_degeneracy_ratio=1.

Planck f(E)=1/[exp(E/(k_B T))-1]이면
f(E0)=1, f(4E0)=1/15, 정확한 f(2E0)=1/3.

위 원본 알고리즘의 수작업 전개에서 tracked 값은
fhat_t=1/sqrt15, companion은 fhat_c=1이다.

실제 source의 paired 식은
Gamma=a[xu(1+fc)(1+ft)-g_ratio*xg fc ft].

정확한 ft=1/3에서는 정방향과 역방향이 둘 다1/6 H^-1 s^-1이고 Gamma=0이다. 보간값을 넣으면

F=(1+1/sqrt15)/8,
R=1/(2sqrt15),
Gammahat=(1-3/sqrt15)/8 H^-1 s^-1 >0.

계산기가 실제 반환한 소수값:
fhat_t=0.2581988897471611,
F=0.15727486121839512,
R=0.12909944487358055,
Gammahat=0.028175416344814574.

직접 차이 F-R의 계산도 같은 소수값을 반환했다. 이 수치는 원본 Rust/Python API 호출 결과나 실제 HyRec 오차 추정이 아니다. 명시한 두 노드·order2 제조 반례의 폐형식 값이다. source/원본 표/평형률을 강제로 수정하지 않았다.

## 8. 새 결론: 보존적인 deposition만으로 읽기 단계의 열평형 결함을 복구할 수 없다

하나의 고립된 두 광자 반응을 고려한다. 같은 순사건률 Gamma가 두 photon 다리에 하나씩 기여한다. W_i>0, n_H>0, 각 다리별로 sum_i B_it=sum_i B_ic=1인 임의의 map을 가정하면

C_i=n_H/W_i*(B_it+B_ic)Gamma,
sum_i W_i C_i=2n_H Gamma.

따라서 Gamma!=0이면 C가 모든 목표에서0일 수 없다. 이 명제는 B의 세부 모양과 무관하며, 비음수 조건보다 약한 column-sum 조건만으로도 성립한다. 여러 반응의 우연한 총합 상쇄나 각도 커널의 일반 경우로 확대하지 않는다.

제조 반례에서 총 photon rate/n_H=2Gammahat=0.05635083268962915 H^-1 s^-1이다.

에너지 보존까지 만족하는 map이면
sum_i E_i W_i C_i=n_H(E_t+E_c)Gammahat=n_H E21 Gammahat.
원자 에너지 항을 -n_H E21 Gammahat로 두면 총에너지 장부는 정확히0이지만 열평형에서 가짜 변화는 계속된다.

결론: number/energy 보존과 detailed balance는 독립된 요구다. 보존 검사를 통과한 map만 선택해도 이 읽기오차는 없어지지 않는다. 기존 atom/radiation 결합을 발전시키려면 읽기 단계의 평형 결함을 별도로 다뤄야 한다. 이는 이번 직접 유도에서 얻은 결정이며 새 production gate나 B 선택이 아니다.

### 꼬리 읽기의 추가 경계

현재 COM처럼 B_is>=0, sum_i B_is=1, sum_i E_i B_is=E_s를 요구하면 E_s는 목표 에너지들의 convex hull에 있어야 한다. 즉 min E_i <= E_s <= max E_i가 필요하다. 원본 radial.rs가 격자 밖의 f를 외삽할 수 있다는 사실은 그 에너지의 packet을 같은 유한 목표에 보존적으로 분배할 수 있다는 뜻이 아니다. 실제 표에서 이 조건을 위반한 채널을 이번에 측정한 것은 아니다.

## 9. 정확한 평형 조건과 후속 설계의 조건부 가능성

양의 occupation에 psi(f)=ln[(1+f)/f]를 정의한다. LTE population xu=g_ratio*xg*exp[-E21/(k_B T)]일 때 원본 paired 식은 정확히

Gamma=a*g_ratio*xg*fc*ft*expm1(psi(fc)+psi(ft)-E21/(k_B T)).

따라서 양의 prefactor 영역에서 Gamma=0의 필요충분조건은
psi(fc)+psi(ft)=E21/(k_B T)다.

보간오차 epsilon_s=psi(fhat_s)-E_s/(k_B T)를 쓰면
Gammahat=a*g_ratio*xg*fhat_c*fhat_t*expm1(epsilon_c+epsilon_t).

두 다리 각각의 occupation 오차가 독립적으로0이어야만 pair 영점이 생긴다는 주장은 하지 않는다. 합오차가 상쇄될 수도 있다. 다만 모든 에너지/온도에서 안정적으로 평형을 보존하려면 개별 psi 재현이 한 충분조건이다.

이 조건은 실제 보간법을 선택하지 않고도 명시할 수 있다. 비음수 P에 P*1=1, P*E_nodes=E_source가 성립한다면

psi_s=sum_i P_si psi(f_i),
f_s=1/expm1(psi_s)

는 Planck nodal 상태에서 정확한 Planck source 값을 재현한다. Planck에서는 psi_i=E_i/(k_B T)이기 때문이다. P>=0이면 양의 psi 영역도 보존된다. 이것은 현재 log-f 보간과 다른 연산이며, 기존 source를 바꾸거나 생산 기본값으로 채택한 것이 아니다. 실제 P/measure/방향/경계/JVP 정확도는 인증하지 않는다.

같은 조건부 P를 photon-number 분율로 사용할 때의 B=P^T 역시 한 가능한 약형 구성일 뿐이다. log-f 읽기 Jacobian의 전치와는 다르다. 이 연구는 현재 source의 결함을 숨기는 보정이나 implicit Planck closure를 승인하지 않는다. 비평형 field는 계속 하나의 실제 분포여야 한다.

## 10. 근거와 감사 범위

핵심 소스 URL:
- https://github.com/cosmosapjw-quantum/bass/blob/9d1c702ddf58549a06b29965a3d1b790a0c23159/bianchi/q/modeb.py
- https://github.com/cosmosapjw-quantum/bass/blob/9d1c702ddf58549a06b29965a3d1b790a0c23159/_rustcore/src/kinetic/radial.rs
- https://github.com/cosmosapjw-quantum/bass/blob/9d1c702ddf58549a06b29965a3d1b790a0c23159/_rustcore/src/kinetic/comoving.rs
- https://github.com/cosmosapjw-quantum/rec_bianchi/blob/84205ab6a9b4e6d51097a82ec15da4deedfefc41/src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py
- https://github.com/cosmosapjw-quantum/rec_bianchi/blob/84205ab6a9b4e6d51097a82ec15da4deedfefc41/src/full_bianchi_hyrec/trajectory/com_source_deposition.py

원 문헌 검색에서 arXiv:1011.3758(HyRec)와 arXiv:1009.2748(Fast conservative and entropic numerical methods for the Boson Boltzmann equation)의 공개 초록을 확인했다. 전자는 원자 population과 radiation field의 동시 진화, 후자는 보존·entropy·Bose equilibrium을 별개 구조로 다룬다는 방법론적 문맥이다. 이번에 두 논문의 전문을 읽었다거나 그 방법이 이 코드의 정확한 해법이라고 주장하지 않는다. 위 수식·반례·no-go 명제는 직접 유도이며 문헌의 정리를 전용한 것이 아니다.

검토는 같은 작성자가 수학·단위·소스 의미를 구분해 수행했다. 독립 reviewer나 제3자 native 검증은 호출하지 않았다. 수치 문턱이나 기존 기대값을 바꾸지 않았고, f=0/relative-frame/moving-map/convex-hull 밖 조건을 명시적으로 분리했다. 새 그림은 없다.

## 11. 종료와 다음 한 작업

수학적으로 A–D의 정의·유도·정확한 반례를 정리했고 선택된 폐형식은 계산기로 수치대조했다. 원본 함수의 runtime 구현 검증은 실행환경 때문에 미완료다. 이 문서는 전체 고정상태 진단 PASS가 아니다.

남은 다음 한 작업은 현재 대화의 실행 경로가 실제로 작동할 때, 이미 고정한 원본 radial.rs의 order2 질의와 ModeB/paired API를 한 번 호출하여 이 폐형식과 대조하는 것이다. 새 계획 승인, PR70 재실행, 별도 작업 스레드/local Codex 인계는 만들지 않는다. 이번에 도출한 psi 조건을 생산 구현으로 자동 전환하지 않는다.

physical_source_authenticated=false; provider_admitted=false.
실제 B/mu/p_star/g_gamma·각도/편광 kernel·moving-map/event·accepted-state update·BASS 통합·merge/ready는 미수행이다.
