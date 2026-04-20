import pytest
from django.test import TestCase
from app.models import Provider, LLMModel
from datetime import date
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
            arena_elo_score=1320,
            release_date=date(2025, 5, 22),
            is_open_source=False,
        )
        assert model.name == "Claude Sonnet 4"
        assert model.provider == self.provider
        assert model.context_window == 200000
        assert model.created_at is not None
        assert model.updated_at is not None
        assert str(model) == "Anthropic - Claude Sonnet 4"

    def test_llm_model_ordering_by_elo(self):
        LLMModel.objects.create(
            provider=self.provider,
            name="Model A",
            description="",
            context_window=100000,
            input_price_per_1m="1.0000",
            output_price_per_1m="5.0000",
            arena_elo_score=1100,
            release_date=date(2025, 1, 1),
        )
        LLMModel.objects.create(
            provider=self.provider,
            name="Model B",
            description="",
            context_window=100000,
            input_price_per_1m="1.0000",
            output_price_per_1m="5.0000",
            arena_elo_score=1300,
            release_date=date(2025, 1, 1),
        )
        models = list(LLMModel.objects.values_list("name", flat=True))
        assert models == ["Model B", "Model A"]

    def test_llm_model_nullable_elo(self):
        model = LLMModel.objects.create(
            provider=self.provider,
            name="New Model",
            description="",
            context_window=100000,
            input_price_per_1m="1.0000",
            output_price_per_1m="5.0000",
            arena_elo_score=None,
            release_date=date(2025, 1, 1),
        )
        assert model.arena_elo_score is None

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
            arena_elo_score=1320,
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
            arena_elo_score=1320,
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
            arena_elo_score=1320,
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
                "arena_elo_score": 1350,
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

    def test_seed_is_idempotent(self):
        from django.core.management import call_command

        call_command("seed")
        count_first = LLMModel.objects.count()
        call_command("seed")
        count_second = LLMModel.objects.count()
        assert count_first == count_second
