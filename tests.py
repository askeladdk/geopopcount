#!/usr/bin/env python
import unittest
from geopopcountd import spatial

with open('./cities500.txt') as f:
    popcounter = spatial.PopulationCounter(spatial.read_places_from_csv(f))

class TestSpatial(unittest.TestCase):
    def test_locate(self):
        taipei = popcounter.locate('taipei')
        self.assertIsNotNone(taipei)
        self.assertEqual(taipei.name, 'Taipei')

    def test_popcount_radius_1(self):
        amsterdam = popcounter.locate('amsterdam')
        popcount, places = popcounter.popcount(amsterdam, 1)
        self.assertEqual(len(places), 1)
        self.assertEqual(popcount, 741636)
    
    def test_popcount_radius_30000(self):
        buenos_aires = popcounter.locate('buenos aires')
        popcount, places = popcounter.popcount(buenos_aires, 30000)
        self.assertEqual(len(places), 20)
        self.assertEqual(popcount, 14542815)

if __name__ == '__main__':
    unittest.main()
