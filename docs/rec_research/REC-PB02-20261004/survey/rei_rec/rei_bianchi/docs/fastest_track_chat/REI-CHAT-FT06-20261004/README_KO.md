# REI-CHAT-FT06-20261004: paired science specification

SCOPED_PAIR_SPEC_DERIVATION_AND_LIGHT_PILOT_COMPLETE__PHYSICAL_MODEL_ERROR_AND_PRODUCTION_OPEN.

이번 단위는 동일 부피팽창의 prescribed FLRW/Bianchi comparison을 정의하고 각도 모멘트·source realization·관측면·오차 진단을 연결했다. 작은 scalar shear signal의 부호가 six-axis와 isotropic-continuum 근사에서 달라지는 반례를 실제 계산했다. 원자 정확도, omitted processes, Einstein-solved cosmology와 actual Rust remainder는 승인하지 않는다.

## 전체 재현 패키지

- REI_CHAT_FT06_20261004.zip, 286959 bytes, 109 entries.
- SHA-256: 03e56d2844a767a840f3047361a2aab5e8e07d80ba9c6d3354c3f70037eceabe
- Drive: https://drive.google.com/file/d/1e3LU7LlDn7FASltkouJYMW515Dm_tCco/view?usp=drivesdk
- Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FT06_20261004.zip
- 양쪽 ID/path/size 확인 완료, R1 metadata. 원격 전체 restore/hash 확인은 미수행. SHA는 로컬 sealed archive 값이다.

ZIP의 rei_chat_ft06_20261004/REPORT_KO.md, PAIRED_SCIENCE_SPEC.json, PILOT_RESULTS.json과 research/가 전체 SSOT다. 이 Git 폴더는 요약·기계가독 계약 projection·실행반환 수신·다음 인계다. projection을 full contract의 byte identity로 취급하지 않는다.

## 과학적 증분

1. 초기 등방·회전 공변·매끄럽고 threshold-separated인 coupled model은 fixed a_bar에서 tracefree shear의 scalar first variation이0이다. 일반 scalar는 짝함수가 아니며 tr(B^3)의 cubic이 허용된다. Collisionless kernel은 K/A=1+(4/15)tr(B^2)eps^2-(8/63)tr(B^3)eps^3+O(eps^4)다.
2. 여섯 축은 M2=delta/3만 맞고 M4가 틀린다. scalar energy quadratic coefficient는 continuum의5/8이다. 각 axis1/15, cube corner8개 각3/40인 양의14점 rule은 M4를 맞춘다. 모든 angular function에 대한 exactness는 아니다.
3. common-time와 observed-z를 분리했다. 방향별 emission-time 이동은 delta t_e=n_o^T(beta_o-beta_e)n_o/H_e이며 passive tau의 endpoint 항은 -c*sigma_T*n_e(t*)*delta t_e다. 이는1차일 수 있고 fixed-time chemistry의2차 변화와 다르다.
4. 같은 H/matter/Lambda와 비영 shear를 모두 고정한 Einstein pair는 불가능하다. proper sigma2=sum(dot beta_i^2)/2에서 3H^2=8*pi*G*epsilon_m/c^2+Lambda*c^2+sigma2다. 같은 matter에서 mean expansion 변화도 scalar response와 같은2차다. 이번 background는 prescribed다.
5. common atomic realization은 같은 함수이지 같은 T/site point value가 아니다. RR alpha_lambda=alpha0 exp(lambda_a+lambda_s ln(T/Tp))면 q_lambda=q0+lambda_s를 cooling에도 반영한다. 실제 cooling 오차에는 rate오차뿐 아니라 lnT slope오차가 필요하다. +/-0.02 probe는 물리 uncertainty bound가 아니다.

## 제한된 실제 pilot

s=t/1e13s, a_bar=exp(.03s), beta=eps*(1/3,2/3,-1)*s, eps=.02. 같은 FT03 초기 조성·T0=50000K·nH0=1e-4cm^-3·CaseA 및 20/35/70eV line spectrum. 128방향 결과는 deltaT=+0.0216190194K, delta xHeIII=-2.522812681e-7, delta tau=-8.085426114e-12다. six axes에서는 deltaT=-0.0228612997K, delta xHeIII=+2.613212021e-7로 부호가 반대다. FT05의 별도로 정의한 six delta-beam model을 오류라고 부르지 않는다.

32->128 paired scaled-observable 차이 최대4.85048668e-11, 회전차이4.33661995e-11, tightened-time1.77635684e-15, 독립5population+lnT 조립식5.32907052e-15. 좁은 flat bands는 lines와 다른 spectrum이며 동일 band의 Gauss4->8 차이는6.66133815e-16이다. 모두 경험적 수렴 진단이지 rigorous bound가 아니다. family continuous T range는 약31878.9116792~106192.751654K이며 guard[30000,110000]의 첫 이탈을 배제했다.

최종 새 runner6단계 exit0, unit8개, random admissible RHS energy identity24개, 마지막 reproduction solver49회(45 unique saved pilot runs), 최대787변수. 모든 저장run의 energy ledger 잔차 최대1.7763568394e-14eV/H. full Rust/Grackle/Einstein history와 기존 suites 재실행은0이다.

## Git 동기화

시작HEAD ba86cc1 이후 외부5f3bfe2fc8fe275ab6a054ca9082f03c5b91427a를 live 조회로 수신했다. F00 설계와 F02 scalar hydrogen oracle 반환을 읽었으며 외부 테스트를 여기서 다시 실행하지 않았다. CODEX_RETURN_ACK.json은 실제 Git 인계 수신이며 browser 직접전달 성공을 뜻하지 않는다. 이 외부 commit을 parent로 보존한다. Codex의 다음 작업F01은 중복 구현하지 않는다. actual_solver_binding=NOT_IMPLEMENTED_F03_F04이므로 FT04는 여전히 대기다.

다음 chat은 FT07 physical model error budget. strict local<2e-4/public width<2e-3, [160,161] FAIL 및 tick160 유지. 새 branch/merge/force push와 canonical TASKS 수정 없음.
