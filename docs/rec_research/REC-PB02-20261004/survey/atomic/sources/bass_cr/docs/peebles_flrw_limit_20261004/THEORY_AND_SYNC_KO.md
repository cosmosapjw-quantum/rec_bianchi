# FLRW Peebles 복원 이론 01 및 수신측 PB01 동기화

사용자 명시 요청: FLRW 극한에서 Peebles effective three-level hydrogen recombination formula와 C-factor 복원을 우선 검증한다. 이는 원자 native lane 재개, fastest baseline 변경 또는 rei_bianchi production 물리 수정 요청으로 확대하지 않는다.

## 판정

- 조건부 유효 3준위 축약: 직접 유도 및 제한 대수 검산 완료.
- 현재 F00의 SYNTHETIC_CASE_A_ESCAPE를 기하만 FLRW로 보내는 경로: STRUCTURALLY_NOT_EQUIVALENT. 모형 차이이며 해당 합성모형 구현 버그 판정은 아니다.
- 실제 receiver의 Peebles regression 및 재결합 x_e(z): NOT_EXECUTED.
- 정밀 원자 및 production의 기존 제한: 그대로 보존.

## 고정 모델에서 복원

순수 수소, proper n_H, x=x_e=x_p, x_1+x_2+x=1인 유효모델을 사용한다. 최초 비교는 T_m=T_gamma로 고정한다. higher-level cascade는 alpha_B로 축약하고 명시적 고준위 점유는 생략한다. Case-B, 열적 역반응, 두꺼운 Sobolev Lyalpha escape, 2s two-photon 및 statistical x_2p=3x_2s=3x_2/4가 필요하다. 외부 UV/CR off는 thermal CMB bath off가 아니다.

A=n_H alpha_B x^2, b=exp[-E_alpha/(k_B T_gamma)], beta_P=4 beta_2,
Gamma_2=(Lambda+3R_alpha)/4.

    dot(x)   = -A + beta_2 x_2
    dot(x_2) = A - beta_2 x_2 - Gamma_2 (x_2 - 4x_1 b)

QSS dot(x_2)=0와 별도의 x_2<<1 근사를 적용하면

    dot(x)=-C_P [n_H alpha_B x^2-beta_P(1-x)b]
    C_P=[1+K_alpha Lambda n_H(1-x)]/
        [1+K_alpha(Lambda+beta_P)n_H(1-x)]
    K_alpha=lambda_alpha^3/(8pi H)
    R_alpha=8pi H/(3lambda_alpha^3 n_H x_1)

를 얻는다. beta_2는 전체 n=2 shell을 곱하는 계수이며 beta_P와 혼용하지 않는다. alpha_B의 단위는 volume/time, K_alpha는 volume*time이고, 여기 K_alpha는 기존 원자 weak K가 아니다.

공통온도 및 전자질량 근사에서 beta_P=alpha_B [m_e k_B T/(2pi hbar^2)]^(3/2) exp[-chi_2/(k_B T)]. 역반응의 E_alpha를 더해 chi_1을 복원한다. reduced mass 사용 시 양쪽 comparator와 상수 pin을 함께 바꾼다. RECFAST1999의 literal T_m 및 F=1.14와 HyRec2011의 beta(T_gamma) 관례는 구분한다. 첫 구조적 comparator의 fudge=1은 별도 선택이지 보정된 RECFAST 전체를 재현한 것이 아니다.

Bianchi I에서 dot(E)/E=-H-sigma_ij e_i e_j이고, sigma=0 및 별도로 등방 radiation/matter/zero tilt 조건에서 FLRW Liouville 항을 얻는다. 다른 Bianchi 유형에 shear=0만으로 충분하다는 주장을 하지 않는다. dot(n_H)+3Hn_H=0을 사용하면 x의 희석항은 상쇄되며, dx/dz=-dot(x)/[(1+z)H]이다.

## 이번에 얻은 정확한 closure defect

QSS 이전의 같은 유효 shell 모델에서는

    dot(x)=-C[A-beta_P x_1 b]-(1-C)dot(x_2)

가 정확하다. x_1=1-x-x_2, n_1=n_H x_1, n_1^P=n_H(1-x),
C_t=C(n_1), C_p=C(n_1^P), B_0=A-beta_P(1-x)b로 두면

    delta_C=C_t-C_p
           =K_alpha beta_P n_H x_2 /
            ([1+K_alpha(Lambda+beta_P)n_1]
             [1+K_alpha(Lambda+beta_P)n_1^P])

    dot(x)-F_P(x)=-delta_C B_0-C_t beta_P b x_2-(1-C_t)dot(x_2).

따라서 들뜬상태 점유, C의 ground-density 의존성, finite-relaxation 항을 각각 남겨야 한다. 세 항 절댓값합은 이 shell 축약에 한정된 조건부 상계다. full radiative-transfer, geometric, physical rate error는 포함하지 않는다.

