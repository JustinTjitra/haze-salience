# Econometric methods and Python implementations for the haze-fire event study and panel (as of 2026-11-20)

VERIFICATION STATUS (read first). In this session only pypi.org, github.com and a web-search tool were reachable. These hosts failed DNS and could not be fetched: arxiv.org, api.crossref.org, py-econometrics.github.io (pyfixest docs), bashtage.github.io (linearmodels docs), www.statsmodels.org, and the journal sites. So:
- "VERIFIED" = read on a fetched page this session (URL given).
- "UNVERIFIED-AT-SOURCE" = bibliographic details and formulas written from the author's background knowledge of the literature; the DOIs are given as stable identifiers but were NOT resolved here. An implementing agent should check each DOI with `https://doi.org/<DOI>` before citing, and should check each package signature with `help()` in the installed version before coding against it.
- The date-of-release of package versions is not shown on the PyPI JSON pages that were read (the pages were truncated); only version numbers are verified.

## 1. Event-study methodology and test statistics (Patell, BMP, Kolari-Pynnonen, Corrado, GRANK); 5 firms on the same date; two events 11 days apart

### Takeaway
With 5 firms sharing identical calendar event dates, abnormal returns are cross-sectionally correlated, so the Patell and plain BMP tests over-reject. Use the Kolari-Pynnonen (2010) adjusted BMP statistic with a t(N-1) reference, and cross-check with a calendar-time equally-weighted portfolio time-series test (which handles the correlation by construction). Treat any N=5 rank-test result as low-powered. Hand-rolling is standard.

### Cited Findings (all UNVERIFIED-AT-SOURCE; citation details from background knowledge)
- Canonical references: Brown & Warner (1985), "Using daily stock returns: The case of event studies", J. Financial Economics 14(1):3-31, doi:10.1016/0304-405X(85)90042-X; MacKinlay (1997), "Event studies in economics and finance", J. Economic Literature 35(1):13-39, https://www.jstor.org/stable/2729691; Campbell, Lo & MacKinlay (1997), The Econometrics of Financial Markets, Princeton UP, ch. 4; Kothari & Warner (2007), "Econometrics of event studies", Handbook of Corporate Finance Vol. 1 ch. 1, Elsevier, doi:10.1016/B978-0-444-53265-7.50015-9.
- Patell (1976), J. Accounting Research 14(2):246-276, doi:10.2307/2490543. Boehmer, Musumeci & Poulsen (1991), J. Financial Economics 30(2):253-272, doi:10.1016/0304-405X(91)90032-F. Kolari & Pynnonen (2010), "Event study testing with cross-sectional correlation of abnormal returns", Review of Financial Studies 23(11):3996-4025, doi:10.1093/rfs/hhq072. Corrado (1989), J. Financial Economics 23(2):385-395, doi:10.1016/0304-405X(89)90064-0; Corrado & Zivney (1992), J. Financial and Quantitative Analysis 27(3):465-478, doi:10.2307/2331331. Kolari & Pynnonen (2011), "Nonparametric rank tests for event studies", J. Empirical Finance 18(5):953-971, doi:10.1016/j.jempfin.2011.08.003 (generalized rank test, GRANK).
- Formulas (standard; check against MacKinlay 1997 and KP 2010 before final coding). Market model on estimation window of L1 days (e.g. t=-250..-31 relative to the first event): R_it = a_i + b_i R_mt + e_it. Estimation-window residual variance s_i^2 = sum(e_is^2)/(L1-2). Abnormal return AR_it = R_it - a_i_hat - b_i_hat R_mt.
  - Forecast-error-corrected variance (Patell/MacKinlay): S^2(AR_it) = s_i^2 * [1 + 1/L1 + (R_mt - Rbar_m)^2 / sum_{s in est}(R_ms - Rbar_m)^2].
  - Standardized AR: SAR_it = AR_it / S(AR_it).
  - Patell: for event window of L2 days, CSAR_i = sum_t SAR_it, Var(CSAR_i) = L2 (L1-2)/(L1-4); Z_P = (1/sqrt(N)) * sum_i CSAR_i / sqrt(L2 (L1-2)/(L1-4)). Single-day version: Z_P(t) = sum_i SAR_it / sqrt(N (L1-2)/(L1-4)). Assumes cross-sectional independence.
  - BMP: t_BMP(t) = [ (1/N) sum_i SAR_it ] / [ s_t / sqrt(N) ], s_t^2 = (1/(N-1)) sum_i (SAR_it - mean_t)^2; for a window use SCAR_i = CSAR_i / sqrt(Var(CSAR_i)) in place of SAR. Robust to event-induced variance, not to cross-correlation.
  - Kolari-Pynnonen: t_KP = t_BMP * sqrt( (1 - rbar) / (1 + (N-1) rbar) ), where rbar = average of the N(N-1)/2 pairwise sample correlations of estimation-window residuals e_i, e_j (KP implementation: average over off-diagonal entries of the residual correlation matrix). Reference distribution t(N-1) (KP use t-test). With positive rbar this shrinks the statistic; rbar must exceed -1/(N-1).
  - Corrado rank test: pool L1+L2 days (est + event window), K_it = rank(AR_it) in 1..L; t_Corrado(0) = (Kbar_0 - (L+1)/2) / S_K, with Kbar_t = (1/N) sum_i K_it and S_K^2 = (1/L) sum_{t in pooled} (Kbar_t - (L+1)/2)^2. Compute ranks on AR (or SAR). Requires cross-sectional independence too.
  - Generalized rank (GRANK, KP 2011): use SAR (scaled by est-window s, forecast-corrected), add a synthetic "event-window CAR" day for multi-day windows, rank over pooled days, U_it = rank/(L+1); test = Ubar-based statistic with variance estimated from the cross-sectional average of ranks and a KP-type correlation correction. Exact formula not reproduced here; take it from KP (2011) Sec. 2 before coding (UNVERIFIED).
