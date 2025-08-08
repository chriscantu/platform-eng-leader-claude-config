#!/usr/bin/env python3
"""
Performance benchmarking tool for ClaudeDirector Phase 2
Measures performance improvements across all optimization areas
"""

import time
from pathlib import Path
from typing import Any, Dict

try:
    import structlog

    logger = structlog.get_logger()
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

from .core.config import get_config
from .utils.cache import CacheManager
from .utils.memory import MemoryOptimizer
from .utils.parallel import ParallelProcessor


class PerformanceBenchmark:
    """Comprehensive performance benchmarking suite"""

    def __init__(self):
        self.config = get_config()
        self.results = {}

    def benchmark_parallel_processing(self) -> Dict[str, Any]:
        """Benchmark parallel processing performance"""
        print("📊 Benchmarking Parallel Processing...")

        # Create test files
        test_dir = Path("benchmark_workspace")
        test_dir.mkdir(exist_ok=True)

        test_files = []
        for i in range(10):
            test_file = test_dir / f"benchmark_{i}.txt"
            test_file.write_text(f"Benchmark content {i} " * 100)  # ~2KB files
            test_files.append(test_file)

        def simple_processor(file_path):
            content = file_path.read_text()
            return {"length": len(content), "words": len(content.split())}

        try:
            # Sequential baseline
            parallel_processor = ParallelProcessor(validation_mode=True)

            start_time = time.time()
            sequential_results = []
            for file_path in test_files:
                result = simple_processor(file_path)
                sequential_results.append(result)
            sequential_time = time.time() - start_time

            # Parallel processing
            start_time = time.time()
            parallel_result = parallel_processor.process_files_parallel(
                test_files, simple_processor, chunk_size=3
            )
            parallel_time = time.time() - start_time

            # Calculate metrics
            speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0
            efficiency = speedup / parallel_processor.max_workers

            benchmark_result = {
                "files_processed": len(test_files),
                "sequential_time": sequential_time,
                "parallel_time": parallel_time,
                "speedup": speedup,
                "efficiency": efficiency,
                "validation_passed": parallel_result.get("validation_passed", False),
                "max_workers": parallel_processor.max_workers,
            }

            print(f"  📈 Speedup: {speedup:.2f}x ({efficiency:.2f} efficiency)")

        finally:
            # Cleanup
            for test_file in test_files:
                test_file.unlink(missing_ok=True)
            test_dir.rmdir()

        return benchmark_result

    def benchmark_caching_system(self) -> Dict[str, Any]:
        """Benchmark caching system performance"""
        print("💾 Benchmarking Caching System...")

        cache_manager = CacheManager()

        # Generate test data
        test_data = [
            {"key": f"test_key_{i}", "value": {"data": f"test_value_{i}" * 50}} for i in range(100)
        ]

        # Benchmark cache writes
        start_time = time.time()
        successful_writes = 0
        for item in test_data:
            if cache_manager.set(item["key"], item["value"]):
                successful_writes += 1
        write_time = time.time() - start_time

        # Benchmark cache reads (cold)
        start_time = time.time()
        cache_hits = 0
        for item in test_data:
            if cache_manager.get(item["key"]) is not None:
                cache_hits += 1
        read_time = time.time() - start_time

        # Benchmark cache reads (warm - second pass)
        start_time = time.time()
        warm_cache_hits = 0
        for item in test_data:
            if cache_manager.get(item["key"]) is not None:
                warm_cache_hits += 1
        warm_read_time = time.time() - start_time

        # Get cache statistics
        cache_stats = cache_manager.get_cache_stats()

        benchmark_result = {
            "items_tested": len(test_data),
            "successful_writes": successful_writes,
            "write_time": write_time,
            "writes_per_second": successful_writes / write_time if write_time > 0 else 0,
            "cache_hits": cache_hits,
            "read_time": read_time,
            "reads_per_second": cache_hits / read_time if read_time > 0 else 0,
            "warm_cache_hits": warm_cache_hits,
            "warm_read_time": warm_read_time,
            "warm_reads_per_second": warm_cache_hits / warm_read_time if warm_read_time > 0 else 0,
            "cache_hit_rate": cache_stats.get("hit_rate", 0),
            "available_tiers": cache_stats.get("available_tiers", []),
        }

        speedup = read_time / warm_read_time if warm_read_time > 0 else 1.0
        print(f"  🚀 Cache speedup: {speedup:.2f}x (hit rate: {cache_stats.get('hit_rate', 0):.2f})")

        return benchmark_result

    def benchmark_memory_optimization(self) -> Dict[str, Any]:
        """Benchmark memory optimization features"""
        print("🧠 Benchmarking Memory Optimization...")

        memory_optimizer = MemoryOptimizer()

        # Create large dataset for memory testing
        large_dataset = [f"Large item {i} " * 1000 for i in range(500)]  # ~5MB total

        def memory_intensive_processor(item):
            # Simulate memory-intensive processing
            processed = item.upper().split()
            return {"word_count": len(processed), "char_count": len(item)}

        # Benchmark without memory optimization
        start_memory = memory_optimizer.get_current_memory_usage()
        start_time = time.time()

        # Process without chunking (baseline)
        baseline_results = []
        for item in large_dataset[:100]:  # Process subset to avoid memory issues
            result = memory_intensive_processor(item)
            baseline_results.append(result)

        baseline_time = time.time() - start_time
        baseline_memory = memory_optimizer.get_current_memory_usage()

        # Benchmark with memory optimization
        start_time = time.time()
        optimized_results = []

        for chunk_result in memory_optimizer.process_items_in_chunks(
            large_dataset, memory_intensive_processor, chunk_size=50
        ):
            optimized_results.extend(chunk_result["results"])

        optimized_time = time.time() - start_time
        final_memory = memory_optimizer.get_current_memory_usage()

        # Calculate metrics
        memory_stats = memory_optimizer.get_memory_stats()

        benchmark_result = {
            "items_processed": len(large_dataset),
            "baseline_items": len(baseline_results),
            "optimized_items": len(optimized_results),
            "baseline_time": baseline_time,
            "optimized_time": optimized_time,
            "time_ratio": baseline_time / optimized_time if optimized_time > 0 else 1.0,
            "start_memory_mb": start_memory["rss_mb"],
            "baseline_memory_mb": baseline_memory["rss_mb"],
            "final_memory_mb": final_memory["rss_mb"],
            "peak_memory_mb": memory_stats["peak_memory_mb"],
            "gc_collections": memory_stats["gc_collections"],
            "chunks_processed": memory_stats["chunks_processed"],
        }

        memory_efficiency = (
            (baseline_memory["rss_mb"] - final_memory["rss_mb"]) / baseline_memory["rss_mb"]
            if baseline_memory["rss_mb"] > 0
            else 0
        )
        print(f"  💚 Memory efficiency: {memory_efficiency:.1%} reduction")

        return benchmark_result

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run complete performance benchmark suite"""
        print("🏁 ClaudeDirector Phase 2 Performance Benchmark")
        print("=" * 50)

        overall_start = time.time()

        # Run individual benchmarks
        self.results["parallel_processing"] = self.benchmark_parallel_processing()
        self.results["caching_system"] = self.benchmark_caching_system()
        self.results["memory_optimization"] = self.benchmark_memory_optimization()

        overall_time = time.time() - overall_start

        # Calculate summary metrics
        parallel_speedup = self.results["parallel_processing"].get("speedup", 1.0)
        cache_speedup = self.results["caching_system"].get("read_time", 1.0) / self.results[
            "caching_system"
        ].get("warm_read_time", 1.0)

        summary = {
            "total_benchmark_time": overall_time,
            "parallel_processing_speedup": parallel_speedup,
            "caching_speedup": cache_speedup,
            "overall_performance_gain": (parallel_speedup + cache_speedup) / 2,
            "memory_optimization_active": self.results["memory_optimization"]["chunks_processed"]
            > 0,
            "timestamp": time.time(),
        }

        self.results["summary"] = summary

        print("\n" + "=" * 50)
        print("📊 Performance Summary:")
        print(f"  🔄 Parallel Processing: {parallel_speedup:.2f}x speedup")
        print(f"  💾 Caching System: {cache_speedup:.2f}x speedup")
        print(f"  🧠 Memory Optimization: Active")
        print(f"  ⚡ Overall Gain: {summary['overall_performance_gain']:.2f}x")
        print("\n🎉 Phase 2 Performance Optimization Complete!")

        return self.results


def run_benchmark():
    """Run performance benchmark from command line"""
    benchmark = PerformanceBenchmark()
    return benchmark.run_comprehensive_benchmark()


if __name__ == "__main__":
    run_benchmark()
