from django.urls import path
from app.views import (
    health_check,
    LLMModelListView,
    LLMModelDetailView,
    LLMModelCreateView,
)

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("models/", LLMModelListView.as_view(), name="model-list"),
    path("models/create/", LLMModelCreateView.as_view(), name="model-create"),
    path("models/<int:pk>/", LLMModelDetailView.as_view(), name="model-detail"),
]
