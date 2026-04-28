"""Spherical math primitives for findmyring solver.

Distances use Earth radius R = 6_371_000 m (typical mean radius). The server
likely uses google.maps.geometry.spherical.computeDistanceBetween, which is
WGS84-ellipsoidal in places; the difference matters only at sub-metre scales,
so we accept ~0.5% error and verify empirically against /api/antenna responses.
"""
from __future__ import annotations

import numpy as np

EARTH_R = 6_371_000.0  # metres


def latlon_to_xyz(lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
    """Convert (lat, lon) in degrees → unit vectors (..., 3)."""
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)
    cos_lat = np.cos(lat)
    return np.stack([cos_lat * np.cos(lon), cos_lat * np.sin(lon), np.sin(lat)], axis=-1)


def xyz_to_latlon(xyz: np.ndarray) -> tuple[float, float]:
    """Convert single unit vector → (lat_deg, lon_deg)."""
    x, y, z = xyz / np.linalg.norm(xyz)
    lat = np.rad2deg(np.arcsin(np.clip(z, -1.0, 1.0)))
    lon = np.rad2deg(np.arctan2(y, x))
    return float(lat), float(lon)


def haversine_m(lat1: float, lon1: float, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Great-circle distance from one point to many, in metres."""
    p1 = np.deg2rad(lat1)
    p2 = np.deg2rad(lat2)
    dl = np.deg2rad(lon2 - lon1)
    dp = p2 - p1
    a = np.sin(dp / 2.0) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2.0) ** 2
    return 2.0 * EARTH_R * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def spherical_centroid(lat: np.ndarray, lon: np.ndarray) -> tuple[float, float]:
    """Centroid by averaging unit vectors. Returns (lat_deg, lon_deg)."""
    xyz = latlon_to_xyz(lat, lon)
    mean = xyz.mean(axis=0)
    norm = np.linalg.norm(mean)
    if norm < 1e-12:
        # Degenerate — antipodal cluster. Fall back to first point.
        return float(lat[0]), float(lon[0])
    return xyz_to_latlon(mean / norm)


def sample_uniform_sphere(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """N points uniformly on the sphere via Lambert (cos-lat) sampling."""
    u = rng.random(n)
    v = rng.random(n)
    lat = np.rad2deg(np.arcsin(2.0 * u - 1.0))
    lon = (v * 360.0) - 180.0
    return lat, lon


def cluster_diameter_m(lat: np.ndarray, lon: np.ndarray) -> float:
    """Approximate max pairwise distance via centroid + 2 * max-radius.

    For tight clusters this is close to the true diameter and avoids O(n²).
    """
    if len(lat) <= 1:
        return 0.0
    c_lat, c_lon = spherical_centroid(lat, lon)
    d = haversine_m(c_lat, c_lon, lat, lon)
    return float(2.0 * d.max())
