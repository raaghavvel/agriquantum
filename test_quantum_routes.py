import unittest
import numpy as np
import pandas as pd
from data_loader import DataLoader
from quantum_routes import candidates, solve_quantum, benchmarks, evolve

class QuantumRouteTests(unittest.TestCase):
    def test_circuit_equivalence(self):
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import DiagonalGate
        from qiskit.quantum_info import Statevector
        energies = np.array([-.8,-.3,.2,3.])
        theta = [.4,.7,.2,.6]
        circuit = QuantumCircuit(2)
        circuit.h(range(2))
        for k in range(2):
            circuit.append(DiagonalGate(np.exp(-1j*theta[k]*energies)),range(2))
            circuit.rx(2*theta[2+k],range(2))
        np.testing.assert_allclose(evolve(energies,theta),Statevector.from_instruction(circuit).data,atol=1e-12)

    def test_full_dataset_top_three_and_capacity(self):
        loader=DataLoader()
        df, unsold=candidates(loader,'S001','C015',100.,24.)
        self.assertGreater(len(df),18)
        q=solve_quantum(df,unsold,iterations=30)
        self.assertEqual(len(q['top']),3)
        self.assertTrue((q['top'].shots>0).all())
        self.assertTrue((q['top'].capacity_kg>=100).all())
        self.assertLessEqual(q['qubits'],9)
        before=q['top'].copy(deep=True)
        baseline,_=benchmarks(df,unsold)
        self.assertLessEqual(q['objective'],baseline.iloc[0].objective+1e-6)
        pd.testing.assert_frame_equal(before,q['top'])
        huge,_=candidates(loader,'S001','C015',1e9,24.)
        self.assertTrue(huge.empty)

    def test_small_and_invalid(self):
        df=pd.DataFrame([dict(market_id='M1',net_margin=100.)])
        result=solve_quantum(df,10.,iterations=20)
        self.assertEqual(len(result['top']),1)
        self.assertEqual(result['qubits'],1)
        with self.assertRaises(ValueError):
            solve_quantum(pd.DataFrame(),10.)
        with self.assertRaises(ValueError):
            candidates(DataLoader(),'S001','C015',-1.,24.)

if __name__=='__main__':
    unittest.main()
