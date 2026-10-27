"""Small constructive controls with independently specified answers."""
from fractions import Fraction as F
from remainder import PiecewiseLinear as PL


def run_controls():
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(dict(name=name, status="PASS"))
    def reject(name, action):
        try:
            action()
        except ValueError:
            check(name, True)
        else:
            check(name, False)
    def identity(name, result, expected):
        check(name, result["direct"] == result["signed"] == expected and abs(expected) <= result["bound"])

    affine = PL([-2, -1, 0, 2, 4], [-3, -1, 1, 5, 9])
    identity("nonuniform_affine_positive", affine.retime(F(-3,2), F(7,2)), F(0))
    identity("nonuniform_affine_negative", affine.retime(F(7,2), F(-3,2)), F(0))
    identity("affine_chord", affine.chord(F(-3,2), F(1,3), F(7,2)), F(0))
    hinge = PL([-2, 0, 2], [2, 0, 2])
    for q, target, name in [(F(-1,4), F(1,4), "positive"), (F(1,4), F(-1,4), "negative")]:
        result = hinge.retime(q, target)
        identity("absolute_value_hinge_"+name, result, F(1,2))
    check("negative_path_sign_mutation_detected", hinge.retime(F(1,4), F(-1,4))["direct"] != -F(1,2))
    identity("start_knot_positive", hinge.retime(0, F(1,2)), F(0))
    identity("start_knot_negative", hinge.retime(0, F(-1,2)), F(0))
    check("starting_atom_mutation_detected", hinge.retime(0,F(1,2))["direct"] != F(1,2)*hinge.jump(1))
    identity("target_knot_positive", hinge.retime(F(-1,2), 0), F(0))
    identity("target_knot_negative", hinge.retime(F(1,2), 0), F(0))
    identity("zero_step_left_boundary", hinge.retime(-2, -2), F(0))
    check("zero_step_no_exterior_derivative", hinge.retime(-2,-2)["directional_slope"] is None)
    identity("hinge_chord_minus_sign", hinge.chord(-1,0,1), F(-1))
    cancellation = PL([0,1,2,3,4], [0,0,1,0,0])
    result = cancellation.retime(F(1,2), F(7,2))
    identity("multi_jump_cancellation", result, F(0))
    check("cancellation_absolute_envelope_positive", result["bound"] == 6)
    check("dropped_jump_zero_curvature_mutation_detected", hinge.retime(F(-1,4), F(1,4))["direct"] != 0)
    flat = PL([0,1,2], [0,0,0])
    identity("flat_crossing_no_false_mutation_requirement", flat.retime(F(1,2), F(3,2)), F(0))
    reject("reversed_grid", lambda: PL([1,0], [0,0]))
    reject("duplicate_grid", lambda: PL([0,0,1], [0,0,0]))
    reject("short_grid", lambda: PL([0], [0]))
    reject("sample_count", lambda: PL([0,1], [0]))
    reject("nan_grid", lambda: PL([0,float('nan')], [0,0]))
    reject("infinite_sample", lambda: PL([0,1], [0,float('inf')]))
    reject("final_causal_endpoint", lambda: hinge.value(2))
    reject("left_exterior", lambda: hinge.value(F(-5,2)))
    reject("right_exterior", lambda: hinge.retime(0,3))
    reject("zero_step_invalid_endpoint", lambda: hinge.retime(2,2))
    reject("exterior_derivative", lambda: hinge.directional_slope(-2,-1))
    reject("bad_chord_order", lambda: hinge.chord(0,0,1))
    return checks
