# Stage 2 pre-registration

> **Status: DRAFT, not frozen.** Nothing here is binding until the commit is tagged `prereg-v1`.
> Freeze it **before** running any Stage 2 regression, and after that, record every deviation in
> the log at the bottom instead of editing the spec in place.
>
> Freeze with:
> ```bash
> git tag -a prereg-v1 -m "Freeze Stage 2 main specification"
> ```
> then push the tag (`git push origin prereg-v1`).

The defaults below come from [`design.md`](design.md). Items marked **DECIDE** need a deliberate choice
before freezing; the default is a starting point, not a recommendation from the data.

## 1. Sample

- **Seasons:** 2015, 2019, 2023, 2026.
- **Season window:** 1 August to 30 November of each year. **DECIDE:** fixed calendar window vs a window
  defined by FIRMS activity in Sumatra/Kalimantan. A data-defined window is a forking path; the
  calendar window is the default for that reason.
- **Universe:** SGX: First Resources, Bumitama Agri, Golden Agri-Resources, Wilmar, Indofood Agri.
  IDX: Astra Agro Lestari, SMART, London Sumatra, Salim Ivomas, Sawit Sumber Mas, Dharma Satya Nusantara.
  A firm-season enters only if the firm was listed for the whole season and its estimation window.
- **Exclusions:** IDX auto-reject limit days are dropped (flag kept for a robustness run). Firm-days
  with zero volume are dropped.

## 2. Outcome

- **AR<sub>i,t</sub>:** daily abnormal return from a market model on the home index (STI for SGX names,
  JCI for IDX names) plus the CPO futures return. The model is estimated per firm-season over 1 February
  to 30 June of the same year, so the estimation window never overlaps the haze season.
- **CPO series:** Bursa FCPO front-month (manual CSV). Soybean oil is a robustness check only.

## 3. Fire exposure

- **Detections:** VIIRS S-NPP 375 m (available from 2012, so all four seasons use the same sensor).
  NOAA-20 and MODIS are robustness checks only.
- **Confidence filter:** nominal + high; low-confidence detections are dropped.
- **Exposure:** Fire<sub>i,t</sub> = hotspots inside firm *i*'s concessions on day *t* ÷ (total concession
  area in ha ÷ 1,000).
- **Parent links:** all links with confidence medium or high enter the main spec; high-only is a robustness run.
- **Day assignment:** detections are assigned to the local (WIB/SGT) calendar date of acquisition.
  **DECIDE:** whether a detection acquired after the 17:00 SGX close is assigned to the next trading day.
  Default: yes, because it cannot be priced the same day.

## 4. Salience

- **HighPSI<sub>t</sub>** = 1 if Singapore's 24-hour PSI (maximum across regions) exceeds 100 (NEA's
  "unhealthy" band) at the 12:00 SGT reading on day *t*.
  **DECIDE:** reading time. Noon is observable during the trading day; a later reading would let PSI
  partly reflect the afternoon's news.

## 5. Main specification

```
AR_{i,t} = α_i + Σ_{k=1}^{10} β_k Fire_{i,t−k} + γ (Fire_{i,t−1} × HighPSI_t) + δ HighPSI_t
           + θ r^CPO_t + λ_season + ε_{i,t}
```

- Firm and season fixed effects.
- Standard errors clustered by date. Because there are fewer than 20 firms, wild-cluster bootstrap
  p-values (clustered by date, Webb weights, 9,999 replications) are the reported inference.

## 6. Hypothesis tests (the only confirmatory tests)

| Hypothesis | Statistic | Direction | Level |
| --- | --- | --- | --- |
| H1 fire exposure predicts returns | Cumulative effect Σ<sub>k=1..10</sub> β<sub>k</sub> | One-sided, < 0 | 5% |
| H2 salience gates the reaction | γ | One-sided, < 0 | 5% |

One statistic per hypothesis, so there is no correction across lags. Individual β<sub>k</sub> are reported
descriptively. Effect sizes are reported in basis points per one-SD change in Fire.

## 7. Robustness (exploratory, reported but not confirmatory)

- Buffer exposure at 2 km and 5 km, entered alongside inside exposure (H5).
- PSI cutoffs 150 and 200; continuous PSI.
- High-confidence parent links only; MODIS detections; FCPO-hedged returns; soybean oil control.
- IDX limit days kept with a flag; Dimson betas for thin traders.
- Wind instrument for HighPSI (Stage 3), reported separately.

## 8. What a null means

If neither H1 nor H2 is rejected, the write-up reports it as evidence that the haze price reaction
is driven by regulatory events rather than slow processing of satellite information (design.md,
"Threats to validity").

## Deviation log

| Date | Change | Reason |
| --- | --- | --- |
| | | |
