# Backend Take-Home Task (Senior)

## Context

You have 1 hour to work on this task. You may use AI coding assistants, install any packages, and restructure the code as you see fit. Be prepared for a 10-minute presentation afterward.

Our evaluation team runs benchmark suites against the models in our leaderboard on a recurring cadence. A long-standing client just asked — on a tight turnaround — for those results to be exposed through our API alongside each model: per-benchmark scores, how they've evolved across runs, and how models stack up against each other. We don't currently have a way to attach evaluation results to a model or to compare them in a meaningful way. Close this gap so we can demo it to the client this week.

## Core Requirements

### As an evaluation engineer, I want to attach benchmark results to the models in our catalog, so that I can see how performance changes between runs.

- [ ] A new benchmark result — tied to a specific model, benchmark, and run — can be persisted through the API.
- [ ] Re-submitting a result for a model on the same benchmark preserves prior history rather than overwriting it.
- [ ] Retrieving results for a single model returns them in chronological order, with enough metadata to distinguish runs.
- [ ] The data shape accommodates multiple distinct benchmarks without a schema change each time a new one is added.

### As a product manager preparing a client update, I want a leaderboard view per benchmark, so that I can show which models are currently ahead on the evaluations our customers care about.

- [ ] Given a benchmark, the API returns the models that have participated, ranked by their most recent score on that benchmark.
- [ ] Models that have never been evaluated on the benchmark are distinguishable from models that have scored zero.
- [ ] Response time stays reasonable as the number of models and historical runs grows well beyond the current seed data.

### As a reviewer comparing models at a glance, I want a consolidated performance summary for a single model across every benchmark it has participated in, so that I don't have to stitch the view together from multiple requests.

- [ ] One request returns a model's current score on each benchmark it has been evaluated on, along with the timestamp of that score.
- [ ] The endpoint remains responsive when a model has accumulated many historical runs across many benchmarks.

## Stretch Goals

- Introduce a blended leaderboard that ranks models using a weighting strategy across multiple benchmarks, and expose how a model's overall rank has moved over time.
- Offer a side-by-side comparison between two models, so a client stakeholder can pass two names and see their trajectories diverge or converge.
- Use a language model to generate a short, plain-English narrative that explains why a model's performance has shifted between runs or relative to its peers. It should be triggerable on demand and produce something a non-technical reader could forward in an email.

## Cross-Stack Questions

1. The React app currently fetches models with a cached query hook and renders a list of cards. If the leaderboard view you've built becomes the primary landing page, what caching and invalidation strategy would you recommend on the frontend, and what affordances from your API would make that strategy easier to implement?
2. Looking at how the app currently handles loading and error states per request, what would you change about your summary endpoint's response shape — or split into multiple endpoints — to give the frontend a better experience when one benchmark's data is slow or unavailable?
3. If a later iteration needed to show near-real-time updates whenever a new benchmark run completes, what pattern would you suggest instead of the current fetch-on-mount approach, and what would that require you to add on the backend?
