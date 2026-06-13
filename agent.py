"""
agent.py

Core agent logic:
- recall_similar_incidents(): pulls relevant past incidents from Hindsight
- generate_without_memory(): generic response, simulating a memory-less agent
- generate_with_memory(): response that uses recalled past incidents
- save_resolution(): writes the new incident's resolution back into memory
  (this is what makes the agent "learn")
"""

import os
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = "oncall-copilot-auth-service"
MODEL = "openai/gpt-oss-120b"

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])


def _get_hindsight_client():
    """Create a fresh Hindsight client. We create a new one per call (instead
    of one shared global client) to avoid asyncio event-loop conflicts with
    Streamlit's re-run model."""
    return Hindsight(
        base_url=os.environ["HINDSIGHT_BASE_URL"],
        api_key=os.environ.get("HINDSIGHT_API_KEY"),
    )


def recall_similar_incidents(incident_description, max_tokens=600):
    """Search Hindsight memory for incidents related to the new incident."""
    with _get_hindsight_client() as client:
        response = client.recall(
            bank_id=BANK_ID,
            query=incident_description,
            max_tokens=max_tokens,
        )
        return response.results


def _call_groq(prompt: str) -> str:
    completion = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return completion.choices[0].message.content


def generate_without_memory(incident_description: str) -> str:
    """Simulates an agent with NO memory - generic advice only."""
    prompt = f"""You are an on-call engineering assistant for an Auth Service.
You have NO access to any history of past incidents.

NEW INCIDENT REPORT:
{incident_description}

Respond with exactly two sections:

ENGINEER NOTES:
(Generic troubleshooting steps for this type of issue - 3-5 bullet points)

CUSTOMER MESSAGE:
(A short, generic status update suitable for a status page, 2-3 sentences)
"""
    return _call_groq(prompt)


def generate_with_memory(incident_description: str, recalled_memories) -> str:
    """Uses recalled past incidents to give a much more specific response."""
    if recalled_memories:
        memory_text = "\n".join(f"- {m.text}" for m in recalled_memories)
    else:
        memory_text = "(no relevant past incidents found in memory)"

    prompt = f"""You are an on-call engineering assistant for an Auth Service.
You have access to memory of past incidents, shown below.

RELEVANT MEMORY FROM PAST INCIDENTS:
{memory_text}

NEW INCIDENT REPORT:
{incident_description}

Respond with exactly two sections:

ENGINEER NOTES:
(If a past incident closely matches, name it explicitly and explain what the
likely root cause is based on that history, what fix worked before, and what
NOT to try because it didn't work before. If nothing matches well, say so.
3-5 bullet points.)

CUSTOMER MESSAGE:
(A status update for customers. Match the tone and approach that worked well
in similar past incidents, e.g. naming the cause type, giving concrete next
steps, or reassurance about data safety where relevant. 2-3 sentences.)
"""
    return _call_groq(prompt)


def save_resolution(incident_description: str, resolution_summary: str):
    """Writes the resolved incident back into memory so future incidents
    benefit from it. This is the 'learning' step."""
    content = (
        f"INCIDENT: {incident_description}\n"
        f"RESOLUTION: {resolution_summary}"
    )
    with _get_hindsight_client() as client:
        client.retain(
            bank_id=BANK_ID,
            content=content,
            context="incident_postmortem",
        )


def list_all_memories(limit=50):
    """For the 'Memory Browser' view in the UI."""
    with _get_hindsight_client() as client:
        return client.list_memories(bank_id=BANK_ID, limit=limit)
