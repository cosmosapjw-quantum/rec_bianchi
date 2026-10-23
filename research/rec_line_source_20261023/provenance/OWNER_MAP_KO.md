# LINE01 실제 소스 소유권·재사용 조사

## 판정

**현재 단위에서는 저장된 원본 HyRec 상태를 읽기 전용 조건으로 받아,
소유자가 하나인 독립적인 resolved Lyα 선 source를 만들 수 있다.**
기존 코드에 이미 `IsotropicEinsteinLineSource`가 있으므로 그 Einstein
paired-action을 재사용하고, LINE01은 수·에너지 장부와 ANGULAR01 탈출
모멘트 연결을 추가하는 것이 적절하다.

이것은 native FULL transfer를 수정하여 새로운 Bianchi 우주론 해를 얻었다는
뜻이 아니다. 기존 FULL의 Sobolev·history·virtual diffusion·압축 행렬을 둔 채
같은 Lyα 방출원을 추가하면 중복이다. 따라서 현재 구현은 standalone/source
owner selector를 두고, canonical native와 resolved LINE01의 동시 합산을
거부해야 한다.

이 조사에서 ODE, native runtime, 완료 campaign, 기존 테스트는 실행하지 않았다.
수행한 계산은 파일 byte hash, CSV 읽기, `allow_pickle=False` NPZ key/shape
확인뿐이다. Physical HOLD, REC U5 HOLD_9_FAIL/HOLD_8_FAIL,
CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED,
REI_activation=false를 유지한다.

## 1. 최신 변경의 제한된 확인

기존 407 refs / 347 PR 접근 가능 inventory를 재사용했다.
2026-10-22 22:40 UTC 이후의 변경을 확인하기 위해 REC와 REI의
`sort=updated&direction=desc&per_page=20` 결과를 각각 읽었다.
각 목록은 10월19일까지 내려가므로 cutoff 이후 갱신 PR은 해당 페이지에
포함된다. 이것을 모든 미게시 branch commit이나 접근 불가 대화까지
다시 조사했다는 주장으로 확대하지 않는다.

| PR | 현재 HEAD | updated UTC | 판정 |
|---|---|---|---|
| REC119 | `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7` | 10-22 23:13:36 | 원래 REC126 HEAD 유지 |
| REC127 | `5185c396b7e07076565ca2f5044a5ccd193e6ee1` | 10-22 23:13:34 | 완료 ANGULAR01 anchor 유지 |
| REI220 | `8be7533cc97b3302bf42608699d6e8313ed6af8a` | 10-22 23:13:37 | 원래 REI129 HEAD 유지 |
| REC114 | `df95a074730ea0d13d609cf88d448f01f4a47ef1` | 10-21 05:05:32 | canonical owner source 고정 |
| REC125 | `b28b387fecd6cc71fddb98e95f336eba5f8a647f` | 10-22 22:38:15 | cutoff 이전 THERM02 유지 |
| REC126 | `12068893fab749ae1efb513563d0a86cc1cf649f` | 10-22 22:34:51 | cutoff 이전 diagnostic C2 유지 |
| REI221 | `73c5e00cac26b4efc782446975bd6b6762555997` | 10-22 22:34:30 | cutoff 이전 local-flow 유지 |
| REI222 | `b4b5d289aaad9ef167f683f19418b0ff87ed8425` | 10-22 17:53:26 | orchestration successor의 새 HEAD 없음 |

근거는 `donor_source_reads/PRIMARY_READ_RECEIPTS.json`에 response body와
확인한 tree blob을 보존했다. 최신 REC119/REI220 댓글 본문은 이 자식 작업이
중복 조회하지 않았다. 부모가 확인한 PR127 최신 댓글은 6353387255이며,
정확한 HEAD의 root AGENTS.md는 remote404 / local 없음이라는 부모 반환을
기록하고 다시 찾지 않았다. 본 조사의 “변경 없음”은 위 PR HEAD와 코드
소유권 범위다.

