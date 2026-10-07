use rec_microphysics::coverage::CoverageError;
use rec_microphysics::frame::{MaterialVelocity, NormalFourForce};
use rec_microphysics::he_singlet::{C_M_S, Complex64, Mat2, Mat3};
use rec_microphysics::ledger::MaterialFourForce;

fn close(actual: f64, expected: f64, tolerance: f64) {
    assert!(
        expected != 0.0 && (actual - expected).abs() <= tolerance * expected.abs(),
        "{actual} != {expected}"
    );
}
fn close_zero(actual: f64, gross_scale: f64, tolerance: f64) {
    assert!(gross_scale > 0.0 && gross_scale.is_finite());
    assert!(
        actual.abs() <= tolerance * gross_scale,
        "{actual} is not zero at gross scale {gross_scale}"
    );
}
fn c(re: f64, im: f64) -> Complex64 {
    Complex64::new(re, im)
}
fn norm4(q: [f64; 4]) -> f64 {
    -q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]
}

#[test]
fn zero_tilt_is_identity_and_clocks_agree() {
    let v = MaterialVelocity::new([0.0; 3]).unwrap();
    let ray = v.normal_to_material_ray(21.0, [0.0, 1.0, 0.0]).unwrap();
    assert_eq!(ray.energy_material_ev(), 21.0);
    assert_eq!(ray.direction_material(), [0.0, 1.0, 0.0]);
    assert_eq!(ray.doppler(), 1.0);
    assert_eq!(v.scalar_source_normal_time(7.0, 2.0, 3.0).unwrap(), 1.0);
    let f = Mat2([[c(2.0, 1.0); 2]; 2]);
    assert_eq!(ray.normal_time_after_screen_map(f).unwrap(), f);
    close(
        ray.normal_length_after_screen_map(f).unwrap()[0][0].re,
        2.0 / C_M_S,
        1e-15,
    );
    assert_eq!(
        v.normal_to_material_four_vector([-3.0, 1.0, 2.0, 4.0])
            .unwrap(),
        [-3.0, 1.0, 2.0, 4.0]
    );
}

#[test]
fn analytic_parallel_antiparallel_and_oblique_rays() {
    let v = MaterialVelocity::new([0.6, 0.0, 0.0]).unwrap();
    close(v.gamma(), 1.25, 1e-15);
    let aligned = v.normal_to_material_ray(12.0, [1.0, 0.0, 0.0]).unwrap();
    let opposed = v.normal_to_material_ray(8.0, [-1.0, 0.0, 0.0]).unwrap();
    let transverse = v.normal_to_material_ray(10.0, [0.0, 1.0, 0.0]).unwrap();
    close(aligned.doppler(), 0.5, 1e-15);
    close(opposed.doppler(), 2.0, 1e-15);
    close(transverse.doppler(), 1.25, 1e-15);
    close(aligned.energy_material_ev(), 6.0, 1e-15);
    close(opposed.energy_material_ev(), 16.0, 1e-15);
    close(transverse.direction_material()[0], -0.6, 1e-15);
    close(transverse.direction_material()[1], 0.8, 1e-15);
    close(aligned.direction_material()[0], 1.0, 1e-15);
    close(opposed.direction_material()[0], -1.0, 1e-15);
    let oblique = v.normal_to_material_ray(10.0, [0.6, 0.8, 0.0]).unwrap();
    close(oblique.doppler(), 0.8, 1e-15);
    close_zero(oblique.direction_material()[0], 1.0, 1e-15);
    close(oblique.direction_material()[1], 1.0, 1e-15);
}

#[test]
fn ray_and_worldline_factors_scale_distinct_sources() {
    let v = MaterialVelocity::new([0.6, 0.0, 0.0]).unwrap();
    let ray = v.normal_to_material_ray(10.0, [1.0, 0.0, 0.0]).unwrap();
    close(
        v.scalar_source_normal_time(7.0, 2.0, 3.0).unwrap(),
        0.8,
        1e-15,
    );
    let orbital = Mat3([[c(2.0, -4.0); 3]; 3]);
    let scaled = v.orbital_collision_normal_time(orbital).unwrap();
    close(scaled[1][2].re, 1.6, 1e-15);
    close(scaled[1][2].im, -3.2, 1e-15);
    let mapped = Mat2([[c(-2.0, 3.0); 2]; 2]);
    let normal = ray.normal_time_after_screen_map(mapped).unwrap();
    close(normal[0][0].re, -1.0, 1e-15);
    close(normal[0][0].im, 1.5, 1e-15);
    close(
        ray.normal_length_after_screen_map(mapped).unwrap()[0][0].re,
        -1.0 / C_M_S,
        1e-15,
    );
    assert_ne!(normal[0][0].re, scaled[0][0].re);
}

