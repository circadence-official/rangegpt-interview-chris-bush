from django.db import transaction
from rest_framework import serializers
from app.models import (
    Benchmark,
    BenchmarkResult,
    BenchmarkRun,
    LatestBenchmarkResult,
    LLMModel,
    Provider,
)


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


class BenchmarkResultInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenchmarkResult
        fields = ["id", "llm_model", "score", "created_at"]
        read_only_fields = ["id", "created_at"]


class BenchmarkRunSerializer(serializers.ModelSerializer):
    results = BenchmarkResultInlineSerializer(many=True)

    class Meta:
        model = BenchmarkRun
        fields = [
            "id",
            "benchmark",
            "run_at",
            "results",
            "created_at",
        ]
        read_only_fields = ["id", "benchmark", "created_at"]

    def validate_results(self, value):
        if not value:
            raise serializers.ValidationError(
                "A run must include at least one result."
            )
        model_ids = [r["llm_model"].id for r in value]
        if len(model_ids) != len(set(model_ids)):
            raise serializers.ValidationError(
                "Duplicate llm_model entries in results."
            )
        return value

    def create(self, validated_data):
        results_data = validated_data.pop("results")
        benchmark = self.context["benchmark"]
        with transaction.atomic():
            run = BenchmarkRun.objects.create(
                benchmark=benchmark, **validated_data
            )
            for result_data in results_data:
                result = BenchmarkResult.objects.create(
                    run=run, **result_data
                )
                LatestBenchmarkResult.upsert_for_result(result)
        return run


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
