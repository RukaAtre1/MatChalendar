import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

register_chat_agent(
    "MatChalendar",
    "https://swaddling-autopilot-chaperone.ngrok-free.dev/submit",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"],        
    ),
)