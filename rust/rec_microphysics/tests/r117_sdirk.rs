use rec_microphysics::anisotropic::DirectionalSky;
use rec_microphysics::species_thermal::{
    HeliumModel, KB_J_K, Point, SDIRK_GAMMA, State, sdirk_first, sdirk_second,
};
fn point(theta: f64) -> Point {
    Point::new(
        &DirectionalSky {
            weights: &[1.],
            temperature_k: &[0.1],
            expansion_factor: &[1.],
        },
        1.,
        1e-12,
        1.,
        theta,
        0.,
        HeliumModel::NeutralHelium,
    )
    .unwrap()
}
#[test]
fn matched_reference_exact_and_stage_binding() {
    let f = 0.08;
    let a = State::from_xp_tm(0.4, 0., 0., 100., f).unwrap();
    let m = State::from_xp_tm(0.39, 0., 0., 98., f).unwrap();
    let b = State::from_xp_tm(0.38, 0., 0., 95., f).unwrap();
    let p = point(3.);
    let s = sdirk_first(a, a, m, 0.01, f, &p, &p).unwrap();
    assert_eq!(s.state(), m);
    let (out, diag) = sdirk_second(&s, b, &p, &p).unwrap();
    assert_eq!(out, b);
    assert!(diag.thermal_balance_defect_j_per_h.abs() < 1e-28);
}
#[test]
fn adiabatic_scalar_stability_order_and_stiff_limit() {
    let f = 0.;
    let r = State::from_xp_tm(0., 0., 0., 100., f).unwrap();
    let p = point(2.7);
    let q = point(0.);
    let mut errs = vec![];
    for n in [8, 16, 32, 64] {
        let h = 1. / n as f64;
        let mut y = r;
        for _ in 0..n {
            let a = sdirk_first(y, r, r, h, f, &p, &q).unwrap();
            let (b, d) = sdirk_second(&a, r, &p, &q).unwrap();
            assert!(d.thermal_balance_defect_j_per_h.abs() < 1e-28);
            assert_eq!(b.xe(), 0.);
            y = b;
        }
        let z = -1.8 * h;
        let g = SDIRK_GAMMA;
        let amp = (1. + (1. - 2. * g) * z) / (1. - g * z).powi(2);
        assert!((y.w_k - r.w_k * amp.powi(n)).abs() < 1e-10);
        errs.push((y.w_k - r.w_k * (-1.8f64).exp()).abs());
    }
    eprintln!("SDIRK adiabatic errors {:?}", errs);
    assert!(
        errs.windows(2)
            .all(|x| x[0] / x[1] > 3.8 && x[0] / x[1] < 4.3)
    );
    // Stiff pure decay may produce negative SDIRK state; reject rather than
    // clip or mislabel L stability as positivity.
    let p = point(150.);
    let a = sdirk_first(r, r, r, 1., f, &p, &q).unwrap();
    assert!(sdirk_second(&a, r, &p, &q).is_err());
}
#[test]
fn tiny_heat_response_retained() {
    let r = State::from_xp_tm(0., 0., 0., 100., 0.).unwrap();
    let q = point(0.);
    let p = Point::new(
        &DirectionalSky {
            weights: &[1.],
            temperature_k: &[0.1],
            expansion_factor: &[1.],
        },
        1.,
        1e-12,
        1.,
        0.,
        1.5 * KB_J_K * 1e-12 * 1e-9,
        HeliumModel::NeutralHelium,
    )
    .unwrap();
    let a = sdirk_first(r, r, r, 0.1, 0., &p, &q).unwrap();
    let (b, _) = sdirk_second(&a, r, &p, &q).unwrap();
    assert!((b.w_k - r.w_k - 1e-10).abs() < 3e-14);
}

#[test]
fn stiff_non_autonomous_thermal_reference() {
    let r = State::from_xp_tm(0., 0., 0., 100., 0.).unwrap();
    let q = point(0.);
    let p = |t: f64| {
        Point::new(
            &DirectionalSky {
                weights: &[1.],
                temperature_k: &[0.1],
                expansion_factor: &[1.],
            },
            1.,
            1e-12,
            1.,
            180.,
            1.5 * KB_J_K * 1e-12 * (120. * (100. + (2. * t).sin()) + 2. * (2. * t).cos()),
            HeliumModel::NeutralHelium,
        )
        .unwrap()
    };
    let mut errs = vec![];
    for n in [64, 128, 256, 512] {
        let h = 1. / n as f64;
        let mut y = r;
        for i in 0..n {
            let a = sdirk_first(y, r, r, h, 0., &p((i as f64 + SDIRK_GAMMA) * h), &q).unwrap();
            let (b, _) = sdirk_second(&a, r, &p((i + 1) as f64 * h), &q).unwrap();
            y = b;
        }
        errs.push((y.w_k - 100. - 2f64.sin()).abs());
    }
    eprintln!("nonautonomous stiff thermal errors {errs:?}");
    assert!(
        errs.windows(2)
            .all(|w| w[0] / w[1] > 3.6 && w[0] / w[1] < 4.4)
    );
}
