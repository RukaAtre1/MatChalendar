# MatChalendar

**Local-first AI campus planner** - a one-screen weekly planner for UCLA daily life.

MatChalendar turns a natural-language student goal into an explainable weekly calendar across class time, homework, dining, recovery, transportation, and carbon goals. The current MVP keeps a deterministic demo path, but now routes planning through a provider layer that can use GX10 local AI, ASI:One hosted AI, or deterministic fallback.

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
POST /api/memory/update
GET /api/memory
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
    |-- agents/
    |   `-- campus_life_planner_agent.py
    |-- integrations/
    |   |-- local_ai.py
    |   `-- asi_one.py
    |-- memory/
    |   |-- SOUL.md
    |   |-- MEMORY.md
    |   `-- memory_store.py
    |-- planner/
    |   |-- planner_provider.py
    |   |-- ai_master_planner.py
    |   |-- fallback_planner.py
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
    |-- skills_external/
    |   `-- campus_life_planner_skill.py
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
user prompt -> PlannerProvider -> GX10 local AI or ASI:One planner contract -> internal skills -> calendar replanner validation -> PlanResponse
```

If GX10 and ASI:One are disabled or unavailable, the provider safely falls back to `fallback_planner.py`. Skills return recommendations, constraints, scores, and evidence; the planner pipeline owns the final calendar output.

## AI and Memory

Planner source order:

```text
GX10 local AI -> ASI:One hosted AI -> deterministic fallback
```

Environment variables:

```text
USE_LOCAL_AI=false
LOCAL_AI_BASE_URL=
LOCAL_MODEL_NAME=
FALLBACK_TO_MOCK=true

USE_ASI_ONE=false
ASI_ONE_API_KEY=
ASI_ONE_BASE_URL=
ASI_ONE_MODEL=
```

`SOUL.md` defines MatChalendar's product identity. `MEMORY.md` stores approved long-term preferences. `/api/plan` includes both in AI planner context and returns a `memory_update_suggestion` when useful. The frontend can save approved suggestions through `/api/memory/update`.

## Frontend

The one-screen demo preserves:

- left goal input / chat-style control panel
- right weekly calendar
- explanation drawer
- carbon budget card
- skills used trace
- generated_by / planner_mode badge
- memory update suggestion card
- local fallback PlanResponse

## Integration Points

- ASUS GX10: `backend/integrations/local_ai.py` OpenAI-compatible local adapter.
- ASI:One: `backend/integrations/asi_one.py` hosted planner reasoning adapter.
- Agentverse: `CampusLifePlannerAgent` wrapper calls `PlannerProvider.plan()`.
- OmegaClaw: `CampusLifePlannerSkill` exposes MatChalendar as one high-level skill.

Built for LA Hacks 2026.
