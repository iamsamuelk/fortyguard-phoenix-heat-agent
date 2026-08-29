"""
Filters the real Valley Metro GTFS stops.txt down to the South Phoenix /
Central Ave corridor (a documented heat-vulnerable area) and writes
data/sample_bus_stops.csv in the schema the notebook expects:
    stop_id, name, latitude, longitude
"""
import pandas as pd
import pathlib

GTFS_STOPS = pathlib.Path("data/phoenix_gtfs/stops.txt")
OUT_CSV = pathlib.Path("data/sample_bus_stops.csv")

LAT_MIN, LAT_MAX = 33.365, 33.435
LON_MIN, LON_MAX = -112.095, -112.035

df = pd.read_csv(GTFS_STOPS)
df.columns = [c.strip() for c in df.columns]

mask = (
    (df["jurisdiction"].astype(str).str.strip() == "Phoenix")
    & (df["stop_lat"].between(LAT_MIN, LAT_MAX))
    & (df["stop_lon"].between(LON_MIN, LON_MAX))
)
subset = df[mask].copy()

subset = subset.rename(columns={
    "stop_id": "stop_id",
    "stop_name": "name",
    "stop_lat": "latitude",
    "stop_lon": "longitude",
})[["stop_id", "name", "latitude", "longitude"]]

subset = subset.head(40).reset_index(drop=True)

OUT_CSV.parent.mkdir(exist_ok=True)
subset.to_csv(OUT_CSV, index=False)
print(f"Wrote {len(subset)} real Phoenix stops to {OUT_CSV}")
print(subset.head())

aoi = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature", "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [LON_MIN, LAT_MIN], [LON_MAX, LAT_MIN],
                [LON_MAX, LAT_MAX], [LON_MIN, LAT_MAX],
                [LON_MIN, LAT_MIN],
            ]]
        }
    }]
}
print("\n--- Paste this into the notebook's Setup cell as SOUTH_PHOENIX_POLYGON ---")
import json
print(json.dumps(aoi, indent=2))
