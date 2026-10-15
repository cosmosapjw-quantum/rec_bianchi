"""Scientific route from source-executed primordial HyRec to REI conditional IC.

Freeze the REI scenario *shape* without depending on the user's external
Dropbox checkout in generic REC CI. Source-specific raw full native C
integration is a separate opt-in slow integration test.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
import pytest

from full_bianchi_hyrec.trajectory.rei_initial_boundary import (
    REIConditionalIC,construct_rei_matched_donor,shear_extrapolation_guard,
    HYREC_NU_DENSITY_FACTOR,HYREC_RADIATION_H2_PER_K4,
)

ROOT=Path(__file__).resolve().parents[2]
REPORT_DIR=ROOT/"research/rec_r3c_rei_bridge_20261015"
ORIGINAL_ARCHIVE=ROOT/"archive/inputs/original_hyrec_oct2012/HyRec_Oct2012.zip"


def _scenario():
    return {
        "schema":"rei.axbi.scenario_lock.v1",
        "cosmology":{
            "h0_km_s_mpc":67.4,
            "omega_m":.315,
            "omega_r":.000092,
            "helium_mass_fraction":.2454,
            "tcmb0_k":2.7255,
            "omega_b_formula":"0.0224/(0.674^2)",
        },
        "interval":{"zbar_start":20,"zbar_end":4},
        "gas_initial":{
            "kind":"DECLARED_APPROXIMATE_CONDITIONAL_IC_NOT_REC_DONOR",
            "x_HII":.0002,"x_HeII":0.,"x_HeIII":0.,
            "temperature_k_formula":"2.7255*21^2/(150*(0.0224/0.023)^0.4)"
        },
    }


@pytest.fixture
def ic(tmp_path):
    path=tmp_path/"SCENARIO_LOCK.json"
    path.write_text(json.dumps(_scenario(),sort_keys=True))
    return REIConditionalIC.from_scenario(path)


def test_equivalent_massless_radiation_density_and_source_density_mapping(ic):
    params=ic.matched_hyrec2012_parameters()
    calculated=HYREC_RADIATION_H2_PER_K4*ic.tcmb0_K**4*(
        1+HYREC_NU_DENSITY_FACTOR*params["N_eff_massless_equivalent"]
    )
    assert abs(calculated/(ic.omega_r*ic.h**2)-1)<2e-15
    assert abs(params["omega_cb_h2"]/ic.h**2-ic.omega_m)<2e-15
    assert abs((params["omega_cb_h2"]+params["omega_lambda_h2"]+
                calculated)/ic.h**2-1)<2e-15
    d=ic.densities_at()
    assert d["H_s_inv"]>0 and d["nH_REI_m3"]>0
    assert abs(d["relative_nH_donor_minus_rei"])<.003
    assert 0<d["fHe_REI"]<d["fHe_HyRec"]<.1
    assert ic.actual_electron_fraction==.0002


def test_q0_native_hyrec_electron_and_temperature_is_conditional_rei_candidate(ic):
    native=np.array([[8000.,1.16,1.],[20.,.000210349192936,
                    9.306042400380866/(21*ic.tcmb0_K)], [0.,.000175,.008]])
    b=construct_rei_matched_donor(
        ic,source_z=native[:,0],source_xe=native[:,1],
        source_Tr_ratio=native[:,2],native_source_sha256="native_r3c_fixture")
    assert b["decision"]=="REI_REFERENCE_COUNTERFACTUAL_NOT_ADOPTED"
    assert b["helium_projected_species"]["xHeII"]==0.0
    assert b["donor_minus_baseline"]["xe_fractional"]>0
    assert b["donor_minus_baseline"]["Tgas_fractional"]>.1
    assert (b["donor_minus_baseline"]["optical_depth_rate_fractional"]
            ==pytest.approx(b["donor_minus_baseline"]["xe_fractional"],
                           rel=1e-12))
    assert (b["donor_minus_baseline"]["thermal_energy_fractional"]
            >.1)
    with pytest.raises(ValueError,match="exact original"):
        construct_rei_matched_donor(ic,source_z=native[:,0]+.1,
            source_xe=native[:,1],source_Tr_ratio=native[:,2],
            native_source_sha256="missing_z20")


def test_provenance_rejects_undeclared_reionization_ic_change(tmp_path):
    source=_scenario()
    source["gas_initial"]["kind"]="UNDECLARED_REC_DONOR"
    p=tmp_path/"SCENARIO_LOCK.json";p.write_text(json.dumps(source))
    with pytest.raises(ValueError,match="provenance"):
        REIConditionalIC.from_scenario(p)
    source=_scenario()
    source["cosmology"]["omega_b_formula"]="0.023/(0.674^2)"
    p.write_text(json.dumps(source))
    with pytest.raises(ValueError,match="baryon source"):
        REIConditionalIC.from_scenario(p)


def test_formal_signed_shear_backextrapolation_is_not_admitted_physics(ic):
    output=shear_extrapolation_guard(ic)
    rows=output["rows"]
    def row(q,z):
        return next(x for x in rows if x["q_ref"]==q and
                    x["zbar_formal"]==z)
    assert row(0,1100)["signed_sigma_over_H"]==0
    assert row(-.01,20)["within_REI_physical_domain"]
    assert not row(-.01,600)["within_REI_physical_domain"]
    assert row(-.01,600)["H_parallel_over_H"]<0
    assert not row(-.01,600)["directional_monotone_redshift"]
    assert row(+.01,600)["H_parallel_over_H"]>0
    assert row(+.01,600)["H_perp_over_H"]>0
    assert row(+.01,1100)["ratio_shear_squared_to_hflrw_squared"]>1
    assert abs(row(+.01,600)["signed_sigma_over_H"]+
               row(-.01,600)["signed_sigma_over_H"])<1e-15


def test_frozen_original_source_execution_and_byte_identity_from_saved_receipt(ic):
    # This regression verifies the artifact identity and content of the
    # source-executed result, without rerunning source code in all CI.
    receipt=json.loads((REPORT_DIR/"SOURCE_EXECUTION_RECEIPT.json").read_text())
    compressed=(REPORT_DIR/"HYREC_ORIGINAL_REI_MATCHED_STDOUT.gz").read_bytes()
    data=gzip.decompress(compressed)
    assert hashlib.sha256(data).hexdigest()==receipt["native_C_stdout_sha256"]
    assert hashlib.sha256(compressed).hexdigest()==receipt["raw_output_gzip_sha256"]
    assert receipt["native_C_output_rows"]==8001
    assert receipt["two_worker_parallel_bit_identical"] is True
    hist=np.loadtxt(io.BytesIO(data))
    assert hist.shape==(8001,3)
    assert hist[7980,0]==20
    assert 2e-4<hist[7980,1]<2.2e-4
    assert 9.<hist[7980,2]*ic.tcmb0_K*21<10.
    real=json.loads((REPORT_DIR/"REI_CONDITIONAL_BOUNDARY.json").read_text())
    assert real["source_sha256"]==receipt["native_C_stdout_sha256"]
    assert real["normalization_mismatch"]["nH_REI_m3"]>0


@pytest.mark.slow
def test_original_HyRec2012_full_native_reproduction_independent_of_saved_IC(tmp_path):
    # Actual scientific oracle recompiles unmodified source in a temp tree.
    # This does not start any production REI Rust computation.
    from run_rei_primordial_source_intake import _native_build,_run_once
    source=REIConditionalIC.from_scenario(_saved_scenario_for_slow(tmp_path))
    p=source.matched_hyrec2012_parameters()
    assert hashlib.sha256(ORIGINAL_ARCHIVE.read_bytes()).hexdigest()==(
        "48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27")
    native,binary,_,_=_native_build(tmp_path)
    observed=_run_once(binary,native,p,"CI_SOURCE_INDEPENDENT")
    replay=json.loads((REPORT_DIR/"SOURCE_EXECUTION_RECEIPT.json").read_text())
    assert observed["native_stdout_sha256"]==replay["native_C_stdout_sha256"]


def _saved_scenario_for_slow(tmp_path):
    p=tmp_path/"fixture_rei_scenario.json"
    p.write_text(json.dumps(_scenario(),sort_keys=True))
    return p


def test_rec_donor_export_requires_opt_in_and_exact_source_binding(ic,tmp_path):
    from export_rei_conditional_donor import make_candidate
    sample=np.array([[8000.,1.1634,1.],
                     [20.,.000210349192936,
                      9.306042400380866/(21*ic.tcmb0_K)],
                     [0.,.000175,.008]])
    source=construct_rei_matched_donor(ic,
        source_z=sample[:,0],source_xe=sample[:,1],
        source_Tr_ratio=sample[:,2],
        native_source_sha256="fixture_source_stdout")
    src=tmp_path/"boundary.json"
    src.write_text(json.dumps(source))
    scenario=tmp_path/"scenario.json"
    # Same logical fields but exact file byte hash can vary; identity must
    # refer to the actual read source bytes, never just named scenario.
    new_raw=json.dumps(_scenario(),sort_keys=True)
    assert hashlib.sha256(new_raw.encode()).hexdigest()==ic.scenario_sha256
    scenario.write_text(new_raw)
    out=make_candidate(scenario=scenario,source_boundary=src)
    assert out["activation"]=="DISABLED_REQUIRES_SEPARATE_REI_SENSITIVITY_CAMPAIGN"
    assert out["candidate_initial_gas"]["x_HII"]==sample[1,1]
    assert out["candidate_initial_gas"]["Tgas_K"]==pytest.approx(9.306042400380866)
    assert not out["adopted_into_original_REI_scenario"]
    assert out["original_REI_gas_initial"]["x_HII"]==.0002
    drift=dict(_scenario())
    drift["gas_initial"]={**drift["gas_initial"],"x_HII":.00021}
    scenario.write_text(json.dumps(drift,sort_keys=True))
    with pytest.raises(ValueError,match="drifted"):
        make_candidate(scenario=scenario,source_boundary=src)
