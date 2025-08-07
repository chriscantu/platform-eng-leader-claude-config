"""Performance benchmarking utilities for Strategic Integration Service."""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark."""
    
    name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: Optional[int] = None
    memory_after: Optional[int] = None
    memory_peak: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def memory_delta(self) -> Optional[int]:
        """Memory usage delta in bytes."""
        if self.memory_before is not None and self.memory_after is not None:
            return self.memory_after - self.memory_before
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/reporting."""
        return {
            "name": self.name,
            "duration_seconds": round(self.duration, 4),
            "memory_delta_mb": round(self.memory_delta / (1024 * 1024), 2) if self.memory_delta else None,
            "memory_peak_mb": round(self.memory_peak / (1024 * 1024), 2) if self.memory_peak else None,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class PerformanceBenchmark:
    """Performance benchmarking utility with memory and timing tracking."""

    def __init__(self, enable_memory_tracking: bool = True):
        self.enable_memory_tracking = enable_memory_tracking
        self.results: List[BenchmarkResult] = []
        
        # Try to import memory tracking
        self.psutil = None
        if enable_memory_tracking:
            try:
                import psutil
                self.psutil = psutil
                self.process = psutil.Process()
            except ImportError:
                logger.warning("psutil not available - memory tracking disabled")

    def _get_memory_usage(self) -> Optional[int]:
        """Get current memory usage in bytes."""
        if self.psutil:
            try:
                return self.process.memory_info().rss
            except Exception as e:
                logger.warning("Failed to get memory usage", error=str(e))
        return None

    @contextmanager
    def measure(self, name: str, **metadata):
        """Context manager for measuring performance."""
        start_time = time.time()
        memory_before = self._get_memory_usage()
        peak_memory = memory_before
        
        result = BenchmarkResult(
            name=name,
            start_time=start_time,
            end_time=0,
            duration=0,
            memory_before=memory_before,
            metadata=metadata,
        )

        try:
            yield result
            
            # Update peak memory during execution (if possible)
            if self.psutil:
                try:
                    current_memory = self._get_memory_usage()
                    if current_memory and (not peak_memory or current_memory > peak_memory):
                        peak_memory = current_memory
                except Exception:
                    pass
                    
        except Exception as e:
            result.success = False
            result.error = str(e)
            logger.error("Benchmark failed", name=name, error=str(e))
            raise
        finally:
            end_time = time.time()
            memory_after = self._get_memory_usage()
            
            result.end_time = end_time
            result.duration = end_time - start_time
            result.memory_after = memory_after
            result.memory_peak = peak_memory
            
            self.results.append(result)
            
            # Log the result
            logger.info("Performance measurement", **result.to_dict())

    def benchmark_function(self, func, name: str, *args, **kwargs):
        """Benchmark a function call."""
        with self.measure(name, function=func.__name__):
            return func(*args, **kwargs)

    def get_results(self) -> List[BenchmarkResult]:
        """Get all benchmark results."""
        return self.results.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.results:
            return {"total_benchmarks": 0}

        durations = [r.duration for r in self.results if r.success]
        memory_deltas = [r.memory_delta for r in self.results if r.memory_delta is not None]
        
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful

        summary = {
            "total_benchmarks": len(self.results),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.results) if self.results else 0,
        }

        if durations:
            summary.update({
                "total_time_seconds": sum(durations),
                "average_time_seconds": sum(durations) / len(durations),
                "min_time_seconds": min(durations),
                "max_time_seconds": max(durations),
            })

        if memory_deltas:
            summary.update({
                "average_memory_delta_mb": sum(memory_deltas) / len(memory_deltas) / (1024 * 1024),
                "max_memory_delta_mb": max(memory_deltas) / (1024 * 1024),
                "min_memory_delta_mb": min(memory_deltas) / (1024 * 1024),
            })

        return summary

    def clear(self):
        """Clear all benchmark results."""
        self.results.clear()
        logger.info("Benchmark results cleared")


