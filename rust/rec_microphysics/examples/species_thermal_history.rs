//! Standalone bounded tracer history. Positive/negative shear-like directional
//! factors and temperature perturbations are manufactured prescribed sky inputs,
//! NOT a self-consistent metric evolution. BASS drives the actual geometry.
use rec_microphysics::anisotropic::DirectionalSky;
use rec_microphysics::species_thermal::{Point, ReferenceHistory, matched_step};
fn main() -> Result<(), String> {
    let a = std::env::args().skip(1).collect::<Vec<_>>();
    if a.len() != 3 {
        return Err("usage: species_thermal_history REF.tsv N EPS".into());
    }
    let fail = |e| format!("{e:?}");
    let h = ReferenceHistory::parse(&std::fs::read_to_string(&a[0]).map_err(|e| e.to_string())?)
        .map_err(fail)?;
    let n = a[1].parse::<usize>().map_err(|e| e.to_string())?;
    let eps = a[2].parse::<f64>().map_err(|e| e.to_string())?;
    if n == 0 || !eps.is_finite() || eps.abs() >= 0.1 {
        return Err("bad step count or epsilon".into());
    }
    let dt = h.duration() / n as f64;
    let mut r = h.at(0.).map_err(fail)?;
    let mut y = r.state;
    let fhe = h.f_he();
    println!(
        "eta\txp\tx_heii\tx_heiii\txe\ttm_k\tdelta_xe\tdelta_tm_k\titerations\tscaled_residual\theat_defect_j_per_h\tphysical_compton_j_per_h\tmatched_heat_j_per_h\tbinding_change_j_per_h"
    );
    println!(
        "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t0\t0\t0\t0\t0\t0\t0\t0",
        0.,
        y.xp(),
        y.x_heii,
        y.x_heiii,
        y.xe(),
        y.tm(fhe)
    );
    for i in 1..=n {
        let t = dt * i as f64;
        let next = h.at(t).map_err(fail)?;
        let reference = h.point(next).map_err(fail)?;
        // Prescribed small temperature quadrupole and expansion factors,
        // unit gamma. The density/volume histories are the same FLRW anchors.
        let e = eps * (t / h.duration() * std::f64::consts::PI).sin();
        let temperatures = [next.tr_k * (1. + e), next.tr_k * (1. - e)];
        let expansion = [1. + e, 1. - e];
        let actual = Point::new(
            &DirectionalSky {
                weights: &[1., 1.],
                temperature_k: &temperatures,
                expansion_factor: &expansion,
            },
            next.n_h_m3,
            next.h_s,
            1.,
            3.,
            0.,
            h.helium(),
        )
        .map_err(fail)?;
        let (out, d) = if eps == 0. {
            matched_step(y, r.state, next.state, dt, fhe, &reference, &reference)
        } else {
            matched_step(y, r.state, next.state, dt, fhe, &actual, &reference)
        }
        .map_err(|e| {
            format!(
                "step {i} eta={t:e} previous={y:?} reference={:?}: {e:?}",
                next.state
            )
        })?;
        y = out;
        r = next;
        println!(
            "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            t,
            y.xp(),
            y.x_heii,
            y.x_heiii,
            y.xe(),
            y.tm(fhe),
            y.xe() - r.state.xe(),
            y.tm(fhe) - r.state.tm(fhe),
            d.iterations,
            d.scaled_residual,
            d.thermal_balance_defect_j_per_h,
            d.physical_compton_j_per_h,
            d.matched_thermal_correction_j_per_h,
            d.binding_change_j_per_h
        );
    }
    Ok(())
}
