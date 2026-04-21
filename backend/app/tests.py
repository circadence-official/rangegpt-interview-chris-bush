import pytest
from django.test import TestCase
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
from rest_framework.test import APIClient
from decimal import Decimal


class ProviderModelTest(TestCase):
    def test_create_provider(self):
        provider = Provider.objects.create(
            name="Anthropic",
            website="https://anthropic.com",
        )
        assert provider.name == "Anthropic"
        assert provider.website == "https://anthropic.com"
        assert provider.created_at is not None
        assert str(provider) == "Anthropic"

    def test_provider_name_unique(self):
        Provider.objects.create(name="Anthropic")
        with pytest.raises(Exception):
            Provider.objects.create(name="Anthropic")

    def test_provider_ordering(self):
        Provider.objects.create(name="OpenAI")
        Provider.objects.create(name="Anthropic")
        providers = list(Provider.objects.values_list("name", flat=True))
        assert providers == ["Anthropic", "OpenAI"]


class LLMModelModelTest(TestCase):
    def setUp(self):
        self.provider = Provider.objects.create(
            name="Anthropic",
            website="https://anthropic.com",
        )

    def test_create_llm_model(self):
        model = LLMModel.objects.create(
            provider=self.provider,
            name="Claude Sonnet 4",
            description="Fast and capable model",
            context_window=200000,
            input_price_per_1m="3.0000",
            output_price_per_1m="15.0000",
            release_date=date(2025, 5, 22),
            is_open_source=False,
        )
        assert model.name == "Claude Sonnet 4"
        assert model.provider == self.provider
        assert model.context_window == 200000
        assert model.created_at is not None
        assert model.updated_at is not None
        assert str(model) == "Anthropic - Claude Sonnet 4"

    def test_unique_together_provider_name(self):
        LLMModel.objects.create(
            provider=self.provider,
            name="Claude Sonnet 4",
            description="",
            context_window=200000,
            input_price_per_1m="3.0000",
            output_price_per_1m="15.0000",
            release_date=date(2025, 5, 22),
        )
        with pytest.raises(Exception):
            LLMModel.objects.create(
                provider=self.provider,
                name="Claude Sonnet 4",
                description="",
                context_window=200000,
                input_price_per_1m="3.0000",
                output_price_per_1m="15.0000",
                release_date=date(2025, 5, 22),
            )


class BenchmarkModelTest(TestCase):
    def test_create_benchmark(self):
        benchmark = Benchmark.objects.create(name="MMLU")
        assert benchmark.name == "MMLU"
        assert benchmark.created_at is not None
        assert str(benchmark) == "MMLU"

    def test_benchmark_name_unique(self):
        Benchmark.objects.create(name="MMLU")
        with pytest.raises(Exception):
            Benchmark.objects.create(name="MMLU")


