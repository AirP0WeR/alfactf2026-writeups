"""Information-optimal Monte-Carlo binary search on the sphere."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np

from sphere import (
    cluster_diameter_m,
    haversine_m,
    sample_uniform_sphere,
    spherical_centroid,
)


@dataclass
class Probe:
    lat: float
    lon: float
    radius_m: float
    found: bool


# Oracle takes (lat, lon, radius_m) and returns (found: bool, attempts_left: int|None).
Oracle = Callable[[float, float, float], tuple[bool, int | None]]


def _apply_constraint(lat: np.ndarray, lon: np.ndarray, p: Probe) -> np.ndarray:
    d = haversine_m(p.lat, p.lon, lat, lon)
    return d <= p.radius_m if p.found else d > p.radius_m


def _resample(
    constraints: Iterable[Probe],
    target: int,
    rng: np.random.Generator,
    bbox_center_lat: float,
    bbox_center_lon: float,
    bbox_radius_m: float,
    *,
    max_batches: int = 60,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate ~target points satisfying every probe constraint.

    Strategy: rejection sampling around current centroid with progressively
    tighter proposal cap. The cap is parameterised by `bbox_radius_m`; we
    sample uniformly inside that cap and keep points satisfying all probes.
    """
    constraints = list(constraints)
    kept_lat: list[np.ndarray] = []
    kept_lon: list[np.ndarray] = []
    kept = 0

    # Sample uniformly inside a cap of given angular radius around (clat, clon).
    # Use the formula: pick cos(theta) uniform in [cos(alpha), 1], phi uniform [0, 2π].
    # Then rotate from north pole to (clat, clon).
    alpha = bbox_radius_m / 6_371_000.0  # angular radius (radians)
    cos_alpha = float(np.cos(alpha))

    # Rotation: from north pole frame → (clat, clon)
    clat = np.deg2rad(bbox_center_lat)
    clon = np.deg2rad(bbox_center_lon)
    # Build rotation matrix that maps (0,0,1) → centre vector.
    cv = np.array(
        [np.cos(clat) * np.cos(clon), np.cos(clat) * np.sin(clon), np.sin(clat)]
    )
    # Pick any axis perpendicular to z-axis and cv to rotate around.
    # Use Rodrigues with axis = z × cv normalised.
    z = np.array([0.0, 0.0, 1.0])
    axis = np.cross(z, cv)
    axis_norm = np.linalg.norm(axis)
    if axis_norm < 1e-12:
        # Already at pole; identity (or flip).
        R = np.eye(3) if cv[2] > 0 else np.diag([1.0, -1.0, -1.0])
    else:
        axis /= axis_norm
        cos_t = cv[2]  # dot(z, cv)
        sin_t = axis_norm
        K = np.array(
            [
                [0, -axis[2], axis[1]],
                [axis[2], 0, -axis[0]],
                [-axis[1], axis[0], 0],
            ]
        )
        R = np.eye(3) + sin_t * K + (1.0 - cos_t) * (K @ K)

    batch_size = max(target * 4, 4096)
    for _ in range(max_batches):
        if kept >= target:
            break
        # Cap-uniform sampling
        u = rng.random(batch_size)
        cos_theta = cos_alpha + (1.0 - cos_alpha) * u
        sin_theta = np.sqrt(np.clip(1.0 - cos_theta * cos_theta, 0.0, 1.0))
        phi = rng.random(batch_size) * (2.0 * np.pi)
        local = np.stack(
            [sin_theta * np.cos(phi), sin_theta * np.sin(phi), cos_theta], axis=-1
        )
        world = local @ R.T  # rotate
        lat = np.rad2deg(np.arcsin(np.clip(world[:, 2], -1.0, 1.0)))
        lon = np.rad2deg(np.arctan2(world[:, 1], world[:, 0]))
        mask = np.ones(batch_size, dtype=bool)
        for p in constraints:
            mask &= _apply_constraint(lat, lon, p)
        if mask.any():
            kept_lat.append(lat[mask])
            kept_lon.append(lon[mask])
            kept += int(mask.sum())

    if kept == 0:
        # Fallback: keep current centre alone — caller should treat as collapse.
        return np.array([bbox_center_lat]), np.array([bbox_center_lon])
    return np.concatenate(kept_lat)[:target], np.concatenate(kept_lon)[:target]


def _pick_probe_centre(
    lat: np.ndarray,
    lon: np.ndarray,
    rng: np.random.Generator,
    *,
    trials: int = 12,
) -> tuple[float, float, float]:
    """Pick (lat, lon, r) that minimises max post-split cluster diameter.

    Tries several random candidate-points as probe centres, computes median
    distance r, splits, and scores by max(diameter_inside, diameter_outside).
    Picks the lowest score. For uniform clouds the choice is roughly equivalent
    to a random candidate, but for elongated/annular clouds it favours probes
    that cut perpendicular to the long axis.
    """
    n = len(lat)
    if n == 1:
        return float(lat[0]), float(lon[0]), 1.0

    # Limit candidate count for speed when n huge.
    sample_idx = rng.integers(0, n, min(trials, n))
    best_score = float("inf")
    best = None
    for idx in sample_idx:
        c_lat = float(lat[idx])
        c_lon = float(lon[idx])
        d = haversine_m(c_lat, c_lon, lat, lon)
        r = float(np.median(d))
        if r < 1e-3:
            continue
        inside = d <= r
        if inside.sum() < 2 or (~inside).sum() < 2:
            continue
        # Approx diameter = 2 × max distance from sub-cluster centroid.
        di_lat = lat[inside]
        di_lon = lon[inside]
        do_lat = lat[~inside]
        do_lon = lon[~inside]
        # Cheap diameter proxies: take centroid then 2 * max dist.
        ci_lat, ci_lon = spherical_centroid(di_lat, di_lon)
        co_lat, co_lon = spherical_centroid(do_lat, do_lon)
        diam_in = 2.0 * float(haversine_m(ci_lat, ci_lon, di_lat, di_lon).max())
        diam_out = 2.0 * float(haversine_m(co_lat, co_lon, do_lat, do_lon).max())
        score = max(diam_in, diam_out)
        if score < best_score:
            best_score = score
            best = (c_lat, c_lon, max(1.0, min(r, 20_037_500.0)))
    if best is None:
        # Fallback to random candidate.
        idx = int(rng.integers(0, n))
        c_lat = float(lat[idx])
        c_lon = float(lon[idx])
        d = haversine_m(c_lat, c_lon, lat, lon)
        r = max(1.0, min(float(np.median(d)), 20_037_500.0))
        return c_lat, c_lon, r
    return best


