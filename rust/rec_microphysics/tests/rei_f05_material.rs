use rec_microphysics::rei_f05_material::{
    C_CM_PER_S, ElectronSign, SIGMA_T_CM2, SourceCell, aggregate_original_material,
    evaluate_source_cell, source_volume_cm3,
};

fn cell(weight: f64) -> SourceCell {
    let p = [8.0, 2.0, 1.0, 0.5, 0.5];
    SourceCell {
        weight,
        initial: p,
        accepted_lower: [8.0, 1.8, 0.9, 0.4, 0.4],
        accepted_upper: [8.3, 2.0, 1.1, 0.6, 0.6],
    }
}
fn rel(a: f64, b: f64) -> f64 {
    (a - b).abs() / a.abs().max(b.abs())
}
#[test]
fn original_source_volume_is_positive_and_physical() {
    let v = source_volume_cm3(1.0).unwrap();
    assert!(v > 0.0 && v.is_finite());
    assert!(rel(source_volume_cm3(0.1).unwrap(), v / 10.0) < 1e-15);
    assert!(source_volume_cm3(0.0).is_err());
    assert!(source_volume_cm3(f64::NAN).is_err());
}
#[test]
fn helium_triply_ionized_contributes_two_electrons() {
    let r = evaluate_source_cell(cell(1.0)).unwrap();
    assert_eq!(r.initial_electron_h, 2.0);
    assert_eq!(r.initial_electron_he, 1.5);
    assert_eq!(r.initial_electron, 3.5);
    assert!(
        rel(
            r.gamma_initial_s,
            C_CM_PER_S * SIGMA_T_CM2 * r.initial_electron / r.volume_cm3,
        ) < 1e-15
    );
    assert_eq!(r.sign, ElectronSign::Ambiguous);
}
#[test]
fn genuinely_unphysical_h_or_he_conservation_rejected() {
    let mut r = cell(1.0);
    r.accepted_upper[0] = 5.0; // H total 7 < source H total 10
    assert!(evaluate_source_cell(r).is_err());
    let mut r = cell(1.0);
    r.accepted_lower[3] = -1.0;
    assert!(evaluate_source_cell(r).is_err());
}
#[test]
fn strict_ordering_and_nonfinite_source_fail_closed() {
    let mut r = cell(1.0);
    r.accepted_lower[1] = 4.0;
    assert!(evaluate_source_cell(r).is_err());
    let mut r = cell(1.0);
    r.initial[0] = f64::INFINITY;
    assert!(evaluate_source_cell(r).is_err());
}
#[test]
fn exact_photon_thomson_source_rate_difference_uses_electron_increment() {
    let x = evaluate_source_cell(cell(1.0)).unwrap();
    let delta =
        (x.accepted_electron_lower - x.initial_electron) * C_CM_PER_S * SIGMA_T_CM2 / x.volume_cm3;
    assert!(rel(x.delta_gamma_lower_s, delta) < 1e-15);
    assert!(x.delta_gamma_lower_s < 0.0);
    assert!(x.delta_gamma_upper_s > 0.0);
}
#[test]
fn sign_classes_are_exclusive_and_material_driven() {
    let mut positive = cell(1.0);
    positive.accepted_lower = [7.5, 2.1, 0.8, 0.6, 0.5];
    positive.accepted_upper = [8.1, 2.3, 1.1, 0.8, 0.7];
    let mut negative = cell(1.0);
    negative.accepted_lower = [8.1, 1.7, 1.1, 0.4, 0.3];
    negative.accepted_upper = [8.4, 1.8, 1.2, 0.5, 0.4];
    let p = evaluate_source_cell(positive).unwrap();
    let n = evaluate_source_cell(negative).unwrap();
    assert_eq!(p.sign, ElectronSign::Gain);
    assert_eq!(n.sign, ElectronSign::Loss);
    let a = aggregate_original_material(&[p, n, evaluate_source_cell(cell(1.0)).unwrap()]).unwrap();
    assert_eq!(a.counts, [1, 1, 1]);
    assert_eq!(a.count, 3);
}
#[test]
fn uniform_density_has_clumping_one_even_with_different_cell_volumes() {
    let r1 = cell(1.0);
    let mut r2 = cell(2.0);
    for i in 0..5 {
        r2.initial[i] *= 2.0;
        r2.accepted_lower[i] *= 2.0;
        r2.accepted_upper[i] *= 2.0;
    }
    let a = aggregate_original_material(&[
        evaluate_source_cell(r1).unwrap(),
        evaluate_source_cell(r2).unwrap(),
    ])
    .unwrap();
    assert!(rel(a.initial_clumping, 1.0) < 1e-15);
    assert!(a.accepted_upper_clumping >= 1.0);
}
#[test]
fn aggregate_errors_on_empty_source() {
    assert!(aggregate_original_material(&[]).is_err());
}
