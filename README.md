# Maison Rue

A customer-service drafting assistant for our HEC MSc DSAIB Generative AI project (Case 01).

**[Try the app](https://maison-rue-genai.vercel.app)** · **[Appendix](https://maison-rue-genai.vercel.app/appendix)** · **[Demo video and solution ZIP](https://github.com/RemiBp/maison-rue-genai/releases/tag/v1.0.0)**

The assistant reads a customer message and drafts a reply using only the four supplied policies and three fictional orders. It answers every question in the message, lists the supporting facts, asks for missing details and proposes who acts next. A person reviews every draft. Nothing is sent or refunded.

## Run locally

Requires Python 3 and an authenticated Codex CLI account.

```sh
python3 server.py
```

Open `http://127.0.0.1:8524/`.

## Tests

```sh
python3 -m unittest test_workflow test_server   # 14 tests
python3 run_evaluation.py                        # 12 cases
cd vercel && npm ci && node --test test-cloud.mjs   # 7 tests
```

On 12 development cases (5 from the brief, 7 added variations), the assistant passed 12/12 and a simple first-topic template 3/12, after a content review with Codex. The prompt was adjusted after the first run and no independent support review has been done, so these are development results. Cost and time saved are not measured. Raw outputs are in `evaluation.json`, the review in `audit.json`.

## Cloud version

`vercel/` holds the online app: `openai/gpt-4.1` through Vercel AI Gateway. The 12/12 result comes from the local version; the cloud model has not been evaluated on the 12 cases. No credentials are included.

## Team

Rémi Barbier: prototype, data setup, tests and documentation.
Pauline Perrotton: test cases and response validation.

Policies and orders are fictional. Photos are not analysed, and there is no carrier tracking or CRM connection.
