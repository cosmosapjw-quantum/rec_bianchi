# REC에서 공동 원자·복사 수송 프로젝트로 전달할 수 있는 것

## 원래 알고리즘을 보존하는 계산 단순화

원본 HyRec2012의 시간 재귀는

\[
Y_{n+1}=Y_n+h(5F_n/4-F_{n-2}/4),\qquad h=\Delta\ln a.
\]

H와 열 변수의 현재 상태뿐 아니라 두 개의 이전 RHS를 각각 저장해야 한다. 단계 전환은 RHS를 평가하는 입력 상태가 소유한다. FULL→EMLA→Peebles 전환에서 이전 RHS를 새 단계 연산자로 재계산하면 원래 재귀와 달라진다. FULL에는 수용된 causal photon history도 필요하다. 현재 공개 low-z runner는 이 증강 상태를 복구하므로 네 메모리와 stage flag를 보존한 재시작은 같은 recurrence를 계속한다.

이미 완료한 prefix의 서로 다른 열에만 병렬 map을 적용할 수 있다. 시간 단계는 전 단계의 상태·RHS·광자 이력에 의존하므로 독립 task로 나눌 수 없다. R3P의 immutable geometry cache는 실제 energy bytes/shape로 식별하고, per-step causal/current-future guard와 forensic callback 뒤 invalidate를 유지한다. 현재 정확 결과를 재사용하는 이 구조가 NCP 병렬도의 우선 기준이다.

원 R3M exclusive CPU의 audit 비율 f=21.409138/37.588099=0.569572...라면 다른 비용이 고정된 조건에서 audit만 s배 빨라졌을 때 전체 CPU비는

\[
S(s)=[1-f+f/s]^{-1},\qquad S(\infty)=2.323270264\ldots.
\]

실제 R3P Rust1 audit paired CPU 중앙비2.232513를 대입한 약1.4587은 조건부 비용 모형이다. 전체 native production의 관측 가속률은 아직 없다. 독립 ratio API의 약110배 scalar-loop 대비 비를 전체 물리 계산에 곱하지 않는다.

## 재결합 출력의 과학적 범위와 공통 단위

현재 검증된 실제 이력은 원본 HyRec2012의 FLRW, q=0 원자·열 연산자를 따른다. 기존 h U5 HOLD_9_FAIL 및 h2 HOLD_8_FAIL, 세 격자 전역 수렴 미완료를 함께 전달한다. h2 U6 완료와 원본 C 같은-h 일치는 해당 이산식에 대한 검증이며 연속해 오차는 별도 h/h2/h4 비교가 정한다.

REC public interface의 국소 입력은 T_m[K], T_r[K], n_H[m^-3], x_e=n_e/n_H이다. 원본 atomic C에는 n_H[cm^-3]=10^-6 n_H[m^-3], 온도에 k_B[eV/K]를 곱해 eV로 넘긴다. cross-repo packet은 단위 tag와 필요 종 분율을 명시한다. `rei_bianchi`의 baryon-normalized isotope state Y_{i,q}=n_{i,q}/n_b와 결합할 때

\[
Y_e=\sum_{i,q}qY_{i,q},\quad Y_H=n_H/n_b,\quad
x_e=Y_e/Y_H,\quad n_e=n_bY_e=n_Hx_e.
\]

여기서 n_H가 ^1H 핵만인지 D/T를 포함한 hydrogen nuclei인지 source 정의를 일치시켜야 한다. 원래 H+He 모델에서 f_He=n_He/n_H라면(다른 핵종을 생략한 그 모형에서만) Y_H=1/(1+4f_He)이다. ^1H/D/T/He3/He4/Li7 및 Be7/excluded reservoir를 가진 dossier에는 일반 합 \(\sum_i A_iY_i=1\)을 적용한다. retained17을 다시 정규화하거나 small8 prior covariance를 기존59 donor의 공분산으로 대체하지 않는다.

BASS의 비등방 geometry와 REI의 retarded illumination은 원래 REC scalar input에 자동 포함되지 않는다. 원자율 k(T_m) 사전표는 background-independent microscopic kernel로 전달할 수 있지만, photo-rate와 radiation-mediated terms는 실제 주파수·방향·이력의 functional이다. 따라서 상대 프로젝트의 제조된 gas IC나 경계 packet과 REC 원시 이력을 합칠 때 입력 surface와 normalization을 먼저 맞춘다.

이 단위는 위 exact recurrence·단위 사상과 기존 결과를 통합한 derived/reused 결과다. 새 NCP 적분이나 새로운 가열·광학깊이·CMB 예측은 실행하지 않았다. 다음 계층은 독립 h2/h4 결과와 source-compatible coupling이다.
