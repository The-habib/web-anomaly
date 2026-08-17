"""Unit tests for Experiment Ledger."""

import unittest
import tempfile
import shutil
from pathlib import Path
from atlas.experiments.ledger import ExperimentLedger

class TestExperimentLedger(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.ledger = ExperimentLedger(base_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_auto_incrementing_ids(self):
        id1 = self.ledger.get_next_experiment_id()
        self.assertEqual(id1, "0001")

        exp1_dir = self.ledger.create_experiment(title="Exp 1", hypothesis="Hypothesis 1")
        self.assertEqual(exp1_dir.name, "0001")

        id2 = self.ledger.get_next_experiment_id()
        self.assertEqual(id2, "0002")

        exp2_dir = self.ledger.create_experiment(title="Exp 2", hypothesis="Hypothesis 2")
        self.assertEqual(exp2_dir.name, "0002")

    def test_scaffold_files_created(self):
        exp_dir = self.ledger.create_experiment(title="Test Scaffold", hypothesis="Test Hypothesis")
        self.assertTrue((exp_dir / "hypothesis.md").exists())
        self.assertTrue((exp_dir / "setup.md").exists())
        self.assertTrue((exp_dir / "notes.md").exists())
        self.assertTrue((exp_dir / "result.md").exists())
        self.assertTrue((exp_dir / "experiment.json").exists())
        self.assertTrue((exp_dir / "evidence").is_dir())

if __name__ == "__main__":
    unittest.main()
