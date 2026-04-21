from django.db import models


class Provider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LLMModel(models.Model):
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="models"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    context_window = models.IntegerField()
    input_price_per_1m = models.DecimalField(max_digits=10, decimal_places=4)
    output_price_per_1m = models.DecimalField(max_digits=10, decimal_places=4)
    arena_elo_score = models.IntegerField(null=True, blank=True)
    release_date = models.DateField()
    is_open_source = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-arena_elo_score"]
        unique_together = ["provider", "name"]

    def __str__(self):
        return f"{self.provider.name} - {self.name}"


class Benchmark(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BenchmarkRun(models.Model):
    benchmark = models.ForeignKey(
        Benchmark, on_delete=models.CASCADE, related_name="runs"
    )
    run_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-run_at"]
        indexes = [
            models.Index(fields=["benchmark", "-run_at"]),
        ]

    def __str__(self):
        return f"{self.benchmark.name} @ {self.run_at.isoformat()}"


class BenchmarkResult(models.Model):
    run = models.ForeignKey(
        BenchmarkRun, on_delete=models.CASCADE, related_name="results"
    )
    llm_model = models.ForeignKey(
        LLMModel, on_delete=models.CASCADE, related_name="benchmark_results"
    )
    score = models.DecimalField(max_digits=9, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["run", "llm_model"]
        indexes = [
            models.Index(fields=["llm_model", "run"]),
        ]

    def __str__(self):
        return f"{self.llm_model} · {self.run} · {self.score}"


class LatestBenchmarkResult(models.Model):
    # Cache of the newest BenchmarkResult per (benchmark, model); kept in
    # sync by the run-submission view so leaderboard/summary reads are O(1).
    benchmark = models.ForeignKey(
        Benchmark, on_delete=models.CASCADE, related_name="latest_results"
    )
    llm_model = models.ForeignKey(
        LLMModel,
        on_delete=models.CASCADE,
        related_name="latest_benchmark_results",
    )
    result = models.ForeignKey(
        BenchmarkResult, on_delete=models.CASCADE, related_name="+"
    )
    score = models.DecimalField(max_digits=9, decimal_places=4)
    measured_at = models.DateTimeField()

    class Meta:
        unique_together = ["benchmark", "llm_model"]
        indexes = [
            models.Index(fields=["benchmark", "-score"]),
            models.Index(fields=["llm_model", "benchmark"]),
        ]

    def __str__(self):
        return f"{self.llm_model} · {self.benchmark} · {self.score}"
