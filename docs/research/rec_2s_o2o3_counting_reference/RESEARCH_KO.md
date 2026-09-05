# 원본 2s 광자 계수와 기준장: O2/O3 연구 검토

기준: PR #65, `e65ae5c211db4e3375e73410a404f0b23da084d4`, tree `e12a4ae4ed17859e4625f80fb0fa86e83a034036`.

이 문서는 원본 재현과 비평형 확장을 구별하는 조건부 유도다. PR #63의 수치 어댑터 및 PR #65의 140행 추적은 완료된 선행 증거로 재사용한다. 생산 코드, 원본 표, 과거 증거, 실제 분배 행렬 B와 측도 mu는 변경하지 않는다. O2/O3의 생산 모델 선택이나 물리 입력 인증을 승인한 문서가 아니다.

## 1. 근거와 범위

직접 읽은 저장소 근거:
- `docs/research/original_hyrec_2s_input_trace/SOURCE_EXCERPTS.txt`: 원본 `hydrogen.c` 270~347, 413~532의 표시용 발췌. 정확한 바이트 권위는 그 문서가 지정한 원본 ZIP이다.
- 같은 디렉터리의 `OWNER_REVIEW_CONTRACT.json`, `README.md`, `bins_2s.csv`.
- `src/full_bianchi_hyrec/trajectory/hyrec_two_photon_raman.py`: 원본 계수 읽기와 `PhysicalTwoPhotonRamanBin`을 분리한 기존 구현.
- PR #64의 `367a36d569f961b20fa14e312581c2965ea289fd`: 더 넓은 물리 입력 계약 초안. PR #65의 부모가 아닌 형제 문서이므로 자동으로 포함되었다고 보지 않는다.

원본 사실은 위 자료에서 읽고, 아래 식은 별도로 유도한다. 문헌은 Hirata, arXiv:0803.0808 및 Ali-Haimoud와 Hirata, arXiv:1011.3758이다. 이번 SciSpace 검색과 공개 초록 대조는 범위 확인용이다. 논문 전문의 식 번호는 PR #65의 기존 출처 연결을 참조하며 이번에 전문을 새로 읽었다고 주장하지 않는다.

수소 원자 정지계, 스칼라 비편광 2s/1s 채널만 다룬다. 준위 축퇴도 비는 이 채널에서 1이다. 원자 반동, 각도별 쌍커널, 편광, Raman, 이동 구간과 우주론 시간 진화는 이 유도의 적용 대상이 아니다. 계량은 (-,+,+,+), 에너지는 J, theta=k_B T_r는 에너지, 일반 주파수는 nu=E/h, h=2*pi*hbar이다. 저장된 eV 좌표와 theta_eV를 함께 쓰는 무차원 지수도 동등하다. 자연단위를 도입하지 않는다.

## 2. 원시계수와 유효계수를 구별한다

b=0..139에서 E_t=E_b, E_c=E21-E_b>0이다. E_t는 쌍 중 고에너지 광자다. 140개 중심점이 Lyman-alpha보다 낮다는 사실과 혼동하지 않는다.

A_b는 PR #65에서 한 번 정규화된 구간 적분계수다. lambda_b=(fsR^8 meR) A_b이며 단위는 s^-1이다. 물리 에너지를 바꾸는 fsR^2 meR와 rate 배율을 섞지 않는다. 아래 계수 비교는 이 값들이 고정된 조건에서 수행한다.

원본 발췌는 v=exp(-E_c/theta)에 대해 다음을 준다.

C_b=lambda_b/(1-v), D_b=C_b*v.

Tvr[0,b]=-C_b, Trv[0,b]=-D_b, 지정된 2s 대각 증가량은 sum_b C_b이다. 전체 행렬에는 다른 채널도 있으므로 이것을 전체 Trr라고 부르지 않는다.

흑체 companion occupation n_c=v/(1-v)이면 C_b=lambda_b(1+n_c), D_b=lambda_b n_c다. C_b를 원시 lambda_b로 재사용해 Bose 인자를 다시 곱하면 중복 계산이다.

## 3. 구별해야 할 두 rate 법칙

x_u=x_2s, x_g=x_1s는 수소 원자당 population, f_t와 f_c는 무차원 점유수다. 양의 방향은 2s에서 1s로 가는 순사건이며 역반응이면 음수다.

전체 점유수 인자를 유지한 기존 스칼라 쌍식:

Gamma_F=lambda_b[x_u(1+f_c)(1+f_t)-x_g f_c f_t].

흑체 companion을 고정하고 고에너지 유도방출을 생략한 원본 계수식:

Gamma_N=C_b x_u-D_b x_g f_t.

두 식의 비교에는 f_c=n_c가 필요하다. 그 조건에서:

