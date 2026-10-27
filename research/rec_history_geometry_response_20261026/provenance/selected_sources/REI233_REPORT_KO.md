# H1 일차 전자의 에너지분해 공급원

이번 결과는 기존 GRID044의 연속 광자 이력을 H1 광이온화 일차 전자의 양의 에너지 측도로 연결한 것이다. 광원의 birth time·energy·direction 적분을 보존한 307,200개 에너지 항과 두 광원별 가중치를 실제로 저장했다. 같은 적분 규칙의 기존 모멘트와 최대 상대차 1.3423e-16, 저장된 더 높은 차수의 endpoint 모멘트와 7.4381e-13 이내에서 일치했다. 새 유한 실행은 13/13 검사를 통과했다. 독립 최종 판정은 **PASS_SCOPED_H1_PRIMARY_SOURCE_MEASURE**다. 검토자가 모든 저장 NPZ 값을 별도 표준 라이브러리 경로로 읽어 양성성·모멘트·에너지 수지를 확인했다.

전체 목표에서는 중앙 88노드 DAG의 REI-EXP-EVENT-CONSUMER 아래 **REI-H1-PRIMARY-DEGRADATION-BINDING-01의 스펙트럼 공급 의무**에 해당한다. 직전 대화의 WU import 및 실제 endpoint 연결은 중앙에서 이미 완료돼 있었다. 이번에는 그 32 Python/9 Rust 결과와 PR230의 19개 검사 결과를 재사용하고, 다음으로 지정된 에너지분해 입력을 구현했다. N6 HOLD, L4_ready=false, 전역 물리 완료율 null은 유지한다.

## 근거와 상태 복구

2026-10-26(KST) 조사에서 접근 가능한 51개 저장소의 2,292개 branch head와 관련 7개 저장소의 PR 1,108개를 pagination 끝까지 확인했다. 실제 내용 조사는 다음 의존성에 해당하는 현재 handoff·계약·DAG·source에 집중했다. Dropbox 지정 폴더의 직계 154개 항목을 확인했으며 Drive 목록은 100개 제한 범위다. 다른 비공개 대화는 접근할 수 없었다. 따라서 모든 대화와 모든 branch 내용을 읽었다고 주장하지 않는다.

중앙 PR222는 a5db4bac9dafadae29685bbea3cec7f43ab990b2로 진행했고 PR230 및 owner PR221은 유지됐다. 자동 작업공간 정리로 없어진 이전 파일은 coupled-collision, endpoint S1/S2, opacity archive와 원래 WORK_THREAD 명세에서 복구했다. 알려진 archive SHA256와 크기, source archive manifest의 모든 member를 확인했다. Rust bootstrap이나 이전 과학 suite는 실행하지 않았다.

최신 WU PR150의 registry 확장과 HE PR102의 조건부 열교환 반환을 확인했다. WU의 새 nuclear rate/Q 활성화와 HE의 물리 stopping 승인 상태는 여전히 닫히지 않았다. 과거 synthetic compiler 검증이나 thermal exchange 유도를 실제 electron stopping 입력으로 전용하지 않았다.

## 유도와 세 물리 축

정상 tetrad, metric (-,+,+,+), proper seconds, stationary ground-state H1 target 및 recoil을 무시하는 기존 근사를 사용한다. 기존의 비등방 redshift map으로 E_gamma=g E_birth를 얻고, 원래 photon measure에 HI 단면적을 곱한다.

\[
dA_s=\sigma_{\rm HI}(E_\gamma)dN_{\gamma,s},\quad
E_e=E_\gamma-\chi_{\rm HI},\quad \chi_{\rm HI}=13.6\,\mathrm{eV},
\]
\[
d\dot N_{e,s}^{\rm ref}=c\,r\,y_{\rm HI}\alpha_s\,dA_s,
\qquad d\dot n_{e,s}=r\,d\dot N_{e,s}^{\rm ref}.
\]

여기서 r=5.151254745827818 m^-3, y_HI=1.561568161163724e-5는 저장된 z=2 endpoint의 실제 값이다. stellar/external IGM 광원의 모수와 escape fraction, 정규화는 그대로다. 배경의 log H는 원래 PCHIP, shear는 원래 CubicHermiteSpline과 s/H 도함수를 사용한다. 저장 target은 이 광원 아래 새로 진화시킨 궤적이 아니므로 결과는 지정된 상태에서의 순간 반응이다.

| 축 | 적용 내용 | 의미 |
|---|---|---|
| 대칭성·게이지 | 축대칭·반사 대칭의 원래 birth-angle measure와 비등방 redshift, 정상 관측자, fixed-comoving reference | 에너지 marginal을 취하며 전자 방출 방향의 등방성은 가정하지 않는다. 기준 재정의와 물리 밀도 변화의 미분을 구분한다. |
| 불변량 | H1 핵수·전하와 radiation/binding/primary kinetic energy의 단일 사건 장부 | P=chi M0+K. 동일 H1 사건의 두 source 기여를 더하며 새로운 event owner를 만들지 않는다. |
| 관측가능량으로 이어질 출력 | 에너지별 일차 전자 주입, source별 사건률·평균 운동에너지·문턱 분율 | 선택 모형의 source 진단이다. 실제 thermal deposition은 공급된 spectrum과 승인된 stopping/secondary operator의 결합에서 계산한다. |

정규화된 photon inventory와 y를 고정한 물리 밀도 partial derivative에서는 per-reference source가 r, per-volume source가 r²에 비례한다. 순수 기준 변경 r→lambda r, y→y/lambda, A→A/lambda에서는 물리 source가 불변이다. 일반 quotient 식과 미분은 기존 계약을 재사용했다. Wolfram은 바뀐 atom·moment·quotient 관련 기호 잔차 7개가 0임을 확인했다.

