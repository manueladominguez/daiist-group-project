# Controlled validation with real Gemini (28 Nov 2026)

**What this is:** a small, controlled check of the integrated product (WP1 risk model + WP2 tools + WP3 agent + WP6 bandit + WP7 interface) with **real** Gemini answers, before the feedback campaign. Run by Manuela (coordination) with Claude Code.

**What this is not:** it is **not the evaluation** (WP4 evaluates `eval/cases.csv`, the test split and the judge) and **not production traffic**. It does not change the pre-registered success criteria and gives no result for them. Nine requests with hand-written readings are evidence that the pieces work together and of problems to fix, not performance estimates.

## 1. Simulated checks vs real checks

| | Simulated Gemini (27–28 Nov) | **Real Gemini (this document)** |
|---|---|---|
| What | WP3's fake Gemini (`tests/test_agent.py`, 26 tests) plus our compatibility checks with the bandit and the interface (`docs/INTEGRATION_CHECKLIST.md`, 6.5) | 9 requests through the real `app.serve()` path: 16 Gemini requests |
| Shows | The code paths, guardrails and fallbacks behave as designed, for answers we scripted | How the real model answers: wording per style, tool use, decisions, tokens, cost, latency, rate limits |
| Quota | 0 | 16 of the 30 authorised by Manuela |

## 2. Isolation (how the run avoided contaminating anything)

- Run locally with Manuela's own key, logs in a **temporary local folder** (never PostgreSQL); nothing from those logs is committed.
- Every record has `source = controlled_test`: the bandit excludes it (checked: 0 eligible as logged).
- `LLM_CACHE=off`: nothing written to the evaluation cache.
- `DAILY_LLM_BUDGET=30` with an empty log folder: the app itself would refuse call 31.
- **Hand-written readings only** (`ui/presets.py` and one hand-written high-risk reading). No data split was read, so the test split and the campaign scenarios are untouched.
- No rating was given.

Reproduction (spends about 16 Gemini requests; needs authorisation): `uv run python eval/controlled_validation/controlled_gemini_validation.py --i-authorise-gemini-calls`. The summary of the 28 Nov run (decisions, texts, tokens, latency; no request ids, session tags or keys) is `eval/controlled_validation/results_2026-11-28.json`.

## 3. Results

Model `gemini-3.5-flash-lite`, prompts `agent-v1`, risk model `maintai-gb-sigmoid-v1`, policy `ts-v1`. Cost is the paid-tier equivalent (the free tier is used).

| Case | Style | Gemini requests | Latency | Cost | Priority · action · mode · part · window | Review |
|---|---|---|---|---|---|---|
| Out of scope (air 365 K) | — | 0 | 0.01 s | 0 € | Refused before any model call | — |
| Low risk (p = 0.17%) | checklist | 1 | 5.5 s (first request) | 0.00042 € | P4 · monitor · none · – · – | No |
| Low risk | cost | 1 | 2.3 s | 0.00049 € | P4 · monitor · none · – · – | No |
| Low risk | root_cause | 1 | 1.2 s | 0.00068 € | P4 · monitor · none · – · – | No |
| High risk (p = 59%) | checklist | 3 | 4.7 s | 0.00232 € | P2 · replace_tool · TWF · P-TW-001 · W-2026-12-02-A | Yes (agent) |
| High risk | cost | 3 | 4.1 s | 0.00259 € | P2 · replace_tool · TWF · P-TW-001 · W-2026-12-02-A | Yes (agent) |
| High risk | root_cause | 3 | 3.4 s | 0.00281 € | P2 · replace_tool · TWF · P-TW-001 · W-2026-12-02-A | **No** |
| Critical, heat dissipation (p = 93%) | cost | 3 + 1 retry | **31.0 s** | 0.00225 € | P1 · cooling_check · HDF · P-CL-010 · no window in the next 8 h | Yes (critical + agent) |
| Critical, no key (degraded on purpose) | checklist | 0 | 0.06 s | 0 € | Rule-based template, "Degraded mode" banner | Yes |

Tokens per request: about 1,100–1,300 for a low-risk note; about 4,800–5,400 for a three-call order (thinking tokens only in the tool call).

### What worked

- **Out of scope** refused with 0 calls; **degraded mode** without a key: template order, banner, 0 calls.
- **Tools and guardrails:** the agent asked for parts, a window of the right length (2 h) and the policy; parts and windows exist in the simulated plant data; no invented id; no validation error; the critical order went to review by rule.
- **Writing styles differ visibly:** short imperative steps (checklist); breakdown-to-preventive ratio and planned downtime first (cost); indicators and mechanism (root_cause).
- **Action, priority, failure mode, part and window were identical in the three styles** of the high-risk reading, in three independent requests.
- **Interface:** every real answer renders (App result, agent trace, review reasons); no unknown review reason.
- **RL eligibility:** as logged, 0 records are eligible (controlled test). Read as production traffic (in memory only, nothing written), the 7 handled, non-degraded orders would be eligible and the degraded and out-of-scope ones would not.

### Problems found

1. **Economic faithfulness error (WP3, must be fixed before the campaign).** In the low-risk note with the `cost` style, the model wrote *"A breakdown would cost about 4.0 times more than this intervention, which needs 1.5 h of planned downtime"*. Both numbers are invented: a monitor order has no intervention cost or downtime, and the low-risk call does not receive the cost facts, but the `cost` style prompt asks for them. 18 of the 30 campaign scenarios are low risk, so this would penalise the `cost` style for a bug and fail the judge's faithfulness item. The code check (`writing_warnings`) did not catch it. Fix proposed to WP3: no ratio or downtime in low-risk notes, then bump the prompt version to `agent-v2` (no ratings exist under `agent-v1`, so nothing is lost).
2. **Variable human-review request.** For the same high-risk reading, the agent requested a review in two requests and not in the third (root_cause). The style is not the cause: the decision call never sees it, and the deterministic review rules (critical risk, out of range, uncertainty band, failed validation) are unaffected. It is variability of the model between independent requests, even at temperature 0. Consequence: the protected decision is the same *within* a request, but the agent's optional review request is not stable *across* requests. Either documented as a limitation or stabilised by WP3.
3. **Latency after a rate limit (429).** After about 13 Gemini requests in one minute, Gemini answered 429; the client retried once and succeeded, but the request took 31 s. During the campaign at most two participants should work at the same time (`docs/RL_CAMPAIGN_KIT.md`).

Minor observations (no action needed now): the root_cause low-risk note had five steps where the low-risk prompt asks for one to three; the rule-based template asks for a 1-hour window even when the action needs 2 hours (degraded mode only).

## 4. Status and pending

- Real-Gemini compatibility: **checked on 9 requests**; problems 1–3 recorded above.
- Pending: WP3's fix and `agent-v2`; a short re-check of the fix after deployment (one low-risk reading with the `cost` style); memory and CPU on Render with the real agent; the evaluation (WP4).
