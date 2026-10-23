# LINE02 R2–R3 원전·현행 코드 연결

## 선택과 근거 범위

2026-10-23 KST. `/root/line02_sources`는 원전 및 재사용 연결을 구성했다.
독립 심사나 새 수치 캠페인이 아니다. 실제로 읽은 skill context는
`../skill_context/SKILL.md`, `POLICY_INTEGRATION.md`, `THEORY_LOOP.md`
(physmath-research-loop 1.3.0)와 `../RESUME_SELECTION.md`이다.
요청 범위는 R2/R3이며 native solver, IVP, 과거 campaign을 실행하지 않았다.

## 1. 이번에 고정할 소스

| 역할 | 고정 소스 | 읽은 위치와 재사용 의미 |
|---|---|---|
| 실행 계약 | REC114 df95a074730ea0d13d609cf88d448f01f4a47ef1의 May2012 hydrogen.c | 기존 donor hash421ad4678a9a2f00d54f72ebb841648f34a95a9892171c07af5f657a3b2a051b. 실제 저장 snapshot을 생성한 버전이다. |
| 이론 근거 | Ali-Haïmoud & Hirata, HyRec, arXiv:1011.3758v2, Phys.Rev.D83,043513(2011) | §II eq4–5, §III.A eq18–20, §IV.D.3, §V eq71–94. |
| 최신 대조 | Lee & Ali-Haïmoud, HYREC-2, arXiv:2007.14114v2, Phys.Rev.D102,083517(2020) | §II.C eq3–8, §III.A eq10, §III.B eq11와 바로 뒤 단락. |
| 현행 upstream 확인 | nanoomlee/HYREC-2 master09e8243d0e08edd3603a94dfbc445ae06cafe139 | 마지막 commit2023-09-14, README 변경. hydrogen.c blob233f174bfb1758fa910866310340ae1bfad703db,46627byte. |

조회 HTML/PDF의 다시 생성된 표지 날짜(2024/2026)를 새 논문 버전으로 해석하지
않는다. arXiv version과 정식 출판 식별자를 기준으로 한다. SciSpace는 같은
논문의 중복 레코드와 다른 year를 반환했으므로 검색 결과의 year는 채택하지 않았다.
원 논문/식으로 검증했다.

## 2. 원전이 실제로 주는 소유권 구분

**HyRec2011.** Eq18의 공명선 순 flux는
`R_Lyn [x_np−3x_1s f_plus]`이다. Eq19–20의 f_plus는 이전 redshift에서
오는 redward radiation history다. §IV.D.3에서 core 입사장은 이미 blue-wing
two-photon 및 diffusion에 의해 처리된다. §V eq79의 virtual population
`x_b=x_1s fbar_b`는 복사장을 표현한 보조 좌표이다. Eq82는 line center와
인접 bin의 diffusion을 2p와 연결하고, eq86/93은 실제·가상 상태의 결합
선형계를 정의한다. Eq94의 과거 입력 이후에 계를 풀고 red-edge 값을 갱신한다.
따라서 core pair만의 교체는 현존 virtual diffusion과 history를 자동 소유하지 않는다.

**HyRec2.** Eq3의 effective ground-state rate에는 실제 radiative history 의존성이
있다. Eq10의 Sobolev base rate는 `8πH/(3nH x1s λ³)`이며, eq11의
`R_Lya/(1+Δ)`는 full mode의 같은 상태에서 xdot_e를 맞춘 보정이다.
논문은 두 excited population을 동시에 맞추는 별도 보정은 선택하지 않았다고
명시한다. 그러므로 그 표를 하나의 독립 microscopic source로 취급하거나,
기존 full diffusion/source 위에 더하는 방식은 논문에서 도출되지 않는다.

## 3. 실행 소스에 직접 대응한 최소 변경 표면

다음은 보존된 May2012 code를 직접 읽은 결과다. 새 이론의 추정이 아니다.

| 원본 code site | 직접 식 | 소유권 |
|---|---|---|
| hydrogen.c441 | RLya=LYA_FACT H/(nH x1s) | thick core coefficient |
|462|Trr[1][1]=Beta[1]+R2p2s+RLya|core decay의 단일 diagonal 기여|
|464|sr[1]=recombination terms+3RLya x1s Dfplus_Ly[0]|core blue feedback의 짝|
|469–477|two-photon real/virtual couplings|현재 virtual sector 유지|
|492–517|A2p_up/down 및 인접-bin coupling|bare A21가 아닌 diffusion; core pair와 구분|
|521–526|Dtau, Tvv0, sv|가상 frequency-spike source|
|594–618|Trr−Trv Tvv^-1 Tvr, sr−Trv Tvv^-1 sv|선형 Schur 제거; 새로운 IVP 불필요|
|667–718|fplus_from_fminus|시간 지연 경계 입력|
|794–799|Dfminus_Lya=xr[1]/(3x1s), Dfbar=xv/x1s|해를 얻은 뒤 복사 출력 갱신|

`xr[1]`은 실제 x2p가 아닌 Wien equilibrium으로부터의 departure다.
`Dfplus`도 같은 방식의 distortion이다. 고정 TR에서
`x2p=xr[1]+3x1s exp(-E21/TR)`,
`f_plus_native=exp(-E21/TR)+Dfplus_Lya`를 함께 사용하면 core 식은
`RLya[xr[1]−3x1s Dfplus_Lya]`로 정확히 옮겨진다.
LINE01의 full Planck/stimulated 모델은 별도 계약이며 여기의 native 복원 항에
부분적으로 섞어 넣어선 source identity가 유지되지 않는다.

