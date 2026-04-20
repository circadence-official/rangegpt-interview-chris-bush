from rest_framework import serializers
from app.models import Provider, LLMModel


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["id", "name", "website"]


class LLMModelSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(read_only=True)
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=Provider.objects.all(), source="provider", write_only=True
    )

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


class LLMModelListSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(read_only=True)

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