#[test]
fn sharp_line_delta_factor_is_separate_and_pair_uses_each_ray() {
    let v = MaterialVelocity::new([0.6, 0.0, 0.0]).unwrap();
    let a = v.normal_to_material_ray(12.0, [1.0, 0.0, 0.0]).unwrap();
    let b = v.normal_to_material_ray(8.0, [-1.0, 0.0, 0.0]).unwrap();
    close(a.sharp_line_normal_energy_ev(20.0).unwrap(), 40.0, 1e-15);
    close(a.sharp_line_delta_jacobian().unwrap(), 2.0, 1e-15);
    let mapped_amplitude = Mat2([[c(3.0, 0.0); 2]; 2]);
    let smooth_clock_scaled = a.normal_time_after_screen_map(mapped_amplitude).unwrap()[0][0].re;
    close(smooth_clock_scaled, 1.5, 1e-15);
    close(
        smooth_clock_scaled * a.sharp_line_delta_jacobian().unwrap(),
        3.0,
        1e-15,
    );
    close(
        a.energy_material_ev() + b.energy_material_ev(),
        a.doppler() * 12.0 + b.doppler() * 8.0,
        1e-15,
    );
    assert_ne!(a.energy_material_ev() + b.energy_material_ev(), 12.0 + 8.0);
}

#[test]
fn signed_four_vectors_roundtrip_preserve_metric_and_balance() {
    let v = MaterialVelocity::new([0.3, -0.4, 0.2]).unwrap();
    for q in [
        [5.0, 2.0, -1.0, 3.0],
        [-5.0, -2.0, 1.0, -3.0],
        [0.0, 1.0, 2.0, -4.0],
    ] {
        let m = v.normal_to_material_four_vector(q).unwrap();
        let recovered = v.material_to_normal_four_vector(m).unwrap();
        for k in 0..4 {
            if q[k] == 0.0 {
                close_zero(
                    recovered[k],
                    q.iter().map(|x| x.abs()).fold(0.0, f64::max),
                    1e-14,
                );
            } else {
                close(recovered[k], q[k], 1e-14);
            }
        }
        close(norm4(m), norm4(q), 1e-14);
    }
    let x = MaterialVelocity::new([0.6, 0.0, 0.0]).unwrap();
    let force = MaterialFourForce {
        q_photon: [10.0, 2.0, 3.0, 0.0],
        q_matter: [-10.0, -2.0, -3.0, 0.0],
    };
    let normal: NormalFourForce = x.material_four_force_to_normal(force).unwrap();
    close(normal.q_photon[0], 14.0, 1e-15);
    close(normal.q_photon[1], 10.0, 1e-15);
    close(normal.q_photon[2], 3.0, 1e-15);
    for k in 0..4 {
        close_zero(normal.q_photon[k] + normal.q_matter[k], 14.0, 1e-15);
    }
}

