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
