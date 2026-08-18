# Project Atlas — Treasure Review Runbook
## Operator & Reviewer Guide for Human Review Console

```
=====================================================================================
                           TREASURE REVIEW OPERATOR RUNBOOK
=====================================================================================
```

### 1. Quick Start Commands

#### Inspect Dashboard Status
```bash
python3 -m atlas.cli treasure review status
```
*Outputs total packets, reviewed count, remaining count, and active reviewer count.*

#### Inspect the Next Review Packet
```bash
python3 -m atlas.cli treasure review next
```
*Renders the mobile-first vertical evidence view for the next unreviewed candidate.*

#### Inspect a Specific Packet or Candidate
```bash
python3 -m atlas.cli treasure review show --id REV_PKT_V2_001
# Or by Candidate ID:
python3 -m atlas.cli treasure review show --id TCAND_0106
```

#### Submit a Human Review Verdict
```bash
python3 -m atlas.cli treasure review submit \
  --packet-id REV_PKT_V2_001 \
  --reviewer HUMAN_ARCHAEOLOGIST_01 \
  --verdict POTENTIAL_TREASURE \
  --confidence 0.85 \
  --notes "Authentic serialized fictional log format from early community archives."
```

#### Export Review Session for Offline Review
```bash
python3 -m atlas.cli treasure review export --file data/treasure_runs/TREASURE_RUN_0003/review_v2/review_session.json
```

#### Import External / Completed Human Reviews
```bash
python3 -m atlas.cli treasure review import --file data/treasure_runs/TREASURE_RUN_0003/review_v2/review_session.json
```

#### Run Neutrality Audit
```bash
python3 -m atlas.cli treasure review audit
```

#### Run 15-Point Release Gate
```bash
python3 -m atlas.cli treasure release-check --run-id TREASURE_RUN_0003
```

---

### 2. Evaluative Guidelines for Reviewers

- **Do Not Look for Modern Styling**: Historical artifacts frequently use table layouts, pre-CSS typography, and vintage markup.
- **Inspect Archive Provenance**: Look at earliest historical capture dates and persistence over time.
- **Verify Live Availability**: Ensure the HTTP response is authentic (HTTP 200) with intact content.
- **Provide Justification**: Briefly note why the surface is unique, obscure, or historically noteworthy in the `--notes` argument.
