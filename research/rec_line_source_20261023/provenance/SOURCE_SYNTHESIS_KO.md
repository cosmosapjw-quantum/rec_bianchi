# LINE01 R2/R3 — Lyα source와 population 규약 고정

작성: 2026-10-23 KST. 이 파일은 LINE01의 원전·상수·공식 지도다. 새 과학 계산은 수행하지 않았다. 전체 source lock은 `LINE_SOURCES.json`이며, 검색·열람 응답은 `source_raw/`에 보존했다.

## 이번 단위의 선택

**단일 \(2p_{1/2}\to1s_{1/2}\) 성분을 기본 source로 권한다.** \(n_l,n_u\)는 각 \(J\) 준위의 자기부준위를 모두 합한 물질 정지계의 물리적 수밀도다. \(g_l=g_u=2\), 따라서 \(g=1\)이다. 무편극 scalar population과 방향에 무관한 청색 경계 occupation \(f_+\)를 명시한다. 이 선택은 NIST 행과 population 변수를 직접 대응시키며, 실제 우주론적 Lyα 이중선 전체의 독립·고립성을 보증하지 않는다.

[NIST H I persistent-line table](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable3.htm)의 입력은 다음과 같다.

| 성분 | 진공 파장 Å | \(A_{ul}\), s\(^{-1}\) | \(g_u/g_l\) |
|---|---:|---:|---:|
| \(2p_{1/2}\to1s_{1/2}\) | 1215.67364 | \(6.2649\times10^8\) | 1 |
| \(2p_{3/2}\to1s_{1/2}\) | 1215.66824 | \(6.2648\times10^8\) | 2 |

표에 명시된 수치 불확도는 없다. 위 유한 자릿수를 코드 입력값으로 고정할 수 있지만, 이것을 물리적 정확도 \(10^{-8}\)의 자료로 해석하면 안 된다. [NIST 참고문헌](https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable7.htm)은 파장의 MK00a와 전이율의 BM00를 2000년 미발표 계산으로 연결한다. 해당 계산 원파일은 열람하지 않았다. 이번 조회는 현재 접근 가능한 NIST Handbook의 확인이며, 최신 ASD 데이터베이스 버전 전체를 조회했다는 주장은 하지 않는다.

## collapsed 2p와 전체 n=2 shell의 차이

\(n_{2p}=n_{2p_{1/2}}+n_{2p_{3/2}}\)로 묶으면 \(g_u=6,\ g_l=2,\ g=3\)이다. 공통 \(A,\nu\) 또는 통계적 population 비율을 도입할 때는 각각 추가 근사를 선언해야 한다. NIST의 intensity 열은 population 비율을 결정하지 않는다. 두 성분의 파장 차 \(0.00540\) Å는 표의 차이로 계산한 값이며, 모델의 불확도가 아니다.