L=beta_2+Gamma_2, q=(A+4Gamma_2 x_1 b)/L, delta=x_2-q에 대해 dot(delta)=-Ldelta-dot(q). L>=L_*>0이면 초기층과 forcing slope의 비교상계가 성립한다. 실제 trajectory의 q 미분은 미평가다. Saha root와 C~1 tail만으로 복원 성공을 판정하지 않는다.

유한 2s/2p 혼합의 별도 algebraic test family에서도 statistical-shell 한계를 계산했다. 이것은 실제 수소의 혼합률이나 새 physical provider 채택이 아니다.

## 실제 실행과 경계

이번 standalone 정확유리수 API 시험 16건이 기대된 assertion RED 후 GREEN을 통과했다. 생산 모듈을 import하지 않는 SymPy 구성에서 13개 항등식, 36개 정확유리수 coefficient 조합을 확인했다. 80자리 120개 relaxation 공식 진단은 interval 또는 physical history 검증이 아니다. 원자적분/native/receiver/history/과거 suite 재실행은 모두 0회다. 별도 인간/agent/proof-assistant 검증은 없다.

## 작업 중 발생한 live source 진전

시작 입력: bass_cr bcd33d5706efccb0e3aaf5215b0aadc0b13a2ab3, rei_bianchi dc931a67cd5ed25046a96eb5deb42186d72176da.
게시 전 receiver가 67957715cf3336b89c27c1e59c33ca23098f8934로 전진했다. bounded compare의 2개 commit에서 F01 provider/homogeneous adapter와 REI-CHAT-PB01 결과가 추가됨을 확인했다. 현재 closure_process_decision blob 456bf4fd1a6f1005b69cdbb0c246a8ec50a5d60e는 동일하다. F01 완료는 계수/단위/흡수 ledger 구현 범위이며 physical provider/history admission은 아니다.

수신측 PB01 README, NEXT_HANDOFF와 F01 반환을 읽었다. PB01의 모델 불일치/계수4/conditional QSS 결론은 본 유도와 일치한다. PB01의 원시 ZIP을 복원하거나 해당 scalar/linear 검사를 재실행하지 않았다. 같은 assistant의 별도 구성 결과이며 외부 독립 reviewer로 세지 않는다.

최신 다음 노드는 owner의 REI-CHAT-PB02_SOURCE_BOUND_REDUCTION_CONTRACT에 통합한다. 이 문서가 archive의 이전 일반적 next-reference 순서보다 최신 routing을 제공한다. 이미 PB01이 확보한 scalar points와 source profile을 반복 생성하지 않는다. 실제 level/radiation residual 또는 REC-owner adapter의 exact commit/path/blob를 먼저 연결하고, 지원될 때 동일 입력의 C,beta_P,R_alpha,retained residual과 reduced RHS를 비교한다. 연결 부재는 MISSING_PEEBLES_CLOSURE_AT_CONSUMER이며 현재 Case-A lock을 소급 치환하지 않는다. 짧은 history는 source-bound 계약 이후에만 판단한다.

## 완전 패키지 및 원격 회수

PEEBLES_FLRW_LIMIT_THEORY_PACKAGE_20261004_v1.zip
bytes=26913
SHA256=cf7c2e7f72015ffd7e3063a342138421da94340e12e4a569f4c63908d3fe8036
Dropbox ID=id:BSpOijBcT10AAAAAADyDuw
Drive ID=1-bWQX9VG7r72Jv76OfUY3WSJjNp_XXfL

ZIP의 17개 CRC와 16개 payload SHA를 확인했고 양쪽 업로드 완료/ID/크기를 확인했다. 등급은 R1 UPLOAD_VERIFIED이며 원격 full restore는 하지 않았다. 한 mirror만 직접 회수하며 사용자 재업로드를 요구하지 않는다. ZIP에는 전체 유도, 새 코드/시험, 실행 로그, machine-readable benchmark와 DAG가 있다. Git에는 이 이론/동기화 요약만 게시하며 production 구현을 게시했다는 뜻이 아니다. ZIP은 업로드 후 불변이고 다음 작업의 최신 routing은 이 문서 및 detached sync receipt를 따른다.

원전: Peebles1968 DOI10.1086/149628 Eqs26,29-31; Ali-Haimoud/Hirata2011 DOI10.1103/PhysRevD.83.043513 SecIIA Eqs1-11; Seager/Sasselov/Scott1999 astro-ph/9909275v2 Eqs1,3와 온도 문단. 원 Peebles PDF screenshot 실패는 보존했고 readable HyRec PDF page3을 시각 대조했다.

G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO. CR_OFF_FASTEST default 및 parked precision atomic lane 유지. NCP의 새 중원자/full-K batch 요청 없음.