class BenchmarkRunModelTest(TestCase):
    def setUp(self):
        self.benchmark = Benchmark.objects.create(name="MMLU")

    def test_create_run(self):
        run = BenchmarkRun.objects.create(
            benchmark=self.benchmark,
            run_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        assert run.benchmark == self.benchmark
        assert run.run_at == datetime(2026, 1, 1, tzinfo=timezone.utc)

    def test_runs_ordered_newest_first(self):
        BenchmarkRun.objects.create(
            benchmark=self.benchmark,
            run_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        BenchmarkRun.objects.create(
            benchmark=self.benchmark,
            run_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        )
        run_at_values = [r.run_at.month for r in BenchmarkRun.objects.all()]
        assert run_at_values == [3, 1]


class BenchmarkResultModelTest(TestCase):
    def setUp(self):
        self.benchmark = Benchmark.objects.create(name="MMLU")
        self.run = BenchmarkRun.objects.create(
            benchmark=self.benchmark,
            run_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        provider = Provider.objects.create(name="Anthropic")
        self.model = LLMModel.objects.create(
            provider=provider,
            name="Claude Sonnet 4",
            context_window=200000,
            input_price_per_1m="3.0000",
            output_price_per_1m="15.0000",
            release_date=date(2025, 5, 22),
        )

    def test_create_result(self):
        result = BenchmarkResult.objects.create(
            run=self.run,
            llm_model=self.model,
            score=Decimal("87.5000"),
        )
        assert result.score == Decimal("87.5000")
        assert result.run == self.run
        assert result.llm_model == self.model

    def test_result_unique_per_run_and_model(self):
        BenchmarkResult.objects.create(
            run=self.run, llm_model=self.model, score=Decimal("87.5000")
        )
        with pytest.raises(Exception):
            BenchmarkResult.objects.create(
                run=self.run, llm_model=self.model, score=Decimal("88.0000")
            )


class LatestBenchmarkResultModelTest(TestCase):
    def setUp(self):
        self.benchmark = Benchmark.objects.create(name="MMLU")
        self.run = BenchmarkRun.objects.create(
            benchmark=self.benchmark,
            run_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        provider = Provider.objects.create(name="Anthropic")
        self.model = LLMModel.objects.create(
            provider=provider,
            name="Claude Sonnet 4",
            context_window=200000,
            input_price_per_1m="3.0000",
            output_price_per_1m="15.0000",
            release_date=date(2025, 5, 22),
        )
        self.result = BenchmarkResult.objects.create(
            run=self.run, llm_model=self.model, score=Decimal("87.5000")
        )

    def test_create_latest(self):
        latest = LatestBenchmarkResult.objects.create(
            benchmark=self.benchmark,
            llm_model=self.model,
            result=self.result,
            score=self.result.score,
            measured_at=self.run.run_at,
        )
        assert latest.score == Decimal("87.5000")
        assert latest.measured_at == self.run.run_at

    def test_latest_unique_per_benchmark_and_model(self):
        LatestBenchmarkResult.objects.create(
            benchmark=self.benchmark,
            llm_model=self.model,
            result=self.result,
            score=self.result.score,
            measured_at=self.run.run_at,
        )
        with pytest.raises(Exception):
            LatestBenchmarkResult.objects.create(
                benchmark=self.benchmark,
                llm_model=self.model,
                result=self.result,
                score=self.result.score,
                measured_at=self.run.run_at,
            )


class ProviderSerializerTest(TestCase):
    def test_provider_serialization(self):
        from app.serializers import ProviderSerializer

        provider = Provider.objects.create(name="Anthropic", website="https://anthropic.com")
        serializer = ProviderSerializer(provider)
        data = serializer.data
        assert data["id"] == provider.id
        assert data["name"] == "Anthropic"
        assert data["website"] == "https://anthropic.com"


class LLMModelSerializerTest(TestCase):
    def setUp(self):
        self.provider = Provider.objects.create(name="Anthropic", website="https://anthropic.com")
        self.model = LLMModel.objects.create(
            provider=self.provider,
            name="Claude Sonnet 4",
            description="Fast and capable",
            context_window=200000,
            input_price_per_1m="3.0000",
            output_price_per_1m="15.0000",
            release_date=date(2025, 5, 22),
            is_open_source=False,
        )

    def test_detail_serialization_nests_provider(self):
        from app.serializers import LLMModelSerializer

        serializer = LLMModelSerializer(self.model)
        data = serializer.data
        assert data["name"] == "Claude Sonnet 4"
        assert data["provider"]["name"] == "Anthropic"
        assert data["description"] == "Fast and capable"

    def test_list_serialization_omits_description(self):
        from app.serializers import LLMModelListSerializer

        serializer = LLMModelListSerializer(self.model)
        data = serializer.data
        assert data["name"] == "Claude Sonnet 4"
        assert "description" not in data
        assert data["provider"]["name"] == "Anthropic"


class HealthCheckViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check_returns_200(self):
        response = self.client.get("/api/health/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class LLMModelListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        provider = Provider.objects.create(name="Anthropic")
        LLMModel.objects.create(
            provider=provider,
            name="Claude Sonnet 4",
            description="Fast and capable",
            context_window=200000,
            input_price_per_1m="3.0000",
            output_price_per_1m="15.0000",
            release_date=date(2025, 5, 22),
        )

    def test_list_returns_200_with_models(self):
        response = self.client.get("/api/models/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Claude Sonnet 4"
        assert "description" not in data[0]


class LLMModelDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        provider = Provider.objects.create(name="Anthropic")
        self.model = LLMModel.objects.create(
            provider=provider,
            name="Claude Sonnet 4",
            description="Fast and capable",
            context_window=200000,
            input_price_per_1m="3.0000",
            output_price_per_1m="15.0000",
            release_date=date(2025, 5, 22),
        )

    def test_detail_returns_200_with_description(self):
        response = self.client.get(f"/api/models/{self.model.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Claude Sonnet 4"
        assert data["description"] == "Fast and capable"
        assert data["provider"]["name"] == "Anthropic"

    def test_detail_returns_404_for_missing(self):
        response = self.client.get("/api/models/99999/")
        assert response.status_code == 404


class LLMModelCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider = Provider.objects.create(name="Anthropic")

    def test_create_model_with_valid_data(self):
        response = self.client.post(
            "/api/models/create/",
            {
                "provider_id": self.provider.id,
                "name": "Claude Opus 4",
                "description": "Most capable model",
                "context_window": 200000,
                "input_price_per_1m": "15.0000",
                "output_price_per_1m": "75.0000",
                "release_date": "2025-05-22",
                "is_open_source": False,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Claude Opus 4"
        assert LLMModel.objects.count() == 1

    def test_create_model_missing_required_field(self):
        response = self.client.post(
            "/api/models/create/",
            {"name": "Incomplete Model"},
            format="json",
        )
        assert response.status_code == 400


class SeedCommandTest(TestCase):
    def test_seed_creates_providers_and_models(self):
        from django.core.management import call_command

        call_command("seed")
        assert Provider.objects.count() >= 5
        assert LLMModel.objects.count() >= 15

    def test_seed_populates_arena_elo_benchmark(self):
        from django.core.management import call_command

        call_command("seed")
        arena = Benchmark.objects.get(name=ARENA_ELO_BENCHMARK_NAME)
        assert LatestBenchmarkResult.objects.filter(benchmark=arena).count() >= 15

    def test_seed_is_idempotent(self):
        from django.core.management import call_command

        call_command("seed")
        models_first = LLMModel.objects.count()
        runs_first = BenchmarkRun.objects.count()
        results_first = BenchmarkResult.objects.count()
        call_command("seed")
        assert LLMModel.objects.count() == models_first
        assert BenchmarkRun.objects.count() == runs_first
        assert BenchmarkResult.objects.count() == results_first


class LLMModelListArenaEloTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        provider = Provider.objects.create(name="TestProvider")
        self.model_a = LLMModel.objects.create(
            provider=provider,
            name="Model A",
            context_window=100000,
            input_price_per_1m="1.0000",
            output_price_per_1m="5.0000",
            release_date=date(2025, 1, 1),
        )
        self.model_b = LLMModel.objects.create(
            provider=provider,
            name="Model B",
            context_window=100000,
            input_price_per_1m="1.0000",
            output_price_per_1m="5.0000",
            release_date=date(2025, 1, 1),
        )
        self.model_c = LLMModel.objects.create(
            provider=provider,
            name="Model C",
            context_window=100000,
            input_price_per_1m="1.0000",
            output_price_per_1m="5.0000",
            release_date=date(2025, 1, 1),
        )
        arena = Benchmark.objects.create(name=ARENA_ELO_BENCHMARK_NAME)
        run = BenchmarkRun.objects.create(
            benchmark=arena,
            run_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        for model, score in ((self.model_a, 1100), (self.model_b, 1300)):
            result = BenchmarkResult.objects.create(
                run=run, llm_model=model, score=Decimal(score)
            )
            LatestBenchmarkResult.objects.create(
                benchmark=arena,
                llm_model=model,
                result=result,
                score=Decimal(score),
                measured_at=run.run_at,
            )

    def test_list_orders_by_arena_elo_desc_nulls_last(self):
        response = self.client.get("/api/models/")
        assert response.status_code == 200
        names = [m["name"] for m in response.json()]
        assert names == ["Model B", "Model A", "Model C"]

    def test_list_exposes_arena_elo_from_benchmark_cache(self):
        response = self.client.get("/api/models/")
        scores = {m["name"]: m["arena_elo_score"] for m in response.json()}
        assert scores["Model A"] == 1100
        assert scores["Model B"] == 1300
        assert scores["Model C"] is None

    def test_detail_exposes_arena_elo_from_benchmark_cache(self):
        response = self.client.get(f"/api/models/{self.model_a.id}/")
        assert response.status_code == 200
        assert response.json()["arena_elo_score"] == 1100
