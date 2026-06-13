"""
seed_data.py

Run this ONCE to:
1. Create a Hindsight memory bank for the "Auth Service"
2. Load it with 8 synthetic past incident postmortems

Run with: python seed_data.py
"""

import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = "oncall-copilot-auth-service"

client = Hindsight(
    base_url=os.environ["HINDSIGHT_BASE_URL"],
    api_key=os.environ.get("HINDSIGHT_API_KEY"),
)

# ---------------------------------------------------------------------------
# SYNTHETIC PAST INCIDENTS
# Each one is a "postmortem" written as a single block of text.
# This is the memory the agent will learn from.
# ---------------------------------------------------------------------------

PAST_INCIDENTS = [
    {
        "title": "INC-101: Login failures after deploy v2.14",
        "content": (
            "INCIDENT INC-101: Users started seeing 'Invalid session token' errors "
            "immediately after deploy v2.14 of the Auth Service. Error rate spiked to 18%. "
            "ROOT CAUSE: The new JWT signing key was rotated but the old key was removed "
            "from the verification key set too early, so tokens issued minutes before the "
            "deploy could not be verified. "
            "FIX: Re-added the previous signing key to the verification key set for a "
            "24-hour grace period, then removed it after token expiry. "
            "WHAT DIDN'T WORK: Restarting the auth service pods did not help, since the "
            "key set was loaded from config, not memory. "
            "CUSTOMER MESSAGE USED: 'We identified an issue affecting some users' login "
            "sessions after a recent update. A fix has been deployed and most users should "
            "no longer be affected. If you are still logged out, please log in again.' "
            "TONE NOTE: Customers responded well to a short, plain-language message that "
            "told them exactly what to do (log in again) rather than a vague apology."
        ),
    },
    {
        "title": "INC-102: Auth Service 500 errors - DB connection pool exhausted",
        "content": (
            "INCIDENT INC-102: Auth Service started returning HTTP 500 errors under high "
            "traffic during a marketing campaign. Logs showed 'connection pool exhausted, "
            "timeout waiting for connection'. ROOT CAUSE: The database connection pool size "
            "was set to 10, which was fine for normal traffic but far too small for the "
            "campaign traffic spike (5x normal). FIX: Increased connection pool size to 50 "
            "and added connection pool usage to the monitoring dashboard. WHAT DIDN'T WORK: "
            "Initially the team tried scaling up the number of Auth Service pods, which did "
            "not help because the bottleneck was the shared database connection limit, not "
            "compute. CUSTOMER MESSAGE USED: 'Some users may have experienced login errors "
            "during a period of high traffic. This has been resolved and login should now "
            "work normally. We apologize for the inconvenience.' TONE NOTE: This message "
            "performed well because it acknowledged the issue was traffic-related, which "
            "reduced confusion about whether accounts were compromised."
        ),
    },
    {
        "title": "INC-103: OAuth login broken - third-party provider outage",
        "content": (
            "INCIDENT INC-103: Users could not log in via 'Sign in with Google'. Email/"
            "password login worked fine. ROOT CAUSE: Google's OAuth provider had a partial "
            "outage (confirmed via Google's own status page). This was NOT a bug in our "
            "Auth Service. FIX: No fix needed on our side; issue resolved itself once Google "
            "restored service after about 40 minutes. We added a fallback banner that "
            "suggests email/password login when OAuth providers are down. WHAT DIDN'T WORK: "
            "Restarting our OAuth integration service had no effect since the upstream "
            "provider was down. CUSTOMER MESSAGE USED: 'We are aware that Sign in with "
            "Google is currently unavailable due to an outage on Google's side. As a "
            "workaround, you can sign in using your email and password. We will update this "
            "message once Google resolves the issue.' TONE NOTE: Clearly attributing the "
            "issue to a third party (with evidence) reduced support tickets significantly "
            "compared to a vague 'we are investigating' message."
        ),
    },
    {
        "title": "INC-104: Memory leak causing Auth Service restarts every 2 hours",
        "content": (
            "INCIDENT INC-104: Auth Service pods were restarting every ~2 hours due to "
            "out-of-memory errors, causing brief login interruptions for all users during "
            "each restart. ROOT CAUSE: A session cache was implemented without an eviction "
            "policy, so it grew unbounded and consumed all available memory. FIX: Added a "
            "TTL-based eviction policy (sessions expire from cache after 30 minutes of "
            "inactivity) and added a memory usage alert at 80% threshold. WHAT DIDN'T WORK: "
            "Increasing the pod memory limit only delayed the crash from 2 hours to "
            "roughly 6 hours; it did not fix the underlying leak. CUSTOMER MESSAGE USED: "
            "'Some users may have experienced brief login interruptions over the past few "
            "hours. We have deployed a fix and are continuing to monitor. No user data was "
            "affected.' TONE NOTE: Proactively stating 'no user data was affected' reduced "
            "anxious follow-up questions, especially relevant for an auth-related issue."
        ),
    },
    {
        "title": "INC-105: Rate limiter misconfiguration blocking legitimate logins",
        "content": (
            "INCIDENT INC-105: Users on shared corporate networks (e.g. large offices) "
            "started getting 'Too many login attempts, try again later' errors even on "
            "their first attempt. ROOT CAUSE: The rate limiter was configured per-IP-address "
            "rather than per-account, so many employees behind the same corporate NAT "
            "shared one IP and quickly hit the limit. FIX: Changed rate limiting to be "
            "per-account-plus-IP combined, with a higher threshold for shared IP ranges. "
            "WHAT DIDN'T WORK: Simply raising the global rate limit was tried first but "
            "this significantly increased exposure to credential-stuffing attacks, so it "
            "was reverted. CUSTOMER MESSAGE USED: 'We identified an issue causing login "
            "errors for users on shared office networks. This has been fixed - if you were "
            "affected, please try logging in again.' TONE NOTE: Mentioning 'shared office "
            "networks' specifically helped affected users self-identify quickly."
        ),
    },
    {
        "title": "INC-106: Password reset emails delayed by up to 30 minutes",
        "content": (
            "INCIDENT INC-106: Password reset emails were taking 15-30 minutes to arrive "
            "instead of the usual few seconds. ROOT CAUSE: The email queue worker had "
            "crashed silently two days earlier due to an unhandled exception on a malformed "
            "email address, and emails had been queuing up ever since with no alerting. "
            "FIX: Fixed the unhandled exception (now logs and skips malformed addresses "
            "instead of crashing the worker), restarted the worker to clear the backlog, "
            "and added a queue-depth alert. WHAT DIDN'T WORK: Asking users to 'wait and try "
            "again' did not help since the underlying worker was still down; the queue kept "
            "growing until the worker was fixed. CUSTOMER MESSAGE USED: 'We're aware that "
            "some password reset emails have been delayed. We've resolved the underlying "
            "issue and delayed emails are now being delivered. If you still don't see your "
            "email after 10 minutes, please request a new reset link.' TONE NOTE: Giving a "
            "concrete time threshold (10 minutes) before asking users to retry reduced "
            "duplicate support tickets."
        ),
    },
    {
        "title": "INC-107: Two-factor authentication codes not being accepted",
        "content": (
            "INCIDENT INC-107: Users entering correct 2FA codes were getting 'Invalid code' "
            "errors. ROOT CAUSE: A clock drift issue on two Auth Service servers caused "
            "their system time to be off by 90 seconds, which exceeded the time-based OTP "
            "(TOTP) tolerance window of 60 seconds. FIX: Re-synced server clocks via NTP "
            "and increased the TOTP tolerance window to 90 seconds to add buffer. WHAT "
            "DIDN'T WORK: Telling users to 'wait for a new code' did not help, since the "
            "problem was server-side clock drift, not the user's code generation. CUSTOMER "
            "MESSAGE USED: 'We identified a server issue causing valid two-factor "
            "authentication codes to be rejected. This has been fixed. If you are still "
            "unable to log in, please try generating a new code.' TONE NOTE: Being explicit "
            "that the issue was 'a server issue' (not the user's fault) reduced confused "
            "reports of 'my authenticator app is broken'."
        ),
    },
    {
        "title": "INC-108: Account lockouts after routine password policy update",
        "content": (
            "INCIDENT INC-108: After deploying a new password complexity policy, a number "
            "of existing users were unexpectedly locked out of their accounts. ROOT CAUSE: "
            "The new policy check was incorrectly applied retroactively to existing "
            "sessions during login, locking accounts whose stored passwords did not meet "
            "the new (stricter) complexity rules, even though those passwords were valid "
            "when created. FIX: Changed the policy check to apply only to NEW password "
            "creation/changes, not to validating existing passwords at login, and added a "
            "one-time prompt encouraging (not forcing) affected users to update their "
            "password. WHAT DIDN'T WORK: Manually unlocking individual accounts via support "
            "tickets did not scale - hundreds of users were affected within the first hour. "
            "CUSTOMER MESSAGE USED: 'A recent update incorrectly locked some accounts due "
            "to a password policy change. This has been fixed and affected accounts have "
            "been automatically unlocked. We recommend updating your password for extra "
            "security, but it is not required.' TONE NOTE: Clarifying that updating the "
            "password was 'recommended but not required' prevented a second wave of "
            "confused users trying to force a password change immediately."
        ),
    },
]


def main():
    print(f"Creating bank '{BANK_ID}'...")
    try:
        client.create_bank(
            bank_id=BANK_ID,
            name="On-Call Copilot - Auth Service",
            mission=(
                "I am an on-call engineering assistant for the Auth Service. "
                "I help engineers diagnose incidents quickly using past incident history, "
                "and I help draft customer-facing status updates using the tone and "
                "approach that worked well in similar past incidents."
            ),
            disposition={"skepticism": 2, "literalism": 3, "empathy": 4},
        )
        print("Bank created.")
    except Exception as e:
        print(f"Bank may already exist, continuing... ({e})")

    print(f"Seeding {len(PAST_INCIDENTS)} past incidents...")
    items = [
        {"content": inc["content"], "context": "incident_postmortem"}
        for inc in PAST_INCIDENTS
    ]
    client.retain_batch(bank_id=BANK_ID, items=items, retain_async=False)
    print("Done! Memory bank is seeded and ready.")


if __name__ == "__main__":
    main()
