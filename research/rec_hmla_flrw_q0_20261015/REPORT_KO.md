# REC 원본 HyRec EMLA2s2p q=0 자체 재결합 이력 연구

2026-10-15 KST. 선택된 연구: 새 이론 R2(원전·가정·소스·코드 연결), 작은 독립 H+Tm 모델의 코딩 C5/C6 구현과 과학 수치 검사. 기초 REC PR90 parent 99dbd883042bb60734f92cd424f2f91826d1ea48. 별도 local Codex 및 REI 생산 프로세스 변경 없음.

## I. 무엇을 실제로 풀었는가

**독립 REC Python 적분:** 소스는 원본 HyRec 2012 Oct ZIP SHA256 48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27, 보존된 Alpha_inf.dat/R_inf.dat effective atom tables. 새로운 trajectory/hmla_flrw.py의 HMLAFlrwSource.hydrogen_rhs_ln_a는 원본 C hydrogen.c 약 236–264행 rec_HMLA_dxHIIdlna 수식을 물리적 단위와 함께 재구현했다.

상태는 eta=ln a, x_HII=n_HII/n_H, T_m[K]. z=1600→600, q_ref=0, H(z)=HyRec 원본 FLRW, n_H(z)=HyRec 원본 수소 핵수 밀도, neutral helium heat capacity 포함. H+Tm는 SciPy BDF로 **직접 결합 적분**, IC는 Saha/post-Saha analytic source local linearization이고 참조 x_e(z) 값은 주입하지 않았다.

**범위:** EMLA2s2p, original effective 2s/2p rates, two-photon 2s→1s rate and Sobolev Lyα escape. 이것은 원본 HyRec FULL의 dynamic nonthermal Lyα diffusion, Raman/two-photon spectral memory, full helium evolution, atomic/virtual split-domain owner와는 다르다. Helium은 z1600→600에서 중성이라 가정하고 thermal denominator에 f_He만 유지하므로 일반적인 전체 x_e가 아닌 x_HII를 적분한다.

## II. 원본 C에 근거한 물리 방정식

HyRec 원본 hydrogen.h, hydrogen.c가 사용하는 cgs/eV source의 물리 정규화:
- n_H[cgs]=10^-6 n_H[SI], alpha[cgs]=10^6 alpha[SI].
- Tr[eV]=8.617343e-5 Tr[K], H[s^-1], original case Lambda_2s1s=8.2206 s^-1.
- Lyα rate = 4.662899067555897e15 H/[n_H(cgs)(1−x_HII)] s^-1.

Define beta_s, beta_p, R=R_2p2s, Λ=Λ_2s1s, L=R_Lya.
Gamma_s=beta_s+3R+Λ, Gamma_p=beta_p+R+L.
The subtraction-safe Schur denominator is

D=(beta_s+Λ)(beta_p+L)+R(beta_s+Λ+3beta_p+3L).

C_s=[Λ(beta_p+R+L)+3RL]/D,
C_p=[L(beta_s+3R+Λ)+RΛ]/D.

S=SahaCoeff * Tr^(3/2) exp(-EI/Tr)/n_H(cgs), EI=13.598286071938324eV.
Delta_e=x_e*x_HII−S(1−x_HII).

dx_HII/deta=−n_H(cgs)/H * sum_i C_i{alpha_i Delta_e + S(1−x_HII) Delta_alpha_i}.

Delta_alpha=alpha(Tm,Tr)−alpha(Tr,Tr), NOT a temperature derivative. Thermal
dTm/deta = −2Tm + Gamma_C/H (Tr−Tm),
Gamma_C=4.91466895548409e-22 Tr[K]^4*x_e/(1+x_e+f_He) [s^-1].

Wolfram 15.0.1에서 D, C_s, C_p와 original C의 subtraction 표현의 residual 3개 0. D는 비음수 rates와 Λ,L>0에서 양수이며, 열원/원자 source가 서로 다른 clock을 사용하는 근사를 추가하지 않았다.

## III. 원본 C 순간 RHS 직접 재현

새 scripts/c_harness/original_hyrec_hmla_rhs_harness.c는 수정되지 않은 archived original hydrogen.c와 hyrectools.c를 GCC로 링크한다. scripts/verify_hmla_native_rhs.py가 z=(650,900,1200,1600), x_HII=(.2,.5,.9,.995), helium 자유전자 추가=(0,.2 f_He), Tm/Tr=(.82,.94,1.0)의 **96개 독립 source state**를 원본 C 함수와 새 Python HMLA 함수에 각각 주었다.

측정 최대 scaled relative 차이 **1.8348257610199602e-14**, 승인 사전설정 3e-10. 원본 source RATE table 재현에 대한 PR90 60점 최대 1.364e-12와는 별도의 더 직접적인 whole RHS 검증이다.

## IV. 두 원본 C 모델과 REC 자체 적분의 교차 비교

원본 FULL HyRec2012 C를 별도 사본의 정확히 1개 source macro만 MODEL FULL→MODEL EMLA2s2p 로 바꿔 새 C EMLA mode reference를 컴파일/실행했다. 다른 원본 C 파일과 source table은 그대로다.
- original source header SHA256 cab1a5d92389ea7eec408e8a8419f59c717a227332bc2ae2b51e84488578e7e2
- switched source header SHA256 7f704890535b25b4836dc5cf187acff5611ae17a90370e6d0af635c06c69b593
- common input SHA256 523eeef77af15c00404962afc0f63ff907897b6d7535ea782e46bd46538395b3
- C-EMLA result SHA256 75d4bd873fa45b941a58a2977c5f8206002fedead134499d2a16a976b49d38d6
- ORIGINAL default C FULL result SHA256 e772c8cdd19e20618a1f71c2104e542fbb7de287ecc8ee1c7ae06697af8bf906.

