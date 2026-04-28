"""Live runner against findmyring-ber1a2bw.alfactf.ru. Up to N retries — each
retry starts a fresh game (new cookie jar)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

from solver import Probe, solve

BASE = "https://findmyring-ber1a2bw.alfactf.ru"
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class Game:
    def __init__(self, attempt_idx: int, log_path: Path) -> None:
        self.session = requests.Session()
        self.attempts_left: int | None = None
        self.total_attempts: int | None = None
        self.attempt_idx = attempt_idx
        self.log_fp = open(log_path, "w", buffering=1)
        self._log_event({"event": "session_start", "ts": time.time()})

    def _log_event(self, ev: dict) -> None:
        self.log_fp.write(json.dumps(ev, ensure_ascii=False) + "\n")

    def start(self) -> None:
        r = self.session.post(f"{BASE}/api/start", timeout=20)
        r.raise_for_status()
        d = r.json()
        self.total_attempts = d["total_attempts"]
        self.attempts_left = d["attempts_left"]
        self._log_event({"event": "start", "data": d})
        print(f"[game {self.attempt_idx}] start: {d}")

    def antenna(self, lat: float, lon: float, radius_m: float) -> tuple[bool, int | None]:
        body = {"lat": lat, "lon": lon, "radius": radius_m}
        for retry in range(3):
            try:
                r = self.session.post(
                    f"{BASE}/api/antenna",
                    json=body,
                    timeout=30,
                )
                if r.status_code != 200:
                    raise RuntimeError(f"antenna http {r.status_code}: {r.text[:200]}")
                d = r.json()
                self.attempts_left = d.get("attempts_left", self.attempts_left)
                self._log_event({"event": "antenna", "req": body, "resp": d})
                if d.get("flag"):
                    print(f"[game {self.attempt_idx}] FLAG via antenna: {d['flag']}")
                    raise FlagFound(d["flag"])
                return bool(d["found"]), d.get("attempts_left")
            except (requests.RequestException, ValueError) as e:
                self._log_event({"event": "antenna_error", "req": body, "error": str(e), "retry": retry})
                time.sleep(1.5 * (retry + 1))
        raise RuntimeError("antenna: 3 retries exhausted")

    def guess(self, lat: float, lon: float) -> tuple[bool, str | None]:
        body = {"lat": lat, "lon": lon}
        r = self.session.post(f"{BASE}/api/guess", json=body, timeout=20)
        if r.status_code != 200:
            raise RuntimeError(f"guess http {r.status_code}: {r.text[:200]}")
        d = r.json()
        self.attempts_left = d.get("attempts_left", self.attempts_left)
        self._log_event({"event": "guess", "req": body, "resp": d})
        flag = d.get("flag")
        return flag is not None, flag

    def close(self) -> None:
        self.log_fp.close()


class FlagFound(Exception):
    def __init__(self, flag: str) -> None:
        super().__init__(flag)
        self.flag = flag


def run_attempt(idx: int, seed: int) -> str | None:
    log_path = LOG_DIR / f"attempt_{idx:02d}_seed{seed}.jsonl"
    game = Game(attempt_idx=idx, log_path=log_path)
    try:
        game.start()
        # Wrap antenna() into oracle signature.
        def oracle(lat: float, lon: float, radius_m: float):
            return game.antenna(lat, lon, radius_m)

        g_lat, g_lon, probes = solve(
            oracle,
            initial_attempts=game.attempts_left or 46,
            seed=seed,
            log=lambda s: print(f"  {s}"),
        )
        print(f"[game {idx}] guessing at ({g_lat:.7f}, {g_lon:.7f})")
        ok, flag = game.guess(g_lat, g_lon)
        print(f"[game {idx}] guess result: ok={ok} flag={flag}")
        return flag
    except FlagFound as ff:
        return ff.flag
    finally:
        game.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-attempts", type=int, default=3, help="number of game retries")
    ap.add_argument("--seed-base", type=int, default=42)
    args = ap.parse_args()

    for i in range(args.max_attempts):
        seed = args.seed_base + i * 1000
        print(f"\n========== ATTEMPT {i+1}/{args.max_attempts} (seed={seed}) ==========\n")
        try:
            flag = run_attempt(i + 1, seed)
        except Exception as e:
            print(f"[game {i+1}] ERROR: {e}")
            continue
        if flag and flag.startswith("alfa{"):
            print(f"\n*** FLAG: {flag} ***\n")
            (LOG_DIR / "FLAG.txt").write_text(flag + "\n")
            return 0
        else:
            print(f"[game {i+1}] no flag — retrying with new session")
    print("\n--- all attempts exhausted, no flag ---")
    return 1


if __name__ == "__main__":
    sys.exit(main())
