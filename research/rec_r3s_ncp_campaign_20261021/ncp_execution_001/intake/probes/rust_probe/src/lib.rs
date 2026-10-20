pub fn dot(a: [f64; 2], b: [f64; 2]) -> f64 { a[0]*b[0] + a[1]*b[1] }
#[cfg(test)] mod tests { #[test] fn exact_probe() { assert_eq!(super::dot([1.0,2.0],[2.0,1.0]),4.0); } }
