//! Source-owned reference with a manufactured smooth directional sky. The
//! temperature and Sobolev perturbations are prescribed, not a Bianchi solve.
use rec_microphysics::anisotropic::DirectionalSky;
use rec_microphysics::species_thermal::{
    Point, ReferenceHistory, ReferenceNode, SDIRK_GAMMA, sdirk_first, sdirk_second,
};
fn actual(h: &ReferenceHistory, r: ReferenceNode, eps: f64) -> Result<Point, String> {
    let e = eps * (r.eta / h.duration() * std::f64::consts::PI).sin();
    Point::new(
        &DirectionalSky {
            weights: &[1., 1.],
            temperature_k: &[r.tr_k * (1. + e), r.tr_k * (1. - e)],
            expansion_factor: &[1. + e, 1. - e],
        },
        r.n_h_m3,
        r.h_s,
        1.,
        3.,
        0.,
        h.helium(),
    )
    .map_err(|e| format!("{e:?}"))
}
fn main() -> Result<(), String> {
    let a = std::env::args().skip(1).collect::<Vec<_>>();
    if a.len() != 3 {
        return Err("usage: species_sdirk_history REF.tsv N EPS".into());
    }
    let err = |e| format!("{e:?}");
    let r = ReferenceHistory::parse(&std::fs::read_to_string(&a[0]).map_err(|e| e.to_string())?)
        .map_err(err)?;
    let n = a[1].parse::<usize>().map_err(|e| e.to_string())?;
    let eps = a[2].parse::<f64>().map_err(|e| e.to_string())?;
    if n == 0 || !eps.is_finite() || eps.abs() >= 0.1 {
        return Err("invalid integration parameters".into());
    }
    let f = r.f_he();
    let h = r.duration() / n as f64;
    let mut old = r.at(0.).map_err(err)?;
    let mut y = old.state;
    println!(
        "eta\txp\tx_heii\tx_heiii\txe\ttm_k\tdelta_xe\tdelta_tm_k\titerations\tscaled_residual\theat_defect_j_per_h"
    );
    println!(
        "0\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t0\t0\t0\t0\t0",
        y.xp(),
        y.x_heii,
        y.x_heiii,
        y.xe(),
        y.tm(f)
    );
    for i in 0..n {
        let m = r.at((i as f64 + SDIRK_GAMMA) * h).map_err(err)?;
        let b = r.at((i + 1) as f64 * h).map_err(err)?;
        let pm = r.point(m).map_err(err)?;
        let pb = r.point(b).map_err(err)?;
        let am = if eps == 0. {
            pm.clone()
        } else {
            actual(&r, m, eps)?
        };
        let ab = if eps == 0. {
            pb.clone()
        } else {
            actual(&r, b, eps)?
        };
        let first = sdirk_first(y, old.state, m.state, h, f, &am, &pm)
            .map_err(|e| format!("step {i} stage1: {e:?}"))?;
        let (next, d) = sdirk_second(&first, b.state, &ab, &pb)
            .map_err(|e| format!("step {i} stage2: {e:?}"))?;
        y = next;
        old = b;
        println!(
            "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{}\t{:.17e}\t{:.17e}",
            b.eta,
            y.xp(),
            y.x_heii,
            y.x_heiii,
            y.xe(),
            y.tm(f),
            y.xe() - b.state.xe(),
            y.tm(f) - b.state.tm(f),
            d.iterations,
            d.scaled_residual,
            d.thermal_balance_defect_j_per_h
        );
    }
    Ok(())
}
