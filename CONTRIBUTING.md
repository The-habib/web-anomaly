# Contributing to Project Atlas

Thank you for your interest in contributing to Project Atlas. This guide outlines how to create new experiments, add anomaly detectors, and improve the research pipeline.

---

## 🔬 How to Conduct an Experiment

1. **Provision a New Experiment**:
   Use the Atlas CLI or script to generate the next numbered experiment folder:
   ```bash
   atlas experiment new "Investigation of 1990s Web Directories" --hypothesis "Open directory indexes on legacy academic subdomains preserve 1990s HTML 2.0/3.2 markup."
   ```

2. **Define Candidate Targets in `setup.md`**:
   Add candidate URLs to your experiment directory (`experiments/XXXX/setup.md`).

3. **Run Pipeline on Target Candidates**:
   ```bash
   atlas scan https://target-url.edu/legacy/
   ```

4. **Log Notes & Observations**:
   Update `experiments/XXXX/notes.md` with observations during your investigation.

5. **Document Results & Findings**:
   Link the generated finding reports (`reports/REPORT_ATLAS-*.md`) into `experiments/XXXX/result.md` and update `DISCOVERIES.md`.

---

## ⚙️ Adding New Anomaly Signals

To introduce a new anomaly signal:

1. **Register the Rule**: Add the signal definition and weight in `atlas/config/scoring_rules.json`:
   ```json
   {
     "id": "my_new_signal",
     "name": "My New Anomaly Signal",
     "category": "technological",
     "weight": 3,
     "description": "Description of the anomaly condition."
   }
   ```

2. **Implement the Detector**: Add evaluation logic in `atlas/scoring/scorer.py` under `AnomalyScorer.evaluate()`.

3. **Write Unit Tests**: Add test cases in `tests/test_scorer.py` verifying that the detector fires appropriately on matching HTML/timeline fixtures.

---

## 🧪 Running Laboratory Tests

Run the full test suite before submitting any changes:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Verify laboratory readiness and toolchain health:
```bash
python3 scripts/verify_environment.py
```

---

## 📝 Commit Conventions

Use Conventional Commits:
- `feat:` for new capabilities, detectors, or pipeline stages.
- `fix:` for bug fixes in clients, scorers, or formatters.
- `docs:` for improvements to documentation or experiment notes.
- `test:` for adding or updating unit/integration tests.
- `refactor:` for architectural refactoring without functional alterations.
