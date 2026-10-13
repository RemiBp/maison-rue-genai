MAISON RUE · CUSTOMER SERVICE
HEC MSc DSAIB, Generative AI, Case 01.

A drafting assistant for Maison Rue's support team. It reads an enquiry,
uses only the supplied policies and orders, and prepares a reply for a
person to review. Nothing is sent, refunded or approved by the app.

Online: https://maison-rue-genai.vercel.app

TEAM
Rémi Barbier: prototype, data setup, tests and documentation.
Pauline Perrotton: test cases and response validation.

RUN LOCALLY
Requires Python 3 and an authenticated Codex CLI account.
python3 server.py
Open http://127.0.0.1:8524

TESTS
python3 -m unittest test_workflow test_server     (14 tests)
python3 run_evaluation.py                          (12 cases)
Results on the 12 development cases: assistant 12/12, template 3/12,
after a content review with Codex. These are development results: the
prompt was adjusted after the first run, and no independent support
review has been done. Cost and time saved are not measured.

CLOUD VERSION
vercel/public: interface and appendix.
vercel/api, vercel/lib: server code and supplied facts.
Model: openai/gpt-4.1 through Vercel AI Gateway. No credentials included.
cd vercel && npm ci && node --test test-cloud.mjs   (7 tests)
The 12/12 above comes from the local version; the cloud model has not
been evaluated on the 12 cases.

DATA
knowledge.json: policies P1–P4 and orders A101–A103 from the case.
cases.json: M1–M5 from the case, V6–V12 added variations.
expected.json: expected behaviour, never shown to the model.
evaluation.json, audit.json: raw outputs and review results.

LIMITS
Photos are not analysed. No carrier tracking or CRM connection.
Support staff review every draft; the manager approves refunds and exceptions.
