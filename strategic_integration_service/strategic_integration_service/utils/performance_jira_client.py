"""Performance-optimized Jira client with caching and parallel processing."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

import structlog

from ..core.config import Settings
from .cache import MultiTierCache
from .jira_client import JiraClient

logger = structlog.get_logger(__name__)


class PerformanceJiraClient(JiraClient):
    """Enhanced Jira client with caching and parallel processing capabilities."""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        
        # Initialize cache system
        self.cache = MultiTierCache(
            enable_memory=True,
            enable_file=settings.enable_caching,
            enable_redis=False,  # Can be enabled with Redis configuration
            cache_dir=settings.output_base_dir / ".cache",
        ) if settings.enable_caching else None
        
        self.cache_ttl = settings.cache_ttl_seconds
        self.max_parallel_requests = settings.parallel_requests
        
        # Performance metrics
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "api_calls": 0,
            "total_time": 0.0,
            "parallel_requests": 0,
        }

    def get_cached_or_fetch(
        self,
        cache_prefix: str,
        fetch_func,
        cache_key_params: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> Any:
        """Get data from cache or fetch and cache it."""
        if not self.cache:
            return fetch_func()

        ttl = ttl or self.cache_ttl

        # Try to get from cache
        cached_value = self.cache.get(cache_prefix, **cache_key_params)
        if cached_value is not None:
            self.metrics["cache_hits"] += 1
            logger.debug("Cache hit", prefix=cache_prefix, params=cache_key_params)
            return cached_value

        # Cache miss - fetch and store
        self.metrics["cache_misses"] += 1
        logger.debug("Cache miss - fetching", prefix=cache_prefix, params=cache_key_params)
        
        start_time = time.time()
        result = fetch_func()
        fetch_time = time.time() - start_time
        
        self.metrics["api_calls"] += 1
        self.metrics["total_time"] += fetch_time

        # Store in cache
        self.cache.set(cache_prefix, result, ttl, **cache_key_params)
        
        return result

    def search_issues_cached(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        max_results: int = 100,
        ttl: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Search issues with caching support."""
        
        def fetch_func():
            return self.search_all_issues(jql, fields, max_results)

        cache_params = {
            "jql": jql,
            "fields": fields or [],
            "max_results": max_results,
        }

        return self.get_cached_or_fetch("jira_search", fetch_func, cache_params, ttl)

    def parallel_search_issues(
        self,
        queries: List[Tuple[str, str, Optional[List[str]], int]],  # (cache_key, jql, fields, max_results)
        max_workers: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Execute multiple Jira searches in parallel."""
        max_workers = max_workers or min(self.max_parallel_requests, len(queries))
        
        logger.info(
            "Starting parallel Jira queries",
            query_count=len(queries),
            max_workers=max_workers,
        )

        results = {}
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all queries
            future_to_key = {}
            for cache_key, jql, fields, max_results in queries:
                future = executor.submit(
                    self.search_issues_cached,
                    jql,
                    fields,
                    max_results,
                )
                future_to_key[future] = cache_key

            # Collect results as they complete
            for future in as_completed(future_to_key):
                cache_key = future_to_key[future]
                try:
                    result = future.result()
                    results[cache_key] = result
                    logger.debug("Parallel query completed", cache_key=cache_key, count=len(result))
                except Exception as e:
                    logger.error("Parallel query failed", cache_key=cache_key, error=str(e))
                    results[cache_key] = []

        total_time = time.time() - start_time
        self.metrics["parallel_requests"] += len(queries)
        
        logger.info(
            "Parallel queries completed",
            total_time=total_time,
            query_count=len(queries),
            results_count={k: len(v) for k, v in results.items()},
        )

        return results

    async def async_search_issues(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """Async wrapper for search_issues_cached."""
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            None,
            self.search_issues_cached,
            jql,
            fields,
            max_results,
        )

    async def async_parallel_search(
        self,
        queries: List[Tuple[str, str, Optional[List[str]], int]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Async version of parallel search for better integration."""
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            None,
            self.parallel_search_issues,
            queries,
        )

    def batch_search_with_pagination(
        self,
        base_jql: str,
        batch_size: int = 100,
        max_total: int = 1000,
        fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Search large datasets with efficient pagination and caching."""
        all_results = []
        start_at = 0
        
        logger.info(
            "Starting batch search with pagination",
            base_jql=base_jql,
            batch_size=batch_size,
            max_total=max_total,
        )

        while len(all_results) < max_total:
            remaining = max_total - len(all_results)
            current_batch_size = min(batch_size, remaining)
            
            # Create cache key that includes pagination
            cache_params = {
                "jql": base_jql,
                "fields": fields or [],
                "start_at": start_at,
                "max_results": current_batch_size,
            }

            def fetch_batch():
                return self.search_issues(
                    jql=base_jql,
                    start_at=start_at,
                    max_results=current_batch_size,
                    fields=fields,
                )

            batch_results = self.get_cached_or_fetch(
                "jira_batch", fetch_batch, cache_params
            )

            if not batch_results:
                logger.info("No more results found", start_at=start_at)
                break

            all_results.extend(batch_results)
            start_at += len(batch_results)

            logger.debug(
                "Batch completed",
                batch_size=len(batch_results),
                total_so_far=len(all_results),
                start_at=start_at,
            )

            # If we got fewer results than requested, we've hit the end
            if len(batch_results) < current_batch_size:
                break

        logger.info(
            "Batch search completed",
            total_results=len(all_results),
            batches_processed=(start_at // batch_size) + 1,
        )

        return all_results

    def warm_cache(self, queries: List[Tuple[str, str, Optional[List[str]], int]]) -> None:
        """Pre-warm cache with commonly used queries."""
        logger.info("Warming cache", query_count=len(queries))
        
        start_time = time.time()
        results = self.parallel_search_issues(queries)
        warm_time = time.time() - start_time
        
        total_results = sum(len(result) for result in results.values())
        logger.info(
            "Cache warming completed",
            time_taken=warm_time,
            queries_warmed=len(queries),
            total_results=total_results,
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        cache_hit_rate = (
            self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"])
            if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0
            else 0
        )

        avg_api_time = (
            self.metrics["total_time"] / self.metrics["api_calls"]
            if self.metrics["api_calls"] > 0
            else 0
        )

        return {
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "api_calls": self.metrics["api_calls"],
            "parallel_requests": self.metrics["parallel_requests"],
            "average_api_time": avg_api_time,
            "total_api_time": self.metrics["total_time"],
        }

    def clear_cache(self, confirm: bool = False) -> None:
        """Clear all cache data."""
        if self.cache:
            self.cache.clear(confirm=confirm)
            logger.info("Performance cache cleared")

    def close(self) -> None:
        """Close client and log performance metrics."""
        metrics = self.get_performance_metrics()
        logger.info("Performance metrics", **metrics)
        super().close()


class PerformanceExtractorMixin:
    """Mixin to add performance optimization to extractors."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace standard Jira client with performance client
        if hasattr(self, 'settings'):
            self.perf_client = PerformanceJiraClient(self.settings)

    def extract_with_performance(
        self,
        queries: List[Tuple[str, str, Optional[List[str]], int]],
        warm_cache: bool = False,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract data using performance-optimized parallel queries."""
        
        if warm_cache:
            # Pre-warm cache with common queries
            self.perf_client.warm_cache(queries)

        # Execute all queries in parallel
        return self.perf_client.parallel_search_issues(queries)

    def get_extraction_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from the current extraction."""
        if hasattr(self, 'perf_client'):
            return self.perf_client.get_performance_metrics()
        return {}
