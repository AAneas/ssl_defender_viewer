from geometry import *

import unittest
import numpy.testing

class TestSegmentPointProjection(unittest.TestCase):
    def test_middle(self):
        p1 = np.array([1,1])
        p2 = np.array([3,3])
        p3 = np.array([3,1])
        np.testing.assert_allclose(np.array([2,2]), segmentPointProjection(p1,p2,p3))

    def test_src(self):
        p1 = np.array([1,0])
        p2 = np.array([2,0])
        p3 = np.array([-1,3])
        np.testing.assert_allclose(np.array([1,0]), segmentPointProjection(p1,p2,p3))

    def test_end(self):
        p1 = np.array([0,1])
        p2 = np.array([0,-1])
        p3 = np.array([-1,-3])
        np.testing.assert_allclose(np.array([0,-1]), segmentPointProjection(p1,p2,p3))