def solve(
    oracle: Oracle,
    *,
    initial_attempts: int = 46,
    initial_n: int = 1_000_000,
    resample_floor: int = 20_000,
    target_diameter_m: float = 2.0,
    seed: int = 1337,
    log: Callable[[str], None] = print,
) -> tuple[float, float, list[Probe]]:
    """Run binary-search localisation. Returns (final_lat, final_lon, probes_log)."""
    rng = np.random.default_rng(seed)
    lat, lon = sample_uniform_sphere(initial_n, rng)
    constraints: list[Probe] = []
    attempts_left = initial_attempts

    while attempts_left > 1:
        # Diagnostics from centroid (only for logging / stop check).
        cc_lat, cc_lon = spherical_centroid(lat, lon)
        cc_d = haversine_m(cc_lat, cc_lon, lat, lon)
        diameter = float(2.0 * cc_d.max())

        if diameter < target_diameter_m:
            log(
                f"[stop] n={len(lat)} diam≈{diameter:.3f}m < {target_diameter_m}m, ready to guess "
                f"attempts_left={attempts_left}"
            )
            return cc_lat, cc_lon, constraints

        # Pick (centre, radius) by best-of-trials greedy.
        c_lat, c_lon, r = _pick_probe_centre(lat, lon, rng, trials=12)

        log(
            f"[probe {len(constraints)+1}] n={len(lat)} centre=({c_lat:.6f},{c_lon:.6f}) "
            f"r={r:.3f}m centroid=({cc_lat:.6f},{cc_lon:.6f}) diam≈{diameter:.3f}m "
            f"attempts_left={attempts_left}"
        )

        found, server_left = oracle(c_lat, c_lon, r)
        attempts_left -= 1
        if server_left is not None:
            attempts_left = server_left

        probe = Probe(c_lat, c_lon, r, found)
        constraints.append(probe)

        mask = _apply_constraint(lat, lon, probe)
        lat, lon = lat[mask], lon[mask]
        log(f"  ↳ found={found} kept={len(lat)}")

        if len(lat) < resample_floor:
            # Resample by bootstrap-with-jitter so that the cluster's spatial
            # support is preserved (cap-uniform proposal expands extent → bad).
            new_lat, new_lon = _bootstrap_jitter(
                lat, lon, constraints, initial_n, rng
            )
            lat, lon = new_lat, new_lon
            log(f"  ↳ resampled (bootstrap+jitter) to n={len(lat)}")

    cc_lat, cc_lon = spherical_centroid(lat, lon)
    log(f"[final] attempts_left={attempts_left}, centroid=({cc_lat:.6f},{cc_lon:.6f})")
    return cc_lat, cc_lon, constraints


def _bootstrap_jitter(
    lat: np.ndarray,
    lon: np.ndarray,
    constraints: list[Probe],
    target: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Densify by sampling existing points with replacement + small Gaussian
    jitter, then re-applying constraints. Preserves spatial distribution.

    Jitter sigma = max(cluster radius / 4, 1m).
    """
    if len(lat) == 0:
        return lat, lon
    cc_lat, cc_lon = spherical_centroid(lat, lon)
    radii = haversine_m(cc_lat, cc_lon, lat, lon)
    sigma_m = max(float(radii.max()) / 4.0, 1.0)
    # Convert metres to degrees: 1 deg lat ≈ 111_320 m; lon scaled by cos(lat).
    deg_per_m_lat = 1.0 / 111_320.0
    rounds = 0
    out_lat: list[np.ndarray] = []
    out_lon: list[np.ndarray] = []
    have = 0
    while have < target and rounds < 30:
        rounds += 1
        batch = max(target * 2, 4096)
        idx = rng.integers(0, len(lat), batch)
        nlat = lat[idx]
        nlon = lon[idx]
        jl = rng.normal(0.0, sigma_m * deg_per_m_lat, batch)
        cos_lat = np.cos(np.deg2rad(nlat))
        # avoid division by zero near poles
        cos_lat = np.where(np.abs(cos_lat) < 1e-3, 1e-3, cos_lat)
        jo = rng.normal(0.0, sigma_m * deg_per_m_lat, batch) / cos_lat
        nlat = nlat + jl
        nlon = nlon + jo
        # clamp lat into [-90, 90]; wrap lon into [-180, 180]
        nlat = np.clip(nlat, -89.999, 89.999)
        nlon = ((nlon + 180.0) % 360.0) - 180.0
        mask = np.ones(batch, dtype=bool)
        for p in constraints:
            mask &= _apply_constraint(nlat, nlon, p)
        if mask.any():
            out_lat.append(nlat[mask])
            out_lon.append(nlon[mask])
            have += int(mask.sum())
    if have == 0:
        return lat, lon
    return np.concatenate(out_lat)[:target], np.concatenate(out_lon)[:target]
