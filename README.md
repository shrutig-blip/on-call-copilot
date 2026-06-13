# On-Call Copilot - Hackathon Build Guide (1.5 Days, 3 People)

This is a step-by-step plan to take this starter project from zero to a working
demo. Scope has been deliberately kept small so 3 first-time builders can
finish it. Don't add features beyond what's listed here until everything
below works end to end.

## The pitch (memorize this for your demo)

> "When production breaks, engineers waste time re-discovering fixes that were
> already found before, and support teams write customer messages from
> scratch every time. On-Call Copilot gives an AI agent memory of every past
> incident - so the next time something similar happens, it instantly
> recognizes the pattern, tells the engineer exactly what worked (and what
> didn't), and drafts a customer message in the tone that worked best before.
> The more incidents it sees, the smarter it gets."

---

## Role split (do this immediately)

- **Person A - Memory/Backend setup**: accounts, `.env`, run `seed_data.py`,
  verify Hindsight works
- **Person B - Agent logic**: owns `agent.py`, tunes prompts, tests with/without
  memory outputs
- **Person C - UI/Demo**: owns `app.py` (Streamlit), styling, demo script,
  recording the video

You can work in parallel from minute one because the files are already
separated by responsibility.

---

## Step 1: Accounts & setup (everyone, ~30 min)

1. **Hindsight Cloud**: go to https://ui.hindsight.vectorize.io and sign up.
   - After signing up, go to the billing section and apply promo code
     `MEMHACK6` for $50 in free credits.
   - Find your **API base URL** and **API key** (usually shown on a "Quick
     Start" or "API Keys" page in the dashboard).
2. **Groq**: go to https://groq.com, sign up, create an API key (free tier).
3. **Python**: make sure everyone has Python 3.10+ installed
   (`python --version`).
4. **Get this project onto everyone's machine** (e.g. push it to a shared
   GitHub repo immediately - this IS your submission repo).

Each person should then:

```bash
cd oncall-copilot
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Now edit .env and paste in your real GROQ_API_KEY, HINDSIGHT_BASE_URL, HINDSIGHT_API_KEY
```

---

## Step 2: Seed the memory bank (Person A, ~30-45 min)

```bash
python seed_data.py
```

This creates a Hindsight memory bank called `oncall-copilot-auth-service` and
loads it with 8 fake "past incident" postmortems (login bugs, DB pool
exhaustion, OAuth outages, etc.) along with what fixed each one and what
customer message worked.

**Verify it worked**: open a Python shell and try:

```python
from agent import recall_similar_incidents
results = recall_similar_incidents("Users getting 500 errors on login during high traffic")
for r in results:
    print(r.text[:120])
```

You should see it return text mentioning the connection pool incident
(INC-102). If you get an error here, fix it before moving on - everything
else depends on this working.

**Common issues:**
- Wrong `HINDSIGHT_BASE_URL` -> check the exact URL format in your Hindsight
  Cloud dashboard quick-start snippet.
- 401/403 errors -> double check `HINDSIGHT_API_KEY` is set correctly in `.env`.

---

## Step 3: Test the agent logic (Person B, ~1-2 hrs)

Once Step 2 works, test the two generation functions directly:

```python
from agent import recall_similar_incidents, generate_without_memory, generate_with_memory

incident = "Auth Service is returning HTTP 500 errors for ~12% of login requests. Logs show 'connection pool exhausted'. Traffic is 6x normal due to a flash sale."

recalled = recall_similar_incidents(incident)
print("WITHOUT MEMORY:\n", generate_without_memory(incident))
print("\nWITH MEMORY:\n", generate_with_memory(incident, recalled))
```

**What to check:**
- Does the "with memory" version explicitly reference INC-102 (the connection
  pool incident)?
- Does it mention what NOT to do (scaling pods didn't help)?
- Is the customer message tone noticeably better/more specific than the
  "without memory" one?

If the model isn't picking up the memory well, tweak the prompt in
`generate_with_memory()` in `agent.py` - e.g. be more explicit: "If any past
incident matches, you MUST name it by its INC number."

**If Groq gives function-calling/format errors**: we're not using function
calling here (just plain text generation), so this should be low-risk. If
`openai/gpt-oss-120b` is slow or flaky, try `qwen/qwen3-32b` as a fallback -
just change the `MODEL` constant in `agent.py`.

---

## Step 4: Build and test the UI (Person C, in parallel with Step 3)

```bash
streamlit run app.py
```

This gives you:
- A sidebar with 3 pre-written demo incidents + a custom incident box
- A side-by-side "Without Memory" vs "With Memory" comparison
- An expandable list of exactly which memories were recalled
- A "Save Resolution to Memory" button so you can demo the agent *learning*
  live during your presentation
- A Memory Browser tab showing everything currently in the bank

You can build/test this UI with placeholder text before Step 3 is fully
tuned - just make sure `agent.py` functions don't crash (they'll return
*something* even with rough prompts).

---

## Step 5: Polish pass (everyone, last few hours)

Priorities, in order:

1. **Make sure the 3 demo scenarios produce a clear before/after.** This is
   the entire point of the project (25% of your score). If "with memory"
   doesn't look obviously better than "without memory" for at least 2 of the
   3 demo scenarios, fix the prompts or the seed data before doing anything
   else.
2. **Add a 4th "live learning" moment**: during the demo, run a brand-new
   incident scenario that has NO match in memory (so the agent says "no
   similar past incident found"), resolve it using the "Save Resolution"
   button, then immediately re-run a similar incident and show it now
   recalls what you just taught it. This is your "wow" moment.
3. **Basic visual polish**: make sure text doesn't overflow and layout looks
   clean. Don't spend more than 1 hour on styling - Streamlit's defaults are
   fine.
4. **README for your GitHub repo**: explain what the project does, how
   Hindsight is used (retain/recall), and how to run it. Reuse content from
   this file.

---

## Step 6: Record your demo video (last 1-2 hrs)

Script (aim for under 3 minutes):

1. (15s) State the problem: "Engineers and support teams waste time
   re-solving incidents that already happened before."
2. (30s) Show "Without Memory" output for the flash-sale scenario - point out
   it's generic.
3. (45s) Show "With Memory" output for the same scenario - point out it names
   the past incident, says what worked/didn't, and gives a tailored customer
   message.
4. (45s) Show the "live learning" moment from Step 5.2 - a new incident with
   no memory match, resolve it, then show a follow-up incident now recalling
   it.
5. (15s) Briefly show the Memory Browser tab and explain it's powered by
   Hindsight's retain/recall.
6. (10s) Wrap up: what you'd build next with more time (e.g. multiple
   services, Slack integration, automatic postmortem generation).

---

## Submission checklist

- [ ] GitHub repo with this code, clean and documented
- [ ] Demo video recorded
- [ ] Explanation of how Hindsight memory is used (retain past postmortems,
      recall similar incidents, compare with/without memory)
- [ ] Check the official "Hackathon Content Guide" for the additional
      article / social post / video requirements per team member - budget at
      least 1-2 hours for this near the end, it's a separate requirement from
      the demo video

---

## If you have extra time (optional, do NOT start until everything above works)

- Add a second service (e.g. a "Notifications Service") with its own memory
  bank, to show the agent works across services
- Use Hindsight's `reflect()` instead of raw `recall()` + manual prompting,
  for a more "agentic" feel
- Add a simple chart showing memory bank size growing over time
