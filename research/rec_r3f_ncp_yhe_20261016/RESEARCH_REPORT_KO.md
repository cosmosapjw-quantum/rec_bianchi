# REC R3f: 원본 HyRec FULL H+He의 헬륨 입력 민감도 및 NCP 계산 계약

**일자**: 2026-10-16 KST. **범위**: 원본 October-2012 HyRec의 FLRW \(q=0\), H+He FULL 재결합 이력. REI native 이력 또는 고적색편이 비등방 Einstein–Boltzmann–HyRec 해가 아님. 이번 수치 실험에서는 \(\omega_bh^2,\omega_mh^2,\omega_rh^2,\omega_\Lambda h^2,T_{\gamma0}\)와 원자율 테이블을 고정하고 **입력** \(Y_{\rm He}\)만 바꾸었다.

## 1. 소스와 재현

- REC PR96 부모: `05e35be9f5788b3ea1708027f2c131ccd57985a5`.
- HyRec October-2012 원본 ZIP SHA-256: `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`.
- 이전 PR94의 REI-background-matched original-C stdout: 8,001 rows SHA-256 `6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400`.
- 이번 로컬에서 GCC `-std=gnu99 -O3 -fno-fast-math`로 원본 C를 수정하지 않고 빌드하여 같은 입력의 전 8,001행 stdout을 **byte-identical** 재생산했다.
- 기존 REI scenario SHA-256: `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`. 모든 donor 후보는 `DISABLED`이며 실제 REI 초기조건은 바꾸지 않았다.
- 학술적 원전: Ali-Haïmoud & Hirata, *Phys. Rev. D* **83**, 043513 (2011), DOI `10.1103/PhysRevD.83.043513`; Hirata, *Phys. Rev. D* **78**, 023001 (2008), DOI `10.1103/PhysRevD.78.023001`. 논문의 원전/알고리즘과 코드가 일치하는 물리적 적용 범위만 주장한다.

## 2. 응답함수의 정의와 구성적 유도

source hydrogen number density는 \(n_H(z;Y)\propto (1-Y)(1+z)^3\)이고, 원본 소스 helium-to-hydrogen number fraction은 \(f_{\rm He}=Y/[3.97153(1-Y)]\)이다. \(x_e=n_e/n_H\)로 정의하면 고정된 redshift, \(\omega_bh^2\), \(H(z)\)에서

\[
\left.\partial_Y\ln n_e\right|_z
= \left.\partial_Y\ln x_e\right|_z-\frac{1}{1-Y},
\qquad
\left.\partial_Y\ln\bigl|d\tau_T/d\ln a\bigr|\right|_z
=\left.\partial_Y\ln n_e\right|_z,
\quad\bigl|d\tau_T/d\ln a\bigr|=c\sigma_Tn_e/H.
\]

이는 미시적 helium-only rate 효과가 아니다. \(Y\)가 바뀌면서 수소 기준 개수밀도와 초기 helium census도 함께 변한다. 별도로 REI의 **고정된** recipient \(n_H\)에 donor \(x_e(Y)\)만 입력하는 조건부 실험에서는 \(\partial_Y\ln n_e\equiv\partial_Y\ln x_e\)가 되며, 두 정의는 엄격히 다르다.

