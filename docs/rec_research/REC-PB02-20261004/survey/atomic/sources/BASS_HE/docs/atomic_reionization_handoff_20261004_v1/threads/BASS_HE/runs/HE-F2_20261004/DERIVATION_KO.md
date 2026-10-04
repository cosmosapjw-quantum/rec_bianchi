# HE-F2: 원자 패킷과 실제 FT03 변수의 결속

## 전제와 근거 상태

BASS_HE supplier pin은 cbc654cf6037a4a0dad2f60fb138964cfff62ada이다. 소비기 pin은
rei_bianchi 64bc3aa0871bb324817afd3d36db018dd34181cf, tree
8ffe43af6debb54a95b4ab7d213c34bd1e1876d4이다. FT03 MODEL_POLICY와 closure_model의
실제 상태 정규화·binding chi를 읽었다. 아래 사건 정식화는 이 상태와 호환되는
**조건부 대수적 결속**이다. 현재 소비기는 charge_exchange를 명시적으로 제외하므로
아래 항을 RHS에 추가하지 않았다. 원자율·전자구조·cosmological history를 새로 계산하지 않았다.

## 1. 사건수와 종 벡터

선택된 W82 ground-state RCT 시나리오는
HeIII + HI -> HeII + HII + photon 이다. 순서 (HI,HII,HeI,HeII,HeIII,e)에서
nu=(-1,1,0,1,-1,0). 핵수와 전하의 왼쪽 벡터는
H=(1,1,0,0,0,0), He=(0,0,1,1,1,0), Z=(0,1,0,1,2,-1)이고 모두 nu와의 내적은0이다.
광자 birth=1, 직접 free-electron=0이다. 광흡수·secondary는 별도 사건이다.

공통 gas-rest Maxwell 온도, 상대 drift0이라는 공급기 조건 아래 proper event density rate는
R=k(T)n_HI n_HeIII 이다. 단위는 k[cm^3/s]와 n[cm^-3] 사용시 cm^-3 s^-1이다.
이종 반응이므로 추가1/2를 넣지 않는다. 반응률 선택·온도 범위는 부모 공급기가 검사한다.

## 2. FT03 상태의 서로 다른 분모

FT03는 x=x_HII=n_HII/n_H, y2=x_HeII=n_HeII/n_He,
y3=x_HeIII=n_HeIII/n_He를 사용한다. Y=n_He/n_H=0.083=83/1000이다.
따라서 사건수/전체H핵/초는

r_H = R/n_H = k n_H Y (1-x) y3,

이고 반응만의 기여는

(dx/dt, dy2/dt, dy3/dt) = r_H (1, 1/Y, -1/Y).

원자 공급기의 nu*k에 밀도곱을 한 번 적용한 뒤, 각 종의 분모로 나누는 것과 같다.
H분율과 He분율에 같은 r_H를 더하면 helium abundance를 잘못 처리한다.
자유전자/H는 e=x+Y(y2+2y3)이므로 de/dt=r_H+Y(r_H/Y-2r_H/Y)=0이다.
Y=0은 이 He fraction 좌표에서 정의되지 않으므로 compiler는 거부한다. 순수H 모형은 별도 좌표/분기다.
FT03의 내부 시간 tau=t/TEND는 소비기 RHS에서 TEND를 한 번 곱한다. 원자 provider나 본 compiler는
밀도·시간 정규화를 실행하지 않는다. 팽창·proper/comoving 변환은 rei_bianchi만 소유한다.

## 3. binding Q와 방출/열은 다른 양

FT03 코드와 fixture의 같은 chi를 각각 AST literal/JSON에서 읽어 동일성을 검사했다:
chi_HI=13.598434599702eV, chi_HeI=24.587389011eV, chi_HeII=54.41776eV.
이들은 FT03에서 채택한 binding convention이다. 이번에 새로운 상수 정확도나 불확실성을 승인하지 않는다.

w=(0,chi_HI,0,chi_HeI,chi_HeI+chi_HeII,0)이면
w.nu=chi_HI-chi_HeII=-40.819325400298eV = -Q.
chi_HeI는 HeII와 HeIII 양쪽에 나타나 상쇄된다. chi_HeI를 chi_HeII 대신 차감하면 안 된다.

국소 사건의 에너지 보존은
Delta E_thermal + Delta E_primary + Delta E_escape + Delta E_other = Q.
other에는 소비기가 선언한 fast/bulk/recoil/excitation 등이 포함된다. 동일 에너지를 여러 칸에
중복 배정할 수 없다. 공급된 scalar k는 광자에너지나 열 moment를 결정하지 않는다.
Egamma=Q, prompt heat=0인 mono-Q 모델은 선택 가능한 **추가 근사**이지 이 항등식의 유일한 해가 아니다.
FT03의 RR/DR escape 규칙은 RR/DR에 한정되어 있다. RCT가 제외된 그 모델에서 이를 RCT에도
자동 적용할 근거가 없으므로 photon_energy_eV와 prompt_heat_eV는 null로 유지했다.

FT03의 primary photon 대표 에너지는20,35,70eV다. Q와 일치하는 군은 없다. 향후 명시적 mono-Q
transport를 선택하더라도 광자 수·에너지와 opacity 적용을 함께 보존하는 projection 또는 별도
방출 채널을 소비기에서 정해야 한다. 본 단계는 임의로35eV 또는70eV 군에 광자를 넣지 않는다.

## 4. 실제 source domain 비교

부모 코드의 GM25 범위는[200,10000]K, KF96 수치호출 범위는[1000,10000000]K이다.
KF96의 원문 하한~표시/nominal prescription 구분은 원 B3 packet에 남는다.
두 출처의 공통구간은[1000,10000]K이며 FT03 guard[30000,110000]K와 교집합이 없다.
초기 T=50000K부터 GM25 범위 밖이다. KF96가 수치 범위를 덮더라도 그것만으로 RCT 활성화·
physical admission·두-source sensitivity의 성립을 주장할 수 없다. 범위를 clamp하거나 가스 온도를
자의적으로 낮춰 기존 실험을 바꾸지 않는다. source spread는 statistical uncertainty가 아니다.

## 결론

원자 측 event/fraction/chemical ledger 및 consumer research schema에 맞는 candidate 표현은
구현되었다. 실제 사용 수락은 별개다. 현재 HE-F2는 BLOCKED_CONSUMER_CONTRACT이며 기존 소비기
모형은 unchanged/no-injection이다. canonical REI-F00/F01 인스턴스와 RCT 포함 여부·온도 범위·
closure 선택이 확정될 때 해당 changed input만 다시 읽는다. REI-F08 baseline과 REI-CHAT-FT05는
이 원자 감도 연결을 기다릴 이유가 없다. HE-L1/L2/L3는 PARKED_OPEN 그대로다.
