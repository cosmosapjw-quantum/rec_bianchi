# Bianchi 재결합 다음 단위: 원전·코드 재사용과 각도 escape 축약

작성: 2026-10-22 UTC. 담당: /root/recombination_sources. 적용 스킬: physmath-research-loop 1.3.0, 선택 범위 R2–R5.
관련 기계 판독 기록: SOURCES.json, WOLFRAM_RECEIPTS.json. 전체 프로젝트 판정·구현·게시·백업은 parent가 통합한다.

## 1. 연구 위치와 실제 추가 성과

이번에 제안하는 단위는 **공급된 등방 line emissivity에 작용하는 국소 Sobolev escape 연산자의 유한 광학깊이 각도 평균과 PSTF 모멘트**다. 기존 PR114에는 이미 방향별 광학깊이, 정확한 spike jump, JVP, zero/sign-change 사건 처리가 있다. 따라서 \(H_{\boldsymbol n}\) 또는 방향별 \(\tau_{\boldsymbol n}\) 자체를 새 결과로 보고하지 않는다.

새로 구성한 것은 다음 네 가지를 함께 묶은 계산 계약이다.

1. 고정 \(H,C_S>0\), 모든 방향의 양의 팽창률 아래에서 각도 평균 escape가 등방 escape보다 크지 않다는 Jensen 부등식.
2. 충분히 큰 **최소 방향 광학깊이**가 보장하는 scalar mean과 tensor moment의 명시적 절대오차.
3. 선도 scalar mean이 \(\sigma_{ab}\)에 무관해도 escaping quadrupole은 남는다는 식.
4. 그 오차식으로만 두꺼운 선의 계산 생략을 허용하고, 나머지 영역은 원래 방향별 연산자를 사용하도록 하는 분기.

이는 단순화된 국소 연산자에 대한 수학적 결과다. 원시 재결합의 재분배·기억·feedback까지 닫힌 결과, 생산 승인, 모든 핵종 핵반응망, 또는 비등방 효과 전체의 소멸 정리가 아니다. 원전/기존 branch 중복 탐색에서 같은 묶음을 확인하지 못했다는 사실은 학술적 최초성 증명이 아니다.

### 역사적 lane의 분리

| 항목 | 유지할 해석 |
|---|---|
| REC119 / REC126 | 125 main + 1 control; 사용자 지정 복구 결과를 재사용 |
| REI220 / REI129 | 127 main + 2 oracle; 62→33 축약; REC 수와 합치지 않음 |
| REI의 첫 실패 raw | 당시 local-only라는 보존 범위를 유지 |
| THERM02 | \(z=20\to2\), 5–60 eV, 조건부 21-population atomic/thermal test-fluid 결과 |
| 이번 국소 escape 단위 | 원시 재결합 문헌과 기존 primordial donor에 연결하는 연산자 연구; THERM02의 연장 적분이 아님 |
| 실행 | 이 조사자는 ODE, RHS 평가, 기존 suite, benchmark를 실행하지 않음 |

Physical HOLD, REC U5 HOLD, CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false를 유지한다.

## 2. 원전에서 실제로 재사용할 것

### HyRec-2 / HyRec: rate elimination과 복사전달을 분리

