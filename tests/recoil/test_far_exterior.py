from pathlib import Path
import numpy as np
from full_bianchi_hyrec.recoil import pair_cell_conductance as PCC
from full_bianchi_hyrec.recoil.far_exterior import (
    FAR_BLUE_CELLS, FAR_RED_CELLS, assemble_scalar_pair_generator,
    far_pair_conductance, interval_mode_measure,
)

def test_far_cells_are_symmetric_and_cover_10p25_to_21p25():
    assert FAR_RED_CELLS[0][0] == -21.25
    assert FAR_RED_CELLS[-1][1] == -10.25
    assert FAR_BLUE_CELLS[0][0] == 10.25
    assert FAR_BLUE_CELLS[-1][1] == 21.25
    assert tuple((-r, -l) for l, r in FAR_RED_CELLS[::-1]) == FAR_BLUE_CELLS

def test_selected_far_pair_is_positive_and_orientation_independent():
    source=(float(PCC.xedges[0]),float(PCC.xedges[1])); target=FAR_RED_CELLS[-1]
    f=far_pair_conductance(target,source,lane='coarse',ell_max=4)
    r=far_pair_conductance(source,target,lane='coarse',ell_max=4)
    assert f[0]>0 and np.linalg.norm(f-r)/np.linalg.norm(f)<2e-12

def test_outermost_far_tail_is_tiny_for_wing_source():
    # Use the durable v0.50 production network for this compact CI gate.
    # Reintegrating all six full bound+continuum far pairs belongs to the
    # PR-03 scientific-stage audit and is intentionally not repeated here.
    data_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "full_scalar_com_khw_v050.npz"
    )
    with np.load(data_path, allow_pickle=False) as data:
        labels = data["state_labels"].astype(str)
        pair = data["pair_moments_m3_sInv"][0]
    index = {label: i for i, label in enumerate(labels)}
    source = index["I00"]
    inner = sum(
        pair[index[label], source]
        for label in ("FR01", "FR02", "FB00", "FB01")
    )
    outer = sum(pair[index[label], source] for label in ("FR00", "FB02"))
    assert outer / inner < 1e-8

def test_generic_pair_generator_preserves_number_and_equilibrium():
    pi=np.asarray([2.,3.,5.]); s=np.zeros((3,3)); s[0,1]=s[1,0]=.4; s[1,2]=s[2,1]=.7
    g=assemble_scalar_pair_generator(s,pi)
    assert np.max(np.abs(np.ones(3)@g))<1e-15
    assert np.max(np.abs(g@pi))<1e-15
    assert interval_mode_measure(-.25,.25)>0
