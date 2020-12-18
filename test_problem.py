from problem import *

import unittest
import numpy.testing

class TestSegmentPointProjection(unittest.TestCase):
    def test_on_projection(self):
        S = np.array([1,1])
        E = np.array([3,1])
        R = np.array([2,2])
        expected = np.array([2,1])
        received = getDynamicInterception(S,E,R,0.1,0.1)
        np.testing.assert_allclose(expected,received)

    def test_closer_than_projection_same_speed(self):
        S = np.array([3,3-np.sqrt(2)])
        E = np.array([3,5])
        R = np.array([2,4])
        expected = np.array([3,3])
        received = getDynamicInterception(S,E,R,1.0,1.0)
        np.testing.assert_allclose(expected,received)

    def test_closer_than_projection(self):
        S = np.array([1,1])
        E = np.array([3,3])
        R = np.array([2,3])
        expected = np.array([2,2])
        received = getDynamicInterception(S,E,R,np.sqrt(2),1.0)
        np.testing.assert_allclose(expected,received)

    def test_too_far(self):
        S = np.array([1,1])
        E = np.array([3,1])
        R = np.array([20,2])
        received = getDynamicInterception(S,E,R,0.1,0.1)
        self.assertEqual(received, None)
