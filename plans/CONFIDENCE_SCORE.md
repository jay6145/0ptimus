# Confidence Score — What It Is and How It’s Calculated

## What is the confidence score for?

The **confidence score** (0–100) answers:

**“How much can we trust the on-hand inventory for this SKU at this store?”**

- **High score (e.g. 90+):** Records are likely accurate; fewer unexplained drops; recent cycle count; no systematic shrink pattern.
- **Low score (e.g. &lt;70):** Records may be wrong; more anomalies; no recent count or possible shrink/theft/errors.

It’s used to:

1. **Prioritize cycle counts** — Low-confidence items get “Schedule cycle count” and are good candidates for a physical count.
2. **Overview alerts** — “Low Confidence” count on the homepage (items with score &lt; 70).
3. **SKU detail** — Shows score, grade (A–F), and a breakdown of what lowered it.
4. **Recommendations** — Cycle count is “recommended” when score &lt; 80; “High” priority when &lt; 60.

So the score is **inventory accuracy confidence**, not demand or forecast confidence.

### Why did most items used to be C or D in the demo?

In the demo data, only 20% of SKUs had any cycle count, and those counts were spread randomly over 60 days. So most items either had **no count** (−30) or a **count from weeks ago** (−20). Many SKUs are perishable, so they also got **“perishable without recent count”** (−10). That pushed scores into the 60–70 range (C/D). The demo has been updated so **60% of SKUs get a recent cycle count** (within the last 7 days), **20% get an older count**, and **20% have no count**, giving a better spread of A/B/C/D/F.

---

## How is it calculated?

**Location:** `backend/app/services/confidence_scorer.py` → `calculate_confidence_score(db, store_id, sku_id)`.

**Idea:** Start at **100** and **subtract** points for risk factors. Result is clamped to 0–100, then mapped to a grade.

### 1. Anomaly frequency (max −30)

- **Input:** Count of **anomaly events** in the last 30 days for this store/SKU.
- **Rule:** `anomaly_penalty = min(anomaly_count * 5, 30)`.
- **Example:** 3 anomalies → −15; 6+ → −30.

*More unexplained inventory drops → lower confidence.*

### 2. Anomaly magnitude (max −20)

- **Input:** Sum of **absolute residuals** (units “lost” in those anomalies) in the last 30 days.
- **Rule:** `magnitude_penalty = min(total_residual * 0.5, 20)`.
- **Example:** 20 units total residual → −10; 40+ → −20.

*Larger unexplained drops → lower confidence.*

### 3. Days since last cycle count (max −20)

- **Input:** Days since the **most recent cycle count** for this store/SKU.
- **Rule:** `count_penalty = min(days_since_count * 0.3, 20)`.
- **If never counted:** −30 (not −20).

*Longer since a physical count → lower confidence.*

### 4. Perishable without recent count (−10)

- **Input:** SKU is **perishable** and (no cycle count **or** last count &gt; 7 days ago).
- **Rule:** −10.

*Perishable items need more frequent verification.*

### 5. Systematic shrink pattern (−15)

- **Input:** `find_anomaly_patterns(db, store_id, sku_id, days=30)` from the anomaly detector.
- **Rule:** If `has_pattern` is True (e.g. many negative residuals in a short window), −15.

*Repeated shrink-like pattern → lower confidence.*

---

## Formula (conceptual)

```text
score = 100
score -= min(anomaly_count * 5, 30)           # 1. Anomaly frequency
score -= min(total_residual * 0.5, 20)        # 2. Anomaly magnitude
score -= min(days_since_count * 0.3, 20)      # 3. Days since count (or −30 if never)
# or if never counted: score -= 30
if perishable and (no count or count > 7 days): score -= 10   # 4. Perishable
if systematic_shrink_pattern: score -= 15                      # 5. Pattern

final_score = max(0, min(100, score))
```

---

## Grade mapping

| Score  | Grade |
|--------|--------|
| 90–100 | A     |
| 80–89  | B     |
| 70–79  | C     |
| 60–69  | D     |
| 0–59   | F     |

---

## Where it’s used in the app

| Place            | Use |
|------------------|-----|
| **Overview**      | Per-row confidence score/grade; “Low Confidence” alert count (items &lt; 70). |
| **SKU detail**   | Current score, grade, and “Confidence Score Breakdown” (list of deductions). |
| **Recommendations** | “Cycle count recommended” when score &lt; 80; “High/Medium/Low” when &lt; 60 / &lt; 80 / else. |
| **API**          | `calculate_confidence_score()`; overview and SKU endpoints include `confidence_score` and `confidence_grade`. |

---

## Summary

- **Purpose:** Measure how much you can trust **inventory accuracy** for a store/SKU (not demand or forecast).
- **Calculation:** Start at 100; subtract for anomaly count, anomaly size, days since (or lack of) cycle count, perishable without recent count, and systematic shrink pattern; clamp to 0–100; map to A–F.
- **Code:** `backend/app/services/confidence_scorer.py` → `calculate_confidence_score()`.