Gamma_F-Gamma_N=C_b x_u f_t.

이는 원본 구현의 버그라는 판정이 아니라 명시된 근사 차이다. 임의의 비열적 companion으로 확장하면 계수 C_b,D_b 자체도 달라지므로 위 차이식만으로 전체 모델 차이를 설명하지 않는다.

정방향 rate F_plus=C_b x_u(1+f_t)>0에 대한 생략 상대량은 f_t/(1+f_t)다. Planck f_t에서 이는 exp(-E_t/theta)와 같다. 그러나 순rate Gamma_F는 정방향과 역방향이 상쇄될 수 있으므로, 이 작은 정방향 상대량을 순rate의 균일 상대오차라고 부를 수 없다. 상세균형에서 Gamma_F=0이고 생략량은 일반적으로 0이 아니다.

## 4. Planck 평형과 Wien 평형은 다르다

u=exp(-E_t/theta), v=exp(-E_c/theta), p=u/(1-u)라 하자. 공통 온도에서 population은 x_u=x_g*u*v이다.

Gamma_F(f_t=p,f_c=v/(1-v))=0.
Gamma_N(f_t=u)=0.
Gamma_N(f_t=p)=-C_b*x_u*p.
Gamma_F(f_t=u)=C_b*x_u*u.

따라서 원본의 Wien null을 전체 쌍식의 정확한 Planck null로 이름만 바꿀 수 없다.

검산용 합성 예: lambda=1 s^-1, u=1/4, v=1/2, x_g=8/9, x_u=1/9이면 C=2 s^-1, D=1 s^-1이다. 이는 E_t=2E_c이고 theta=E_c/ln(2)인 양의 에너지/온도 조건으로 실현 가능하지만, 실제 우주론 population이나 원본 bin 상태를 선택한 것은 아니다.

| f_t | Gamma_N (H^-1 s^-1) | Gamma_F (H^-1 s^-1) |
|---|---:|---:|
| 1/4 | 0 | 1/18 |
| 1/3 | -2/27 | 0 |

## 5. 기준장 변환과 필수 보정항

원본 departure는 d_u=x_u-x_g*u*v, d_b^W=x_g(f_t-u)다.

C_b*d_u-D_b*d_b^W=Gamma_N.

Planck 기준 departure d_b^P=x_g(f_t-p)를 도입하면:

d_b^W=d_b^P+x_g(p-u),
p-u=u^2/(1-u).

따라서 같은 원본 rate를 유지하려면:

Gamma_N=C_b*d_u-D_b*d_b^P-D_b*x_g*(p-u).

보정 없이 기준장 이름만 바꾸면 +D_b*x_g*(p-u)의 가짜 source가 생긴다. 위 합성 예의 Planck 상태에서 이 결함은 +2/27 H^-1 s^-1이다. 이것을 고에너지 유도방출 복원의 차이와 같은 연산으로 취급하지 않는다.

또한 d_b를 occupation이나 occupation의 미분으로 직접 사용할 수 없다. x_g>0에서 f_t=d_b/x_g+w, w는 명시된 기준장이다. 방향미분은:

delta f_t=delta d_b/x_g-d_b*delta x_g/x_g^2+delta w.

Wien w=exp(-E_t/theta)의 경우:

delta w=w[-delta E_t/theta+E_t*delta theta/theta^2].

x_g=0에서는 이 좌표 역변환이 특이하므로 거부하거나 다른 좌표가 필요하다. 이 문서는 새 기준장 adapter를 구현하지 않는다.

## 6. 사건과 두 광자의 장부

반구간에서 한 사건을 한 번 세는 순rate Gamma_b에 대해 두 광자를 명시적으로 계산한다면:

R_(b,t)=Gamma_b, R_(b,c)=Gamma_b,
(delta x_u/dt,delta x_g/dt)=(-Gamma_b,+Gamma_b).

광자수와 에너지 장부는:

Ndot_gamma,b=2 Gamma_b,
Edot_t=E_t Gamma_b,
Edot_c=E_c Gamma_b,
Edot_atom=-E21 Gamma_b,
Edot_t+Edot_c+Edot_atom=0.

이는 충돌에 의한 수소 원자당 rate의 장부다. 팽창에 따른 에너지 변화나 전체 four-force를 유도한 것이 아니다. E_t+E_c=E21에는 위의 반동 무시 범위가 따른다.

고에너지 광자만 진화시킨다면 companion에 전달되는 E_c Gamma_b를 외부 복사장 장부에 명시해야 한다. 이는 원본 프로그램이 독립 companion 방정식을 풀었다는 주장이 아니다. 축약 모델을 다른 계층에 연결할 때 필요한 에너지 회계다.

