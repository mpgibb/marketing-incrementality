# Marketing effectiveness and incrementality

An evaluated **synthetic** randomized campaign study for Michael P. Gibb's commercial analytics portfolio. No client data or actual marketing impact is claimed.

## Business decision

Should a fixed customer-reactivation campaign receive a further controlled rollout to the same eligible population, given its incremental 28-day contribution and cost? The estimand is the finite-sample intention-to-treat average assignment effect across 6,000 eligible existing customers.

## Practical implication

At a hypothetical $6 cost per assigned customer, the adjusted estimate implies $2.16 net contribution, with a 95% interval of $0.36–$3.95. This is a synthetic decision example. Cost sensitivity holds campaign intensity fixed; it is not a spending-response model or a budget-allocation recommendation.

## Evidence

| Estimator | Effect / customer | 95% interval |
| --- | --- | --- |
| Unadjusted stratified baseline | $8.07 | $5.51–$10.63 |
| Frozen historical pre-period adjustment | $8.16 | $6.36–$9.95 |

Known average synthetic effect: **$8.00**. The adjusted interval is **29.8% narrower** in this primary experiment.

The simulation uses 400 repetitions of 2,000 customers per scenario. Base adjusted coverage is 94.5% (Monte Carlo SE 1.14 percentage points); zero-effect rejection is 5.5%. When the historical relationship weakens, adjusted RMSE worsens to $2.20 versus $1.65 for the baseline. Skewed-outcome adjusted coverage is 95.5%. Full results include bias, RMSE, empirical SD, mean estimated SE, coverage and rejection rates. These selected diagnostics do not establish validity for real campaigns.

Pre-period placebo: −$0.14, 95% interval −$3.20 to $2.92. Exact arm balance is enforced by design: 1,500 per arm per segment. Passing diagnostics does not prove no interference or missingness.

## Reproduce

Use Python **3.11.16**, uv and the frozen dependency-free lockfile:

```sh
uv sync --frozen
uv run python -m unittest discover -s tests -v
uv run python study.py
git diff --exit-code -- data results
```

A plain Python 3.11.16 installation also works: `python -m unittest discover -s tests -v` and `python study.py`. Everything uses the standard library. CI runs correctness tests and reproduces committed data/results. There is no paid dataset, API or network dependency during the pipeline.

Data version: `synthetic-campaign-v1`. Experiment seed 20260928; historical seed 20260927; simulation seeds 41000–41399, reused across scenarios for controlled comparisons. Source inputs, data hashes and full configuration are in `results/summary.json`. This repository contains a current-source snapshot of the protocol, implementation and evaluation; earlier commit history is not retained. Monetary draws are rounded to six decimal places for stable CSVs.

## Data and methodology

[PROTOCOL.md](PROTOCOL.md) specifies the data process, assignment, estimand, uncertainty and robustness scenarios. CSVs contain no real people or proprietary data:

- `data/experiment.csv`: observed assignment, pre-period contribution and outcome; no oracle columns.
- `data/historical.csv`: independent pre-period/outcome pairs used to fit frozen adjustment slopes.
- `data/ground_truth.csv`: potential untreated outcomes and assignment effects, for evaluation only.

The stratified difference estimator uses sample-share weights and Neyman variance. Adjustment subtracts segment-specific historical slopes times pre-period contribution. It does not fit to experimental outcomes or use post-treatment information. Large-sample normal intervals are approximate; with individual effect heterogeneity the variance can be conservative.

The synthetic process and data are original study materials. No third-party data license is needed. No source/data reuse license has been selected; public availability permits inspection but does not by itself grant reuse rights. The original CUPED paper is linked in the protocol.

## Limitations and review status

No actual client impact, observed acquisition effect, long-term value estimate, multi-channel budget optimizer or live API is established. These results do not generalize automatically to new customers, different campaigns, spend levels or changed operations. Historical transportability is not guaranteed by randomization.

Seven correctness tests and the recorded synthetic evaluation are complete; Michael's independent technical review remains pending.

Interactive case study: https://michaelpgibb.com/projects/marketing-incrementality
