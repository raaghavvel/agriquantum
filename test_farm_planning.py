import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from data_loader import DataLoader
from farm_planning import farm_loader, route_data
from problem_builder import ProblemBuilder
from quantum_optimizer import QuantumFarmOptimizer


class FarmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = DataLoader(str(Path(__file__).parent / 'data'))

    def setUp(self):
        self.farms = pd.DataFrame([dict(source_id='F1', source_name='Test farm', latitude=11., longitude=77.)])
        self.batches = pd.DataFrame([dict(batch_id='B1', source_id='F1', crop_id='C015', quantity_kg=100., max_delivery_hours=24.)])

    def test_all_market_optimum_and_tooltips(self):
        loader = farm_loader(self.base, self.farms, self.batches)
        p = ProblemBuilder(loader).build(max_batches=1, all_markets=True)
        opt = QuantumFarmOptimizer(p)
        result = opt.solve_classical_milp()
        self.assertTrue(result['is_feasible'])
        feasible = p.feasible[0] & (p.market_capacity_kg >= 100)
        expected = max(0, p.profit_gain[0, feasible].max()) - p.unsold_penalty[0]
        self.assertAlmostEqual(result['net_objective'], expected, places=4)
        routes, points = route_data(p, result['assignments'], loader)
        self.assertTrue(routes.tooltip.str.len().gt(0).all())
        self.assertTrue(points.tooltip.str.len().gt(0).all())
        self.assertEqual(set(routes.src_lat), {11.})
        self.assertEqual(set(points.kind), {'Source', 'Market'})
        self.assertNotIn('F1', set(self.base.sources.source_id))

    def test_gps_changes_travel(self):
        a = farm_loader(self.base, self.farms, self.batches)
        self.farms.loc[0, 'latitude'] = 12.
        b = farm_loader(self.base, self.farms, self.batches)
        self.assertNotEqual(a.travel_dict, b.travel_dict)

    def test_invalid_inputs(self):
        for col, val in [('quantity_kg', -1), ('crop_id', 'BAD'), ('source_id', 'MISSING')]:
            data = self.batches.copy()
            data.loc[0, col] = val
            with self.assertRaises(ValueError):
                farm_loader(self.base, self.farms, data)
        self.farms.loc[0, 'latitude'] = np.nan
        with self.assertRaises(ValueError):
            farm_loader(self.base, self.farms, self.batches)


if __name__ == '__main__':
    unittest.main()
