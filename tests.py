import unittest
from utils.graph import Graph

class TestGraphClass(unittest.TestCase):
    def test_attributes(self):
        g = Graph()
        self.assertAlmostEqual(g.traces, [])


if __name__ == '__main__':
    unittest.main()