[Lee & Ali-Haïmoud 2020, arXiv:2007.14114v2](https://arxiv.org/abs/2007.14114), II.C 식 (3)–(8)은 유효 excited-state 계수와 ground-state net decay rate를 분리한다. III.A 식 (10)은 단순화된
\[
R_{\mathrm{Ly}\alpha}=\frac{8\pi H}{3n_Hx_{1s}\lambda_\alpha^3}
\]
를, III.B 식 (11)은 \(R_{2p,1s}=R_{\mathrm{Ly}\alpha}/[1+\Delta]\)를 쓴다. \(\Delta\)는 FULL 계산의 이력에 맞춘 보정이며 Bianchi에 대한 보정표가 아니다. 재사용 대상은 기존 effective-state algebra와 이미 검증된 원자계수 연결이다. 비등방 복사장으로의 적용은 해당 radiation-rate 가정을 다시 맞춰야 한다.

[공식 HYREC-2](https://github.com/nanoomlee/HYREC-2)의 실제 master는 조회 시점에
`09e8243d0e08edd3603a94dfbc445ae06cafe139` (2023-09-14)이었다. 조사한 `hydrogen.c`, `hydrogen.h`는 cgs+eV, \(H\)는 s\(^{-1}\), \(n_H\)는 cm\(^{-3}\), 반환값은 \(dx_{\rm HII}/d\ln a\)라는 계약을 명시한다.

| 경계 | 공식 코드 위치 | 이번 단위의 활용 |
|---|---|---|
| 유효 원자계수 | `interpolate_rates`, hydrogen.c 333–424 | 기존 source binding 재사용; 새로운 계수표를 만들지 않음 |
| 기본 EMLA | `rec_HMLA_dxHIIdlna`, 490–543 | \(R_{\rm Ly\alpha}\)의 물리적 위치 확인 |
| SWIFT | `rec_swift_hyrec_dxHIIdlna`, 429–486 | 등방 보정표의 적용 경계 확인 |
| FULL operator | `populateTS_2photon`, 630–736 부근 | line rate, incoming distortion, diffusion, virtual bin의 결합 확인 |
| 시간 변수 | 같은 함수들의 최종 \(1/H\) | line escape의 \(H\)와 \(d/d\ln a\) 변환의 \(H\)를 구분 |

**함수에 들어가는 \(H\) 전체를 \(H_{\boldsymbol n}\)으로 치환하지 않는다.** 선의 redshift operator와 시간 변수 변환, 원자계수, diffusion/feedback은 서로 다른 자리다. 이번 작업은 새 upstream 코드를 복제하지 않았고, source tree에 독립 LICENSE 파일이 없다는 관측을 provenance에 남겼다. 기존 프로젝트 donor의 사용·라이선스는 별도 확보된 기록을 사용한다.

### Sobolev 식과 한계

[Chluba & Sunyaev 2009, arXiv:0810.1045v2](https://arxiv.org/abs/0810.1045), §3.2, 식 (35b)가
\[
\beta(\tau)=\frac{1-e^{-\tau}}{\tau}
\]
를 제공한다. 준정상성과 완전 주파수 재분배가 도출에 들어간다. [Hirata & Forbes 2009, arXiv:0903.4925v2](https://arxiv.org/abs/0903.4925), 도입부 p.2는 같은 방출/흡수 profile, complete redistribution, 고립된 선, 준정상성이라는 가정을 명시하고 실제 재결합에서의 한계를 다룬다. 이번 \(\exp(-\tau_{\min})\) 오차는 **정확한 Sobolev 식을 thick 식으로 바꾸는 오차**이며, 이 원전들이 다루는 Sobolev 자체의 물리 오차까지 제한하지 않는다.

### CosmoRec / RECFAST

[CosmoRec 공식 저자 페이지](https://www.jb.man.ac.uk/~jchluba/Science/CosmoRec/CosmoRec.html)는 v2.0.3 beta와 효과 목록을 제공한다. effective multilevel 구조와 고차 two-photon, Raman, Ly-\(\alpha\) diffusion, time dependence, He continuum/feedback을 기존 code/source inventory에 대응시키는 데 유용하다. 페이지의 FLRW 정확도 주장을 Bianchi 정확도로 옮기지 않는다.

[RECFAST 공식 페이지](https://www.astro.ubc.ca/people/scott/recfast.html)와 [Fortran 원문](https://www.astro.ubc.ca/people/scott/recfast.for)은 1.5.2, 2012-09를 확인한다. H/He와 matter temperature, SI convention, He fraction 정규화 및 near-standard-cosmology 보정이 명시돼 있다. 이번에는 이미 존재하는 비교 lane을 재사용한다. 역사적 C판은 해당 페이지가 구판으로 표시하므로 새 재사용 기준으로 고르지 않았다.

## 3. 최신 문헌을 확인한 결과

검색 기준일은 2026-10-22, 최근 범위는 2025-10-22부터다. Exa를 실제 5회 사용해 요청 수 6+6+6+4+4=26건을 검토했고, SciSpace를 실제 1회 사용해 10행을 받았다. 이 수는 unique primary-paper 수가 아니다. SciSpace가 일부 오래된 arXiv 항목에 표시한 2022년은 원문 버전 날짜로 교정했다.

가장 최근의 직접 관련 line-transfer 원전으로 확인한 [Li & Zheng 2026, MNRAS 550, stag1223](https://doi.org/10.1093/mnras/stag1223)은 2026-06-26 출판, 2026-07-13 typeset correction이다. 유한 slab/cylinder/sphere, recoil, velocity-gradient 문제를 다루며, §2의 주된 수치 설정은 정적 cloud와 \(T=10\) K다. 준정상 유한 경계 escape의 유용한 비교 자료이지만, 원시 우주 재결합에 그 fitting formula를 직접 넣을 근거는 없다. 따라서 이번 구현 계수로 채택하지 않는다.

2025의 PMF/clumping 원전은 공간 비균질성과 MHD라는 추가 문제여서 현재 균질 Bianchi 국소 단위에 포함하지 않았다. 이번 조사만으로 “더 최신 primordial recombination 연구가 없다”는 주장은 하지 않는다.

## 4. 확정한 수학 계약

전체 증명과 코드용 식은 ../THEORY.md에 있다. 여기서 \(\tau_0=C_S/H\), \(S=\sigma/H\), \(q(\boldsymbol n)=1+S_{ab}n^an^b>0\), \(\langle\cdot\rangle=(4\pi)^{-1}\int d\Omega\)다.

\[
b(q)=\frac{q}{\tau_0}\left(1-e^{-\tau_0/q}\right),\qquad
\bar\beta=\langle b(q)\rangle,\qquad
Q_{ab}=\left\langle\left(n_an_b-\frac{\delta_{ab}}3\right)b(q)\right\rangle.
\]

\[
\boxed{\bar\beta\leq\beta(\tau_0)}
\]
이고,
\[
0\leq\frac1{\tau_0}-\bar\beta
\leq\frac{e^{-\tau_0/q_{\max}}}{\tau_0},
\qquad
\boxed{\left\|Q-\frac{2S}{15\tau_0}\right\|_F
\leq\sqrt{\frac23}\frac{e^{-\tau_0/q_{\max}}}{\tau_0}}.
\]

확률의 사중극 \(Q\)를 곧바로 물리적 photon stress \(\Pi_\gamma\)로 식별하지 않는다. 그 변환에는 공급 emissivity의 에너지·주파수·시간·이후 수송이 추가로 필요하다.

작은 shear의 finite-\(\tau\) 결과는
\[
\bar\beta=\beta(\tau_0)
-\frac{\tau_0e^{-\tau_0}}{15}\operatorname{tr}(S^2)
+O(\|S\|^3),
\]
\[
Q=\frac{2}{15\tau_0}
[1-(1+\tau_0)e^{-\tau_0}]S+O(\|S\|^2).
\]

LRS 예제 \(S=\operatorname{diag}(-s/2,-s/2,s)\)는
\(q=1+sP_2(\mu)\), \(-1<s<2\)를 준다. 이는 저장소의 다른 \(\Sigma\) 변수와 자동으로 같은 정규화가 아니다. 기존 donor의 tetrad·shear convention에 명시적으로 매핑해야 한다.

## 5. 적용 경계와 구현에 넘길 기준

| 조건 | 처리 |
|---|---|
| 실대칭 tracefree \(S\), \(q_{\min}=1+\lambda_{\min}(S)>0\), \(C_S>0\) | 현재 식의 정의역 |
| 모든 방향 thick: \(\tau_{\min}=\tau_0/q_{\max}\) | 명시 오차로 scalar/tensor 축약을 허용 |
| finite optical depth | 원래 \(b(q)\) 각도 적분; refined quadrature 차이는 유한 검증으로 기록 |
| \(q_{\min}\le0\), zero/sign crossing | 기존 사건 처리로 반환; 절댓값을 취해 이번 정리로 밀어 넣지 않음 |
| anisotropic emissivity 또는 incoming field | 이번 등방-source theorem을 그대로 적용하지 않음; 필요한 weighted moments를 별도로 구성 |
| redistribution, line overlap, diffusion, recoil, time memory | 해당 원전/기존 FULL operator의 별도 의무 |
| rate/energy ledger 연결 | source-bound row·단위·에너지 회계를 후속 단계에서 명시; 이 local operator만으로 thermal closure 판정 불가 |

ANGULAR01의 함수 결과는 mean, PSTF tensor, \(q_{\min,\max}\), 사용 분기, scalar/tensor 오차 상계, source/donor identity다. 동결한 두꺼운 선 분기는 \(r=e^{-\tau_{\min}}\le\epsilon/(1+\epsilon)\), \(\epsilon=10^{-8}\)이며 로그 조건 \(\tau_{\min}\ge\log(1+1/\epsilon)\)으로 판정한다. 실제 평균 \(B\)에 대한 scalar 상대오차는 \(r/(1-r)\), tensor Frobenius 오차를 \(B\)로 나눈 값은 \(\sqrt{2/3}r/(1-r)\) 이하여서 둘 다 선택한 기준을 만족한다. finite quadrature는 N=64/128, 정규화 차이 기준 \(10^{-8}\)의 유한 비교이며 floating-point interval certificate로 부르지 않는다. 지수 underflow는 양의 상계가 0인 것처럼 표시하지 않고 로그 상계를 보존한다. shear가 0인 근방에서 tensor 상대오차를 정의하려 하지 않는다.

검증할 최소 항목은 등방 한계, trace/rotation covariance, Jensen 부호, 두 thick bounds, small-shear 계수, donor와의 개별 ray 일치, qmin 사건 경계다. ODE 재실행이나 cosmological convergence 시험은 이 수학 단위의 증명에 필요하지 않다.

## 6. 실제 도구 검산과 다음 행동

WolframContext는 `-32603 Internal error`로 실패했으며 성공으로 기록하지 않았다. 이후 서로 독립된 stateless evaluator 두 호출은 실제 성공했다. 확인한 항목은 \(b''(q)\), \(\langle P_2\rangle\), \(\langle P_2^2\rangle\), LRS domain, scalar의 2차 shear 항, 일반 tracefree 대각행렬의 분산과 PSTF moment다. 이는 CAS 식 검산이며 독립 과학 심사나 전역 수렴성 검증은 아니다.

다음 행동은 parent가 선택한 **기존 PR114 donor를 사용하는 finite-\(\tau\) angular-moment kernel**을 구현하고, 사전 고정한 유한 기준으로 실제 그림과 결과를 만드는 것이다. 기존 primordial FULL operator 및 U5 HOLD 의무는 이 단위의 완료와 별도로 남긴다.

