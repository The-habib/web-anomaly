# Project Atlas — Phase 1.7 Pre-Registration Protocol

**Project**: Atlas — Web Anomaly Research Laboratory  
**Document**: Phase 1.7 Scientific Pre-Registration Protocol  
**Date**: 2026-08-17T22:54:30Z  
**Status**: **FROZEN PRE-EXECUTION PROTOCOL**  

---

## 1. Research Questions & Hypotheses

### Primary Research Question
> *«Does historical/public path density improve the efficiency of selecting domains for deep web archaeology under an equal research budget compared to uniform random selection?»*

### Primary Hypothesis ($\mathbf{H}_{\text{density}}$)
Under equal retrieval constraints ($\le 15$ retrievals/domain), domain cohorts selected from the upper tail of historical path density will yield a statistically significant higher rate of independently validated archaeological discoveries per 1,000 successful deep retrievals than cohorts selected uniformly at random from the same population.

### Null Hypothesis ($\mathbf{H}_0$)
There is no statistically significant difference in validated discovery yield between path-density-prioritized domains and uniform random domains ($RR = 1.0$).

### Secondary Research Questions
1. Is raw historical URL count ($D_{\text{raw}}$) or normalized rate ($D_{\text{year}}$, $D_{\text{capture}}$) a stronger predictor?
2. Is user-space density ($D_{\text{user}}$) or legacy directory density ($D_{\text{legacy}}$) more informative than generic volume?
3. Does path diversity ($D_{\text{diversity}}$) explain discovery yield better than raw volume?
4. Does the density effect survive strict category matching?
5. Does the effect survive removal of the extreme anchor domain (`thunix.net`)?
6. Does the effect generalize to an unseen holdout set ($N=200$ domains)?
7. Does density prioritization increase false-positive rates?

---

## 2. Quantitative Success Metrics & Primary Outcome

### Primary Outcome
$$\text{Yield}_{\text{retrieval}} = \frac{\text{Validated Discoveries}}{\text{Successful Deep Retrievals}} \times 1,000$$

### Secondary Outcomes
- $\text{Yield}_{\text{domain}} = \frac{\text{Validated Discoveries}}{\text{Evaluated Domains}} \times 100$
- **Discovery Rate Ratio ($RR$)**: $RR = \frac{\text{Yield}_D}{\text{Yield}_U}$
- **False Positive Rate**: $\text{FPR} = \frac{\text{False Positives}}{\text{Evaluated Domains}} \times 100$
- **Cost Efficiency**: Megabytes downloaded and seconds elapsed per validated discovery.

---

## 3. Density Feature Definitions (Metrics A through H)

1. **Metric A ($D_{\text{raw}}$)**: Total unique normalized historical URLs observed in public index metadata.
2. **Metric B ($D_{\text{year}}$)**: $D_{\text{raw}} / \text{Observed Web-History Years}$.
3. **Metric C ($D_{\text{capture}}$)**: $D_{\text{raw}} / \text{Total Index Captures}$.
4. **Metric D ($D_{\text{span}}$)**: $\text{Latest Observed Year} - \text{Earliest Observed Year}$.
5. **Metric E ($D_{\text{user}}$)**: Count of paths matching public user spaces (`/~user/`, `users/`, `people/`, `faculty/`, `staff/`, `students/`).
6. **Metric F ($D_{\text{legacy}}$)**: Count of paths matching legacy markers (`old/`, `archive/`, `history/`, `legacy/`, `pub/`, `ftp/`, `doc/`).
7. **Metric G ($D_{\text{diversity}}$)**: Shannon entropy $H = -\sum p_i \ln p_i$ across 14 deterministic path-type categories.
8. **Metric H ($D_{\text{content}}$)**: Number of unique content digests observed across historical captures.

---

## 4. Deterministic Path-Type Taxonomy

All discovered paths are classified into exactly one primary category:
- `ROOT`: Canonical homepage (`/`, `index.html`)
- `USER_SPACE`: Academic and multi-user tilde directories (`/~[name]`, `~[name]`, `users/`)
- `ARCHIVE`: Historical and backup archives (`/old/`, `/archive/`, `/history/`, `/legacy/`)
- `DOCS`: Documentation, manuals, RFCs (`/doc/`, `/man/`, `/rfc/`, `/manual/`)
- `PERSONAL`: Individual personal pages and blogs (`/people/`, `/personal/`, `/blog/`)
- `SOFTWARE`: Code repositories, software packages (`/src/`, `/software/`, `/code/`)
- `PROJECT`: Research projects, labs, initiatives (`/projects/`, `/lab/`)
- `FILES`: Download mirrors, distribution directories (`/pub/`, `/files/`, `/dist/`)
- `MEDIA`: Audio, video, vintage interactive embeds (`/media/`, `/audio/`, `/swf/`)
- `RESEARCH`: Papers, technical reports, preprints (`/research/`, `/papers/`)
- `DIRECTORY`: Generic nested directory indices
- `OTHER`: Unclassified valid URL paths

---

## 5. Experimental Population, Arms & Holdout Design

- **Starting Population**: Atlas Corpus v2 ($N=1,000$ curated real-world domains).
- **Holdout Reservation**: Prior to arm assignment, $N=200$ domains are drawn via stratified random sampling (`seed=42`) and reserved as an untouched holdout set.
- **Eligible Experimental Pool**: Remaining $N=800$ domains.
- **Arm U (Uniform Random Selection)**: $N=100$ domains drawn uniformly at random from the eligible pool.
- **Arm D (Density Prioritized)**: $N=100$ domains drawn from the highest $D_{\text{raw}}$ tail, matched across the 6 Corpus v2 categories.
- **Blinded Internal Labels**: The deep archaeology executor receives domains under randomized blinded identifiers (`STUDY_A` vs `STUDY_B`).

---

## 6. Equal Research Budget & Operational Fairness

Both arms receive strictly identical resource allocations:
- Maximum candidate paths per domain: **100**
- Maximum targeted retrievals per domain: **15**
- Network HTTP timeout: **5.0 seconds**
- Evidence capture: Full HTML raw payload frozen with cryptographic SHA-256 digest
- Scoring Engine: Strictly frozen Phase 1.5 anomaly scoring engine ($\ge 50.0$ threshold for `CANDIDATE_ANOMALY`).

---

## 7. Blind Human Review & Discovery Validation

- **Review Blinding**: Reviewers are blinded to density tier, numerical scores, and arm identity.
- **Review Sample**: Includes all candidates scoring $\ge 40.0$, a stratified sample of near-threshold domains ($20.0-35.0$), and random negative controls.
- **Validation Criteria**: A validated discovery requires:
  1. Cryptographically intact frozen HTML payload in `data/phase1_7/evidence/raw_artifacts/`.
  2. Anomaly score $\ge 50.0$ (`CANDIDATE_ANOMALY`).
  3. Positive reviewer verdict (`CLEAR_ANOMALY`).
  4. Documented archaeological novelty (`OBSCURE` / `NEW_TO_ATLAS`).

---

## 8. Planned Statistical Analysis & Stopping Rules

- **Primary Statistical Test**: Fisher's exact test (two-tailed) comparing discovery yield between Arm D and Arm U.
- **Rate Ratio Estimation**: $RR = \text{Yield}_D / \text{Yield}_U$ with 95% bootstrap confidence intervals.
- **Thunix Sensitivity Analysis**: Calculation of $RR$ with and without `thunix.net`.
- **Generalization Test**: Execution of the identical prioritization rule on the $N=200$ holdout set.
- **Stopping Rule**: The experiment must execute all assigned domains to completion without early stopping.