첫 Saha 값 x_HII(z1600)=.9943708480958812; 자체 post-Saha source-Jacobian 초기값 .9944061343157344; 원본 C EMLA 최초값 .994406140624752. Delta ≈6.31e−9. 이 initial value는 원본 C 이력값을 읽어서 설정한 것이 아니다. 물리적 Saha x'와 유한차분 local d f/dx를 이용한 first-order post-Saha 선형화이다.

REC 자기 BDF 적분 z1600→600, 201 output points, coarse/baseline/tight rtol (3e-6/2e-7/2e-9) 실제 실행. 가장 조밀한 결과:
- own z600 x_HII=.0009569296273028047, Tm=1628.163562779938 K
- OWN Python vs independent original C EMLA source mode history maximum relative difference **2.5313434416585068e-5** at z≈901.5
- OWN Python vs independent original C FULL maximum relative difference **0.01427747173733307** at z≈1270.7
- ORIGINAL C EMLA vs ORIGINAL C FULL maximum relative difference **0.014281952168201384** at z≈1268 (600≤z≤1600).
- Own Tm vs FULL maximum relative difference ≈1.03928668211406e-5.
- Baseline→tight own x_HII maximum relative difference 6.712733820135597e-6. Coarse→tight 6.243091725099958e-5. 실제 수치 오차가 모델 모드 FULL 대 EMLA 차이를 설명할 수 없음.
- C EMLA reference includes residual helium whereas Python scoped source assumes neutral He. Their small residual mismatch is not independently proven to be numerical error only.

Thus the original C model switch nearly reproduces the entire FULL-vs-Python discrepancy. A new FULL-vs-EMLA physical source replacement, *not merely tightening BDF*, is the appropriate science next step. FULL radiative transfer and split-domain dynamic ownership remain **NOT_ADMITTED**. This result is not a proof that every discrepancy comes uniquely from Lyα diffusion alone: the FULL switch includes other spectral effects.

## V. 실제 벡터화·스레드 병렬화 테스트

New method hydrogen_rhs_ln_a_many uses the canonical original rate table once for common (z,Tm), then evaluates separate x_HII/x_e C-factors with NumPy arrays. Scalar-vs-batch results on 4 source points×53 states match to <2e-12, actual comparisons bit identical. Measured source-only runtime (3-repeat median, Linux host):
- N64 scalar 8.15ms / vector .1666ms, 48.96x
- N512 scalar 82.51ms / vector .1835ms, 449.66x
- N2048 scalar 294.97ms / vector .1940ms, 1520.81x
- N8192 scalar 1213.96ms / vector .2406ms, 5046.51x.
This does NOT imply full ODE is 1500x faster: the ODE has only two evolving global states at a time. For four independent physical chunks (8192 total) 1/2/4 CPU threads cost 0.807ms/1.910ms/2.861ms respectively, no benefit under observed workload. Default vector array evaluation is single worker. No CUDA, no Numba install, and no claim of arbitrary heterogeneous Tm rates shared.

## VI. 검증 상태 및 다음 실행

New targeted tests with actual original C HMLA compilation PASS 12; scoped source and thermodynamic tests including Saha/post-Saha, helium electron extra, positivity, units, BDF refinement, batch equivalence. Full REC pytest and repository quick gate results recorded in TEST_RECEIPT.json. Native full-recombination science admission remains NOT_ISSUED. The generic Bianchi background, native REI Rust code, original source header and all local-Codex worktrees were not changed by this branch.

Next theory R3: map native HyRec FULL 311 virtual bins and 2s/2p source owner, identify Lyα nonthermal photon and atomic current equations, validate species/gas photon energy source transfer, then implement smallest causally valid virtual-level transport replacement. Respect source-domain admissibility and single accepted-step owner. Next coding step: source-identifiable FULL coupling, helium dynamics, and source-locked q=0 full x_e/Tm convergence before Bianchi q≠0 extension. **Do not relabel the HMLA result as FULL or REI abundance history.**

Primary: Ali-Haïmoud & Hirata 2011 PRD83 043513 (generalized 2s/2p C factors Eqs 43–46); original HyRec Oct2012 hydrogen.c, history.c, source rate tables; Lee & Ali-Haïmoud 2020 PRD102 083517. SciSpace and Exa source search cross-checked primary source, actual archived C is authoritative for the current numerical formulation.

## VII. 2026-10-15 관련 repo 최신 교차 확인

- BASS_HE PR59 HEAD 9a4a554bfffd5aea81dbf0ea018f092f55e3efa9: warm P01 실제 third saved-cell, 2904 photon-source error, Verner FT03/HM12. Warm HE/later REI source 영역의 광자·가스 결합 방법론은 향후 운반 가능하지만 원시 z600..1600 C HYREC2s2p rate나 flat initial condition으로 바꾸지 않는다.
- bass_cr PR67 HEAD 5c6ea6ceb1cffb05f482bc0437b4e5eb2b2a13d9: heap cohort source / vector Verner source, 방향별 검증, 병렬 IPC가 느린 실제 benchmark. 이번 HMLA batch에서는 원자율 테이블을 공통 z/Tm 상태에 대해 공유하는 방식만 직접 계승했고 UVB 값을 혼합하지 않는다.
- WU088_HH PR75 HEAD 2f06fc263a1162a1eb0fb2ce7fdfda2317e0f272: hydrogen two-centre source partial angular residual. 원시 primordial recombination C source로 채택하지 않는다.
- REI PR117 마지막 확인 HEAD e4db1ba1a8c22c7e443650fd4f51d8a3c31a4b1e. 사용자 요청에 따라 REC 개발은 대화 환경에서 직접 수행. REI owner producer와 STATE 체크포인트는 수정하지 않는다.
