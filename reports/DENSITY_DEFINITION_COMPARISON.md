# Density Definition Comparison Report — Project Atlas Phase 1.7

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.7 Multi-Metric Prioritization Comparison  
**Date**: 2026-08-17T22:55:00Z  

---

## Evaluation of Prioritization Metrics (Metrics A through H)

| Metric | Definition | Correlation with Anomaly Yield | Interpretability | Recommended Role |
| :--- | :--- | :--- | :--- | :--- |
| **$D_{\text{raw}}$ (Metric A)** | Unique historical URLs | Moderate ($r_s = 0.42$) | High | **Primary Prioritization Feature** |
| **$D_{\text{year}}$ (Metric B)** | Unique paths / years | Moderate ($r_s = 0.38$) | High | Secondary Control |
| **$D_{\text{capture}}$ (Metric C)** | Unique paths / captures | Low ($r_s = 0.15$) | Medium | Prone to crawl frequency bias |
| **$D_{\text{span}}$ (Metric D)** | Calendar years span | Weak ($r_s = 0.22$) | High | Temporal baseline |
| **$D_{\text{user}}$ (Metric E)** | User-space path count | **Highest ($r_s = 0.68$)** | Very High | **Primary Sub-Feature for User Tildes** |
| **$D_{\text{legacy}}$ (Metric F)**| Archive/legacy directory count | Moderate ($r_s = 0.35$) | High | Structural sub-feature |
| **$D_{\text{diversity}}$ (Metric G)**| Shannon path-type entropy | Moderate ($r_s = 0.31$) | High | Diversity proxy |
| **$D_{\text{content}}$ (Metric H)**| Unique content digests | Moderate ($r_s = 0.40$) | Medium | Content churn proxy |
