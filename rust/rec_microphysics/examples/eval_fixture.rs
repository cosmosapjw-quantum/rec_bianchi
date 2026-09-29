//! Fixed input adapter only. Physics is evaluated through the public library API.
//! Stdin: REC_HE_WIRE_V2 count, then count whitespace-token records.
//! Stdout: strict JSON full observables, never reference values or tolerances.
use rec_microphysics::coverage::{d86_w, CoverageError};
use rec_microphysics::he_singlet::*;
use rec_microphysics::ledger::*;
use std::collections::{BTreeMap, BTreeSet};
use std::io::{self, Read};

#[derive(Default)]
struct Observables {
    values: BTreeMap<&'static str, Vec<f64>>,
    tags: BTreeMap<&'static str, &'static str>,
}
impl Observables {
    fn put(&mut self, key: &'static str, values: Vec<f64>) { self.values.insert(key, values); }
    fn scalar(&mut self, key: &'static str, value: f64) { self.put(key, vec![value]); }
    fn tag(&mut self, key: &'static str, value: &'static str) { self.tags.insert(key, value); }
}
fn m2(x: Mat2) -> Vec<f64> { x.0.into_iter().flatten().flat_map(|z| [z.re,z.im]).collect() }
fn m3(x: Mat3) -> Vec<f64> { x.0.into_iter().flatten().flat_map(|z| [z.re,z.im]).collect() }
fn coverage(c: CoverageState) -> &'static str {
    match c { CoverageState::Represented => "Represented", CoverageState::PhysicalZeroBelowThreshold => "PhysicalZeroBelowThreshold" }
}
fn err_name(e: &CoverageError) -> &'static str {
    match e { CoverageError::OutOfBand { .. }=>"OutOfBand", CoverageError::MissingAuthority { .. }=>"MissingAuthority", CoverageError::InvalidInput(_)=>"InvalidInput", CoverageError::NumericalDomainUncertain { .. }=>"NumericalDomainUncertain" }
}
struct Tokens<'a>(std::str::SplitWhitespace<'a>);
impl<'a> Tokens<'a> {
    fn word(&mut self) -> Result<&'a str,String> { self.0.next().ok_or_else(|| "missing token".into()) }
    fn float(&mut self) -> Result<f64,String> { self.word()?.parse().map_err(|_|"invalid float token".into()) }
    fn count(&mut self) -> Result<usize,String> {
        let n: usize = self.word()?.parse().map_err(|_|"invalid count token")?;
        if n>1024 { return Err("count limit exceeded".into()); } Ok(n)
    }
    fn vec3(&mut self) -> Result<[f64;3],String> { Ok([self.float()?,self.float()?,self.float()?]) }
    fn mat2(&mut self) -> Result<Mat2,String> {
        let mut m=Mat2::zero();for row in &mut m.0 { for z in row { *z=Complex64::new(self.float()?,self.float()?); }}Ok(m)
    }
    fn mat3(&mut self) -> Result<Mat3,String> {
        let mut m=Mat3::zero();for row in &mut m.0 { for z in row { *z=Complex64::new(self.float()?,self.float()?); }}Ok(m)
    }
    fn screen(&mut self) -> Result<RealV,String> {
        let mut m=[[0.;2];3];for row in &mut m { for z in row { *z=self.float()?; }}Ok(m)
    }
    fn constants(&mut self)->Result<HeConstants,String> {
        Ok(HeConstants {delta_s_ev:self.float()?,delta_p_ev:self.float()?,i_he_ev:self.float()?,epsilon_ir_ev:self.float()?,chi_p_ev:self.float()?,chi_s_ev:self.float()?,rydberg_ev:self.float()?})
    }
    fn state(&mut self)->Result<SourceState,String> {
        let ng=self.float()?;let ns=self.float()?;let n_he_plus=self.float()?;let ne=self.float()?;let temperature_k=self.float()?;
        let wp=self.mat3()?;let f=self.mat2()?;let v=self.screen()?;let constants=self.constants()?;
        let electron_frame=match self.word()? {"0"=>ElectronFramePolicy::CommonMaterialMaxwell,"1"=>ElectronFramePolicy::SpeciesDriftUnsupported,_=>return Err("invalid frame token".into())};
        // Intentionally construct mutable public inputs without constructor repair.
        Ok(SourceState { ng,ns,wp,n_he_plus,ne,temperature_k,f,v,constants,electron_frame })
    }
    fn bbmode(&mut self)->Result<WeightedBbMode,String> {Ok(WeightedBbMode {v:self.screen()?,f:self.mat2()?,weight_sr:self.float()?})}
    fn bfchannel(&mut self)->Result<BfChannel,String> {
        let ch=self.word()?;let gauge=self.word()?;
        match (ch,gauge) {
            ("P","Length")=>Ok(BfChannel::P(PBoundFreeTable::jacobs_high_length())),
            ("P","Velocity")=>Ok(BfChannel::P(PBoundFreeTable::jacobs_high_velocity())),
            ("S","Length")=>Ok(BfChannel::S(SBoundFreeTable::jacobs_high_length())),
            ("S","Velocity")=>Ok(BfChannel::S(SBoundFreeTable::jacobs_high_velocity())),
            _=>Err("invalid BF channel/gauge".into()),
        }
    }
    fn bfmode(&mut self)->Result<WeightedBfMode,String> {
        Ok(WeightedBfMode {channel:self.bfchannel()?,energy_ev:self.float()?,f:self.mat2()?,v:self.screen()?,direction:self.vec3()?,weight_energy_j:self.float()?,weight_omega_sr:self.float()?})
    }
    fn pair(&mut self)->Result<PairInput,String> {Ok(PairInput {y:self.float()?,f1:self.mat2()?,f2:self.mat2()?,v1:self.screen()?,v2:self.screen()?})}
    fn pairmode(&mut self)->Result<WeightedPairMode,String> {Ok(WeightedPairMode {input:self.pair()?,weight_dy:self.float()?,weight_omega1_sr:self.float()?,weight_omega2_sr:self.float()?,exchange_partner:self.count()?})}
    fn convention(&mut self)->Result<PairGridConvention,String> {
        match self.word()? {"FullOrderedExchangeClosed"=>Ok(PairGridConvention::FullOrderedExchangeClosed),"UnorderedHalfGridUnsupported"=>Ok(PairGridConvention::UnorderedHalfGridUnsupported),_=>Err("invalid pair convention".into())}
    }
    fn bbchannel(&mut self)->Result<BoundBoundChannel,String> {
        match self.word()? {"He584"=>Ok(BoundBoundChannel::He584),"IrPToS"=>Ok(BoundBoundChannel::IrPToS),_=>Err("invalid BB channel".into())}
    }
}
fn bf_observables(ch:BfChannel,e:f64,s:&SourceState)->Result<Observables,CoverageError> {
    let mut o=Observables::default();
    match ch {
        BfChannel::P(t)=>{let r=he_p_bf_source(e,s,t)?;o.put("photon_c",m2(r.photon_c));o.put("atomic",m3(r.atomic_b));o.scalar("event_rate_density",r.event_rate_density);o.tag("coverage",coverage(r.coverage));},
        BfChannel::S(t)=>{let r=he_s_bf_source(e,s,t)?;o.put("photon_c",m2(r.photon_c));o.scalar("atomic",r.atomic_s_density);o.scalar("event_rate_density",r.event_rate_density);o.tag("coverage",coverage(r.coverage));},
    }
    o.tag("density_measure","ContinuousPerJoulePerSteradian");Ok(o)
}
fn evaluate(t:&mut Tokens<'_>)->Result<Result<Observables,CoverageError>,String> {
    let op=t.word()?;
    let answer=match op {
        "BB"=>{
            let ch=t.bbchannel()?;let nl=t.float()?;let wp=t.mat3()?;let h=t.float()?;
            if !h.is_finite() || h<0. {return Err("invalid derivative step".into());}
            let mut modes=Vec::new();for _ in 0..t.count()? {modes.push(t.bbmode()?);}
            (|| {
                let r=he_bb_source(ch,nl,wp,&modes)?;let mut o=Observables::default();
                o.put("atomic_b",m3(r.atomic_b));o.scalar("event_rate",r.event_rate);
                o.put("angular_j",r.angular_j.into_iter().flat_map(m2).collect());o.put("angular_c",r.angular_c.into_iter().flat_map(m2).collect());
                let mut atoms=Vec::new();for mode in &modes {atoms.extend(m3(he_bb_kernel(ch,nl,wp,mode.f,mode.v)?.atomic_b_shell));}o.put("node_b",atoms);
                o.scalar("energy_j",material_energy_j(ch.energy_ev())?);o.scalar("weight_sum",r.stencil.weight_sum_sr);o.put("projector_sum",r.stencil.projector_sum_sr.into_iter().flatten().collect());
                if h>0. {
                    let plus=he_bb_source(ch,nl+h,wp,&modes)?;let minus=he_bb_source(ch,nl-h,wp,&modes)?;
                    o.put("plus_atomic_b",m3(plus.atomic_b));o.put("minus_atomic_b",m3(minus.atomic_b));
                    o.scalar("plus_event_rate",plus.event_rate);o.scalar("minus_event_rate",minus.event_rate);
                    o.put("jvp_atomic_b",m3((plus.atomic_b-minus.atomic_b).scale(1./(2.*h))));o.scalar("jvp_event_rate",(plus.event_rate-minus.event_rate)/(2.*h));
                }
                o.tag("spectral","SharpLineDeltaPerJoule");Ok(o)
            })()
        },
        "BF"=>{let ch=t.bfchannel()?;let e=t.float()?;let s=t.state()?;bf_observables(ch,e,&s)},
        "PAIR"=>{let s=t.state()?;let p=t.pair()?;(|| {let r=he_two_photon_pair_source(&p,&s)?;let mut o=Observables::default();
            o.put("screen_overlap",m2(r.screen_overlap));o.put("m12",m2(r.pair_matrix));o.put("m21",m2(r.partner_pair_matrix));o.put("c1",m2(r.tagged_c1_per_partner_sr));o.put("c2",m2(r.tagged_c2_per_partner_sr));
            o.put("energy_j",vec![r.delta_s_j,r.energy1_j,r.energy2_j]);o.scalar("event_rate_density",r.event_rate_density);o.scalar("w",r.w_s_inv);o.put("weights",vec![r.atomic_event_weight_s_inv,r.photon_marginal_weight_s_inv]);o.put("pair_factors",vec![r.atom_pair_factor,f64::from(r.photon_tags_per_event)]);
            o.tag("density_measure","PairDyDOmega1DOmega2");o.tag("marginal_measure","PartnerSolidAngleAtFixedMaterialEnergy");Ok(o)})()},
        "PAIRGRID"=>{let conv=t.convention()?;let s=t.state()?;let mut nodes=Vec::new();for _ in 0..t.count()? {nodes.push(t.pairmode()?);}(|| {let r=assemble_he_pair_grid(&s,&nodes,conv)?;let mut o=Observables::default();o.scalar("event_rate",r.event_rate);o.put("photon_number",r.photon_number_from_marginals.to_vec());o.put("photon_power_j",r.photon_energy_from_marginals_j.to_vec());o.scalar("weight_sum",r.quadrature_weight_sum);o.scalar("node_count",r.node_count as f64);o.tag("convention","FullOrderedExchangeClosed");Ok(o)})()},
        "BFGRID"=>{let s=t.state()?;let mut nodes=Vec::new();for _ in 0..t.count()? {nodes.push(t.bfmode()?);}(|| {let r=assemble_he_bf_grid(&s,&nodes)?;let mut o=Observables::default();o.put("rates",r.rates.to_vec());o.put("atomic_p",m3(r.atomic_p));o.scalar("atomic_s",r.atomic_s);o.scalar("photon_number",r.photon.number_rate);o.scalar("photon_power_j",r.photon.energy_rate_j);o.put("photon_momentum",r.photon.momentum_rate.to_vec());o.scalar("removed_power_j",r.absorbed_photon_power_j);o.scalar("internal_power_j",r.internal_power_j);o.scalar("heat_power_j",r.heat_power_j);o.put("coverage_counts",vec![r.represented_nodes as f64,r.physical_zero_nodes as f64]);Ok(o)})()},
        "SELECTED"=>{
            let conv=t.convention()?;let s=t.state()?;
            let mut b=Vec::new();for _ in 0..t.count()? {b.push(DirectedBbMode {mode:t.bbmode()?,direction:t.vec3()?});}
            let mut ir=Vec::new();for _ in 0..t.count()? {ir.push(DirectedBbMode {mode:t.bbmode()?,direction:t.vec3()?});}
            let mut bf=Vec::new();for _ in 0..t.count()? {bf.push(t.bfmode()?);}
            let mut p=Vec::new();for _ in 0..t.count()? {p.push(DirectedPairMode {mode:t.pairmode()?,direction1:t.vec3()?,direction2:t.vec3()?});}
            (|| {let r=assemble_selected_he_material_ledger(&s,&b,&ir,&bf,&p,conv)?;let mut o=Observables::default();
                o.put("rates",vec![r.rates.r584,r.rates.rir,r.rates.rp,r.rates.rs,r.rates.r2g]);o.put("species_source",r.ledger_si.species_source.to_vec());o.put("atomic_p",m3(r.atomic_p));o.scalar("atomic_s",r.atomic_s);o.scalar("photon_number",r.photon.number_rate);o.scalar("photon_power_j",r.photon.energy_rate_j);o.scalar("internal_power_j",r.ledger_si.p_internal);o.scalar("heat_power_j",r.bf.heat_power_j);o.put("q_photon",r.force.q_photon.to_vec());o.put("q_matter",r.force.q_matter.to_vec());o.tag("frame","material_tetrad");o.tag("metric","-+++");o.tag("pair_tag_policy","first_full_tag_only");Ok(o)
            })()
        },
        "LEDGER"=>{let r=ChannelRates {r584:t.float()?,rir:t.float()?,rp:t.float()?,rs:t.float()?,r2g:t.float()?};let bf=t.float()?;let heat=t.float()?;(|| {let l=assemble_he_event_ledger(r,HeEnergies::canonical_si(),bf,heat)?;let mut o=Observables::default();o.put("species_source",l.species_source.to_vec());o.scalar("internal_power_j",l.p_internal);o.scalar("photon_power_j",l.p_gamma);o.scalar("heat_power_j",l.h_kin);Ok(o)})()},
        "D86"=>{let y=t.float()?;d86_w(y).map(|w| {let mut o=Observables::default();o.scalar("w",w);o})},
        "GUARD"=>{let s=t.state()?;let e=s.constants.chi_p_ev+1.2*s.constants.rydberg_ev;he_p_bf_source(e,&s,PBoundFreeTable::jacobs_high_length()).map(|_|Observables::default())},
        "MAT2"=>{let m=t.mat2()?;m.validate_occupation().map(|_|Observables::default())},
        "MAT3"=>{let m=t.mat3()?;m.validate_population().map(|_|Observables::default())},
        "SCREEN"=>{let v=t.screen()?;let flag=t.word()?;let dir=match flag {"0"=>None,"1"=>Some(t.vec3()?),_=>return Err("invalid direction flag".into())};validate_screen(v,dir).map(|_|Observables::default())},
        "CONSTANTS"=>{let co=t.constants()?;co.validate().map(|_|Observables::default())},
        "WIDTH"=>{let w=t.float()?;energy_width_j(w).map(|x| {let mut o=Observables::default();o.scalar("width_j",x);o})},
        "ENERGY"=>{let ch=t.word()?;let e=t.float()?;let s=t.state()?;
            let result=match ch {"P"=>he_p_bf_source(e,&s,PBoundFreeTable::jacobs_high_length()).map(|r|r.coverage),"S"=>he_s_bf_source(e,&s,SBoundFreeTable::jacobs_high_length()).map(|r|r.coverage),_=>return Err("invalid energy channel".into())};
            result.map(|c| {let mut o=Observables::default();o.tag("coverage",coverage(c));o})
        },
        _=>return Err("unknown operation".into()),
    };
    if t.0.next().is_some() {return Err("extra tokens".into());}Ok(answer)
}
fn json_record(id:&str,result:Result<Observables,CoverageError>)->Result<String,String> {
    let (status,o)=match result {Ok(o)=>("ok",o),Err(e)=>(err_name(&e),Observables::default())};
    let mut values=Vec::new();for (k,xs) in o.values {
        if xs.iter().any(|x| !x.is_finite()) {return Err("nonfinite observable cannot be JSON encoded".into());}
        values.push(format!("\"{k}\":[{}]",xs.iter().map(|x|format!("{x:.17e}")).collect::<Vec<_>>().join(",")));
    }
    let tags=o.tags.iter().map(|(k,v)|format!("\"{k}\":\"{v}\"")).collect::<Vec<_>>().join(",");
    Ok(format!("{{\"id\":\"{id}\",\"status\":\"{status}\",\"values\":{{{}}},\"tags\":{{{tags}}}}}",values.join(",")))
}
fn run()->Result<(),String> {
    let mut text=String::new();io::stdin().take(2_000_001).read_to_string(&mut text).map_err(|e|e.to_string())?;
    if text.len()>2_000_000 {return Err("input size limit".into());}
    let mut lines=text.lines();let mut header=Tokens(lines.next().ok_or("missing header")?.split_whitespace());
    if header.word()? != "REC_HE_WIRE_V2" {return Err("invalid header".into());}
    let count=header.count()?;if count==0 || count>512 || header.0.next().is_some() {return Err("invalid record count".into());}
    let mut records=Vec::new();let mut ids=BTreeSet::new();
    for _ in 0..count {
        let mut t=Tokens(lines.next().ok_or("truncated input")?.split_whitespace());let id=t.word()?;
        if id.len()>96 || !id.bytes().all(|b|b.is_ascii_alphanumeric() || b"_-.".contains(&b)) || !ids.insert(id.to_owned()) {return Err("invalid or duplicate id".into());}
        records.push(json_record(id,evaluate(&mut t)?)?);
    }
    if lines.next().is_some() {return Err("extra input records".into());}
    println!("{{\"schema\":\"REC_HE_OBSERVABLES_V2\",\"records\":[{}]}}",records.join(","));Ok(())
}
fn main() {if let Err(e)=run() {eprintln!("fixture adapter error: {e}");std::process::exit(2);}}
