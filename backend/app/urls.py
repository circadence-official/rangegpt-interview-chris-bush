from django.urls import path
from app.views import (
    health_check,
    BenchmarkDetailView,
    BenchmarkLeaderboardView,
    BenchmarkListView,
    BenchmarkRunCreateView,
    LLMModelListView,
    LLMModelDetailView,
    LLMModelCreateView,
)

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("models/", LLMModelListView.as_view(), name="model-list"),
    path("models/create/", LLMModelCreateView.as_view(), name="model-create"),
    path("models/<int:pk>/", LLMModelDetailView.as_view(), name="model-detail"),
    path("benchmarks/", BenchmarkListView.as_view(), name="benchmark-list"),
    path(
        "benchmarks/<int:pk>/",
        BenchmarkDetailView.as_view(),
        name="benchmark-detail",
    ),
    path(
        "benchmarks/<int:pk>/runs/",
        BenchmarkRunCreateView.as_view(),
        name="benchmark-run-create",
    ),
    path(
        "benchmarks/<int:pk>/leaderboard/",
        BenchmarkLeaderboardView.as_view(),
        name="benchmark-leaderboard",
    ),
]
