# 실제 첫 PNG 검토와 읽는 법

Root Astra와 독립 검토자가 results/figures001의 실제 첫 PNG 두 장을
각각 열어 확인했다. 제목, 축, 단위, legend와 colorbar가 읽히며
잘림이나 panel 겹침이 없다. 그림을 다시 생성하지 않았다.

## absolute_response.png

314 outgoing × 313 incoming의 nominal represented Khat 절댓값을
log10 색으로 표시한다. 대각 성분과 population solve를 통해 전달되는
off-diagonal 성분이 함께 보인다. 이 그림의 색은 coefficient magnitude다.
구간 enclosure 자체와 row norm의 인증 수치는 RAW_RESPONSE.npz,
OUTGOING_ROW_GAINS.csv 및 SUMMARY.json에 있다.

## query_event_contributions.png

위 panel은 최대 nominal row0 및 Lyalpha row311의 |Khat_ij|다.
아래 panel은 같은 Lyalpha event의 |c_j|이며 log 축에 그린 절댓값이다.
아래 축의 Number coefficient 표기는 magnitude로 읽어야 한다.
부호가 있는 원래 coefficient는 QUERY_RESPONSE_COEFFICIENTS.csv를 사용한다.
특히 incoming Lyalpha j311의 c_j=-691681999.2433568
m^-3 s^-1 per occupation이다. 그림이 양의 event flux를 뜻하지 않는다.

두 그림 모두 unit-box sensitivity다. 실제 물리적 incoming error epsilon은
아직 없으며, error bar나 검증된 physical history error로 해석하지 않는다.
Atomic energy와 radiation energy는 같은 event에서 반대 부호이며
outgoing 저장을 추가 photon source로 더하지 않는다.
