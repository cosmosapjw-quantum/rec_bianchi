# REC–BASS 단일 광자 상태 대응: 읽기·로그 좌표·분배의 구분

상태: `SOURCE_INSPECTED_DERIVATIONS_PENDING_LOCAL_CHECK`.

이 문서는 PR70의 계산을 반복하지 않는다. 다음 작업의 식별자 `REC_SPEC03A_MODEB_READ_SCATTER_COMPATIBILITY`는 이 문서에서 새로 부여하는 제한된 연구 작업명이다. 기존 생산 API나 승인된 공급자 이름이 아니다.

## 기준과 범위

REC 기준은 PR70의 완료 게시 commit `84205ab6a9b4e6d51097a82ec15da4deedfefc41`, tree `6f89ef4b871015912596200ba9aec3f2b2999c63`이다. 기존 승인 `REC_2S_FULL_BOSE_SINGLE_FIELD_TWO_LEG_RESEARCH`를 유지한다. PR63의 수치 어댑터, PR65–68의 입력/근사/식별성 연구, PR70의 기본/고해상도 비교는 이미 완료된 증거다. 다시 실행하지 않는다.

BASS의 이번 읽기 기준은 표현 어댑터 계열 PR127의 commit `9d1c702ddf58549a06b29965a3d1b790a0c23159`, tree `12ab5b477ff75b4fdfdb4bbc60e3864675fe0e3c`이다. 이것은 제한된 소스 조사 기준이지 생산 결합 승인 기준이 아니다. 해당 PR은 projection authority의 테스트 전용 RED 계약이며 실제 상태 연결을 완료했다고 주장하지 않는다. BASS main은 조회 당시 오래된 복구 checkpoint이므로 이를 최신 photon 구현으로 대신하지 않았다. 최신 배경 진단 PR128–131은 이 표현 branch의 자동 대체물이 아니다.

모든 BASS 파일은 읽기 전용이다. 전체 저장소의 모든 분광 상태를 조사했다고 주장하지 않는다. 특히 특정 J 계층에서 에너지 축을 찾지 못한 것을 저장소 전체의 F_Aell(q) 부재로 일반화하지 않는다. 주파수별 PSTF 경로는 보존해야 할 별도 요구이고, 이번 첫 구체적 읽기 경로만 ModeB로 정한다. 새 photon 진화 백엔드는 만들지 않는다.

## 실제로 읽은 소스와 대응

아래 BASS 경로는 모두 위의 고정 commit에 대한 것이다. blob 값은 GitHub의 Git tree/file 응답에서 읽었다. 이번 환경에서 전체 checkout이나 blob 바이트 재해시를 실행한 것은 아니다. 단일 소스의 현재 동작과 문서의 과거 성능 주장을 구별했다.

| 경로 | Git blob | 확인한 구체적 역할 |
|---|---|---|
| bianchi/q/modeb.py | 4df8421ab81459a448fff174286a03d1d38423c3 | ModeBState.lnf; 방향 우선 a*n_p+j; 균일 lnq; pack의 광자 배열 offset25; spectrum은 고정 q의 공변각 평균 |
| bianchi/q/comoving.py | 987c1b7b20a224d6b914035235d57693d1809839 | p=Mq; 기하 mu=abs(M qhat); 물리 방향과 각도 Jacobian; ModeA는 에너지 적분된 ln Ghat |
| _rustcore/src/kinetic/qevolve.rs | 0ed0b6556c8ba43fae43981c20345e223a9ec8b6 | 읽은 범위1–245 및350–555: QState.lg 의미, pack, lnGhat 축약, H_anchor 시간 변환, 공통 정지계 p로 이동하는 collide_mode_b |
| _rustcore/src/kinetic/radial.rs | ec946fced75e80201d516d1368c77eee87afd5b2 | 균일 로그 운동량의 Lagrange 시프트, ln f 보간, 명시적 Wien/PowerLaw 외삽, 사다리꼴 moment |
| bianchi/q/contract.py | e6b1a3de2a0fbcfe92928eb102c5aef3de7870c4 | 읽은 범위1–175: dtau=H dt, 내부 단위·앵커·각도 규약, 이산화와 근사 절환의 구분 |
| bianchi/physical/units.py | 10ff57f5a0ee9d136beacdae11bd6faa292f2ff0 | SI 경계 변환용 상수·단위 문서. 이 상수 파일 자체가 ModeB의 절대 운동량 눈금을 결정하지는 않음 |
| bianchi/source_adapters.py | 8b00602fc76e1cd49ac5b43615c97a686b56f080 | 읽은 범위1–210: 명시적인 f 값/분광계수 tuple에 대한 상수 source, H 또는 c로 나누는 시간 변환; evolution 연결은 아니라고 명시 |
| bianchi/matter/grid_boltzmann.py | 707f2dd833e4f56a5770ff3cc5aa5c07d585645e | F[r,a]의 반경 우선 저장, 모멘트는 DQ*Q^2*WANG/V. multipole_amplitudes는 먼저 반경적분 |
| bianchi/matter/hierarchy_coeff.py | 9ed97cab33d1ab7a458c44a56e53ab114a9142f9 | dict[(ell,i)]의 에너지 적분 J 계층. 그 자체를 주파수별 F_Aell(q) 저장소라고 부를 수 없음 |
| bianchi/q/species.py | f57b234465c36d21eccde9b7b97c78cf760b961d | 다성분 lG 캐리어. 이름이 photon이라는 이유만으로 full ModeB lnf 상태와 같게 취급하지 않음 |

