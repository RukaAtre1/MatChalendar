# MatChalendar

**Local-first AI campus planner** - a one-screen weekly planner for UCLA daily life.

MatChalendar turns a natural-language student goal into an explainable weekly calendar across class time, homework, dining, recovery, transportation, and carbon goals. The current MVP keeps a deterministic demo path, but now routes planning through a provider layer that uses ASI:One hosted AI first and falls back safely when AI is unavailable.

![MatChalendar status](https://img.shields.io/badge/status-api_ready_mvp-2c4a2e?style=flat-square)

## Fetch.ai / Agentverse Deliverables

MatChalendar is registered as an Agentverse Chat Protocol agent and can be invoked from ASI:One.

**Agent name:** MatChalendar Campus Planner Agent  
**Agent handle:** @matchalendar

**Agentverse Agent Profile:**  
https://agentverse.ai/agents/details/agent1qgckjr38ks3wflddkzw3rh0ynf64z4uv2ec9axmcm40pwnr9jz7rcs5kmta/profile

**ASI:One Chat Session / Invite Link:**  
https://asi1.ai/invite?channelInviteKey=MK7fcyyuh87kQxz0dtADv7U9apOLYt91VXMCTKtjXr8

**Agentverse flow:**  
A user asks ASI:One to use @matchalendar. ASI:One invokes the Agentverse agent. The agent calls the MatChalendar backend planner and returns an explainable weekly calendar plan with carbon-aware replanning.

## Quick Start

Run the API and static demo from the project root:

```bash
python backend/main.py
```

On Windows PowerShell:

```powershell
cd C:\Users\12392\Desktop\MatChalendar
python backend\main.py
```

Or use the Windows startup script from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

You can still open `index.html` directly. In that mode, Run Planner attempts `POST http://127.0.0.1:8000/api/plan`; if the backend is unavailable, the frontend uses its local mock PlanResponse fallback.

Useful local endpoints:

```text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/api/runtime/status
http://127.0.0.1:8000/api/agentverse/plan
```

## ASUS GX10 / Local-first Runtime

MatChalendar includes a GX10/local-first runtime path for private, low-latency student planning. The normal local demo runs at `http://127.0.0.1:8000`; the same backend can be started on an ASUS Ascent GX10 and exposed on the LAN or tailnet, for example `http://100.121.103.97:8000`.

Run the local backend from PowerShell:

```powershell
python backend/main.py
```

Run the backend on GX10 by copying the project to the GX10, configuring `.env.local` on that machine, and starting the same backend command there:

```powershell
$env:USE_GX10_RUNTIME="false"
$env:LOCAL_BACKEND_URL="http://100.121.103.97:8000"
python backend/main.py
```

To point a local frontend/router at the GX10 backend, set these values in `.env.local` or in the current PowerShell session before starting the local backend:

```powershell
$env:USE_GX10_RUNTIME="true"
$env:GX10_BACKEND_URL="http://100.121.103.97:8000"
$env:LOCAL_BACKEND_URL="http://127.0.0.1:8000"
$env:RUNTIME_FAILOVER_ENABLED="true"
$env:RUNTIME_ROUTER_TIMEOUT_SECONDS="8"
python backend/main.py
```

When the frontend is opened from a backend origin, it calls that same origin by default. You can also override the planner API before `app.js` loads by setting `window.MATCHALENDAR_API_URL` to a URL such as `http://100.121.103.97:8000/api/plan`.

Verify runtime status:

```powershell
curl.exe http://127.0.0.1:8000/api/runtime/status
```

Verify planning:

```powershell
$body = @{
  prompt = "Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/plan" -Method POST -ContentType "application/json" -Body $body
```

The `/api/runtime/status` response includes `runtime_mode`, `backend_url`, `gx10_enabled`, `gx10_available`, `local_first`, `fallback_enabled`, `backend_label`, `agentverse_enabled`, and `asi_one_enabled`. If the GX10 URL is unreachable while `USE_GX10_RUNTIME=true`, the status reports `gx10_available=false` and the router can continue through deterministic fallback when `RUNTIME_FAILOVER_ENABLED=true`.

For ASUS challenge evidence, capture screenshots of:

- The frontend badge/card showing `ASUS GX10 / Local-first runtime`, runtime mode, GX10 availability, fallback status, and backend label.
- `curl.exe http://127.0.0.1:8000/api/runtime/status` in PowerShell.
- A successful `/api/plan` response using the demo prompt.
- `scripts/asus_gx10_evidence.ps1` output.
- If available, the same status page or frontend served from `http://100.121.103.97:8000`.

### Devpost ASUS Challenge Note

MatChalendar was built with a GX10/local-first runtime path for private student planning. The backend exposes a runtime router and status endpoint so the planner can run against an ASUS Ascent GX10 backend when available, while keeping a deterministic fallback for demo stability. This supports low-latency planning over sensitive student context such as schedules, dining preferences, health routines, transportation choices, and carbon goals.

Submission links:

```text
Agentverse Profile URL: https://agentverse.ai/agents/details/agent1qgckjr38ks3wflddkzw3rh0ynf64z4uv2ec9axmcm40pwnr9jz7rcs5kmta/profile
ASI:One Shared Chat URL: https://asi1.ai/invite?channelInviteKey=MK7fcyyuh87kQxz0dtADv7U9apOLYt91VXMCTKtjXr8
```

## API

```text
POST /api/plan
POST /api/agentverse/plan
POST /api/memory/update
GET /api/memory
GET /api/dining
GET /api/demo-schedule
GET /api/health
GET /api/runtime/status
```

## UCLA Dining Cache

Refresh the local UCLA Dining knowledge base before running a dining-aware demo:

```bash
python backend/food/food_data_pipeline.py --days 7
```

The scraper reads UCLA Dining's official menu and menu-item nutrition pages, writes an ignored local cache under `backend/data/dining_cache/`, and the planner falls back to `dining_mock.json` if that cache is missing or malformed. ASI:One only receives the user's planning intent; full menu records stay in the backend cache and are retrieved by internal skills.

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

USE_GX10_RUNTIME=false
GX10_BACKEND_URL=http://100.121.103.97:8000
LOCAL_BACKEND_URL=http://127.0.0.1:8000
RUNTIME_FAILOVER_ENABLED=true
AGENTVERSE_AGENT_ENABLED=false
RUNTIME_ROUTER_TIMEOUT_SECONDS=8

MATCHALENDAR_BACKEND_URL=http://127.0.0.1:8000
AGENT_NAME=MatChalendar Campus Planner Agent
AGENT_SEED_PHRASE=replace_with_secure_seed
AGENT_ENDPOINT=https://replace-with-current-ngrok-host
AGENTVERSE_KEY=replace_if_needed
ASI1_API_KEY=replace_if_needed
AGENTVERSE_API_KEY=replace_if_needed
```

For local setup, copy `.env.example` to `.env.local`, fill in your ASI:One key, and run `python backend/main.py`. Do not commit `.env.local` or any API keys. `.env.local` contains local-only secrets such as ASI:One and Agentverse API keys. `.env.local` is ignored by git and must not be committed. In PowerShell, you can also set session variables directly:

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

## Agentverse

MatChalendar includes a Fetch.ai uAgents Chat Protocol agent:

```text
agentverse/matchalendar_agent.py
```

The agent name is `MatChalendar Campus Planner Agent`. It reads `MATCHALENDAR_BACKEND_URL`, defaults to `http://127.0.0.1:8000`, calls `POST /api/plan`, and formats the backend plan as a concise chat response with a summary, calendar blocks, carbon adjustment, skills used, and local-first / GX10 runtime note. If the backend is unavailable, it returns a deterministic demo plan.

Install the Agentverse dependency:

```powershell
python -m pip install uagents
```

Run the backend:

```powershell
cd C:\Users\12392\Desktop\MatChalendar
python backend\main.py
```

Run the Agentverse agent in a second terminal:

```powershell
cd C:\Users\12392\Desktop\MatChalendar
python agentverse\matchalendar_agent.py
```

Expected terminal output includes an agent address beginning with:

```text
agent1...
```

To point the agent at a GX10 or public backend:

```powershell
$env:MATCHALENDAR_BACKEND_URL="http://<gx10-or-public-backend>:8000"
python agentverse\matchalendar_agent.py
```

For Agentverse External Integration through ngrok, set `AGENT_ENDPOINT` to the ngrok base URL without `/submit`:

```powershell
$env:AGENT_ENDPOINT="https://swaddling-autopilot-chaperone.ngrok-free.dev"
python agentverse\matchalendar_agent.py
```

Register this webhook URL in Agentverse:

```text
${AGENT_ENDPOINT}/submit
```

Register on Agentverse:

1. Start the backend and `agentverse/matchalendar_agent.py`.
2. Open the Agentverse inspector or registration flow shown in the uAgents startup logs.
3. Register the running uAgent as `MatChalendar Campus Planner Agent`.
4. Use this description: `A campus-life planning agent that turns a student's natural language request into an explainable weekly calendar across classes, homework, dining, health, energy, transportation, and carbon impact.`
5. Paste the final profile link into the placeholders below.

```text
Agentverse Profile URL: TBD
ASI:One Shared Chat URL: TBD
```

Test from ASI:One by asking it to use the MatChalendar Campus Planner Agent with this prompt:

```text
Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight.
```

Expected output:

- summary of the weekly plan
- calendar blocks for class, homework, meals, recovery, and low-carbon transportation
- carbon adjustment after the emergency Uber
- skills used
- local-first / GX10 runtime note if available

## Integration Points

- ASI:One: `backend/integrations/asi_one.py` hosted planner reasoning adapter.
- ASUS GX10: `backend/integrations/local_ai.py` OpenAI-compatible adapter, disabled until configured.
- Runtime router: `backend/runtime_router.py` lets Agentverse/Python entrypoints try GX10 first and fall back to the in-process local planner.
- Agentverse: `POST /api/agentverse/plan` returns a compact structured plan when `AGENTVERSE_AGENT_ENABLED=true`.
- OmegaClaw: `CampusLifePlannerSkill` exposes MatChalendar as one high-level skill through the same runtime router.

See `docs/gx10-agentverse-runtime.md` for GX10, public tunnel, Agentverse registration, and post-hackathon disable steps.

## Troubleshooting

If Python reports that `backend/main.py` is not found, you are not in the project root. Start from:

```powershell
cd C:\Users\12392\Desktop\MatChalendar
python backend\main.py
```

Or run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
```

If port 8000 is already occupied on Windows, find and stop the process:

```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Built for LA Hacks 2026.
