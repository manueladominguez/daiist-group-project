"""
Controlled real-Gemini validation of the integrated product (WP6/WP7 coordination, 28 Nov 2026).

    uv run python eval/controlled_validation/controlled_gemini_validation.py --i-authorise-gemini-calls
    ... --i-authorise-gemini-calls --only B_low_cost     # one case only (1 Gemini request)

USES REAL GEMINI QUOTA: about 16 requests (hard cap 30). Run it only with the team's explicit
authorisation. It is NOT the evaluation (WP4) and NOT production traffic:
    - logs go to a new temporary folder, never to PostgreSQL (LOG_DIR set means files);
    - every record has source = "controlled_test", so the bandit never counts it;
    - LLM_CACHE=off, so nothing is written to the evaluation cache;
    - DAILY_LLM_BUDGET=30 with an empty log folder: the app's own budget refuses call 31;
    - inputs are hand-written (ui/presets.py and one hand-written high-risk reading):
      no data split is read, so the test split stays untouched.
The writing style is forced per case by wrapping bandit.decide inside app (production code is not
changed). Output: a JSON summary without request ids, session tags or keys
(eval/controlled_validation/results_<date>.json). Results of the 28 Nov run: docs/GEMINI_VALIDATION.md.
"""

import argparse
import json
import os
import re
import sys
import tempfile
import time
from datetime import date
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HIGH = {"type": "L", "air_temperature_k": 302.0, "process_temperature_k": 309.9, "rotational_speed_rpm": 2400,
        "torque_nm": 35.0, "tool_wear_min": 215}  # hand-written; component A rates it "high" (p about 0.59)
MAX_CALLS = 30
KEEP = ["case", "arm", "status", "risk_band", "review", "degraded", "degraded_reason", "latency_s", "cost_eur", "tokens",
        "llm", "decision_source", "decision_errors", "writing_warnings", "versions", "decision", "review_reasons",
        "validation_errors", "tools", "cost", "steps", "justification", "ui_ok", "ui_unknown_reason_keys",
        "ui_degraded_banner", "budget_used_after"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--i-authorise-gemini-calls", action="store_true", help="required: the run spends real quota")
    parser.add_argument("--only", default="", help="comma-separated case names to run (default: all)")
    args = parser.parse_args()
    if not args.i_authorise_gemini_calls:
        raise SystemExit("This script spends real Gemini quota. Re-run with --i-authorise-gemini-calls.")
    os.environ.update(LOG_DIR=tempfile.mkdtemp(prefix="maintai-controlled-"), MAINTAI_SOURCE="controlled_test",
                      LLM_CACHE="off", DAILY_LLM_BUDGET=str(MAX_CALLS), DATABASE_URL="")
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    import app  # loads .env (GEMINI_API_KEY); the key is never printed or saved
    import logbook
    from maintai import bandit, llm
    from ui import components as ui
    from ui.presets import PRESETS

    assert logbook.database_url() == "", "must not write to PostgreSQL"
    cases = [("A_out_of_scope", PRESETS["Out of range"], "checklist")]
    cases += [(f"B_low_{a}", PRESETS["Normal operation"], a) for a in ("checklist", "cost", "root_cause")]
    cases += [(f"C_high_{a}", HIGH, a) for a in ("checklist", "cost", "root_cause")]
    cases += [("D_critical_review_cost", PRESETS["Heat dissipation"], "cost"),
              ("E_degraded_no_key", PRESETS["Heat dissipation"], "checklist")]
    if args.only:
        cases = [c for c in cases if c[0] in set(args.only.split(","))]
    real_decide = bandit.decide

    def forced(arm):
        def decide(logs=None, **kw):
            d = real_decide(logs, **kw)
            d.arm = arm
            return d
        return decide

    rows = []
    for name, reading, arm in cases:
        if llm.budget_status()["used"] > MAX_CALLS - 4:
            print(f"Stopped before {name}: budget nearly used")
            break
        key = os.environ.get("GEMINI_API_KEY", "")
        if name.startswith("E_"):
            os.environ["GEMINI_API_KEY"] = ""  # degraded mode on purpose: no key, no call
        app.bandit.decide = forced(arm)
        try:
            rec = app.serve(json.dumps(reading), session_tag="controlled-test")
        finally:
            app.bandit.decide = real_decide
            os.environ["GEMINI_API_KEY"] = key
        row = {k: rec.get(k) for k in KEEP if k in rec} | {"case": name, "budget_used_after": llm.budget_status()["used"]}
        if rec.get("status") == "ok":
            b = rec["outputs"]["component_b"]
            wo, d = b["work_order"], b["work_order"]["draft"]
            row.update(decision={k: d.get(k) for k in ("priority", "action", "failure_mode_addressed", "part_ids",
                                                       "window_id", "requires_human_review")},
                       review_reasons=wo.get("review_reasons"), validation_errors=wo.get("validation_errors"),
                       steps=d.get("steps"), justification=d.get("justification"), cost=wo.get("cost"),
                       tools=[(c.get("name"), c.get("arguments")) for c in b.get("tool_calls", [])])
            html = ui.results(rec)
            row.update(ui_ok=True, ui_unknown_reason_keys=[r for r in wo.get("review_reasons", [])
                                                           if r not in ui.REVIEW_REASONS],
                       ui_degraded_banner="Degraded mode" in unescape(re.sub(r"<[^>]+>", " ", html)))
        else:
            row["ui_ok"] = bool(ui.out_of_scope(rec))
        rows.append(row)
        print(f"{name:24} calls={(rec.get('llm') or {}).get('llm_calls')} degraded={rec.get('degraded')}", flush=True)
        time.sleep(6)  # stay under the client's 12 requests a minute

    suffix = f"_{args.only.replace(',', '-')}" if args.only else ""  # never overwrite the full run
    out = ROOT / "eval" / "controlled_validation" / f"results_{date.today().isoformat()}{suffix}.json"
    out.write_text(json.dumps({"run": {"date": date.today().isoformat(), "type": "controlled_test",
                                       "gemini_requests": llm.budget_status()["used"], "authorised": MAX_CALLS},
                               "cases": rows}, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}; Gemini requests used: {llm.budget_status()['used']}")


if __name__ == "__main__":
    main()
