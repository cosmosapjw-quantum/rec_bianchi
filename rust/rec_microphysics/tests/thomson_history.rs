use rec_microphysics::thomson_history::*;

const X: [f64; 3] = [1., 0., 0.];
const ZERO: [f64; 3] = [0.; 3];

fn state(t: f64, n: f64, x: f64, b: f64, e: [f64; 3]) -> RaySample {
    RaySample::new(t, n, x, [b, 0., 0.], e).unwrap()
}
fn close(x: f64, y: f64, tol: f64) {
    assert!(
        (x - y).abs() <= tol * y.abs().max(1e-300),
        "{x:e} versus {y:e}"
    );
}
#[test]
fn moving_slab_charge_count_and_reversal() {
    let ne = 40. + 5. + 2. * 9.;
    let p = RaySample::from_ion_densities(0., 80., [40., 5., 9.], [0.6, 0., 0.], X).unwrap();
    close(
        p.normal_rate_per_s().unwrap(),
        C_SIGMA_T_M3_S * ne * 0.5,
        2e-15,
    );
    for (e, expected) in [(X, 0.5), ([-1., 0., 0.], 2.), ([0., 1., 0.], 1.25)] {
        let pts = [
            state(7., 80., ne / 80., 0.6, e),
            state(10., 80., ne / 80., 0.6, e),
        ];
        let b = integrate(&pts).unwrap()[0];
        close(b.delta_tau, C_SIGMA_T_M3_S * ne * expected * 3., 2e-15);
        close(b.visibility_mass, b.delta_tau, 2e-15);
        assert!(b.visibility_mass > 0. && b.tau_near == 0.);
    }
    assert!(RaySample::from_ion_densities(0., 1., [2., 0., 0.], ZERO, X).is_err());
}
#[test]
fn expanding_contracting_and_opaque_bins() {
    let a = state(0., 1e19, 0.2, 0., X);
    let b = state(1., 1e19 / f64::exp(2.), 0.9, 0., X);
    let rev = [
        state(0., 1e19 / f64::exp(2.), 0.9, 0., X),
        state(1., 1e19, 0.2, 0., X),
    ];
    let expect = C_SIGMA_T_M3_S
        * 1e19
        * (0.2 * (1. - f64::exp(-2.)) / 2. + 0.7 * (1. - 3. * f64::exp(-2.)) / 4.);
    for h in [[a, b], rev] {
        close(integrate(&h).unwrap()[0].delta_tau, expect, 2e-15);
    }
    let h = [
        state(0., 1., 1., 0., X),
        state(1., 1., 1., 0., X),
        state(2., 1., 1e24, 0., X),
    ];
    let v = integrate(&h).unwrap();
    assert!(v[0].delta_tau > 0. && v[0].visibility_mass == 0.);
    assert_eq!(v[1].visibility_mass, 1.);
    let none = integrate(&[state(0., 1., 0., 0., X), state(1., 1., 0., 0., X)]).unwrap()[0];
    assert_eq!(none.visibility_mass, 0.);
    assert_eq!(none.survival_near, 1.);
}
#[test]
fn cell_subdivision_telescope_and_input_validation() {
    let h0 = state(0., 1e19, 0.2, 0., X);
    let h1 = state(3., 6e19, 0.8, 0., X);
    let mid = state(1., 1e19 * f64::cbrt(6.), 0.4, 0., X);
    let split = integrate(&[h0, mid, h1]).unwrap();
    let whole = integrate(&[h0, h1]).unwrap()[0];
    close(split[0].tau_far, whole.tau_far, 2e-15);
    close(
        split[0].visibility_mass + split[1].visibility_mass,
        whole.visibility_mass,
        2e-15,
    );
    assert!(integrate(&[h1, h0]).is_err());
    assert!(integrate(&[h0, h0]).is_err());
    assert!(integrate(&[h0]).is_err());
    assert!(RaySample::new(0., 0., 1., ZERO, X).is_err());
    assert!(RaySample::new(0., 1., -1., ZERO, X).is_err());
    assert!(RaySample::new(0., 1., 1., X, X).is_err());
    assert!(RaySample::new(0., 1., 1., ZERO, [0., 0., 0.]).is_err());
}
#[test]
fn full_tangent_matches_independent_finite_differences() {
    // Independent perturbation of n_H, x_e, beta, and a rotating null direction
    // at each endpoint; perturb both earlier and later bins.
    let amp = [0.03, -0.08, 0.12];
    let dx = [0.03, 0.1, -0.05];
    let db = [0.11, -0.07, 0.1];
    let angle = [0.1, 0.8, 0.7];
    let w = [-0.2, 0.14, 0.2];
    let n = [1e19, 4e19, 2e19];
    let samples = |h: f64| {
        (0..3)
            .map(|i| {
                let phi: f64 = angle[i] + h * w[i];
                RaySample::new(
                    i as f64,
                    n[i] * (h * amp[i]).exp(),
                    0.55 + h * dx[i],
                    [0.1 + h * db[i], 0.15, 0.03],
                    [phi.cos(), phi.sin(), 0.],
                )
                .unwrap()
            })
            .collect::<Vec<_>>()
    };
    let tangent = (0..3)
        .map(|i| RayTangent {
            d_ln_reference: amp[i],
            d_electrons_per_reference: dx[i],
            d_beta: [db[i], 0., 0.],
            d_direction: [-angle[i].sin() * w[i], angle[i].cos() * w[i], 0.],
        })
        .collect::<Vec<_>>();
    let (bins, d) = integrate_tangent(&samples(0.), &tangent).unwrap();
    let h = 1e-5;
    let hi = integrate(&samples(h)).unwrap();
    let lo = integrate(&samples(-h)).unwrap();
    for i in 0..2 {
        close(
            d[i].d_delta_tau,
            (hi[i].delta_tau - lo[i].delta_tau) / (2. * h),
            1e-8,
        );
        close(
            d[i].d_visibility_mass,
            (hi[i].visibility_mass - lo[i].visibility_mass) / (2. * h),
            1e-8,
        );
        close(
            d[i].d_tau_far,
            (hi[i].tau_far - lo[i].tau_far) / (2. * h),
            1e-8,
        );
    }
    let d_sum = d.iter().map(|s| s.d_visibility_mass).sum::<f64>();
    close(d_sum, (-bins[0].tau_far).exp() * d[0].d_tau_far, 2e-15);
    let mut invalid = tangent.clone();
    invalid[0].d_direction = [1., 0., 0.];
    assert!(integrate_tangent(&samples(0.), &invalid).is_err());
}

#[test]
fn long_clock_with_small_density_keeps_representable_exposure() {
    let s = [
        state(0., 1e-310, 1., 0., X),
        state(1e300, 1e-310, 1., 0., X),
    ];
    close(
        integrate(&s).unwrap()[0].delta_tau,
        C_SIGMA_T_M3_S * 1e-10,
        5e-14,
    );
}
