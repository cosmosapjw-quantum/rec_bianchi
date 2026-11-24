use rec_microphysics::anisotropic::{
    anisotropic_one_temperature_source, anisotropic_two_temperature_source, matched_hydrogen_rhs,
    DirectionalSky,
};
use rec_microphysics::hydrogen_peebles::RetainedState;
#[test]
fn temperatures_and_clocks() {
    let sky = DirectionalSky {
        weights: &[1., 1.],
        temperature_k: &[3000., 3000.],
        expansion_factor: &[1., 1.],
    };
    let s = RetainedState { xp: 0.5, x2: 0.01 };
    let a = anisotropic_one_temperature_source(&sky, 1e8, 1e-13, s).unwrap();
    let b = anisotropic_two_temperature_source(&sky, 1e8, 1e-13, s, 2000.).unwrap();
    assert!(b.alpha_b_m3_s > a.alpha_b_m3_s);
    assert_eq!(a.beta_p_s, b.beta_p_s);
    assert_eq!(a.r_alpha_s, b.r_alpha_s);
    assert_eq!(
        matched_hydrogen_rhs(-0.25, -2., 4., 1., -2., 4.).unwrap(),
        -0.25
    );
    assert_eq!(
        matched_hydrogen_rhs(-0.25, -2., 4., 2., -2., 4.).unwrap(),
        0.
    );
    assert!(matched_hydrogen_rhs(0., 1., 1., 0.9, 1., 1.).is_err());
}