REC125의 독립 thermal cohort, REC126의 diagnostic 단위, REC119의
125main+1control=126, REI220의127main+2oracle=129는 다른 실행 집합이다.
warm729와 역사적 REI 첫 실패 raw의 local-only 보존 범위도 바꾸지 않는다.

## 2. 실제 재사용 코드

아래 파일들은 REC PR114
`df95a074730ea0d13d609cf88d448f01f4a47ef1`에 고정했다.
기존 intake의 raw UTF-8 파일을 사용할 때도 Git blob SHA1을 다시 계산하고
현재 정확한 tree와 대조했다.

| 실제 파일 | 위치 / 역할 | Git blob SHA1 |
|---|---|---|
| `src/full_bianchi_hyrec/trajectory/hyrec_source_adapter.py` | 267–349: IsotropicEinsteinLineSource | `00b9eceec888839a0d1cd7644e569a397d4f7279` |
| 같은 파일 | 123–166: one-photon paired action / LTE helper; 41–264: 별도 virtual distortion adapters | 같은 blob |
| `tests/trajectory/test_hyrec_source_adapter.py` | 134–176: 기존 LTE null, angular normalized-weight convention | `1bbbb59a70f7880d26e1e908b6cc81ecec307647` |
| `src/full_bianchi_hyrec/trajectory/full_2012_atomic_source.py` | 227–358: 실제 native atomic matrix / Schur / outgoing history | `ffeda51ddbde4d631088fd4787822e3a94e49785` |
| `src/full_bianchi_hyrec/trajectory/primitive_trajectory.py` | 313–335: departure에서 physical population 복원 | `bb59e80d2a655113f99c3d59109d612f0b113b01` |
| `src/full_bianchi_hyrec/recoil/original_hyrec_native.py` | 63–66: energy / units; 216–295: diffusion rates | `069a1671e18229f27882549a0cd38071e6d9a661` |
| `src/full_bianchi_hyrec/recoil/original_hyrec_physical_flux.py` | 269–315: saved-state schema; 402–532: CSV parser; 946–956: equal-opposite event energy algebra | `f183c005058dd618b97694061ca7e376814b16c0` |
| `src/full_bianchi_hyrec/trajectory/hmla_flrw.py` | 33–37 native constants, 68–75 H/nH provider | `9ba49ea9136fb306d99dba9fa5622422a41f6553` |
| `src/full_bianchi_hyrec/trajectory/hyrec_spike_transfer.py` | signed virtual-spike transfer; physical resolved-line source와 구분 | `ade2cc6d3da852f444289d7c6f2e9132c8ca7c90` |

기존 resolved-line adapter는 ordinary frequency \(\nu\)와
population per hydrogen nucleus \(x_u,x_l\)를 받아

\[
\left.\dot f_\nu\right|_{\rm line}
=\frac{c^3 n_{\rm H}}{8\pi\nu^2}
 A_{ul}\phi_\nu
 \left[x_u(1+f_\nu)-\frac{g_u}{g_l}x_l f_\nu\right]
\]

를 구현한다. \(\phi_\nu\)의 단위는 Hz\(^{-1}\)이며 \(A\)는 s\(^{-1}\)이다.
현 코드에 \(\phi_\nu\)의 전 주파수 정규화 적분을 자동 검증하는 기능은 없다.
LINE01이 finite profile 혹은 narrow-line approximation을 선택하면 그
정규화와 photon-number measure를 새 계약에 명시해야 한다.

\[
h=2\pi\hbar,\qquad E_\gamma=2\pi\hbar\nu,\qquad
dN_\gamma=\frac{8\pi\nu^2}{c^3}f_\nu\,d\nu
\]

를 사용하면 source의 number integral과 atomic population exchange가 같은
사건을 센다. bound–bound 사건의 반대 에너지는 atomic internal energy에
기록한다. 별도 collisional/recoil/thermal 분해 없이 이를 gas heat라고
부르면 안 된다. 기존 equal-opposite energy 함수는 장부의 대수적 패턴으로
재사용할 수 있지만 과정의 물리적 분류까지 자동으로 보장하지 않는다.

