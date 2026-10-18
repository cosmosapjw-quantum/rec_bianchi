"""Opt-in U6 performance lane; frozen legacy implementation is unchanged.

Only history ownership/gathering differs. The clock, source atomic snapshot,
Schur solver, thermal RHS, two-step memory, endpoint and tolerances are reused.
No stable escape-factor substitution, new time step, or EMLA evaluation occurs.
"""
from __future__ import annotations

import math
from full_bianchi_hyrec.trajectory import primordial_2012_refined_u6_rt_boundary as legacy
from full_bianchi_hyrec.trajectory.owned_flrw_history import OwnedFLRWHistory


def integrate_u6_owned(checkpoint, c, source, *,
                       max_extra_accepted=legacy.MAX_EXTRA_ACCEPTED,
                       max_full_evaluations=legacy.MAX_FULL_EVALUATIONS,
                       on_attempt=None, observer=None, on_accept=None):
    if not 1 <= max_extra_accepted <= legacy.MAX_EXTRA_ACCEPTED:
        raise ValueError("EXTRA_ACCEPTED_CAP")
    if not 1 <= max_full_evaluations <= legacy.MAX_FULL_EVALUATIONS:
        raise ValueError("FULL_EVALUATION_CAP")
    if legacy.DLNA != 8.49e-5/2. or c.izH0 != legacy.RT_IZ:
        raise ValueError("H2_GRID_OR_RT_START")
    state0 = dict(checkpoint["state"])
    if (state0["iz"] != legacy.START_IZ or state0["post_saha"] or
            state0["xHeII"] != 0. or state0["branch"] != "H_ONLY" or
            abs(state0["z"] - c.redshift(legacy.START_IZ)) > 2.e-12):
        raise ValueError("CHECKPOINT_SOURCE_STAGE")
    if (tuple(checkpoint["rhs_h_tail"]) != legacy.H_RHS_TAIL or
            tuple(checkpoint["rhs_t_tail"]) != legacy.T_RHS_TAIL):
        raise ValueError("CHECKPOINT_PREDICTOR_MEMORY")
    stop = legacy.original_rt_stop_index(c)
    if stop != 58389 or legacy.START_IZ + legacy.MAX_EXTRA_ACCEPTED != stop:
        raise ValueError("FROZEN_RT_BOUNDARY")
    table = legacy._canonical_twophoton_table(source.table.archive_path)
    history = OwnedFLRWHistory(
        energies_eV=table.energy_eV, z_start=c.redshift(legacy.RT_IZ),
        dlna=legacy.DLNA, virtual=checkpoint["virtual_out"],
        average=checkpoint["average_virtual"], lyman=checkpoint["lyman_out"],
        capacity=legacy.PREFIX_COLUMNS + max_extra_accepted,
    )
    if history.accepted_columns != legacy.PREFIX_COLUMNS:
        raise ValueError("CHECKPOINT_PHOTON_PREFIX")
    states, steps = [state0], []
    h2, h1 = legacy.H_RHS_TAIL
    t2, t1 = legacy.T_RHS_TAIL
    evaluations = 0
    for _ in range(max_extra_accepted):
        state = states[-1]
        g, z, xe, tm = state["iz"], state["z"], state["xe"], state["Tm_K"]
        j = g - legacy.RT_IZ
        if g >= stop:
            raise ArithmeticError("EMLA_EVALUATION_PROHIBITED")
        if j != history.accepted_columns:
            raise ArithmeticError("UNACCEPTED_PHOTON_HISTORY_READ")
        if not 0. < xe < 1. or not 0. < tm <= c.T0_K * (1. + z):
            raise ArithmeticError(f"SOURCE_STATE_DOMAIN:{g}")
        if evaluations >= max_full_evaluations:
            raise ArithmeticError(f"FULL_SOURCE_OR_CAP:{g}")
        if on_attempt is not None:
            on_attempt(g, z, xe, tm, j)
        incoming_v, incoming_l = history.incoming(z)
        tr = c.T0_K * (1. + z)
        source_tm = math.nextafter(tm, 0.) if tm == tr else tm
        snapshot = legacy.populate_original_full_atomic(
            source, z=z, xHII=xe, xe=xe, Tm_K=source_tm,
            incoming_virtual=incoming_v, incoming_lyman=incoming_l,
        )
        out = legacy.complete_original_full_atomic(snapshot)
        evaluations += 1
        if (not math.isfinite(out.normalized_matrix_residual) or
                out.normalized_matrix_residual > 2.e-10):
            raise ArithmeticError(f"FULL_SOURCE_OR_CAP:{g}")
        if observer is not None:
            v_view, _, l_view = history.readonly_views()
            observer(g, z, xe, source_tm, v_view, l_view, out)
        dh = out.dxHII_dln_a
        dt = legacy.source_thermal_rhs(c, xe, tm, z)
        xe_next = xe + legacy.DLNA * (1.25 * dh - .25 * h2)
        tm_next = tm + legacy.DLNA * (1.25 * dt - .25 * t2)
        if not all(math.isfinite(x) for x in (xe_next, tm_next)) or not 0. < xe_next < 1.:
            raise ArithmeticError(f"NONPHYSICAL_ACCEPTED_NODE:{g+1}")
        next_state = {
            "iz": g+1, "z": c.redshift(g+1), "xH1s": 1.-xe_next,
            "xHII": xe_next, "xHeII": 0., "xe": xe_next, "Tm_K": tm_next,
            "post_saha": False, "branch": "H_ONLY",
        }
        step = {
            "input_iz": g, "output_iz": g+1, "branch": "H_ONLY",
            "hydrogen_rhs": dh, "thermal_rhs": dt,
            "schur_residual": out.normalized_matrix_residual,
            "photon_col": j, "coupled": True,
        }
        history.append(expected_index=j, virtual=out.outgoing_virtual,
                       average=out.average_virtual, lyman=out.outgoing_lyman)
        states.append(next_state)
        steps.append(step)
        h2, h1 = h1, dh
        t2, t1 = t1, dt
        if on_accept is not None:
            on_accept(next_state, step, out)
    status = ("RT_BOUNDARY_REACHED_NO_EMLA_EVALUATION" if
              states[-1]["iz"] == stop else "HOLD_CAP_BEFORE_RT_BOUNDARY")
    v, a, ly = (array.copy() for array in history.readonly_views())
    return legacy.U6RTResult(tuple(states), tuple(steps), v, a, ly,
                             checkpoint["event"], evaluations, status, stop)
