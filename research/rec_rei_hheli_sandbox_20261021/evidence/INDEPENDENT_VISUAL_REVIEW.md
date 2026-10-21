# 독립 그림 검토

판정: **PASS_SCOPED**. 최종 PNG 5개를 직접 열어 확인했다. 그림 작성 agent의 자체 QA와 별개로 실제 렌더링과 최종 파일 해시를 확인했다.

검토자는 이번 atomic/coupled/plot 구현의 작성자가 아니지만, 재사용된 PR118 tangent dependency의 이전 작성자다. 따라서 해당 dependency 자체의 독립 검증으로 주장하지 않는다.

- `figures/01_shear_stress_evolution.png`: Four norm panels display 125 completed histories, median/range and representative seeds over z20 to2. The zero seed legend uses its declared target; its retained roundoff residual is disclosed. Signed components are added before the total norm. Labels and legend are legible.
- `figures/02_physical_parameter_sweep.png`: Endpoint Sigma norm axis begins at zero. Signed heatmap colorbar ticks are separated, including zero. Stored redshifts and the fixed Sigma slice are explicit; no interpolation or parameter-domain certification is implied.
- `figures/03_all_isotope_ion_fractions.png`: All six populated isotope panels and retained ionic stages are visible, including Li IV. Roman I to IV correspond to charges0 to3. Initial isotope inventory normalization, unpopulated n/T and lack of a populated decay history are explicit. No clipping or diagnostic renormalization is claimed.
- `figures/04_atomic_opacity_energy_diagnostics.png`: Electron density, prescribed T/UV, accumulated optical depth, photon/neutrino signed stress and trace-energy/power diagnostics are legible. Sparse zero ticks and separated legends resolve the earlier display overlap. Net required gas input, absorption, bath-minus-escape and unresolved core energy are distinct.
- `figures/05_opacity_control_response.png`: Paired on/off histories and signed on-minus-off responses are explicit. Off optical depth is labeled as a potential electron column and applied collision is zero. Indirect matter/neutrino geometry feedback and lack of global convergence certification are stated. Legends and footer do not overlap.

125개 main case의 identity·RESULT·NPZ 해시는 앞선 독립 저장 배열 감사와 일치한다. Control의 NPZ와 signed 6성분의 끝점/최대 차이도 독립 산술과 일치한다. PNG/PDF/CAPTIONS 11개 실제 크기·SHA256이 PLOT_BUILD와 일치하며, PDF의 직접 렌더링 검토는 수행하지 않았다.

추가 ODE/NCP/benchmark 0; 과학 입력·배열 수정 0. Physical HOLD, global convergence NOT_RUN, production NOT_APPROVED 및 기존 REC U5 HOLD를 유지한다. 전체 개별 파일 해시와 검토 범위는 동명 JSON에 기록했다.
