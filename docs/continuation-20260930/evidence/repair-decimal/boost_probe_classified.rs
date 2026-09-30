use std::io::{self, BufRead};
use rec_microphysics::frame::MaterialVelocity;
fn main() {
 for line in io::stdin().lock().lines() {
  let line=line.unwrap(); let a:Vec<f64>=line.split_whitespace().map(|s|s.parse().unwrap()).collect();
  let v=MaterialVelocity::new([a[0],a[1],a[2]]).unwrap();
  let q=[a[3],a[4],a[5],a[6]];
  let m=match v.normal_to_material_four_vector(q) { Ok(m)=>m, Err(e)=>{println!("ERR {:?}",e);continue;} };
  let r=match v.material_to_normal_four_vector(m) { Ok(r)=>r, Err(e)=>{println!("ERR {:?}",e);continue;} };
  for x in m.into_iter().chain(r) {print!("{:.17e} ",x);} println!();
 }
}
