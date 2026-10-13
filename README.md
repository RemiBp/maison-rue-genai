# Maison Rue

A small customer-service assistant for our HEC MSc DSAIB GenAI project.

**[Try the app](https://maison-rue-genai.vercel.app)** · **[Project appendix](https://maison-rue-genai.vercel.app/appendix)** · **[Demo video and solution ZIP](https://github.com/RemiBp/maison-rue-genai/releases/tag/v1.0.0)**

The assistant drafts replies using the four supplied policies and three fictional orders. It handles multiple questions, shows supporting facts separately from the customer reply, asks for missing details and proposes the next responsible person. No message or refund is sent.

## Run locally

Requires Python 3 and an authenticated Codex CLI account.

```sh
codex login status
python3 server.py
```

Open `http://127.0.0.1:8524/`. Each teammate uses their own model account. No credentials are included.

## Checks and evidence

```sh
python3 -m unittest test_workflow test_server
python3 run_evaluation.py
python3 build_appendix_en.py
cd vercel
npm ci
node --test test-cloud.mjs
```

The local development set contains five supplied cases and seven labelled variations. The text inspection performed with Codex judged the assistant 12/12 and the simple first-topic template 3/12. The prompt was improved after inspecting the first run: this is a known development set, not an unseen benchmark or independent human acceptance.

The local 12-case Codex batch took 113.7 seconds, including CLI startup. Monetary cost and human time savings were not measured. `evaluation.json` contains raw outputs and timings; `audit.json` contains the separate text review. These local results do not benchmark the cloud model.

Fourteen Python tests and seven Node tests cover source validation, action ownership, input handling, baseline parity and visible provider failures without a silent fallback. After rerunning inference, inspect the new replies and update the audit before presenting results.

## Cloud version

`vercel/` contains the English app and Node functions. The server uses Vercel AI Gateway and request-time OIDC authentication. Model access and credits belong to the Vercel account deploying it. Never commit `.env` files or `.vercel` credentials.

## Team and submission

Team: Rémi Barbier and Pauline Perrotton. Rémi: prototype, source setup and documentation, prepared with Codex. Pauline: test cases and response validation. The reported scores remain development evidence, not independent human acceptance.

The assignment asks for a 3–5 minute demo video and a solution/evidence appendix. The current v2 video is 3:29 and demonstrates the working local app. The repository and release are shared for team review; they are not an academic submission.

See `README.txt` and `appendix.html` for details. Policies and order records are fictional teaching data. Photos are not analysed, and no live carrier or CRM data is available.
