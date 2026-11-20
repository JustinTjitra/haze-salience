# Fire-detection (NASA FIRMS) and Indonesian oil palm concession data sources, as of Nov 2026

**RESEARCH LIMITATION (read first):** In this session, WebFetch could not resolve ANY target host (firms.modaps.eosdis.nasa.gov, data.globalforestwatch.org, datasets-dev.wri.org, apis.io, appliedsciences.nasa.gov, rallypointone.github.io all returned ENOTFOUND; the session network allowlist blocks them). Only WebSearch worked, so every finding below comes from search-result summaries, NOT from reading the live pages. Treat all of it as "search-snippet verified, live page not read". The coding agent must test endpoints before relying on them. To redo this properly, allow firms.modaps.eosdis.nasa.gov and data.globalforestwatch.org (and data-api.globalforestwatch.org) in the session network settings.

## NASA FIRMS API: endpoints, URL structure, key placement, limits, output columns

### Takeaway
The official API page lists eight source identifiers and an area endpoint at /api/area/csv plus /api/data_availability/. Day-range maximum and rate limit were only seen via third-party summaries (1-5 days; 5000 transactions per 10 minutes), so they are unconfirmed.

### Cited Findings
- Area endpoint documentation lives at https://firms.modaps.eosdis.nasa.gov/api/area/csv ; the endpoint takes MAP_KEY, source, area coordinates and day range, and without a date returns data from today back to today minus (DAY_RANGE-1) — [FIRMS API / area](https://firms.modaps.eosdis.nasa.gov/api/area/csv) (via search summary)
- Official API page lists eight source identifiers: LANDSAT_NRT, MODIS_NRT, MODIS_SP, VIIRS_NOAA20_NRT, VIIRS_NOAA20_SP, VIIRS_NOAA21_NRT, VIIRS_SNPP_NRT, VIIRS_SNPP_SP; LANDSAT_NRT is US and Canada only; /api/data_availability/ checks product date availability; the date parameter of the area endpoint is optional — [FIRMS API](https://firms.modaps.eosdis.nasa.gov/api) (via search summary of the API page)
- A third-party OpenAPI spec says day range is 1 to 5 and the key is rate limited to 5000 transactions per 10-minute interval; another source says each day counts as one transaction — [NASA FIRMS Area Fire Detections API (apis.io)](https://apis.io/apis/nasa-firms/nasa-firms-area-fire-detections-api/) ; NASA's own page not read, so unverified
- NASA's API page links to a status check for remaining transactions for a key — [FIRMS API / area](https://firms.modaps.eosdis.nasa.gov/api/area/csv)
- Third-party connector and client docs exist (Microsoft Power Platform connector, Julia clients) that wrap the same API — [MS connector](https://learn.microsoft.com/en-us/connectors/nasafirms), [GeoDataAccess.jl](https://rallypointone.github.io/GeoDataAccess.jl/dev/sources/nasa_firms.html)
- Country API documentation is at https://firms.modaps.eosdis.nasa.gov/api/country/ (URL exists per FIRMS docs structure; contents not read) — see Gaps

### Inferences
- Because the day range cap is likely 5 (or at most ~10), a loader for a ~120-day haze season should loop in chunks of <=5 days per bounding-box call and respect 5000 tx / 10 min. An archive download is far more efficient for 2015/2019/2023.

### Gaps
- NOT VERIFIED on any live page: exact URL template (from memory it is https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{west,south,east,north}/{DAY_RANGE}/{YYYY-MM-DD}, i.e. MAP_KEY in the URL path, not a header); this recollection is unsourced here.
- Max day range and transaction accounting (see third-party claims above); country API parameters (IDN code); output column list for the API CSV (only partial attribute info found, see semantics section); data_availability output format (search could not find it).
- Whether the API serves 2015, 2019, 2023: not confirmed. Archive coverage statements suggest SP data exist back to 2012 (VIIRS) / 2000 (MODIS), but API date-range limits per source were not found.

## Archive download tool and hosts

### Takeaway
The Archive Download tool (https://firms.modaps.eosdis.nasa.gov/download/) serves MODIS and VIIRS data older than ~7 days as shapefile, CSV or JSON, with Earthdata Login or email authentication and delivery by email.

### Cited Findings
- Archive Download supports MODIS and VIIRS, sign-in via Earthdata Login or an emailed code, formats shapefile/CSV/JSON; you submit a request and receive an email with download instructions — [Archive Download](https://firms.modaps.eosdis.nasa.gov/download/) (via search summary)
- Coverage cited: MODIS Collection 6 from 11 November 2000; VIIRS 375 m from 20 January 2012 (page-level sources differ; NOAA-21 from 17 January 2024) — [Archive Download](https://firms.modaps.eosdis.nasa.gov/download/); note a separate search summary attributed 20 Jan 2012 to the NOAA-20 standard product, which is implausible since NOAA-20 launched in 2017 (conflict; treat the 2012 date as S-NPP's start, unverified) — [VIIRS I-Band 375 m page](https://www.earthdata.nasa.gov/data/instruments/viirs/near-real-time-data/viirs-i-band-375-m-active-fire-data)
- NRT file archive hosts: https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/ and https://nrt4.modaps.eosdis.nasa.gov/archive/FIRMS/ (README at nrt3 .../README.pdf); access needs Earthdata credentials, with wget and an Earthdata Download Token — [nrt4 archive](https://nrt4.modaps.eosdis.nasa.gov/archive/FIRMS/), [nrt3 README](https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/README.pdf)
- Alternate FIRMS host exists: https://firms2.modaps.eosdis.nasa.gov/download/ (mirror) — [firms2 download](https://firms2.modaps.eosdis.nasa.gov/download/)

### Inferences
- Hosts a script likely needs: firms.modaps.eosdis.nasa.gov (API, archive tool), nrt3/nrt4.modaps.eosdis.nasa.gov (file archive), urs.earthdata.nasa.gov (Earthdata login; hostname from general knowledge, not confirmed in sources), possibly firms2.modaps.eosdis.nasa.gov.
- Archive delivery by email means a human-in-the-loop step; an unattended agent cannot fetch 2015/2019/2023 data without a pre-delivered file. Request once, manually, a Sumatra+Kalimantan extract per season.

### Gaps
- Per-request area/size limits of the archive tool, retention time of emailed links, and file naming were not found.

## FIRMS data semantics, S-NPP status and gaps

### Takeaway
The biggest finding: Suomi NPP VIIRS data delivery ceases at the start of November 2026 (and S-NPP may have been non-nominal since July 2026), which directly affects the 2026 season. Use NOAA-20/NOAA-21 for 2026.

### Cited Findings
- NASA FIRMS says production and delivery of new FIRMS Suomi NPP active fire data ceases at 13:00 UTC on 2 November 2026; NOAA's notice and NASA's forum give 1 November 13:00 UTC (date conflict) — [NASA Earthdata blog](https://www.earthdata.nasa.gov/news/blog/transitioning-from-s-npp-viirs-omps-what-nasa-firms-users-need-know), [NOAA NESDIS](https://www.nesdis.noaa.gov/news/cessation-of-suomi-national-polar-orbiting-partnership-s-npp-data-users-onafter-november-01-2026), [Earthdata forum](https://forum.earthdata.nasa.gov/viewtopic.php?p=26446)
- API/feed users are told to switch from VIIRS_SNPP_NRT/VIIRS_SNPP_SP to VIIRS_NOAA20_NRT or VIIRS_NOAA21_NRT; NASA says no loss of afternoon-orbit observation capability — [NASA Earthdata blog](https://www.earthdata.nasa.gov/news/blog/transitioning-from-s-npp-viirs-omps-what-nasa-firms-users-need-know)
- S-NPP VIIRS products remain available for dates prior to 2 November 2026 — [Archive Download](https://firms.modaps.eosdis.nasa.gov/download/)
- A Copernicus notice says S-NPP entered a non-nominal state in July 2026 and its science data have been unavailable since then (this is a snippet-level claim; affects Aug-Oct 2026 completeness) — [Copernicus Land](https://land.copernicus.eu/en/production-updates/global-burnt-area-production-temporary-switch-to-noaa-viirs-source-3)
- NOAA-21 VIIRS active fire in FIRMS from 2024; coverage 17 Jan 2024 to present — [FIRMS wiki](https://wiki.earthdata.nasa.gov/spaces/FIRMS/blog/2024/02/08/343475617/NOAA-21+VIIRS+Active+Fire+Detection+Data+Now+Available)
- VIIRS 375 m confidence is categorical low/nominal/high; low daytime pixels tied to sun glint / weak MIR anomaly (<15 K), nominal has strong anomaly (>15 K), high tied to saturated pixels — [VIIRS I-Band 375 m page](https://www.earthdata.nasa.gov/data/instruments/viirs/near-real-time-data/viirs-i-band-375-m-active-fire-data). Earth Engine encodes it 0/1/2, but FIRMS CSVs use letters l/n/h (letters from memory, unverified) — [Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/NASA_LANCE_SNPP_VIIRS_C2)
- MODIS confidence is 0-100%, binned low/nominal/high — [FIRMS attributes](https://earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs)
- acq_time is overpass time in UTC; daynight D/N; frp in MW; version field encodes collection plus NRT suffix (e.g. 6.1NRT); satellite codes MODIS A/T, VIIRS N (S-NPP) / 1 (NOAA-20) — [FIRMS attributes](https://earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs), [apis.io schema](https://apis.io/schemas/nasa-firms/fire-detection/); acq_time format HHMM in CSV vs seconds in Earth Engine (conflict) — [Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/NASA_LANCE_SNPP_VIIRS_C2)
- NRT data may have geolocation errors or be reprocessed and are not science quality; standard (SP) is science quality — [Earth Engine NRT description](https://developers.google.com/earth-engine/datasets/catalog/NASA_LANCE_SNPP_VIIRS_C2)
- Authoritative references to read: [VIIRS C2 AF 375m User Guide 1.2](https://www.earthdata.nasa.gov/s3fs-public/2025-06/VIIRS_C2_AF-375m_User_Guide_1.2.pdf), [MOD14 User Guide V61](https://LPDAAC.USGS.GOV/documents/1005/MOD14_User_Guide_V61.pdf)

### Inferences
- For 2015, 2019, 2023 use SP products (VIIRS_SNPP_SP; MODIS_SP); for 2026 use VIIRS_NOAA20/NOAA21 (NRT likely, SP lag unknown) and treat S-NPP as truncated; construction of a cross-year consistent measure should consider the sensor switch (NOAA-20/21 overpass ~13:30 like S-NPP, per NASA statement of afternoon orbit).
- 2026 season exposure is not comparable on S-NPP-only basis; a harmonised series should use NOAA-20 where available or MODIS.

### Gaps
- Overpass times over Sumatra/Kalimantan in WIB (S-NPP ~13:30 local solar equator crossing is from general knowledge; not sourced here, convert UTC+7 WIB; Kalimantan can be WIB for West/Central, WITA UTC+8 for East/South). Not verified.
- Known S-NPP outages/gaps in Aug-Nov 2015, 2019, 2023: none found. Exact CSV column list incl. bright_ti4/ti5 (unconfirmed); VIIRS 375 m start date for S-NPP given as 20 Jan 2012 in archive coverage text only.
- Differences in NRT vs SP for confidence field: one summary said FIRMS NRT confidence fields removed, conflicting with Earth Engine; unresolved.

## Global Forest Watch oil palm concessions

### Takeaway
GFW hosts a global "Oil Palm Concessions" compilation (not Indonesia-only); a current version updated monthly appears in the WRI dataset catalogue. Exact API ids, fields and download URLs were not verified.

### Cited Findings
- Dataset "oil-palm-concessions-lm-v3-gfw": areas allocated by governments to companies for oil palm; created 27 May 2024, last updated 13 Mar 2025; compiled from various countries and sources — [WRI datasets](https://datasets-dev.wri.org/datasets/oil-palm-concessions-lm-v3-gfw)
- Newer dataset "com-024-rw0-nrt-oil-palm-concessions-rw": updated monthly, created/updated 25 Nov 2025; may not include all concessions and locations may be inaccurate — [WRI datasets](https://datasets-dev.wri.org/datasets/com-024-rw0-nrt-oil-palm-concessions-rw)
- A Land Matrix record cites an older file "indonesia_oil_palm_concessions" from data.globalforestwatch.org dated 2020-05-27 — [Land Matrix](https://landmatrix.org/deal/8104/82374/data-sources)
- GFW also hosts palm oil mills (Universal Mill List derived) — [WRI mills dataset](https://datasets-dev.wri.org/datasets/palm-oil-mills-lm-v3v202207-gfw); Universal Mill List blog — [GFW](https://www.globalforestwatch.org/blog/data/improved-universal-mill-list-expands-partnerships-improves-transparency-in-palm-oil-industry/)
- Oil palm extent/planting year raster (Descals et al.), CC-BY-4.0 — [Earth Engine BIOPAMA](https://developers.google.com/earth-engine/datasets/catalog/BIOPAMA_GlobalOilPalm_v1_2)

### Inferences
- Hostnames likely: data.globalforestwatch.org (ArcGIS Hub downloads), data-api.globalforestwatch.org (Data API), gis-gfw.wri.org; the last two not confirmed here.
- Indonesia data originate from Ministry (KLHK/ATR-BPN) permits; Greenpeace court-case reporting (below) indicates the official data are restricted, so coverage/vintage is likely uneven.

### Gaps
- Attribute fields (company, group, licence type, area), license (CC BY 4.0 unconfirmed), file format and URLs, data API dataset id/version, province-level coverage gaps: not found.

## Alternative concession and ownership sources

### Takeaway
Few are cleanly downloadable. Kepo Hutan says official data are unavailable; Nusantara Atlas incorporates the Greenpeace concession compilation but no bulk download was found.

### Cited Findings
- Kepo Hutan (Greenpeace): site says official data are not currently available due to Indonesian government restrictions — [Kepo Hutan](https://kepohutan.greenpeace.org/about)
- Greenpeace maps were built from paper maps/PDFs digitised to shapefiles; no public download found — [Eco-Business](https://www.eco-business.com/news/indonesias-forestry-ministry-takes-greenpeace-to-court-over-freedom-of-information-request); Greenpeace says 2017 Supreme Court ruled oil palm concession data public information — same
- Nusantara Atlas compiles concessions, mills and company names and the Greenpeace concession dataset — [Nusantara Atlas blog](https://nusantara-atlas.org/palm-oil-giant-using-shadow-companies-to-hide-their-links-to-deforestation-of-tiger-habitat-in-sumatra), [Milieudefensie report](https://milieudefensie.nl/actueel/astra-agro-lestari-kapt-indonesisch-bos-palmolie/@@download/file/ASTRA%20AGRO%20LESTARI%20PENETRATES%20INDONESIA_S%20FORESTS_final%20March%202024.pdf)
- A report noted that none of the groups reviewed has published concession boundaries in a reusable format such as shapefiles — [FoE Cultivating Conflict (Astra Agro Lestari)](https://foe.org/wp-content/uploads/2024/06/AAL_CultivatingConflict_Eng_final.pdf) (via snippet; context is Astra Agro Lestari-related reporting)
- Trase Indonesia palm oil supply chain data: years 2018-2024, v1.2.5, DOI 10.48650/0717-AJ12; maps/graphics CC BY 4.0, raw-data licence not stated on page, commercial use via info@trase.earth — [Trase](https://trase.earth/open-data/datasets/supply-chains-indonesia-palm-oil); new 2023-24 data scheduled 13 Oct 2026 — [SEI](https://www.sei.org/about-sei/press-room/indonesia-palm-oil-domestic-demand/)
- Aidenvironment Nusantara reporting exists — [Aidenvironment PDF](https://aidenvironment.org/wp-content/uploads/2021/02/Nusantara-Fiber-Report-Aidenvironment.pdf) (a fibre report; not a concession dataset)

### Inferences
- Trase supply-chain data is mill/trader-level, not concession polygons; use for ownership links not geometry.

### Gaps
- GeoRSPO (download terms, formats): search returned nothing relevant. Chain Reaction Research, company sustainability-report concession lists (First Resources, Bumitama, GAR/SMART, Wilmar, Salim Ivomas/Lonsum, AAL, SSMS, DSN) were not searched or found. Nusantara Atlas terms/exports unverified.

## Concession-to-parent linking and prior fire attribution work

### Takeaway
Prior work exists but with mixed methods; the main peer-reviewed caution is that attribution of fire to concessions is hard because of overlapping claims.

### Cited Findings
- Gaveau et al. (Conservation Letters 2017): 163 Riau oil palm and pulpwood concessions; attribution of fire and deforestation is effectively impossible without field investigation; CIFOR summary: about half of fires in concessions, ~60% of burned area outside concessions within 5 km (pulpwood-specific) — [CIFOR](https://forestsnews.cifor.org/embed-post/46097), [UMT PDF](https://www.umt.edu/media/leopold/pubs/925.pdf)
- Overlapping land claims limit satellite monitoring of no-burning compliance — [AGRIS record](https://agris.fao.org/search/en/records/672359fbb605bda15e0a7b44)
- Greenpeace 2019 linked traders to producers with hotspots (Wilmar-supplied groups >140,000 ha burned 2015-2018); advocacy source — [Greenpeace Burning Down the House](https://www.greenpeace.org/static/planet4-taiwan-stateless/2024/01/02b74d15-burning-down-the-house-2019.pdf)
- Sept 2026 NGO analysis: nearly a quarter of burned forest/peat across Indonesia inside concessions, majority from oil palm — [Jakarta Post](https://thejakartapost.com/indonesia/2026/09/04/unchecked-businesses-blamed-for-raging-wildfires)
- Universal Mill List (GFW) maps mills to parent groups — [GFW blog](https://www.globalforestwatch.org/blog/data/improved-universal-mill-list-expands-partnerships-improves-transparency-in-palm-oil-industry/)

### Inferences
- A 0 km (inside polygon) plus 5 km buffer sensitivity is defensible, citing Gaveau; also flag polygon-overlap and smallholder/plasma uncertainty.

### Gaps
- Specific peer-reviewed paper attributing FIRMS hotspots to SGX/IDX-listed firms with buffer specs: not found.

## Indonesia boundaries / bounding boxes for FIRMS queries

### Takeaway
Not researched successfully.

### Cited Findings
- None found (search returned nothing on GADM/geoBoundaries).

### Inferences
- Unsourced suggestion only: use GADM level-1 or geoBoundaries IDN ADM1 to select Sumatra and Kalimantan provinces and query the union bounding box in chunks.

### Gaps
- Sumatra/Kalimantan bounding boxes, GADM/geoBoundaries URLs and licences: not verified.
