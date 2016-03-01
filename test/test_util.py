import unittest

import numpy as np

from pycgtool.util import stat_moments, sliding
from pycgtool.util import r_squared, gaussian
from pycgtool.util import triplets_from_pairs, tuple_equivalent
from pycgtool.util import quadruplets_from_pairs


class UtilTest(unittest.TestCase):
    def test_tuple_equivalent(self):
        t1 = (0, 1, 2)
        t2 = (2, 1, 0)
        self.assertTrue(tuple_equivalent(t1, t2))
        t2 = (2, 1, 3)
        self.assertFalse(tuple_equivalent(t1, t2))

    def test_triplets_from_pairs(self):
        nodes = [0, 1, 2, 3]
        pairs = [(0, 1), (1, 2), (2, 3)]
        result = [(0, 1, 2), (1, 2, 3)]
        self.assertEqual(result, triplets_from_pairs(nodes, pairs))
        pairs = [(0, 1), (1, 2), (2, 3), (3, 0)]
        result = [(0, 1, 2), (0, 3, 2), (1, 0, 3), (1, 2, 3)]
        self.assertEqual(result, triplets_from_pairs(nodes, pairs))

    def test_quadruplets_from_pairs(self):
        nodes = [0, 1, 2, 3]
        pairs = [(0, 1), (1, 2), (2, 3)]
        result = [(0, 1, 2, 3)]
        self.assertEqual(result, quadruplets_from_pairs(nodes, pairs))
        pairs = [(0, 1), (1, 2), (2, 3), (3, 0)]
        result = [(0, 1, 2, 3), (0, 3, 2, 1), (1, 0, 3, 2), (2, 1, 0, 3)]
        self.assertEqual(result, quadruplets_from_pairs(nodes, pairs))

    def test_stat_moments(self):
        t1 = [3, 3, 3, 3, 3]
        t2 = [1, 2, 3, 4, 5]
        np.testing.assert_allclose(np.array([3, 0]), stat_moments(t1))
        np.testing.assert_allclose(np.array([3, 2]), stat_moments(t2))

    def test_sliding(self):
        l = [0, 1, 2, 3, 4]
        res = [(None, 0, 1), (0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, None)]
        for res, pair in zip(res, sliding(l)):
            self.assertEqual(res, pair)

    def test_r_squared(self):
        ref = [i for i in range(5)]
        fit = ref
        self.assertEqual(1, r_squared(ref, fit))
        fit = [2 for _ in range(5)]
        self.assertEqual(0, r_squared(ref, fit))
        fit = [i for i in range(1, 6)]
        self.assertEqual(0.5, r_squared(ref, fit))


if __name__ == '__main__':
    unittest.main()