## 3. native FULL이 이미 소유하는 항

원본 C의 정확한 repo 경로:

`research/rec_r3s_ncp_campaign_20261021/ncp_execution_001/evidence/campaign_001/jobs/h4_legacy16/run/worker/source_extract/HyRec/hydrogen.c`

Git blob은 `2df4561f1b1ef80991ca3b7645666a630eea19b7`이다.
동일 directory의 `hydrogen.h` blob은
`80d612d2c032059f419b701f1376d43513cff2ed`이다.
원본 raw를 별도로 보존했다.

| 소유항 | 원본 C 위치 | Python source-equivalent 위치 |
|---|---|---|
| Sobolev Lyα real diagonal | hydrogen.c441,462 | full_2012_atomic_source.py268,281 |
| blue Lyα feedback source | hydrogen.c464 | 같은 파일291 |
| two-photon/Raman true coupling | hydrogen.c467–477 | 같은 파일258–285 |
| virtual Aup/Adn diffusion | hydrogen.c482–505 | 같은 파일264–286,295–306 |
| 2p↔139/140 line-center coupling | hydrogen.c492–517 | 같은 파일307–311 |
| escape-compressed diagonal/source | hydrogen.c521–526 | 같은 파일295–312 |
| scalar redshift/history closure | hydrogen.c667–718 | canonical causal history adapter가 별도 소유 |
| Lyα outgoing departure | hydrogen.c794 | 같은 Python343 |

구체적으로

\[
R_{\rm Ly\alpha}
=\frac{4.662899067555897\times10^{15}\,H}
 {n_{\rm H}[{\rm cm^{-3}}]\,x_{1s}}
=\frac{8\pi H}{3n_{\rm H}x_{1s}\lambda_\alpha^3}
\]

가 이미 2p diagonal에 있고, \(3R_{\rm Ly\alpha}x_{1s}
 Df^+_{\rm Ly\alpha}\)가 source에 있다.
원본 departure convention에서 이 둘의 net action은

\[
R_{\rm Ly\alpha}
 [\,x_{r,2p}-3x_{1s}Df^+_{\rm Ly\alpha}\,]
\]

이다. 이를 새로운 bare Einstein 또는 escaped-line source와 합산하지 않는다.

압축된 virtual diagonal은
\[
(T_{vv})_{bb}=\frac{\Gamma_b}{1-P(\Delta\tau_b)},
\qquad \Delta\tau_b\propto\Gamma_b
\]
이며 \(\Gamma_b\)에는 true coupling과 diffusion이 함께 들어간다.
완성된 \(T_{vv}\)를 두 개의 additive physical operator로 나누어 패치할 수
없다는 기존 firewall을 현재 실제 C521–526행에서도 확인했다.

`SUBSTITUTION_FIREWALL.md` blob
`d935d4f90c4c95b88fa03bcb29544fd1cad25d80`의 joint-retirement 목록을
그대로 유지한다. 향후 production 연결에는 Sobolev, blue feedback,
diffusion, 두 line-neighbor coupling, compressed diagonal/source,
scalar redshift/history를 함께 residual/JVP/보존 장부의 새 owner로 넘겨야 한다.
이번 작은 독립 선 source 구현만으로 이 전환이 완료되지는 않는다.

## 4. 실제 저장된 primordial snapshot 1개

다음은 새 solver 없이 읽은 원본 CSV 값이다. 입력 decimal string을
`donor_source_reads/STORED_NATIVE_LYA_STATE.json`에 따로 보존했다.

원본:

`archive/expanded/Full_Bianchi_HyRec_PR04B2A_physical_native_edge_flux_v0_53/ORIGINAL_HYREC_TRAJECTORY_SNAPSHOT.csv`

Git blob `6399b59ca3c97d6c5b1162f83f50a6677fad06ff`,141089bytes.

