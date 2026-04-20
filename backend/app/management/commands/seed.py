from django.core.management.base import BaseCommand
from app.models import Provider, LLMModel
from datetime import date


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


class Command(BaseCommand):
    help = "Seed the database with LLM provider and model data"

    def handle(self, *args, **options):
        for provider_name, provider_data in SEED_DATA.items():
            provider, created = Provider.objects.get_or_create(
                name=provider_name,
                defaults={"website": provider_data["website"]},
            )
            action = "Created" if created else "Already exists"
            self.stdout.write(f"  {action}: Provider '{provider_name}'")

            for model_data in provider_data["models"]:
                _, created = LLMModel.objects.get_or_create(
                    provider=provider,
                    name=model_data["name"],
                    defaults=model_data,
                )
                action = "Created" if created else "Already exists"
                self.stdout.write(f"    {action}: {model_data['name']}")

        total_providers = Provider.objects.count()
        total_models = LLMModel.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {total_providers} providers, {total_models} models"
            )
        )