class ExtractionBenchmark(PerformanceBenchmark):
    """Specialized benchmark for extraction operations."""

    def benchmark_extraction(
        self,
        extractor,
        extraction_method: str = "extract",
        **method_kwargs
    ) -> Any:
        """Benchmark an extraction operation."""
        method = getattr(extractor, extraction_method)
        
        with self.measure(
            f"{extractor.__class__.__name__}.{extraction_method}",
            extractor_type=extractor.__class__.__name__,
            method=extraction_method,
            **method_kwargs
        ) as result:
            
            extraction_result = method(**method_kwargs)
            
            # Add extraction-specific metadata
            if hasattr(extraction_result, '__len__'):
                result.metadata['result_count'] = len(extraction_result)
            
            if hasattr(extractor, 'get_extraction_metrics'):
                extraction_metrics = extractor.get_extraction_metrics()
                result.metadata.update(extraction_metrics)
                
            return extraction_result

    def compare_extractors(
        self,
        extractors: List[Any],
        extraction_method: str = "extract",
        **method_kwargs
    ) -> Dict[str, Any]:
        """Compare performance of multiple extractors."""
        logger.info("Starting extractor performance comparison", 
                   extractor_count=len(extractors))

        comparison_results = {}
        
        for extractor in extractors:
            extractor_name = extractor.__class__.__name__
            logger.info(f"Benchmarking {extractor_name}")
            
            try:
                result = self.benchmark_extraction(
                    extractor, extraction_method, **method_kwargs
                )
                comparison_results[extractor_name] = {
                    "success": True,
                    "result": result,
                    "benchmark": self.results[-1].to_dict()
                }
            except Exception as e:
                logger.error(f"Extractor {extractor_name} failed", error=str(e))
                comparison_results[extractor_name] = {
                    "success": False,
                    "error": str(e),
                    "benchmark": self.results[-1].to_dict() if self.results else None
                }

        # Generate comparison summary
        successful_results = {
            name: data for name, data in comparison_results.items() 
            if data["success"]
        }

        if successful_results:
            fastest = min(successful_results.items(), 
                         key=lambda x: x[1]["benchmark"]["duration_seconds"])
            slowest = max(successful_results.items(), 
                         key=lambda x: x[1]["benchmark"]["duration_seconds"])
            
            comparison_summary = {
                "fastest": {
                    "extractor": fastest[0],
                    "duration": fastest[1]["benchmark"]["duration_seconds"]
                },
                "slowest": {
                    "extractor": slowest[0], 
                    "duration": slowest[1]["benchmark"]["duration_seconds"]
                },
                "performance_improvement": (
                    slowest[1]["benchmark"]["duration_seconds"] / 
                    fastest[1]["benchmark"]["duration_seconds"]
                ) if fastest[1]["benchmark"]["duration_seconds"] > 0 else 1
            }
        else:
            comparison_summary = {"error": "No successful extractions to compare"}

        logger.info("Extractor comparison completed", summary=comparison_summary)
        
        return {
            "results": comparison_results,
            "summary": comparison_summary,
            "overall_benchmark_summary": self.get_summary()
        }


def benchmark_jira_queries(
    jira_client,
    queries: List[Dict[str, Any]],
    warmup_runs: int = 1,
    test_runs: int = 3,
) -> Dict[str, Any]:
    """Benchmark Jira query performance."""
    benchmark = PerformanceBenchmark()
    
    logger.info("Starting Jira query benchmarks", 
               query_count=len(queries),
               warmup_runs=warmup_runs,
               test_runs=test_runs)

    results = {}
    
    for query_config in queries:
        query_name = query_config.get("name", "unnamed_query")
        jql = query_config["jql"]
        fields = query_config.get("fields", [])
        max_results = query_config.get("max_results", 100)
        
        logger.info(f"Benchmarking query: {query_name}")
        
        # Warmup runs
        for i in range(warmup_runs):
            try:
                jira_client.search_issues(jql, fields=fields, max_results=max_results)
            except Exception as e:
                logger.warning(f"Warmup run {i+1} failed for {query_name}", error=str(e))

        # Test runs
        query_results = []
        for i in range(test_runs):
            try:
                with benchmark.measure(f"{query_name}_run_{i+1}",
                                     query=query_name,
                                     jql=jql,
                                     max_results=max_results) as result:
                    
                    search_result = jira_client.search_issues(
                        jql, fields=fields, max_results=max_results
                    )
                    result.metadata["result_count"] = len(search_result)
                    query_results.append(search_result)
                    
            except Exception as e:
                logger.error(f"Test run {i+1} failed for {query_name}", error=str(e))

        # Calculate query statistics
        query_benchmarks = [r for r in benchmark.results if r.name.startswith(query_name)]
        if query_benchmarks:
            durations = [r.duration for r in query_benchmarks if r.success]
            results[query_name] = {
                "runs": len(query_benchmarks),
                "successful_runs": len(durations),
                "average_duration": sum(durations) / len(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "result_counts": [r.metadata.get("result_count", 0) for r in query_benchmarks],
            }

    return {
        "query_results": results,
        "overall_summary": benchmark.get_summary()
    }