- Which test for 5 same-date firms (reasoned from KP 2010's argument that events clustered on one calendar date induce positive cross-correlation of ARs that inflates Patell/BMP rejection rates): use t_KP with t(4) critical values, and also report the calendar-time portfolio test: AR_pt = (1/N) sum_i AR_it, t = AR_pt / sd(AR_p over estimation window) (Jaffe 1974 / Mandelker 1974 style; Kothari & Warner 2007 discuss calendar-time and cross-correlation issues).
- Two events 11 days apart: no source was successfully fetched on how published studies handle this. See Gaps. Practical options consistent with Kothari & Warner (2007) logic: (a) estimation window ends before the first event window and excludes both event windows (no re-estimation between events); (b) define one pooled window spanning event 1 day -k to event 2 day +k, and test CAR over each sub-window plus the union; (c) treat events as separate and do NOT claim independence, since the windows (if +/-5 days) overlap by design 11 days apart only if k>=6.

### Inferences
- With N=5 and one calendar date, effective sample is ~1 cross-sectional draw per day; the t(N-1) KP test has little power; report the calendar-time portfolio test as primary and individual-firm SAR t-stats as descriptive.
- Because estimation-window residual correlation among 5 palm-oil stocks is probably large (shared commodity/market factor beyond the market index), rbar could be ~0.2-0.5; compute it and report the deflation factor sqrt((1-rbar)/(1+(N-1)rbar)).
- Hand-rolling is standard: ~30 lines of numpy; no maintained Python package was verified (see Q4).

### Gaps
- How published studies handle two events 11 days apart: not found (no fetchable source).
- Exact GRANK formula and the MacKinlay (1997) treatment of clustered events: not verified at source.
- All DOIs above unresolved in this session.

## 2. Thin trading, non-synchronous prices, price limits

### Takeaway
For thinly traded IDX stocks use the Dimson (1979) aggregated-coefficient beta (market return at lags -1..+1, optionally more) and compare with Scholes-Williams (1977); drop or flag zero-volume/no-trade days and handle price-limit hits explicitly (delayed price discovery per Kim & Rhee 1997).

### Cited Findings (UNVERIFIED-AT-SOURCE)
- Dimson (1979), "Risk measurement when shares are subject to infrequent trading", J. Financial Economics 7(2):197-226, doi:10.1016/0304-405X(79)90013-8. Regression: R_it = a_i + sum_{k=-K..K} b_ik R_{m,t+k} + e_it; beta_i = sum_k b_ik. Typical K=1 (or 2 for very thin stocks). Use the summed beta, abnormal return AR_it = R_it - a - sum_k b_k R_{m,t+k}. The standard error of the sum comes from the covariance matrix of the b_k.
- Scholes & Williams (1977), "Estimating betas from nonsynchronous data", J. Financial Economics 5(3):309-327, doi:10.1016/0304-405X(77)90041-1. beta_SW = (b_-1 + b_0 + b_+1) / (1 + 2 rho_m), with b_k slope of R_i on R_{m,t+k} (separate simple regressions) and rho_m first-order autocorrelation of market return.
- Kim & Rhee (1997), "Price limit performance: Evidence from the Tokyo Stock Exchange", Journal of Finance 52(2):885-901 (DOI to be verified; likely 10.1111/j.1540-6261.1997.tb02719.x). Finding as recalled: limit hits are followed by higher volatility, price continuation and delayed price discovery, so limit-day returns are censored. Not verified at source.
- Implementation note (own reasoning): flag days where |R| is within a tick of the exchange auto-rejection (ARA/ARB) limit and where volume=0; run the event study (i) with all days, (ii) excluding flagged days from estimation window, and (iii) with a limit-hit dummy; for event-window days that hit limits, report CAR over a window long enough (>=2 days) to absorb continuation.

### Inferences
- Dimson lead/lag terms use market returns from adjacent days; the event window for the AR still uses the same-day regressor set, so the market-return series needs K extra days either side.
- SGX stocks are liquid; apply Dimson mainly to IDX names (check by zero-return frequency); use the same model for both for comparability or report both.

### Gaps
- IDX specific price-limit rules and their dates (they changed during COVID and in 2023): not researched.
- Kim & Rhee DOI and findings not fetched.

## 3. Few-cluster inference; date-clustering; Petersen (2009)

### Takeaway
Clustering by date with hundreds of dates is asymptotically fine against cross-sectional correlation within a day, but it does nothing about serial correlation of a single firm's residuals over time (a firm effect) and each haze season gives few independent time blocks. With only 10-20 firms, firm-level dependence (persistent firm effects/ autocorrelation) can't be cleared by firm clustering, so use two-way (firm and date) CRV1 as the main spec and wild-cluster bootstrap as a robustness check, with caveats below.

### Cited Findings (UNVERIFIED-AT-SOURCE unless noted)
- Cameron, Gelbach & Miller (2008), "Bootstrap-based improvements for inference with clustered errors", Rev. Economics and Statistics 90(3):414-427, doi:10.1162/rest.90.3.414 (wild cluster bootstrap-t, Rademacher weights, null imposed; 6-ish clusters over-reject without it). Cameron, Gelbach & Miller (2011), "Robust inference with multiway clustering", JBES 29(2):238-249, doi:10.1198/jbes.2010.07136 (V = V_firm + V_date - V_firm-date-intersection; take non-PSD fix by eigenvalue truncation). Thompson (2011), "Simple formulas for standard errors that cluster by both firm and time", J. Financial Economics 99(1):1-10, doi:10.1016/j.jfineco.2010.08.016.
- Petersen (2009), "Estimating standard errors in finance panel data sets: Comparing approaches", Rev. Financial Studies 22(1):435-480, doi:10.1093/rfs/hhn053. As recalled: with a permanent firm effect plus a time effect, cluster by both firm and time; Fama-MacBeth only handles the time effect; with few clusters (his Monte Carlo ~ <10-20) clustered SEs are biased down. Not verified at source.
- Roodman, Nielsen, MacKinnon & Webb (2019), "Fast and wild: Bootstrap inference in Stata using boottest", Stata Journal 19(1):4-60, doi:10.1177/1536867X19830877 (algorithm underlying fwildclusterboot/wildboottest; also WCR vs WCU, and the null-imposed "restricted" version is recommended). Webb (2014), "Reworking wild bootstrap based inference for clustered errors", Queen's Univ. Working Paper 1315, https://www.econ.queensu.ca/research/working-papers/1315; published as Webb (2023), Canadian J. Economics 56(3):839-858, doi:10.1111/caje.12661. Six-point weights: values +-sqrt(3/2), +-1, +-sqrt(1/2), each with prob 1/6 (E=0, Var=1) -- use when G < ~12 where Rademacher has only 2^G distinct draws.
- MacKinnon & Webb (2017), "Wild bootstrap inference for wildly different cluster sizes", J. Applied Econometrics 32(2):233-254, doi:10.1002/jae.2508; MacKinnon & Webb (2018), "The wild bootstrap for few (treated) clusters", Econometrics Journal 21(2):114-135, doi:10.1111/ectj.12107; MacKinnon, Nielsen & Webb (2023), "Fast and reliable jackknife and bootstrap methods for cluster-robust inference", J. Applied Econometrics 38(5):671-694, doi:10.1002/jae.2969 (CRV3 jackknife; WCR/WCU types referenced by wildboottest). Cameron & Miller (2015), "A practitioner's guide to cluster-robust inference", J. Human Resources 50(2):317-372, doi:10.3368/jhr.50.2.317 (rule: bootstrap with G<~30-50; wild cluster bootstrap-t; few clusters).
- Driscoll & Kraay (1998), REStat 80(4):549-560, doi:10.1162/003465398557825: SEs robust to cross-sectional and temporal dependence, but consistency needs T large; works when N large or small as T->inf (their Monte Carlo is for N up to a few hundred). Hoechle (2007), Stata Journal 7(3):281-312.
- Own reasoning for this design: (i) date clusters absorb arbitrary cross-firm correlation on a day, valid as T (dates) large and dependence across dates small; but overlapping 10-lag regressors and fire exposure (a slow-moving, season-level variable) make residuals serially correlated across dates, so date-cluster SEs are likely too small; the bootstrap should resample at a level where blocks are approximately independent (season is only 4 clusters -- too few). Options: (a) Driscoll-Kraay with Bartlett bandwidth >= number of lags (10-15) or a Newey-West HAC on the date-averaged series; (b) two-way firm x date CRV1 with the caveat that firm dimension (10-20) is small and the two-way variance estimate may be non-PSD; (c) wild bootstrap by firm (G=10-20) as per CGM/MacKinnon-Webb with Webb weights (G<=12) and restricted residuals; (d) a date-block "wild" bootstrap is non-standard -- do not use without validation.
- VERIFIED: wildboottest (PyPI) says it does not support multiway clustering or the subcluster bootstrap; so two-way bootstrap cannot be done there. https://pypi.org/pypi/wildboottest/json , https://github.com/py-econometrics/wildboottest

### Inferences
- A reasonable inference ladder: primary = two-way (firm, date) or DK SEs; robustness = firm-level wild cluster bootstrap-t (Webb weights if G<=12, else Rademacher OK for G>=13 as 2^13 > 8000 draws); report that the date-cluster-only result is the weakest control for serial dependence.
- A Monte Carlo on placebo fire series (randomized/permuted exposure across seasons) is a cleaner size check than any single asymptotic argument; randomization inference is available in pyfixest (`ritest`, unverified).

### Gaps
- Petersen's exact recommendation for few firms: not verified at source.
- No source that directly evaluates date clustering with many dates and few firms for a design like this.

## 4. Python implementations (versions as of PyPI JSON read 2026-11-20)

### Takeaway
Latest versions seen: wildboottest 0.3.2 (released 2024-09-01), pyfixest 0.70.0 (requires Python >=3.11), linearmodels 7.1 (Python >=3.10), statsmodels 0.15.0 (Python >=3.10). wildboottest is the only Python wild cluster bootstrap and it is one-way clustering only; whether it works with fixed effects/linearmodels was not verifiable. Hand-roll the bootstrap if you need exact control.

### Cited Findings
- VERIFIED wildboottest 0.3.2, released Sep 1 2024, requires Python <4.0,>=3.8: "Wild Cluster Bootstrap Inference for Linear Models in Python". Supports bootstrap variants WCR13, WCR31, WCR33, WCU13, WCU31, WCU33; CRV1 and CRV3 (incl. CRV3-Jackknife); non-clustered wild bootstrap. Usage: `from wildboottest.wildboottest import wildboottest; wildboottest(model, param="x", cluster=df.firm, B=9999, bootstrap_type='11')` (examples use '11' and '31'). Omit `param` for all coefficients; omit `cluster` for non-clustered. Output is a table of t-stat and bootstrap p-value only (no CIs). Subcluster bootstrap and multiway clustering not supported. Direct support for statsmodels and linearmodels is "work in progress"; the example uses statsmodels OLS formula. Weight type options and fixed-effect handling are not documented on these pages (weights: not stated; practical consequence: absorb FE by dummies or demeaning yourself and check that the p-value matches pyfixest). https://pypi.org/pypi/wildboottest/json , https://github.com/py-econometrics/wildboottest
- VERIFIED pyfixest 0.70.0 (Python >=3.11): "Fast high dimensional fixed effect estimation following syntax of the fixest R package". README lists OLS, WLS, GLMs, IV with high-dimensional FE; cluster-robust and HAC variance estimators; wild cluster bootstrap "via wildboottest". Varying slopes `f[x]` syntax listed. Multiway clustering, `i()` interactions and Driscoll-Kraay were not shown on the pages read (fixest R has them and pyfixest mirrors; unverified). https://pypi.org/pypi/pyfixest/json , https://github.com/py-econometrics/pyfixest
- From search snippet (pyfixest tutorial): `fit = pf.feols("Y ~ X1 | f1", data, vcov={"CRV1": "group_id"}); fit.wildboottest(param="X1", reps=9999, cluster="group_id")`. Python keyword for Webb weights not confirmed. https://py-econometrics.github.io/pyfixest/tutorials/standard-errors.html (not fetchable; snippet via web search)
- VERIFIED linearmodels 7.1 ("Linear Panel, Instrumental Variable, Asset Pricing, and System Regression models for Python"), requires Python >=3.10. https://pypi.org/pypi/linearmodels/json
- VERIFIED statsmodels 0.15.0, Python >=3.10. https://pypi.org/pypi/statsmodels/json
- UNVERIFIED (from background knowledge; check with help()): `linearmodels.panel.PanelOLS(dependent, exog, entity_effects=False, time_effects=False, other_effects=None, ...)`, `.fit(cov_type='clustered', cluster_entity=True, cluster_time=True, debiased=True)` for two-way clustering; `cov_type='kernel'` gives Driscoll-Kraay-style (`kernel='bartlett', bandwidth=...`). Panel index must be MultiIndex (entity, time). `linearmodels.iv.IV2SLS(dependent, exog, endog, instruments)`, `.fit(cov_type='clustered', clusters=...)`; results have `.first_stage` (with `.diagnostics` incl. partial R2, partial F; `.individual` for per-endogenous-regressor), `.wu_hausman()`, `.sargan`. statsmodels: `OLS.fit(cov_type='cluster', cov_kwds={'groups': g})`; two-way via `groups=np.column_stack([a,b])`; `cov_type='hac-groupsum'` is a Driscoll-Kraay-style option with `cov_kwds={'time': t, 'maxlags': L}`; `'hac-panel'` for within-group HAC.
- No maintained Python event-study package was verified. Names to check on PyPI: `eventstudy`, `eventstudies`, `estudy2` (R package, CRAN, not Python). Hand-rolling (numpy/pandas + statsmodels OLS per firm) is the standard route. Not verified.

### Inferences
- Pin versions in the project environment; pyfixest>=0.70 forces Python>=3.11, which may conflict with other pins.
- Because wildboottest 0.3.2 dates from Sep 2024 and has no documented FE support, validate by comparing with a manual implementation on a simulated panel before relying on it. A manual WCR with G=10-20 firms is short: restricted-residual fit under H0, draw weights per cluster, rebuild y*, compute cluster-robust t* each rep, p = share |t*| >= |t|.

### Gaps
- Release dates of pyfixest 0.70.0, linearmodels 7.1, statsmodels 0.15.0 (page truncated); pyfixest/linearmodels/statsmodels docs not fetchable; wildboottest weight option and FE support not documented in reachable sources; whether `eventstudy`-type Python packages exist and are maintained.

## 5. Distributed lag: cumulative effect, one-sided test

### Takeaway
Reparametrize so the sum of lag coefficients is a single coefficient, then test it with a one-sided t and bootstrap that single parameter.

### Cited Findings
- Own derivation (standard linear-combination algebra; no source needed but UNVERIFIED externally): model AR_it = sum_{j=0..9} b_j x_{i,t-j} + ... . Define S = sum b_j. Rewrite with z_0 = x_t and z_j = x_{t-j} - x_t (j=1..9): sum b_j x_{t-j} = S x_t + sum_{j>=1} b_j z_j. The coefficient on z_0 is S itself, so any package that reports a t-stat and supports `param="z0"` yields the cumulative test directly. For the haze interaction, do the same with x*H: sum (b_j + d_j) is tested by reparametrizing the interaction block (or by recentring H at 1 so that the main-block coefficients are the high-haze effects).
- One-sided p (H1: S > 0 or S < 0 as pre-registered): p = 1 - Phi(t) (or t-dist with G-1 df for clustered) if t>0 else > 0.5; in a wild bootstrap use p = share of t*_b >= t (signed), not |t*|, for the right-tail test. Wald alternative: statsmodels `res.t_test("x0 + x1 + ... + x9 = 0")` (two-sided; halve p if sign matches); linearmodels: `res.wald_test(formula=...)` or `(restriction, value)` (UNVERIFIED).
- wildboottest's reported p-value is two-sided from the examples; for one-sided use the bootstrap distribution of t* if the function exposes it (not confirmed) -- otherwise hand-roll.

### Inferences
- Preregister the sign (direction) of the one-sided test and the exact lag set to avoid specification search.

### Gaps
- No package documentation fetched confirming one-sided bootstrap options.

## 6. IV with binary endogenous regressor and interaction; weak-instrument diagnostics; wind-direction precedents

### Takeaway
With an endogenous binary HighPSI and endogenous exposure x HighPSI interaction, use 2SLS with the instruments wind and exposure x wind (linear first stages), not a probit-plugged "forced regression"; report the Olea-Pflueger effective F (single endogenous variable) and for the two-endogenous case the Sanderson-Windmeijer conditional F; use tF (Lee et al.) when F is small.

### Cited Findings (UNVERIFIED-AT-SOURCE)
- Wooldridge (2010), Econometric Analysis of Cross Section and Panel Data, 2nd ed., MIT Press, sec. 9.5 and 18.4 (instrumenting a dummy with a linear 2SLS is consistent; plugging in fitted probabilities as regressors in the second stage — "forbidden regression" — is not safe; use fitted probabilities only as an instrument). Angrist & Pischke (2009), Mostly Harmless Econometrics, Princeton UP, sec. 4.6.1 (same advice).
- Olea & Pflueger (2013), "A robust test for weak instruments", J. Business & Economic Statistics 31(3):358-369 (DOI not verified). Lee, McCrary, Moreira & Porter (2022), "Valid t-ratio inference for IV", American Economic Review 112(10):3260-3290, doi:10.1257/aer.20211063 (tF critical-value adjustment; with F around 10 the 5% t critical value is far above 1.96; F>~104.7 needed for t=1.96).
- Wind-direction precedents: Deryugina, Heutel, Miller, Molitor & Reif (2019), "The mortality and medical costs of air pollution: Evidence from changes in wind direction", AER 109(12):4178-4219, doi:10.1257/aer.20180279; Anderson (2020), "As the wind blows: The effects of long-term exposure to air pollution on mortality", J. European Economic Association 18(4):1886-1927, doi:10.1093/jeea/jvz051. Other precedents (Rangel & Vogl 2019 on Brazilian sugarcane fires, Jayachandran 2009 on Indonesian haze) were recalled but not verified.
- Exclusion-restriction caveat (own reasoning): wind direction affects haze but also shipping, rain and sea-state/regional weather affecting palm oil logistics and equities; control for weather and month/season FE; wind must be direction relative to source-receptor geometry (Sumatra fires -> Singapore under southwesterly), a function of the firm location only for firm-specific instruments.
- Implementation: `IV2SLS(y, exog_df, endog_df[['HighPSI','Exp_x_High']], instr_df[['Wind','Exp_x_Wind']])`; or pyfixest `feols("AR ~ controls | firm + season | HighPSI + ExpHigh ~ Wind + ExpWind", vcov={"CRV1":"date"})` (IV syntax recalled; unverified). With a single interaction instrument, relevance must hold for both first stages (conditional F).

### Gaps
- Sanderson-Windmeijer (2016, J. Econometrics) conditional F not fetched; no software confirmation of effective-F (Stata `weakivtest`; Python: none verified, hand-compute from first-stage variance).

## 7. Multiple testing and pre-registration

### Takeaway
Harvey-Liu-Zhu argue for t>3 thresholds; pre-registration is accepted in economics via pre-analysis plans; a tagged public git commit is a weaker credibility signal than a third-party time-stamped registry.

### Cited Findings (UNVERIFIED-AT-SOURCE)
- Harvey, Liu & Zhu (2016), "... and the cross-section of expected returns", Review of Financial Studies 29(1):5-68, doi:10.1093/rfs/hhv059 (t-statistic hurdle > 3.0; multiple-testing adjustments Bonferroni/Holm/BHY). Harvey (2017), "The scientific outlook in financial economics", Journal of Finance 72(4):1399-1440, doi:10.1111/jofi.12530 (AFA presidential address; p-hacking, Bayesian view, pre-registration-like practices).
- Olken (2015), "Promises and perils of pre-analysis plans", J. Economic Perspectives 29(3):61-80, doi:10.1257/jep.29.3.61. Registries: AEA RCT Registry https://www.socialscienceregistry.org ; OSF https://osf.io ; AsPredicted https://aspredicted.org (all existence-level knowledge; norms not verified).
- Own reasoning: a git tag proves content at a time only if the hosting timestamp is trusted and history cannot be rewritten; strengthen by (a) depositing the frozen plan and commit SHA on OSF (time-stamped registration, can be embargoed), (b) signing the tag, (c) archiving to Zenodo (DOI), (d) stating in the plan the family of tests, the primary hypothesis (cumulative lags 0-9, one-sided), Holm/BHY across secondary tests, and rules for deviations. Plan must be committed before the 2026 season outcomes (or the data used for the confirmatory test) are examined; state which seasons are exploratory (2015, 2019, 2023 already known) and which confirmatory.

### Gaps
- No fetched confirmation of whether finance journals accept git tags as pre-registration; none found.

## 8. Reporting standards for null results and effect sizes

### Takeaway
No fetched source; recommended practice from reasoning: report effect sizes with CIs, equivalence/minimum detectable effect, and all specifications.

### Cited Findings
- None verified in this session.

### Inferences
- Report cumulative AR in percentage points per standard-deviation exposure with 95% CI (bootstrap), the minimum detectable effect given N=5/dates, the full set of tests (Patell, BMP, KP, rank, calendar-time) rather than the significant one, and run an equivalence test (TOST) against a economically meaningful bound; cite HLZ for the multiple-test hurdle and Kothari-Warner (2007) for event-study power concerns.

### Gaps
- Journal reporting standards for nulls (e.g. Journal of Finance policies, Journal of Accounting Research registered reports) not located.
