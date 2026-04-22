from rest_framework import serializers
from app.models import Benchmark, LLMModel, Provider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["id", "name", "website"]


class BenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benchmark
        fields = ["id", "name", "created_at", "updated_at"]


class LLMModelSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(read_only=True)
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=Provider.objects.all(), source="provider", write_only=True
    )
    arena_elo_score = serializers.SerializerMethodField()

    class Meta:
        model = LLMModel
        fields = [
            "id",
            "provider",
            "provider_id",
            "name",
            "description",
            "context_window",
            "input_price_per_1m",
            "output_price_per_1m",
            "arena_elo_score",
            "release_date",
            "is_open_source",
            "created_at",
            "updated_at",
        ]

    def get_arena_elo_score(self, obj):
        score = getattr(obj, "arena_elo_score", None)
        return int(score) if score is not None else None


class LLMModelListSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(read_only=True)
    arena_elo_score = serializers.SerializerMethodField()

    class Meta:
        model = LLMModel
        fields = [
            "id",
            "provider",
            "name",
            "context_window",
            "input_price_per_1m",
            "output_price_per_1m",
            "arena_elo_score",
            "release_date",
            "is_open_source",
        ]

    def get_arena_elo_score(self, obj):
        score = getattr(obj, "arena_elo_score", None)
        return int(score) if score is not None else None
