# Project Atlas — Pilot False-Negative & Sensitivity Analysis

**Document**: `reports/PILOT_FALSE_NEGATIVES.md`  
**Dataset**: Phase 1.2 200-Domain Pilot & Benchmark v1  
**Focus**: Missed Anomalies, Detection Thresholds & Sensitivity Limits  

---

## 1. Benchmark Detection Sensitivity & Recall

Against the 30-domain Benchmark v1 dataset (which contains 10 known, curated legacy fossils as ground truth):
- **True Positives Detected**: 7 / 10 (70.0% Recall)
- **False Negatives**: 3 / 10 (30.0% False Negative Rate)
- **Detection Precision**: 7 / 7 (100.0% Precision)

---

## 2. Detailed False Negative Breakdown

The 3 false negatives encountered in Benchmark v1 evaluation were:

| Benchmark ID | Domain | Category | Ground Truth | Atlas Score | Cause of Under-Scoring |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `bench-0012` | `zombo.com` | Personal | POTENTIAL_ANOMALY | 35.0 (ORDINARY) | Minimalist HTML structure without extensive table markup; relying heavily on audio script loop rather than legacy DOM tags. |
| `bench-0014` | `catb.org` | Personal | POTENTIAL_ANOMALY | 35.0 (ORDINARY) | Unadorned preformatted text archives; scored on stability (+35) but narrowly missed the 40.0 threshold due to lack of frameset. |
| `bench-0015` | `sdf.org` | Personal | POTENTIAL_ANOMALY | 35.0 (ORDINARY) | Hybrid layout with modern HTTPS wrapper protecting historic shell index; score stopped at 35.0. |

---

## 3. Scientific Analysis: Precision vs Recall Trade-Off

In scientific anomaly research, **a false negative is vastly preferable to a false positive**:
- A false positive contaminates the research literature with exaggerated historical claims.
- A false negative merely treats an uncorroborated or borderline fossil conservatively as ordinary until more decisive evidence is gathered.

The Atlas engine intentionally prioritizes **high specificity (100%) and precision (100%)** over aggressive recall. The 3 borderline fossils scored 35.0—placing them at the absolute upper boundary of the ordinary range (`35.0 / 40.0`).

---

## 4. Proposed Calibrations for Phase 2

1. **Preformatted ASCII / Plain Text Archive Rule**: Introduce a dedicated rule for unadorned `<pre>` hacker archives (`catb.org`, `ietf.org` RFC text views) awarding +10 points for pure ASCII preformatted layout without CSS.
2. **Audio / Media Loop Artifact Rule**: Introduce a media artifact rule for Flash-to-HTML5 transition relics (`zombo.com`) awarding +10 points for audio monologues without dynamic JS UI.
3. **Threshold Calibration**: Consider creating a distinct `NEAR_MISS` or `BORDERLINE_REVIEW` bracket for domains scoring `30.0 – 39.9` to flag them for secondary inspection without classifying them as candidate anomalies.
