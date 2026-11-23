# Interview sheet: haze-salience

For the owner. Plain-language answers to the questions an interviewer is likely to ask, written
on 23 Nov 2026 from the code and outputs as they stand. Numbers come from
`outputs/figures/pilot_report.md` (run of 20 Nov 2026). This page contains pilot return figures:
do not pass it to a session that is meant to stay blind to them.

## 1. Why is PSI a usable attention shock, and what would break that?

**The argument.** Singapore's PSI measures the smoke that reaches Singapore. Whether smoke
reaches Singapore on a given day depends on wind direction as much as on how much is burning. So
on two days with the same fires inside a firm's concessions, PSI can be low or high. PSI changes
what investors in Singapore see and breathe; it does not change what that one firm's land is
doing. If returns respond to a firm's own fires mainly on high-PSI days, the information was
there all along and attention is what moved.

**What would break it.**
- PSI also rises when total burning rises. Total burning is a fundamental: it raises the odds of
  fines, permit action and supply loss for the whole sector. Then PSI is partly news, not only
  attention.
- A high PSI can itself trigger government action in Singapore. That makes a high-PSI day a
  regulatory-risk day.
- El Niño drives fires, PSI and palm oil prices together.
- The investors who set prices for the Jakarta-listed names may not be in Singapore.
- The design's answer is Stage 3: use wind direction as an instrument for high PSI. That is not
  built. Even then, wind also spreads fires, so the instrument is arguable, not clean.

## 2. What is the market model here, and why is a palm oil price in it?

For each firm: regress its daily return on the Straits Times Index return and a vegetable-oil
price return, over 120 trading days ending 30 days before the event. The fitted line is the
"normal" return. The abnormal return is the actual return minus what the line predicts. Summing
abnormal returns over days gives the cumulative abnormal return (CAR).

**Why the oil price.** These firms sell palm oil, so their shares follow its price. Haze seasons
come with dry weather that cuts supply and moves that price. Without the control, a share move
caused by the commodity would be counted as a reaction to the event.

**What was actually used.** The design calls for Bursa palm oil futures (FCPO). The one real run
used CBOT soybean oil as a stand-in, with its previous day added as a second term because Chicago
closes after Singapore. Not the plantation share index: the haze shock moves that index too, so
controlling for it would remove the effect being measured.

## 3. What does the placebo p-value measure that an ordinary p-value does not?

An ordinary p-value assumes the abnormal returns follow a normal distribution. Daily returns of
small, thinly traded shares do not. The placebo p-value asks a direct question instead: in this
firm's own 120 estimation days, what share of same-length windows had a return at least as
negative as the event window? No distribution is assumed.

**Its limits, which you should say first.** With 120 days the smallest possible value is about
0.008. It slightly overstates significance, because an event-day return also carries the error
of the estimated line. It does not fix the fact that all five firms share one event date; the
portfolio rows do that, by treating the five as one series.

## 4. What did the pilot show?

**Sample.** Five SGX names, two event dates (5 Oct 2026, an NGO report naming two of the firms;
16 Oct 2026, a government statement). One run. Soybean-oil stand-in control. Both event dates
are still unverified, and the tickers are still marked unchecked.

**The statistic fixed in advance** (the planning rule in `docs/PROJECT_GUIDE.md`): the portfolio
abnormal return over days 0 and +1, with its placebo p-value.

| Event | Named firms (2) | All firms (5) |
| --- | --- | --- |
| 5 Oct | +0.56%, p = 0.61 | +0.73%, p = 0.66 |
| 16 Oct | -2.92%, p = 0.22 | -2.55%, p = 0.12 |

**Other numbers in the report.**
- Day 0 alone on 16 Oct: named firms -6.34% (p = 0.025), all firms -3.19% (p = 0.033), named
  minus not named -5.24% (p = 0.041). Part of the day-0 fall in the named firms reversed on day +1.
- The ten days before 5 Oct: named firms -26.18% cumulative, all firms -13.96%. The band around
  a ten-day sum is wide, but this is the largest number in the report and it comes before the
  first dated event.
- Abnormal volume on the event days was within about two standard deviations for every firm.

**How to say it honestly.** "On the statistic I fixed beforehand, neither date shows a reaction
I can tell from noise with five firms. Day 0 of the second date, taken alone, was unusually
negative for the named firms, but I chose the two-day window first, so I report day 0 as
description. The named firms had already fallen sharply before the first date I had coded,
which tells me my event dates or my story about when the news arrived need checking."

**Limits.** Five firms, one cluster of dates, one run. Stand-in control; the FCPO run replaces
it, and FCPO has its own flaw (contract-roll days are ignored). Several statistics were looked
at, so one small p-value among them is weaker than it looks.

**Open decision, yours.** The go/no-go table reads a "reaction" as that two-day portfolio return
being negative with p below 0.10. Read literally against the table above, neither date
qualifies. Switching the rule to day 0 now would be a choice made after seeing the data. Either
is defensible if you say which you did and when.

## 5. What would change your mind once Stage 2 runs?

**Towards slow diffusion.** The summed effect of ten lags of a firm's own fire exposure is
negative (H1), the effect is stronger on high-PSI days (H2), both survive few-cluster inference,
and fires inside the concession matter more than fires in a ring just outside it.

**Away from it.**
- H1 is null with a tight interval: the market either prices fires at once or does not care.
- High PSI moves all palm oil names equally, whatever their own fires: a sector haze shock, not
  firm-level information.
- Inside and buffer exposure have the same effect: the signal is regional burning.
- The result depends on one season, one firm, or on low-confidence concession links.

**Before any of that.** Stage 2 does not exist yet as code or data: no fire loader, no concession
join, no parent table, no regression. The pre-registration is a draft with six open decisions.

## Two things to fix before an interviewer finds them

- **H2's sign.** `docs/design.md` says H2 is rejected if the interaction is "zero or negative".
  `docs/preregistration.md` tests it one-sided below zero. If fire exposure lowers returns, a
  stronger effect on high-PSI days is a negative interaction, so the pre-registration looks
  right and the design table looks wrong. Both files are yours to edit.
- **The opening story.** The README says the big move came on 16 October. The pilot's largest
  cumulative number is in the ten days before 5 October. Check the dates before repeating the
  story.
