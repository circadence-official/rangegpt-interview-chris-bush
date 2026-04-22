from django.db.models import F, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from app.constants import ARENA_ELO_BENCHMARK_NAME
from app.llm import LLMUnavailable, generate_insight
from app.models import Benchmark, BenchmarkResult, LatestBenchmarkResult, LLMModel
from app.serializers import (
    BenchmarkResultHistorySerializer,
    BenchmarkRunSerializer,
    BenchmarkSerializer,
    BenchmarkSummaryEntrySerializer,
    InsightSerializer,
    LeaderboardEntrySerializer,
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


class LLMModelBenchmarkResultsPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class LLMModelBenchmarkSummaryView(generics.ListAPIView):
    serializer_class = BenchmarkSummaryEntrySerializer
    pagination_class = None

    def get_queryset(self):
        model = get_object_or_404(LLMModel, pk=self.kwargs["pk"])
        return (
            LatestBenchmarkResult.objects.filter(llm_model=model)
            .select_related("benchmark")
            .order_by("benchmark__name")
        )


class LLMModelBenchmarkResultsView(generics.ListAPIView):
    serializer_class = BenchmarkResultHistorySerializer
    pagination_class = LLMModelBenchmarkResultsPagination

    def get_queryset(self):
        model = get_object_or_404(LLMModel, pk=self.kwargs["pk"])
        qs = (
            BenchmarkResult.objects.filter(llm_model=model)
            .select_related("run", "run__benchmark")
            .order_by("run__run_at", "id")
        )
        benchmark_id = self.request.query_params.get("benchmark")
        if benchmark_id:
            qs = qs.filter(run__benchmark_id=benchmark_id)
        return qs


class BenchmarkListView(generics.ListAPIView):
    queryset = Benchmark.objects.all()
    serializer_class = BenchmarkSerializer


class BenchmarkDetailView(generics.RetrieveAPIView):
    queryset = Benchmark.objects.all()
    serializer_class = BenchmarkSerializer


class BenchmarkLeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardEntrySerializer

    def get_queryset(self):
        benchmark = get_object_or_404(Benchmark, pk=self.kwargs["pk"])
        return (
            LatestBenchmarkResult.objects.filter(benchmark=benchmark)
            .select_related("llm_model__provider")
            .order_by("-score", "llm_model__name")
        )


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


def _model_insight_prompt(model, summary_rows) -> str:
    specs = [
        f"Model: {model.provider.name} {model.name}",
        f"Context window: {model.context_window:,} tokens",
        f"Input price: ${model.input_price_per_1m} per 1M tokens",
        f"Output price: ${model.output_price_per_1m} per 1M tokens",
        f"Released: {model.release_date}",
        f"Open source: {'yes' if model.is_open_source else 'no'}",
    ]
    if summary_rows:
        specs.append("")
        specs.append("Latest benchmark scores:")
        for row in summary_rows:
            specs.append(f"- {row.benchmark.name}: {row.score}")
    return (
        "You are an AI analyst writing for engineers evaluating LLMs. "
        "In 3-4 short sentences, describe this model's strengths, likely "
        "use cases, and notable tradeoffs. Be concrete and cite the specs "
        "below. Do not use markdown.\n\n"
        + "\n".join(specs)
    )


def _compare_prompt(model_a, rows_a, model_b, rows_b) -> str:
    def describe(model, rows):
        lines = [
            f"{model.provider.name} {model.name}:",
            f"  context: {model.context_window:,} tokens",
            f"  input ${model.input_price_per_1m}/1M, output ${model.output_price_per_1m}/1M",
            f"  released {model.release_date}; open source: {'yes' if model.is_open_source else 'no'}",
        ]
        if rows:
            lines.append("  scores:")
            for row in rows:
                lines.append(f"    {row.benchmark.name}: {row.score}")
        return "\n".join(lines)

    return (
        "You are an AI analyst helping engineers choose between two LLMs. "
        "In 4-5 short sentences, identify where each model wins, who should "
        "pick which, and any meaningful tradeoffs. Be concrete and cite the "
        "specs below. Do not use markdown.\n\n"
        + describe(model_a, rows_a)
        + "\n\n"
        + describe(model_b, rows_b)
    )


class LLMModelInsightView(APIView):
    @extend_schema(responses=InsightSerializer)
    def get(self, request, pk):
        model = get_object_or_404(_llm_queryset(), pk=pk)
        summary_rows = list(
            LatestBenchmarkResult.objects.filter(llm_model=model)
            .select_related("benchmark")
            .order_by("benchmark__name")
        )
        prompt = _model_insight_prompt(model, summary_rows)
        try:
            result = generate_insight(
                prompt=prompt, subject=f"model:{model.pk}"
            )
        except LLMUnavailable as exc:
            return Response({"detail": str(exc)}, status=503)
        return Response(
            {
                "text": result.text,
                "llm_model": result.llm_model,
                "cached": result.cached,
            }
        )


class ComparisonInsightView(APIView):
    @extend_schema(responses=InsightSerializer)
    def get(self, request):
        a_raw = request.query_params.get("a")
        b_raw = request.query_params.get("b")
        if not a_raw or not b_raw:
            return Response(
                {"detail": "Provide 'a' and 'b' model IDs."}, status=400
            )
        try:
            a_id, b_id = int(a_raw), int(b_raw)
        except ValueError:
            return Response(
                {"detail": "Model IDs must be integers."}, status=400
            )
        if a_id == b_id:
            return Response(
                {"detail": "Model IDs must be distinct."}, status=400
            )

        queryset = _llm_queryset()
        model_a = get_object_or_404(queryset, pk=a_id)
        model_b = get_object_or_404(queryset, pk=b_id)

        def rows_for(model):
            return list(
                LatestBenchmarkResult.objects.filter(llm_model=model)
                .select_related("benchmark")
                .order_by("benchmark__name")
            )

        prompt = _compare_prompt(
            model_a, rows_for(model_a), model_b, rows_for(model_b)
        )
        subject = f"compare:{min(a_id, b_id)}:{max(a_id, b_id)}"
        try:
            result = generate_insight(prompt=prompt, subject=subject)
        except LLMUnavailable as exc:
            return Response({"detail": str(exc)}, status=503)
        return Response(
            {
                "text": result.text,
                "llm_model": result.llm_model,
                "cached": result.cached,
            }
        )
