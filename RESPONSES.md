# Candidate Responses

## Cross-Stack Questions

### Question 1
> The React app currently fetches models with a cached query hook and renders a list of cards. If the leaderboard view you've built becomes the primary landing page, what caching and invalidation strategy would you recommend on the frontend, and what affordances from your API would make that strategy easier to implement?

I'd keep TanStack Query but tune it for the access pattern. Leaderboards move when a run lands, not second to second, so bump `staleTime` to something like 5min and hold `gcTime` longer so returning users hit the cache. Then for write-triggered invalidation, the client that posts a run calls `queryClient.invalidateQueries(['leaderboard', benchmarkId])` in its `onSuccess`, which refetches just the one ranking that changed.

What makes that easier from the API side is a cheap "has anything changed" signal. Two options I'd pick between: a `Last-Modified` header (or ETag) on the leaderboard response so conditional GETs are nearly free when nothing's moved, or a `latest_run_at` field in the payload so a poll can compare a timestamp without pulling the whole ranking. Either lets the client stay fresh without treating every refetch as a full-cost request.

### Question 2
> Looking at how the app currently handles loading and error states per request, what would you change about your summary endpoint's response shape — or split into multiple endpoints — to give the frontend a better experience when one benchmark's data is slow or unavailable?

Right now the summary is one flat array, so one bad or slow benchmark stalls the whole response and the card can't render anything. I'd split it. First endpoint returns a lightweight list of which benchmarks this model has been scored on — just IDs and names. Second endpoint is per (model, benchmark) and returns the score plus `measured_at`. The frontend renders a skeleton row per benchmark from the first call, then fetches each detail in parallel with its own query, its own loading state, its own error boundary. One slow benchmark degrades into a spinner in one cell instead of blocking the whole card.

If I didn't want the fanout, the fallback is keeping a single endpoint but giving each entry its own status (`{benchmark, score, measured_at, error: null}`) so the server can return partial data. That works, but per-entry queries feel cleaner — especially since TanStack Query already handles per-query state well.

Beyond that, adding in skeleton loaders to the UI enhances the waiting UX in a modular way.

### Question 3
> If a later iteration needed to show near-real-time updates whenever a new benchmark run completes, what pattern would you suggest instead of the current fetch-on-mount approach, and what would that require you to add on the backend?

Push, not poll. Server-Sent Events is the right fit — unidirectional, proxy-friendly, no WebSocket ceremony. The frontend opens an `EventSource`, and when a run event comes in it just calls `queryClient.invalidateQueries(['leaderboard', benchmarkId])`. Existing fetch-on-mount stays; SSE just nudges staleness.

On the backend, the run-submission view emits a `run.completed` event after the DB transaction commits — either via a `post_save` signal or an explicit publish in the success branch. A thin `/api/events/` endpoint streams those to subscribed clients. If we're running more than one worker, that needs a Redis pub/sub (or equivalent) so events fan out across processes instead of being trapped in the one that handled the POST.

Fallback if SSE infra is too much right now: drop `staleTime` and poll the leaderboard every 30s. It's blunt, but it gets you most of the perceived freshness with zero new infrastructure, and you can swap in SSE later without touching the component that consumes the query.

## Notes (optional)

A few things worth flagging up front:

- **Run submission is whole-run, not per-result.** `POST /api/benchmarks/:id/runs/` takes `{run_at, results: [...]}` and writes the run plus all results in one transaction. That matches how evals actually execute — you run every candidate model at once under the same conditions — and it makes atomicity natural rather than something I have to bolt on. That said, extending this to allow results to be added via a new API as we go would be relatively trivial as results are represented separately in their own table.
- **`LatestBenchmarkResult` is a materialized cache, not a substitute for history.** Leaderboard and per-model summary both want "latest per group." Without a cache those reads grow with history depth (`DISTINCT ON (llm_model_id)` scanning every row). With the cache they're single-index lookups — O(rows returned), not O(history). The write path keeps it consistent via `upsert_for_result`, and older backfills are explicit no-ops so late replays can't clobber current state.
- **Write endpoints are `AllowAny`.** Inherited from the existing `POST /models/`. Before this ships publicly, the run-submission endpoint needs auth — probably a service token, since the evaluator is internal rather than end-user-facing.
