# T115 Feasibility check on live pages

Tier: planner · Depends: none · Needs: network (available since 20 Nov 2026)

## Goal
Before the go/no-go, the owner knows whether the diffusion design (Phase 3) can be built at all.
The source research of 20 Nov could not open a single data provider's page, so the three inputs
below are still unconfirmed.

## Files
- `docs/feasibility.md` (new)

## What to confirm, each on the provider's own page
1. **Concession polygons.** Is there a downloadable oil palm concession layer covering Sumatra and
   Kalimantan with a company or group attribute? Start from `data.globalforestwatch.org`. Record
   the dataset name, download URL, format, attribute fields (open the file and list the property
   names), last update, licence, and how many features fall in Indonesia. If nothing usable
   exists, say so plainly: that makes the regulatory-event story the fallback whatever the pilot
   shows.
2. **FIRMS API.** From `firms.modaps.eosdis.nasa.gov/api`: the exact URL template, where the key
   goes, the day-range and rate limits, the product names, and whether the API serves Aug to Nov
   of 2015, 2019 and 2023 or only the archive tool does. Confirm or correct the report that S-NPP
   delivery ended in November 2026. Do not request a key and do not sign up for anything; record
   that the owner must supply one.
3. **PSI history.** From `data.gov.sg` and `api-open.data.gov.sg`: the dataset id and download URL
   of the bulk 24-hour PSI file, its columns, its first and last dates (does it cover Aug to Nov
   2015?), and whether the API needs a key.

## Rules
- Only hosts the environment allows. If a host is refused, record the host name and move on.
- Every statement in `docs/feasibility.md` carries the URL it came from and the date it was read.
  Anything not read on a live page is labelled "not confirmed".
- Download only what is needed to read field names. Commit no data.
- End the file with a three-line verdict: concession source usable (yes / no / partly), FIRMS
  history obtainable unattended (yes / no), PSI history covers 2015 (yes / no).

## Out of scope
Writing loaders, choosing the sensor (a DECIDE item for the owner), judging the go/no-go.
