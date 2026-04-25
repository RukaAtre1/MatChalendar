# MatChalendar

**Local-first AI campus planner** - a one-screen weekly planner for UCLA daily life.

MatChalendar turns a natural-language student goal into an explainable weekly calendar across class time, homework, dining, recovery, transportation, and carbon goals. The current MVP keeps a deterministic demo path, but now routes planning through a provider layer that uses ASI:One hosted AI first and falls back safely when AI is unavailable.

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
user prompt -> PlannerProvider -> ASI:One AIPlannerContext -> internal skills -> calendar replanner validation -> PlanResponse
```

If ASI:One is disabled or unavailable, the provider safely falls back to `fallback_planner.py`. Skills return recommendations, constraints, scores, and evidence; the planner pipeline owns the final calendar output. GX10 local AI remains an optional future provider and is disabled by default until a concrete model endpoint exists.

## AI and Memory

Planner source order:

```text
ASI:One hosted AI -> deterministic fallback
```

Environment variables:

```text
USE_ASI_ONE=true
ASI_ONE_API_KEY=
ASI_ONE_BASE_URL=https://api.asi1.ai/v1
ASI_ONE_MODEL=asi1
ASI_ONE_TIMEOUT_SECONDS=20

USE_LOCAL_AI=false
LOCAL_AI_PROVIDER=openai_compatible
LOCAL_AI_BASE_URL=
LOCAL_AI_API_KEY=
LOCAL_MODEL_NAME=
LOCAL_AI_TIMEOUT_SECONDS=20
```

For local setup, copy `.env.example` to `.env.local`, fill in your ASI:One key, and run `python backend/main.py`. `.env.local` is ignored by git and must not be committed. In PowerShell, you can also set session variables directly:

```powershell
$env:USE_ASI_ONE="true"
$env:ASI_ONE_API_KEY="<your-key>"
$env:ASI_ONE_BASE_URL="https://api.asi1.ai/v1"
$env:ASI_ONE_MODEL="asi1"
$env:ASI_ONE_TIMEOUT_SECONDS="20"
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

- ASI:One: `backend/integrations/asi_one.py` hosted planner reasoning adapter.
- ASUS GX10: `backend/integrations/local_ai.py` OpenAI-compatible adapter, disabled until configured.
- Agentverse: `CampusLifePlannerAgent` wrapper calls `PlannerProvider.plan()`.
- OmegaClaw: `CampusLifePlannerSkill` exposes MatChalendar as one high-level skill.

Built for LA Hacks 2026.
