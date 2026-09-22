use rec_microphysics::coverage::d86_w;
use rec_microphysics::he_singlet::{
    AngularSample, BoundBoundChannel, Complex64, Mat2, Mat3, PBoundFreeTable, SBoundFreeTable,
    SourceState, he_bb_source, he_p_bf_source, he_s_bf_source, he_two_photon_pair_source,
    planck_occupation,
};
use rec_microphysics::ledger::{ChannelRates, HeEnergies, assemble_he_event_ledger};

fn c(x: f64) -> Complex64 {
    Complex64::new(x, 0.0)
}
fn wp_diag(a: f64, b: f64, d: f64) -> Mat3 {
    Mat3([
        [c(a), c(0.0), c(0.0)],
        [c(0.0), c(b), c(0.0)],
        [c(0.0), c(0.0), c(d)],
    ])
}
fn main() {
    let d025 = d86_w(0.025).unwrap();
    let d05 = d86_w(0.5).unwrap();
    let d975 = d86_w(0.975).unwrap();
    let p12 = PBoundFreeTable::jacobs_high_length().lookup(1.2).unwrap();
    let s10 = SBoundFreeTable::jacobs_high_length().lookup(1.0).unwrap();

    let wp = wp_diag(1.0, 2.0, 3.0);
    let vac = he_bb_source(
        BoundBoundChannel::He584,
        0.0,
        wp,
        Mat2::zero(),
        &AngularSample::octahedron_6(),
    )
    .unwrap();
    let a = BoundBoundChannel::He584.a_s_inv();
    let mut bb_vac_rel: f64 = 0.0;
    for i in 0..3 {
        for j in 0..3 {
            let want = wp[i][j].scale(-a);
            bb_vac_rel = bb_vac_rel.max((vac.atomic_b[i][j] - want).abs() / (1.0 + want.abs()));
        }
    }

    // Weak/JVP-style oracle on the finite angular stencil: for isotropic F=fI,
    // dR_BB/dn_lower = -3 A f. This is an implementation parity check, not a
    // promotion of the September weak/JVP scientific result.
    let focc = 0.13;
    let fmat = Mat2::scalar(focc);
    let n0 = 1.7;
    let h = 2.0_f64.powi(-16);
    let rp = he_bb_source(
        BoundBoundChannel::He584,
        n0 + h,
        wp,
        fmat,
        &AngularSample::octahedron_6(),
    )
    .unwrap()
    .event_rate;
    let rm = he_bb_source(
        BoundBoundChannel::He584,
        n0 - h,
        wp,
        fmat,
        &AngularSample::octahedron_6(),
    )
    .unwrap()
    .event_rate;
    let jvp_num = (rp - rm) / (2.0 * h);
    let jvp_ana = -3.0 * a * focc;
    let jvp_rel = (jvp_num - jvp_ana).abs() / (1.0 + jvp_ana.abs());

    let t = 8000.0;
    let mut ps = SourceState::lte_populations(t, 2.0e7, 3.0e7).unwrap();
    let ep = ps.constants.chi_p_ev + 1.2 * ps.constants.rydberg_ev;
    ps.f = Mat2::scalar(planck_occupation(ep, t));
    let po = he_p_bf_source(ep, &ps, PBoundFreeTable::jacobs_high_length()).unwrap();
    let p_lte = po.photon_c.max_abs() / po.gross_scale.max(f64::MIN_POSITIVE);
    let p_lte_atom = po.atomic_b.max_abs() / po.atomic_gross_scale.max(f64::MIN_POSITIVE);

    let mut ss = SourceState::lte_populations(t, 2.0e7, 3.0e7).unwrap();
    let es = ss.constants.chi_s_ev + 1.2 * ss.constants.rydberg_ev;
    ss.f = Mat2::scalar(planck_occupation(es, t));
    let so = he_s_bf_source(es, &ss, SBoundFreeTable::jacobs_high_length()).unwrap();
    let s_lte = so.photon_c.max_abs() / so.gross_scale.max(f64::MIN_POSITIVE);

    let mut cx = SourceState::simple(2.0, 0.7, wp_diag(0.4, 0.7, 1.1), 0.3, 0.4, 9000.0).unwrap();
    cx.f = Mat2([
        [Complex64::new(0.2, 0.0), Complex64::new(0.03, 0.04)],
        [Complex64::new(0.03, -0.04), Complex64::new(0.1, 0.0)],
    ]);
    cx.wp[0][1] = Complex64::new(0.05, 0.02);
    cx.wp[1][0] = Complex64::new(0.05, -0.02);
    let ecx = cx.constants.chi_p_ev + 1.2 * cx.constants.rydberg_ev;
    let co = he_p_bf_source(ecx, &cx, PBoundFreeTable::jacobs_high_length()).unwrap();
    let trace_rel = (co.atomic_b.trace().re + co.event_rate_density).abs()
        / (1.0 + co.atomic_b.trace().re.abs() + co.event_rate_density.abs());

    let pair_state = SourceState::lte_populations(7000.0, 3.0e7, 3.0e7).unwrap();
    let e1 = 0.5 * pair_state.constants.delta_s_ev;
    let pf = Mat2::scalar(planck_occupation(e1, pair_state.temperature_k));
    let pair = he_two_photon_pair_source(0.5, &pair_state, pf, pf).unwrap();

    let rates = ChannelRates {
        r584: 2.0,
        rir: -3.0,
        rp: 5.0,
        rs: -7.0,
        r2g: 11.0,
    };
    let en = HeEnergies::canonical();
    let hkin = -8.0;
    let bf = en.chi_p * rates.rp + en.chi_s * rates.rs + hkin;
    let led = assemble_he_event_ledger(rates, en, bf, hkin).unwrap();

    println!(
        concat!(
            "{{",
            "\"d86_0025\":{:.17e},\"d86_05\":{:.17e},\"d86_0975\":{:.17e},",
            "\"p_q12_s_mb\":{:.17e},\"p_q12_d_mb\":{:.17e},\"s_q10_mb\":{:.17e},",
            "\"bb_vac_rel\":{:.17e},\"bb_jvp_num\":{:.17e},\"bb_jvp_ana\":{:.17e},\"bb_jvp_rel\":{:.17e},",
            "\"p_lte_rel\":{:.17e},\"p_lte_atom_rel\":{:.17e},\"s_lte_rel\":{:.17e},",
            "\"complex_trace_rel\":{:.17e},\"pair_matrix_abs\":{:.17e},",
            "\"pair_tags\":{},\"pair_factor\":{:.17e},\"pair_weight_ratio\":{:.17e},",
            "\"he_nuclei_residual\":{:.17e},\"charge_residual\":{:.17e},\"energy_residual\":{:.17e}",
            "}}"
        ),
        d025,
        d05,
        d975,
        p12.sigma_s_mb,
        p12.sigma_d_mb,
        s10,
        bb_vac_rel,
        jvp_num,
        jvp_ana,
        jvp_rel,
        p_lte,
        p_lte_atom,
        s_lte,
        trace_rel,
        pair.pair_matrix.max_abs(),
        pair.photon_tags_per_event,
        pair.atom_pair_factor,
        pair.photon_marginal_weight_s_inv / pair.atomic_event_weight_s_inv,
        led.he_nuclei_residual,
        led.charge_minus_e_residual,
        led.energy_residual
    );
}
