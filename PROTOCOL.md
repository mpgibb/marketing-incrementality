# Synthetic campaign study protocol

Specified before the first evaluation run. No seed selection based on favorable results.

Decision: repeat a fixed reactivation campaign for the same eligible customer population only if the evidence and contribution economics justify a further controlled rollout. This simulation is not a recommendation for an actual business.

Unit: individual eligible customer, with 28-day pre-period net contribution available. Two equally weighted synthetic segments represent lower and higher historical engagement. Within each segment, assign exactly half to campaign and half to holdout. Outcomes are 28-day net contribution in USD, before campaign contact/incentive cost. Values may be negative (e.g. returns or service costs). Assignment, not message opening or conversion, defines treatment.

Estimand: finite-sample intention-to-treat average effect of campaign assignment on net contribution across all 6,000 eligible customers. This includes nonresponse in the modeled assignment effect. The simulation imposes no interference, no missing outcomes, fixed follow-up, and an unchanged outcome definition.

Data process: segment s is 0 or 1; pre-period contribution X ~ Gamma(shape=4, scale=25+10s). Untreated outcome Y(0)=20+0.6X+25s+noise, with noise SD 30+10s. Assignment effect Y(1)-Y(0)=6+4s, so the equally weighted sample-average truth is $8. Base noise is normal and independent across customers. This is invented data with no client records, external dataset, or observed business effect.

Baseline: stratum-size-weighted difference in means. Method: subtract theta_s times pre-period contribution within each stratum, then apply the same randomized estimator (CUPED-style adjustment). Estimate theta_s from a separate, independently generated historical cohort with no campaign. Freeze it before examining experimental outcomes. No post-treatment covariates, data-driven segment selection or model search.

Uncertainty: sum stratum weights squared times (sample variance in each arm divided by arm size); use a normal 95% interval. This is the stratified Neyman variance estimator. With effect constant within strata in this DGP it targets design variance; with individual effect heterogeneity it is generally conservative. Large-sample intervals are not exact small-sample guarantees. No stopping rule or repeated peeking.

Primary evaluation: report both estimates, standard errors and intervals, realized interval-width reduction, known truth, arm counts, pre-period balance and pre-period placebo interval. Monte Carlo at 2,000 customers with 400 repetitions per fixed scenario reports bias, RMSE, mean estimated SE, empirical SD, 95% coverage and rejection of zero; report Monte Carlo error of coverage. Do not interpret power as a client result.

Robustness: (1) base process; (2) sharp null with zero effect; (3) weak contemporary covariate relationship (coefficient 0.1) while historical adjustment still uses 0.6; (4) centered, standardized lognormal noise instead of normal, retaining the same marginal noise SD. The weak-covariate scenario tests loss of transportability and may worsen precision. These checks do not validate interference, missingness or observational confounding assumptions.

Economics: subtract a hypothetical $6 cost per assigned customer from the effect and its interval. Explore $0–$12 solely as accounting sensitivity for the SAME fixed campaign. An increase in incentive or contact intensity can change the treatment effect; this study estimates no dose-response curve and supports no budget optimizer, arbitrary spending levels or extrapolation to new customers. Future acquisition experiments and competing campaigns need their own assignment design and response evidence.

Review status: Automated tests and a synthetic evaluation are complete only after their recorded runs. Michael's independent technical review remains pending.

Method reference: Deng, Xu, Kohavi & Walker (2013), “Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data.” https://ai.stanford.edu/~ronnyk/2013-02CUPEDImprovingSensitivityOfControlledExperiments.pdf . This implementation freezes separate historical slopes rather than fitting pooled slopes from the experiment.
