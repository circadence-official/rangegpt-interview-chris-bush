from django.contrib import admin

from .models import (
    Benchmark,
    BenchmarkResult,
    BenchmarkRun,
    LatestBenchmarkResult,
    LLMModel,
    Provider,
)

admin.site.register(Provider)
admin.site.register(LLMModel)
admin.site.register(Benchmark)
admin.site.register(BenchmarkRun)
admin.site.register(BenchmarkResult)
admin.site.register(LatestBenchmarkResult)
