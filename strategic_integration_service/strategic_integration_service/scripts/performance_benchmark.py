#!/usr/bin/env python3
"""Performance benchmark CLI for Strategic Integration Service.

Usage:
    sis-benchmark --help
    sis-benchmark --extractor l2 --runs 3
    sis-benchmark --comparison --cache-warmup
    sis-benchmark --queries --output benchmark_results.json
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import click
import structlog

from ..core.config import Settings
from ..extractors.l2_initiatives import L2InitiativeExtractor
from ..extractors.memory_optimized_extractor import compare_memory_strategies
from ..extractors.performance_l2_initiatives import PerformanceL2InitiativeExtractor
from ..utils.performance_benchmark import ExtractionBenchmark, benchmark_jira_queries
from ..utils.performance_jira_client import PerformanceJiraClient

logger = structlog.get_logger(__name__)


@click.command()
@click.option(
    "--extractor",
    type=click.Choice(["l2", "current", "all"]),
    default="l2",
    help="Which extractor to benchmark",
)
@click.option(
    "--runs",
    type=int,
    default=3,
    help="Number of benchmark runs",
)
@click.option(
    "--comparison",
    is_flag=True,
    help="Compare standard vs performance extractors",
)
@click.option(
    "--cache-warmup",
    is_flag=True,
    help="Warm cache before benchmarking",
)
@click.option(
    "--queries",
    is_flag=True,
    help="Benchmark individual Jira queries",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file for benchmark results (JSON)",
)
@click.option(
    "--max-results",
    type=int,
    default=100,
    help="Maximum results for extraction tests",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--memory-strategies",
    is_flag=True,
    help="Compare memory optimization strategies",
)
def main(
    extractor: str,
    runs: int,
    comparison: bool,
    cache_warmup: bool,
    queries: bool,
    output: str,
    max_results: int,
    verbose: bool,
    memory_strategies: bool,
):
    """Run performance benchmarks for Strategic Integration Service."""

    # Configure logging
    if verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

    click.echo("🚀 Strategic Integration Service Performance Benchmark")
    click.echo("=" * 60)

    try:
        settings = Settings()
        click.echo(f"📊 Configuration loaded - Cache: {settings.enable_caching}")

        benchmark_results = {}

        if queries:
            benchmark_results["query_benchmarks"] = run_query_benchmarks(settings)

        if memory_strategies:
            benchmark_results["memory_strategies"] = run_memory_strategy_comparison(
                settings, max_results
            )

        if comparison:
            benchmark_results["extractor_comparison"] = run_extractor_comparison(
                settings, runs, cache_warmup, max_results
            )
        elif extractor:
            benchmark_results["extractor_benchmark"] = run_single_extractor_benchmark(
                settings, extractor, runs, cache_warmup, max_results
            )

        # Output results
        if output:
            output_path = Path(output)
            with output_path.open("w") as f:
                json.dump(benchmark_results, f, indent=2, default=str)
            click.echo(f"📁 Results saved to: {output_path}")
        else:
            display_results(benchmark_results)

        click.echo("\n✅ Benchmarking completed successfully!")

    except Exception as e:
        click.echo(f"❌ Benchmark failed: {e}", err=True)
        if verbose:
            logger.exception("Benchmark error")
        sys.exit(1)


def run_query_benchmarks(settings: Settings) -> Dict[str, Any]:
    """Run Jira query performance benchmarks."""
    click.echo("\n🔍 Running Jira Query Benchmarks...")

    client = PerformanceJiraClient(settings)

    # Define test queries
    test_queries = [
        {
            "name": "l2_small",
            "jql": f'project = PI AND division in ("{settings.l2_division_filter}") AND type = L2',
            "max_results": 50,
        },
        {
            "name": "l2_medium",
            "jql": f'project = PI AND division in ("{settings.l2_division_filter}") AND type = L2',
            "max_results": 100,
        },
        {
            "name": "l2_large",
            "jql": f'project = PI AND division in ("{settings.l2_division_filter}") AND type = L2',
            "max_results": 200,
        },
    ]

    results = benchmark_jira_queries(client, test_queries, warmup_runs=1, test_runs=3)

    click.echo("✅ Query benchmarks completed")
    return results


def run_extractor_comparison(
    settings: Settings, runs: int, cache_warmup: bool, max_results: int
) -> Dict[str, Any]:
    """Compare standard vs performance extractors."""
    click.echo(f"\n⚖️  Running Extractor Comparison ({runs} runs)...")

    benchmark = ExtractionBenchmark()

    # Create extractors
    standard_extractor = L2InitiativeExtractor(settings)
    performance_extractor = PerformanceL2InitiativeExtractor(settings)

    # Warm cache if requested
    if cache_warmup:
        click.echo("🔥 Warming cache...")
        performance_extractor.warm_extraction_cache()

    extractors = [standard_extractor, performance_extractor]

    results = benchmark.compare_extractors(
        extractors,
        extraction_method="extract",
    )

    click.echo("✅ Extractor comparison completed")
    return results


def run_single_extractor_benchmark(
    settings: Settings, extractor_type: str, runs: int, cache_warmup: bool, max_results: int
) -> Dict[str, Any]:
    """Run benchmark on a single extractor type."""
    click.echo(f"\n🎯 Benchmarking {extractor_type} extractor ({runs} runs)...")

    benchmark = ExtractionBenchmark()

    if extractor_type == "l2":
        extractor = PerformanceL2InitiativeExtractor(settings)

        if cache_warmup:
            click.echo("🔥 Warming cache...")
            extractor.warm_extraction_cache()

        results = []
        for i in range(runs):
            click.echo(f"🏃 Run {i + 1}/{runs}")
            result = benchmark.benchmark_extraction(extractor, "extract")
            results.append(result)

    else:
        raise ValueError(f"Unsupported extractor type: {extractor_type}")

    summary = benchmark.get_summary()

    click.echo("✅ Single extractor benchmark completed")
    return {
        "extractor_type": extractor_type,
        "runs": runs,
        "results": [r.to_dict() for r in benchmark.get_results()],
        "summary": summary,
    }


def display_results(results: Dict[str, Any]) -> None:
    """Display benchmark results in a user-friendly format."""
    click.echo("\n📊 BENCHMARK RESULTS")
    click.echo("=" * 50)

    for category, data in results.items():
        click.echo(f"\n📋 {category.replace('_', ' ').title()}")
        click.echo("-" * 30)

        if category == "extractor_comparison":
            display_comparison_results(data)
        elif category == "extractor_benchmark":
            display_single_benchmark_results(data)
        elif category == "query_benchmarks":
            display_query_results(data)
        elif category == "memory_strategies":
            display_memory_results(data)


def display_comparison_results(data: Dict[str, Any]) -> None:
    """Display extractor comparison results."""
    summary = data.get("summary", {})

    if "fastest" in summary:
        fastest = summary["fastest"]
        slowest = summary["slowest"]
        improvement = summary.get("performance_improvement", 1)

        click.echo(f"🏆 Fastest: {fastest['extractor']} ({fastest['duration']:.3f}s)")
        click.echo(f"🐌 Slowest: {slowest['extractor']} ({slowest['duration']:.3f}s)")
        click.echo(f"⚡ Performance Improvement: {improvement:.2f}x")

    for extractor, result in data.get("results", {}).items():
        if result["success"]:
            benchmark = result["benchmark"]
            click.echo(f"\n{extractor}:")
            click.echo(f"  ⏱️  Duration: {benchmark['duration_seconds']:.3f}s")
            if benchmark.get("memory_delta_mb"):
                click.echo(f"  🧠 Memory: {benchmark['memory_delta_mb']:.1f}MB")


def display_single_benchmark_results(data: Dict[str, Any]) -> None:
    """Display single extractor benchmark results."""
    summary = data.get("summary", {})

    click.echo(f"🎯 Extractor: {data.get('extractor_type', 'unknown')}")
    click.echo(f"🏃 Runs: {data.get('runs', 0)}")

    if summary:
        click.echo(f"⏱️  Average Time: {summary.get('average_time_seconds', 0):.3f}s")
        click.echo(f"⚡ Min Time: {summary.get('min_time_seconds', 0):.3f}s")
        click.echo(f"🐌 Max Time: {summary.get('max_time_seconds', 0):.3f}s")
        click.echo(f"✅ Success Rate: {summary.get('success_rate', 0) * 100:.1f}%")


def display_query_results(data: Dict[str, Any]) -> None:
    """Display query benchmark results."""
    query_results = data.get("query_results", {})

    for query_name, stats in query_results.items():
        click.echo(f"\n🔍 {query_name}:")
        click.echo(f"  ⏱️  Avg Time: {stats.get('average_duration', 0):.3f}s")
        click.echo(
            f"  📊 Results: {
                stats.get(
                    'result_counts',
                    [0])[0] if stats.get('result_counts') else 0}"
        )
        click.echo(f"  ✅ Success: {stats.get('successful_runs', 0)}/{stats.get('runs', 0)}")


def run_memory_strategy_comparison(settings: Settings, max_results: int) -> Dict[str, Any]:
    """Run memory optimization strategy comparison."""
    click.echo(f"\n🧠 Running Memory Strategy Comparison (max {max_results} results)...")

    results = compare_memory_strategies(settings, max_results)

    click.echo("✅ Memory strategy comparison completed")
    return results


def display_memory_results(data: Dict[str, Any]) -> None:
    """Display memory optimization results."""
    strategy_results = data.get("strategy_results", {})
    summary = data.get("comparison_summary", {})

    for strategy, result in strategy_results.items():
        if result["success"]:
            memory_report = result["memory_report"]
            click.echo(f"\n🧠 {strategy.title()} Strategy:")
            click.echo(f"  📊 Initiatives: {result['initiative_count']}")
            click.echo(f"  🏔️  Peak Memory: {memory_report['peak_mb']:.1f}MB")
            click.echo(f"  📈 Memory Growth: {memory_report.get('peak_growth_mb', 0):.1f}MB")
        else:
            click.echo(
                f"\n❌ {strategy.title()} Strategy: Failed - {result.get('error', 'Unknown error')}"
            )

    if "most_memory_efficient" in summary:
        efficient = summary["most_memory_efficient"]
        click.echo(f"\n🏆 Most Memory Efficient: {efficient['strategy'].title()}")
        click.echo(f"  Peak Memory: {efficient['peak_memory_mb']:.1f}MB")


if __name__ == "__main__":
    main()