두 광자를 수치 어댑터로 보낼 때에는 동일 event_id 아래 서로 다른 energy와 leg_id를 가진 두 photon packet을 구성하는 것이 조건부 제안이다. 기존 각 B 열의 합 1은 광자 packet 하나에 대한 규칙으로 유지한다. 한 event 열을 그대로 사용해 모든 column sum을 2로 바꾸는 것은 다른 계약이며 이번에 하지 않는다. 실제 행렬이나 각도는 구성하지 않는다.

140-bin tracked 벡터를 단순히 두 배로 하면 에너지가 2E_b Gamma_b가 되어, 올바른 E21 Gamma_b와 (2E_b-E21)Gamma_b만큼 어긋난다. number만 맞는다고 올바른 광자 쌍을 나타내지 않는다. 서로 다른 사건의 photon 다리가 동일 목표 cell에 놓이는 것은 합산 문제이며 자동으로 중복 사건이라는 뜻도 아니다.

## 7. 쌍식의 방향미분

Q=x_u(1+f_c)(1+f_t)-x_g*f_c*f_t라 두면:

delta Gamma_F=delta lambda*Q+lambda[
 (1+f_c)(1+f_t)delta x_u-f_c*f_t*delta x_g
 +(x_u(1+f_t)-x_g*f_t)delta f_c
 +(x_u(1+f_c)-x_g*f_c)delta f_t].

이 식은 지정한 에너지/구간에서의 변수 미분이다. 실제 map/measure 변화, 사건 경계와 saltation을 포함하지 않는다. 두 photon 다리에 같은 사건미분을 적용해야 atomic/photon ledger가 일치한다. 각도별 비등방 복사장에는 별도의 쌍 방향 커널이 필요하므로 scalar 계수만으로 companion 방향을 추론하지 않는다.

## 8. 검증 계획과 도구 상태

`verify_o2o3.py`는 생산 모듈을 import하지 않는 연구 검산이다. SymPy 항등식, Fraction 반례, PR #65의 고정 CSV를 이용한 80자리 정방향 생략량 진단만 수행한다. 원본 ZIP 추출, 140행 재생성, C 행렬, 실제 deposition 또는 trajectory는 재실행하지 않는다. 실행 성공은 RESULT.json과 실제 workflow 기록이 있을 때만 주장한다.

로컬 container와 Python은 각각 한 번 process 시작 전 ClientError였다. Wolfram context/evaluator는 MCP HTTP404로 커널 결과가 없었다. 따라서 작은 read-only hosted workflow를 별도 경로로 사용한다. 출력과 package 설치는 Git 밖이다. 이 연구는 새 production API를 추가하지 않으므로 구현부재 RED를 만들지 않는다. 잘못된 기준장 변환·유도방출 삭제·광자 에너지 이중배치의 명시적 반례가 검산의 대상이다.

그림은 140개 중심점에서 Planck 가정의 exp(-E_t/theta)를 그린다. 실제 순rate 오차나 관측 예측으로 읽지 않는다. 그림 생성과 렌더링 시각 검토는 별개로 기록한다.

## 9. 두 관점의 감사와 정지 경계

수학 감사: 사건/광자/occupation을 구별하고, s^-1 계수와 H^-1 s^-1 순rate를 구별한다. Planck와 Wien null, rate 생략과 기준장 변환, 외부 companion 장부를 구별한다. 순rate 상대오차는 상세균형에서 정의되지 않으므로 정방향 분모만 사용한다.

코드 감사: 기존 source, COM, resolved adapter, 표와 증거를 변경하지 않는다. 연구 검산의 기호 항등식은 기존 생산 구현의 새로운 PASS가 아니다. 입력 CSV와 실행 스크립트의 Git blob 및 파일 SHA를 기록한다. 같은 작성자의 두 관점 감사이며 독립 reviewer 두 명이나 독립 최종 심사를 주장하지 않는다.

연구 제안은 원본 HyRec를 동결된 비교 기준으로 보존하고, 장기 비평형 확장에는 전체 점유수 쌍식과 두 photon 다리의 명시적 장부를 사용하는 것이다. 다만 연구 제안과 책임자의 생산 모델 승인은 다르다. 선택은 `owner_model_choice=null`로 유지한다. O1 적분 구간, O4 target measure, O5 map, O6 각도/미분의 미결정 사항은 그대로다.

다음 단일 작업: 이 두 경로의 비교와 장부를 근거로 O2/O3의 책임자 모델 선택을 확정한다. 그 전에는 물리 map/source 인증, provider, BASS 연결, ready/merge를 수행하지 않는다.

`NO_PASS_REC_PHYSICAL_SPLIT`
