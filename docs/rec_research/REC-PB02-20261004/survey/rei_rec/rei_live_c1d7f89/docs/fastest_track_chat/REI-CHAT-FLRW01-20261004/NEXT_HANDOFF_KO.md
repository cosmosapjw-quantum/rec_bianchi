# FLRW01 -> FLRW02 source-bound three-equation regression

Repo cosmosapjw-quantum/rei_bianchi, branch forward/rust-reion-kernels-20260922, draft PR83. 시작/단계경계/게시전후 live ref를 읽고 바뀐 source만 compare한다. 새 branch/merge/force push와 전체 suite 재실행은 없다. 현재 사용자 우선순위는 local photoionization-recombination/filling/photon equation 회복이며 Peebles PB02와 FT07은 deferred다.

읽기: README_KO.md -> FLRW_RECOVERY_CONTRACT.json -> RESULTS_SUMMARY.json -> ZIP REPORT_KO.md 필요한 절 -> 실제 소비자 source. 이미 닫힌 FT/PB 유도 및 외부 F00/F01/F02를 반복하지 않는다. ZIP SHA와 remote publication identity는 분리한다.

다음 REI-CHAT-FLRW02_SOURCE_BOUND_THREE_EQUATION_REGRESSION:
1. Codex F03가 들어오면 exact commit/path/blob의 actual local species RHS, per-species absorbed photons, emitted ionizing-photon count, group-edge exits, diffuse inventory를 읽는다. 정답식을 외부 주입하고 consumer 복원이라고 하지 않는다.
2. fraction에 -3H 없음, pureH recombination x^2, proper/comoving count conversion, sum photon loss=sum species events, lowest-edge redshift flux를 같은 input/site에서 검사한다.
3. XM와QV를 구분한다. filling consumer가 없다면 원 homogeneous F00을 변경하지 않고 별도 manufactured sharp two-phase fixture에서 Delta=1,CI=1,빠른흡수 극한의 표준식을 확인한다. density bias/partial ionization/storage/redshift/He loss의 반례도 유지한다.
4. exact defect dotQV-(s-QV/tref)=-doteta-lz-aother+iextra-dot(XM-QV)-(reff-QV/tref)의 각 항을 독립 output으로 연결한다. tref는 사전 고정하며 잔차0을 만들기 위해 fitting하지 않는다. emitted energy에서 jrec photon count를 추측하지 않는다.
5. local OTS alphaB와 explicit ground recombination photons를 중복하지 않는다. 표준 Q식의 추가 closure조건을 코드복원과 따로 기록한다. overlap clip 대신 초과 photons를 저장하거나 source/loss 경계로 보낸다.

최종9개 경량ODE, 이번turn전체18개, 최대차원5의 기준은 standalone이다. 실제 Rust/source-bound regression과 physical admission은 아직 없다. 기존 local<2e-4/public width<2e-3,[160,161] FAIL 및 tick160 보존. production runtime Python/JAX를 복원하지 않는다.

같은 branch의 새 scoped directory에 append-only non-force 게시하고 Drive1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ와 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1에 create-only 백업한다. metadata ACK와 full restore/science validation을 구분한다.
