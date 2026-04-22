from django.db.models import F, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.constants import ARENA_ELO_BENCHMARK_NAME
from app.models import Benchmark, LatestBenchmarkResult, LLMModel
from app.serializers import (
    BenchmarkRunSerializer,
    BenchmarkSerializer,
    LLMModelSerializer,
    LLMModelListSerializer,
)


def _llm_queryset():
    arena_elo_latest = LatestBenchmarkResult.objects.filter(
        llm_model=OuterRef("pk"),
        benchmark__name=ARENA_ELO_BENCHMARK_NAME,
    ).values("score")[:1]
    return LLMModel.objects.select_related("provider").annotate(
        arena_elo_score=Subquery(arena_elo_latest),
    )


@extend_schema(
    summary="Liveness probe",
    description="Returns a static payload used by the frontend healthcheck.",
    responses=OpenApiResponse(
        response={"type": "object", "properties": {"status": {"type": "string"}}},
        examples=[OpenApiExample("ok", value={"status": "ok"})],
    ),
)
@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


class LLMModelListView(generics.ListAPIView):
    queryset = _llm_queryset().order_by(
        F("arena_elo_score").desc(nulls_last=True), "name"
    )
    serializer_class = LLMModelListSerializer


class LLMModelDetailView(generics.RetrieveAPIView):
    queryset = _llm_queryset()
    serializer_class = LLMModelSerializer


class LLMModelCreateView(generics.CreateAPIView):
    queryset = LLMModel.objects.all()
    serializer_class = LLMModelSerializer


class BenchmarkListView(generics.ListAPIView):
    queryset = Benchmark.objects.all()
    serializer_class = BenchmarkSerializer


class BenchmarkDetailView(generics.RetrieveAPIView):
    queryset = Benchmark.objects.all()
    serializer_class = BenchmarkSerializer


class BenchmarkRunCreateView(generics.CreateAPIView):
    # [Claude Note] AllowAny -- per-project decision to defer write auth.
    # Anyone can POST a run; tighten before this service goes public.
    serializer_class = BenchmarkRunSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["benchmark"] = get_object_or_404(
            Benchmark, pk=self.kwargs["pk"]
        )
        return context
