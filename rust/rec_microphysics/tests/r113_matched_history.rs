//! BASS R113 V12-V13: implicit matched hydrogen step.
use rec_microphysics::anisotropic::DirectionalSky;
use rec_microphysics::matched_history::{
    anisotropic_peebles_rate, implicit_matched_step, isotropic_peebles_rate, MatchedStep,
};

const N_H: f64 = 2.532027908215197e8; // m^-3 at z = 1100 (BASS hyrec_1100 anchor)
const H_S: f64 = 5.148602492099132e-14;
const T_K: f64 = 2.7255 * 1101.0;

fn quadrupole_sky(amplitude: f64) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    // 8 x 16 latitude-longitude directions with T = T_K (1 + amplitude P2(cos theta)).
    let mut w = Vec::new();
    let mut t = Vec::new();
    let mut f = Vec::new();
    for i in 0..8 {
        let z = -1.0 + (2 * i + 1) as f64 / 8.0;
        for _ in 0..16 {
            w.push(1.0);
            t.push(T_K * (1.0 + amplitude * 0.5 * (3.0 * z * z - 1.0)));
            f.push(1.0 + 0.1 * amplitude * (3.0 * z * z - 1.0));
        }
    }
    (w, t, f)
}

#[test]
fn flrw_identity_holds_for_every_step_size() {
    let x_ref_prev = 0.20;
    let x_ref_next = 0.18;
    let r_ref = isotropic_peebles_rate(T_K, N_H, H_S, x_ref_next).unwrap();
    for d_eta in [1e-4, 1e-2, 1.0, 50.0] {
        let step = MatchedStep {
            x_prev: x_ref_prev,
            x_ref_prev,
            x_ref_next,
            d_eta,
            gamma: 1.0,
            hubble_s: H_S,
            reference_rate_s: r_ref,
            reference_hubble_s: H_S,
        };
        let x = implicit_matched_step(&step, |x| isotropic_peebles_rate(T_K, N_H, H_S, x))
            .unwrap();
        assert!(
            (x - x_ref_next).abs() < 1e-14,
            "d_eta {d_eta}: {x} vs {x_ref_next}"
        );
    }
}

#[test]
fn anisotropic_step_is_bracketed_stiff_stable_and_first_order() {
    let (w, t, f) = quadrupole_sky(0.02);
    let sky = DirectionalSky {
        weights: &w,
        temperature_k: &t,
        expansion_factor: &f,
    };
    let rate = |x: f64| anisotropic_peebles_rate(&sky, N_H, H_S, x, None);
    // The anisotropic rate differs from the isotropic one at the same state.
    let x_ref = 0.15;
    let r_iso = isotropic_peebles_rate(T_K, N_H, H_S, x_ref).unwrap();
    assert!((rate(x_ref).unwrap() - r_iso).abs() > 1e-6 * r_iso.abs());
    // Constant synthetic reference x_ref = 0.15 with matched rates; integrate the
    // matched correction over d_eta_total = 0.02 with n and 2n steps.
    let integrate = |n: usize| {
        let mut x = x_ref;
        let h = 0.02 / n as f64;
        for _ in 0..n {
            let step = MatchedStep {
                x_prev: x,
                x_ref_prev: x_ref,
                x_ref_next: x_ref,
                d_eta: h,
                gamma: 1.0 + 1e-6,
                hubble_s: H_S * (1.0 + 1e-3),
                reference_rate_s: r_iso,
                reference_hubble_s: H_S,
            };
            x = implicit_matched_step(&step, rate).unwrap();
            assert!((0.0..1.0).contains(&x));
        }
        x
    };
    let a = integrate(8);
    let b = integrate(16);
    let c = integrate(32);
    let ratio = (a - b) / (b - c);
    assert!((1.7..2.3).contains(&ratio), "first-order ratio {ratio}");
    // Stiff (L-stable) limit: a huge step relaxes to the quasi-static root.
    let step = MatchedStep {
        x_prev: 0.9,
        x_ref_prev: x_ref,
        x_ref_next: x_ref,
        d_eta: 1e6,
        gamma: 1.0,
        hubble_s: H_S,
        reference_rate_s: r_iso,
        reference_hubble_s: H_S,
    };
    let x = implicit_matched_step(&step, rate).unwrap();
    assert!((0.0..1.0).contains(&x));
    // Invalid inputs fail closed.
    let mut bad = step;
    bad.gamma = 0.5;
    assert!(implicit_matched_step(&bad, rate).is_err());
}