각 상태량 \(F(Y)\)의 중앙차분 \(D_h=[F(Y+h)-F(Y-h)]/(2h)\)와 Richardson \(R_h=(4D_h-D_{2h})/3\)를 계산했다. 매끄러운 \(F\)에 대해 \(R_h=F'(Y)+O(h^4)\). Wolfram에서 5차 다항식 테스트 함수의 정확한 오차 \(-4g h^4\)를 확인했다. \(h=0.000125\), 별도 \(2h\), \(4h\) 결과와 비교한다. 계산 출력값의 machine formatting도 오차 예산 일부다.

## 3. 수행한 실제 로컬 원본 C 수치계산

- 첫 시험: \(Y=0.2454+jh\), \(j=-4,-2,-1,0,1,2,4\), **7개 FULL C histories PASS**, source baseline stdout SHA 완전 일치.
- 후속 독립 계산: \(j=-24,\ldots,24\), **49개 FULL C histories PASS**, \(Y\in[0.2424,0.2484]\). 현재 5-logical-CPU affinity 환경에서 4 concurrent native C 과학 case, 본체 6.86초; 7개 동일 control serial/parallel 벽시계비 2.979 (전체 학습/컴파일 소요, NCP 속도 아님).
- 각 case에 대해 8,001개 \(z=8000,\ldots,0\) 행을 온전하게 해석·검사하고 출처 입력/출력 SHA-256, \(z=4,20,100,600,900,1100,1600\) 값을 보존했다. 중앙 7 case로부터 1,581개 \(z=20\ldots1600\) 도함수 표를 작성했다.
- 전체 결과 `local49_fine/RUN.json`, `CASE_SUMMARY.csv`, `SOURCE_DERIVATIVES_Z20_1600.csv`, `SHA256_MANIFEST.json` 및 `SOURCE_NE_YHE_SENSITIVITY.png`, `SOURCE_TM_YHE_SENSITIVITY.png`.

\(Y_0=0.2454,z=20\)에서

\[
x_e=2.10349192936\times10^{-4},\quad T_m=9.306042400380866\;{\rm K},
\]
\[
\partial_Y x_e=2.90610983333\times10^{-4},\quad
\partial_Y T_m=3.04851186664\;{\rm K},
\]
\[
\partial_Y\ln x_e=1.38156452743,\quad -1/(1-Y)=-1.32520540684,
\quad\partial_Y\ln n_e=0.05635912059.
\]

\(\Delta Y=0.002\)의 국소 선형 추정은 \(x_e\) 상대 변화 \(+0.2763\%\), 원본 물리적 \(n_e\) 상대 변화 \(+0.01127\%\)이다. 이러한 상쇄는 원본 source \(n_H\) 변화까지 일관되게 포함한 *local parameter sensitivity*이며 실제 REI optical depth 변화나 새 관측치를 의미하지 않는다.

전체 \(20\le z\le1600\)에서 \(\partial_Y\ln n_e\)는 \(z=142\)에서 \(+3.46374\times10^{-5}\), \(z=143\)에서 \(-2.12039\times10^{-4}\)로 부호가 바뀐다. 인접 정수 적색편이를 선형 보간하면 **\(z\approx142.1404\)**다. 이는 interpolation-derived 위치일 뿐 물리적인 영점 오차막대/추정 posterior가 아니다.

**검증:** source raw stdout byte identity, 49개 native run 전부 finite 및 8,001-row/시계/도메인 검사, 7개 control serial·parallel stdout byte identity, 두 차분 스케일의 Richardson self-consistency, postrun independent result/manifest/invariant verifier PASS. 

## 4. NCP 실행 / 미실행 범위

이 답변 환경에서는 64 CPU/128 GiB NCP에 직접 접근하는 Desktop Commander가 직전 실행 이후 월간 사용 제한 상태다. NCP의 Rust1.99와 64 CPU를 이전 스레드에서 관측했지만 **이번 97-case NCP 실행 자체는 NOT_RUN**이다. 원본 C 입력 매개변수 scan은 NumPy/SciPy/Rust 설치를 요구하지 않도록 Python3 표준 라이브러리, gcc, prlimit만으로 구현했다. NCP 실험은 \(j=-48,\ldots,48\)의 **97개 FULL original-C** 독립 case, 최대48 CPU/총 requested 주소공간상한 96 GiB, 과학 case당 \(120\)초, 완전 독립 create-only output 아래에서 실행한다. 다른 NCP 태스크가 경쟁 중이면 실제 점유 자원을 확인해 작업자 수를 줄인다.

## 5. 다음 물리적 과제

이번 결과는 원본 HyRec 물리 모형의 \(q=0\) source-parameter sensitivity이다. **독립적으로 개발한 Python FULL H+He의 실제 원시 초기 spectrum을 포함한 전체 \(x_e(z),T_m(z)\) 해**와 원본 C production integration parity는 여전히 미완료다. signed Bianchi primordial recombination, He coupled anisotropic collisions, 실제 CMB 및 새 REI native runs는 별도 DAG다. REI PR150의 covariant photon ledger와 source IC 사용 여부는 독립적 source/refinement gate 이후에만 결정한다.

부속 Codex handoff, 실행·backups·return contract는 `CODEX_NCP_HANDOFF_KO.md`, `NCP_RUN_CONTRACT.json`, `scripts/run_r3f_ncp_hyrec_yhe.py`를 참조.
