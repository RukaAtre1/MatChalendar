# MatChalendar

**A sustainability-aware AI life planner that turns chaotic student weeks into executable calendar plans.**

MatChalendar is a full-stack AI planning project built for student life at UCLA. A student gives one natural-language goal, and the system returns a structured weekly plan across classes, homework, dining, health, recovery, transportation, energy, and carbon goals.

The product is not just a calendar UI and not just a chatbot. It is a planner-orchestrator:

```text
Master AI Planner + Specialist Skills + Food Data Intelligence + Carbon-aware Calendar Replanning
```

Core design principle:

```text
Skills propose. Planner decides. Calendar renders.
```

## Demo Prompt

Try this prompt in the one-screen demo or through `POST /api/plan`:

```text
Plan my UCLA week around sustainability. I prefer vegetarian meals, walking, transit, and focused study blocks. I have class from 10 to 2 and homework tonight.
```

MatChalendar should produce visibly different plans for sustainability, recovery, homework, and group-project prompts. The response includes an explanation, calendar blocks, skill traces, carbon budget estimates, and planner metadata.

## What It Does

- Converts messy natural-language student goals into validated weekly calendar blocks.
- Plans across academics, dining, health, energy, transportation, recovery, and sustainability.
- Uses specialist skills to propose recommendations, constraints, scores, and evidence.
- Runs a backend-owned calendar replanning step so final `plan_blocks` are validated and executable.
- Estimates carbon impact for meals and transportation choices without claiming exact real-world accounting precision.
- Provides a stable deterministic fallback when hosted AI, Agentverse, or a remote runtime is unavailable.
- Supports a local-first backend runtime that can be deployed on an ASUS Ascent GX10 and accessed over a LAN or tailnet.
- Exposes an Agentverse / ASI:One path so users can ask `@matchalendar` for a plan from ASI:One.

## Architecture Overview

```text
User prompt
  -> PlannerProvider
  -> ASI:One AIPlannerContext or deterministic fallback
  -> intent normalization
  -> specialist skill router
  -> calendar replanner and validator
  -> PlanResponse
  -> web UI or Agentverse response
```

The hosted AI layer is intentionally constrained. ASI:One returns structured planning context only:

- `goals`
- `constraints`
- `priority_order`
- `selected_skills`
- `tradeoffs`
- `explanation_draft`
- `confidence`

The backend planner owns the final calendar generation, validation, metadata, fallback behavior, and `PlanResponse` shape. This keeps the system explainable and demo-stable: AI can guide the plan, but it does not directly overwrite the calendar.

## Specialist Skills

MatChalendar includes internal specialist skills under `backend/skills/`:

- `calendar_skill.py`: schedule constraints and class-aware time windows.
- `study_skill.py`: focused study sprints, assignment buffers, and academic planning.
- `dining_skill.py`: UCLA dining recommendations from local menu data or mock fallback data.
- `health_skill.py`: recovery, sleep, and wellness-aware planning.
- `energy_skill.py`: low-energy and high-focus block placement.
- `transportation_skill.py`: walking, biking, transit, and trip-mode recommendations.
- `sustainability_carbon_skill.py`: carbon budget estimates and low-impact alternatives.
- `explanation_skill.py`: concise reasoning for the final plan.

Skills return options, constraints, evidence, and scores. They do not own final placement. The planner compares those proposals and the calendar renderer turns decisions into blocks.

## Carbon-Aware Replanning

MatChalendar treats sustainability as a scheduling constraint, not an afterthought. The planner can adapt blocks for prompts about vegetarian meals, transit, walking, biking, low-waste groceries, and recovery after higher-carbon choices such as an emergency ride.

The carbon features are designed for useful relative planning:

- Food estimates are grounded in local dining data and ingredient/category heuristics.
- Transportation estimates compare lower-impact options such as walking, biking, and transit.
- The UI surfaces a carbon budget, estimated impact, percent used, and relevant skill traces.
- The system avoids claiming exact certified emissions accounting.

Refresh the local UCLA Dining cache before a dining-heavy demo:

```bash
python backend/food/food_data_pipeline.py --days 7
```

If the live cache is missing or malformed, the planner falls back to `backend/data/dining_mock.json`.

## Agentverse / ASI:One Integration

MatChalendar is registered as an Agentverse Chat Protocol agent and can be invoked from ASI:One.

```text
Agent name:   MatChalendar Campus Planner Agent
Agent handle: @matchalendar
```

- Agentverse Profile: https://agentverse.ai/agents/details/agent1qgckjr38ks3wflddkzw3rh0ynf64z4uv2ec9axmcm40pwnr9jz7rcs5kmta/profile
- ASI:One Shared Chat: https://asi1.ai/invite?channelInviteKey=MK7fcyyuh87kQxz0dtADv7U9apOLYt91VXMCTKtjXr8

Agentverse flow:

```text
ASI:One
  -> @matchalendar Agentverse agent
  -> MatChalendar backend planner
  -> specialist skills
  -> structured calendar response
  -> ASI:One answer
```

Relevant files:

