# Project Atlas — Treasure Review Protocol
## Independent Human Review Methodology & Quality Assurance

```
=====================================================================================
                           HUMAN REVIEW PROTOCOL SPECIFICATION
=====================================================================================
```

### 1. Review Population & Control Formulation

The Run #003 review dataset is prepared in [`data/treasure_runs/TREASURE_RUN_0003/review_v2/`](file:///workspaces/web-anomaly/data/treasure_runs/TREASURE_RUN_0003/review_v2/) consisting of:
- **41 Treasure Candidates**: Nominated during blind discovery.
- **10 Random Dismissed Controls**: Selected from the ordinary population.
- **Total Review Packets**: 51 packets.
- **Interleaving Seed**: Deterministic PRNG Seed `303`. Candidates and controls are randomized together so the reviewer cannot determine whether a packet is a machine-nominated candidate or an ordinary baseline control.

---

### 2. Evaluative Verdicts

Reviewers evaluate each packet independently using four mutually exclusive verdicts:

| Verdict | Definition | Promotion Effect |
| :--- | :--- | :--- |
| `CLEAR_TREASURE` | Authentic surviving historical/obscure artifact with deep preservation value. | Eligible for Living Web Museum exhibit upon confidence $\ge 0.8$. |
| `POTENTIAL_TREASURE` | Notable or anomalous web surface requiring further archival investigation. | Placed in `POTENTIAL_TREASURES` research registry. |
| `ORDINARY` | Modern boilerplate, active commercial site, generic CMS, or ordinary surface. | Marked ordinary; excluded from museum promotion. |
| `INSUFFICIENT_EVIDENCE` | Broken artifact, missing raw evidence, or unverifiable state. | Returned to investigation queue for re-capture. |

---

### 3. Reviewer Prompts & Cognitive Guidance

To eliminate confirmation bias, the review console prompts the reviewer with neutral analytical questions:
1. *What is unusual or historically noteworthy about this surface?*
2. *Is this page still functioning as an authentic public web artifact?*
3. *Would an ordinary web user easily discover this without specialized archaeological discovery engines?*
4. *What elements might make this page ordinary or generic instead?*

---

### 4. Multi-Reviewer Dispute Resolution

If two independent reviewers evaluate the same candidate:
- **Consensus**: When verdicts match, consensus is recorded.
- **Disagreement**: When verdicts differ (e.g. `CLEAR_TREASURE` vs `ORDINARY`), the candidate is flagged with `SECOND_REVIEW_REQUIRED` and scheduled for third-party arbitration.
- **Anti-Fabrication Policy**: Atlas records `reviewer_count = 1` for single-reviewer sessions and never fabricates synthetic inter-rater reliability scores.
