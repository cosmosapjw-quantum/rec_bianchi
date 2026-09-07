# Figure inspection

의도: 동일 제조 스펙트럼에서 원자 population ratio에 따른 실제 nodal
entropy 생성률을 비교한다. 계산된 음의 구간을 보존 회계 통과와 구분한다.
곡선은 해석식, marker는 API 출력이며 본문에 명시했다.

첫 PNG를 직접 열어 축·범례·음영·마커와 CASES.csv를 대조했다. 세로축의
`S/N_H k_B` 표기는 곱셈 순서가 모호할 수 있어 `S/(N_H k_B)`로 바꿨다.
plot만 재생성하고 새 PNG를 다시 열었다. 수치 실행과 그 CSV는 바꾸거나
재실행하지 않았다. 두 plot 호출은 모두 process exit0이다.

단일 열 폭 3.54 inch (약90 mm), font 8–9pt로 제작했고 SVG를 보존했다.
180 mm에서는 확대 표시할 수 있다. 축·범례의 겹침/잘림은 관찰되지 않았다.
선 종류와 marker 모양이 색상 외에도 두 조건을 구별한다. 확대된 화면에서
직접 확인한 결과이며 실제 프린터 교정지는 생성하지 않았다.

의미상의 주요 오독 위험은 제조 log-control의 음의 생성률을 실제 물리
엔트로피 위반으로 읽는 것이다. 캡션과 본문에서 제조 이산화의 반례임을
명시했다. 10^3 세로축 배율을 유지하며 log 축·표시 하한·절대값 치환은 없다.

잔여 오류: 관찰된 blocking figure defect 없음. 최종 판정: PASS for this
bounded diagnostic figure. 실제 우주론적 오차막대나 논문 투고 인증은 아니다.

게시 형식 검사에서 Matplotlib SVG path의 줄 끝 공백이 별도로 검출됐다.
serializer에서 그 공백만 정리했다. XML path token·텍스트가 동일하며 PNG
바이트도 동일함을 확인했다. 첫 exit2, 최종 정리 exit0 및 원래 오류
출력은 `evidence/FORMAT_REPAIR.json`에 보존했다. 과학 실행 결과는 불변이다.
