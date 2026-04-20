from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.models import LLMModel
from app.serializers import LLMModelSerializer, LLMModelListSerializer


@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok"})


class LLMModelListView(generics.ListAPIView):
    queryset = LLMModel.objects.select_related("provider").all()
    serializer_class = LLMModelListSerializer


class LLMModelDetailView(generics.RetrieveAPIView):
    queryset = LLMModel.objects.select_related("provider").all()
    serializer_class = LLMModelSerializer


class LLMModelCreateView(generics.CreateAPIView):
    queryset = LLMModel.objects.all()
    serializer_class = LLMModelSerializer
