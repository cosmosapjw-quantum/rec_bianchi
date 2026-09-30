use rec_microphysics::coverage::CoverageError;
use rec_microphysics::frame::MaterialVelocity;
use rec_microphysics::he_singlet::{Complex64, Mat2, RealV};
use rec_microphysics::screen::ScreenTransform;

fn z(re: f64, im: f64) -> Complex64 {
    Complex64::new(re, im)
}

fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() <= 64.0 * f64::EPSILON * (1.0 + a.abs().max(b.abs())),
        "{a} != {b}"
    );
}

fn close_block(a: Mat2, b: Mat2) {
    for i in 0..2 {
        for j in 0..2 {
            close(a[i][j].re, b[i][j].re);
            close(a[i][j].im, b[i][j].im);
        }
    }
}

fn xy() -> RealV {
    [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]
}

#[test]
fn identity_and_parallel_antiparallel_clocks() {
    let e = [0.0, 0.0, 1.0];
    let block = Mat2([[z(-3.0, 0.0), z(1.0, 2.0)], [z(1.0, -2.0), z(2.0, 0.0)]]);
    for beta_z in [0.0, 0.6, -0.6] {
        let velocity = MaterialVelocity::new([0.0, 0.0, beta_z]).unwrap();
        let transform = ScreenTransform::new(velocity, e, xy(), xy()).unwrap();
        assert_eq!(transform.transported_normal_screen(), xy());
        assert_eq!(transform.overlap(), [[1.0, 0.0], [0.0, 1.0]]);
        close_block(transform.normal_to_material(block).unwrap(), block);
        close_block(transform.material_to_normal(block).unwrap(), block);

        let ray = velocity.normal_to_material_ray(1.0, e).unwrap();
        let expected_d = if beta_z == 0.6 {
            0.5
        } else if beta_z == -0.6 {
            2.0
        } else {
            1.0
        };
        close(ray.doppler(), expected_d);
        let normal_rate = ray
            .normal_time_after_screen_map(transform.material_to_normal(block).unwrap())
            .unwrap();
        close(normal_rate[0][0].re, expected_d * block[0][0].re);
        close(normal_rate[0][1].im, expected_d * block[0][1].im);
    }
}

#[test]
fn oblique_null_gauge_rotation_and_signed_complex_congruence() {
    let velocity = MaterialVelocity::new([0.6, 0.0, 0.0]).unwrap();
    let e = [0.0, 0.0, 1.0];
    // Eq. (135) and the rotation-free boost give physical columns (.8,0,.6), (0,1,0).
    let transported = [[0.8, 0.0], [0.0, 1.0], [0.6, 0.0]];
    let theta: f64 = 0.37;
    let (s, c) = theta.sin_cos();
    // A rotation of the material basis.
    let material = [[c * 0.8, s * 0.8], [-s, c], [c * 0.6, s * 0.6]];
    let transform = ScreenTransform::new(velocity, e, xy(), material).unwrap();
    for row in 0..3 {
        for col in 0..2 {
            close(
                transform.transported_normal_screen()[row][col],
                transported[row][col],
            );
        }
    }
    let t = transform.overlap();
    close(t[0][0], c);
    close(t[0][1], -s);
    close(t[1][0], s);
    close(t[1][1], c);

    let block = Mat2([[z(-3.0, 0.0), z(1.0, 2.0)], [z(1.0, -2.0), z(2.0, 0.0)]]);
    let mapped = transform.normal_to_material(block).unwrap();
    close_block(transform.material_to_normal(mapped).unwrap(), block);
    close(mapped[0][0].re + mapped[1][1].re, -1.0);
    close(
        mapped[0][0].re * mapped[1][1].re
            - (mapped[0][1].re * mapped[1][0].re - mapped[0][1].im * mapped[1][0].im),
        -11.0,
    );
    close(mapped[0][1].re, mapped[1][0].re);
    close(mapped[0][1].im, -mapped[1][0].im);
    assert!(mapped[0][0].re < 0.0 || mapped[1][1].re < 0.0);
    let reflected = [[0.8, 0.0], [0.0, -1.0], [0.6, 0.0]];
    let reflection = ScreenTransform::new(velocity, e, xy(), reflected).unwrap();
    assert_eq!(reflection.overlap(), [[1.0, 0.0], [0.0, -1.0]]);
}

#[test]
fn validation_and_binary64_extremes() {
    let velocity = MaterialVelocity::new([0.6, 0.0, 0.0]).unwrap();
    let e = [0.0, 0.0, 1.0];
    let physical = [[0.8, 0.0], [0.0, 1.0], [0.6, 0.0]];
    assert!(ScreenTransform::new(velocity, [0.0, 0.0, 0.5], xy(), physical).is_err());
    assert!(
        ScreenTransform::new(
            velocity,
            e,
            [[f64::NAN, 0.0], [0.0, 1.0], [0.0, 0.0]],
            physical
        )
        .is_err()
    );
    assert!(ScreenTransform::new(velocity, e, xy(), xy()).is_err());
    assert!(ScreenTransform::new(velocity, e, xy(), [[0.0; 2]; 3]).is_err());
    let transform = ScreenTransform::new(velocity, e, xy(), physical).unwrap();
    assert!(matches!(
        transform.normal_to_material(Mat2([[z(f64::NAN, 0.0); 2]; 2])),
        Err(CoverageError::InvalidInput(_))
    ));
    let (s, c) = std::f64::consts::FRAC_PI_4.sin_cos();
    let rotated = [[c * 0.8, s * 0.8], [-s, c], [c * 0.6, s * 0.6]];
    let rotation = ScreenTransform::new(velocity, e, xy(), rotated).unwrap();
    assert!(matches!(
        rotation.normal_to_material(Mat2([[z(f64::MAX, 0.0); 2]; 2])),
        Err(CoverageError::NumericalDomainUncertain { .. })
    ));

    let stationary = MaterialVelocity::new([0.0; 3]).unwrap();
    let identity = ScreenTransform::new(stationary, e, xy(), xy()).unwrap();
    let smallest = Mat2([[z(f64::from_bits(1), 0.0), z(0.0, 0.0)]; 2]);
    assert_eq!(identity.normal_to_material(smallest).unwrap(), smallest);
}
