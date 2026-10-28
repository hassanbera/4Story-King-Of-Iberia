import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from import_soldier_walk import convert


def samples(points):
    return [[str(i * 500), '0', *map(str, p)] for i, p in enumerate(points)]


class RecordedWalkTests(unittest.TestCase):
    def test_preserves_valley_instead_of_interpolating_endpoint_heights(self):
        points = [[i * 2, 95 - min(i, 18, 40-i), 0] for i in range(41)]
        route = convert(samples(points), points[0], points[-1])
        self.assertEqual(min(p[1] for p in route), 77)
        self.assertLessEqual(abs(route[-1][0] - 80), 6)

    def test_rejects_unfinished_walk(self):
        with self.assertRaisesRegex(ValueError, 'completed walk'):
            convert(samples([[i, 95, 0] for i in range(6)]), [0, 95, 0], [100, 80, 0])

    def test_rejects_teleport_gap(self):
        with self.assertRaisesRegex(ValueError, 'Discontinuous'):
            convert(samples([[0, 95, 0], [2, 95, 0], [4, 95, 0], [60, 95, 0], [78, 95, 0], [80, 95, 0]]),
                    [0, 95, 0], [80, 95, 0])


if __name__ == '__main__':
    unittest.main()
