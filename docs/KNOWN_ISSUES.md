# Known issues

Triagepath — issues observed but not yet fixed. Each entry describes the
symptom, how to reproduce, and the suspected cause. These are tracked so the
fixes can be scheduled rather than rediscovered.

## 1. Human-review resume over HTTP returns deep_dive instead of the final report

**Symptom:** `POST /api/review {action:"approve"}` over HTTP returns a `final`
whose `step` is `deep_dive` (re-scored tasks, no `report`), instead of the
executive report.

**Reproduce:**
```bash
TID=$(curl -s -N -X POST http://localhost:8000/api/analyze/stream \
  -H 'Content-Type: application/json' -d '{"preset":"lumea","llm_provider":"mock"}' \
  | grep -m1 '"thread_id"' | sed 's/.*"thread_id": "\([^"]*\)".*/\1/')
curl -s -X POST http://localhost:8000/api/review \
  -H 'Content-Type: application/json' -d "{\"thread_id\":\"$TID\",\"action\":\"approve\"}"
# -> final.step == "deep_dive", no "report" key
```

**Works in-process, fails over HTTP:** driving the graph in a single process
(`run_analysis` then `resume_review` with the same runtime) produces the report
correctly. Over HTTP the stream and the review run in separate requests, each
building a fresh runtime, and the SQLite checkpointer does not restore the
human-review interrupt in a way that lets `Command(resume="approve")` advance
to `generate_report`.

**Suspected cause:** `langgraph-checkpoint-sqlite` + a freshly compiled graph
per request; the interrupt state is not resumed cleanly across reloads. Not
fixed by sharing one sqlite connection per path.

**Impact:** the streaming frontend (`web/`) shows an empty "final report"
after Approve in a deployed backend. The UI flow itself (timeline, review
panel, edit re-score) works; only the final approve→report step via HTTP is
affected.

**Suggestion:** investigate reusing a single compiled graph/runtime across
requests in the FastAPI app, or verify the `Command(resume=...)` + sqlite
checkpointer combination against the pinned `langgraph-checkpoint-sqlite==3.1.1`.
