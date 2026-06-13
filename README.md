# 🚨 On-Call Copilot

**An AI incident-response assistant that learns from every production incident — powered by [Hindsight](https://hindsight.vectorize.io/) memory.**

Built for the *AI Agents That Learn Using Hindsight* hackathon.

---

## 🧩 The Problem

When production breaks, two things happen badly, every time:

- **Engineers** waste time re-discovering fixes for incidents that have already happened before, because the knowledge lives in scattered postmortem docs nobody re-reads.
- **Support/comms teams** write customer-facing status updates from scratch, with inconsistent tone, even when a near-identical incident happened last month.

Both of these are **memory problems**.

## 💡 The Solution

On-Call Copilot is an AI agent for an "Auth Service" on-call rotation. For every new incident, it produces **two outputs**:

1. **Engineer Notes** — diagnosis and fix steps
2. **Customer Message** — a status update, in the tone that worked best for similar past incidents

The core feature is a live **side-by-side comparison**:

| Without Memory | With Hindsight Memory |
|---|---|
| Generic troubleshooting advice | Names the exact past incident this resembles |
| Generic "we're investigating" message | Specific root cause + what worked / didn't work before |
| No learning | Customer message matches the tone that reduced complaints last time |

After resolving an incident, you can **teach the agent** — saving the resolution back into Hindsight's memory so the next similar incident is handled even better.

---

## ✨ Features

- 🧠 **Memory-powered recall** — every new incident triggers a semantic search over past incident postmortems stored in Hindsight
- 🎯 **Memory Match Confidence gauge** — visualizes how strongly a new incident matches existing knowledge (New Pattern → Partial Match → Strong Match)
- 📊 **Memory Browser** — donut chart of memory types, bar chart of most-referenced past incidents, and a live "memory growth" chart for the session
- 🎨 **4 color themes** — Midnight Red, Ocean Blue, Forest Emerald, Sunset Violet
- ✍️ **Live learning loop** — resolve a new incident and watch the agent recall it on the next similar one
- 📋 **6 demo incident scenarios** covering JWT key rotation, DB connection pool exhaustion, OAuth outages, rate limiting, email delays, and 2FA clock drift

---

## 🛠️ How Hindsight Memory Is Used

- **`retain()`** — 8 synthetic past incident postmortems (symptoms, root cause, fix, what *didn't* work, and the customer message tone that worked) are seeded into a Hindsight memory bank. New resolutions are also `retain()`-ed after each incident.
- **`recall()`** — for every new incident, the agent searches the memory bank for semantically related past incidents and observations.
- The recalled context is injected into the LLM prompt, allowing the agent to:
  - Name the specific past incident a new one resembles
  - State what fix worked (and what didn't) last time
  - Reuse the tone/approach from past customer communications

This is what powers the "Without Memory vs With Memory" comparison — same LLM, same incident, radically different quality of response once memory is involved.

---

## 🧰 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (Python)
- **LLM**: [Groq](https://groq.com/) (`openai/gpt-oss-120b`)
- **Memory**: [Hindsight](https://hindsight.vectorize.io/) (Vectorize)
- **Charts**: Plotly

---

## 🚀 Running Locally

### 1. Clone and set up environment
```bash
git clone https://github.com/shrutig-blip/on-call-copilot.git
cd on-call-copilot
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. Add API keys
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_hindsight_api_key
```

### 3. Seed the memory bank (run once)
```bash
python seed_data.py
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
on-call-copilot/
├── app.py          # Streamlit UI
├── agent.py        # Hindsight recall/retain + Groq LLM logic
├── seed_data.py    # Seeds 8 synthetic past incident postmortems
├── requirements.txt
└── .env            # API keys (not committed)
```

---

## 🎬 Demo Flow

1. Pick a demo incident from the sidebar (e.g. "500 errors during flash sale traffic spike")
2. Click **Analyze Incident** — see the Without Memory vs With Memory comparison, plus the Memory Match Confidence gauge
3. Check the **Memories Recalled** section to see exactly which past incident informed the response
4. Try a **custom incident** with no historical match — the agent flags it as a "New Pattern"
5. Resolve it via **Resolve & Teach the Agent** — the memory bank grows
6. Run a similar incident again — the agent now recalls what it just learned

---

## 🔮 Future Improvements

- Multiple services (not just Auth Service), each with its own memory bank
- Slack/PagerDuty integration for real incident ingestion
- Automatic postmortem drafting from resolved tickets
- `reflect()`-based reasoning for more agentic incident triage
