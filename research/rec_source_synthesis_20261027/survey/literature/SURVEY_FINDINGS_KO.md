# HD/H5 1차 자료 조사 — 2026-10-27

## 확보한 결론과 다음 실행 선택

고정 LAMDA HD 파일을 원 제공자에서 직접 회수했다. 2289 bytes와 SHA256
`0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`가 기존 고정 입력과 일치한다.
원래 35 Hz 검사와 7/8 실패는 이전 exact 계산을 재사용한다. 이번 조사에서는 해당 계산을 다시 실행하지 않았다.

최신 중앙 저장소 `ee94bef85b56d879dc38f184856a5c613575e9e1`의 다음 세 자료를 읽고 기존 발견을 채택했다.

- `research/rei_expanded_event_consumer/blocker_parallel_20261026/atomic/HD_SOURCE_RESOLUTION.md`
- `research/rei_expanded_event_consumer/coupled_followup_20261026/atomic/HD_SUCCESSOR_PRECISION_GATE.md`
- `research/rei_expanded_event_consumer/blocker_closure_20261026/intake/HD_SOURCE_REPAIR_FINDING.md`

세 문서는 source diagnosis와 precision 조건을 정리했고 새 과학 계산을 실행하지 않았다고 명시한다.
그 문서들에는 8 line × 3 source temperature의 joint thermal imbalance 계산 결과가 없다.
이는 읽은 세 문서의 범위에 대한 진술이며 전체 repo에 대한 부재 증명은 아니다.

다음 유효한 bounded 계산은 고정 source를 그대로 둔 joint thermal incoherence의 정량화다.
에너지 차와 photon frequency를 동시에 사용하는 평형 진단은 기존의 서로 분리된 DB/LTE 검사를 보완한다.
해당 식과 coding 후보는 `DERIVATION_CANDIDATES.md`에 있다.
원 source gate 또는 canonical HD 완료 상태를 바꾸는 계산으로 취급하지 않는다.

## 원자료 진전과 실제 한계

[공식 CDMS v2 archive](https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/)의 directory index를 새로 확보했다.
다음 파일 이름과 수정 시각이 확인되었다:
HD.fit, HD.int, HD.lin, HD.par, HD_bad.lin, HD_mrg.lin,
c003501.cat, c003501.egy, c003501.lit, c003501i.cat.
2011-12-07의 fit/parameter 파일과 2019-02-25의 catalog 파일이 같은 archive에 기록돼 있다.
이 정보는 파일 위치를 좁힌다. 아직 payload identity를 확보한 것은 아니다.

7개 소형 raw payload의 직접 요청은 모두 HTTP503이었다.
비권한 실행환경의 첫 요청은 operation-not-permitted였고, 승인된 네트워크 실행으로 다시 요청한 후 LAMDA만 성공했다.
CDMS의 같은 실패를 더 반복하지 않았다.
실패 응답을 원자료로 저장하거나 수치 source로 채택하지 않았다.
각 receipt는 같은 폴더의 JSON에 있다.

[unversioned CDMS HD entry](https://cdms.astro.uni-koeln.de/cgi-bin/cdmsinfo?file=e003501.cat)는
Exa가 v2 December2011, web search가 v3 August2026 metadata를 반환했다.
중앙 최신 조사에서도 이미 관측한 cache/version 충돌을 재확인했다.
동일 URL이라는 이유로 v3 numerical deck을 회수했다고 기록하지 않는다.

## 재사용한 source 해석

[LAMDA format](https://home.strw.leidenuniv.nl/~moldata/molformat.html)은 level energy를 cm^-1,
A를 s^-1, collision rates를 cm^3/s로 지정한다.
frequency column은 프로그램에서 사용하지 않는 부가 정보로 소개된다.
따라서 유효한 LAMDA 형식과 프로젝트의 공통 energy-frequency 표현 조건은 별도 계약이다.

[CDMS 설명](https://cdms.astro.uni-koeln.de/classic/predictions/description.html)은
음수 molecular tag를 실험 빈도·불확실성의 표시로 정의하고,
예측 catalog에 측정 빈도를 병합한다고 설명한다.
이는 source column 불일치의 가능한 메커니즘이다.
이번에도 실제 HD row tags와 upstream reduction을 회수하지 못했으므로 7개 실패의 row별 원인으로 확정하지 않는다.

현재 기본 .cat/.egy precision만으로 35 Hz를 보장할 수 없다는 중앙의 기존 유도를 재사용한다.
q_e=10^-9 cm^-1, q_nu=10 Hz인 같은 모델의 독립 반올림이면
100 c q_e+q_nu/2=34.9792458 Hz이며,
기존 million-Hz mismatch는 이 반올림만으로 설명되지 않는다.
이것은 internal serialization 조건이다. 실험 불확실성을 35 Hz로 제한하는 주장이 아니다.
합산 frequency로 level ladder를 만들어 equality를 강제하는 대안은 source repair로 채택하지 않았다.

[Flower1999의 저자 기관 기록](https://durham-repository.worktribe.com/output/1616941/a-quantum-mechanical-study-of-the-rotational-excitation-of-hd-by-h2)은
J.Phys.B32(7),1755–1767, DOI10.1088/0953-4075/32/7/016으로 확인했다.
H2 collision 원 논문을 atomic-H 논문이나 Flower–Roueff rovibrational 논문으로 바꾸지 않았다.
원 논문 전체 본문은 확보하지 못했으며, pinned file의 Tables1/2 attribution을 유지한다.

## H5에 연결할 1차 근거

[Neumaier1994 author preprint](https://arnold-neumaier.at/ms/ode.pdf)의
Theorem3.5, Theorem4.1, Proposition4.3, Corollary4.5를 읽었다.
이들은 weighted norm에서 continuous residual, 전체 tube의 Jacobian bound, strict closure를 연결한다.
고정 S에서 signed logarithmic norm μ를 허용하는 error envelope의 원전이다.
이 원전이 REC의 실제 defect·μ·tube-radius·curvature 수치를 제공하지는 않는다.

[Akrivis–Makridakis–Nochetto](https://www.cse.uoi.gr/~akrivis/AMN2.pdf)의 reconstruction 절은
continuous reconstruction을 명시해야 residual-based error equation을 만들 수 있음을 보여준다.
REC의 실제 saved history가 piecewise linear이면 derivative jump를 포함한 별도 interpolation identity가 적절하다.
이에 대한 직접 유도 후보를 같은 폴더에 적었다.
새 원격 계산·IVP·logarithmic-norm 수치 실행은 없다.

## 도구와 근거 범위

SciSpace는 full natural-language question 두 개로 HD spectroscopy와 rigorous ODE error bound 문헌을 검색했다.
Exa는 공식 source와 저자-hosted paper를 찾고 읽는 데 사용했다.
서지 검색 결과의 요약을 수치/증명 authority로 대체하지 않고 primary pages에서 필요한 내용을 확인했다.
원전별 actual reading scope, DOI, source URL은 `SOURCE_REFERENCES.json`,
query와 실패 상태는 `QUERY_PROVENANCE.json`에 있다.

이 조사 자체의 canonical completion increment는 0이다.
부모 작업이 실제 새 유도·구현·독립검토를 완료한 범위를 별도로 판정한다.
raw LAMDA 파일은 private recovery input으로 전달하며 public Git에는 URL/hash/derived facts만 넣는 기존 source 정책을 유지한다.