- `agentverse/matchalendar_agent.py`
- `backend/agentverse_payload.py`
- `backend/integrations/asi_one.py`
- `backend/planner/planner_provider.py`

Run the Agentverse agent locally after starting the backend:

```powershell
python -m pip install uagents
python agentverse\matchalendar_agent.py
```

Point the agent at a GX10 or public backend:

```powershell
$env:MATCHALENDAR_BACKEND_URL="http://<gx10-or-public-backend>:8000"
python agentverse\matchalendar_agent.py
```

Do not commit API keys, seed phrases, ngrok URLs with secrets, or `.env.local`.

## ASUS GX10 Local-First Runtime

MatChalendar includes a local-first backend/planner runtime designed to run on the ASUS Ascent GX10. Sensitive student context such as class schedules, dining preferences, health routines, transportation choices, energy patterns, and carbon goals can be processed through a local backend deployed on the GX10 and accessed over a local network or tailnet.

This project does not claim completed local model inference on GX10 unless an OpenAI-compatible local model endpoint is explicitly configured. The current GX10 path focuses on running the planner backend locally, exposing runtime status, supporting LAN/tailnet access, and keeping deterministic fallback available for demo stability when external AI services are unavailable.

Run on GX10:

```bash
cd /home/asus/MatChalendar
bash scripts/start_backend_gx10.sh
```

The GX10 startup script creates `.venv` if needed, installs `requirements.txt`, binds the backend to `0.0.0.0:8000`, and serves the one-screen demo at:

```text
http://<gx10-ip>:8000
```

