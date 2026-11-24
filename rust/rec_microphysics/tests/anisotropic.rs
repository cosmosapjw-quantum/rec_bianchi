//! BASS R110 THEORY D8 checks for the anisotropic effective-atom source.
use rec_microphysics::anisotropic::{
    AnisotropyError, DirectionalSky, anisotropic_one_temperature_source, compton_temperature_k,
    escape_rate_factor, sobolev_escape_average, wien_average_ln,
};
use rec_microphysics::hydrogen_peebles::{
    HYREC_E21_EV, HYREC_KB_EV_K, RetainedState, hyrec2_one_temperature_source,
};
use std::f64::consts::PI;

/// Gauss-Legendre (cos theta) x uniform phi directions and weights.
fn sphere(nmu: usize, nphi: usize) -> (Vec<[f64; 3]>, Vec<f64>) {
    let mut x = vec![0.0; nmu];
    let mut w = vec![0.0; nmu];
    for i in 0..nmu {
        let mut z = (PI * (i as f64 + 0.75) / (nmu as f64 + 0.5)).cos();
        for _ in 0..100 {
            let (mut p0, mut p1) = (1.0f64, 0.0f64);
            for j in 0..nmu {
                let p2 = p1;
                p1 = p0;
                p0 = ((2.0 * j as f64 + 1.0) * z * p1 - j as f64 * p2) / (j as f64 + 1.0);
            }
            let dp = nmu as f64 * (z * p0 - p1) / (z * z - 1.0);
            let dz = p0 / dp;
            z -= dz;
            if dz.abs() < 1e-16 {
                x[i] = z;
                w[i] = 2.0 / ((1.0 - z * z) * dp * dp);
                break;
            }
        }
    }
    let mut dirs = Vec::new();
    let mut weights = Vec::new();
    for (zi, wi) in x.iter().zip(&w) {
        let s = (1.0 - zi * zi).sqrt();
        for k in 0..nphi {
            let phi = 2.0 * PI * k as f64 / nphi as f64;
            dirs.push([s * phi.cos(), s * phi.sin(), *zi]);
            weights.push(wi * 2.0 * PI / nphi as f64);
        }
    }
    (dirs, weights)
}

/// Trace-free symmetric shear with eigenvalues (0.6, -0.25, -0.35) in a rotated basis.
fn rate_factors(dirs: &[[f64; 3]]) -> Vec<f64> {
    let (c, s) = (0.6f64.cos(), 0.6f64.sin());
    let r = [[c, -s, 0.0], [s * 0.8, c * 0.8, 0.6], [-s * 0.6, -c * 0.6, 0.8]];
    let lam = [0.6, -0.25, -0.35];
    dirs.iter()
        .map(|e| {
            let mut q = 0.0;
            for k in 0..3 {
                let proj: f64 = (0..3).map(|i| r[k][i] * e[i]).sum();
                q += lam[k] * proj * proj;
            }
            1.0 + q
        })
        .collect()
}

#[test]
fn isotropic_sky_reproduces_the_hyrec2_tla_source() {
    let (dirs, w) = sphere(12, 24);
    let t = vec![3000.0; dirs.len()];
    let f = vec![1.0; dirs.len()];
    let sky = DirectionalSky { weights: &w, temperature_k: &t, expansion_factor: &f };
    let state = RetainedState { xp: 0.1, x2: 0.0 };
    let iso = hyrec2_one_temperature_source(3000.0, 3000.0, 250e6, 5e-14, state).unwrap();
    let ani = anisotropic_one_temperature_source(&sky, 250e6, 5e-14, state).unwrap();
    let rel = |a: f64, b: f64| ((a - b) / b).abs();
    assert!(rel(ani.matter_temperature_k, 3000.0) < 1e-12, "{}", ani.matter_temperature_k);
    assert!(rel(ani.alpha_b_m3_s, iso.alpha_b_m3_s) < 1e-11);
    assert!(rel(ani.beta_p_s, iso.rates.beta_p_s()) < 1e-13);
    assert!(rel(ani.boltzmann_lya, iso.rates.boltzmann_lya()) < 1e-13);
    // Optically thick Sobolev: tau0 = A/r_alpha >> 1, correction exp(-tau0).
    assert!(ani.sobolev_depth > 1e6);
    assert!(rel(ani.r_alpha_s, iso.r_alpha_s) < 1e-13);
    assert!(rel(ani.rates.c_factor(), iso.rates.c_factor()) < 1e-12);
}

