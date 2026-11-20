# Market-price, commodity-price and air-quality (salience) data sources, as of 2026-11-20

Research limits: about 20 tool calls. Several hosts were unreachable from the research sandbox (data.gov.sg, guide.data.gov.sg, api-open.data.gov.sg, cds.climate.copernicus.eu, market.bisnis.com, snips.stockbit.com, theedgesingapore mirrors). Facts below come from search-result summaries unless stated. Nothing was verified by hitting a live endpoint. Items from my own background knowledge are listed only under Gaps/Inferences and marked UNVERIFIED.

## Listing status and tickers (SGX and IDX stocks, indices, Yahoo symbols)

### Takeaway
No source found showing First Resources, Bumitama, Golden Agri, Wilmar or Indofood Agri delisted as of Nov 2026. Indofood Agri's only exit offer (2019) failed. Global Palm Resources (SGX) was privatised and delisted 4 Jul 2023. No IDX listing status was verified at all.

### Cited Findings
- Indofood Agri Resources (SGX 5JS): PT Indofood Sukses Makmur (INDF) made a voluntary conditional cash offer in 2019 to delist it, at S$0.28 per share, later raised to a final S$0.3275. It lapsed because acceptances were short of the 90% condition (concert group held 88.08%), and tendered shares were returned. — [search summary of MarketScreener/Edge/Kontan results](https://www.theedgemarkets.com/article/indofood-agri-resources-gets-28-cents-share-offer-delist); [Kontan](https://insight.kontan.co.id/news/tender-saham-indoagri-tak-penuhi-syarat-indofood-kembalikan-seluruh-saham-penawaran)
- Indofood Agri is still trading in 2026: MarketScreener quote late Sep 2026 about S$0.34; board reconstitution effective 31 Jul 2026; 1H2026 results (period ended 30 Jun 2026) reported. — [MarketScreener](https://www.marketscreener.com/quote/stock/INDOFOOD-AGRI-RESOURCES-L-6500283/); [MarketScreener director news](https://www.marketscreener.com/news/indofood-agri-resources-ltd-announces-resignation-of-goh-kian-chee-as-a-non-executive-director-and-ce7f50d8dd8cf12d)
- An FPA Financial note dated 14 Aug 2026 speculates about a possible Salim/INDF privatisation (estimated minimum price S$0.430, cost S$83.8m). This is analyst speculation, not an announced offer. — [FPA Financial PDF](https://fpafinancial.com/wp-content/uploads/indofood-agri-resources-ltd-company-update-august-2026.pdf)
- SGX rule change on 11 Jul 2019: exit offers accompanying voluntary delistings must be fair and reasonable, and the offeror and concert parties must abstain from the delisting vote. — [search summary of Edge Singapore](https://alfi.dev.theedgesingapore.com/views/management-corporate-governance/sgxs-delisting-rule-changes-are-commendable-impact-0)
- Golden Agri-Resources (E5H): no 2026 privatisation or delisting found. It still files normal documents (AGM notice appendices dated 2 Apr 2026). — [SGX AR2025 appendices](https://links.sgx.com/1.0.0/corporate-announcements/AZ8IVTSQL4RDPNJ9/881750_Appendices%20Golden-Agri%20Resources%20AR%202025.pdf)
- Do not confuse GAR with Golden Energy and Resources (GEAR, SGX): on 9 Nov (year not shown in the snippet, probably 2026) Duchess Avenue made a conditional exit offer at S$0.16 per share. — [Edge Singapore mirror](https://alfi.dev.theedgesingapore.com/capital/company-news/golden-energy-and-resources-delist-offers-gems-shares-and-exit-offer-16-cents)
- Wilmar (F34): no privatisation or delisting found. 2026 filings are routine (May 2026 Russian court seizure of a 24% indirect interest in JSC Etalon; June 2026 West Africa JV with TGI Group). — [SGX announcement](https://links.sgx.com/1.0.0/corporate-announcements/SH0U2BQIUS3YK13B/bca72c1f8d5bc92cf1f63288251910f27925b4c353122e73213ede183b68640d)
- Global Palm Resources Holdings (SGX): Adijanto family offer at S$0.25 cash announced 29 Mar 2023 (about S$62.3m); acceptances 93.14% at completion 31 May 2023; SGX RegCo approved delisting 21 Jun 2023; delisted from 9:00am on 4 Jul 2023 after compulsory acquisition. — [MarketScreener completion](https://in.marketscreener.com/quote/stock/GLOBAL-PALM-RESOURCES-HOL-6811673/news/Adijanto-family-completed-the-offer-to-acquire-Global-Palm-Resources-Holdings-Limited-from-GPR-Inves-44012713); [SGX delisting date notice](https://links.sgx.com/1.0.0/corporate-announcements/8S4AMBSK8XUHLZGO/763876_GPR%20-%20Announcement%20on%20Delisting%20Date.pdf); [SIAS reaction](https://sg.finance.yahoo.com/news/sias-calls-privatisation-offer-global-231549274.html)
- A Sinarmas Land privatisation offer (31 cents) also surfaced, which is unrelated to palm oil. — [EdgeProp](https://www.edgeprop.sg/property-news/billionaire-widjaja-family-offers-privatise-sinarmas-land-31-cents-share-shares-surge-23)

### Inferences
- For loaders: treat the SGX five as live through Nov 2026, but have the loader tolerate a series that ends early (a last-trade date must be checked per ticker).
- Global Palm Resources is delisted, so it cannot be added unless history through Jun 2023 is acceptable.

### Gaps
- Not verified on any live page: current status, listing dates and any corporate actions for First Resources (EB5), Bumitama (P8Z), and all six IDX names (AALI, SMAR, LSIP, SIMP, SSMS, DSNG). No search covered them.
- Not searched: Kencana Agri, Sampoerna Agro, Triputra Agro Persada, Eagle High Plantations, Austindo Nusantara Jaya, Tunas Baru Lampung and other candidates, so no tickers can be cited. UNVERIFIED recall only: Eagle High is IDX BWPT, Austindo is ANJT, Tunas Baru Lampung is TBLA, Sampoerna Agro is SGRO, Kencana Agri was on SGX (delisted, details unknown), Triputra Agro Persada is TAPG (IPO believed 2021), and Sawit Sumbermas/Dharma Satya IPO dates are unknown. Check each.
- Likely Yahoo symbols (UNVERIFIED recall, test live): EB5.SI, P8Z.SI, E5H.SI, F34.SI, 5JS.SI; AALI.JK, SMAR.JK, LSIP.JK, SIMP.JK, SSMS.JK, DSNG.JK; indices ^STI and ^JKSE.
- Indofood Agri status was inferred from secondary aggregators, not SGX's own announcements page.

## yfinance behaviour in late 2026

### Takeaway
The latest release found is 1.8.0, which requires curl_cffi >= 0.17. Rate limiting is IP-based and shows up as YFRateLimitError, often at the crumb step. Hostnames, proxy/CA behaviour and delisted-ticker history were not verified.

### Cited Findings
- PyPI latest version is 1.8.0; install requirements include curl_cffi>=0.17, pandas>=1.3.0, requests>=2.31, websockets>=13.0, protobuf, peewee, platformdirs, pytz, lxml, beautifulsoup4, numpy; optional extras `repair` (scipy, scikit-learn). The release date was not visible. — [PyPI JSON](https://pypi.org/pypi/yfinance/json)
- GitHub releases (month and day only, year not shown but presumably 2026): 1.8.0 on 03 Nov (forces curl_cffi >= 0.17; new Tickers.calendar and Tickers.info with spam-block risk); 1.7.0 26 Aug (proxy fixes, lazy history_metadata); 1.6.0 13 Aug; 1.5.2 23 Jul (fix for curl_cffi >= 0.16); 1.5.1 28 Jun (replaced retracted 1.5.0); 1.4.1 28 May (keeps Date index name in download()); 1.4.0 23 May (adds yf.Auth login and a fallback from curl_cffi to requests); 1.2.1 07 Apr (curl_cffi >= 0.15 for a CVE). — [GitHub releases](https://github.com/ranaroussi/yfinance/releases)
- yfinance raises YFRateLimitError when the crumb response is a 429 or contains "Too Many Requests". It rejects requests_cache sessions ("request_cache sessions don't work with curl_cffi"). A debug trace shows fc.yahoo.com returning 404 in normal operation, which is expected. — [yfinance data.py copy found in search](https://generationalwealth.duckdns.org/venv/lib/python3.13/site-packages/yfinance/data.py); [issue](https://github.com/ranaroussi/yfinance/issues/2422)
- Blocks are IP-based and usually lift after a while; one user reported over 24 hours. — [discussion #2431](https://github.com/ranaroussi/yfinance/discussions/2431)

### Inferences
- A loader should sleep between tickers, retry with backoff on YFRateLimitError, cache to disk, and pin yfinance and curl_cffi versions.
- Because curl_cffi uses its own TLS stack (libcurl-impersonate), the system CA bundle and the standard requests env vars may not apply; the sandbox proxy needs testing. This is inference, not a documented finding.

### Gaps
- Official hostnames list (query1/query2.finance.yahoo.com, fc.yahoo.com, consent/guce hosts) not confirmed from docs. Recall only (UNVERIFIED).
- No source on curl_cffi plus proxy or custom CA settings (e.g. CURL_CA_BUNDLE, verify option) in 2026.
- No source on whether delisted tickers (e.g. GPR) return history.
- Release years not shown on the releases page.

## Alternatives for SGX/IDX daily history (Stooq, IDX, SGX, Investing.com, EODHD)

### Takeaway
Not researched; no cited findings.

### Cited Findings
- None.

### Inferences
- None.

### Gaps
- Stooq symbol format, IDX and SGX official downloads, Investing.com and EODHD free-tier limits were not looked up.

## FCPO and palm-oil proxy price data

### Takeaway
Investing.com shows an FCPO continuous series (FCPOc1) with an HTML table; TradingView lists MYX:FCPO1!. A free scriptable CSV was not confirmed from any source.

### Cited Findings
- Investing.com historical-data page for Malaysian palm oil futures uses the label FCPOc1 (Reuters-style continuous front contract). — [Investing.com](https://ca.investing.com/commodities/palm-oil-historical-data)
- TradingView lists the continuous contract as MYX:FCPO1! with monthly contract pages (e.g. FCPOU2026). — [TradingView](https://www.tradingview.com/symbols/MYX-FCPO1!/contracts/)
- Barchart has a historical-download page pattern for its KO (Crude Palm Oil) symbols, e.g. KOM27, but the search snippet indicates downloads need a Barchart membership. — [Barchart](https://www.barchart.com/futures/quotes/KOJ27/price-history/download)
- Barchart also shows an unrelated CME crude palm oil contract (CUZ20). — [Barchart](https://www.barchart.com/futures/quotes/CUZ20/historical-download)
- A vendor (Portara) sells FCPO/MPO history. — [Portara](https://portaracqg.com/Futures/int/MPO)

### Inferences
- Barchart's own KO prefix suggests a front-month roll must be built by the loader if only individual contracts are free.

### Gaps
- Not verified: Yahoo symbols (KPO=F etc.), Stooq, MPOB, Bursa Malaysia downloads, CSV columns, login requirements.
- Not researched: Dalian palm olein, ZL=F, World Bank Pink Sheet, IMF.
- FCPO roll convention (third-month benchmark) not sourced; the claim in the brief is unverified here.

## Singapore PSI history (data.gov.sg / NEA)

### Takeaway
Endpoints are partly confirmed from search snippets only; the official docs could not be fetched. A bulk CSV covering Apr 2014 to Jul 2026 exists on data.gov.sg, which would cover Aug-Nov 2015.

### Cited Findings
- Bulk dataset: "historical regional 24-hr PSI" Apr 2014 to Jul 2026 as CSV on data.gov.sg; PSI real-time dataset updated every 15 minutes. — [data.gov.sg historical 24-hr PSI](https://data.gov.sg/dataset/historical-24-hr-psi); [dataset d_9213...](https://data.gov.sg/datasets/d_9213cd2e4631f7148ab5932a10df9958/view). The exact dataset id for the 24-hr series was not confirmed from the page text.
- v2 real-time API on api-open.data.gov.sg: a date query accepts YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss (SGT); no date returns latest; a paginationToken is returned for date-filtered requests; API key goes in an x-api-key header (the PM2.5 docs are the ones described). — [data.gov.sg real-time API guide](https://guide.data.gov.sg/developer-guide/real-time-apis)
- Legacy v1: https://api.data.gov.sg/v1/environment/psi with date=YYYY-MM-DD, or date_time=YYYY-MM-DDTHH:mm:ss, community-documented. — [Towards Data Science tutorial](https://towardsdatascience.com/exploring-data-gov-sg-api-725e344048dc/)
- Per one collection page, an API key gives higher rate limits and priority support (so a key appears optional). — [data.gov.sg collection](https://data.gov.sg/collections/2215/view)

### Inferences
- Use the bulk CSV rather than paging the API for 2014-2026; use the API only for recent top-ups.

### Gaps
- Exact v2 PSI path (probably /v2/real-time/api/psi, UNVERIFIED), response schema (regions, psi_twenty_four_hourly), rate limits, whether the v1 host still works in 2026.
- CSV columns and timestamp convention not seen.
- NEA PSI band definitions and the April 2014 PM2.5 inclusion not sourced. Recall only, UNVERIFIED: Good 0-50, Moderate 51-100, Unhealthy 101-200, Very unhealthy 201-300, Hazardous above 300.
- Alternative 2015 archives (haze.gov.sg, Kaggle) not searched.

## IDX trading rules, circuit breakers, holiday calendars

### Takeaway
IDX auto-rejection has been changed repeatedly; as of Nov 2026 the lower limit (ARB) is asymmetric 7% from 19 Oct 2026 through 31 Dec 2026, with a plan to return to symmetric from 1 Jan 2027 (sources disagree on details).

### Cited Findings
- BEI cut ARB for equities to an asymmetric 7% effective 19 Oct 2026 through 31 Dec 2026, to be re-evaluated; OJK confirmed the 15%-to-7% change runs to 31 Dec 2026 and buybacks without a shareholder meeting are extended to 30 Jun 2027. — [Bisnis 19 Oct 2026](https://market.bisnis.com/read/20261019/7/2013651/bei-pangkas-batas-auto-rejection-bawah-arb-jadi-asimetris-7); [Bisnis 6 Nov 2026](https://market.bisnis.com/read/20261106/7/2019143/ojk-tekankan-arb-15-jadi-7-hanya-berlaku-sampai-31-desember-2026)
- ARA tiers: 35% for Rp11-Rp200, 25% for >Rp200-Rp5,000, 20% above Rp5,000; Rp1-Rp10 uses Rp1 for both. A tier-change plan (ARB symmetric with ARA from 1 Jan 2027, and a 28 Sep 2026 reclassification) is reported by some outlets; Katadata says ARB widens to 35% in 2027. These disagree with the later 7% decision. — [Ajaib](https://ajaib.co.id/belajar/berita/aturan-baru-ara-arb-saham-28-september-2026); [Katadata](https://katadata.co.id/finansial/bursa/6ab10d458e4d5/bei-ubah-aturan-auto-rejection-batas-arb-makin-lebar-jadi-35-mulai-2027); [Stockbit](https://snips.stockbit.com/snips-terbaru/-bei-ubah-klasifikasi-auto-rejection-per-28-september-2026-arb-simetris-per-2027)
- ARB was lowered in April 2025 after trade-war volatility (per Stockbit summary). — [Stockbit](https://snips.stockbit.com/snips-terbaru/-bei-ubah-klasifikasi-auto-rejection-per-28-september-2026-arb-simetris-per-2027)

### Inferences
- The 2020-2023 asymmetric 7% regime and the 2015 rules (symmetric 35%/25%/20% by price tier, with 10% for prices Rp50-200 in some periods) are not sourced here; model limit-hit flags by date-dependent parameters and verify each change date.

### Gaps
- Not verified: 2015-2025 change dates, trading halt rules (IDX 5%/10%/15% market-wide suspension), how to detect limit-hit days, SGX circuit breakers, and the holiday calendars for SGX, IDX and Bursa Malaysia.

## ERA5 and lighter wind alternatives

### Takeaway
New CDS uses base URL https://cds.climate.copernicus.eu/api with a personal access token; dataset id is reanalysis-era5-single-levels. Sources were forum summaries; the official page was unreachable.

### Cited Findings
- ~/.cdsapirc: `url: https://cds.climate.copernicus.eu/api` and `key: <personal-access-token>` (no UID); legacy api/v2 and UID:KEY formats are obsolete. — [ECMWF forum](https://forum.ecmwf.int/t/unable-to-run-script-despite-migrating-to-new-cds-api/5608); [how-to-api](https://cds.climate.copernicus.eu/how-to-api)
- cdsapi 0.7.2 or later recommended to avoid 404s; dataset terms must be accepted on the website first. Pointing at the EWDS host gives 404 for ERA5. — [ECMWF forum](https://forum.ecmwf.int/t/cdsapi-key-and-404-issues/10905); [forum](https://forum.ecmwf.int/t/not-found-error-of-era5-hourly-data-on-single-levels-from-1940-to-present/12977)
- Dataset id: reanalysis-era5-single-levels; REST pattern https://cds.climate.copernicus.eu/api/retrieve/v1/processes/{dataset}/execute/. — [same forum thread](https://forum.ecmwf.int/t/not-found-error-of-era5-hourly-data-on-single-levels-from-1940-to-present/12977)

### Inferences
- A token requires a free CDS account, which this task forbids creating; the loader needs a user-supplied token.

### Gaps
- Variable names (10m_u_component_of_wind, 10m_v_component_of_wind), `area` ordering, licence text, queue times: UNVERIFIED recall. Open-Meteo, Meteostat and NOAA ISD (WSSS) not researched.

## Attention proxies (Google Trends, GDELT)

### Takeaway
Not researched; no cited findings.

### Cited Findings
- None.

### Inferences
- None.

### Gaps
- pytrends status in 2026, the official Trends API alpha, GDELT DOC 2.0 endpoint (UNVERIFIED recall: api.gdeltproject.org/api/v2/doc/doc) and limits.
