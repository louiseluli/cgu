# EDA — invisibility index pipeline

## 1. Source data quality (`municipality_sex_race_summary.csv`)

- Rows: 8,629
- Duplicate (year, municipality, sex, race) keys: 0
- Nulls in mean_wage/worker_count: 0
- Non-positive mean_wage rows: 0
- Non-positive worker_count rows: 0
- Years present: [np.int64(2010), np.int64(2011), np.int64(2012), np.int64(2013), np.int64(2014), np.int64(2015), np.int64(2016), np.int64(2018), np.int64(2021), np.int64(2022), np.int64(2023), np.int64(2024)]
  (2006-2008, 2017, 2019, 2020 excluded upstream — `BLOCKED_YEARS` in wage_gap's `build_dataset.py`, a pre-existing documented decision, not introduced by this pipeline.)
- Municipalities per year: min=92, max=92 (RJ has 92 municipalities total — years below that are missing coverage, not necessarily an error, since a municipality can simply have zero workers in a given sex×race cell in a given year).

## 2. Worker-count-per-cell distribution (justifies MIN_CELL_COUNT)

Black-women cell worker_count, all municipality-years (n=1104):
  - p5: 17
  - p10: 29
  - p25: 93
  - p50: 254
  - p75: 883
  - p90: 3028
  - share below 100 workers: 25.8%
  - share below 30 workers: 10.1%

MIN_CELL_COUNT=100 in build_invisibility_index.py excludes the bottom 26% of municipality-years by black-women worker count — this is the noisy tail where invisibility_pct swings to ±150-350% on cells as small as N=52 (see §3).

## 3. Effect of the N-filter on invisibility_pct (why it's necessary)

Latest year (2024), invisibility_pct across municipalities:
  - Unfiltered (n=92): std=56.0, min=-355.0, max=212.1
  - Filtered N>=100 (n=81): std=52.7, min=-355.0, max=154.2

Most unfiltered extremes are driven by small N combined with a small denominator — confirmed by manual lookup: the unfiltered top-ranked municipality (Cardoso Moreira, +212%) has only 58 black-women workers. Filtering to N>=100 removes most of this and stabilizes std from noisy to ~53 points.

### 3.1 A second, distinct failure mode survives the N-filter
The filtered minimum is still an extreme -355% (Maricá, 2024). This is *not* a small-N artifact — Maricá has 2,004 black-women workers, well above the threshold. It happens because invisibility_pct divides by actual_gap, and Maricá's actual gap is only R$29 (white men and Black women are at near pay parity there specifically), so dividing a modest R$102 invisibility_index by a R$29 denominator produces a huge percentage even though both numbers are individually well-sampled and real. **Consequence: invisibility_pct is not a safe ranking key on its own, even after N-filtering** — this is why build_invisibility_index.py ranks municipalities by invisibility_index in R$ terms for the narrative's top-10 lists, and reports p5/p95 rather than raw min/max as the headline heterogeneity spread.

## 4. Sensitivity check: sex-only gap definition

The pipeline computes sex_only_gap over **all four race categories** (black, pardo, white, yellow), while race_only_gap is restricted to **black/white only**. This is a deliberate, defensible choice (sex-only should reflect 'what if we only knew someone's sex', i.e. the whole population) but it's an asymmetry worth stress-testing: does restricting sex_only_gap to black/white workers only change the conclusion?

      sex_only_gap_all_races  sex_only_gap_black_white_only   diff  diff_pct_of_gap
year                                                                               
2010                   424.0                          446.1  -22.1             -5.2
2011                   468.7                          490.7  -22.0             -4.7
2012                   546.2                          568.1  -21.9             -4.0
2013                   637.9                          657.5  -19.7             -3.1
2014                   692.6                          722.8  -30.1             -4.4
2015                   706.2                          743.1  -36.9             -5.2
2016                   725.6                          774.4  -48.8             -6.7
2018                   726.5                          803.9  -77.4            -10.6
2021                   759.6                          843.7  -84.1            -11.1
2022                  1206.8                         1325.6 -118.7             -9.8
2023                   831.2                          844.5  -13.4             -1.6
2024                   813.4                          831.0  -17.6             -2.2

Max divergence: 11.1% of the sex-only gap. This is small enough not to change the direction or rough magnitude of the invisibility index reported in the narrative.

## 5. Robustness check: is this specific to Black women, or generic to any woman-of-color category?

The invisibility index so far compares white men to Black women only. If the same naive-additive-vs-actual gap showed up for *any* non-white women's category, the 'hidden compounding' story would be a generic artifact of the arithmetic rather than a real feature of the Black-women comparison specifically. Re-running the identical computation with pardo and yellow women in place of Black women tests that directly.

               comparison  n_women_statewide_2024  invisibility_pct_2024  invisibility_pct_mean_all_years
 white men vs black women                  309905                   -3.3                             -2.3
 white men vs pardo women                 1007927                    7.4                              4.6
white men vs yellow women                   23499                    9.0                             13.1

Honest read: all three statewide invisibility percentages sit in the same single-to-low-double-digit range (-3.3% to +13.1%) — this is *not* a clean 'only Black women show it' result, and the narrative should not claim it is. What it does rule out is the arithmetic being a pure artifact that would blow up for any category regardless of N: the largest deviation (yellow women, 13.1% multi-year mean) belongs to the smallest, most volatile subgroup (statewide N=23,499 vs 310k for black, 1.0M for pardo), consistent with sampling noise rather than a distinct effect. The municipality-level heterogeneity finding in §3 (p5/p95 of -39% to +40% for the black-women comparison specifically) remains the strongest, best-supported claim in this analysis — it is not undermined by this check, but this check does mean the narrative should frame the state-level black-women number as 'small and inconclusive on its own', not as evidence the effect is uniquely absent for Black women.

## 6. Approximate statewide confidence interval

Every number so far is a point estimate — no uncertainty is reported. True confidence intervals need per-cell wage variance, which only exists **statewide** (via the `inequality/` percentile tables), not per municipality — so this section covers the statewide invisibility index only; municipality-level numbers cannot get a rigorous CI from the outputs available today (see §7 recommendations).

Sigma approximated from the IQR (`(p75-p25)/1.349`, the normal-distribution relationship) since no raw standard deviation is published. RAIS wages are heavily right-skewed (max values run 50-100x the median — see §1), so **this understates true sigma and therefore understates the interval width; treat it as a lower bound on uncertainty, not an exact interval.** By the Central Limit Theorem the *mean's* sampling distribution is still approximately normal at these sample sizes (hundreds of thousands), which is what justifies a normal-approximation SEM despite the skewed individual-wage distribution.

sex_label   count    mean  sigma_approx  sem
   female 2480105 3499.52       1460.97 0.93
     male 3295755 4312.89       1690.52 0.93

Sex-only gap SEM (error propagation, independent samples): 1.31 -> approx 95% CI half-width ±2.58 on a gap of R$813. Even this conservative lower-bound interval is tiny relative to the gap itself, which is expected given the sample sizes involved — the state-level **point estimate** (sex-only + race-only gaps, and their sum) is not noise. What remains genuinely uncertain is not 'is there a gap' but 'how much of the R$2,622 actual gap in 2024 is missed by naive addition' (-3.3%, i.e. close to zero either way) — that number's practical conclusion (roughly additive at the state level) does not hinge on the precision of this approximation.