## 4. 최신 upstream의 재사용 판단

현행 source는 May2012 source와 byte-identical하지 않다. exact current blob을
tree로 검증했고 비교 diff를 저장했다. current hydrogen.c637/664/666은 위의
RLya/core diagonal/core blue pair를 그대로 갖고,667에는 `0.75 exclya`가
추가된다. current source에는 SWIFT와 비표준 에너지 주입 등 더 넓은 변경이
있다. 이번 frozen snapshot adapter는 기존2012 pin을 유지하는 것이 맞다.
상류 최신 코드는 *대조 근거*이며 이 작업에서 runtime 교체하지 않는다.

재사용할 핵심은 원본 block partition과 Schur 계산이다. 임의의 단일 core
coefficient/source pair 변경을 실제/가상 모든 항의 재계산으로 확대할 필요가 없다.
정확한 rank-one update와 미분은 LINE02 유도 작업에서 별도로 증명하고,
수치 오차·conditioning은 해당 실행 결과로 판정한다. 이 문헌조사는 새 update를
상류가 제공한 구현으로 오인시키지 않는다.

기존 REC MIT license와 저작권표시는 보존한다. upstream root recursive tree에는
LICENSE/COPYING 이름의 파일이 없고 source header도 명시 license를 제공하지
않는다. 이 제한된 조사로 upstream 권리조건 전부를 판정하지 않았다.
이번 current upstream 전체 파일은 출처 비교용 읽기 증거이며 신규 실행
의존성으로 vendoring하지 않았다. REC MIT가 상류 전체를 재라이선스한다는
주장은 하지 않는다.

## 5. 물리 장부의 경계

한 core bound–bound event는 원자 upper/lower 및 line photon의 교환으로
맵핑할 수 있다. 하지만 virtual `x_b`를 추가 원자 종으로 세거나, 모든
virtual flux에 똑같은 Lyα photon energy를 곱하면 원래 frequency-resolved
복사 문제를 바꾼다. 원자 internal energy와 복사 energy ledger는 교체한
core pair에 한정해야 한다. 재결합/이온화, two-photon, diffusion recoil,
과거 경계장 및 matter-temperature의 완전한 열역학 장부는 별도 의무다.
고정 입력에 대한 JVP와 전체 상태/이력에 대한 JVP도 구분해야 한다.

Physical HOLD, REC U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET,
global convergence NOT_RUN, production NOT_APPROVED, REI_activation=false를 유지한다.
기존 first-failed REI raw의 historical local-only 보존 범위도 변하지 않는다.

## 6. 실제 조회 및 실패 범위

- Exa targeted search1, SciSpace natural-language search1.
- Web primary retrieval: 원문2 URL batch 중1011.3758 HTML DisabledError1;
  같은 논문의 PDF 경로로1회 복구 성공. 후속 find/open은 이미 연 문서의
  수식 위치를 읽었다. 총 web tool call4.
- GitHub read3: current master commit, pinned hydrogen.c, pinned recursive tree.
  마지막 tree read는 connector가 decoded UTF-8 content를 반환하여 API base64
  metadata가 없었던 상황에서 blob identity 및 license-file names를 확인하기
  위한 구체적 후속이었다. 원격 재조회 retry는 없었다.
- 로컬 wrapper extraction2회 실패 후 실제 envelope keys를 확인했다.
  첫 parser는 최종 content를 base64 API JSON으로 잘못 예상했고,
  두 번째는 encoding=base64 종료만 추가하여 동일 decoded-content 상황을
  해결하지 못했다. 실제 decoded UTF-8를 사용한 표적 수정으로 저장 성공.
  원격 재실행/과학 실행0, 원본 source/raw 수정0.
- 라이선스 source 파일 및 snapshot 자료는 기존 보존본을 읽었다.
  literature/papers ZIP은 필요한 원전이 직접 확보돼 추가 추출하지 않았다.

추천 다음 행동: saved snapshot의 core diagonal+blue pair를 함께 제거/교체하는
단일 독점 owner 계약을 먼저 고정하고, 그 밖의 block/history는 고정한다.
그 상태에서 기존 Schur를 재사용하는 residual/JVP/number-energy adapter를
한정 검증한다. 전체 full-history 실행과 Li yield closure는 이번 문헌근거가
제공하지 않는다.

## 출처 URL

- https://arxiv.org/pdf/1011.3758
- https://doi.org/10.1103/PhysRevD.83.043513
- https://arxiv.org/html/2007.14114v2
- https://doi.org/10.1103/PhysRevD.102.083517
- https://github.com/nanoomlee/HYREC-2/commit/09e8243d0e08edd3603a94dfbc445ae06cafe139
- https://github.com/nanoomlee/HYREC-2/blob/09e8243d0e08edd3603a94dfbc445ae06cafe139/hydrogen.c

Root가 citation하려면 직접 위 URL을 open해야 한다. 이 agent의 webpage refs는
turn33view1, turn34view0, turn36view0이며 참고용이다.

