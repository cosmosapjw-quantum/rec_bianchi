use rec_microphysics::live_line::{Hat, Network};
#[test]
fn projected_be_inverse_and_equilibrium() {
    let a = Hat::new(2., vec![0.3, 0.7], vec![1.01, 0.99]).unwrap();
    let b = Hat::new(3., vec![0.4, 0.6], vec![0.98, 1.02]).unwrap();
    for x in [1e-18, 0.1, 0.3, 0.8] {
        let f = a.value(x).unwrap().0;
        assert!((a.inverse(f).unwrap() / x - 1.).abs() < 2e-14);
    }
    let f = [a.value(0.3).unwrap().0, b.value(0.3).unwrap().0];
    let net = Network::new(vec![a, b], vec![-1., 1.], vec![0., 0.5, 0.5, 0.]).unwrap();
    let q = net.step(&f, 1e4).unwrap();
    assert!(q.f.iter().zip(f).all(|(a, b)| (a / b - 1.).abs() < 2e-13));
}
#[test]
fn stiff_be_positive_conservative() {
    let net = Network::new(
        vec![
            Hat::new(2., vec![1.], vec![1.]).unwrap(),
            Hat::new(3., vec![1.], vec![0.99]).unwrap(),
        ],
        vec![-1., 1.],
        vec![0., 1., 1., 0.],
    )
    .unwrap();
    for dt in [1e-6, 0.1, 10., 1e4] {
        let q = net.step(&[0.5, 0.], dt).unwrap();
        assert!(q.f[0] >= 0. && q.f[1] >= 0.);
        assert!((2. * q.f[0] + 3. * q.f[1] - 1.).abs() < 2e-12);
        assert!(q.residual < 2e-10 && q.centered_defect < 2e-10);
    }
}

#[test]
fn unanchored_species_step_uses_only_actual_rhs() {
    use rec_microphysics::{
        anisotropic::DirectionalSky,
        species_thermal::{HeliumModel, Point, State, proper_rate, standalone_step},
    };
    let fhe = 0.08;
    let y = State::from_hi_tm(0.85, 0., 0., 2999.9, fhe).unwrap();
    let p = Point::new(
        &DirectionalSky {
            weights: &[1., 1.],
            temperature_k: &[3000., 3000.],
            expansion_factor: &[0.99, 1.01],
        },
        2.53e8,
        5.15e-14,
        1.,
        3.,
        0.,
        HeliumModel::NeutralHelium,
    )
    .unwrap();
    let h = 1e-5;
    let (q, d) = standalone_step(y, h, fhe, &p).unwrap();
    let r = proper_rate(q, fhe, &p).unwrap();
    assert!((q.x_hi - y.x_hi - h * r.d_x_hi / p.clock_s()).abs() < 1e-12);
    assert!((q.w_k - y.w_k - h * r.d_w_k / p.clock_s()).abs() < 1e-7);
    assert_eq!(d.matched_thermal_correction_j_per_h, 0.);
}

#[test]
fn nonlinear_bose_analytic_jacobian_matches_finite_difference() {
    let hats = vec![
        Hat::new(1.5, vec![0.4, 0.6], vec![0.98, 1.02]).unwrap(),
        Hat::new(2.1, vec![0.2, 0.8], vec![1.01, 0.99]).unwrap(),
        Hat::new(0.9, vec![0.3, 0.7], vec![0.97, 1.03]).unwrap(),
    ];
    let n = Network::new(
        hats,
        vec![-1., 0., 1.],
        vec![0., 0.1, 0.2, 0.1, 0., 0.3, 0.2, 0.3, 0.],
    )
    .unwrap();
    for f in [[0.3, 0.1, 0.8], [2., 5., 1.]] {
        let a = n.action(&f).unwrap();
        for j in 0..3 {
            let h = 1e-5 * f[j];
            let mut x = f;
            let mut y = f;
            x[j] += h;
            y[j] -= h;
            let u = n.action(&x).unwrap();
            let v = n.action(&y).unwrap();
            for i in 0..3 {
                let fd = (u.rate[i] - v.rate[i]) / (2. * h);
                let an = a.jac[3 * i + j];
                assert!(
                    (fd - an).abs() < 1e-9 * an.abs().max(1.),
                    "{i} {j} {fd:e} {an:e}"
                );
            }
        }
        assert!(a.entropy_rate <= 0.);
        let s = n.step(&f, 2.).unwrap();
        assert!(s.free_change <= 1e-14);
    }
}
