import unittest
from utils.graph import Graph
import os


class TestGraphClass(unittest.TestCase):
    def test_custom_attributes(self):
        g = Graph(
            total_size=(1, 6),
            graph_size=(7, 3),
            graph_offset=(1, 1),
            freq_range=(2, 2),
            amp_range=(6, 9),
            file_name='test_file.svg'
        )

        self.assertListEqual(g.traces, [])
        self.assertTupleEqual(g.total_size, (1, 6))
        self.assertTupleEqual(g.graph_size, (7, 3))
        self.assertTupleEqual(g.graph_offset, (1, 1))
        self.assertTupleEqual(g.freq_range, (2, 2))
        self.assertTupleEqual(g.amp_range, (6, 9))
        self.assertEqual(g.file_name, 'test_file.svg')

    def test_default_attributes(self):
        g = Graph()

        self.assertListEqual(g.traces, [])
        self.assertTupleEqual(g.total_size, (1000, 600))
        self.assertTupleEqual(g.graph_size, (700, 300))
        self.assertTupleEqual(g.graph_offset, (120, 10))
        self.assertTupleEqual(g.freq_range, (20, 20000))
        self.assertTupleEqual(g.amp_range, (60, 95))
        self.assertEqual(g.file_name, './default_output.svg')

    def test_add_trace(self):
        g = Graph()
        g.add_trace([(0, 0), (1, 1)])
        self.assertTupleEqual(g.traces[0][0], (0, 0))
        self.assertTupleEqual(g.traces[0][1], (1, 1))

    def test_log_scale(self):
        g = Graph(
            total_size=(1000, 600),
            graph_size=(700, 300),
            graph_offset=(0, 0),
            freq_range=(20, 20000),
            amp_range=(60, 95),
        )
        self.assertTupleEqual(g.log_scale(20, 60), (0, 300))
        self.assertTupleEqual(g.log_scale(20, 95), (0, 0))
        self.assertTupleEqual(g.log_scale(20000, 60), (700, 300))
        self.assertTupleEqual(g.log_scale(20000, 95), (700, 0))

    def test_log_scale(self):
        g = Graph(
            total_size=(1000, 600),
            graph_size=(700, 300),
            graph_offset=(0, 0),
            freq_range=(20, 20000),
            amp_range=(60, 95),
        )
        self.assertTupleEqual(g.log_scale(20, 60), (0, 300))
        self.assertTupleEqual(g.log_scale(20, 95), (0, 0))
        self.assertTupleEqual(g.log_scale(20000, 60), (700, 300))
        self.assertTupleEqual(g.log_scale(20000, 95), (700, 0))

    def test_file_creation(self):
        if 'test_output.svg' in os.listdir('svg_output'):
            os.unlink('svg_output/test_output.svg')
        g = Graph(file_name='svg_output/test_output.svg')
        g.render()
        self.assertTrue('test_output.svg' in os.listdir('svg_output'))
        os.unlink('svg_output/test_output.svg')

    def test_render(self):
        if 'example_output.svg' in os.listdir('svg_output'):
            os.unlink('svg_output/example_output.svg')
        g = Graph(file_name='svg_output/example_output.svg')
        # Render some points
        g.draw_point(120,10);
        g.draw_point(130,20);
        g.draw_point(140,30);
        g.draw_point(150,40);
        g.draw_point(160,50);
        g.render()


if __name__ == '__main__':
    unittest.main()
