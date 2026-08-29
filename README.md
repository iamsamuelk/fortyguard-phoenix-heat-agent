# Phoenix Bus-Stop Cooling Priority Report

**FortyGuard Hackathon '26 — Track 1 (Resilient Cities & Infrastructure) / Track 6 (Agentic)**

## The problem

Phoenix riders wait for buses at stops that reach dangerous peak heat, and Maricopa
County tracks heat-associated illness and death every summer as a public health
crisis. Valley Metro and the City of Phoenix's Office of Heat Response &
Mitigation have limited shade/cooling capital budgets and need a defensible,
data-driven way to decide **which stops to fix first**.

## Who this is for

City of Phoenix heat-response planners and Valley Metro capital-planning teams —
anyone deciding where a shade structure, misting station, or reflective paving
dollar goes furthest.

## What this does

Starting from real Valley Metro GTFS stop data (40 real stops in the South
Phoenix / Central Ave corridor, a documented heat-vulnerable area), this
pipeline:

1. Pulls a live FortyGuard heatmap over the corridor (`POST /v1/heatmap`) and
   joins each bus stop to its containing tile's peak temperature
2. Ranks all 40 stops by peak heat exposure
3. Runs satellite segmentation (`POST /v1/satellite`) and street-view
   segmentation (`POST /v1/streetview`) on the top 3 hottest stops to diagnose
   *why* each is hot (impervious surface %, canopy %, sky exposure)
4. Pulls environmental parameters (`POST /v1/env_params`) for diurnal heat
   index, apparent temperature, wet-bulb temperature, and relative humidity
   across the day at each hot stop
5. Generates a threshold-triggered, per-stop prioritized action list
   (e.g. misting stations for dry-air-effective cooling vs. tree planting)
6. Bundles everything into a client-ready PDF report + CSV action list +
   interactive HTML maps

## Result

On 2025-07-15 (peak summer), the hottest stop in the corridor —
**7th Ave & Tamarisk St** — reached **40.3°C (104.5°F)** peak tile
temperature, with 78% impervious surface coverage and only 13% vegetation.
It's now the #1 recommended site for a misting station and reflective paving,
backed by real satellite and street-level imagery a planner can act on
immediately, not just an abstract heat number.

## FortyGuard endpoints used

- `POST /v1/heatmap`
- `POST /v1/satellite`
- `POST /v1/streetview`
- `POST /v1/env_params`
- `GET /v1/status/{activity_id}`

## Data sources

- Real bus stop coordinates: [Valley Metro GTFS feed](https://www.phoenixopendata.com),
  City of Phoenix Open Data portal
- Real temperature, surface, and environmental data: FortyGuard Temperature API

## How to run it

```bash
git clone <this-repo>
cd temperature-api-quickstart
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # paste your FORTYGUARD_API_KEY
jupyter lab
```

Open `notebooks/use_cases/urban_planner_bus_stop_prioritization.ipynb` and run
all cells. The South Phoenix AOI, real stop data (`data/sample_bus_stops.csv`),
and study date are already configured.

To regenerate `data/sample_bus_stops.csv` from a fresh GTFS pull, see
`prepare_phoenix_stops.py` in the repo root.

## Known issue

The "Surface Composition Across Top-N" summary chart on report page 3 renders
empty due to a data-shape mismatch in that aggregation cell. The same data is
fully present and correct on each stop's individual page (4, 7, 10).

## Output bundle

`outputs/bus_stops_2025-07-15/`
- `bus_stops_report.pdf` — full client-ready report
- `action_list.csv` — machine-readable ranked action list
- `maps/*.html` — interactive maps (overall heatmap, hot-stop cluster,
  satellite/street-view/env-params deep dives)
