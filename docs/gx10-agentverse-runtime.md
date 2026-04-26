# GX10 Agentverse Runtime

MatChalendar keeps the normal frontend path on `POST /api/plan`. GX10 routing is only used by Agentverse/OmegaClaw and Python agent entrypoints.

## Run Local Backend

```powershell
python backend/main.py
```

Local demo URL:

```text
http://127.0.0.1:8000
```

Keep this in `.env.local` for local-only development:

```text
USE_GX10_RUNTIME=false
RUNTIME_FAILOVER_ENABLED=true
AGENTVERSE_AGENT_ENABLED=false
LOCAL_BACKEND_URL=http://127.0.0.1:8000
```

## Run GX10 Backend

On the ASUS GX10, run the same repository and configure ASI:One in `.env.local`. GX10 does not need a local LLM for this MVP.

```powershell
python backend/main.py
```

Expected Tailscale backend URL:

```text
http://100.121.103.97:8000
```

On the public-facing MatChalendar backend, enable GX10-first routing:

```text
USE_GX10_RUNTIME=true
GX10_BACKEND_URL=http://100.121.103.97:8000
LOCAL_BACKEND_URL=http://127.0.0.1:8000
RUNTIME_FAILOVER_ENABLED=true
AGENTVERSE_AGENT_ENABLED=true
RUNTIME_ROUTER_TIMEOUT_SECONDS=8
```

If GX10 fails or times out, Agentverse requests fall back to the local in-process planner. ASI:One still remains the first planner inside whichever backend handles the request.

## Public HTTPS Endpoint

Agentverse should not register the Tailscale URL directly. Expose the public-facing MatChalendar backend with a public HTTPS tunnel.

Ngrok example:

```powershell
ngrok http 8000
```

Cloudflare Tunnel example:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

Register this Agentverse endpoint:

```text
https://<public-tunnel-host>/api/agentverse/plan
```

The endpoint accepts `prompt`, `user_prompt`, `message`, `input`, `query`, or `messages[]` and returns compact structured JSON.

## Verify Runtime

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/runtime/status -Method Get
```

The status response intentionally exposes only labels and booleans, not backend URLs or secrets.

## Disable After Hackathon

Turn off the public Agentverse demo:

```text
AGENTVERSE_AGENT_ENABLED=false
```

Stop the ngrok or Cloudflare Tunnel process. Local `/api/plan` remains available for normal development.
