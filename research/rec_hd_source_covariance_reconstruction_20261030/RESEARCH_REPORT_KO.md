# REC HD 실험 원천 공분산 복원: 역사적 자료 탐색과 calibration-invariant cycle

**연구 단위:** `REC_HD_SOURCE_COVARIANCE_RECONSTRUCTION`  
**일자:** 2026-10-30 (KST)  
**고정 부모:** `cosmosapjw-quantum/rec_bianchi` PR #164, HEAD `e050b97b7d5c6c0929062fafd7333e0164112399`, Open/Draft. 조부모 PR #163, 불변 HEAD `65c5c4c9105c9957418ff014d34e007e53a63b3b`.  
**실행 경계:** 부모·main·owner·production 미수정, 별도 이론 및 구현 산출물 생성. 새 canonical DAG 완료 판정 없음, 자동 후속 노드 없음.

## 1. 원본 복원과 자료 출처

PR #164 SOURCE ZIP을 실제 작업환경으로 복원했다. 크기 **2,582,583 bytes**, SHA-256 `2d781a67a312a7f124955d3ad9c83fe739fa8fb0925390b5139df7d954e92dd8`; ZIP CRC PASS, manifest 46/46 항목의 크기와 SHA-256 일치. 내장된 불변 PR #163 원본 SOURCE ZIP의 SHA-256은 `90ca686b37a15f69605b8f4aad1a259adfb94430474fd6fe8694a38d0365820d`이다. 실측 JSON `data/LAB_INPUT.json`의 SHA-256은 `e568752432b1dc45e2b5ca37f8b767dad0ced0cea2c289fa29dc77ccdbf8da32`이며 이를 변경 없이 `input/LAB_INPUT_PR164_IMMUTABLE.json`으로 복사했다. 구현은 이 입력 바이트가 변하면 거부한다.

새로 확인된 **CDMS 공식 2011년 v2 역사 보존 디렉터리**:

`https://cdms.astro.uni-koeln.de/classic/entries/archive/H2/vers.2/`

서버 인덱스에 `HD.fit`(2011-12-07 14:31), `HD.par`(동일), `HD.lin`(동일), `c003501i.cat`(2011-12-07 16:55), `c003501.egy`(2011-12-07 14:36)가 있다. 같은 디렉터리의 `c003501.cat`은 **2019-02-25** 수정본이라 2011 v2 원본으로 대용하지 않는다. v2 목록에는 `.var`가 없다. `HD.par`는 2011-12-07 헤더와 SPFIT 파라미터 구성이 포함된 **웹 추출 텍스트**를 읽었지만, 원본 바이트 획득/해시 인증은 실패했다. `HD.fit`과 다른 파일 원본도 현재 런타임에서 다운로드되지 않았다. 따라서 상태는 **OFFICIAL_INDEX_LOCATED / ORIGINAL_BYTES_NOT_ACQUIRED**이며, 역사적 full SPFIT fit covariance도 여전히 null이다. `.par` 값만으로 해당 공분산을 임의 복원해서는 안 된다.

Sung et al., *JQSRT* **295**, 108412 (2023), DOI `10.1016/j.jqsrt.2022.108412`의 공개 원문은 `https://hal.science/hal-03870721`에서 렌더된 텍스트로 확인했다. SOLEIL AILES의 2018/2019 FTS 실험에서 순수 HD 세 스펙트럼과 HD+H₂ 14개 스펙트럼을 측정했으며, 물의 잔류 흡수선과 HITRAN 2020 표준을 통해 주파수를 보정했다. 논문의 주파수 정확도 표현은 0.0001 cm⁻¹보다 좋다는 것이다. **네 R(j) 전이는 서로 따로 적합**했고, 각 전이에 해당하는 여러 온도·압력 스펙트럼만 동시에 적합했다. Table 4의 선중심 괄호 오차는 이 피팅 오차이며 실험의 systematic errors는 이를 초과한다고 논문이 명시한다.

논문 Table 7의 상관계수는 선폭, 충돌 주파수 이동, 그 온도의존 파라미터의 coupling에 관한 것이지, 네 선중심 사이의 4×4 공분산이 아니다. 실험적 line-center cross-covariance 및 원 스펙트럼은 미확보. 추가로 제공된 intensity·linewidth·shift의 uncertainty information을 선중심 공분산으로 잘못 이식하지 않았다.

## 2. 실측된 9개 전이 관계의 정확한 그래프

HD의 바닥 진동상태 `v=0`, 회전준위 `J=0,…,8`에 대해 `x_J=E_J/h` (MHz)를 둔다. 실측값은 `y_e=x_{u(e)}−x_{l(e)}`이며 행 순서는 다음과 같다.

