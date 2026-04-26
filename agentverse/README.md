# MatChalendar Campus Planner Agent

Agentverse Profile URL: TBD

ASI:One Shared Chat URL: TBD

## Purpose

MatChalendar Campus Planner Agent is a Fetch.ai uAgents Chat Protocol agent for campus-life planning. It turns a student's natural-language request into an explainable weekly calendar across classes, homework, dining, health, energy, transportation, and carbon impact.

The agent delegates planning to:

```text
POST ${MATCHALENDAR_BACKEND_URL}/api/plan
```

If the backend is unavailable, it returns a deterministic demo plan so Agentverse Testing still gets a response.

## Required Local Environment

Put these in `.env.local`:

```text
AGENTVERSE_KEY=<secret>
AGENT_SEED_PHRASE=<secret stable seed phrase>
AGENT_ENDPOINT=https://<current-ngrok-host>
MATCHALENDAR_BACKEND_URL=http://127.0.0.1:8000
```

`AGENT_ENDPOINT` is the ngrok base URL without `/submit`. Agentverse should register:

```text
${AGENT_ENDPOINT}/submit
```

The running agent address is derived from `AGENT_SEED_PHRASE`. If the seed changes, the address changes and Agentverse must be updated.

## Why /submit Can Return 400

The native uAgents ASGI server expects `/submit` to receive a full uAgents Envelope with fields such as `version`, `sender`, `target`, `session`, `schema_digest`, and `payload`.

Agentverse External Integration testing can send a simpler JSON body such as:

```json
{"text":"Plan my UCLA week with sustainability focus."}
```

`matchalendar_agent.py` installs `SubmitCompatibilityMiddleware` in front of the native uAgents `/submit` handler:

- valid uAgents Envelopes are forwarded to the normal Chat Protocol path
- plain JSON or ACP-style chat payloads are parsed directly
- all `/submit` raw request errors are logged
- parsed text is routed to the same MatChalendar backend planner

## Run

Terminal 1, backend:

```powershell
cd C:\Users\12392\Desktop\MatChalendar
python backend\main.py
```

Terminal 2, agent:

```powershell
cd C:\Users\12392\Desktop\MatChalendar
python agentverse\matchalendar_agent.py
```

Terminal 3, ngrok:

```powershell
ngrok http 8001
```

After ngrok prints the HTTPS URL, set `AGENT_ENDPOINT` in `.env.local` to that base URL and restart the agent.

## Register on Agentverse

Use the startup banner from `python agentverse\matchalendar_agent.py`.

Register:

```text
Agent address: <agent1... printed at startup>
Webhook URL: ${AGENT_ENDPOINT}/submit
Name: MatChalendar Campus Planner Agent
Protocol: AgentChatProtocol
```

For the current ngrok example:

```text
Webhook URL: https://swaddling-autopilot-chaperone.ngrok-free.dev/submit
```

## Smoke Tests

Local:

```powershell
Invoke-RestMethod -Uri http://localhost:8001/submit -Method Post -ContentType "application/json" -Body '{"text":"Plan my UCLA week with sustainability focus."}' -TimeoutSec 35
```

Ngrok:

```powershell
$agentEndpoint = "https://swaddling-autopilot-chaperone.ngrok-free.dev"
Invoke-RestMethod -Uri "$agentEndpoint/submit" -Method Post -ContentType "application/json" -Body '{"text":"Plan my UCLA week with sustainability focus."}' -TimeoutSec 35
```

Expected:

- HTTP 200
- response includes `MatChalendar Campus Planner Agent`
- agent logs `received message`
- agent logs `backend URL called: http://127.0.0.1:8000/api/plan`
- ngrok shows `POST /submit 200`

## ASI:One Test Prompt

```text
Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight.
```

Expected response includes summary, calendar blocks, carbon adjustment, skills used, and a local-first / GX10 runtime note.
