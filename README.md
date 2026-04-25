# MatChalendar

**Local-first AI campus planner** - a one-screen weekly planner for UCLA daily life.

MatChalendar turns a natural-language student goal into an explainable weekly calendar across class time, homework, dining, recovery, transportation, and carbon goals. The current MVP is API-ready and deterministic: no ASUS GX10, Agentverse, or OmegaClaw integration is implemented yet, but the UI and docs keep those as visible future integration points.

![MatChalendar status](https://img.shields.io/badge/status-api_ready_mvp-2c4a2e?style=flat-square)

## Quick Start

Run the API and static demo with Python:

```bash
python backend/main.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

You can still open `index.html` directly. In that mode, Run Planner attempts `POST http://127.0.0.1:8000/api/plan`; if the backend is unavailable, the frontend uses its local mock PlanResponse fallback.

## API

```text
POST /api/plan
GET /api/dining
GET /api/demo-schedule
GET /api/health
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/plan \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight.\"}"
```

## Project Structure

```text
MatChalendar/
|-- index.html
|-- styles.css
|-- app.js
|-- matcalendar-demo.html
|-- PRD_MatChalendar.md
|-- README.md
`-- backend/
    |-- main.py
    |-- planner/
    |   |-- master_planner.py
    |   |-- intent_parser.py
    |   |-- skill_router.py
    |   |-- calendar_replanner.py
    |   `-- schemas.py
    |-- skills/
    |   |-- calendar_skill.py
    |   |-- dining_skill.py
    |   |-- study_skill.py
    |   |-- health_skill.py
    |   |-- energy_skill.py
    |   |-- transportation_skill.py
    |   |-- sustainability_carbon_skill.py
    |   `-- explanation_skill.py
    |-- food/
    |   |-- food_data_pipeline.py
    |   |-- nutrition_estimator.py
    |   |-- carbon_estimator.py
    |   `-- food_store.py
    `-- data/
        |-- dining_mock.json
        |-- sample_schedule.json
        `-- carbon_factors.json
```

## Planner Flow

```text
user prompt -> intent parser -> skill router -> internal skills -> calendar replanner -> PlanResponse
```

The MVP keeps the code simple for a hackathon demo. Skills return recommendations, constraints, scores, and evidence; the Master Planner owns the final calendar output.

## Frontend

The one-screen demo preserves:

- left goal input / chat-style control panel
- right weekly calendar
- explanation drawer
- carbon budget card
- skills used trace
- local fallback PlanResponse

## Integration Points

- ASUS GX10: visible local-AI badge only; no local model call yet.
- Agentverse: planned external `CampusLifePlannerSkill`; not implemented yet.
- OmegaClaw: planned invoker; not implemented yet.

Built for LA Hacks 2026.
