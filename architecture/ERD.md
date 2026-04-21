# Data Model ERD

Current state of the persistence layer in `backend/app/models.py`.
Regenerate this diagram whenever a model or field changes (see
`CLAUDE.md` → *Architecture artifacts*).

```mermaid
erDiagram
    Provider ||--o{ LLMModel : "has many"

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
        int            arena_elo_score "nullable, default ordering desc"
        date           release_date
        bool           is_open_source "default false"
        datetime       created_at "auto_now_add"
        datetime       updated_at "auto_now"
    }
```

## Constraints and indexes

- `Provider.name` is unique.
- `LLMModel` has `unique_together = (provider, name)`.
- `LLMModel` default ordering is `-arena_elo_score`.
