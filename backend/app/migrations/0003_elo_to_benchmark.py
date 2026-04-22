from django.db import migrations


def copy_arena_elo_to_benchmark(apps, schema_editor):
    LLMModel = apps.get_model("app", "LLMModel")
    legacy_models = LLMModel.objects.filter(arena_elo_score__isnull=False)
    if not legacy_models.exists():
        return

    Benchmark = apps.get_model("app", "Benchmark")
    BenchmarkRun = apps.get_model("app", "BenchmarkRun")
    BenchmarkResult = apps.get_model("app", "BenchmarkResult")
    LatestBenchmarkResult = apps.get_model("app", "LatestBenchmarkResult")

    arena_elo, _ = Benchmark.objects.get_or_create(name="Arena ELO")

    for model in legacy_models:
        run = BenchmarkRun.objects.create(
            benchmark=arena_elo,
            run_at=model.updated_at,
        )
        result = BenchmarkResult.objects.create(
            run=run,
            llm_model=model,
            score=model.arena_elo_score,
        )
        LatestBenchmarkResult.objects.create(
            benchmark=arena_elo,
            llm_model=model,
            result=result,
            score=model.arena_elo_score,
            measured_at=model.updated_at,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_add_benchmarks"),
    ]

    operations = [
        migrations.RunPython(
            copy_arena_elo_to_benchmark, migrations.RunPython.noop
        ),
        migrations.AlterModelOptions(
            name="llmmodel",
            options={},
        ),
        migrations.RemoveField(
            model_name="llmmodel",
            name="arena_elo_score",
        ),
    ]
