# Haze Salience and Price Discovery: Design Doc

Nov 8, 2026 · @tjitra

## Summary

This project tests whether satellite fire data predicts palm oil stock returns, and whether prices only react once haze makes the fires salient to investors. It uses the 2026 Southeast Asian haze crisis as the anchor case and stacks the 2015, 2019, 2023 and 2026 haze seasons for statistical power.

The core signal is a daily, firm-level fire exposure measure: NASA FIRMS hotspots inside each company's plantation concessions. The attention shock is Singapore's daily PSI air quality reading, which depends heavily on wind direction rather than on any one firm's fires. If returns respond to fire exposure mainly on high-PSI days, that is evidence of attention-driven slow information diffusion.

The target deliverable is a reproducible pipeline, a short research note, and a one-line resume claim with a number in it, ready before the Jane Street FTTP deadline on 31 January 2027.

## Motivation and the 2026 timeline

In 2026, information about plantation fires reached prices in stages, and the big price move came 11 days after the evidence went public. That gap is the puzzle this project studies.

| Date (2026) | Stage | What happened |
| --- | --- | --- |
| Aug to Oct | Satellite | Hotspots visible in near real time on NASA FIRMS; Singapore sees its worst haze in over a decade ([ANN](https://asianews.network/?p=309080)) |
| 5 Oct | NGO report | Greenpeace links SGX-listed First Resources and Bumitama Agri to concessions with detected fires ([Dr Wealth](https://drwealth.com/?p=146214552)) |
| 13 to 15 Oct | Salience | Singapore 24-hour PSI hits the unhealthy range for 12 straight days, the longest run since 2015 ([ANN](https://asianews.network/?p=308529)) |
| 16 Oct | Government | PM Lawrence Wong says Singapore is looking into which firms are responsible; palm stocks fall ([Longbridge](https://longbridge.com/en/news/302043938)) |
| 16 Oct | Price | First Resources drops as much as 9.1% intraday, Golden Agri closes down 3.5%, Wilmar down 1.2% ([JournalArta](https://journalarta.com/en/2026/10/16/first-resources-haze-response-el-nino/), [The Star](https://www.thestar.com.my/business/business-news/2026/10/19/palm-oil-stocks-tumble-as-spore-probes-haze-links)) |

Why it matters: the literature on gradual information diffusion (Hong and Stein 1999) predicts exactly this kind of lag, but it is usually tested with proxies like analyst coverage. Here the underlying information is physically observable from space, timestamped daily, and publicly available, which makes the lag measurable directly.

Open question to answer first: did the 5 October report move prices at all? If it did, the story is partial underreaction. If it did not, the story is pure inattention until salience arrived.

## Research questions and hypotheses

The central question: does public, satellite-observable fire information reach palm oil stock prices immediately, or only when attention spikes?

| # | Question | Hypothesis | Rejected if |
| --- | --- | --- | --- |
| H1 | Does fire exposure predict returns? | Lagged in-concession hotspot counts predict negative abnormal returns over 1 to 10 days | No significant lagged coefficient after controlling for CPO price and market |
| H2 | Does salience gate the reaction? | The H1 effect is concentrated on high-PSI days in Singapore | Exposure × PSI interaction is zero or negative |
| H3 | Do NGO and government events add news or attention? | Abnormal returns cluster around attention events (reports, official statements) more than around hotspot spikes | Returns load on hotspots and not on event days |
| H4 | Does one market price it first? | SGX-listed group arms react before their IDX-listed siblings | Cross-market lead-lag is symmetric or reversed |
| H5 | Does the market discount the firms' defense? | Hotspots inside concessions matter more than hotspots in a buffer zone around them | Inside and buffer coefficients are equal |

H1 and H2 are the core. H3 to H5 are extensions to pursue only if the core results hold up.

## Data sources and construction

Everything in the core design is free and public. The hard part is not access, it is linking concessions to listed parents.

| Layer | Source | Granularity | Notes |
| --- | --- | --- | --- |
| Fire hotspots | NASA FIRMS (MODIS from 2000, VIIRS from 2012) | Point, daily | Free API key; filter by confidence level |
| Concession boundaries | Global Forest Watch oil palm concession maps | Polygon | Coverage and vintage vary by province; check against each firm's sustainability report |
| Concession to parent | Annual reports, sustainability reports, RSPO filings, own interlock map from the influence network repo | Firm | The highest-effort layer; record the confidence of each link |
| Stock prices | SGX and IDX daily prices (yfinance or IDX downloads) | Daily | Adjust for dividends; flag IDX auto-reject limit days |
| CPO price | Bursa Malaysia crude palm oil futures (FCPO) | Daily | Main fundamental control; source may need effort |
| Salience | Singapore NEA 24-hour PSI history (data.gov.sg) | Daily, by region | Confirm how far back the archive goes |
| Wind | ERA5 reanalysis (Copernicus) | Hourly, gridded | Only needed for the instrument in H2 |
| Attention | Google Trends, GDELT news counts, Reddit and X mentions | Daily | Secondary measures |
| Events | Greenpeace and NGO reports, Singapore government statements, company responses | Dated | Hand-coded event list |

**Sample universe (to confirm):** SGX-listed First Resources, Bumitama Agri, Golden Agri-Resources, Wilmar, Indofood Agri; IDX-listed Astra Agro Lestari, SMART (Sinar Mas Agro), London Sumatra, Salim Ivomas, Sawit Sumber Mas, Dharma Satya Nusantara. Expect roughly 15 to 20 names in total.

**Key constructed variable:** fire exposure for firm *i* on day *t* = hotspots inside *i*'s concessions, scaled by total concession area. A buffer version counts hotspots within a ring around each concession (start at 2 km, then test 5 km).

## Empirical design and identification

The design runs in three stages, from a one-plot sanity check to a panel regression with an instrument. Each stage is only worth doing if the previous one shows something.

**Stage 1: Pilot event study (2026 only).** Compute cumulative abnormal returns for the 5 SGX names around 5 October and 16 October, using a market model on the STI plus the CPO futures return, with a 120-day estimation window ending 30 days before the event. Output: one CAR plot with both events marked.

**Stage 2: Panel regression (all four haze seasons).** Daily abnormal return on lagged fire exposure, the exposure × PSI interaction, and controls:

```latex
AR_{i,t} = \alpha_i + \sum_{k=1}^{K} \beta_k \, Fire_{i,t-k} + \gamma \, (Fire_{i,t-1} \times HighPSI_{t}) + \delta \, HighPSI_t + \theta \, r^{CPO}_t + \lambda_{season} + \varepsilon_{i,t}
```

H1 is a test on the betas. H2 is a test on gamma. Cluster standard errors by date, because every firm shares the same haze day. With fewer than 20 firms, also report wild-cluster bootstrap p-values.

**Stage 3: Wind instrument for salience.** PSI in Singapore partly reflects total fire activity, which also drives fundamentals. To isolate salience, instrument HighPSI with the share of hours of southerly to southwesterly wind at Singapore from ERA5. The exclusion restriction: wind direction changes what Singaporean investors see, but not how many fires burn inside a given firm's concessions that day. That assumption needs to be argued explicitly, and is weaker in the long run because wind also spreads fires.

**Extensions.** For H4, a lead-lag regression on the SGX/IDX sibling pairs (Golden Agri and SMART; Indofood Agri and London Sumatra/Salim Ivomas). For H5, inside and buffer exposure entered side by side in the Stage 2 regression.

## Threats to validity and robustness checks

The biggest threat is that the 16 October drop was a rational reaction to new enforcement risk, not delayed absorption of old information. Every claim of slow diffusion has to survive that alternative.

| Threat | Why it matters | Check |
| --- | --- | --- |
| New news, not slow news | The PM's statement raised the probability of penalties under the Transboundary Haze Pollution Act | Show drift or non-reaction to hotspots and the 5 Oct report before 16 Oct; compare names named vs not named by Greenpeace |
| CPO price confound | El Niño lifts CPO prices, which helps the same stocks the fires hurt | CPO futures return as a control; re-run on CPO-hedged returns |
| Small sample | About 15 to 20 firms and one big event per season | Stack four seasons; wild-cluster bootstrap; report effect sizes, not just stars |
| Noisy exposure | Firms say fires spread from outside their boundaries | Inside vs buffer exposure (H5); vary FIRMS confidence filter |
| Concession mapping errors | Wrong parent links bias the signal toward zero | Report results using only high-confidence links |
| IDX price limits | Auto-reject limits mechanically create next-day continuation that mimics drift | Drop or flag limit-hit days for IDX names |
| Thin trading | Some IDX palm names trade rarely, so prices react late for mechanical reasons | Dimson betas; volume filter |
| Multiple testing | Many lags, buffers and PSI cutoffs | Pre-register the main spec in this doc before running Stage 2 |

A null result in Stage 2 is still publishable as a note: it would suggest the haze premium is driven by regulatory events rather than by slow processing of satellite information.

## Pipeline architecture and tech stack

Every source flows into one firm-day panel, so all three analysis stages run off the same dataset.

&#91;embedded content: data pipeline · 5 sources, 2 processing steps, 3 analysis stages\]

The spatial join is the only geospatial step. Everything downstream is ordinary tabular work.

**Stack:** Python, using geopandas and shapely for the spatial join, pandas for the panel, statsmodels and linearmodels for the regressions, and matplotlib for the figures. Use Python rather than R even though STAT 4220 uses R: quant firms expect Python fluency, and this project is how you show it. Keep the code in a new folder of the influence networks repo, or its own repo, with a README that reproduces the pilot plot in one command.

## Milestones and timeline

The plan puts a pilot result in hand by late November and a full panel result by 28 January, three days before the FTTP New York deadline.

&#91;embedded content: milestones · November 2026 to March 2027\]

The go/no-go on 29 November is the key gate. If the pilot shows no reaction to either event, rescope to the regulatory-event story before investing in the four-season panel. The wind instrument runs after the deadline, so it becomes a talking point if you are admitted. Dates assume finals take most of mid-December; adjust once your exam schedule is set.

## Positioning for FTTP and other pre-internship quant programs

This project helps, but it will not be what gets you into FTTP. First-year programs screen mostly on your resume and a short motivation, and later quant rounds test probability, mental math and market-making games. The project's job is to give you one sharp, numerate story to tell. Your informatics and economics olympiad results are likely a stronger screening signal than any first-year project.

**Programs open to you this cycle (verify each page before applying):**

| Program | Who | When | Apply by |
| --- | --- | --- | --- |
| [Jane Street FTTP, New York](https://www.janestreet.com/fttp-nyc-email.html) | First-year undergraduates, STEM-leaning | 21 to 25 March 2027 | 31 January 2027 |
| [Jane Street FTTP, London](https://quantvault.org/quant-early-insight-programs-2027.html) | First-year undergraduates | March to April 2027 | 3 January 2027 |
| [Jane Street Bridge](https://ep-advisory.com/?p=38454) | First- and second-years; Strategy and Product or Institutional Sales and Trading tracks | 1 to 3 April 2027 | 3 January 2027 |
| [SIG virtual intro to quant trading](https://quantvault.org/quant-early-insight-programs-2027.html) | High school, first- and second-year students | December 2026 and May 2027 | Check page |

**Programs to target next year** (most are aimed at sophomores, or at classes graduating before yours): Optiver FutureFocus, IMC Launchpad, Explore HRT, and Citadel Securities Discover. See the [Extern 2028 guide](https://www.extern.com/post/quant-internships-summer-2028-guide) and the [IMC Launchpad posting](https://www.imc.com/us/careers/jobs/4781344101). Strong performance at some of these can lead to an accelerated internship process.

**How to frame the project for quant firms.** Talk about signal, latency and edge, not sustainability. The quant version of the pitch: "I built an alternative-data signal from satellite fire detections and tested whether markets price it immediately or only once it becomes salient." Keep the impact and IVSB framing for the Wharton transfer application, where it fits better.

**Resume line template** (fill in the brackets only with real results):

- Built a Python pipeline linking \[N\] NASA satellite fire detections to \[N\] SGX/IDX palm oil firms' concessions; found fire exposure predicts \[X\] bp abnormal returns over \[K\] days, concentrated on high-haze days

**What else to do before 31 January:** daily probability and expected-value practice, a few rounds of market-making games with friends, and fluent Python with pandas. Those carry more weight in later rounds than the project does.

## Literature and references

**Core papers this project builds on**

- Hong and Stein (1999), gradual information diffusion model; Hong, Lim and Stein (2000), momentum stronger in low-analyst-coverage stocks ([summary](https://scite.ai/authors/harrison-hong-mOdjRr))
- Da, Gurun and Warachka, "Frog in the Pan": investors underreact to information that arrives continuously in small amounts ([summary](https://alphaarchitect.com/2015/11/frog-in-the-pan-identifying-the-highest-quality-momentum-stocks/))
- [Hirshleifer, Peng and Wang (RFS 2025)](https://www.nber.org/papers/w30860), news diffusion through social networks speeds price reactions but raises trading volume
- [Gradual information diffusion across commonly owned firms (JFE)](https://login.x-mol.com/paper/1784049572419194880), cross-firm return predictability through shared owners
- [Lopez-Lira and Tang](https://arxiv.org/abs/2304.07619v5), LLM-scored news predicts returns, consistent with delayed diffusion
- [Semenova and Winkler (Quantitative Finance 2025)](https://www.inet.ox.ac.uk/publications/social-contagion-and-asset-prices-reddits-self-organised-bull-runs), social contagion and price run-ups

**2026 haze sources**

- [Singapore's worst haze in more than a decade (ANN, 20 Oct 2026)](https://asianews.network/?p=309080)
- [12th consecutive day of unhealthy air; Greenpeace links Bumitama and First Resources (ANN, 16 Oct 2026)](https://asianews.network/?p=308529)
- [We Hate the Haze, and So Do Palm Oil Stocks (Dr Wealth, 22 Oct 2026)](https://drwealth.com/?p=146214552)
- [Palm oil stocks slide after Singapore looks into responsible firms (Longbridge)](https://longbridge.com/en/news/302043938)
- [First Resources haze response (JournalArta, 16 Oct 2026)](https://journalarta.com/en/2026/10/16/first-resources-haze-response-el-nino/)
- [Palm oil stocks tumble as S'pore probes haze links (The Star, 19 Oct 2026)](https://www.thestar.com.my/business/business-news/2026/10/19/palm-oil-stocks-tumble-as-spore-probes-haze-links)

**Methods**

- [A tutorial on Hawkes processes for events in social media (arXiv)](https://arxiv.org/pdf/1708.06401), for modeling attention cascades in an extension

Note: several of these links are search-result summaries rather than the papers themselves. Pull the original PDFs before citing them in a write-up.
