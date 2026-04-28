"""Offline validator: pretend to be the server, run solver on N random rings."""
from __future__ import annotations

import argparse
import sys
import time

import numpy as np

from solver import solve
from sphere import EARTH_R, haversine_m, sample_uniform_sphere


def make_oracle(true_lat: float, true_lon: float):
    counter = {"n": 0}

    def oracle(lat: float, lon: float, radius_m: float):
        counter["n"] += 1
        d = float(haversine_m(lat, lon, np.array([true_lat]), np.array([true_lon]))[0])
        return d <= radius_m, None

    return oracle, counter


def trial(seed: int, attempts: int, log_fn):
    rng = np.random.default_rng(seed)
    tl, tn = sample_uniform_sphere(1, rng)
    true_lat, true_lon = float(tl[0]), float(tn[0])
    oracle, ctr = make_oracle(true_lat, true_lon)
    g_lat, g_lon, probes = solve(
        oracle,
        initial_attempts=attempts,
        seed=seed,
        log=log_fn,
    )
    err = float(haversine_m(true_lat, true_lon, np.array([g_lat]), np.array([g_lon]))[0])
    return {
        "seed": seed,
        "true": (true_lat, true_lon),
        "guess": (g_lat, g_lon),
        "err_m": err,
        "probes_used": ctr["n"],
        "ok": err <= 2.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20)
    ap.add_argument("--attempts", type=int, default=46)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    start = time.time()
    results = []
    for s in range(args.trials):
        log_fn = print if args.verbose else (lambda *_: None)
        r = trial(seed=1000 + s, attempts=args.attempts, log_fn=log_fn)
        results.append(r)
        flag = "OK " if r["ok"] else "FAIL"
        print(
            f"[{flag}] seed={r['seed']} err={r['err_m']:.3f}m probes={r['probes_used']} "
            f"true=({r['true'][0]:.4f},{r['true'][1]:.4f})"
        )

    ok = sum(1 for r in results if r["ok"])
    avg = sum(r["err_m"] for r in results) / len(results)
    avg_p = sum(r["probes_used"] for r in results) / len(results)
    print()
    print(f"--- {ok}/{len(results)} succeeded; avg_err={avg:.3f}m; avg_probes={avg_p:.1f}; "
          f"time={time.time()-start:.1f}s ---")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
