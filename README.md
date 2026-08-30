# Phoenix Heat Vulnerability Model — Bus-Stop Cooling Prioritization

**FortyGuard Hackathon '26 — Track 5 (Model Designing)**

## The problem

Phoenix riders wait for buses at stops that reach dangerous peak heat, and
Maricopa County tracks heat-associated illness and death every summer. Valley
Metro and the City of Phoenix's Office of Heat Response & Mitigation have
limited capital budgets and need a scalable, data-driven way to estimate heat
risk at stops — including new or unmeasured ones — without needing a live
heatmap call for every single site.

## Who this is for

City of Phoenix heat-response planners and Valley Metro capital-planning
teams, plus anyone building downstream heat-safety tooling who needs a fast,
cheap heat-risk estimate from satellite imagery alone.

## What we built

Using real Valley Metro GTFS stop data (40 real stops in the South Phoenix /
Central Ave corridor, a documented heat-vulnerable area) and FortyGuard's
Temperature API as ground truth, we:

1. Pulled a live FortyGuard heatmap and satellite segmentation for all 40
   stops — real, live-measured surface composition (% impervious, %
   vegetation, % sky) and peak tile temperature for every stop
2. Pulled live environmental parameters (24-hour diurnal heat index, relative
   humidity, wet-bulb temperature) for all 40 stops
3. **Trained a linear regression model** predicting peak heat index from
   satellite-derived surface composition alone
4. **Validated it properly**: 5-fold cross-validation (not a single lucky
   train/test split), reporting R² and MAE with variance across folds
5. **Packaged it as a deployable artifact** (`heat_vulnerability_model.joblib`)
   with a clean `predict_heat_index(impervious_pct, vegetation_pct, sky_pct)`
   function any downstream tool can call

## Why this approach, and an honest note on what didn't work

Our first target was raw peak tile temperature — but at extreme Phoenix
summer heat, 2-meter air temperature saturates into a very narrow band
(39.88°C–40.31°C across all 40 stops, a 0.43°C spread) almost regardless of
local surface type, so surface composition alone couldn't explain the
remaining variance (5-fold CV R² was negative — worse than predicting the
mean). This is itself a legitimate finding: **air temperature is the wrong
target to model locally during extreme heat**.

We pivoted to **peak heat index** (which combines temperature and humidity
into a feels-like measure) as the target, since it showed 6x more variance
across the corridor (2.50°C spread). That model shows real, honestly
validated signal:

- **5-fold CV R²: 0.131** (mean across folds; std 0.235)
- **5-fold CV MAE: 0.647°C**
- **Held-out test set R²: 0.365, MAE: 0.592°C** (n=8)
- Coefficients make physical sense: impervious surface increases heat index
  (+0.0087°C per 1%), open sky slightly decreases it (−0.0579°C per 1%,
  likely a shade-availability proxy)

This is a modest-but-real effect, reported honestly with proper
cross-validation rather than an inflated single-split number. A model like
this is only useful for triage/screening at scale, not as a replacement for
FortyGuard's own live heatmap for a final go/no-go decision — and we say so
explicitly, because that's the honest limitation.

## FortyGuard endpoints used

- `POST /v1/heatmap` — ground-truth peak temperature per stop (all 40)
- `POST /v1/satellite` — surface composition features (all 40)
- `POST /v1/env_params` — diurnal heat index / RH / wet-bulb (all 40)
- `POST /v1/streetview` — ground-level confirmation on top-3 hottest stops
- `GET /v1/status/{activity_id}` — polling

## Data sources

- Real bus stop coordinates: [Valley Metro GTFS feed](https://www.phoenixopendata.com)
- All temperature, surface, and environmental features: live FortyGuard API
  calls, not cached samples

## How to run it

```bash
git clone <this-repo>
cd temperature-api-quickstart
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install scikit-learn joblib
cp .env.example .env   # paste your FORTYGUARD_API_KEY
jupyter lab
```

Open `notebooks/use_cases/urban_planner_bus_stop_prioritization.ipynb` and run
all cells in order, including the Track-5 add-on cells (full-corpus satellite
loop, full-corpus env-params loop, and the model training/validation cell).

To use the trained model directly without rerunning the notebook:

```python
import joblib
bundle = joblib.load('outputs/bus_stops_2025-07-15/heat_vulnerability_model.joblib')
model = bundle['model']
prediction = model.predict([[75.0, 5.0, 0.0]])  # [impervious%, vegetation%, sky%]
```

## Output bundle

`outputs/bus_stops_2025-07-15/`
- `bus_stops_report.pdf` — client-ready report on the top-3 hottest stops
- `action_list.csv` — machine-readable ranked action list
- `heat_vulnerability_model.joblib` — the trained, validated, deployable model
- `maps/*.html` — interactive maps

`data/heat_vulnerability_training_data.csv` — the full 40-stop training table
(features + targets), for reproducibility.

## Known issue

The "Surface Composition Across Top-N" summary chart on PDF report page 3
renders empty due to a data-shape mismatch in that aggregation cell. The same
data is fully present and correct on each stop's individual page.
