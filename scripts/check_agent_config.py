"""Temporary helper: print agent address from current config."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def strip_quotes(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        return v[1:-1]
    return v

config = {}
for path in (PROJECT_ROOT / ".env", PROJECT_ROOT / ".env.local"):
    if not path.exists():
        continue
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().lstrip("\ufeff")
        v = strip_quotes(v)
        if k and k not in config:
            config[k] = v

seed = config.get("AGENT_SEED", "replace_with_secure_seed")
name = config.get("AGENT_NAME", "MatChalendar Campus Planner Agent")
port = int(config.get("AGENT_PORT", "8001"))
api_key = config.get("AGENTVERSE_API_KEY", "")

print(f"AGENT_NAME   : {name}")
print(f"AGENT_PORT   : {port}")
print(f"AGENT_SEED   : {'<placeholder>' if seed == 'replace_with_secure_seed' else f'<set, len={len(seed)}>'}")
print(f"AGENTVERSE_KEY: {'<set>' if api_key else '<not set>'}")

# Get address
try:
    from uagents import Agent
    agent = Agent(name=name, seed=seed, port=port)
    print(f"Agent address: {agent.address}")
except Exception as e:
    print(f"Error computing address: {e}")