## 실제 결과와 해석

원래 production의 birth/angle/energy 차수 8/12/16을 유지했다. 관측자 에너지 문턱, 이동하는 각도 지지집합, log-energy Jacobian, q/H를 그대로 적용했다. 6개 채널의 기존 suite를 재실행하지 않고 H1 적분의 양의 가중치를 새로 보존했다. 저장 모멘트로 분포를 역산하지 않았다.

| 양 | stellar | external IGM |
|---|---:|---:|
| 일차 전자 주입률 [m^-3 s^-1] | 2.5118260814e-18 | 6.3400374794e-19 |
| 일차 운동에너지 주입 [J m^-3 s^-1] | 1.0268345742e-36 | 4.3574773011e-37 |
| Ee>=10.2 eV 수 분율 | 2.4683% | 10.4953% |
| Ee>=13.6 eV 수 분율 | 0.42949% | 5.27688% |
| Ee>=13.6 eV 운동에너지 분율 | 2.98990% | 26.37167% |

이 문턱 분율은 저장된 유한 양의 측도에서 직접 계산했다. H1 여기·이온화를 위한 에너지 조건을 진단하지만 반응 확률이나 열 침적 분율은 아니다. 새 CDF의 continuum 수렴성은 검증하지 않았고, 이전 fine/oracle 정확도 근거는 그때 검증한 모멘트에만 재사용한다. 양의 source 항의 운동에너지는 0.0111327430–134.4757207213 eV이며, 이론상 허용 범위는 0–136.4 eV다.

전자 에너지와 매질의 이온화 상태에 따라 heating/ionization/excitation 분배가 달라지는 문헌적 맥락은 Furlanetto & Stoever (2010), [arXiv:0910.4410](https://arxiv.org/abs/0910.4410)에 있다. 이 문헌의 numerical deposition fraction을 이번 모형에 도입하지 않았다. SciSpace의 중복 저장소 연도와 자동 요약의 불일치는 출판사 원문 식별자를 기준으로 교정했다. 출처와 사용 범위는 theory/SOURCES.json에 기록했다.

| 검증 | 결과 |
|---|---:|
| 실제 검사 | 13/13 PASS |
| 같은 quadrature의 모멘트 상대차 | 1.3423e-16 |
| 저장 endpoint 모멘트 상대차 | 7.4381e-13 < 5e-12 |
| 에너지 장부 상대잔차 | 1.2228e-16 |
| 정규화 source complex-step 미분 | 2.0211e-16 |
| 물리 source complex-step 미분 | 1.5694e-16 |

zero target/source, 음의 입력·잘못된 frame/reference/source 식별자, 중복 event owner를 검사했다. 밀도 인자 누락, 관측자 에너지 대신 birth energy 사용, threshold subtraction 누락을 검출하는 negative controls도 통과했다. HE receiver는 physical_stopping_provider_admitted=false, thermal_heat_J_m3_s=null을 유지한다.

## 실행·전달과 다음 의무

실행 1회: CPU 0.563139초, wall 0.5670031609988655초, 최대 RSS 103036 KiB. 한도는 1 CPU초/5 wall초, profiling timer 0.8초, 1 worker/BLAS 1, 1 GiB였다. source 누적은 8.764575/10 CPU초 및 8.802586613008316/20 wall초다. Main 595.225063/600 CPU초 NO_MORE_IVPs와 중앙 endpoint의 별도 예산을 보존했으며 서로 이전하지 않았다. 새 렌더링은 하지 않았다. 이번 wrapper CPU 0.032774859초와 독립 저장 배열 검토 CPU 0.892480478초도 별도로 기록했다. 이를 기존 child 원장에 더한 다음 실행 계획용 보수적 CPU 사용은 9.689830337/10초, 잔여 0.310169663초다. 원래 child 원장은 수정하지 않으며, 과거 미계측 overhead는 UNKNOWN으로 유지한다. 추가 1 CPU초 child를 계획할 여유는 없다.

구현자는 gpt-6.1-sol/high, 이론·독립 검토는 서로 다른 Astra 역할로 요청했다. 실제 runtime model identity는 노출되지 않아 UNEXPOSED로 남긴다. 구현 원자료와 입력 snapshot, 32개 binding, 실행 자원 receipt를 보존했다.

공개 Git에는 검토 가능한 text source와 계약·결과를, companion ZIP에는 필수 donor NPZ 및 PRIMARY_SOURCE_ATOMS.npz를 함께 보존한다. Git text만으로 실행하지 말고 delivery/README_PORTABILITY.md의 복원 절차를 따른다. 기존 raw 산출물을 덮어쓰는 재실행은 하지 않는다. 최종 실제 commit·PR·Drive·Dropbox ACK는 뒤에 생성되는 delivery/FINAL_DELIVERY_RECEIPT.json을 확인한다.

다음 최소 의무는 이 source와 같은 frame/reference, 실제 species·charge·T·density 및 Ee 범위를 받는 **승인된 electron stopping/secondary-outcome 연산자**를 확보하는 것이다. HE는 기존 primary reservoir를 받아 residual fast energy·excitation·ionization·thermal energy로 분배해야 하며 photon loss와 binding gain을 다시 생성하면 안 된다. 그 공급자가 준비되면 source packet을 실제 소비하는 소규모 결합을 검증한다. n/T 생성·소멸, beta daughter와 n→p 공급, CR/중성미자/inverse-beta 및 L4 coupled history 의무는 별도로 유지한다.

