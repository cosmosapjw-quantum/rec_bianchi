//! Independent reduced thermochemistry on a prescribed density-fixed
//! LRS Bianchi-I background. Neutral He; collisionless Planck rays;
//! H TLA + W thermal source. No HyRec reference history or BASS.
use rec_microphysics::{
    anisotropic::DirectionalSky,
    hydrogen_peebles::{HYREC_EI_EV, HYREC_KB_EV_K, HYREC_SAHA_PER_CM3_EV32},
    species_thermal::{HeliumModel, Point, State, standalone_step},
};
use std::env;
fn main() -> Result<(), String> {
    let a = env::args().skip(1).collect::<Vec<_>>();
    if a.len() != 4 {
        return Err("usage rec_owned_history Z_START Z_END STEPS SHEAR_S_OVER_HFLRW_START".into());
    }
    let z0: f64 = a[0].parse().map_err(|_| "z0")?;
    let z1: f64 = a[1].parse().map_err(|_| "z1")?;
    let nt: usize = a[2].parse().map_err(|_| "steps")?;
    let s0: f64 = a[3].parse().map_err(|_| "shear")?;
    if !(900. <= z1 && z1 < z0 && z0 <= 1600. && nt > 0 && nt <= 65536 && s0.abs() <= 0.02) {
        return Err("outside bounded H-only tracer domain".into());
    }
    let tcmb = 2.7255_f64;
    let fhe = 0.2454 / ((1. - 0.2454) * 3.97153);
    let om = 0.14309694000000003;
    let od = 0.31113726660800006;
    let or = 4.48162687719e-7 * tcmb.powi(4) * (1. + 0.227107317660239 * 3.03821934419124);
    let n0 = 11.223846333047 * 0.0224 * (1. - 0.2454);
    let flrw = |a1: f64| 3.2407792896393e-18 * (om * a1.powi(3) + or * a1.powi(4) + od).sqrt();
    let hs0 = s0 * flrw(1. + z0);
    let point = |eta: f64| {
        let a1 = (1. + z0) * (-eta).exp();
        let s = hs0 * (-3. * eta).exp();
        let h = flrw(a1).hypot(s);
        (a1 - 1., h, s, n0 * a1.powi(3), tcmb * a1)
    };
    let (_, _, _, n, tr) = point(0.);
    let t = HYREC_KB_EV_K * tr;
    let saha = HYREC_SAHA_PER_CM3_EV32 * t.powf(1.5) * (-HYREC_EI_EV / t).exp() / (n * 1e-6);
    let xp = 2. / (1. + (1. + 4. / saha).sqrt());
    let mut state = State::from_xp_tm(xp, 0., 0., tr, fhe).map_err(|e| format!("{e:?}"))?;
    let dt = ((1. + z0) / (1. + z1)).ln() / nt as f64;
    // Midpoint mu rule, symmetric under reversal, 32 positive ordinates.
    let nm = 32;
    let mu: Vec<_> = (0..nm)
        .map(|i| -1. + 2. * (i as f64 + 0.5) / nm as f64)
        .collect();
    let w = vec![1. / nm as f64; nm];
    let mut b = 0.;
    println!(
        "eta\tz\tH_s\ts_over_H\tb\tx_HII\tx_HI\tT_m_K\tT_r_K\tn_H_m3\tT_min_K\tT_max_K\titerations\tresidual\tthermal_defect_j_per_H\tmatched_correction_j_per_H"
    );
    for i in 0..=nt {
        let eta = i as f64 * dt;
        let (z, h, s, n, tr) = point(eta);
        if i > 0 {
            let (_, hl, sl, _, _) = point(eta - dt);
            let (_, hm, sm, _, _) = point(eta - dt / 2.);
            b += dt * (sl / hl + 4. * sm / hm + s / h) / 6.;
        }
        let temp: Vec<_> = mu
            .iter()
            .map(|m| tr / (((-4. * b).exp() * m * m + (2. * b).exp() * (1. - m * m)).sqrt()))
            .collect();
        let exp: Vec<_> = mu.iter().map(|m| 1. + s / h * (1. - 3. * m * m)).collect();
        let p = Point::new(
            &DirectionalSky {
                weights: &w,
                temperature_k: &temp,
                expansion_factor: &exp,
            },
            n,
            h,
            1.,
            3.,
            0.,
            HeliumModel::NeutralHelium,
        )
        .map_err(|e| format!("{e:?}"))?;
        let d = if i == 0 {
            Default::default()
        } else {
            let (q, d) = standalone_step(state, dt, fhe, &p).map_err(|e| format!("i={i} {e:?}"))?;
            state = q;
            d
        };
        println!(
            "{eta:.17e}\t{z:.17e}\t{h:.17e}\t{:.17e}\t{b:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{tr:.17e}\t{n:.17e}\t{:.17e}\t{:.17e}\t{}\t{:.17e}\t{:.17e}\t{:.17e}",
            s / h,
            state.xp(),
            state.x_hi,
            state.tm(fhe),
            temp.iter().copied().fold(f64::INFINITY, f64::min),
            temp.iter().copied().fold(0., f64::max),
            d.iterations,
            d.scaled_residual,
            d.thermal_balance_defect_j_per_h,
            d.matched_thermal_correction_j_per_h
        );
    }
    Ok(())
}
