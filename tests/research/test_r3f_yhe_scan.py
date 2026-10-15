"""Deterministic source contracts, numerical stencils and actual C smoke gate."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import pytest
import math

SRC=Path(__file__).resolve().parents[2]/'scripts/run_r3f_ncp_hyrec_yhe.py'
spec=importlib.util.spec_from_file_location('r3f_yhe',SRC)
y=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y)


def test_input_identical_to_pr94_source_native():
    inp=y.source_input(y.PARAMS['YHe'])
    import hashlib
    assert hashlib.sha256(inp.encode()).hexdigest()=='b88ee10ad9614689d9deffef519e7e43e40e209128a7bbe85dfe39078599450a'
    assert inp.count('\n')==8
    for bad in (-.01, .8, math.nan):
        with pytest.raises(ValueError): y.source_input(bad)


def test_richardson_exact_for_quadratic_and_quartic_response():
    center=y.PARAMS['YHe'];h=y.STEP
    # General function at fixed z. Symmetric differences and Richardson.
    d={}
    for idx in y.CENTRAL_INDICES:
        z=center+h*idx
        d[idx]={'z_slices':{'20':{'xe_per_H':3*z+2*z*z+8*z**3+4*z**4,
                                      'Tm_K':2+7*z-2*z*z}}}
    data=y.richardson(d,'Tm_K',20)
    assert abs(data['richardson_h_2h']-(7-4*center))<4e-11
    data=y.richardson(d,'xe_per_H',20)
    exact=3+4*center+24*center**2+16*center**3
    assert abs(data['richardson_h_2h']-exact)<1e-8


def test_output_shape_input_validation(tmp_path):
    with pytest.raises(ValueError): y.execute(output_dir=tmp_path,mode='invalid',workers=1)
    with pytest.raises(ValueError): y.execute(output_dir=tmp_path,mode='smoke',workers=0)
    with pytest.raises(ValueError): y.execute(output_dir=tmp_path,mode='smoke',workers=48,address_limit_gib=4)
    with pytest.raises(ValueError): y.execute(output_dir=tmp_path,mode='smoke',workers=2,wall_limit_s=1)


def test_timeout_preserves_partial_raw_process_evidence(tmp_path, monkeypatch):
    import hashlib, json, subprocess
    binary=tmp_path/'solver'; binary.write_bytes(b'fake executable identity')
    source=tmp_path/'source'; source.mkdir()
    raw=tmp_path/'raw'
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 1, output=b'partial stdout', stderr=b'partial stderr')
    monkeypatch.setattr(y.subprocess, 'run', timeout)
    result=y.original_case(binary, source, 0, wall_limit=1, address_limit_gib=2, raw_dir=raw)
    assert result['status']=='ERROR'
    assert (raw/'input.txt').is_file()
    assert (raw/'stdout.bin').read_bytes()==b'partial stdout'
    assert (raw/'stderr.bin').read_bytes()==b'partial stderr'
    meta=json.loads((raw/'case.json').read_text())
    assert meta['status']=='ERROR' and meta['binary_sha256']==hashlib.sha256(binary.read_bytes()).hexdigest()


@pytest.mark.slow
def test_actual_original_c_native_smoke(tmp_path):
    report=y.execute(output_dir=tmp_path/'real_c',mode='smoke',workers=3)
    assert report['source_reference_comparison']['science_equivalent']
    assert report['science_cases_passed']==7
    assert all(k in report['derivatives'] for k in ('1100','900','20'))
    assert (tmp_path/'real_c'/'SOURCE_DERIVATIVES_Z20_1600.csv').exists()
