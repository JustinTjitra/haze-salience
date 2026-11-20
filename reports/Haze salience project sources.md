# Haze-salience sources: unverified endpoints, open gap

**No live page was read for any data source, timeline event or journal article in this project; the only live reads were PyPI and GitHub package pages.** The research sandbox blocked every data, news, regulator and publisher host, so almost everything below rests on search-result summaries, with the rest taken from background knowledge. The one exception is five Python packages (pyfixest, linearmodels, statsmodels, wildboottest, yfinance), whose PyPI or GitHub pages were read. The substantive findings are these. First, **no prior academic study was found** linking FIRMS hotspots in concessions to SGX/IDX palm-oil returns, or an event study of the 2015 or 2019 haze on plantation stocks. The nearest items are an undated NUS student project, descriptive Chain Reaction Research reports and press commentary, and the search could not reach SSRN or Google Scholar. Second, **Suomi NPP VIIRS fire delivery ends 1-2 Nov 2026**, so 2026 fire exposure must come from NOAA-20/21 VIIRS (or MODIS). Third, the 2026 season gives two candidate events 11 days apart: a Greenpeace report on 5 Oct, and PM Wong's Facebook post on the evening of **Thu 15 Oct** (after the SGX close), which makes **Fri 16 Oct 2026** day 0. Fourth, there are no usable concession polygons yet (GFW has a global oil-palm concession layer but its fields, URL and licence are unconfirmed, and Indonesian official data are restricted), and no FCPO CSV source is confirmed. Fifth, the econometrics need hand-rolled code: no Python event-study package was verified, and wildboottest 0.3.2 supports one-way clustering only. The consolidated verification list and the blocked hostnames are at the end.

**Verification tags used throughout**

| Tag | Meaning |
|---|---|
| **LIVE** | Page was fetched and read this session (only PyPI JSON pages and GitHub pages). |
| **SNIPPET** | Supported only by a web-search result summary; the page itself was not opened. |
| **BKG** | Taken from background or model memory; no source consulted. Includes all DOIs marked "BKG". |
| **SNIPPET (conflict)** | Snippet-level and different sources disagree. |

Row-level notes in the source files used terms such as "[V]", "[V-partial]" and "[M]" for literature items. In the tables below, "[V]" is mapped to SNIPPET because it meant a bibliographic-index record, not a live page of the paper, and "[M]" is mapped to BKG.

## Data sources: only the FIRMS endpoint list is documented, and nothing was tested

### NASA FIRMS (fire detections)

