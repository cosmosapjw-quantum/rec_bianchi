# FLRW01: 국소 이온화율, 광자수, filling-factor 식 복원

사용자 우선 요청으로 재이온화의 세 식을 검증했다. Peebles C-factor PB01과 별개다. PB02와 FT07은 deferred이며 완료하거나 삭제하지 않는다.

판정: LOCAL_RATE_AND_PHOTON_REDUCTION_DERIVED_LIGHT_CHECKED__FILLING_CONDITIONAL__FULL_CONSUMER_NOT_VERIFIED.

## 핵심 결과

1. proper continuity와 dot nH=-3H*nH로부터 dx/dt=(1-x)*(Gamma+ne*C)-alpha*ne*x+Ssec/nH. 분율에 -3Hx 없음. pure H에서는 ne=nH*x이므로 recombination은 -alpha*nH*x^2다. Case-A도 일관된 source 아래 이 국소식은 복원한다. Peebles를 복원하지 않는다는 앞선 판단은 다른 physics closure의 문제다.
2. n_E[proper cm^-3 erg^-1]는 partial_t n_E+3H*n_E+partial_E(-HE*n_E)=s_E-c*kappa*n_E. 고정 E0 이상을 적분하면 dot n_>+3H*n_>=s_>-A_>-H*E0*n_E(E0). 적색편이는 전체 photon을 없애지 않지만 ionizing subset에서는 제거한다. comoving/per-H count에 -3H를 또 넣지 않는다.
3. photon/H=eta, mass-ionized fraction XM, geometric filling QV를 구별한다. 같은 inventory에서 dot(XM+eta)=s_star-(rA-jrec)-a_other-l_z+i_extra. jrec는 emitted ENERGY가 아니라 tracked ionizing photon NUMBER다.
4. Xi=XM-QV, reff=rA-jrec라 하면 정확한 복원 잔차는 dotQV-(s_star-QV/t_ref)=-doteta-l_z-a_other+i_extra-dotXi-(reff-QV/t_ref). t_ref는 독립적으로 지정하며 이 잔차를 지우도록 사후 fitting하지 않는다.
5. sharp fully-ionized/neutral phases에서 XM=QV*dI, dI=<Delta|ionized>. 온도 및 electron factor가 고정되면 rB=alphaB*chi_e*nbarH*QV*dI^2*CI. CI=<Delta^2|I>/dI^2이며 global CHII=CI/QV다. 두 clumping을 무기록 치환하지 않는다.
6. dI=1, photon storage derivative/threshold exit/다른 sink/extra process를 무시할 수 있고 Case-B photon ownership이 일관될 때 표준 dotQV=emissivity_comoving/nH_comoving-QV/t_rec, 1/t_rec=alphaB*chi_e*CI*nH_comoving*a^-3가 나온다. geometry isotropization만의 결과가 아니다.

## Case와 반례

Primary-only Case-A escape는 net rA다. 명시적 Case-A diffuse에서 jrec=r1= rA-rB인 제한적 pure-H ground-photon approximation이면 합산 inventory는 rB를 갖는다. 여기에는 storage를 남기므로 즉시흡수 가정이 필요하지 않다. Local OTS는 ground capture와 같은 H의 즉시 재광이온화를 함께 제거하여 primary-only+alphaB를 쓴다. alphaB와 동일 explicit ground source를 동시에 쓰면 이중계상이다. 고온 ionizing tails/helium cross absorption/secondary를 이 단순 상쇄로 숨기지 않는다.

정확 반례: 같은 mean x=.5에서도 uniform partial recombination은 .25*alpha*nH^2, sharp binary 반반은 .5*alpha*nH^2다. 같은 부피의 Delta=(1.6,.4),x=(1,0)는 QV=.5,XM=.8이며 recombination/(alpha*nbarH^2)=1.28이다. mean(nHI*Gamma)=.28, mean(nHI)*mean(Gamma)=1인 covariance 반례도 있다. Q=1을 clip하고 storage를 고정하면 초과 photons가 누락된다.

## 실제 경량 검증

21 symbolic identities,5 counterexample profiles,12 spectrum quadratures,4 finite groups,64 FLRW rays,20 source-algebra points. 최종 재현은8 local+1 inventory ODE, 최대차원5이며 초기 검산까지 turn전체18회다. Unit tests2개와 최종 runner2단계 exit0. 70자리 spectrum 비교는 산술 검산이지 원자 accuracy가 아니다.

density/fraction state 비교 최대차이1.0447198661722723e-12. 별도의 선형 photon-storage bath는 s=.4,kH=.6,loss=.4,r=.1,X0=.2,eta0=0,t=1에서 eta=.25284822353142306,X=.266168886490351. 즉시흡수식은 X=.5616178114633539. 독립 matrix exponential과 최대차6.661338147750939e-16, ledger잔차1.1102230246251565e-16. 이는 prescribed bath이지 self-consistent cosmology나 filling geometry의 인증이 아니다.

## 실제 소비자와의 경계

67957715cf3336b89c27c1e59c33ca23098f8934의 homogeneous_rates.rs는 photon_loss_comoving/(a*MPC_CM)^3=sum species events라는 absorption owner를 제공한다. group_rates.rs의 4group 합은 sumS-sum(kN)-r0*N0다. r0*N0를 lowest-edge exit로 기록한다. 임의 redshift_coeff가 arbitrary spectrum의 edge reconstruction임을 인증하지 않는다. lowgroup effective MFP와 homogeneous explicit HI opacity를 중복하지 않는다. 현 runtime return의 다음 구현은 F03이고 실제 전체 HHe/volume consumer regression은 이번에 실행하지 않았다. Python source-algebra 검사를 Rust 실행으로 세지 않는다.

## 자료와 다음 단계

전체 보고서/계약/연구코드/결과/실패/manifest: REI_CHAT_FLRW01_20261004.zip,51328bytes,39entries.
SHA256 aa9bb322555bc72ce2055c14a57ddc680d4248d175a9cd60767603e2b3a1c86d.
Drive https://drive.google.com/file/d/1wOFiXDT69E9ssWRp9biB9Ts2A6YKQK-P/view?usp=drivesdk
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW01_20261004.zip
두 provider 완료/ID/path/size 확인. 원격 checksum 및 전체 restore는 미검증이다.

다음 REI-CHAT-FLRW02_SOURCE_BOUND_THREE_EQUATION_REGRESSION: 실제 F03의 species/photon/boundary/diffuse/volume hooks를 exact source에 묶는다. missing filling closure에는 별도 manufactured two-phase fixture를 쓰고 원 homogeneous F00을 덮어쓰지 않는다.

원전: C2-Ray DOI10.1016/j.newast.2005.09.004 Eq11; Haardt-Madau2012 DOI10.1088/0004-637X/746/2/125 Eq1; Madau-Haardt-Rees1999 DOI10.1086/306975 Eqs18,20. 추가 범위 arXiv1201.0602 및1710.07636. 상세 source/failure 기록은 ZIP 참조.

기존 strict local<2e-4/public width<2e-3,[160,161] FAIL=2.1245050576368385e-4 및 tick160 보존. production code,source lock,canonical gates 변경 없음. 새로운 branch/merge/force push 없음.