REC 기준에서 읽은 계산기는 `src/full_bianchi_hyrec/trajectory/com_source_deposition.py`, blob `a3662cf399f14b7148d880266825be12baf934a0`이다. 실제 B, mode_measure_m3, 에너지, 합1의 각도 평균 가중치를 외부에서 받고 apply()/고정-map jvp()를 수행한다. 별도의 물리 격자 생성 권위를 제공하지 않는다.

원본 근거 URL은 `https://github.com/cosmosapjw-quantum/bass/blob/9d1c702ddf58549a06b29965a3d1b790a0c23159/` 뒤에 각 경로를 붙인 것이다. REC 파일은 `https://github.com/cosmosapjw-quantum/rec_bianchi/blob/84205ab6a9b4e6d51097a82ec15da4deedfefc41/` 기준이다.

## 소스에서 확인한 네 경계

1. ModeB는 y=ln f를 저장한다. 반면 REC COM의 출력은 df/dt다. 배열 위치에 그대로 더할 수 없다.
2. ModeB는 공변 방향과 q 좌표를 저장한다. 동일 q 인덱스가 방향마다 동일한 물리 에너지를 뜻하지 않는다. 기존 Rust 충돌도 mu*D를 사용해 공통 정지계 운동량으로 옮긴 뒤 연산한다.
3. BASS의 mu=abs(M qhat)는 기하적 배율이다. REC의 mode_measure_m3는 m^-3 단위의 photon measure다. 같은 문자라는 이유로 대입하면 차원과 의미가 틀린다.
4. ln f 읽기 보간, 그 Jacobian, 광자수를 보존하는 deposition은 서로 다른 연산이다. 역방향 remap 또는 전치만으로 필요한 보존 법칙이 생기지 않는다.

이는 아직 존재하지 않는 REC→ModeB 결합에서 방지해야 할 오류이지, 이번에 기존 생산 코드를 고장으로 재현했다는 뜻은 아니다. 고차 보간·유한 격자·꼬리 모형의 근사오차는 물리 법칙 오류와 구별한다.

## 조건부 수학 1: 물리 에너지와 질의 좌표

아래 유도는 고정·비특이 M, 공통 원자/광자 기준계(상대속도0), scalar occupation의 동일 정의를 가정한다. q가 내부 수치 좌표일 때 물리 에너지 눈금 E_*>0 J를 책임자가 제공한다고 하자. 이번에 그 값이나 실제 공급자를 선택하지 않는다.

r_a=abs(M qhat_a), e_a=M qhat_a/r_a,
E_a(q)=E_* r_a q,
ln q_(s,a)=ln(E_s/E_*)-ln r_a.

같은 광자 분포에서 두 source 에너지 E_t,E_c의 값은 위의 서로 다른 질의 좌표에서 읽는다. 상대속도가 있으면 기존 source-frame Doppler/광행차와 시간매개변수 변환이 추가로 필요하다. 이번 aligned-frame 식에 에너지 Doppler 하나만 붙여 일반 공변 충돌 변환을 완성했다고 주장하지 않는다.

ModeBState 자체에는 E_* SI 필드가 보이지 않는다. physical/units.py에는 단위 경계가 존재하지만 이번 읽기에서는 그것과 ModeB 상태를 잇는 절대 운동량/occupation 정규화의 공급자를 확정하지 못했다. 이것은 전체 저장소에서의 부재 증명이 아니다. local 검토는 기존 공급자가 있는지 해당 연결 범위만 확인하며, 없으면 그 한 owner 의무를 미결정으로 남긴다. q.contract와 units.py의 내부 자연단위 표현을 조합해 임의의 SI 정규화를 추측하지 않는다.

