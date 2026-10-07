use rec_microphysics::ledger::{assemble_he_event_ledger, ChannelRates, HeEnergies};
fn main() {
    let rates = ChannelRates { r584: 1.0e308, rir: 0.0, rp: 0.0, rs: 0.0, r2g: 0.0 };
    let ledger = assemble_he_event_ledger(rates, HeEnergies::canonical(), 0.0, 0.0).unwrap();
    println!("p_internal={:?} p_gamma={:?} energy_residual={:?}", ledger.p_internal, ledger.p_gamma, ledger.energy_residual);
    assert!(!ledger.p_internal.is_finite() && !ledger.p_gamma.is_finite() && ledger.energy_residual.is_nan());
}