| Item | Detail | Status |
|---|---|---|
| API docs | `https://firms.modaps.eosdis.nasa.gov/api` and `/api/area/csv`; the endpoint takes MAP_KEY, source, area coordinates and day range; with no date it returns today back to today minus (DAY_RANGE-1) ([FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/area/csv)) | SNIPPET |
| Source IDs | LANDSAT_NRT (US/Canada only), MODIS_NRT, MODIS_SP, VIIRS_NOAA20_NRT, VIIRS_NOAA20_SP, VIIRS_NOAA21_NRT, VIIRS_SNPP_NRT, VIIRS_SNPP_SP; `/api/data_availability/` checks product dates ([FIRMS API](https://firms.modaps.eosdis.nasa.gov/api)) | SNIPPET |
| URL template | `https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{west,south,east,north}/{DAY_RANGE}/{YYYY-MM-DD}` (MAP_KEY in the path) | **BKG, unsourced** |
| Limits | Day range 1-5; 5000 transactions per 10 minutes ([apis.io spec](https://apis.io/apis/nasa-firms/nasa-firms-area-fire-detections-api/)); a status check for remaining transactions is linked from NASA's page. NASA's own page was not read. | SNIPPET (third party) |
| Country API | `https://firms.modaps.eosdis.nasa.gov/api/country/`; IDN parameters not read | SNIPPET (URL only) |
| Archive tool | `https://firms.modaps.eosdis.nasa.gov/download/` serves MODIS and VIIRS as shapefile/CSV/JSON; Earthdata Login or emailed code; **delivery is by email** (a human step) ([Archive Download](https://firms.modaps.eosdis.nasa.gov/download/)). Mirror: `https://firms2.modaps.eosdis.nasa.gov/download/` | SNIPPET |
| Coverage | MODIS C6 from 11 Nov 2000; VIIRS 375 m from 20 Jan 2012 (S-NPP start, unverified); NOAA-21 from 17 Jan 2024 ([Archive Download](https://firms.modaps.eosdis.nasa.gov/download/), [FIRMS wiki](https://wiki.earthdata.nasa.gov/spaces/FIRMS/blog/2024/02/08/343475617/NOAA-21+VIIRS+Active+Fire+Detection+Data+Now+Available)). One summary attributed 20 Jan 2012 to NOAA-20, which is implausible (launched 2017). | SNIPPET (conflict) |
| File archive | `https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/`, `https://nrt4.modaps.eosdis.nasa.gov/archive/FIRMS/`; Earthdata credentials and wget with a download token ([nrt3 README](https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/README.pdf)) | SNIPPET |
| Earthdata login host | `urs.earthdata.nasa.gov` | **BKG** |
| Attributes | `acq_time` is UTC overpass time; `daynight` D/N; `frp` in MW; `version` carries collection plus NRT suffix (e.g. 6.1NRT); satellite codes MODIS A/T, VIIRS N (S-NPP) / 1 (NOAA-20) ([FIRMS attributes](https://earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs)). `acq_time` is HHMM in CSV vs seconds in Earth Engine (conflict). | SNIPPET |
| Confidence | MODIS 0-100%; VIIRS 375 m is categorical low/nominal/high ([VIIRS I-Band page](https://www.earthdata.nasa.gov/data/instruments/viirs/near-real-time-data/viirs-i-band-375-m-active-fire-data)); CSV letters l/n/h are from memory; whether NRT confidence fields were removed is unresolved | SNIPPET / BKG |
| Quality | NRT may have geolocation errors and be reprocessed; SP is science quality ([Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/NASA_LANCE_SNPP_VIIRS_C2)) | SNIPPET |
| User guides | [VIIRS C2 AF 375m User Guide 1.2](https://www.earthdata.nasa.gov/s3fs-public/2025-06/VIIRS_C2_AF-375m_User_Guide_1.2.pdf), [MOD14 User Guide V61](https://LPDAAC.USGS.GOV/documents/1005/MOD14_User_Guide_V61.pdf) | SNIPPET (not opened) |

**S-NPP cessation matters for the 2026 season.** NASA says production and delivery of new S-NPP active-fire data stops at 13:00 UTC on **2 Nov 2026**; NOAA and NASA's forum give 1 Nov, so the date conflicts ([NASA Earthdata blog](https://www.earthdata.nasa.gov/news/blog/transitioning-from-s-npp-viirs-omps-what-nasa-firms-users-need-know), [NOAA NESDIS](https://www.nesdis.noaa.gov/news/cessation-of-suomi-national-polar-orbiting-partnership-s-npp-data-users-onafter-november-01-2026), [Earthdata forum](https://forum.earthdata.nasa.gov/viewtopic.php?p=26446)). Users are told to move to VIIRS_NOAA20_NRT or VIIRS_NOAA21_NRT. A Copernicus notice says S-NPP has been non-nominal since July 2026, which would hurt Aug-Oct 2026 completeness ([Copernicus Land](https://land.copernicus.eu/en/production-updates/global-burnt-area-production-temporary-switch-to-noaa-viirs-source-3)). All of this is SNIPPET. Loader design implications, flagged as inference:

- Use SP products (VIIRS_SNPP_SP, MODIS_SP) for 2015, 2019 and 2023, and NOAA-20/21 for 2026.
- Harmonise the cross-year series on MODIS or NOAA-20 where possible.
- Chunk API calls into at most 5-day windows within the rate limit.
- Request the historical seasons once through the archive tool, since email delivery blocks unattended runs.
- Whether the API serves 2015, 2019 and 2023 at all is unconfirmed.

### Concession polygons and parent links

| Source | What was found | Status |
|---|---|---|
| GFW "Oil Palm Concessions" `oil-palm-concessions-lm-v3-gfw` | Government-allocated oil-palm areas, global (not Indonesia-only); created 27 May 2024, updated 13 Mar 2025 ([WRI datasets](https://datasets-dev.wri.org/datasets/oil-palm-concessions-lm-v3-gfw)) | SNIPPET |
| GFW `com-024-rw0-nrt-oil-palm-concessions-rw` | Monthly updates, created or updated 25 Nov 2025; "may not include all concessions" ([WRI datasets](https://datasets-dev.wri.org/datasets/com-024-rw0-nrt-oil-palm-concessions-rw)) | SNIPPET |
| Older Indonesia file | `indonesia_oil_palm_concessions` from `data.globalforestwatch.org`, dated 2020-05-27 ([Land Matrix](https://landmatrix.org/deal/8104/82374/data-sources)) | SNIPPET |
| Attribute fields, licence, file format, download URL, Data API id | Not found. Hosts `data-api.globalforestwatch.org`, `gis-gfw.wri.org` are inferred only. | **Unknown / BKG** |
| Kepo Hutan (Greenpeace) | Says official data are unavailable because of government restrictions ([Kepo Hutan](https://kepohutan.greenpeace.org/about)) | SNIPPET |
| Greenpeace shapefiles | Digitised from paper maps; no public download; 2017 Supreme Court ruling said concession data are public ([Eco-Business](https://www.eco-business.com/news/indonesias-forestry-ministry-takes-greenpeace-to-court-over-freedom-of-information-request)) | SNIPPET |
| Nusantara Atlas | Compiles concessions, mills, company names and the Greenpeace dataset; no bulk export found ([Nusantara Atlas](https://nusantara-atlas.org/palm-oil-giant-using-shadow-companies-to-hide-their-links-to-deforestation-of-tiger-habitat-in-sumatra)) | SNIPPET |
| FoE report | Notes no group reviewed has published boundaries in reusable form ([FoE](https://foe.org/wp-content/uploads/2024/06/AAL_CultivatingConflict_Eng_final.pdf)); context is Astra Agro Lestari | SNIPPET |
| Trase Indonesia palm oil | 2018-2024, v1.2.5, DOI 10.48650/0717-AJ12; mill/trader level, not polygons; raw-data licence not stated; new 2023-24 data scheduled 13 Oct 2026 ([Trase](https://trase.earth/open-data/datasets/supply-chains-indonesia-palm-oil), [SEI](https://www.sei.org/about-sei/press-room/indonesia-palm-oil-domestic-demand/)) | SNIPPET |
| Universal Mill List (GFW) | Maps mills to parent groups ([GFW blog](https://www.globalforestwatch.org/blog/data/improved-universal-mill-list-expands-partnerships-improves-transparency-in-palm-oil-industry/)); mills layer `palm-oil-mills-lm-v3v202207-gfw` ([WRI](https://datasets-dev.wri.org/datasets/palm-oil-mills-lm-v3v202207-gfw)) | SNIPPET |
| Oil-palm extent raster (Descals et al.) | CC-BY-4.0 ([Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/BIOPAMA_GlobalOilPalm_v1_2)) | SNIPPET |
| GeoRSPO, Chain Reaction Research lists, company sustainability-report concession lists (First Resources, Bumitama, GAR/SMART, Wilmar, Salim Ivomas/Lonsum, AAL, SSMS, DSN) | Not found or not searched | **Unknown** |
| Sumatra/Kalimantan boundaries (GADM, geoBoundaries ADM1) | Not researched; suggestion only | **BKG** |

The attribution caveat is firm literature, not a data gap. Gaveau et al. (Conservation Letters 2017) studied 163 Riau oil palm and pulpwood concessions and conclude that attributing fire to concessions is effectively impossible without field investigation; CIFOR's summary has about half of fires inside concessions and about 60% of burned area outside concessions within 5 km, though that figure is pulpwood-specific ([CIFOR](https://forestsnews.cifor.org/embed-post/46097), [UMT PDF](https://www.umt.edu/media/leopold/pubs/925.pdf)); SNIPPET. The literature notes could not locate the paper directly, so its bibliographic details are BKG. A 0 km inside-polygon measure plus a 5 km buffer sensitivity is defensible on this basis (inference). A Sept 2026 NGO analysis put nearly a quarter of burned forest and peat in concessions, mostly oil palm ([Jakarta Post](https://thejakartapost.com/indonesia/2026/09/04/unchecked-businesses-blamed-for-raging-wildfires)); SNIPPET.

### Stock prices, listing status and tickers

| Firm | Exchange / ticker | Status found | Evidence | Status |
|---|---|---|---|---|
| Indofood Agri Resources | SGX 5JS | Listed; 2019 INDF exit offer (S$0.28, raised to S$0.3275) failed at 88.08% vs the 90% condition; late Sep 2026 quote about S$0.34; 1H2026 results reported; a 14 Aug 2026 analyst note speculates about privatisation (not an offer) | [Edge](https://www.theedgemarkets.com/article/indofood-agri-resources-gets-28-cents-share-offer-delist), [Kontan](https://insight.kontan.co.id/news/tender-saham-indoagri-tak-penuhi-syarat-indofood-kembalikan-seluruh-saham-penawaran), [MarketScreener](https://www.marketscreener.com/quote/stock/INDOFOOD-AGRI-RESOURCES-L-6500283/), [FPA](https://fpafinancial.com/wp-content/uploads/indofood-agri-resources-ltd-company-update-august-2026.pdf) | SNIPPET (aggregators, not SGX) |
| Golden Agri-Resources | SGX E5H | No delisting found; AGM appendices dated 2 Apr 2026. Not to be confused with Golden Energy and Resources (GEAR), which got a S$0.16 exit offer on 9 Nov (year not shown, probably 2026) | [SGX](https://links.sgx.com/1.0.0/corporate-announcements/AZ8IVTSQL4RDPNJ9/881750_Appendices%20Golden-Agri%20Resources%20AR%202025.pdf), [Edge mirror](https://alfi.dev.theedgesingapore.com/capital/company-news/golden-energy-and-resources-delist-offers-gems-shares-and-exit-offer-16-cents) | SNIPPET |
| Wilmar International | SGX F34 | No delisting found; routine 2026 filings | [SGX](https://links.sgx.com/1.0.0/corporate-announcements/SH0U2BQIUS3YK13B/bca72c1f8d5bc92cf1f63288251910f27925b4c353122e73213ede183b68640d) | SNIPPET |
| Global Palm Resources | SGX | **Delisted 4 Jul 2023** (Adijanto offer S$0.25, announced 29 Mar 2023, 93.14% acceptance at completion 31 May 2023, RegCo approval 21 Jun 2023) | [MarketScreener](https://in.marketscreener.com/quote/stock/GLOBAL-PALM-RESOURCES-HOL-6811673/news/Adijanto-family-completed-the-offer-to-acquire-Global-Palm-Resources-Holdings-Limited-from-GPR-Inves-44012713), [SGX notice](https://links.sgx.com/1.0.0/corporate-announcements/8S4AMBSK8XUHLZGO/763876_GPR%20-%20Announcement%20on%20Delisting%20Date.pdf) | SNIPPET |
| First Resources | SGX EB5 | **Not verified** (listed per background; named in 2026 events) | none | BKG |
| Bumitama Agri | SGX P8Z | **Not verified** (named in 2026 events, traded 16 Oct 2026 per press) | none | BKG |
| Kencana Agri | SGX | Queried by RegCo and quoted in 2026 price moves, so apparently still listed; notes' memory says "delisted, details unknown", a contradiction | [Edge Singapore](https://www.theedgesingapore.com/news/trans-boundary-haze/regco-queries-sgx-listed-indonesian-agri-firms-cause-and-impact-haze) | SNIPPET (conflict with BKG) |
| AALI, SMAR, LSIP, SIMP, SSMS, DSNG | IDX | **No listing status verified for any** | none | BKG |
| Other IDX candidates: BWPT (Eagle High), ANJT, TBLA, SGRO, TAPG (IPO believed 2021) | IDX | Tickers from memory only; check each | none | BKG |

Yahoo symbols are recall only and must be tested live: EB5.SI, P8Z.SI, E5H.SI, F34.SI, 5JS.SI; AALI.JK, SMAR.JK, LSIP.JK, SIMP.JK, SSMS.JK, DSNG.JK; indices ^STI and ^JKSE (BKG). SGX's 11 Jul 2019 delisting rule (exit offers must be fair and reasonable; the offeror and concert parties abstain from the vote) comes from an Edge Singapore snippet ([Edge](https://alfi.dev.theedgesingapore.com/views/management-corporate-governance/sgxs-delisting-rule-changes-are-commendable-impact-0)).

**yfinance (LIVE for versions, SNIPPET for behaviour).** PyPI latest is **1.8.0**, requiring curl_cffi>=0.17, pandas>=1.3.0, requests>=2.31, websockets>=13.0, protobuf, peewee, platformdirs, pytz, lxml, beautifulsoup4, numpy ([PyPI](https://pypi.org/pypi/yfinance/json)). GitHub releases (month/day only; years presumably 2026): 1.8.0 on 03 Nov, 1.7.0 on 26 Aug, 1.6.0 on 13 Aug, 1.5.2 on 23 Jul, 1.5.1 on 28 Jun, 1.4.1 on 28 May, 1.4.0 on 23 May (adds `yf.Auth`), 1.2.1 on 07 Apr ([releases](https://github.com/ranaroussi/yfinance/releases)). Rate limiting is IP-based and raises `YFRateLimitError` at the crumb step; requests_cache sessions are rejected; blocks usually lift but one user reported over 24 hours ([issue 2422](https://github.com/ranaroussi/yfinance/issues/2422), [discussion 2431](https://github.com/ranaroussi/yfinance/discussions/2431)). Loader advice (inference): sleep between tickers, back off, cache to disk, pin yfinance and curl_cffi, and test the sandbox proxy because curl_cffi uses its own TLS stack. Whether delisted tickers return history is unknown. **Alternatives (Stooq, IDX and SGX downloads, Investing.com, EODHD) were not researched.**

**IDX price limits (SNIPPET, conflicting).** BEI cut the lower limit (ARB) to an asymmetric 7% from 19 Oct 2026 through 31 Dec 2026 ([Bisnis 19 Oct](https://market.bisnis.com/read/20261019/7/2013651/bei-pangkas-batas-auto-rejection-bawah-arb-jadi-asimetris-7), [Bisnis 6 Nov](https://market.bisnis.com/read/20261106/7/2019143/ojk-tekankan-arb-15-jadi-7-hanya-berlaku-sampai-31-desember-2026)). ARA tiers: 35% for Rp11-200, 25% for Rp200-5,000, 20% above Rp5,000 ([Ajaib](https://ajaib.co.id/belajar/berita/aturan-baru-ara-arb-saham-28-september-2026)). Other outlets report a symmetric ARB from 2027 or a widening to 35% ([Katadata](https://katadata.co.id/finansial/bursa/6ab10d458e4d5/bei-ubah-aturan-auto-rejection-batas-arb-makin-lebar-jadi-35-mulai-2027)); these disagree. Rules for 2015-2025, trading halts and the SGX, IDX and Bursa Malaysia holiday calendars are unverified, so model limit-hit flags with date-dependent parameters.

### Crude palm oil futures

| Source | Detail | Status |
|---|---|---|
| Investing.com | Label FCPOc1 (continuous front contract), HTML table ([page](https://ca.investing.com/commodities/palm-oil-historical-data)) | SNIPPET |
| TradingView | `MYX:FCPO1!`, monthly contracts such as FCPOU2026 ([page](https://www.tradingview.com/symbols/MYX-FCPO1!/contracts/)) | SNIPPET |
| Barchart | KO prefix for crude palm oil (e.g. KOM27); history download appears to need membership ([page](https://www.barchart.com/futures/quotes/KOJ27/price-history/download)); CUZ20 is an unrelated CME contract | SNIPPET |
| Portara | Vendor selling FCPO/MPO history ([page](https://portaracqg.com/Futures/int/MPO)) | SNIPPET |
| Yahoo (e.g. KPO=F), Stooq, MPOB, Bursa Malaysia downloads, World Bank Pink Sheet, Dalian palm olein; FCPO roll convention | Not verified or not researched | **Unknown** |

No free scriptable FCPO CSV was confirmed. If only single contracts are free, the loader must build the front-month roll itself.

### Singapore PSI history

| Item | Detail | Status |
|---|---|---|
| Bulk CSV | "Historical 24-hr PSI" by region, Apr 2014 onward (listings say to Dec 2024 or Jul 2026, currency unclear) ([dataset page](https://data.gov.sg/dataset/historical-24-hr-psi), [d_9213cd2e4631f7148ab5932a10df9958](https://data.gov.sg/datasets/d_9213cd2e4631f7148ab5932a10df9958/view), [d_b4cf557f8750260d229c49fd768e11ed](https://data.gov.sg/datasets/d_b4cf557f8750260d229c49fd768e11ed/view)); which id is the 24-hr series is unconfirmed; this covers Aug-Nov 2015 | SNIPPET |
| v2 real-time API | Host `api-open.data.gov.sg`; `date` accepts YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss (SGT); a paginationToken is returned; API key in an `x-api-key` header (from the PM2.5 docs) ([guide](https://guide.data.gov.sg/developer-guide/real-time-apis)). Path `/v2/real-time/api/psi` is a guess | SNIPPET / **BKG** |
| Legacy v1 | `https://api.data.gov.sg/v1/environment/psi` with `date=` or `date_time=` ([tutorial](https://towardsdatascience.com/exploring-data-gov-sg-api-725e344048dc/)); whether it still works in 2026 is unknown | SNIPPET |
| Key | A key gives higher rate limits and priority support, so it appears optional ([collection](https://data.gov.sg/collections/2215/view)) | SNIPPET |
| PSI definition | Six pollutants, 24-hr rolling, hourly updates, five regions ([dataset page](https://data.gov.sg/dataset/historical-24-hr-psi)) | SNIPPET |
| Bands | Good 0-50, Moderate 51-100, Unhealthy 101-200, Very Unhealthy 201-300, Hazardous >300; the April 2014 PM2.5 inclusion | **BKG** |

Two definitional traps are noted. Media day-counts treat a day as unhealthy if PSI exceeds 100 anywhere at any time ([Star](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/16/singapore-is-experiencing-12th-consecutive-day-of-unhealthy-air-the-longest-since-2015-haze-crisis)), while the THPA trigger is unhealthy-range PSI in any part of Singapore for 24 hours or more ([Star 19 Oct](https://www.thestar.com.my/business/business-news/2026/10/19/palm-oil-stocks-tumble-as-spore-probes-haze-links)); recompute streaks from the CSV and state the rule. CSV columns and timestamp convention are unseen.

### ERA5 wind and attention proxies

| Item | Detail | Status |
|---|---|---|
| CDS config | `~/.cdsapirc` with `url: https://cds.climate.copernicus.eu/api` and `key: <personal-access-token>` (no UID); legacy api/v2 formats obsolete ([ECMWF forum](https://forum.ecmwf.int/t/unable-to-run-script-despite-migrating-to-new-cds-api/5608), [how-to-api](https://cds.climate.copernicus.eu/how-to-api)) | SNIPPET |
| Package / terms | cdsapi 0.7.2 or later recommended to avoid 404s; accept dataset terms on the website first; the EWDS host gives 404 for ERA5 ([forum](https://forum.ecmwf.int/t/cdsapi-key-and-404-issues/10905)) | SNIPPET |
| Dataset id, REST | `reanalysis-era5-single-levels`; `https://cds.climate.copernicus.eu/api/retrieve/v1/processes/{dataset}/execute/` ([forum](https://forum.ecmwf.int/t/not-found-error-of-era5-hourly-data-on-single-levels-from-1940-to-present/12977)) | SNIPPET |
| Variables, `area` ordering, licence, queue times | `10m_u_component_of_wind`, `10m_v_component_of_wind` | **BKG** |
| Token | Requires a free CDS account; the loader needs a user-supplied token | Inference |
| Open-Meteo, Meteostat, NOAA ISD (WSSS) | Not researched | Unknown |
| Google Trends (pytrends status, official Trends API alpha), GDELT DOC 2.0 (`api.gdeltproject.org/api/v2/doc/doc`) | Not researched; the GDELT endpoint is recall only | **BKG** |

## Econometrics: standard methods are in the notes, but only package versions were read live

### Package versions (the only live-verified material)

| Package | Version | Verified facts | Status |
|---|---|---|---|
| wildboottest | **0.3.2** (released 1 Sep 2024; Python >=3.8,<4.0) | Variants WCR13/31/33, WCU13/31/33; CRV1, CRV3 and CRV3-Jackknife; call `wildboottest(model, param="x", cluster=df.firm, B=9999, bootstrap_type='11')`; output is t-stat and bootstrap p only; **no multiway clustering, no subcluster bootstrap**; statsmodels and linearmodels support "work in progress"; weight types and FE handling undocumented ([PyPI](https://pypi.org/pypi/wildboottest/json), [GitHub](https://github.com/py-econometrics/wildboottest)) | LIVE |
| pyfixest | **0.70.0** (Python >=3.11) | OLS, WLS, GLM, IV with high-dimensional FE; clustered and HAC variance; wild cluster bootstrap via wildboottest ([PyPI](https://pypi.org/pypi/pyfixest/json), [GitHub](https://github.com/py-econometrics/pyfixest)). Multiway clustering, `i()` and Driscoll-Kraay were not shown. | LIVE |
| linearmodels | **7.1** (Python >=3.10) | Panel, IV, asset pricing, system models ([PyPI](https://pypi.org/pypi/linearmodels/json)) | LIVE |
| statsmodels | **0.15.0** (Python >=3.10) | ([PyPI](https://pypi.org/pypi/statsmodels/json)) | LIVE |

The release dates of pyfixest, linearmodels and statsmodels were not visible. Documentation sites for all four (py-econometrics.github.io, bashtage.github.io, statsmodels.org) were unreachable, so every API call below is BKG and must be checked with `help()`.

| Call | Status |
|---|---|
| `fit = pf.feols("Y ~ X1 \| f1", data, vcov={"CRV1": "group_id"}); fit.wildboottest(param="X1", reps=9999, cluster="group_id")` (from a [pyfixest tutorial](https://py-econometrics.github.io/pyfixest/tutorials/standard-errors.html) snippet); keyword for Webb weights unconfirmed | SNIPPET |
| `linearmodels.panel.PanelOLS(...).fit(cov_type='clustered', cluster_entity=True, cluster_time=True)` for two-way clustering; `cov_type='kernel'` for Driscoll-Kraay style; MultiIndex (entity, time) required | BKG |
| `linearmodels.iv.IV2SLS(dependent, exog, endog, instruments).fit(cov_type='clustered', clusters=...)`; `.first_stage.diagnostics`, `.wu_hausman()`, `.sargan` | BKG |
| statsmodels `OLS.fit(cov_type='cluster', cov_kwds={'groups': g})`; two-way with `np.column_stack`; `'hac-groupsum'` (Driscoll-Kraay style, `cov_kwds={'time': t, 'maxlags': L}`); `'hac-panel'` | BKG |
| pyfixest IV: `feols("AR ~ controls \| firm + season \| HighPSI + ExpHigh ~ Wind + ExpWind", vcov={"CRV1":"date"})` | BKG |
| No maintained Python event-study package verified (names to check: `eventstudy`, `eventstudies`; `estudy2` is an R package) | Unknown |

### Event-study references and test choice (all bibliographic details BKG; no DOI resolved)

| Reference | Role | DOI / locator (BKG) |
|---|---|---|
| Brown & Warner (1985), JFE 14(1):3-31 | Daily-returns event-study methods | 10.1016/0304-405X(85)90042-X |
| MacKinlay (1997), J. Econ. Literature 35(1):13-39 | Survey; formulas | jstor.org/stable/2729691 |
| Kothari & Warner (2007), Handbook of Corporate Finance Vol. 1 ch. 1 | Power; cross-correlation; calendar-time | 10.1016/B978-0-444-53265-7.50015-9 |
| Patell (1976), JAR 14(2):246-276 | Standardised AR test | 10.2307/2490543 |
| Boehmer, Musumeci & Poulsen (1991), JFE 30(2):253-272 | BMP test | 10.1016/0304-405X(91)90032-F |
| Kolari & Pynnonen (2010), RFS 23(11):3996-4025 | Cross-correlation-adjusted BMP | 10.1093/rfs/hhq072 |
| Corrado (1989), JFE 23(2):385-395; Corrado & Zivney (1992), JFQA 27(3):465-478 | Rank tests | 10.1016/0304-405X(89)90064-0; 10.2307/2331331 |
| Kolari & Pynnonen (2011), J. Empirical Finance 18(5):953-971 | Generalized rank test (GRANK) | 10.1016/j.jempfin.2011.08.003 |
| Dimson (1979), JFE 7(2):197-226 | Aggregated-coefficient beta for thin trading | 10.1016/0304-405X(79)90013-8 |
| Scholes & Williams (1977), JFE 5(3):309-327 | Nonsynchronous betas | 10.1016/0304-405X(77)90041-1 |
| Kim & Rhee (1997), J. Finance 52(2):885-901 | Price-limit effects (DOI guessed: 10.1111/j.1540-6261.1997.tb02719.x) | DOI unverified |

With five firms sharing the same event dates, abnormal returns are cross-sectionally correlated, so Patell and plain BMP over-reject. The notes' reasoned recommendation (not source-verified) is: report **Kolari-Pynnonen** t_KP = t_BMP * sqrt((1 - rbar)/(1 + (N-1) rbar)) with t(N-1) critical values, plus a **calendar-time equally weighted portfolio test** as primary, and treat N=5 rank tests as low-power. Use Dimson K=1 (or 2) for thin IDX names; compare Scholes-Williams; flag zero-volume and limit-hit days; compute the estimation-window residual correlation and report the deflation factor. The GRANK formula was not reproduced and must be taken from KP (2011). The standard formulas (market-model abnormal return, forecast-error-corrected variance, Patell, BMP, Corrado) are written out in the source note and are BKG. **How published studies handle two events 11 days apart was not found.** Options consistent with Kothari-Warner logic are: one estimation window that excludes both event windows; one pooled window with sub-window and union CARs; or separate events without claiming independence (windows of +/-6 or more days overlap).

### Few-cluster inference and the wild bootstrap (BKG except wildboottest limits above)

| Reference | Use | DOI (BKG) |
|---|---|---|
| Petersen (2009), RFS 22(1):435-480 | Firm and time effects; cluster by both | 10.1093/rfs/hhn053 |
| Cameron, Gelbach & Miller (2008), REStat 90(3):414-427 | Wild cluster bootstrap-t, null imposed | 10.1162/rest.90.3.414 |
| Cameron, Gelbach & Miller (2011), JBES 29(2):238-249 | Multiway clustering | 10.1198/jbes.2010.07136 |
| Thompson (2011), JFE 99(1):1-10 | Firm-and-time clustering formulas | 10.1016/j.jfineco.2010.08.016 |
| Roodman, Nielsen, MacKinnon & Webb (2019), Stata J. 19(1):4-60 | boottest algorithm (basis for wildboottest-type tools) | 10.1177/1536867X19830877 |
| Webb (2014), Queen's WP 1315 (pub. Can. J. Econ. 56(3), 2023) | Six-point weights for G < ~12 | 10.1111/caje.12661 |
| MacKinnon & Webb (2017) JAE 32(2); (2018) Econometrics J. 21(2); MacKinnon, Nielsen & Webb (2023) JAE 38(5) | Unequal clusters, few treated clusters, CRV3 jackknife | 10.1002/jae.2508; 10.1111/ectj.12107; 10.1002/jae.2969 |
| Cameron & Miller (2015), J. Human Resources 50(2):317-372 | Practitioner guide; bootstrap when G < ~30-50 | 10.3368/jhr.50.2.317 |
| Driscoll & Kraay (1998), REStat 80(4):549-560; Hoechle (2007), Stata J. 7(3) | Spatial and temporal dependence; needs large T | 10.1162/003465398557825 |

The notes' reasoned inference ladder is: primary two-way (firm, date) or Driscoll-Kraay errors with bandwidth of at least the 10-15 lags; robustness a firm-level wild cluster bootstrap-t with restricted residuals (Webb weights if G<=12, Rademacher acceptable for G>=13); date-only clustering is the weakest control because fire exposure is slow-moving and overlapping lags induce serial correlation. With only four seasons, season-level clustering is too coarse. wildboottest cannot do two-way, so hand-roll or validate against a manual restricted wild cluster bootstrap on a simulated panel. A placebo-exposure Monte Carlo is a cleaner size check, and pyfixest `ritest` was recalled but is unverified.

### Cumulative lag effect, IV design and pre-registration

- **Cumulative effect (own algebra, BKG).** For AR_it on lags 0-9 of exposure x, define S as the sum of coefficients and reparametrise with z_0 = x_t and z_j = x_{t-j} - x_t, so the coefficient on z_0 equals S. Test S one-sided (`p = share of t*_b >= t` in a bootstrap, not |t*|). wildboottest reports two-sided p-values, so use a hand-rolled bootstrap for one-sided tests. Pre-register the sign and lag set.
- **IV for HighPSI and exposure x HighPSI (BKG).** Use linear 2SLS with instruments Wind and Exposure x Wind, not a probit-plugged second stage (Wooldridge 2010 sec. 9.5, 18.4; Angrist & Pischke 2009 sec. 4.6.1). Weak-instrument diagnostics: Olea & Pflueger (2013, JBES 31(3):358-369) effective F for one endogenous variable; Sanderson-Windmeijer (2016, J. Econometrics) conditional F for two (not fetched); Lee, McCrary, Moreira & Porter (2022, AER 112(10):3260-3290, 10.1257/aer.20211063) tF, with F above about 104.7 needed for t=1.96. No Python effective-F routine was verified. Wind-direction precedents: Deryugina et al. (2019, AER 109(12):4178-4219, 10.1257/aer.20180279) and Anderson (2020, JEEA 18(4):1886-1927, 10.1093/jeea/jvz051); Rangel & Vogl (2019) and Jayachandran (2009) are recalled only. Exclusion-restriction risk (shipping, rain, regional weather affecting palm logistics and equities) calls for weather and season controls; wind must be defined relative to the source-receptor geometry.
- **Multiple testing and pre-registration (BKG).** Harvey, Liu & Zhu (2016, RFS 29(1):5-68, 10.1093/rfs/hhv059; t above 3); Harvey (2017, J. Finance 72(4):1399-1440, 10.1111/jofi.12530); Olken (2015, JEP 29(3):61-80, 10.1257/jep.29.3.61). Registries: socialscienceregistry.org, osf.io, aspredicted.org (existence-level knowledge). A git tag is weak; strengthen it with an OSF registration, a signed tag and a Zenodo DOI, commit before the 2026 outcomes are examined, and label 2015, 2019 and 2023 as exploratory. No source confirms that finance journals accept git tags as pre-registration.
- **Null-result reporting.** No source fetched; the notes' recommendation is effect sizes with CIs, the minimum detectable effect at N=5, all specifications, and a TOST equivalence test.

## Literature: the gap looks real, but SSRN and Google Scholar were not searched

### Novelty check

About 25 searches found no paper that links FIRMS/MODIS/VIIRS hotspots to stock returns of palm or pulp firms, and no peer-reviewed event study of the 2015 or 2019 haze on plantation shares. Treat this as "nothing found", not "nothing exists". The nearest material:

| Item | What it is | Status |
|---|---|---|
| NUS Business School student project | Six-stock SGX palm index vs PSI; investors "not very sensitive" within PSI 0-100; no citation or method ([page](https://bschool.nus.edu.sg/?p=582)) | SNIPPET (landing text only) |
| Mongabay, June 2013 | GAR about -8%, Wilmar about -5%, First Resources about -4% since 18 June; Mongabay says link to haze unclear because the index also fell ([article](https://news.mongabay.com/2013/06/palm-oil-companies-linked-to-haze-see-share-prices-drop/)) | SNIPPET |
| 2026 press | Raw moves after NEA notices: one report Wilmar about -9% and GAR about -18% over 23 Sep-23 Oct; another, 9-21 Oct: First Resources -14%, GAR -12.5%, Bumitama -11%, Kencana -7%, Wilmar -4.5%, Indofood Agri +4.6%; not market-adjusted ([Star](https://www.thestar.com.my/business/business-news/2026/10/19/palm-oil-stocks-tumble-as-spore-probes-haze-links), [Red Hot](https://www.redhot.sg/palm-oil-stocks-tumble-as-s-pore-looks-for-firms-responsible-for-haze-markets-this-week-729128.html), [Dollars and Sense](https://dollarsandsense.sg/sgx-listed-palm-oil-companies-haze-corporate-governance/)) | SNIPPET |
| Newswav, Borneo Post 2026 | Haze not hurting palm demand but reviving a reputational issue; First Resources blames El Nino and outside fires; MPOB says a hotspot is not proof of cause; WALHI claims about 50% of high-confidence hotspots in concessions ([Newswav](https://newswav.com/article/haze-is-not-hurting-palm-oil-demand-but-it-is-reviving-an-old-reputational-A2609_oTp8tH), [Borneo Post](https://www.pressreader.com/malaysia/the-borneo-post/20260921/281818585738950)) | SNIPPET |
| Chain Reaction Research | About 15,000 fire alerts in concessions of the top-ten affected companies Jul-Oct 2019 (about 4% of alerts); only a blog summary read ([blog](https://yuleng-khor.squarespace.com/blog/tag/Fires), [CRR](https://aidenvironment.org/project/chain-reaction-research/)); candidate original [PDF](https://aidenvironment.org/wp-content/uploads/2024/04/40.-Deforestation-driven20fires.pdf) not opened | SNIPPET |
| CPO export ban event studies (2022) | AJARE 2026 ([Wiley](https://onlinelibrary.wiley.com/doi/full/10.1111/1467-8489.70151)); EUDL doi 10.4108/eai.2-8-2023.2340640 ([EUDL](https://eudl.eu/doi/10.4108/eai.2-8-2023.2340640)) | SNIPPET |
| China Dec 2013 haze event study | Press page only ([Melbourne](https://fbe.unimelb.edu.au/newsroom/chinas-haze-hits-market)) | SNIPPET |
| "The Effects of Environmental Regulation on the Singapore Stock Market", J. Risk Financial Mgmt 12(4):175 (2019) | Title from a listing; not opened; **check first** whether it concerns the THPA ([MDPI](https://www.mdpi.com/1911-8074/12/4/175)) | SNIPPET |
| GitHub `JustinTjitra/haze-salience` | Pilot event study of 5 SGX firms, Oct 2026, no results; not literature ([GitHub](https://github.com/JustinTjitra/haze-salience)) | SNIPPET |

### Core theory and empirical papers

| Theme | Papers (venue, DOI) | Status |
|---|---|---|
| Slow diffusion | Hong & Stein (1999), J. Finance 54(6):2143-2184, 10.1111/0022-1082.00184; Hong, Lim & Stein (2000), J. Finance 55(1):265-295, 10.1111/0022-1082.00206; Hong, Torous & Valkanov (2007), JFE 83(2):367-396, 10.1016/j.jfineco.2005.09.010; Cohen & Frazzini (2008), J. Finance 63(4):1977-2011, 10.1111/j.1540-6261.2008.01379.x; Menzly & Ozbas (2010), J. Finance 65(4):1555-1580, 10.1111/j.1540-6261.2010.01578.x; Da, Gurun & Warachka (2014), RFS 27(7):2171-2218, 10.1093/rfs/hhu003 (verification search returned nothing) | BKG |
| Diffusion, verified at index level | Anton & Polk (2014), J. Finance 69(3):1099-1127 ([LSE](https://personal.lse.ac.uk/polk/research/ConnectedStocks.pdf)); Ying (2024), JFE 156:103852, 10.1016/j.jfineco.2024.103852 ([IDEAS](https://ideas.repec.org/a/eee/jfinec/v156y2024ics0304405x24000758.html)); Hirshleifer, Peng & Wang (2025), **RFS** 38(3):883-937, NBER w30860 ([NBER](https://www.nber.org/papers/w30860)) (not JF) | SNIPPET |
| Peripheral | Lopez-Lira & Tang, arXiv:2304.07619 ([arXiv](https://arxiv.org/abs/2304.07619)), working paper; Semenova & Winkler (2025), Quantitative Finance 25(12):1873-1904 ([arXiv](https://arxiv.org/abs/2104.01847)) (not Review of Finance) | SNIPPET |
| Closest analogue | Huberman & Regev (2001), J. Finance 56(1):387-396, 10.1111/0022-1082.00330: EntreMed soared after a NYT article on already-public research ([EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:56:y:2001:i:1:p:387-396)) | SNIPPET |
| Attention toolkit | Barber & Odean (2008), RFS 21(2):785-818, 10.1093/rfs/hhm079; DellaVigna & Pollet (2009), J. Finance 64(2):709-749, 10.1111/j.1540-6261.2009.01447.x; Hirshleifer, Lim & Teoh (2009), J. Finance 64(5):2289-2325, 10.1111/j.1540-6261.2009.01501.x; Da, Engelberg & Gao (2011), J. Finance 66(5):1461-1499, 10.1111/j.1540-6261.2011.01679.x (Google search volume); Tetlock (2011), RFS 24(5):1481-1512, 10.1093/rfs/hhq141; Peng & Xiong (2006), JFE 80(3):563-602, 10.1016/j.jfineco.2005.05.003; Engelberg & Parsons (2011), J. Finance 66(1):67-97, 10.1111/j.1540-6261.2010.01626.x; Ben-Rephael, Da & Israelsen (2017), RFS 30(9):3009-3047, 10.1093/rfs/hhx051; Bordalo, Gennaioli & Shleifer (QJE 2012; JPE 2013; AER P&P 2013) | BKG |
| Satellite data and prices | Zhu (2019), **RFS** 32(5):2021-2061 ([IDEAS](https://ideas.repec.org/a/oup/rfinst/v32y2019i5p2021-2061..html)); Katona, Painter, Patatoukas & Zeng (2025), JFQA 60(2):551-579, 10.1017/S0022109023001448 ([Cambridge](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/on-the-capital-market-consequences-of-big-data-evidence-from-outer-space/2F5F99D68D1F8940F61578F198D6C005)); Gerken & Painter (2023), RFS 36(2):409-449, 10.1093/rfs/hhac033 ([EconPapers](https://econpapers.repec.org/RePEc:oup:rfinst:v:36:y:2023:i:2:p:409-449.)); Mukherjee, Panayotov & Shon (2021), JFE 141(1):234-254, 10.1016/j.jfineco.2021.03.002 ([EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:141:y:2021:i:1:p:234-254)); Kang, Stice-Lawrence & Wong (2021), JAR 59(2):713-750 (reference-list only) | SNIPPET |
| Pollution and markets | Heyes, Neidell & Saberian (2016), NBER w22753 ([NBER](https://www.nber.org/papers/w22753)), no journal version found; Huang, Xu & Yu (2020), Management Science 66(10):4455-4476 ([EconPapers](https://econpapers.repec.org/RePEc:inm:ormnsc:v:66:y:2020:i:10:p:4455-4476)); Li, Massa, Zhang & Zhang (2021), JFE 142(2):641-673, 10.1016/j.jfineco.2019.09.003 ([IDEAS](https://ideas.repec.org/a/eee/jfinec/v142y2021i2p641-673.html)); Hirshleifer & Shumway (2003), J. Finance 58(3):1009-1032, 10.1111/1540-6261.00556 (BKG) | SNIPPET / BKG |
| Environmental events | Bolton & Kacperczyk (2021), JFE 142(2):517-549 ([EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:142:y:2021:i:2:p:517-549)); Karpoff, Lott & Wehrly (2005), J. Law & Econ. 48(2):653-675, 10.1086/430808 (BKG); Krueger, Sautner & Starks (2020), RFS 33(3):1067-1111, 10.1093/rfs/hhz137 (BKG); ECGI/INSEAD "Value of NGO Activism" WP 2024/57/ACC, three-day market-adjusted -34bp ([ECGI](https://www.ecgi.global/sites/default/files/2025-08/the-value-of-ngo-activism.pdf)) | SNIPPET / BKG |
| Fire attribution | Gaveau et al. (2014), Sci. Reports 4:6112: June 2013, 163,336 ha burned, 84% on peat, 52% in concessions but 60% of that also community-occupied ([Nature](https://www.nature.com/articles/srep06112)); Marlier et al. (2015), ERL 10:085005: 2006 concessions were 41% of Sumatra and 27% of Kalimantan fire emissions ([PDF](https://scholar.harvard.edu/sites/scholar.harvard.edu/files/skoplitz/files/environ._res._lett._2015_marlier-1.pdf)); Koplitz et al. (2016), ERL 11(9):094023, about 100,300 excess deaths in 2015 ([Columbia](https://academiccommons.columbia.edu/doi/10.7916/D8SQ90Q7)); Greenpeace "Under Fire" and "Burning Down the House" (advocacy, not opened) | SNIPPET |
| Hawkes processes | Rizoiu et al., arXiv:1708.06401 ([arXiv](https://arxiv.org/pdf/1708.06401)); Bacry, Mastromatteo & Muzy (2015), arXiv:1502.04592 ([arXiv](https://arxiv.org/pdf/1502.04592)); no finance application to news-attention cascades found | SNIPPET |

Corrections the notes caught: Hirshleifer-Peng-Wang is in RFS, not JF; the common-ownership JFE paper is Ying (2024); Zhu (2019) is in RFS, not JFE; Katona et al. is in JFQA; Semenova-Winkler is in Quantitative Finance. **No palm-specific market-reaction evidence** was found for IOI 2016, GAR/Sinar Mas 2010, Wilmar or RSPO suspensions, and none for THPA events. THPA background: effective 25 Sep 2014, fines up to S$100,000 per day per AFP ([Statutes Online](https://sso.agc.gov.sg/Act/THPA2014), [RSIS CO15021](https://rsis.edu.sg/rsis-publication/nts/co15021-singapores-transboundary-haze-pollution-act-silver-bullet-or-silver-lining/), [phys.org/AFP](https://phys.org/news/2015-09-singapore-indonesian-firms-haze.pdf)); SNIPPET. Indonesian enforcement in 2015: 23 companies punished and 33 investigated by late December ([Mongabay](https://news.mongabay.com/2015/12/50-companies-being-investigated-or-punished-for-indonesias-haze-crisis/)); SNIPPET. The most apt framing is Huberman-Regev plus Tetlock (stale public information), DellaVigna-Pollet and Hirshleifer-Lim-Teoh (attention-dependent underreaction), and Da-Gurun-Warachka (continuous small signals). The pollution-mood papers supply a competing channel that the project must separate from information salience.

## Event timelines: 2026 is rich but snippet-only; 2015, 2019 and 2023 are thin

All rows below are SNIPPET unless stated. Times are SGT. No SGX announcement, NEA release or Greenpeace original was opened. For event-study coding, the market-relevant corrections to earlier drafts are: Wong's post was **15 Oct** (not 16 Oct), the share fall came on **16 Oct**, the unhealthy streak began 5 Oct (12th day on 16 Oct, at least 14 days by 18 Oct; "13-16 Oct" was wrong), and a "GAR closed down 3.5%" figure is unverified. "Worst in more than a decade" was not found verbatim; sources say longest streak since 2015.

### 2026 season

| Date | Type | Event | Sources | Confidence |
|---|---|---|---|---|
| Aug 2026 (day unknown) | Government | Agencies announce haze-mitigation measures | [NEA](https://www.nea.gov.sg/media/news/news/index/singapore-government-agencies-implement-measures-to-mitigate-impact-of-haze-Aug2026) | URL title only |
| 4 Sep | Salience | Central 24-hr PSI 101 at 7am, first Unhealthy since 8 Oct 2023 | [Malay Mail](https://www.malaymail.com/amp/news/singapore/2026/09/04/singapore-haze-tips-air-quality-into-unhealthy-range-for-first-time-since-2023/233833), [NEA](https://www.nea.gov.sg/media/news/advisories/index/haze-situation-update-(04-september-2026)) | 2 sources |
| 14-15 Sep | Salience | Central PSI 136, south/east/west also unhealthy; first islandwide unhealthy since 2019 | [Star](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/09/14/psi-in-central-singapore-rises-to-136-air-quality-in-south-east-and-west-also-hits-unhealthy-level), [Malay Mail](https://www.malaymail.com/amp/news/singapore/2026/09/15/singapore-records-first-islandwide-unhealthy-psi-since-2019-as-haze-worsens/235275) | 2 sources |
| 5 Oct | NGO report | Greenpeace links First Resources, Bumitama (via Damai Agro Sejahtera) and private First Borneo Plantations to concessions with fires or smoke detected Aug-Sep. The Edge Malaysia (6 Oct) says more than 20 firms were named, including First Resources and KLK. Exact title unknown; Star's Singapore coverage dated 15 Oct | [Mothership](https://mothership.sg/2026/10/two-singapore-listed-palm-oil-firms-greenpeace-report-indonesian-plantation-fires/), [Star](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/15/two-singapore-listed-palm-oil-firms-named-in-greenpeace-report-on-indonesian-plantation-fires), [Edge Malaysia](https://theedgemalaysia.com/node/820713) | Partly confirmed; first public release date unverified |
| 5 Oct | Salience | Start of continuous unhealthy streak | [Star 16 Oct](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/16/singapore-is-experiencing-12th-consecutive-day-of-unhealthy-air-the-longest-since-2015-haze-crisis) | 1 outlet |
| 7-9 Oct | Salience | Three regions unhealthy for over 24h; central 24-hr PSI 192 on 9 Oct | [Malay Mail](https://www.malaymail.com/amp/news/singapore/2026/10/07/haze-blankets-singapore-with-three-regions-recording-unhealthy-air-for-over-24-hours/237997), [Tempo](https://en.tempo.co/read/2121261/singapore-haze-hits-2026-high-as-psi-reaches-192) | 2 sources |
| 10 Oct | Government | NEA 24-hr PSI 118-168; MOE would consider school closure if forecast above 300 (none found) | [NEA](https://www.nea.gov.sg/media/news/advisories/index/haze-situation-update-10-october-2026), [Mothership](https://mothership.sg/2026/10/psi-exceed-300-moe-consider-closing-schools/) | 2 sources |
| 14 Oct | Salience | PSI Very Unhealthy for the first time at 9pm (west 203) | [Star 16 Oct](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/16/singapore-is-experiencing-12th-consecutive-day-of-unhealthy-air-the-longest-since-2015-haze-crisis) | 1 source |
| 15 Oct | Company | First Resources SGX announcement: fires began outside its boundaries; hotspots do not prove deliberate burning; time of day unknown | [Online Citizen](https://news.theonlinecitizen.com/2026/10/16/singapore-listed-palm-oil-firm-denies-fires-originated-on-its-plantations-flagged-in-greenpeace-report) | SGX original not seen |
| **15 Oct (Thu, late evening)** | Government | **PM Lawrence Wong's Facebook post**: Singapore looking into which companies may be responsible; THPA action where warranted; possible joint action with other countries; no companies named. Posted after market close | [Bloomberg](https://www.bloomberg.com/news/articles/2026-10-15/singapore-s-wong-says-probing-firms-behind-haze-causing-fires), [Mothership](https://mothership.sg/2026/10/lawrence-wong-singapore-companies-haze/), [Star](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/16/singapore-looking-into-which-companies-responsible-for-haze-causing-fires-pm-wong) | 2+ sources; exact time and wording not retrieved |
| **16 Oct (Fri)** | Price move | First Resources down as much as 9.1% to S$3.71 (as at 9:20am; close not found); Bumitama low S$1.73 (-7.5%), closed -4.8% at S$1.78; Wilmar closed -1.2%; GAR as much as -6.9% to S$0.27 in one report and -3.4% to S$0.28 in another (conflict) | [Star 19 Oct](https://www.thestar.com.my/business/business-news/2026/10/19/palm-oil-stocks-tumble-as-spore-probes-haze-links), [ST via Magzter](https://www.magzter.com/stories/newspaper/The-Straits-Times/PALM-OIL-STOCKS-TUMBLE-AS-SPORE-LOOKS-FOR-COMPANIES-RESPONSIBLE-FOR-HAZE), [Red Hot](https://www.redhot.sg/palm-oil-stocks-slide-after-singapore-begins-looking-into-which-firms-responsible-for-haze-728491.html) | Direction 2+ outlets; figures conflict; verify against price data |
| 15-16 Oct | Regulatory | SGX RegCo writes to listed firms with Indonesian plantations (Bumitama, First Resources, GAR, Indofood Agri, Kencana Agri, Wilmar; some reports add Olam, TSH); date conflict | [Edge Singapore](https://www.theedgesingapore.com/news/trans-boundary-haze/regco-queries-sgx-listed-indonesian-agri-firms-cause-and-impact-haze) | 1 outlet plus Mongabay |
| 16 Oct | Company | Wilmar: no-burning policy since 2006; GAR: not aware of contribution; Bumitama: no evidence linking its operations | [Star 19 Oct](https://www.thestar.com.my/business/business-news/2026/10/19/palm-oil-stocks-tumble-as-spore-probes-haze-links) | 1 source |
| 16 Oct | Salience | Central 24-hr PSI 229 at 3pm; 12th consecutive unhealthy day, longest since 2015 | [Online Citizen](https://news.theonlinecitizen.com/2026/10/16/singapore-haze-central-region-s-24-hour-psi-hits-229-at-3pm-on-16-october-highest-in-2026), [Star](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/16/singapore-is-experiencing-12th-consecutive-day-of-unhealthy-air-the-longest-since-2015-haze-crisis) | 2 sources |
| 16 Oct (inferred from "last Friday") | Regulatory | NEA preventive measure notices to seven Sumatran agroforestry companies; names not retrieved | [Star 19 Oct](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/19/singapore-vows-tougher-legal-action-against-companies-linked-to-haze) | Inferred date |
| 18-19 Oct | Government | 18 Oct: west PSI 230, 14th day. About 19 Oct: notices to three Kalimantan firms (PT Buana Megatama Jaya, PT Mananjung Hayak, PT Baratama Putra Perkasa), total 10. Shanmugam says some noticed firms link to Singapore-based firms; named APP, First Resources, Bumitama, First Borneo as appearing linked | [Malay Mail](https://www.malaymail.com/news/singapore/2026/10/18/singapores-west-records-season-high-psi-of-230-as-haze-enters-14th-day/239549), [AP/USNews](https://www.usnews.com/news/business/articles/2026-10-19/singapore-expands-crackdown-on-indonesian-companies-linked-to-haze), [MHA](https://www.mha.gov.sg/media-room/newsroom/transcript-of-media-doorstop-by-mr-k-shanmugam-senior-minister-coordinating-minister-for-national-security-and-minister-for-home-affairs-on-the-haze-situation/) | 2+ sources |
| 20 Oct | Company | First Resources welcomes probe, denies land clearing by fire | [Online Citizen](https://news.theonlinecitizen.com/2026/10/20/first-resources-welcomes-haze-probe-denies-land-clearing-by-fire-amid-singapore-s-regulatory-scrutiny) | 1 source |
| 22 Oct | Salience | PSI moderate (71-96); streak ended around 20-22 Oct (24 Oct readings 108-151 unhealthy again) | [NEA](https://www.nea.gov.sg/media/news/advisories/index/haze-situation-update-22-october-2026) | 1 source; last streak day unverified |
| 23 Oct | Regulatory (THPA s.10) | NEA legal notices to 10 Singapore-based companies; all acknowledged; GAR reviewing. Conflict on whether First Resources and Bumitama are among the 10 (Mongabay says yes, Financial Coconut no) | [Little Big Red Dot](https://littlebigreddot.com/nea-thpa-notices-10-singapore-based-firms-haze-23-october-2026/), [Mothership](https://mothership.sg/2026/10/10-companies-notice-nea-confirm/), [Mongabay](https://news.mongabay.com/2026/10/influence-without-enforcement-indonesias-fires-test-singapores-anti-haze-law/) | Weak; company list unresolved |
| 28 Oct | Regulatory | RegCo second-round queries on links to the 10 firms | [Edge Singapore](https://www.theedgesingapore.com/news/trans-boundary-haze/regco-issues-additional-queries-sgx-listed-companies-links-haze) | 1 source; date weak |
| 7 Nov | Government | NEA stops haze advisories | [Wikipedia](https://en.wikipedia.org/wiki/2026_Southeast_Asian_haze) | 1 source |
| 13 Nov | NGO | Greenpeace "Days Full of Haze": 17,390 haze-source spots 8 Aug-31 Oct (another notice says 17,805); 1,776 in 46 palm concessions, 2,586 in 28 pulpwood concessions | [Greenpeace](https://www.greenpeace.org/southeastasia/press/69401/new-report-on-transboundary-haze-asean-govts-must-stop-dodging-responsibility/), [Mongabay ID](https://mongabay.co.id/2026/11/16/masyarakat-sipil-lintas-negara-desak-antisipasi-bencana-asap/) | Counts conflict; URL title may match an older report |
| about 16 Nov | Government | Prabowo apologises to Singapore and Malaysia at ASEAN summit; 17 concessions revoked, 26 companies investigated, 11 charged | [Al Jazeera](https://www.aljazeera.com/news/2026/11/16/indonesian-president-apologises-to-singapore-malaysia-for-wildfire-haze), [SCMP](https://www.scmp.com/news/asia/southeast-asia/article/3374510/indonesias-prabowo-apologises-to-singapore-malaysia-over-transboundary-haze) | 2 sources |

Coding implications (inference): the 5 Oct Greenpeace report and the 16 Oct first-tradable-reaction day are **11 days apart**, which is the overlapping-window case flagged under event-study methods. Greenpeace's 5 Oct report may have had little market impact because Singapore-listed coverage appeared around 15 Oct, so check Straits Times and Business Times dates. The "10 Indonesian plus 10 Singapore-based = 20 firms" reading reconciles Mongabay's "20 firms". Still missing: Wong's exact timestamp, the names of the seven Sumatran and ten Singapore firms, closing moves for First Resources and GAR on 16 Oct and for 19 and 23 Oct, ASMC alert levels, and any named Indonesian concession sealings in 2026. Companies named in 2026: First Resources, Bumitama, GAR, Wilmar, Indofood Agri, Kencana; not found: Astra Agro, SMART, London Sumatra, Salim Ivomas, Sawit Sumbermas, DSN.

### 2015, 2019 and 2023 seasons

| Date | Event | Sources | Status |
|---|---|---|---|
| 24 Sep 2015 | Very unhealthy PSI (headline) | [Malay Mail](https://www.malaymail.com/news/world/2015/09/24/singapore-air-quality-very-unhealthy-as-haze-worsens/975691) | SNIPPET (headline only) |
| 25 Sep 2015 | NEA preventive measure notices to four Indonesian firms under the THPA (Rimba Hutani Mas, Sebangun Bumi Andalas Wood Industries, Bumi Sriwijaya Sentosa, Wachyuni Mandira; names from a blog-grade source) and an information notice to APP Singapore | [NAS press release](https://www.nas.gov.sg/archivesonline/data/pdfdoc/MSE_20150925001.pdf), [Malay Mail](https://www.malaymail.com/amp/news/world/2015/09/25/singapore-presses-asia-pulp-paper-for-information-on-forest-fires/976515) | SNIPPET; verify names against the NAS PDF |
| 25 Sep 2015 | Singapore schools shut | [Malay Mail](https://www.malaymail.com/news/world/2015/09/25/singapore-slams-indonesia-over-haze-response-as-schools-shut/976245) | SNIPPET (headline only) |
| 23 Sep-7 Oct 2015 | 14 consecutive bad-air days | [Star 2026 summary](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/16/singapore-is-experiencing-12th-consecutive-day-of-unhealthy-air-the-longest-since-2015-haze-crisis) | SNIPPET (secondary) |
| Late 2015 | NEA probe widened to 10 firms including Kalimantan (date not retrieved) | [Eco-Business](https://www.eco-business.com/news/singapore-widens-haze-crackdown-to-kalimantan-targeting-10-indonesian-firms/) | SNIPPET |
| about 12-14 Sep 2019 | KLHK seals concessions of about 30 companies (29 per Malay Mail), including Adei Plantation (KLK) | [Malay Mail 13 Sep](https://www.malaymail.com/news/malaysia/2019/09/13/indonesia-seals-off-malaysian-owned-plantation-for-open-burning-amid-haze-r/1790185), [Malay Mail 14 Sep](https://www.malaymail.com/news/malaysia/2019/09/14/malaysian-planter-klk-confirms-fire-at-land-of-unit-named-by-indonesia/1790452), [Mongabay](https://news.mongabay.com/2019/09/indonesian-minister-draws-fire-for-denial-of-transboundary-haze-problem/) | SNIPPET |
| 14 Sep 2019 (Sat; not verified) | Singapore PSI enters unhealthy, first time since 2016 | [Inquirer](https://newsinfo.inquirer.net/1164920/haze-in-singapore-enters-unhealthy-range-across-island) | SNIPPET (headline) |
| 25 Sep 2019 | Jakarta Post: three Indonesian firms with Singapore offices linked to fires, including Hutan Ketapang Industri (Sampoerna Agri link) | [Jakarta Post](https://www.thejakartapost.com/seasia/2019/09/25/three-companies-with-offices-in-singapore-fingered-for-involvement-in-haze-1569394615.html) | SNIPPET |
| 2019 (date unknown) | Greenpeace "Burning down the house" (more than 60 sealed concessions Aug-Oct); "ASEAN Haze 2019: the battle of liability" | [PDF](https://www.greenpeace.org/static/planet4-international-stateless/2019/11/5c8a9799-burning-down-the-house-greenpeace-indonesia-fires-briefing.pdf), [Greenpeace](https://www.greenpeace.org/southeastasia/press/3221/asean-haze-2019-the-battle-of-liability/) | SNIPPET; report date unknown |
| 6 Oct 2023 | Sumatra hotspots rise significantly; Indonesia denies causing haze | [NEA 8 Oct](https://www.nea.gov.sg/media/news/advisories/index/haze-situation-update-8-october-2023), [Star](https://thestar.com.my/aseanplus/aseanplus-news/2023/10/07/singapore-air-turns-unhealthy-but-indonesia-still-denies-causing-haze) | SNIPPET |
| 7 Oct 2023 | 24-hr PSI unhealthy (east 105 at 8am, later east 111, central 102); moderate (57-86) on 8 Oct | [Mothership](https://mothership.sg/2023/10/singapore-unhealthy-haze), [NEA 7 Oct](https://nea.gov.sg/media/news/advisories/index/haze-situation-update-7-october-2023) | SNIPPET |

No project-listed company was confirmed as named in 2015, 2019 or 2023, but that reflects shallow search, not absence. Not retrieved for 2015: first unhealthy day, peak PSI, APP supermarket delisting dates, Indonesian concession freezes. Not retrieved for 2019: PSI peak, Singapore minister statements, THPA actions, and whether Wilmar, GAR, First Resources or Bumitama were named. Not retrieved for 2023: any named companies or ministerial statements. The 2023 episode was short, so it is weak for the main design.

## Consolidated list of what still needs manual verification

### Blocked or unreachable hostnames

| Research area | Hostnames that failed (DNS, ENOTFOUND, or proxy 403) |
|---|---|
| Fire and concessions | firms.modaps.eosdis.nasa.gov, data.globalforestwatch.org, datasets-dev.wri.org, apis.io, appliedsciences.nasa.gov, rallypointone.github.io |
| Market and salience | data.gov.sg, guide.data.gov.sg, api-open.data.gov.sg, cds.climate.copernicus.eu, market.bisnis.com, snips.stockbit.com, theedgesingapore mirrors |
| Econometrics | arxiv.org, api.crossref.org, py-econometrics.github.io, bashtage.github.io, www.statsmodels.org, the journal sites |
| Timelines | thestar.com.my, mongabay, mothership.sg, nea.gov.sg, greenpeace.org, wikipedia, plus most other news hosts |
| Literature | Crossref, MDPI, SSRN, Google Scholar (proxy 403 or DNS) |
| Reachable (only) | pypi.org, github.com, and the web-search tool for the econometrics session |

Hosts to allowlist for a second pass: firms.modaps.eosdis.nasa.gov, nrt3/nrt4.modaps.eosdis.nasa.gov, urs.earthdata.nasa.gov, data.globalforestwatch.org, data-api.globalforestwatch.org, data.gov.sg, api-open.data.gov.sg, cds.climate.copernicus.eu, nea.gov.sg, links.sgx.com, doi.org, and the news hosts above.

### Verification checklist, ordered by what blocks the loaders

| Priority | Item | Why it matters |
|---|---|---|
| 1 | FIRMS: confirm the URL template, MAP_KEY placement, maximum day range, rate limit, CSV columns, and whether the API serves 2015/2019/2023; test `/api/data_availability/` and the IDN country endpoint | Fire loader |
| 1 | Request the historical Sumatra and Kalimantan archive extracts by hand (email delivery) | 2015/2019/2023 exposure |
| 1 | S-NPP cessation date (1 vs 2 Nov 2026) and the July 2026 non-nominal status; NOAA-20/21 SP availability for 2026 | Cross-year consistency |
| 1 | GFW concession layer: attributes, licence, file format, download URL, Data API id, Indonesian coverage and vintage | No polygons otherwise |
| 1 | Listing status and dates for First Resources (EB5), Bumitama (P8Z), Kencana Agri, all six IDX names and other candidate tickers; Indofood Agri status from SGX itself | Panel construction |
| 1 | Yahoo symbols; behaviour of delisted tickers; proxy and CA behaviour of curl_cffi; alternatives (Stooq, IDX, SGX, EODHD) | Price loader |
| 1 | FCPO source: a free scriptable series, the roll convention, other palm price series | CPO factor |
| 1 | data.gov.sg PSI: correct dataset id, columns, timestamp convention, currency of the CSV, v2 path, v1 status, API key requirement; NEA band table | PSI loader |
| 2 | Open each 2026 timeline URL; Wong's post time; the 16 Oct closing moves; Greenpeace 5 Oct report title and company list; names of the seven and ten notified firms; the SGX First Resources announcement | Event dating |
| 2 | 2015, 2019 and 2023 timelines: PSI peaks, NGO reports naming listed firms, ministerial and THPA actions | Event set |
| 2 | ERA5 variable names, `area` ordering, licence; user token; lighter wind alternatives | Wind instrument |
| 2 | Google Trends/pytrends status and GDELT DOC 2.0 endpoint and limits | Attention proxy |
| 2 | Package APIs by `help()`: pyfixest (two-way, IV, Webb weights, `ritest`), linearmodels (`PanelOLS`, `IV2SLS`), statsmodels; wildboottest FE handling and weights; release dates | Estimation code |
| 2 | Event-study formulas (GRANK in KP 2011; MacKinlay 1997) and handling of two events 11 days apart; IDX price-limit history and holiday calendars | Event study |
| 3 | All BKG DOIs via `https://doi.org/<DOI>`; Gaveau et al. (2017) Conservation Letters; Da-Gurun-Warachka venue; JRFM 12(4):175 content | Citation integrity |
| 3 | Manual novelty sweep: SSRN, Google Scholar, JEEM, Ecological Economics, Energy Economics, Pacific-Basin Finance Journal, World Development, Indonesian-language sources; queries "haze" + "abnormal returns", "forest fire" + "plantation" + "stock", "Bursa Malaysia" + "haze", "kabut asap" + "saham" | Novelty claim |

## Conclusion

The project is ready to be designed but not yet to be coded against. Only the 2026 timeline is detailed enough to anchor an event window, and it shows the sharpest salience mechanism in the notes: a Greenpeace report on 5 Oct that moved little, then a Singapore government statement on the evening of 15 Oct that coincided with a Friday sell-off in First Resources, Bumitama, GAR and Wilmar. That is consistent with the project's hypothesis that public fire information is repriced once Singapore salience arrives, but the figures are press numbers, not abnormal returns, and the three earlier seasons are too thinly documented to say whether the pattern is general. The novelty position should be worded "to our knowledge, no prior study", given that SSRN and Google Scholar were never reached.

Two practical findings reshape the build. Fire exposure for 2026 cannot rest on S-NPP, and concession-level exposure currently has no confirmed geometry, so the first manual tasks are the FIRMS archive requests and a hands-on inspection of the GFW concession layer. On inference, only five packages were read live and the rest of the method stack is recalled, so the first coding step should be a simulated-panel check that a hand-rolled wild cluster bootstrap and the chosen two-way or Driscoll-Kraay errors behave properly with 5-20 firms and four seasons.
