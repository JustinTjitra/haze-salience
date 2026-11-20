# Feasibility check on live pages (T115)

All pages below were read on **20 November 2026** (about 16:00 UTC) from the task loop's cloud
environment, with plain HTTPS requests and no account, key or sign-up. Every statement carries the
URL it came from. Anything not read on a live page is labelled **not confirmed**. No data file was
downloaded or committed; only metadata and a handful of rows were read.

This file reports what the providers' pages say. It does not judge the go/no-go.

## 1. Concession polygons (Global Forest Watch)

**Dataset.** "Indonesia oil palm concessions", item `f82b539b9b2f495e853670ddc3f0ce68`, layer 2,
on the GFW open data portal. Found with the portal's search API:
`https://data.globalforestwatch.org/api/search/v1/collections/dataset/items?q=oil%20palm%20concessions&limit=20`.
Metadata read from `https://data.globalforestwatch.org/api/v3/datasets/f82b539b9b2f495e853670ddc3f0ce68_2`.
Portal page: `https://data.globalforestwatch.org/datasets/gfw::indonesia-oil-palm-concessions/about`.

| Item | What the metadata says |
| --- | --- |
| Description | "Provides the boundaries of current or planned oil palm plantations in Indonesia." |
| Type | Feature layer, polygons (`esriGeometryPolygon`) |
| Features | `recordCount` 1845; the `country` field is `IDN` for all 1845 |
| Service URL | `https://gis-gfw.wri.org/arcgis/rest/services/country_data/asia/MapServer/2` (query formats JSON, AMF, geoJSON; 1000 records per request) |
| Direct download | `http://gfw2-data.s3.amazonaws.com/country/idn/zip/idn_oil_palm.zip` (format of the zip's contents **not confirmed**) |
| Item created / modified | 25 Feb 2015 / 10 Oct 2023 (item timestamps). Embedded metadata `ModDate`: 2019-04-02 |
| Source of the polygons | "Ministry of Forestry Indonesia (2010) ... downloaded as Google Earth files (kml) ... accessed 29 July 2010, supplemented with data gathered from provincial planning agencies (BPN). Processed and provided by Greenpeace (2011). Prepared by the World Resources Institute (2012)." |
| Licence field | Contains only a caution: "This data set is known to be incomplete, but it is currently the best available." No licence name is given for this layer. Other layers in the same search (for example the Sarawak one) state CC BY 4.0; this one does not. |
| Citation asked for | "Indonesia Ministry of Forestry, Greenpeace, and WRI. 'Indonesia oil palm concessions.' Accessed through Global Forest Watch on [date]. www.globalforestwatch.org." |

**Attribute fields** (from the layer's field list in the same metadata record; the file itself
could not be opened, see below): `objectid_1`, `objectid`, `po_legalst`, `po_legal_1`, `po_hgu`,
`po_area_hg`, `subgroup`, `groupid`, `source`, `zsl`, `group_comp`, `shape_leng`, `type`,
`area_ha`, `country`, `company`, `name`, `gfwid`, `shape`, `globalid`, `shape_Length`,
`shape_Area`.

**Company and group attributes.** The portal's own field statistics, in the same record:

- `group_comp`: 81 distinct values over 1845 features. 1278 features are "No group", so 567
  carry a group name. The most frequent: Sinar Mas (78), Wilmar (43), Astra International (42),
  Sime Darby (40), Lyman Group (21), Duta Palma Group (21), Surya Dumai Group (20).
- `company`: filled for 1647 of 1845 features. The statistics list is capped at 1000 distinct
  values, so the true number of distinct company names is 1000 or more.
- `subgroup`: blank for 1813 features.
- `type` (permit type): blank for 953; `HGU` 382; `Ijin Lokasi` 295; `HGU in process` 95.

**What could not be done from this environment.**

- The polygons were not opened. The service host `gis-gfw.wri.org` is refused by the
  environment's network policy (proxy 403). The direct-download object answered
  `AccessDenied` from S3 itself (HTTP 403 at `https://gfw2-data.s3.amazonaws.com/country/idn/zip/idn_oil_palm.zip`),
  so that link may be dead or private for everyone, not only for the loop: **not confirmed**
  either way. The portal's own export routes
  (`https://data.globalforestwatch.org/datasets/f82b539b9b2f495e853670ddc3f0ce68_2.geojson` and
  `/api/download/v1/items/.../geojson?layers=2`) returned no response.
- How many of the 1845 features fall in Sumatra and Kalimantan: **not confirmed** (needs the
  geometry). The item's bounding box spans all of Indonesia (95.28E to 140.94E).
- `www.globalforestwatch.org` and `data-api.globalforestwatch.org` are also refused by the
  network policy, so any newer concession layer published only there was not seen.

**Needed to finish this item:** the owner opens the portal page above in a browser and tries the
download, or adds `gis-gfw.wri.org` to the environment's allowed hosts.

## 2. FIRMS API (NASA)

Read from `https://firms.modaps.eosdis.nasa.gov/api/` (index, "API Version: 4.2.10"),
`https://firms.modaps.eosdis.nasa.gov/api/area/`, `https://firms.modaps.eosdis.nasa.gov/api/data_availability/`,
`https://firms.modaps.eosdis.nasa.gov/api/map_key/` and `https://firms.modaps.eosdis.nasa.gov/download/`.
The host reset about half of the connections; each page was read on a retry.

- **URL template** (`/api/area/`):
  `/api/area/csv/[MAP_KEY]/[SOURCE]/[AREA_COORDINATES]/[DAY_RANGE]` for the most recent days, and
  `/api/area/csv/[MAP_KEY]/[SOURCE]/[AREA_COORDINATES]/[DAY_RANGE]/[DATE]`, which
  "Returns data for [DATE] .. [DATE + DAY_RANGE-1]".
- **Where the key goes:** in the URL path, as the segment after `csv/`.
- **Area:** `west,south,east,north` bounding box, or `world`.
- **Day range:** "1 .. 5 - number of days to query at one time". One season (1 Aug to 30 Nov, 122
  days) is therefore at least 25 requests per product.
- **Date:** `YYYY-MM-DD`, optional.
- **Rate limit:** "MAP_KEY limit is 5000 transactions / 10-minute interval. Larger transactions
  may count as multiple requests (ex. requesting 7 days)."
- **Product names (`SOURCE`):** `LANDSAT_NRT` (US/Canada only), `MODIS_NRT`, `MODIS_SP`,
  `VIIRS_NOAA20_NRT`, `VIIRS_NOAA20_SP`, `VIIRS_NOAA21_NRT`, `VIIRS_NOAA21_SP`,
  `VIIRS_SNPP_NRT`, `VIIRS_SNPP_SP`. NRT is near real-time, SP is standard processing.
- **Key:** "sign up for free MAP_KEY using your email. The key will be sent to your email."
  No key was requested. **The owner must supply one.**
- **Country endpoint:** the index lists `/api/country/` as "Feature currently not available", so
  requests have to use a bounding box.
- **Does the API serve Aug to Nov of 2015, 2019 and 2023? Not confirmed.** The API offers the
  standard-processing sources and a `DATE` argument, but the dates each source covers are only
  returned by `/api/data_availability/csv/[MAP_KEY]/[SENSOR]`, which needs a key. With a key this
  is one request.
- **Archive tool** (`/download/`): for data "older than the last 7 days", as shapefile, CSV or
  JSON. It needs an Earthdata login or an emailed code, and "Once the request has been processed,
  you will receive an email with instructions on how to download your data." That step cannot
  run unattended. Temporal coverage stated there: MODIS Collection 6.1 "1 November 2000 -
  present"; VIIRS S-NPP 375m "20 January 2012 - 2 November 2026"; VIIRS NOAA-20 375m "1 April
  2018 - present"; VIIRS NOAA-21 375m "1 March 2023 - present". The same page says NRT data are
  replaced by standard-quality data "with approximately a 5 month lag".
- **S-NPP.** The download page gives S-NPP coverage ending **2 November 2026**, where the other
  sensors say "present". That is consistent with the earlier report that S-NPP delivery ended in
  November 2026, and it gives the date. No announcement explaining the end was read: **reason not
  confirmed**. The API pages still list `VIIRS_SNPP_NRT` and `VIIRS_SNPP_SP` as sources.
- **Bearing on the sensor choice (a DECIDE item, not decided here):** by the coverage dates
  above, S-NPP and MODIS both span 2015, 2019, 2023 and the 2026 season up to 2 November; NOAA-20
  starts after the 2015 season; NOAA-21 starts in March 2023.

## 3. PSI history (data.gov.sg)

**Bulk file.** Dataset "Historical 24-hr PSI", agency NEA (National Environment Agency), dataset
id `d_b4cf557f8750260d229c49fd768e11ed`, format CSV, under the Open Data Licence. Page:
`https://data.gov.sg/datasets/d_b4cf557f8750260d229c49fd768e11ed/view` (the page describes it as
"Historical regional 24-hr PSI").

- **Columns** (from `https://data.gov.sg/api/action/datastore_search?resource_id=d_b4cf557f8750260d229c49fd768e11ed&limit=1`):
  `24hr_psi` (the timestamp, text, day-first, for example `25/9/2015 0:00`), `north`, `south`,
  `east`, `west`, `central` (all text), plus the row id `_id`. There is no national column.
- **Rows:** 109,584, hourly. First row `1/4/2014 1:00`; last row `1/10/2026 0:00` (read with
  `&sort=_id desc`). 109,584 is exactly the number of hours between those two timestamps, so the
  file has no missing hours by count.
- **2015 coverage: yes.** Rows 13007 and 13008 (read with `&limit=2&offset=13006`) are
  `24/9/2015 23:00` and `25/9/2015 0:00`.
- **The file ends on 1 October 2026**, so it does not contain October and November 2026.
- **Download URL:** `https://api-open.data.gov.sg/v1/public/api/datasets/d_b4cf557f8750260d229c49fd768e11ed/poll-download`
  returned `DOWNLOAD_SUCCESS` with a temporary signed link to the CSV on
  `s3.ap-southeast-1.amazonaws.com`. The link was not followed. The row API above pages through
  the same data without leaving `data.gov.sg`.
- **Key:** none was needed for any request above.

**Real-time API.** `https://api-open.data.gov.sg/v2/real-time/api/psi` answered without a key and
returned the reading for 20 Nov 2026. With `?date=YYYY-MM-DD` it returned 24 hourly items for
2019-09-18 and data for 2016-09-25, but "Data not found" for 2015-09-25, 2015-12-31 and
2016-02-01. So it does not reach the 2015 season; its exact first date is **not confirmed**. Its
readings include `psi_twenty_four_hourly` by region (and, in the 2016 response, a `national`
region). It can fill October and November 2026, which the bulk file lacks.

**Not read:** the rate limits of either API, and the dataset's metadata endpoint on
`api-production.data.gov.sg`, which the network policy refuses.

## Hosts refused or failing

| Host | Result |
| --- | --- |
| `gis-gfw.wri.org` | Refused by the environment's network policy (proxy 403) |
| `www.globalforestwatch.org` | Refused by the network policy |
| `data-api.globalforestwatch.org` | Refused by the network policy |
| `api-production.data.gov.sg` | Refused by the network policy |
| `gfw2-data.s3.amazonaws.com` | Reached; S3 answered `AccessDenied` for the concession zip |
| `firms.modaps.eosdis.nasa.gov` | Allowed; intermittent connection resets, pages read on retry |

## Verdict

- Concession source usable: **partly**. A 1845-polygon Indonesian layer with `company` and `group_comp` fields exists, but its geometry could not be opened from here, its sources date from 2010, it is labelled incomplete, and 1278 features have no group.
- FIRMS history obtainable unattended: **no**, as things stand. The API needs the owner's MAP_KEY, and whether it then serves 2015, 2019 and 2023 is not confirmed; the archive tool delivers by email.
- PSI history covers 2015: **yes** (hourly regional 24-hour PSI from 1 April 2014 to 1 October 2026).