## 조건부 수학 2: 로그 상태와 Q 시간의 source/JVP

물리 시간의 occupation source C=(df/dt)_REC이고 dtau=H_phys dt라 하자. aligned frame, f>0, H_phys>0인 현재 진단 영역에서

G=(dy/dtau)_REC = C/(H_phys*f).

dG = dC/(H_phys*f) - G*(dy+dH_phys/H_phys).

여기서 df=f*dy다. dC는 같은 상태 방향의 source 미분이며, dC 안의 df 항과 마지막 -G*dy를 중복/누락하지 않는다. C는 s^-1, H_phys는 s^-1, G는 무차원 tau당 값이다. 분광계수에는 ln f 변환을 무조건 적용하지 않는다. f=0은 이 로그 좌표의 영역 밖이며 임의의 바닥값으로 다른 물리 문제를 만들지 않는다.

QEvolve Config는 물리율 A를 H_anchor*exp(ln_h)로 나누는 경로와 이미 정규화된 nu_tau 경로를 구별한다. ln_h 값 하나를 s^-1라고 취급하지 않는다. H_anchor의 실제 출처는 향후 입력 권위에 포함되어야 한다.

정확한 제조 예: eta=1 s^-1, kappa=0, f=2, H_phys=4 s^-1, dy=1/4, dH_phys=1 s^-1, deta=dkappa=0이면 C=3 s^-1, dC=1/2 s^-1, G=3/8, dG=-1/8이다. 이것은 직접 유도이며 아직 새 실행 검산 전이다.

## 조건부 수학 3: 로그 보간의 미분은 보존적 분배가 아니다

한 질의점에서 현재 보간의 국소 표현을 y_s=sum_i L_si*y_i, f_s=exp(y_s)로 쓰자. 격자와 스텐실을 고정하면

df_s=f_s*sum_i L_si*dy_i,
A_si := d f_s/d f_i = f_s*L_si/f_i.

L의 행합이1이라도 A의 행합은 일반적으로1이 아니다. 정확한 반례는 L=(1/2,1/2), (f1,f2)=(1,4)다. f_s=2, A=(1,1/4), sum A=5/4.

한 단위 packet을 B_i=A_si로 되돌리면 광자수 장부가5/4가 된다. 따라서 읽기 Jacobian의 단순 전치를 deposition map으로 승인할 수 없다. 이 예는 기존 COM map이 잘못됐다는 주장이 아니라 미래 연결의 잘못된 자동구성을 배제하는 반례다.

비교를 위해 f 자체에 선형인 읽기 f_s=sum_i P_si*f_i와 명시적 W=diag(mu_i)>0를 가정하면 D=W^-1 P^T가 한 가능한 약형 분배다. 이 경우 수 보존에는 P*1=1, 에너지 보존에는 P*E_target=E_source가 필요하다. signed source를 비음수 분율로 분배하려면 P_si>=0도 별도로 필요하다. 고차 Lagrange의 행합1만으로 나머지 조건은 나오지 않는다. 이것을 실제 B의 선택으로 채택하지 않는다.

## 조건부 수학 4: Planck 자료의 ln f 보간은 정확한 상세균형을 자동 보존하지 않는다

제조 내부 q 노드(1,4), 질의 q_t=2는 로그좌표의 중간점이다. E=E_* q, k_B T=E_*/ln2, 전이에너지 E21=3E_*라 하자. 같은 단일 Planck 함수 f(q)=1/(2^q-1)를 사용하면

f(1)=1, f(4)=1/15, 정확한 f(2)=1/3.

2점 ln f 보간은 f_interp(2)=1/sqrt(15)를 준다. xg=1/2, xu=1/16, a=1 s^-1인 두 광자식에서 companion q_c=1은 정확히 읽히고,

Gamma_exact=0,
Gamma_interp=(1-3/sqrt(15))/8  H^-1 s^-1.

이는 알려진 유한 격자 읽기오차의 정확한 제조 반례다. 반응률 함수를 고치거나 강제로0을 넣어서는 안 된다. 원본 표 자체의 오차 또는 실제 우주론 rate 오차라고 주장하지 않는다. local은 기존 radial.rs의 order2 실제 연산과 이 반례를 대조하고, order8에서는 고정된 작은 격자열의 잔차를 관측한다. 결과를 보고 차수/범위/tolerance를 바꾸지 않는다.

## 조건부 수학 5: 기하 배율과 photon 측도의 분리