#[test]
fn shear_cancels_from_the_thick_escape_rate_to_all_orders() {
    let (dirs, w) = sphere(24, 48);
    let f = rate_factors(&dirs);
    let t = vec![3000.0; dirs.len()];
    let sky = DirectionalSky { weights: &w, temperature_k: &t, expansion_factor: &f };
    for tau0 in [1e3, 1e6, 1e9] {
        let factor = escape_rate_factor(tau0, &sky).unwrap();
        assert!((factor - 1.0).abs() < 1e-13, "tau0 {tau0}: {factor}");
        let p = sobolev_escape_average(tau0, &sky).unwrap();
        assert!((p * tau0 - 1.0).abs() < 1e-12);
    }
    // Finite depth: identity P = <f>/tau0 - <e^-tau/tau> against the direct average.
    for tau0 in [0.05, 0.7, 4.0] {
        let p = sobolev_escape_average(tau0, &sky).unwrap();
        let factor = escape_rate_factor(tau0, &sky).unwrap();
        assert!((p * tau0 - factor).abs() < 1e-13 * (1.0 + factor), "{p} {factor}");
        assert!(factor < 1.0);
    }
}

#[test]
fn directional_wien_average_shows_the_jensen_amplification() {
    let (dirs, w) = sphere(32, 64);
    let tbar = 3000.0;
    let x = HYREC_E21_EV / (HYREC_KB_EV_K * tbar);
    let f = vec![1.0; dirs.len()];
    for amp in [1e-3, 1e-2, 1e-1] {
        // Zero-mean quadrupolar temperature pattern.
        let raw: Vec<f64> = dirs.iter().map(|e| amp * (3.0 * e[2] * e[2] - 1.0) / 2.0).collect();
        let mean = raw.iter().zip(&w).map(|(d, w)| d * w).sum::<f64>() / (4.0 * PI);
        let delta: Vec<f64> = raw.iter().map(|d| d - mean).collect();
        let t: Vec<f64> = delta.iter().map(|d| tbar * (1.0 + d)).collect();
        let sky = DirectionalSky { weights: &w, temperature_k: &t, expansion_factor: &f };
        let ratio = (wien_average_ln(HYREC_E21_EV, &sky, false).unwrap() + x).exp() - 1.0;
        let d2 = delta.iter().zip(&w).map(|(d, w)| d * d * w).sum::<f64>() / (4.0 * PI);
        let second = (x * x / 2.0 - x) * d2;
        assert!(ratio > 0.0, "Jensen: hot directions dominate the Wien tail");
        if amp <= 1e-3 {
            assert!(((ratio - second) / second).abs() < 1e-2, "{ratio} {second}");
        }
        if amp >= 1e-1 {
            assert!((ratio - second) / second > 0.2, "nonperturbative excess {ratio} {second}");
        }
        let tc = compton_temperature_k(&sky).unwrap();
        let (lo, hi) = t.iter().fold((f64::INFINITY, 0f64), |(a, b), v| (a.min(*v), b.max(*v)));
        assert!(tc > lo && tc < hi);
    }
}

#[test]
fn contracting_or_invalid_directions_fail_closed() {
    let (dirs, w) = sphere(6, 12);
    let t = vec![3000.0; dirs.len()];
    let mut f = vec![1.0; dirs.len()];
    f[3] = -0.01;
    let sky = DirectionalSky { weights: &w, temperature_k: &t, expansion_factor: &f };
    assert_eq!(sobolev_escape_average(1e6, &sky), Err(AnisotropyError::ContractingDirection));
    let f = vec![1.0; dirs.len()];
    let mut bad_t = t.clone();
    bad_t[0] = 0.0;
    let sky = DirectionalSky { weights: &w, temperature_k: &bad_t, expansion_factor: &f };
    assert_eq!(compton_temperature_k(&sky), Err(AnisotropyError::NonPositiveTemperature));
    let short = DirectionalSky { weights: &w[1..], temperature_k: &t, expansion_factor: &f };
    assert_eq!(short.validate(), Err(AnisotropyError::Shape));
}

#[test]
fn thin_sobolev_escape_rate_factor_has_no_cancellation() {
    let (dirs, w) = sphere(16, 32);
    let f = rate_factors(&dirs);
    let t = vec![3000.0; dirs.len()];
    let sky = DirectionalSky { weights: &w, temperature_k: &t, expansion_factor: &f };
    for tau0 in [1e-12, 1e-8, 1e-4, 0.5] {
        let factor = escape_rate_factor(tau0, &sky).unwrap();
        let expected = tau0 * sobolev_escape_average(tau0, &sky).unwrap();
        assert!(factor > 0.0 && factor < tau0);
        assert!(((factor - expected) / expected).abs() < 1e-14, "tau0={tau0}: {factor} vs {expected}");
    }
}
