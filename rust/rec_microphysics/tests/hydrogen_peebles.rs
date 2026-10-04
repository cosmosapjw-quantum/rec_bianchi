use rec_microphysics::hydrogen_peebles::*;
fn near(a:f64,b:f64,rel:f64,abs:f64){assert!((a-b).abs()<=abs+rel*a.abs().max(b.abs()),"{a:.17e} != {b:.17e}");}

#[test]
fn no_extra_factor_four_in_elimination() {
    let r=ShellRates::new(2.0,8.0,0.0,0.0).unwrap();
    assert_eq!(r.beta_shell_s(),0.5); assert_eq!(r.d_ground_s(),2.0);
    near(r.c_factor(),0.8,0.0,1e-15);
    // A negative-control mutant using betaP as the shell coefficient differs.
    let mutant=2.0/(2.0+2.0);
    assert!((r.c_factor()-mutant).abs()>0.1);
}
#[test]
fn per_2p_escape_has_weight_three() {
    let r=ShellRates::new(12.0,4.0,8.0,0.0).unwrap();
    near(r.c_factor(),0.7,0.0,1e-15);
    let mutant=(4.0+8.0)/(4.0+8.0+12.0);
    assert!((r.c_factor()-mutant).abs()>0.1);
}
#[test]
fn c_endpoints_and_extreme_scaling() {
    assert_eq!(ShellRates::new(0.0,1.0,0.0,0.0).unwrap().c_factor(),1.0);
    assert_eq!(ShellRates::new(1.0,0.0,0.0,0.0).unwrap().c_factor(),0.0);
    let r=ShellRates::new(1e308,1e308,1e308,0.0).unwrap();
    near(r.c_factor(),0.8,0.0,1e-15);
    near(ShellRates::new(1e300,1e-300,0.0,0.0).unwrap().c_factor(),0.0,0.0,1e-300);
}
#[test]
fn nuclei_conservation_in_retained_rhs() {
    let r=ShellRates::new(7.0,3.0,2.0,0.04).unwrap();
    let f=retained_rhs(5.0,0.3,r,RetainedState{xp:0.2,x2:0.07}).unwrap();
    near(f.dxp_dt+f.dx2_dt+f.dx1_dt,0.0,0.0,2e-16);
    near(f.dxp_dt,-f.continuum_flux,0.0,0.0);
    near(f.dx1_dt,f.ground_flux,0.0,0.0);
}
#[test]
fn frozen_escape_qss_has_zero_shell_rhs() {
    let r=ShellRates::new(5.0,7.0,3.0,0.01).unwrap();
    let s=frozen_escape_qss(1.0,0.2,r,0.3).unwrap();
    let f=retained_rhs(1.0,0.2,r,s).unwrap();
    near(f.dx2_dt,0.0,0.0,1e-16);
    assert!(s.x2>0.0&&s.x2<0.7);
}
#[test]
fn frozen_and_instantaneous_targets_are_distinguished() {
    let r=ShellRates::new(5.0,7.0,3.0,0.1).unwrap();
    let finite=frozen_escape_qss(1.0,0.2,r,0.3).unwrap();
    let collapsed=qss_at_fixed_ground(1.0,0.2,r,0.3,0.7).unwrap();
    assert!(finite.x2<collapsed);
    near(qss_at_fixed_ground(1.0,0.2,r,0.3,finite.ground().unwrap()).unwrap(),finite.x2,2e-15,0.0);
}
#[test]
fn exact_off_shell_defect_includes_ground_depletion() {
    let r=ShellRates::new(19.0,7.0,3.0,0.13).unwrap();
    for s in [RetainedState{xp:0.2,x2:0.0},RetainedState{xp:0.2,x2:0.1},RetainedState{xp:0.8,x2:0.05}] {
        let d=closure_defect(4.0,0.7,r,s).unwrap();
        near(d.direct,d.reconstructed,1e-14,2e-15);
        if s.x2>0.0 {assert!(d.ground_depletion<0.0);}
    }
}
#[test]
fn qss_still_has_finite_ground_depletion_correction() {
    let r=ShellRates::new(5.0,7.0,3.0,0.1).unwrap();
    let s=frozen_escape_qss(1.0,0.2,r,0.3).unwrap();
    let d=closure_defect(1.0,0.2,r,s).unwrap();
    near(d.shell_lag,0.0,0.0,2e-16);
    near(d.direct,d.ground_depletion,2e-14,2e-16);
    assert!(d.direct.abs()>1e-3);
}
#[test]
fn detailed_balance_has_zero_all_three_rhs_components() {
    // Choose equilibrium composition first, independently impose both flux balances.
    let xp=0.2; let x2=0.04; let x1=0.76;
    let beta_p=4.0; let b=x2/(4.0*x1);
    let alpha=(beta_p/4.0*x2)/(2.0*xp*xp);
    let r=ShellRates::new(beta_p,8.0,3.0,b).unwrap();
    let f=retained_rhs(2.0,alpha,r,RetainedState{xp,x2}).unwrap();
    for v in [f.dxp_dt,f.dx2_dt,f.dx1_dt] {near(v,0.0,0.0,2e-16);}
}
#[test]
fn source_rounded_profile_fixture() {
    let p=hyrec2_one_temperature_source(3000.0,3000.0,250e6,5e-14,RetainedState{xp:0.1,x2:0.0}).unwrap();
    near(p.alpha_b_m3_s,6.685412343969989e-19,2e-14,0.0);
    near(p.rates.beta_p_s(),515.5775345899355,2e-14,0.0);
    near(p.r_alpha_s,1.0361997927901994,2e-14,0.0);
    near(p.rates.c_factor(),0.021501337234858833,2e-14,0.0);
    near(peebles_rhs(250e6,p.alpha_b_m3_s,p.rates,0.1).unwrap(),-3.5862885954445544e-14,2e-14,0.0);
}
#[test]
fn source_reassembles_escape_for_actual_ground_population() {
    let a=hyrec2_one_temperature_source(3000.0,3000.0,250e6,5e-14,RetainedState{xp:0.1,x2:0.0}).unwrap();
    let b=hyrec2_one_temperature_source(3000.0,3000.0,250e6,5e-14,RetainedState{xp:0.1,x2:0.3}).unwrap();
    near(b.r_alpha_s/a.r_alpha_s,1.5,2e-15,0.0);
}
#[test]
fn cgs_si_conversion_preserves_collision_rate() {
    let n=250.0; let a=6.7e-13;
    near(cm3_density_to_si(n).unwrap()*cm3_rate_to_si(a).unwrap(),n*a,2e-15,0.0);
}
#[test]
fn redshift_conversion_sign_and_domain() {
    near(to_redshift_rhs(-6e-13,2.0,1e-13).unwrap(),2.0,2e-15,0.0);
    assert_eq!(to_redshift_rhs(1.0,-1.0,1.0),Err(HydrogenError::Domain));
    assert_eq!(to_redshift_rhs(1.0,0.0,0.0),Err(HydrogenError::Domain));
}
#[test]
fn nonfinite_and_invalid_rates_rejected() {
    for v in [f64::NAN,f64::INFINITY,f64::NEG_INFINITY] {assert!(ShellRates::new(v,1.0,1.0,0.0).is_err());}
    assert!(ShellRates::new(-1.0,1.0,1.0,0.0).is_err());
    assert!(ShellRates::new(1.0,1.0,1.0,1.01).is_err());
    assert_eq!(ShellRates::new(0.0,0.0,0.0,0.0).unwrap_err(),HydrogenError::DegenerateRates);
}
#[test]
fn invalid_mass_and_density_rejected() {
    let r=ShellRates::new(1.0,1.0,1.0,0.0).unwrap();
    for s in [RetainedState{xp:-0.1,x2:0.0},RetainedState{xp:0.9,x2:0.2},RetainedState{xp:f64::NAN,x2:0.0}] {
        assert!(retained_rhs(1.0,1.0,r,s).is_err());
    }
    assert!(retained_rhs(0.0,1.0,r,RetainedState{xp:0.5,x2:0.0}).is_err());
    assert_eq!(frozen_escape_qss(1e30,1.0,r,0.5).unwrap_err(),HydrogenError::NonPhysicalQss);
}
#[test]
fn source_temperature_expansion_and_zero_ground_gates() {
    let s=RetainedState{xp:0.1,x2:0.0};
    assert_eq!(hyrec2_one_temperature_source(2000.0,3000.0,1.0,1.0,s).unwrap_err(),HydrogenError::UnequalTemperatures);
    assert!(hyrec2_one_temperature_source(0.0,0.0,1.0,1.0,s).is_err());
    assert!(hyrec2_one_temperature_source(3000.0,3000.0,1.0,0.0,s).is_err());
    assert_eq!(hyrec2_one_temperature_source(3000.0,3000.0,1.0,1.0,RetainedState{xp:1.0,x2:0.0}).unwrap_err(),HydrogenError::ZeroGroundSobolev);
}
#[test]
fn explicit_physical_constants_profile_and_temperature_gate() {
    let c=PhysicalConstantsSI{h_j_s:6.62607015e-34,k_b_j_k:1.380649e-23,c_m_s:299792458.0,
        reduced_mass_kg:9.1044252765e-31,chi2_j:3.4*1.602176634e-19,lambda_lya_m:121.567e-9};
    let (beta,b)=c.thermal_factors(3000.0,3000.0,6.7e-19).unwrap();
    assert!(beta>500.0&&beta<530.0); assert!(b>1e-18&&b<1e-16);
    assert_eq!(c.thermal_factors(2999.0,3000.0,6.7e-19),Err(HydrogenError::UnequalTemperatures));
    assert_eq!(c.thermal_factors(3000.0,3000.0,0.0).unwrap().0,0.0);
}
#[test]
fn thermal_underflow_is_zero_without_a_floor() {
    let p=hyrec2_one_temperature_source(1.0,1.0,1e6,1e-14,RetainedState{xp:0.1,x2:0.0}).unwrap();
    assert_eq!(p.rates.beta_p_s(),0.0); assert_eq!(p.rates.boltzmann_lya(),0.0);
    assert_eq!(p.rates.c_factor(),1.0);
}
#[test]
fn binding_energy_bookkeeping_is_not_a_heat_source() {
    let r=ShellRates::new(7.0,3.0,2.0,0.04).unwrap();
    let f=retained_rhs(5.0,0.3,r,RetainedState{xp:0.2,x2:0.07}).unwrap();
    let chi1=13.6; let e21=10.2;
    near(chi1*f.dxp_dt+e21*f.dx2_dt,
         -(chi1-e21)*f.continuum_flux-e21*f.ground_flux,2e-14,2e-15);
}
#[test]
fn retained_saha_partition_differs_from_collapsed_saha() {
    let beta_p=4.0; let b=0.2; let n=2.0; let alpha=2.0;
    let s_rate=beta_p*b/(n*alpha);
    let q:f64=s_rate/(1.0+4.0*b);
    let xp=2.0*q/(q+(q*q+4.0*q).sqrt());
    let x1=(1.0-xp)/(1.0+4.0*b); let x2=4.0*b*x1;
    let rates=ShellRates::new(beta_p,8.0,3.0,b).unwrap();
    let f=retained_rhs(n,alpha,rates,RetainedState{xp,x2}).unwrap();
    for v in [f.dxp_dt,f.dx2_dt,f.dx1_dt] {near(v,0.0,0.0,2e-15);}
    near(xp*xp/(1.0-xp),s_rate/(1.0+4.0*b),3e-15,0.0);
    assert!((xp*xp/(1.0-xp)-s_rate).abs()>0.05);
    assert!(peebles_rhs(n,alpha,rates,xp).unwrap().abs()>0.1);
}