- Cozijn 2022의 두 준위차: `(J2,J0), (J3,J1)`.
- Essenwanger–Gush 1984의 세 직접 전이: `(J4,J3), (J6,J5), (J7,J6)`.
- Sung 2022의 네 직접 전이: `(J1,J0), (J2,J1), (J3,J2), (J4,J3)`.

원본 입력의 9개 출판 측정값·DOI·측정 불확도 표기(분포적 의미 부여 없음)와 원래 숫자의 정확한 MHz 환산을 `evidence/MEASURED_NINE_ROWS.csv`에 기록했다. 정확한 상수 `c=299792458 m/s`를 사용한다. 표의 9행은 **새로 생성한 관측이 아니라 기존 실제 논문에 보고된 관계**다.

행렬 `D∈ℤ^{9×9}`의 정확한 rank는 6, 연결성분은 `{0,1,2,3,4}`, `{5,6,7}`, `{8}`이다. rank 3의 왼쪽 영공간 기저로

\[
 C=\begin{pmatrix}
 1&0&0&0&0&-1&-1&0&0\\
 0&1&0&0&0&0&-1&-1&0\\
 0&0&1&0&0&0&0&0&-1
 \end{pmatrix},\qquad CD=0
\]

를 택하면 출판 실측 중심값 사이의 nominal closure residual은

\[
 \mathbf r=C\mathbf y=(-3.921711314,-17.890385768,-60.258284058)\ \mathrm{MHz}
\]

이다. 서로 다른 연결 성분의 절대 에너지 offset은 실험만으로 판별할 수 없다. 따라서 이 9개 관계가 곧 **8개 인접 회전 전이를 모두 직접 실측했다**는 의미는 아니다.

## 3. 공통 보정에 대한 공동 상관오차 모형

전체 실험 관계를 MHz로 표현하면

\[
 \mathbf y=D\mathbf x+B\boldsymbol\eta+\boldsymbol\epsilon,\qquad
 V_y=\Sigma_{\rm fit}+\Sigma_{\rm sys}+B\Omega B^{T}+\Sigma_{\rm cross},\quad
 V_r=C V_y C^T.
\]

여기서 마지막 분해는 **기호적 구조 제안**이지 실제 source covariance의 수치 추정이 아니다. **`V_y`, `Ω`, 원천 사이 상관항의 실험값은 모두 unknown**이다. 원문에 표기된 각 선의 피팅 오차만으로 `V_y`를 대각행렬로 놓을 근거가 없다. 특히 역사적 CDMS fitting parameter covariance가 확보되더라도 그것은 catalog 모형의 예측 공분산 `J_θ Cov(θ) J_θ^T`로 전파되는 객체이므로, **9개 실측 row 자체의 공분산과 구별**해야 한다.

만약 `V_y`를 원천으로부터 확보하고 양의 정부호임이 검증된다면 다음 정확한 identity를 사용할 수 있다.

\[
 \min_{\mathbf x}(\mathbf y-D\mathbf x)^T V_y^{-1}(\mathbf y-D\mathbf x)
 =\mathbf r^T (C V_y C^T)^{-1}\mathbf r.
\]

**증명:** `rank(D)=6`, `rank(C)=3` 및 `CD=0`에 의해 `range(D)=ker(C)`이다. `e=y−Dx`를 정의하면 가능한 residual은 `Ce=Cy=r`인 모든 벡터다. 제약 하에서 `e^T V_y^{-1}e`를 최소화하면 라그랑주 승수법으로 `e_*=V_y C^T(C V_y C^T)^{-1}r`이 나오므로 위 식을 얻는다. 에너지 gauge offset은 이 결과에 영향을 주지 않는다. 특이 공분산에서는 역행렬을 기계적으로 사용하지 않고 support 조건을 다시 확인해야 한다. 본 보고서는 **실제 χ²를 계산하지 않았다**. 합성 SPD 행렬을 이용한 `tests/test_gls_projection.py`는 이 대수 identity만 검증한다.

## 4. 새 명목 calibration-invariant cycle 결합

새롭게 평가한 한정된 반사실적 가설: Sung 네 선중심에 공통 additive 및 multiplicative 주파수 보정만 있다고 놓는다.

\[
 \delta_j=u+v\tilde\nu_j,
 \qquad [\delta_j]=[u]=\mathrm{MHz},\quad
 [\tilde\nu_j]=\mathrm{cm}^{-1},\quad [v]=\mathrm{MHz\,cm}.
\]

이것은 실제 실험 calibration 파라미터를 측정했거나, 가능한 systematic error가 이 두 변수뿐이라고 입증했다는 뜻이 아니다. 이 가정하에서 처음 5개 과거 실측 중심값은 명목 그대로 두고 Sung 네 값만 보정한다. 보정이 세 cycle에 작용하는 행렬은