| 필드 | 원본 값 |
|---|---:|
| target z | 1100 |
| 실제 saved z | 1099.9986525171403 |
| \(x_{1s}\) | 0.85507000330964777 |
| \(x_e=x_{\rm HII}\) | 0.1449299966903522 |
| \(n_{\rm H}\,[{\rm cm^{-3}}]\) | 250.18675437302318 |
| \(H\,[{\rm s^{-1}}]\) | 4.9696512229238343e-14 |
| \(T_R\,[{\rm eV}]\), rescaled | 0.25882399309326415 |
| \(T_M\,[{\rm eV}]\), rescaled | 0.25882127610727856 |
| \(x_{r,2s}\), signed departure | 6.5565949922896059e-15 |
| \(x_{r,2p}\), signed departure | 1.9711283950160407e-14 |
| \(Df^+_{\rm Ly\alpha}\) | 7.6643364422337378e-15 |
| \(Df^-_{\rm Ly\alpha}\) | 7.6840819558108666e-15 |
| \(A^{\uparrow}_{2p}\), diffusion | 3744.6148446595753 s\(^{-1}\) |
| \(A^{\downarrow}_{2p}\), diffusion | 3764.3312792072393 s\(^{-1}\) |

원본 C765–767행은 \(\mathbf x_r\)가
“\(x_i-x_i[{\rm eq\ with\ }1s]\)”라고 명시한다.
기존 Python이 이미 다음을 구현한다.

\[
x_{2s}=x_{r,2s}+x_{1s}e^{-E_{21}/T_R},\qquad
x_{2p}=x_{r,2p}+3x_{1s}e^{-E_{21}/T_R}.
\]

따라서 \(\mathbf x_r\)를 양의 실제 population으로 직접 넣지 않는다.
\(x_{1s}=1-x_{\rm HII}\) 역시 원본 effective-atom convention을 보존한 값이다.
snapshot population을 읽어 detached source를 평가하는 것과 새 fully coupled
population 해를 구하는 것은 다른 주장이다.

원본 \(Df\)는 total occupation이 아닌 distortion이다.
절대 Bose occupation으로 넣을 때는 선택한 thermal baseline을 명시한다.
원본 population equilibrium 복원에는 Wien factor
\(e^{-E_{21}/T_R}\)가 사용된다. full Planck baseline
\(1/[\exp(E_{21}/T_R)-1]\)와 exact stimulated term을 넣은 새 모델을
원본 압축식과 비교할 때는 이 convention 차이를 표시해야 한다.

실제 native angular distribution은 이 scalar snapshot에 없다.
snapshot의 scalar thermodynamics/population을 쓰더라도 방향 패턴이나
Bianchi shear를 별도로 공급하면 “native state + supplied angular fixture”다.
저장된 원본 Bianchi trajectory라고 표현할 수 없다.

### 세 시각 NPZ의 실제 내용

`pr05a_primitive_trajectory_v058.npz`도 원본133779bytes를 확보했다.
Git blob `33fac9c57732c8b7565fec64b6bbd0b8741f2386`,
SHA256 `c4ff9897080ecefdfef1b47f557b10586cd4846a293e09e0e0ab3e540cefa9c6`.

z1300/1100/900 표본은 있지만 저장 항목은 residual313,
implicit native departure311, COM occupation35×302, z와 metrics다.
필요한 real \(\mathbf x_r\), \(x_{1s}\), \(n_{\rm H}\), \(H\), \(T_R\)가
이 NPZ에 없으므로 세 시각을 완전한 line input으로 만들었다고 주장하지 않는다.
추가 원본 state를 확보하기 전에는 위의 완전한 z≈1100 한 표본만 사용한다.

UTF-8 전용 일반 fetch가 binary NPZ를 거절한 실패를 보존했다.
이후 encoding=base64를 공식 지원하는 file-fetch로 원본을 읽어 byte 검증했다.
이것은 과거 과학계산 실패를 재실행한 사건이 아니다.

## 5. 상수와 단위: native convention을 보존할 부분

