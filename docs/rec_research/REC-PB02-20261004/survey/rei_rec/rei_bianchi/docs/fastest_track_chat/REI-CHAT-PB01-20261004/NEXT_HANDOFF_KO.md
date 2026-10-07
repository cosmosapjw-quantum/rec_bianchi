# PB01 -> PB02 source-bound Peebles reduction contract

대상 cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, draft PR83. 사용자 요청으로 Peebles C-factor FLRW 복원을 FT07보다 우선한다. FT07은 deferred이며 완료/삭제하지 않는다. 새 branch/merge, production recombination surrogate, 전체 Rust/Grackle/HyRec 빌드, 큰 history는 시작하지 않는다.

첫 읽기와 단계 경계/게시 전후 live ref를 확인하고 변경된 경우 관련 diff/CODEX_SYNC/runtime_returns만 읽어 보존한다. 과거 FT 전체 시험과 Codex F00/F02를 반복하지 않는다. 읽기 순서는 이 README/contract/results -> ZIP 보고서 필요한 절 -> 실제 연결 source다.

현재 결론: FT03 Case-A instantaneous escape와 F00 합성 closure는 기하만 FLRW로 보내도 Peebles를 복원하지 않는다. F02는 constant-rate scalar oracle다. retained n2의 조건부 QSS 제거는 표준 C를 복원한다. 이론 유도/현재모형 mismatch/production 미검증을 구분한다.

PB02: 실제 level/radiation residual 또는 기존 REC-owner adapter를 exact commit/path/blob에 연결한다. 없으면 MISSING_PEEBLES_CLOSURE_AT_CONSUMER로 남기고 기존 F00 lock을 소급 치환하지 않는다. pure H,Tm=Tr,shared alphaB,betaP=4beta_shell,x2p=3x2s,thermal n2 bath와blue Lyalpha boundary,Lambda2gamma,opaque Sobolev,QSS,x2<<1의 최소 호출 계약을 작성한다. consumer가 산출한 C, betaP, per-2p Ralpha, shell residual/reduced electron RHS를 독립 scalar oracle와 비교한다. Peebles C를 외부에서 강제 주입하고 유도 복원이라고 부르지 않는다.

Saha root와C~1 tail만으로 통과하지 않으며 C<<1 점, factor4/factor3 negative control, inverse bath, fraction/redshift sign, QSS lag를 확인한다. Tm!=Tr,finite Sobolev,보정 RECFAST는 별도 profile이다. 실제 source binding이 된 뒤에만 동일 IC,H(z),T(z),constants의 짧은 history regression을 판단한다. full HyRec와 원 Peebles의 exact equality를 요구하지 않는다.

nH proper cm^-3,alpha cm3/s,Lambda 및beta s^-1,K cm3 s,h=2pi hbar,E21=chi1-chi2=hc/lambda. helium electron은xe*xp. fraction에-3Hxe없음. retained binding=chi1*xp+E21*x2이며 instantaneous CaseA emission을 중복 적용하지 않는다.

기존 strict local<2e-4/public width<2e-3,[160,161] FAIL과tick160,physical fail-closed를 보존한다. 같은branch append-only non-force 게시와 기존 Drive1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ / Dropbox BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1 create-only 백업. metadata와 byte restore,과학 정확도를 분리한다.
