# Data Model ERD

Current state of the persistence layer in `backend/app/models.py`.
Regenerate this diagram whenever a model or field changes (see
`CLAUDE.md` → *Architecture artifacts*).

```mermaid
erDiagram
    Provider ||--o{ LLMModel : "has many"
    Benchmark ||--o{ BenchmarkRun : "has many"
    BenchmarkRun ||--o{ BenchmarkResult : "has many"
    LLMModel ||--o{ BenchmarkResult : "scored on"
    Benchmark ||--o{ LatestBenchmarkResult : "cache rows"
    LLMModel ||--o{ LatestBenchmarkResult : "cache rows"
    BenchmarkResult ||--|| LatestBenchmarkResult : "pinned by"

    Provider {
        bigint       id PK
        varchar(100) name UK "unique"
        url          website "blank ok"
        datetime     created_at "auto_now_add"
    }

    LLMModel {
        bigint         id PK
        bigint         provider_id FK
        varchar(200)   name "unique with provider"
        text           description "blank ok"
        int            context_window
        decimal(10,4)  input_price_per_1m
        decimal(10,4)  output_price_per_1m
        date           release_date
        bool           is_open_source "default false"
        datetime       created_at "auto_now_add"
        datetime       updated_at "auto_now"
    }

    Benchmark {
        bigint       id PK
        varchar(100) name UK "unique"
        datetime     created_at "auto_now_add"
        datetime     updated_at "auto_now"
    }

    BenchmarkRun {
        bigint   id PK
        bigint   benchmark_id FK
        datetime run_at "indexed with benchmark desc"
        datetime created_at "auto_now_add"
    }

    BenchmarkResult {
        bigint        id PK
        bigint        run_id FK
        bigint        llm_model_id FK
        decimal(9,4)  score
        datetime      created_at "auto_now_add"
    }

    LatestBenchmarkResult {
        bigint        id PK
        bigint        benchmark_id FK
        bigint        llm_model_id FK
        bigint        result_id FK "points at newest BenchmarkResult"
        decimal(9,4)  score "denormalized from result"
        datetime      measured_at "denormalized from run.run_at"
    }
```

## Constraints and indexes

- `Provider.name` is unique.
- `LLMModel` has `unique_together = (provider, name)`.
- `Benchmark.name` is unique.
- `BenchmarkRun` default ordering is `-run_at`; index on
  `(benchmark, -run_at)` supports "latest runs for a benchmark" scans.
- `BenchmarkResult` has `unique_together = (run, llm_model)` and an
  index on `(llm_model, run)` for per-model history queries.
- `LatestBenchmarkResult` has `unique_together = (benchmark, llm_model)`
  plus indexes on `(benchmark, -score)` and `(llm_model, benchmark)`.
  It is a materialized cache of the newest `BenchmarkResult` per
  `(benchmark, llm_model)`, maintained on write by
  `LatestBenchmarkResult.upsert_for_result`. Older backfills are
  no-ops so late replays of historical data can never clobber the
  current state.

## Why a cache table

The leaderboard (`GET /api/benchmarks/:id/leaderboard/`) and the
per-model summary (`GET /api/models/:id/benchmark-summary/`) are both
"latest-per-group" reads. Without the cache, each hit would have to
scan all historical results for a benchmark (or model) and collapse
to one row per group before ordering -- cost grows with the history
depth. With the cache, both reads are single indexed lookups that
return exactly the rows the client sees, so cost grows only with the
result size. One extra upsert per write pays for that on every read.
