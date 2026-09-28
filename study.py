"""Standard-library-only, reproducible synthetic randomized campaign study."""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics as st
import sys

ROOT = Path(__file__).resolve().parent


def generate(n: int, seed: int, scenario: str = "base") -> list[dict]:
    if n < 8 or n % 4:
        raise ValueError("Sample size must be a multiple of 4, at least 8")
    if scenario not in {"base", "null", "weak_covariate", "skewed_noise"}:
        raise ValueError("Unknown scenario")
    rng = random.Random(seed)
    rows = []
    for segment in (0, 1):
        assignment = [0] * (n // 4) + [1] * (n // 4)
        rng.shuffle(assignment)
        for treatment in assignment:
            pre = round(rng.gammavariate(4, 25 + 10 * segment), 6)
            noise = rng.gauss(0, 1)
            if scenario == "skewed_noise":
                noise = (math.exp(noise) - math.exp(0.5)) / math.sqrt(math.e * (math.e - 1))
            coefficient = 0.1 if scenario == "weak_covariate" else 0.6
            untreated = round(20 + coefficient * pre + 25 * segment + (30 + 10 * segment) * noise, 6)
            effect = 0.0 if scenario == "null" else 6.0 + 4.0 * segment
            rows.append({"customer_id": len(rows) + 1, "segment": segment,
                         "assigned": treatment, "pre_contribution": pre,
                         "outcome": untreated + treatment * effect,
                         "truth_y0": untreated, "truth_effect": effect})
    return rows


def fit_historical_slopes(rows: list[dict]) -> dict[int, float]:
    """Use only separate historical untreated outcomes; never experimental truth."""
    result = {}
    for segment in (0, 1):
        group = [r for r in rows if r["segment"] == segment]
        x = [r["pre_contribution"] for r in group]
        y = [r["truth_y0"] for r in group]
        mx, my = st.mean(x), st.mean(y)
        result[segment] = sum((a-mx)*(b-my) for a,b in zip(x,y)) / sum((a-mx)**2 for a in x)
    return result


def estimate(rows: list[dict], slopes: dict[int, float] | None = None,
             outcome: str = "outcome", z: float = 1.959963984540054) -> dict:
    """Stratified randomized difference, with frozen pre-treatment adjustment."""
    effect, variance = 0.0, 0.0
    for segment in (0, 1):
        group = [r for r in rows if r["segment"] == segment]
        weight = len(group) / len(rows)
        arms = [[r[outcome] - (slopes or {}).get(segment, 0) * r["pre_contribution"]
                 for r in group if r["assigned"] == arm] for arm in (0, 1)]
        if min(map(len, arms)) < 2:
            raise ValueError("At least two observations per arm and stratum required")
        effect += weight * (st.mean(arms[1]) - st.mean(arms[0]))
        variance += weight**2 * sum(st.variance(a) / len(a) for a in arms)
    se = math.sqrt(variance)
    return {"estimate": effect, "se": se, "ci_low": effect-z*se, "ci_high": effect+z*se}


def monte_carlo(config: dict, slopes: dict[int, float]) -> dict:
    output = {}
    for scenario in config["scenarios"]:
        draws = {"unadjusted": [], "adjusted": []}
        for i in range(config["simulation_repetitions"]):
            rows = generate(config["simulation_customers"], config["simulation_seed"] + i, scenario)
            truth = st.mean(r["truth_effect"] for r in rows)
            for method, theta in (("unadjusted", None), ("adjusted", slopes)):
                result = estimate(rows, theta, z=config["confidence_z"])
                draws[method].append({**result, "error": result["estimate"] - truth,
                                      "covers": result["ci_low"] <= truth <= result["ci_high"],
                                      "rejects_zero": result["ci_low"] > 0 or result["ci_high"] < 0})
        output[scenario] = {}
        for method, runs in draws.items():
            coverage = st.mean(r["covers"] for r in runs)
            output[scenario][method] = {
                "bias": st.mean(r["error"] for r in runs),
                "rmse": math.sqrt(st.mean(r["error"]**2 for r in runs)),
                "empirical_sd": st.stdev(r["estimate"] for r in runs),
                "mean_se": st.mean(r["se"] for r in runs),
                "coverage": coverage,
                "coverage_mcse": math.sqrt(coverage*(1-coverage)/len(runs)),
                "rejection_rate": st.mean(r["rejects_zero"] for r in runs)}
    return output


def write_csv(path: Path, rows: list[dict]) -> str:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> None:
    config = json.loads((ROOT / "config.json").read_text())
    historical = generate(config["historical_customers"], config["historical_seed"])
    slopes = fit_historical_slopes(historical)
    rows = generate(config["customers"], config["seed"])
    # Analysis reads only observed outcome and pre-period covariates. Potential
    # outcomes in the evaluation file are an oracle used for validation only.
    observed = [{k: v for k, v in r.items() if not k.startswith("truth_")} for r in rows]
    (ROOT / "data").mkdir(exist_ok=True)
    hashes = {
        "data/experiment.csv": write_csv(ROOT / "data/experiment.csv", observed),
        "data/ground_truth.csv": write_csv(ROOT / "data/ground_truth.csv", [{k: r[k] for k in ("customer_id", "truth_y0", "truth_effect")} for r in rows]),
        "data/historical.csv": write_csv(ROOT / "data/historical.csv", [{"customer_id": r["customer_id"], "segment": r["segment"], "pre_contribution": r["pre_contribution"], "outcome": r["truth_y0"]} for r in historical])}
    estimates = {name: estimate(observed, theta, z=config["confidence_z"])
                 for name, theta in (("unadjusted", None), ("adjusted", slopes))}
    result = {"synthetic": True, "config": config, "python": sys.version.split()[0],
              "historical_slopes": slopes, "data_sha256": hashes,
              "source_sha256": {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ["study.py", "config.json", "PROTOCOL.md", "pyproject.toml", "uv.lock"]},
              "truth": st.mean(r["truth_effect"] for r in rows), "estimates": estimates,
              "interval_width_reduction": 1 - estimates["adjusted"]["se"] / estimates["unadjusted"]["se"],
              "placebo_pre_period": estimate(observed, outcome="pre_contribution"),
              "counts": [{"segment": s, "control": sum(r["segment"]==s and r["assigned"]==0 for r in rows), "treatment": sum(r["segment"]==s and r["assigned"]==1 for r in rows)} for s in (0,1)],
              "monte_carlo": monte_carlo(config, slopes)}
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/summary.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ["truth", "estimates", "interval_width_reduction", "placebo_pre_period", "monte_carlo"]}, indent=2))


if __name__ == "__main__":
    run()
