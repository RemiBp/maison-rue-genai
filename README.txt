MAISON RUE · CUSTOMER SERVICE
HEC MSc DSAIB, Case 01, 13 October 2026. A student drafting assistant.

STATUS
Local prototype works with the authenticated Codex CLI account.
English site deployed: https://maison-rue-genai.vercel.app
Cloud inference was verified on 13 October with a delivery enquiry for A102.
The recorded video demonstrates the local Codex version; its scores and timings
remain local development evidence, not a benchmark of the cloud model.


TEAM
Rémi Barbier: prototype, sources, tests and documentation prepared with Codex.
Pauline Perrotton: test cases and response validation.
Team: Rémi Barbier and Pauline Perrotton. Case allows 1–3 students.

LOCAL RUN
Python 3 and Codex CLI installed and authenticated.
codex login status
python3 server.py
Open http://127.0.0.1:8524
No additional Python dependencies. Each teammate uses their own model account.

LOCAL CHECKS
python3 -m unittest test_workflow test_server
python3 run_evaluation.py
python3 build_appendix_en.py
Fourteen Python tests passed. Twelve synthetic development cases were reviewed
with Codex: assistant 12/12, template 3/12. Not independent human acceptance.
The prompt was improved after the first run, so this is not an unseen test set.
The final local batch took 113.7 seconds including CLI startup. Human time
savings and monetary cost are not measured. Raw outputs and token usage remain
in evaluation.json. Do not apply these local results to the cloud model.

CLOUD SOURCE
vercel/public contains the English interface and appendix.
vercel/api and vercel/lib contain the Node server code and supplied facts.
Cloud model: openai/gpt-4.1-mini through Vercel AI Gateway, with Vercel OIDC
resolved at request time. No credentials are bundled in this archive.
cd vercel
npm ci
node --test test-cloud.mjs
Seven Node tests passed, including baseline parity with all twelve original
cases, source checks and visible provider failure without silent fallback.
Link the project to your own Vercel account and activate your own model access.

DATA AND RESPONSIBILITIES
knowledge.json reproduces only the supplied P1–P4 policies and A101–A103 snapshot.
M1–M5 are supplied messages. V6–V12 are labelled fictional variations.
The model never sees expected.json. Exact source quotations are validated.
A source check does not prove every customer-facing sentence is correct.
Support staff must review drafts; managers approve exceptions and refunds.
All next steps are proposed. No outgoing message, refund or payment is executed.
Photos are not analysed and no live carrier integration exists.

VIDEO AND SUBMISSION
Two required items: a 3–5 minute demo video and solution/evidence appendix.
The final v2 MP4 is 3:29, 1920×1080, with narration and captions. The video
README reports real recorded local runs for M5, V8 and M3, labelled shortened
loading intervals. Listen through once
before submitting. The video files are separate from the solution archive.
The deadline supplied by Rémi is today at 18:00 Paris time.
Nothing has been submitted or messaged to classmates or the professor.
