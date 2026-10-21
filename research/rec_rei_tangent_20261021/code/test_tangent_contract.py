"""Eight bounded contract checks, separate from the numerical fixture audit."""
from __future__ import annotations

import copy
import unittest

import numpy as np

from owner_model import make_model
from tangent_core import TangentOperator


class TestTangentContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.seed = make_model(.002, .00007, -.0002)
        cls.state = cls.model.initial_state()
        cls.operator = TangentOperator(cls.model)
        cls.prepared = cls.operator.prepare(0., cls.state)

    def test_01_complex_values_are_rejected(self):
        # Even a zero-imaginary complex dtype must not be silently projected.
        for x, y in ((0j, self.state), (0., self.state.astype(complex))):
            with self.subTest(x=x, dtype=y.dtype), self.assertRaises(ValueError):
                self.operator.prepare(x, y)
        with self.assertRaises(ValueError):
            self.prepared.jvp(np.zeros(40, dtype=complex))
        with self.assertRaises(ValueError):
            self.prepared.observable_jvp(np.zeros(40), 1j)
        with self.assertRaises(ValueError):
            self.prepared.vjp(np.zeros(40, dtype=complex))

    def test_02_nonfinite_values_are_rejected(self):
        for value in (np.nan, np.inf, -np.inf):
            y = self.state.copy()
            y[1] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.operator.prepare(0., y)
            with self.assertRaises(ValueError):
                self.operator.prepare(value, self.state)
            with self.assertRaises(ValueError):
                self.prepared.jvp(np.zeros(40), value)
            lam = np.zeros(40)
            lam[10] = value
            with self.assertRaises(ValueError):
                self.prepared.vjp(lam)

    def test_03_state_and_action_shapes_are_rejected(self):
        for state in (self.state[:-1], self.state[:, None], np.zeros((2, 20))):
            with self.subTest(shape=state.shape), self.assertRaises(ValueError):
                self.operator.prepare(0., state)
        for direction in (np.zeros(39), np.zeros((40, 0)), np.zeros((40, 2, 1))):
            with self.subTest(shape=direction.shape), self.assertRaises(ValueError):
                self.prepared.jvp(direction)
            with self.assertRaises(ValueError):
                self.prepared.observable_jvp(direction)
        with self.assertRaises(ValueError):
            self.prepared.jvp(np.zeros((40, 2)), np.zeros(3))
        with self.assertRaises(ValueError):
            self.prepared.vjp(np.zeros((40, 1)))

    def test_04_source_chart_and_seed_domain_are_rejected(self):
        for index, value in ((1, 1.01), (3, -1e-9), (4, 0.), (22, 0.)):
            y = self.state.copy()
            y[index] = value
            with self.subTest(index=index), self.assertRaises(ValueError):
                self.operator.prepare(0., y)
        for x in (-1e-4, self.model.source.xmax + 1e-3):
            with self.assertRaises(ValueError):
                self.operator.prepare(x, self.state)
        for axes in ((1j, 0., 0.), (np.nan, 0., 0.), (3., 0., 0.),
                     (0., 1., 0.), (0., 0., 1.)):
            with self.subTest(axes=axes), self.assertRaises(ValueError):
                make_model(*axes)

    def test_05_collision_sources_are_rejected(self):
        for attribute, value in (("ne_source", object()), ("nu_visc", .01)):
            changed = copy.copy(self.model)
            setattr(changed, attribute, value)
            with self.subTest(attribute=attribute), self.assertRaises(ValueError):
                TangentOperator(changed)

    def test_06_changed_closure_and_grid_are_rejected(self):
        for attribute, value in (("n", 7), ("ellmax", 6), ("fm", .2)):
            changed = copy.copy(self.model)
            setattr(changed, attribute, value)
            with self.subTest(attribute=attribute), self.assertRaises(ValueError):
                TangentOperator(changed)
        for attribute, value in (("mass", 31.), ("radial_cells", 25),
                                 ("angular_cells", 13), ("gauss_order", 2)):
            changed = copy.copy(self.model)
            changed.momentum = copy.copy(self.model.momentum)
            setattr(changed.momentum, attribute, value)
            with self.subTest(attribute=attribute), self.assertRaises(ValueError):
                TangentOperator(changed)

    def test_07_inactive_tau_and_thermal_columns_use_admissible_states(self):
        reference = self.model.rhs(0., self.state)
        for index, displacement in ((0, -.5), (0, .5), (3, .5), (3, 1.)):
            # u >= 0: do not use a forbidden negative thermal perturbation.
            shifted = self.state.copy()
            shifted[index] += displacement
            np.testing.assert_array_equal(self.model.rhs(0., shifted), reference)
            direction = np.zeros(40)
            direction[index] = 1.
            np.testing.assert_array_equal(self.prepared.jvp(direction), np.zeros(40))
            np.testing.assert_array_equal(self.prepared.observable_jvp(direction),
                                          np.zeros(4))
        grad, _ = self.prepared.vjp(np.arange(40, dtype=float))
        self.assertEqual(grad[0], 0.)
        self.assertEqual(grad[3], 0.)

    def test_08_snapshot_and_public_arrays_are_immutable(self):
        changed = copy.copy(self.model)
        changed.energy_matrix = np.array(self.model.energy_matrix, copy=True)
        operator = TangentOperator(changed)
        before = operator.prepare(0., self.state)
        changed.energy_matrix[:] = 0.
        after = operator.prepare(0., self.state)
        direction = np.linspace(-.5, .5, 40)
        direction[3] = 0.
        np.testing.assert_array_equal(before.rhs, after.rhs)
        np.testing.assert_array_equal(before.jvp(direction), after.jvp(direction))
        for array in (before.rhs, before.observables_signed,
                      self.seed.amplitude_gradient, self.seed.initial_tangents):
            self.assertFalse(array.flags.writeable)
            with self.assertRaises(ValueError):
                array.flat[0] = 1.


if __name__ == "__main__":
    unittest.main(verbosity=2)