#[test]
fn invalid_nonfinite_and_underflow_are_typed_not_zero() {
    assert!(matches!(
        MaterialVelocity::new([1.0, 0.0, 0.0]),
        Err(CoverageError::InvalidInput(_))
    ));
    assert!(matches!(
        MaterialVelocity::new([f64::NAN, 0.0, 0.0]),
        Err(CoverageError::InvalidInput(_))
    ));
    let v = MaterialVelocity::new([0.6, 0.0, 0.0]).unwrap();
    assert!(matches!(
        v.normal_to_material_ray(0.0, [1.0, 0.0, 0.0]),
        Err(CoverageError::InvalidInput(_))
    ));
    assert!(matches!(
        v.normal_to_material_ray(1.0, [2.0, 0.0, 0.0]),
        Err(CoverageError::InvalidInput(_))
    ));
    assert!(matches!(
        v.normal_to_material_ray(f64::INFINITY, [1.0, 0.0, 0.0]),
        Err(CoverageError::InvalidInput(_))
    ));
    assert!(matches!(
        v.normal_to_material_ray(f64::MAX, [-1.0, 0.0, 0.0]),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    assert!(matches!(
        v.scalar_source_normal_time(1.0, f64::MAX, 2.0),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    assert!(matches!(
        v.normal_to_material_four_vector([f64::MAX, 0.0, 0.0, 0.0]),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    assert!(matches!(
        v.scalar_source_normal_time(1.0, 0.0, -1.0),
        Err(CoverageError::InvalidInput(_))
    ));
    let ray = v.normal_to_material_ray(1.0, [1.0, 0.0, 0.0]).unwrap();
    assert!(matches!(
        ray.normal_time_after_screen_map(Mat2([[c(f64::MAX, 0.0); 2]; 2])),
        Ok(_)
    ));
    let opposite = v.normal_to_material_ray(1.0, [-1.0, 0.0, 0.0]).unwrap();
    assert!(matches!(
        opposite.normal_time_after_screen_map(Mat2([[c(f64::MAX, 0.0); 2]; 2])),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    assert!(matches!(
        ray.normal_time_after_screen_map(Mat2([[c(f64::NAN, 0.0); 2]; 2])),
        Err(CoverageError::InvalidInput(_))
    ));
    assert!(matches!(
        ray.normal_time_after_screen_map(Mat2([[c(f64::MIN_POSITIVE / 4.0, 0.0); 2]; 2])),
        Ok(_)
    ));
    let tiny = MaterialVelocity::new([0.0, 0.0, 0.0])
        .unwrap()
        .normal_to_material_ray(1.0, [1.0, 0.0, 0.0])
        .unwrap();
    assert!(matches!(
        tiny.normal_length_after_screen_map(Mat2([[c(f64::from_bits(1), 0.0); 2]; 2])),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    assert!(matches!(
        ray.sharp_line_normal_energy_ev(-1.0),
        Err(CoverageError::InvalidInput(_))
    ));
}

#[test]
fn tiny_beta_retains_linear_spatial_boost() {
    let v = MaterialVelocity::new([1e-160, 0.0, 0.0]).unwrap();
    let m = v
        .normal_to_material_four_vector([1.0, 0.0, 0.0, 0.0])
        .unwrap();
    assert_eq!(m[0], 1.0);
    close(m[1] / 1e-160, -1.0, 1e-15);
}

#[test]
fn review_counterexamples_reject_inaccurate_finite_arithmetic() {
    // Exact binary64 inputs used by the independent reviewer: rounded hypot
    // previously admitted gamma=67108864 instead of approximately 56717342.
    assert!(matches!(
        MaterialVelocity::new([0.6, 0.7999999999999998, 0.0]),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    let v = MaterialVelocity::new([0.6, 0.0, 0.0]).unwrap();
    assert!(matches!(
        v.normal_to_material_four_vector([f64::from_bits(3), 0.0, 0.0, 0.0]),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    let parallel = v.normal_to_material_ray(1.0, [1.0, 0.0, 0.0]).unwrap();
    let opposite = v.normal_to_material_ray(1.0, [-1.0, 0.0, 0.0]).unwrap();
    let lossy = Mat2([[c(f64::from_bits(3), 0.0); 2]; 2]);
    assert!(matches!(
        parallel.normal_time_after_screen_map(lossy),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    assert!(matches!(
        opposite.sharp_line_normal_energy_ev(f64::from_bits(3)),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));
    // Exactly representable subnormal operations remain usable.
    let exact = Mat2([[c(f64::from_bits(4), 0.0); 2]; 2]);
    assert_eq!(
        parallel.normal_time_after_screen_map(exact).unwrap()[0][0]
            .re
            .to_bits(),
        2
    );
    assert_eq!(
        opposite
            .sharp_line_normal_energy_ev(f64::from_bits(4))
            .unwrap()
            .to_bits(),
        2
    );
}
