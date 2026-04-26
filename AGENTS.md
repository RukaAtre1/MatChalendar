# MatChalendar Agent Notes

## Product Direction

MatChalendar is a local-first, carbon-aware AI planner-orchestrator for campus life. It is not just a calendar app and not just a chatbot. The user gives a natural-language goal, the AI planner understands intent, internal skills provide options/evidence, and the backend returns an executable weekly calendar with explanations, scores, carbon impact, and skills used.

The product should feel personalized and OpenClaw-like: it reads `backend/memory/SOUL.md`, uses `backend/memory/MEMORY.md` for stable user preferences, and produces plans that feel aware of the user instead of hardcoded.

## Current Architecture

- Active planner priority is ASI:One first, then deterministic fallback.
- GX10/local AI is a future optional provider only. Keep it disabled unless a real OpenAI-compatible local endpoint and model name are provided.
- ASI:One returns structured `AIPlannerContext` only:
  - `goals`
  - `constraints`
  - `priority_order`
  - `selected_skills`
  - `tradeoffs`
  - `explanation_draft`
  - `confidence`
- ASI:One must not directly own or overwrite final `plan_blocks`.
- Backend planner pipeline owns final calendar generation, validation, metadata, fallback, and PlanResponse shape.
- Internal skills return recommendations, constraints, scores, evidence, and reasoning notes. Skills do not own final calendar placement.

Key files:

- `backend/planner/planner_provider.py`: provider selection and PlanResponse metadata.
- `backend/integrations/asi_one.py`: ASI:One OpenAI-compatible adapter.
- `backend/integrations/local_ai.py`: future GX10/local adapter.
- `backend/planner/ai_master_planner.py`: normalizes AI planner context into backend planner contract.
- `backend/planner/fallback_planner.py`: deterministic fallback and pipeline orchestration.
- `backend/planner/calendar_replanner.py`: final calendar block generation.
- `backend/memory/SOUL.md` and `backend/memory/MEMORY.md`: product identity and user preferences.

## Secrets and Environment

Never commit, print, or copy secrets into tracked files.

Local ASI:One config lives in ignored `.env.local`. `.env.example` documents the shape:

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

`backend/config.py` loads `.env` and `.env.local`.

ASI:One requires `User-Agent: MatChalendar/1.0`; without it, requests may return `403` with `error code: 1010`.

## Frontend Rules

- Keep the one-screen demo working at `http://127.0.0.1:8000`.
- Frontend calls `POST /api/plan`.
- Do not show verbose internal metadata in the main UI. Keep only a concise planner badge such as `ASI:One assisted`, `Deterministic fallback`, or `Frontend fallback`.
- Do not show long strategy/status prose in the carbon budget card. Keep the carbon number, target, percent, and meter.
- Different prompts should produce visibly different calendar blocks.
- Frontend request timeout should remain long enough for ASI:One, currently 30 seconds.

## Current Behavior to Preserve

- If ASI:One succeeds, `/api/plan` returns:
  - `metadata.planner_mode = "asi_one_hosted_ai"`
  - `metadata.integrations_used` includes `asi_one`
  - valid backend-generated `plan_blocks`
  - `ai_planner_context`
  - `confidence`
- If ASI:One is disabled, invalid, times out, or returns malformed JSON, `/api/plan` returns a valid deterministic fallback.
- Prompt-adaptive calendar variants currently include:
  - sustainability/vegetarian/walk/transit prompts: low-waste grocery, plant-forward dinner, bike study trip, low-waste meal prep.
  - low-energy/recovery prompts: gentle homework block, early wind-down, quiet recovery reset.
  - meeting/group project prompts: group project meeting.
  - focused study/homework prompts: focused study sprint and assignment review buffer.

## Verification

Run these before handing work back:

```powershell
python -m compileall backend
node --check app.js
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/health -Method Get
```

Useful smoke test:

```powershell
$body = @{ prompt = "Plan my UCLA week around sustainability. I prefer vegetarian meals, walking, transit, and focused study blocks." } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/plan -Method Post -ContentType "application/json" -Body $body -TimeoutSec 30
```

Expected when ASI is configured: `metadata.planner_mode` should be `asi_one_hosted_ai`.

## Next Useful Work

- Make calendar generation more genuinely AI-guided while still backend validated.
- Add better conflict resolution when multiple prompt-derived blocks compete for time.
- Improve PlanResponse validation details and expose user-friendly fallback notices only where needed.
- Add tests for provider fallback, AI context normalization, and prompt-adaptive calendar variants.
- Consider moving from the built-in `http.server` handler to FastAPI only if it helps demo stability or integration needs.

