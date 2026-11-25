use rec_microphysics::{
    angular_line::{AngularNetwork, Edge},
    live_line::{Hat, Network},
};
#[test]
fn sparse_angular_step_matches_dense_and_four_force() {
    let hats = vec![Hat::new(1., vec![0.4, 0.6], vec![0.99, 1.01]).unwrap(); 3];
    let x = vec![-1., 0., 1.];
    let d = vec![[1., 0., 0.], [0., 1., 0.], [-1., 0., 0.]];
    let edges = vec![
        Edge { i: 0, j: 1, k: 0.3 },
        Edge { i: 0, j: 2, k: 0.1 },
        Edge { i: 1, j: 2, k: 0.2 },
    ];
    let q = AngularNetwork::new(hats.clone(), x.clone(), d, edges, 2.4e15, 5.8e10).unwrap();
    let refn = Network::new(hats, x, vec![0., 0.3, 0.1, 0.3, 0., 0.2, 0.1, 0.2, 0.]).unwrap();
    let old = [0.5, 0.1, 0.2];
    let a = q.action(&old).unwrap();
    assert!(a.force_defect < 2e-14 && a.number_defect < 2e-14);
    let r = q.step(&old, 1.).unwrap();
    let b = refn.step(&old, 1.).unwrap();
    for (a, b) in r.f.iter().zip(b.f) {
        assert!((a - b).abs() < 1e-11);
    }
    assert!(r.number_defect < 2e-12 && r.residual < 2e-11 && r.free_change <= 1e-13);
}
