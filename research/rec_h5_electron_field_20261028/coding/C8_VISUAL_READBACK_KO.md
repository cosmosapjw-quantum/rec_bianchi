# C8 그림 직접 확인

Root가 실제 생성된 `execution/C8_PLOTS_attempt001/figures/fh_parity.png`와 `normalized_residual.png`를 열어 확인했다. 첫 그림은 저장 FH와 새 FH가 겹치고, 아래 패널의 절대 차이가 0인 결과를 보인다. 동결된 512 eps64 S_F 기준은 별도 선으로 표시되어 있다. 두 번째 그림은 각 writer의 정규화 잔차와 4096 eps64 기준을 함께 표시한다. 축·범례·값의 구분이 읽히며 잘림은 관찰하지 않았다.

가로축은 writer index다. 점을 연결한 선을 연속 물리 궤도나 whole-domain enclosure로 해석하지 않는다. 그림은 저장된 primary와 독립 검증 결과에서 생성되었고, 이 시각 확인에서 새 kernel 호출·검증 재실행·추가 렌더는 수행하지 않았다. 수치 판단은 원 JSON 결과를 따른다. Physical 0/313 및 canonical 28/88(+0)을 유지한다.
