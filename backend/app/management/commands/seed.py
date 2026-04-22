from django.core.management.base import BaseCommand
from django.db import transaction
from app.constants import ARENA_ELO_BENCHMARK_NAME
from app.models import (
    Benchmark,
    BenchmarkResult,
    BenchmarkRun,
    LatestBenchmarkResult,
    LLMModel,
    Provider,
)
from datetime import date, datetime, timezone
from decimal import Decimal


SEED_DATA = {
    "Anthropic": {
        "website": "https://anthropic.com",
        "models": [
            {
                "name": "Claude Opus 4",
                "description": "Most capable model for complex reasoning, analysis, and multi-step tasks. Excels at nuanced understanding and generation.",
                "context_window": 200000,
                "input_price_per_1m": "15.0000",
                "output_price_per_1m": "75.0000",
                "arena_elo_score": 1350,
                "release_date": date(2025, 5, 22),
                "is_open_source": False,
            },
            {
                "name": "Claude Sonnet 4",
                "description": "Balanced performance and speed. Strong at coding, analysis, and conversational tasks.",
                "context_window": 200000,
                "input_price_per_1m": "3.0000",
                "output_price_per_1m": "15.0000",
                "arena_elo_score": 1320,
                "release_date": date(2025, 5, 22),
                "is_open_source": False,
            },
            {
                "name": "Claude Haiku 3.5",
                "description": "Fastest and most compact model. Ideal for high-throughput, low-latency tasks.",
                "context_window": 200000,
                "input_price_per_1m": "0.8000",
                "output_price_per_1m": "4.0000",
                "arena_elo_score": 1180,
                "release_date": date(2024, 10, 29),
                "is_open_source": False,
            },
        ],
    },
    "OpenAI": {
        "website": "https://openai.com",
        "models": [
            {
                "name": "GPT-4o",
                "description": "Flagship multimodal model with strong text, vision, and audio capabilities.",
                "context_window": 128000,
                "input_price_per_1m": "2.5000",
                "output_price_per_1m": "10.0000",
                "arena_elo_score": 1290,
                "release_date": date(2024, 5, 13),
                "is_open_source": False,
            },
            {
                "name": "GPT-4o mini",
                "description": "Small, affordable model for lightweight tasks. Good cost-performance ratio.",
                "context_window": 128000,
                "input_price_per_1m": "0.1500",
                "output_price_per_1m": "0.6000",
                "arena_elo_score": 1140,
                "release_date": date(2024, 7, 18),
                "is_open_source": False,
            },
            {
                "name": "o1",
                "description": "Reasoning-focused model that thinks before responding. Strong at math, science, and coding.",
                "context_window": 200000,
                "input_price_per_1m": "15.0000",
                "output_price_per_1m": "60.0000",
                "arena_elo_score": 1340,
                "release_date": date(2024, 12, 17),
                "is_open_source": False,
            },
            {
                "name": "o3-mini",
                "description": "Cost-effective reasoning model. Balances thinking capability with speed.",
                "context_window": 200000,
                "input_price_per_1m": "1.1000",
                "output_price_per_1m": "4.4000",
                "arena_elo_score": 1300,
                "release_date": date(2025, 1, 31),
                "is_open_source": False,
            },
        ],
    },
    "Google": {
        "website": "https://deepmind.google",
        "models": [
            {
                "name": "Gemini 2.5 Pro",
                "description": "Advanced multimodal model with a 1M token context window. Strong at long-document analysis.",
                "context_window": 1000000,
                "input_price_per_1m": "1.2500",
                "output_price_per_1m": "10.0000",
                "arena_elo_score": 1310,
                "release_date": date(2025, 3, 25),
                "is_open_source": False,
            },
            {
                "name": "Gemini 2.0 Flash",
                "description": "Fast and efficient model for high-volume workloads. Good at agentic tasks.",
                "context_window": 1000000,
                "input_price_per_1m": "0.1000",
                "output_price_per_1m": "0.4000",
                "arena_elo_score": 1210,
                "release_date": date(2025, 2, 5),
                "is_open_source": False,
            },
            {
                "name": "Gemini 1.5 Pro",
                "description": "Previous generation flagship with 2M token context window.",
                "context_window": 2000000,
                "input_price_per_1m": "1.2500",
                "output_price_per_1m": "5.0000",
                "arena_elo_score": 1260,
                "release_date": date(2024, 2, 15),
                "is_open_source": False,
            },
        ],
    },
    "Meta": {
        "website": "https://ai.meta.com",
        "models": [
            {
                "name": "Llama 4 Scout",
                "description": "Open-source model with 10M token context window. Designed for agentic and long-context tasks.",
                "context_window": 10000000,
                "input_price_per_1m": "0.0000",
                "output_price_per_1m": "0.0000",
                "arena_elo_score": 1250,
                "release_date": date(2025, 4, 5),
                "is_open_source": True,
            },
            {
                "name": "Llama 3.1 405B",
                "description": "Largest open-source Llama model. Competitive with proprietary models on many benchmarks.",
                "context_window": 128000,
                "input_price_per_1m": "0.0000",
                "output_price_per_1m": "0.0000",
                "arena_elo_score": 1200,
                "release_date": date(2024, 7, 23),
                "is_open_source": True,
            },
            {
                "name": "Llama 3.3 70B",
                "description": "Efficient open-source model. Strong performance at 70B parameter scale.",
                "context_window": 128000,
                "input_price_per_1m": "0.0000",
                "output_price_per_1m": "0.0000",
                "arena_elo_score": 1180,
                "release_date": date(2024, 12, 6),
                "is_open_source": True,
            },
        ],
    },
    "Mistral": {
        "website": "https://mistral.ai",
        "models": [
            {
                "name": "Mistral Large",
                "description": "Flagship model from Mistral. Strong at multilingual tasks and European languages.",
                "context_window": 128000,
                "input_price_per_1m": "2.0000",
                "output_price_per_1m": "6.0000",
                "arena_elo_score": 1190,
                "release_date": date(2024, 11, 18),
                "is_open_source": False,
            },
            {
                "name": "Mixtral 8x22B",
                "description": "Open-source mixture-of-experts model. Efficient inference with strong performance.",
                "context_window": 64000,
                "input_price_per_1m": "0.0000",
                "output_price_per_1m": "0.0000",
                "arena_elo_score": 1150,
                "release_date": date(2024, 4, 17),
                "is_open_source": True,
            },
        ],
    },
}