[NIST shell-average 표](https://physics.nist.gov/Pubs/AtSpec/node18.html)의 \(g_u=8,\ A=4.699\times10^8\ {\rm s}^{-1}\)는 \(g=2n^2\)로 세는 **2s를 포함한 전체 n=2 shell** 규약이다. 이를 collapsed 2p의 \(g=3\)이나 선택한 fine-component population과 섞으면 안 된다. 통계적 shell 점유를 가정하면 \(n_{2p}=(3/4)n_2\)가 되어 평균 전이율의 차이를 설명할 수 있다. 이 관계는 점유 규약에 대한 유도이며 실제 2s–2p 혼합률이 아니다.

## 원전에서 직접 가져오는 공식

[Hirata–Forbes, arXiv:0903.4925v2](https://arxiv.org/pdf/0903.4925), §II.B 식 (1)–(3)을 이 단위의 stimulated-emission 공식 근거로 사용한다. 논문의 \(x_i=n_i/n_H\)를 물리적 밀도로 바꾸면

\[
\Delta=g n_l-n_u,\qquad
\tau_{\rm S}=\frac{A_{ul}\lambda^3\Delta}{8\pi H},\qquad
\beta(\tau)=\frac{1-e^{-\tau}}{\tau},
\]

\[
D=n_u(1+f_+)-g n_l f_+=n_u-\Delta f_+,\qquad
\mathcal R=A_{ul}\beta D.
\]

\(\mathcal R>0\)는 순하향 전이와 순선광자 생성을 뜻한다. \(f_+\)는 선의 **청색 경계**에서 들어오는 photon occupation이다. 일반적으로 피드백 성분을 가질 수 있으므로 CMB Planck 함수로 자동 대입하지 않는다. \(\Delta>0\)에서는 \(f_{\rm source}=n_u/\Delta\)이며 \(D=\Delta(f_{\rm source}-f_+)\)다.

[Chluba–Sunyaev, arXiv:0810.1045](https://arxiv.org/pdf/0810.1045)는 \(f_\nu=c^2 I_\nu/(2h\nu^3)\) 규약, 식 (35b)의 Sobolev 확률 및 real emission/absorption과 산란의 구분을 확인하는 보조 원전이다. 이 논문의 일부 source 식은 \(f\ll1\) 근사로 유도되므로 finite-\(f\)의 자극방출 보존식은 앞의 Hirata–Forbes 식을 사용한다.

## LINE01이 직접 유도할 연결

다음은 원전의 인용식이 아니라, 위 source와 완료된 ANGULAR01을 연결하는 유도식이다. \(c,\hbar,k_B\)를 그대로 유지한다.

\[
C_S=\frac{A_{ul}\lambda^3\Delta}{8\pi},\quad
q(\boldsymbol n)=1+\frac{\sigma_{ab}}H n_a n_b,\quad
t=\frac{C_S}{H},\quad \tau(\boldsymbol n)=\frac{t}{q(\boldsymbol n)}.
\]

\(H>0,\Delta>0,q>0\)와 기존 geodesic redshift의 shear 부호 규약이 필요하다. 등방 \(D\)이면 기존 \(B=\langle\beta\rangle\), \(Q_{ab}=\langle(n_an_b-\delta_{ab}/3)\beta\rangle\)를 그대로 사용하여

\[
\mathcal R=A_{ul}DB,\qquad
\epsilon=\frac{2\pi\hbar c}{\lambda},\qquad
\mathcal S_{\pi,ab}=\epsilon A_{ul}D Q_{ab}
\]

를 얻는다. \(\mathcal S_{\pi,ab}\)의 차원은 \({\rm J\,m^{-3}\,s^{-1}}\)이며 선 escape로 정의한 유효 복사 비등방 응력의 **주입률**이다. 전체 미시적 line collision tensor를 유도한 식은 아니다. 저장된 복사 응력이나 물질 응력과 같다고 놓지 않는다. 방향 의존 \(f_+(\boldsymbol n)\)에서는 \(D\)를 각도 평균 밖으로 뺄 수 없다.

원자·광자의 국소 source 장부는

\[
(\dot n_u,\dot n_l,\dot n_\gamma)_{\rm line}=(-\mathcal R,+\mathcal R,+\mathcal R),
\]
\[
(\dot u_{\rm atom},\dot u_\gamma,\dot u_{\rm thermal})_{\rm line}
=(-\epsilon\mathcal R,+\epsilon\mathcal R,0).
\]

마지막 0은 recoil 없는 bound–bound 전이의 가정이다. 광자 생성 에너지를 기체 가열로 이중 계상하지 않는다. 팽창에 따른 희석·적색편이 및 경계 수송은 해당 방정식의 별도 항이다. 동일한 \(\epsilon\)을 사용하는
\(n_u=g n_l e^{-\epsilon/(k_BT)}\),
\(f_+=[e^{\epsilon/(k_BT)}-1]^{-1}\)이면 \(D=0\)이다. 이 국소 상쇄는 전역 열역학 폐쇄의 증명이 아니다.

## 적용 한계와 인계

Sobolev의 준정상성, 선언된 redistribution/profile 처리와 고립선 근사가 적용 범위다. 실제 doublet의 겹침, 다준위 피드백, 원자 편극, recoil, time-dependent transfer, ionic yield는 이 source lock으로 완료되지 않는다. 분리된 두 성분의 escape rate를 더하는 것만으로 겹친 이중선의 전이 계산을 완성했다고 할 수 없다.

Exa는 NIST 원자 표와 shell 규약의 발견·재열람에, SciSpace는 Sobolev/자극방출 원전 탐색에 사용했다. SciSpace 중복 및 연도 불일치는 1차 원문의 식별자로 교정했다. 검색 결과 자체를 공식의 권위로 쓰지 않는다. 저장된 raw는 도구가 반환한 텍스트 표현이며 원격 PDF/HTML의 전체-byte 백업이 아니다.

부모 루프가 다음으로 고정할 것은 입력 소유권, 유한 case 및 잔차 기준, resource cap이다. 이 작업에서는 과학 실행을 시작하지 않았다. Physical HOLD, REC U5 HOLD, CLOSED_HOLD_NOT_RESET, global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false와 REI 첫 실패 raw의 local-only 범위를 유지한다.