\[
 CB=-M,\qquad
 M=\begin{pmatrix}
 2&267.06933\\
 2&443.08196\\
 1&350.85401
 \end{pmatrix}.
\]

`rank(M)=2`이며, 그 왼쪽 영벡터를 마지막 성분 1로 정규화하면

\[
 \boldsymbol\ell=\left(\frac{12931303}{17601263},
 -\frac{43463869}{35202526},1\right)
 \approx(0.7346804033324,-1.2346804033324,1).
\]

따라서 모든 `(u,v)`에 대하여 `ℓᵀ(r−M(u,v)ᵀ)=ℓᵀr`이고, **실제 9개 측정 중심값**을 대입하면

\[
 \boxed{\boldsymbol\ell^{T}\mathbf r=-41.0505797921160089478\cdots\ \mathrm{MHz}}.
\]

두 첫 cycle을 정확히 맞추는 보정의 형식적 예시는 `u=8.63669216504520 MHz`, `v=−0.079361773379558 MHz cm`이며, 이 경우 세 번째 cycle에는 `−41.050579792116… MHz`가 남는다. 위 계산은 동일한 **명목 실측값**의 반사실적 보정 불가능성을 보여주지만, **실제 Sung/1984 실험의 불일치 검출이나 유의성, calibration no-go 주장은 아니다**. 1984년 R(3)의 출판 불확도 `±0.002 cm⁻¹`를 포함한 다른 systematic 변수가 허용되면 이 불변량은 사라지거나 값이 변한다. 원본 두 변수 모형에만 유효한 국소 대수 결과다.

## 5. 실제 구현과 검산

`src/correlated_cycles.py`는 불변 입력의 SHA-256을 검사한 뒤 9개 실측값·D·C·calibration response·정확한 유리수 기반 invariant를 계산한다. `src/emit_tables.py`는 출판된 실측 관계 9개를 CSV로 출력하고 source-projection 표도 만든다. `evidence/RESULTS.json`의 공분산, sigma, p-value, chi-square는 **null**이다.

- **원본 PR164:** Python 19/19 normal, 19/19 `-O` 실제 재실행 PASS.
- **신규 단위:** Python 14/14 normal, 14/14 `-O`, `compileall` PASS.
- **Wolfram:** 독립적인 기호계산으로 `rank(M)=2`, 정규화 영벡터, 불변량 정확 분수 `−903177564029399/22001578750000` MHz, 저준위 두 관계 보정 witness 재현.
- **독립 저자 R6/C9:** Wolfram 검산은 수학적 교차검산이지 실제 다른 저자의 코드·논문 심사가 아니다. 원래대로 NOT_RUN.
- **합성 테스트:** 회귀테스트의 임의 행렬은 오직 GLS identity를 확인하며, 실제 실험 공분산으로 수입하지 않았다.

## 6. 결과 판정 및 제한

| 항목 | 판정 |
|---|---|
| CDMS 2011 v2 공식 파일 위치 | **DISCOVERED**, 원본 바이트 미획득 |
| CDMS v2 전체 fitting covariance | **NULL** |
| Sung 4선 joint center covariance | **NULL** |
| 9행 공동 스펙트럼 모형 | **STRUCTURAL_DERIVATION_CHECKED**, 통계 수치추론 미실행 |
| 두 calibration nuisance의 명목 invariant | **DERIVED / EXACTLY_CHECKED** |
| Canonical DAG | **28/88**, 변화 없음 |
| REC Physical DAG | **0/313**, 변화 없음 |
| REC-EXP-SPECTRAL | **PARTIAL**, 9 measured rows / rank 6 / 3 cycles |
| 이전 scoped R/C | **18/20**, 서로 다른 저자 R6/C9 미실행 |
| 원래 35 Hz | **FAIL7/8** |
| H5 epsilon / H6 / H7 | null / OPEN / OPEN |
| L4 / REI activation / production | false / false / HOLD |
| 후속 자동 노드 | **OFF** |

**다음 단일 실무 진입점:** 위 CDMS `vers.2/` 공식 URL에서 `HD.fit`, `HD.par`, `HD.lin`, `c003501i.cat`, `c003501.egy`를 원바이트로 받아 각각 SHA-256/크기/날짜를 보존하고 역사적 SPFIT covariance 존재 여부를 조사한다. 동시에 Sung 저자/데이터 저장소에서 Labfit의 *line center* 공분산과 실제 교정·계통오차 예산을 확보해야 한다. 이 자료가 확보되기 전에는 본 모형의 실제 likelihood, 실험적 cycle 적합성, canonical·physical DAG 완료 여부를 갱신하지 않는다.