BENCHMARK_CATALOG = [
    {
        "name": "MMLU",
        "score_offset": 50.0,
    },
    {
        "name": "HumanEval",
        "score_offset": 45.0,
    },
    {
        "name": "GPQA Diamond",
        "score_offset": 20.0,
    },
]

SEED_RUN_TIMESTAMPS = [
    datetime(2025, 10, 1, tzinfo=timezone.utc),
    datetime(2026, 1, 1, tzinfo=timezone.utc),
    datetime(2026, 4, 1, tzinfo=timezone.utc),
]


def _synthesize_score(elo, offset, run_index):
    # Higher ELO → higher benchmark score; later runs tick up slightly.
    # Clamp the top end so strong models don't blow past 100%.
    base = max(0.0, (elo - 1000) / 10.0) + offset
    return round(min(99.5, base + run_index * 1.5), 2)


class Command(BaseCommand):
    help = "Seed the database with LLM provider and model data"

    @transaction.atomic
    def handle(self, *args, **options):
        arena_elo, _ = Benchmark.objects.get_or_create(
            name=ARENA_ELO_BENCHMARK_NAME,
        )

        models_with_elo = []
        for provider_name, provider_data in SEED_DATA.items():
            provider, created = Provider.objects.get_or_create(
                name=provider_name,
                defaults={"website": provider_data["website"]},
            )
            action = "Created" if created else "Already exists"
            self.stdout.write(f"  {action}: Provider '{provider_name}'")

            for model_data in provider_data["models"]:
                elo_score = model_data.get("arena_elo_score")
                model_fields = {
                    k: v for k, v in model_data.items() if k != "arena_elo_score"
                }
                model, created = LLMModel.objects.get_or_create(
                    provider=provider,
                    name=model_fields["name"],
                    defaults=model_fields,
                )
                action = "Created" if created else "Already exists"
                self.stdout.write(f"    {action}: {model_fields['name']}")

                if elo_score is not None:
                    self._seed_arena_elo_score(arena_elo, model, elo_score)
                    models_with_elo.append((model, elo_score))

        self._seed_additional_benchmarks(models_with_elo)

        total_providers = Provider.objects.count()
        total_models = LLMModel.objects.count()
        total_benchmarks = Benchmark.objects.count()
        total_results = BenchmarkResult.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {total_providers} providers, "
                f"{total_models} models, {total_benchmarks} benchmarks, "
                f"{total_results} benchmark results"
            )
        )

    def _seed_arena_elo_score(self, benchmark, model, score):
        run, _ = BenchmarkRun.objects.get_or_create(
            benchmark=benchmark,
            run_at=model.updated_at,
        )
        result, _ = BenchmarkResult.objects.get_or_create(
            run=run,
            llm_model=model,
            defaults={"score": score},
        )
        LatestBenchmarkResult.upsert_for_result(result)

    def _seed_additional_benchmarks(self, models_with_elo):
        for catalog in BENCHMARK_CATALOG:
            benchmark, _ = Benchmark.objects.get_or_create(
                name=catalog["name"],
            )
            for run_index, run_at in enumerate(SEED_RUN_TIMESTAMPS):
                run, _ = BenchmarkRun.objects.get_or_create(
                    benchmark=benchmark,
                    run_at=run_at,
                )
                for model, elo in models_with_elo:
                    score = _synthesize_score(
                        elo, catalog["score_offset"], run_index
                    )
                    result, _ = BenchmarkResult.objects.get_or_create(
                        run=run,
                        llm_model=model,
                        defaults={"score": Decimal(str(score))},
                    )
                    LatestBenchmarkResult.upsert_for_result(result)
