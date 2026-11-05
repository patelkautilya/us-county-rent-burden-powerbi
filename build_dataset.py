"""Build a county-level 2024 ACS 1-year rental cost-burden panel.

Downloads the Census table-based summary files; no API key is needed.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import statistics
import urllib.request
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF"
SOURCES = {
    "geography": f"{BASE}/documentation/Geos20241YR.txt",
    "rent_burden": f"{BASE}/data/1YRData/acsdt1y2024-b25070.dat",
    "tenure": f"{BASE}/data/1YRData/acsdt1y2024-b25003.dat",
    "median_gross_rent": f"{BASE}/data/1YRData/acsdt1y2024-b25064.dat",
}


def download_table(name: str) -> tuple[list[dict[str, str]], str]:
    request = urllib.request.Request(SOURCES[name], headers={"User-Agent": "analyst-portfolio/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
    digest = hashlib.sha256(raw).hexdigest()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter="|")
    return list(reader), digest


def integer(row: dict[str, str], key: str) -> int | None:
    value = row.get(key, "")
    if not value or value in {"-", "**", "***"}:
        return None
    number = int(value)
    return None if number < 0 else number


def county_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["GEO_ID"]: r for r in rows if r["GEO_ID"].startswith("0500000US")}


def main() -> None:
    loaded = {name: download_table(name) for name in SOURCES}
    geos = {
        r["GEO_ID"]: r
        for r in loaded["geography"][0]
        if r["SUMLEVEL"] == "050" and r["COMPONENT"] == "00"
    }
    burden = county_rows(loaded["rent_burden"][0])
    tenure = county_rows(loaded["tenure"][0])
    rent = county_rows(loaded["median_gross_rent"][0])
    keys = set(geos) & set(burden) & set(tenure) & set(rent)
    assert keys and set(geos) == set(tenure) == set(rent)
    missing_burden = sorted(geos[k]["NAME"] for k in set(geos) - set(burden))

    output: list[dict[str, object]] = []
    missing_rent = 0
    for geo_id in sorted(keys):
        g, b, t, m = geos[geo_id], burden[geo_id], tenure[geo_id], rent[geo_id]
        bins = [integer(b, f"B25070_E{i:03d}") for i in range(2, 12)]
        total = integer(b, "B25070_E001")
        occupied = integer(t, "B25003_E001")
        owners = integer(t, "B25003_E002")
        renters = integer(t, "B25003_E003")
        if any(v is None for v in [total, occupied, owners, renters, *bins]):
            raise ValueError(f"Unexpected missing count for {geo_id}")
        assert total == sum(bins), geo_id
        assert occupied == owners + renters, geo_id
        assert total == renters, geo_id  # Same renter-occupied universe; not-computed is retained.
        calculable = total - bins[-1]
        burdened = sum(bins[5:9])  # 30–34.9, 35–39.9, 40–49.9, 50%+
        severe = bins[8]
        assert 0 <= severe <= burdened <= calculable <= renters
        median_rent = integer(m, "B25064_E001")
        median_rent_moe = integer(m, "B25064_M001")
        if median_rent is None:
            missing_rent += 1
        name = g["NAME"]
        county, state = name.rsplit(", ", 1)
        output.append({
            "geo_id": geo_id,
            "state_fips": g["STATE"],
            "county_fips": g["COUNTY"],
            "state": state,
            "county": county,
            "county_state": name,
            "occupied_households": occupied,
            "owner_households": owners,
            "renter_households": renters,
            "rent_burden_calculable": calculable,
            "rent_burden_not_computed": bins[-1],
            "rent_burden_30plus": burdened,
            "rent_burden_50plus": severe,
            "rent_burden_30plus_pct": round(100 * burdened / calculable, 2) if calculable else "",
            "rent_burden_50plus_pct": round(100 * severe / calculable, 2) if calculable else "",
            "renter_share_pct": round(100 * renters / occupied, 2) if occupied else "",
            "median_gross_rent_usd": median_rent if median_rent is not None else "",
            "median_gross_rent_moe_usd": median_rent_moe if median_rent_moe is not None else "",
            "renter_households_moe": integer(t, "B25003_M003"),
            "rent_burden_total_moe": integer(b, "B25070_M001"),
        })

    assert len({r["geo_id"] for r in output}) == len(output)
    assert all(r["rent_burden_calculable"] > 0 for r in output)
    fields = list(output[0])
    with (ROOT / "acs_2024_county_rent_burden.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)

    rates = [float(r["rent_burden_30plus_pct"]) for r in output]
    top = sorted(output, key=lambda r: float(r["rent_burden_30plus_pct"]), reverse=True)
    eligible = [r for r in top if r["rent_burden_calculable"] >= 5000]
    summary = {
        "source": SOURCES,
        "sha256": {name: data[1] for name, data in loaded.items()},
        "counties": len(output),
        "counties_missing_rent_burden_table": missing_burden,
        "states_and_dc": len({r["state"] for r in output}),
        "median_county_burden_30plus_pct": round(statistics.median(rates), 2),
        "covered_county_pooled_30plus_pct": round(100 * sum(r["rent_burden_30plus"] for r in output) / sum(r["rent_burden_calculable"] for r in output), 2),
        "covered_county_renter_households": sum(r["renter_households"] for r in output),
        "counties_with_missing_median_rent": missing_rent,
        "top_five_burden_rate_min_5000_calculable": [
            {"county_state": r["county_state"], "rate_pct": r["rent_burden_30plus_pct"], "denominator": r["rent_burden_calculable"]}
            for r in eligible[:5]
        ],
        "state_counties": dict(sorted(Counter(r["state"] for r in output).items())),
    }
    (ROOT / "validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in {"source", "sha256", "state_counties"}}, indent=2))


if __name__ == "__main__":
    main()