f가 편광 하나당 occupation이고 동일한 g_pol개 내부 상태를 대표하며, 물리 p=(E_*/c)M q가 실제로 승인된 convention일 경우만 다음을 쓸 수 있다. h=2*pi*hbar다.

d^3p=(E_*/c)^3*abs(det M)*q^3*dlnq*dOmega_q,

n_gamma=(g_pol*E_*^3/(h^3*c^3))*abs(det M)*integral f*q^3*dlnq*dOmega_q.

logq 사다리꼴의 t_j=(1/2,1,...,1,1/2)를 사용한 노드별 구적 인자는

W_(a,j)=(g_pol*E_*^3/(h^3*c^3))*abs(det M)*w_com,a*t_j*q_j^3*Delta lnq.

단위는 m^-3이지만 이것은 해당 구적 convention의 가중치다. 원본 HyRec의 photon cell이나 REC의 실제 mode_measure로 자동 승인하지 않는다. 기존 QState의 energy 축약은 w_phys*r_a^4 = w_com*abs(det M)*r_a와 q^4 moment를 사용하므로 같은 기하 Jacobian 구조와 대응한다. 절대 SI 계수와 편광 정규화는 별도 확인이 필요하다.

현재 REC COM은 에너지 E_i와 mu_i가 각도축에 공통이고 angular_weights의 합이1인 분리형 배열을 받는다. 반면 일반 M의 ModeB 물리 에너지 E_(a,j)=E_*r_a q_j는 방향에 의존한다. 따라서 ModeB 원 배열을 COM의 (M,A) 배열에 단순 transpose하는 것만으로 물리적으로 같은 상태가 되지 않는다. 기존 common-rest-energy remap을 어떻게 소비할지 또는 더 일반적인 목표 측도가 필요한지는 이후 소유자 결정이다. 이번에는 COM 구조를 바꾸지 않는다.

## 완료와 다음 한 작업

이번에 완료한 것은 위 소스 경로의 제한된 읽기·서로 다른 상태의 구분·조건부 수식과 인계 작성이다. 새 Python/Rust/CAS 실행이나 실제 물리 입력 인증은 없다. 대화의 container 및 Python은 각각 시작 전 ClientError, WolframContext는 평가 전 HTTP404였다. local에 필요한 수학 패키지가 있다는 사용자 설명을 유지하되 실행 경로/버전은 다음 로컬 결과에서 기록한다.

다음 한 작업은 동일한 문서의 LOCAL_CODEX_PROMPT_KO.md에 지정한 `REC_SPEC03A_MODEB_READ_SCATTER_COMPATIBILITY`다. 기존 ModeB/RadialGrid의 실제 저장·보간 경로를 고정 제조 입력으로 확인하고 위 반례·JVP를 독립 검산한다. 물리 B·mu·E_*를 생산 기본값으로 선택하지 않는다. 주파수별 PSTF 상태의 정확한 소유 경로는 필요한 제한된 연결 조사로 남긴다. BASS source 수정·새 provider·전체 backend 재빌드·전체 PR70 재실행은 금지한다.

삼분할: 대화 스레드는 수학·주장 범위를 맡는다. 작업 스레드는 exact source와 반환물을 검토하고 단일 원격 작성자로 게시한다. local Codex는 실제 계산과 원본 소스/로그/그림/bundle을 반환한다. 자동으로 다른 실행을 시작했다고 주장하지 않는다.

## 문헌·근거 상태

SciSpace 검색 후 원 논문의 공개 초록을 확인했다. Ali-Haimoud와 Hirata, arXiv:1011.3758v2는 원자 population과 radiation field의 결합을 명시한다. Le와 Cambier, arXiv:1711.05946v1은 비균일 에너지 격자의 비탄성 전자/원자 충돌 보존 알고리즘을 다룬다. 후자는 이번 광자 Bose interpolation 문제의 정답이나 BASS 구현 검증이 아니다. 두 초록 이상을 이번에 새로 읽었다고 주장하지 않는다. 구체적 source mapping은 위 Git 파일, 식과 반례는 이 문서의 직접 유도가 근거다. 검색의 비관련 결과는 채택하지 않았다.

문헌: https://arxiv.org/abs/1011.3758 ; https://arxiv.org/abs/1711.05946

최종 한계: `NO_PASS_REC_PHYSICAL_SPLIT`. source/provider 인증, 연속 수렴, 실제 물리 target, angular/polarization kernel, moving-map/event JVP, accepted-state transaction, BASS 생산 결합, merge/ready는 승인하지 않는다.