| 항목 | 정확한 source 위치 / 값 | LINE01 처리 |
|---|---|---|
| \(E_{21}\) | hydrogen.h29:10.198714553953742eV | collapsed native Lyα card에 고정 |
| native \(hc\) | hydrogen.h35:1.239841874331e-4eVcm | native wavelength/escape parity에서 별도로 보존 |
| native \(k_B\) | hydrogen.h37:8.617343e-5eV/K | legacy K↔eV convention |
| \(\nu\) 변환 | original_hyrec_native.py66:\(h/e\); physical_flux.py387–390 | modern SI \(E=2\pi\hbar\nu\) 변환이라는 표기 |
| \(T_K\) 변환 | primitive_trajectory.py323–324: \(T_{\rm eV}fsR^2meR\,e/k_B\) | CODATA 변환과 native \(k_B\)를 혼동하지 않음 |
| \(n_{\rm H}\) 변환 | cm\(^{-3}\)→m\(^{-3}\): \(\times10^6\) | density unit 표시 |
| collapsed degeneracy | native equilibrium [1,3] | \(g_{2p}/g_{1s}=3\); fine rows와 별도 |
| \(A_{21}\) | 읽은 native Sobolev C/h에 standalone scalar 정의 없음 | 별도의 primary coefficient sourcecard 필요 |

**\(A^{\uparrow,\downarrow}_{2p}\)를 \(A_{2p\to1s}\)로 사용하면 안 된다.**
전자는 line-center와 virtual bins 사이의 diffusion couplings다.
native Sobolev \(R_{\rm Ly\alpha}\)에서는 bare \(A_{21}\)가 소거되어 있다.
기존 adapter test의6.265e8s\(^{-1}\)도 테스트의 supplied coefficient이지
이 snapshot에서 추출한 original-native A값이 아니다.

서로 다른 NIST fine-structure 행을 native collapsed \(g=3\) source와
섞지 않는다. 새로운 \(A_{21}\) source를 채택하면 그 provenance,
level grouping, energy/frequency convention을 명시하고 sourcecard를 분리한다.
\(c,\hbar,k_B\)는 유도와 공용 단위 계약에서 생략하지 않는다.

## 6. 현재 단위의 완성도와 남은 입력

| 항목 | 상태 |
|---|---|
| cutoff 이후 관련 PR delta + 현재 donor pin | 완료, 접근 범위 명시 |
| 실제 native 소유권과 double-counting 경계 | 완료 |
| 기존 Einstein source / unit / population 재사용 위치 | 완료 |
| 실제 저장 source snapshot 1개 | 확보·byte 검증 완료 |
| 완전한 실제 source snapshot 3개 | 미확보: NPZ에는 필요한 필드 일부 없음 |
| bare \(A_{21}\) primary sourcecard | 별도 문헌/atomic database 조사 담당에게 전달 |
| 실제 native directional occupation | scalar source에 없음; supplied fixture 계약 필요 |
| native FULL production 소유권 교체 | 미실행 |
| new cosmological ODE / completed campaign 반복 | 0 |
| 열역학적·핵반응망 전체 폐쇄 | 이 단위의 달성 주장이 아님 |

다음 coding handoff는 exact donor Einstein action을 가져오고,
읽기 전용 상태 입력 / 소유자 배타성 / signed net number /
atomic-internal-vs-thermal energy 구분 / escaped angular moments를
명시한 작은 모듈을 구현하는 것이다.
완료된 REC126/REI129/warm729/ANGULAR01 수치 campaign을 재실행할 이유는 없다.

## 보존과 출처

총13회의 source call 중12회가 성공했으며, 실패1회는 binary UTF-8제약이다.
각 파일의 byte hash와 URL은 `*.provenance.json`,
정확한 call 목록은 `LIVE_SOURCE_CALLS.json`,
합성 결과는 `../OWNER_DELTA.json`에 있다.

REC adapter 코드는 root MIT license를 raw 그대로 함께 보존했다.
원본 HyRec C/h의 Yacine Ali-Haimoud / Chris Hirata attribution도 보존했다.
검사한 original extract tree에서 별도 upstream license 파일을 발견하지
못했으므로 프로젝트 MIT를 원본 HyRec 전체의 허가로 확장 표기하지 않는다.

