# P02B: 원본 HyRec FLRW 조건부 endpoint

원본 October-2012 HyRec의 `input.dat` cosmology에서 `z=5.807` endpoint를 실제 계산했다. 판정은 `PASS_SCOPED`이며 독립 리뷰 전 상태다. REC 입력의 source와 실제 출력 부재를 이 FLRW 조건부 범위에서 해소한다. REI/Bianchi 초기조건 채택, 저온 REI atomic/thermal provider, photon 또는 CR history는 이 결과만으로 닫히지 않는다.

## 실행 계약과 원본 보존

저장소의 원본 `archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip`을 사용했다. ZIP SHA-256은 `48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27`, `HyRec/input.dat` SHA-256은 `f8073ba70197378e156a6723e229ff47cc9f0d8be0121f1fce82aff6c64abcbc`이다. 원본 ZIP과 저장소의 기존 파일은 수정하지 않았다. 원본 구성원은 임시 빌드 폴더로 추출하고, refinement 폴더의 `hyrec_params.h`에서 `DLNA` 한 매크로만 `8.49e-5`에서 `4.245e-5`로 변경했다. 원본·effective member hash는 evidence에 보존했다.

계약의 cosmology는 `T0=2.728 K, obh2=.021976, omh2=.13, okh2=0, odeh2=.343, w0=-1, wa=0, Y=.24, Nnueff=3.04, fsR=meR=1`이다. 원본 parser는 마지막 `1.,1.` 입력 줄을 읽지 않고 `fsR=meR=1`을 자체 설정한다. 이 effective 설정도 출력으로 확인했다. 질량비는 원본의 `3.97153`을 유지했다.

`endpoint_driver.c`는 원본 `hyrec.c`의 할당·table intake·`rec_build_history` 경로를 사용한다. 원본 `rec_interp1d`를 `ln(a)=-log1p(5.807)`에서 호출해 endpoint를 추출한다. 계산의 원본 `MODEL FULL` 설정과 내부 저적색편이 Peebles 전환은 그대로다. CLI 출력의 `Tm/Tgamma`를 온도로 오인하지 않도록 native `Tm` 배열의 K 값을 직접 내보낸다.

## 결과

| 물리량 | DLNA=8.49e-5 | DLNA=4.245e-5 |
| --- | ---: | ---: |
| `xe = ne/nH` | 0.0001860196684866345 | 0.0001860195581797334 |
| `Tm` (K) | 1.0120602409998003 | 1.0120600999382203 |
| `ne` (m^-3) | 0.010998414136317698 | 0.010998407614421436 |

공통 배경 값은 `a=0.14690759512266782`, `Tgamma=18.569496 K`, `nH=59.12500665007869 m^-3`, `nHe=4.701224649342645 m^-3`, `fHe=0.07951330436486959`, `H=2.086105637709873e-17 s^-1`이다.

`xe`, `Tm`, `ne`의 refinement 상대 차이는 각각 `5.929855021593254e-7`, `1.3938063557787944e-7`, `5.929855021991819e-7`로 고정 한계 `1e-4`를 통과했다. 이는 한 번의 시간격자 반감 비교이며 수렴 차수, continuum error 또는 global model error 인증이 아니다. 각 native history의 105859/211717개 노드에서 유한성, 전자분율 범위, 양의 온도를 확인했다. endpoint의 SI 정규화·charge mapping 및 four-node cubic export는 `64*epsilon` 한계 안이다.

`xHII=xe`, `xHI=1-xe`, `xHeI=1`, `xHeII=xHeIII=0`은 **원본 HyRec의 helium cutoff 이후 neutral mapping**이다. 해석 표기는 `neutral-after-original-HyRec-cutoff`이며, 작은 잔류 helium 이온분율을 실제로 해상한 결과라는 뜻은 아니다. 이 endpoint는 archival FLRW recombination 잔류 상태로서 astro-heating이 없는 값이다. 약 1 K의 온도를 임의로 올리거나 현재 CR-PHYS01의 100 K knot에 맞추지 않았다.

## 검증과 재현

각 science run의 제한은 300초이며 baseline/refined 두 번만 실행했다. 최초 실행 실패와 수리는 없었다. 원본 C의 `fscanf` 반환값 무시 compiler warning은 raw build stderr에 보존했다. 원본 source를 warning 제거 목적으로 바꾸지 않았다. 테스트는 source mismatch 차단, DLNA-only 변경, 저장 endpoint의 domain/mapping/cubic/refinement, 잘못된 helium mapping·온도 export·refinement의 거부를 검사한다.

```bash
python3 -B -m unittest discover -s research/p02b_flrw_endpoint_20261010 -p 'test_endpoint.py' -v
python3 -B research/p02b_flrw_endpoint_20261010/run_endpoint.py --output /path/to/new/p02b-evidence
```

`run_endpoint.py`는 기존 출력 폴더를 거부한다. Python 표준 라이브러리와 `cc -O2`만 사용하며 CAMB 및 fast-math flag는 없다. command/exit/stdout/stderr, compiler와 executable hash, 원본 source/member/config/driver hash, runtime은 `evidence/`의 JSON과 raw receipt에 있다. 임시 executable은 실행 후 제거하므로 executable 보관이나 원격 실행 ACK는 주장하지 않는다. source와 driver로 재빌드할 수 있다.

다음 작업은 이 endpoint와 별개인 **cosmology 및 Bianchi 배경 대응**, **현재 약 1 K 상태에 유효한 atomic/thermal/secondary provider**, **photon/source 초기조건**의 계약을 닫는 것이다. 그 전까지 `REI_Bianchi_IC_adoption=HOLD`를 유지한다.
