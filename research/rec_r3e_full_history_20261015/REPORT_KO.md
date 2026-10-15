# REC R3e: 독립적으로 진화시킨 원본-C/Python FULL 광자 이력 비교

2026-10-15 KST. 부모 커밋 `a76cf0f3044f4946ee4a6c3eb1c9beec3405aee6`, 원본 HyRec ZIP SHA256 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.

**실제로 수행한 계산:** 원본 October 2012 `hydrogen.c::rec_HMLA_2photon_dxHIIdlna`를 변경하지 않은 채 별도 C wrapper를 통해 시간마다 호출했다. `double **`로 NumPy의 고정된 과거 spectrum 행을 직접 넘겨 불필요한 이전 이력 전체 복사를 피한다. 원본 C와 독립 Python 계산은 각각 자기 자신의 311-bin virtual / 3 Lyman outgoing 이력과 수소 전자분율을 새 단계마다 갱신한다. 원본과 Python 사이에 미리 계산한 `x_e(z)`이나 spectral output을 주입하지 않는다.

**공유 전제:** FLRW `q=0`, H-only, `z_start=900`, `x_HII,0=.04`, `T_m/T_gamma=.98`, 이전 spectral distortion은 인위적인 0. 단계 크기는 원본 C와 정확히 동일한 `d ln a=8.49e-5`. chemistry는 Euler, thermal은 암시적 Compton/adiabatic. 계산용 FLRW `H(z)`, `n_H(z)`, thermal law는 동일한 source constants를 사용한다. 원본 production의 higher-order full H+He integrator가 아니므로 primordial physical-history parity를 주장하지 않는다.

**직접 계측:** 33개 시점에서 최대 정규화 오차 `4.2056406721019395e-13`; 129개 시점에서 `6.076757312080765e-13`. 129개에서 `x_HII`: `1.8474805019152996e-14`, `Tm`: `5.559177010959895e-16`, RHS `1.9792880233216484e-13`, virtual `6.076757312080765e-13`, Lyman `2.8281990482160983e-13`. Local owner Ubuntu fast suite `488 passed,41 deselected`; reported logs remain at `/home/cosmosapjw/rec_theory_runs/REC_R3E_NATIVE_HISTORY_20261015/checkout/research/rec_r3e_full_history_20261015/`.

**수학 검산:** `T_next=(T+h A T_gamma)/(1+h(2+A))`, `A=Gamma_C/H>=0`. Wolfram에서 `h>0,T>0,T_gamma>0`의 positivity, 입력 `T<=T_gamma`일 때 동일 광자온도 상한, `x_next=x+hF`의 양/음 F별 positivity admissibility 조건을 기호적으로 확인했다. `x`의 유계성은 무조건 보장되는 것이 아니라 `F<0`일 때 `h<x/(-F)`, `F>0`일 때 `h<(1-x)/F`가 필요하다.

**NCP 관측:** SSH host `s1a0e5abed09`/64CPU/약125GiB RAM/Rust 1.99.0 확인. 기본 Python에 NumPy/SciPy 없음. Python 환경 준비 단계가 실행 도구 안전 검사에 의해 차단되었고 이어 Desktop Commander 월간 한도 도달. NCP scientific job = **NOT_RUN**. 환경 한도 이후 같은 원격 기능 재연결이나 반복을 시도하지 않았다.

**게시/복구:** GitHub 커넥터를 통해 이 브랜치에 재구성한 source wrapper·Python verifier·test를 게시한다. *게시된 바이트가 local verified source와 동일하다는 최종 readback 검증은 미수행*이다. 로컬 worktree는 원격 branch와 병합/동기화 시 untracked 파일 충돌 가능성이 있으니 먼저 파일을 보존해야 한다. 원래 REC root dirty checkout, 원본 HyRec ZIP, REI production과 checkpoint는 수정하지 않았다.

**REI 연결:** 현재 관찰한 REI PR150 head는 `c578683d995d375dbfc824cb080cb6b576d19348`, donor 설정 Git blob `d9dcdbb4b33ebfe89f6c1322cba2a83a7bab15a6`. REC PR94의 z20 donor와 관련된 설정은 바꾸지 않았다. 새 z900 artificial prehistory 궤적을 REI 조건으로 승격해서는 안 된다.

**남은 핵심 작업:** 실제 고-z 초기 radiation 경계와 coupled helium species를 포함한 independent FULL physical history/원본-C 시간 적분 비교, 이어 native REI isolated gas/RT sensitivity. 별도 NCP 48-worker original-C H+He YHe finite-difference campaign은 계획되었지만 실행하지 못했다. Dropbox+Drive 이중 cloud 업로드도 이번 R3e 단계에서는 미완료이며 GitHub 게시만 보존된다.

근거 상태: **LOCAL IMPLEMENTATION-VERIFIED, NUMERICALLY CHECKED; NCP BLOCKED; PR SCIENTIFIC ADMISSION CONDITIONAL.**