Health and runtime checks:

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/runtime/status
```

Useful GX10 environment variables:

```bash
export MATCHALENDAR_HOST=0.0.0.0
export MATCHALENDAR_PORT=8000
export USE_GX10_RUNTIME=false
export RUNTIME_FAILOVER_ENABLED=true
python backend/main.py
```

To route a local frontend/backend through a GX10 backend:

```powershell
$env:USE_GX10_RUNTIME="true"
$env:GX10_BACKEND_URL="http://<gx10-ip>:8000"
$env:LOCAL_BACKEND_URL="http://127.0.0.1:8000"
$env:RUNTIME_FAILOVER_ENABLED="true"
$env:RUNTIME_ROUTER_TIMEOUT_SECONDS="8"
python backend\main.py
```

The runtime status response includes `runtime_mode`, `backend_url`, `gx10_enabled`, `gx10_available`, `local_first`, `fallback_enabled`, `backend_label`, `agentverse_enabled`, and `asi_one_enabled`.

## Figma Make Design Process

Figma Make was used to prototype and iterate on the explanation drawer and visual hierarchy for AI reasoning, carbon impact, and skill traces. That design work shaped the one-screen demo around judge-readable information:

- A goal input and chat-style control area.
- A weekly calendar with concrete blocks.
- A concise planner badge instead of verbose internal metadata.
- A carbon budget card with number, target, percent, and meter.
- An explanation drawer that shows why the plan changed.
- Skill traces that make the orchestration visible without overwhelming the main UI.

## Tech Stack

- Frontend: HTML, CSS, vanilla JavaScript.
- Backend: Python `http.server` with a custom JSON API.
- Planner: provider layer, AI context normalization, deterministic fallback, skill router, calendar replanner, validation.
- AI integration: ASI:One OpenAI-compatible API adapter.
- Agent integration: Fetch.ai Agentverse / uAgents Chat Protocol.
- Local runtime: ASUS GX10 deployable backend path with runtime routing and fallback.
- Data: local UCLA dining cache, mock dining fallback, carbon factor data, memory files.

## Local Setup

Run the API and static demo from the project root:

```bash
python backend/main.py
```

Open:

```text
http://127.0.0.1:8000
```

Windows PowerShell:

```powershell
cd C:\Users\12392\Desktop\MatChalendar
python backend\main.py
```

Or:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

Linux / macOS:

```bash
bash scripts/start_backend.sh
```

GX10 / LAN mode:

```bash
cd /home/asus/MatChalendar
bash scripts/start_backend_gx10.sh
```

Optional ASI:One setup:

```bash
cp .env.example .env.local
```

Then fill local values in `.env.local`:

```text
USE_ASI_ONE=true
ASI_ONE_API_KEY=
ASI_ONE_BASE_URL=https://api.asi1.ai/v1
ASI_ONE_MODEL=asi1
ASI_ONE_TIMEOUT_SECONDS=20
```

`.env.local` is ignored by git and must not be committed.

## API Endpoints

```text
GET  /api/health
GET  /api/runtime/status
GET  /api/dining
GET  /api/demo-schedule
GET  /api/memory
POST /api/plan
POST /api/agentverse/plan
POST /api/memory/update
POST /api/memory/save
```

The frontend calls `POST /api/plan`. If the backend is unavailable while `index.html` is opened directly, the frontend can fall back to a local mock response for demo continuity.

## Example Request / Response Shape

Request:

```bash
curl -X POST http://127.0.0.1:8000/api/plan \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"Plan my UCLA week around sustainability. I prefer vegetarian meals, walking, transit, and focused study blocks.\"}"
```

PowerShell:

```powershell
$body = @{
  prompt = "Plan my UCLA week around sustainability. I prefer vegetarian meals, walking, transit, and focused study blocks."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/plan" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
```

Response shape:

```json
{
  "summary": "A concise explanation of the weekly plan.",
  "generated_by": "asi_one_ai_assisted_planner",
  "metadata": {
    "planner_mode": "asi_one_hosted_ai",
    "integrations_used": ["asi_one"],
    "fallback_reason": "",
    "memory_used": true,
    "soul_used": true
  },
  "intent": {
    "primary_goal": "sustainability-aware weekly planning"
  },
  "understanding": {
    "goals": [],
    "constraints": []
  },
  "carbon_budget": {
    "target_kg": 20,
    "estimated_kg": 0,
    "percent_used": 0
  },
  "plan_blocks": [
    {
      "id": "block-1",
      "title": "Focused study sprint",
      "type": "study",
      "start": "2026-04-27T18:00:00",
      "end": "2026-04-27T19:30:00",
      "reason": "Why this block belongs here.",
      "scores": {
        "academic": 0.9,
        "carbon": 0.8
      },
      "skills_used": ["study", "calendar"]
    }
  ],
  "skills_used": ["study", "dining", "transportation", "sustainability_carbon"]
}
```

When ASI:One is configured successfully, expected metadata includes:

```text
metadata.planner_mode = "asi_one_hosted_ai"
metadata.integrations_used includes "asi_one"
```

When ASI:One is disabled, invalid, unavailable, times out, or returns malformed JSON, the backend returns a valid deterministic fallback plan.

## Project Structure

```text
MatChalendar/
|-- index.html
|-- styles.css
|-- app.js
|-- README.md
|-- requirements.txt
|-- scripts/
|   |-- start_backend.ps1
|   |-- start_backend.sh
|   |-- start_backend_gx10.sh
|   `-- asus_gx10_evidence.ps1
|-- agentverse/
|   `-- matchalendar_agent.py
`-- backend/
    |-- main.py
    |-- runtime_router.py
    |-- runtime_status.py
    |-- agentverse_payload.py
    |-- integrations/
    |   |-- asi_one.py
    |   `-- local_ai.py
    |-- memory/
    |   |-- SOUL.md
    |   |-- MEMORY.md
    |   `-- memory_store.py
    |-- planner/
    |   |-- planner_provider.py
    |   |-- ai_master_planner.py
    |   |-- fallback_planner.py
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

## Track Alignment

### LA Hacks / Devpost

- Meaningful student problem: turns overloaded campus life into concrete plans.
- Full-stack execution: working frontend, backend API, planner pipeline, skills, data, and integrations.
- User-centered design: one-screen workflow with planner explanation, carbon budget, and skill traces.
- Originality: combines AI planning, campus food intelligence, carbon-aware replanning, and Agentverse access.

### Fetch.ai / Agentverse

- Registered Agentverse agent with ASI:One shared chat.
- Agent turns chat requests into structured backend planner calls.
- Response includes calendar blocks, carbon adjustments, skills used, and runtime context.

### ASUS Hardware Challenge

- Backend/planner runtime can be deployed on ASUS Ascent GX10.
- Supports local/tailnet access for low-latency planning over sensitive student context.
- Includes deterministic fallback for stable demos if external AI services are unavailable.
- Does not overclaim local model inference unless a concrete local model endpoint is configured.

## Known Limitations

- Carbon estimates are practical planning heuristics, not audited emissions calculations.
- GX10 local model inference is optional future configuration through `backend/integrations/local_ai.py`; current submission should only claim local backend/runtime deployment unless a model endpoint is actually running.
- The current backend uses Python's built-in HTTP server for hackathon simplicity rather than FastAPI or a production WSGI/ASGI deployment.
- Dining data depends on a local cache or mock fallback when live UCLA Dining scraping is unavailable.
- Calendar conflict resolution is deterministic and can be improved for dense, real student calendars.

## Future Work

- Make calendar generation more deeply AI-guided while preserving backend validation.
- Add stronger conflict resolution when multiple prompt-derived blocks compete for the same time.
- Connect a real local OpenAI-compatible model endpoint on GX10 for private local inference.
- Expand dining data freshness, nutrition modeling, and sustainability scoring.
- Add more tests for provider fallback, AI context normalization, and prompt-adaptive variants.
- Move to FastAPI if it improves demo reliability, deployment, or integration ergonomics.
- Add calendar export and optional integration with real calendar providers.

## Verification

Recommended checks before demoing:

```powershell
python -m compileall backend
node --check app.js
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/health -Method Get
```

Useful smoke test:

```powershell
$body = @{
  prompt = "Plan my UCLA week around sustainability. I prefer vegetarian meals, walking, transit, and focused study blocks."
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8000/api/plan -Method Post -ContentType "application/json" -Body $body -TimeoutSec 30
```

Built for LA Hacks 2026.
