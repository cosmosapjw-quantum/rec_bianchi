use rec_microphysics::frame::MaterialVelocity;
use rec_microphysics::screen::ScreenTransform;
use rec_microphysics::he_singlet::{Complex64,Mat2};
use std::io::{self,BufRead};
fn main(){for line in io::stdin().lock().lines(){let line=line.unwrap();let x:Vec<f64>=line.split_whitespace().map(|s|s.parse().unwrap()).collect();let v=MaterialVelocity::new([x[0],x[1],x[2]]).unwrap();let e=[x[3],x[4],x[5]];let mut n=[[0.;2];3];let mut m=n;for i in 0..3{for j in 0..2{n[i][j]=x[6+2*i+j];m[i][j]=x[12+2*i+j];}}
let t=match ScreenTransform::new(v,e,n,m){Ok(t)=>t,Err(err)=>{println!("ERR {:?}",err);continue}};
let mut f=Mat2([[Complex64::new(0.,0.);2];2]);for i in 0..2{for j in 0..2{f.0[i][j]=Complex64::new(x[18+4*i+2*j],x[19+4*i+2*j]);}}
let out=match t.normal_to_material(f){Ok(o)=>o,Err(err)=>{println!("ERR {:?}",err);continue}};let back=match t.material_to_normal(out){Ok(o)=>o,Err(err)=>{println!("ERR {:?}",err);continue}};let rate=match v.normal_to_material_ray(1.,e).unwrap().normal_time_after_screen_map(back){Ok(o)=>o,Err(err)=>{println!("ERR {:?}",err);continue}};
let mut values=Vec::new();for row in t.transported_normal_screen(){values.extend(row);}for row in t.overlap(){values.extend(row);}for a in [out,back,rate]{for row in a.0{for z in row{values.push(z.re);values.push(z.im);}}}println!("{}",values.iter().map(|x|format!("{:.17e}",x)).collect::<Vec<_>>().join(" "));
}}
