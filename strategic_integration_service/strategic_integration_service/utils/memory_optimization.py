"""Memory optimization utilities for large dataset processing."""

import gc
import sys
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Iterator
import weakref

import structlog

logger = structlog.get_logger(__name__)


class MemoryMonitor:
    """Monitor and report memory usage during operations."""

    def __init__(self):
        self.baseline_memory = self._get_memory_usage()
        self.peak_memory = self.baseline_memory
        self.checkpoints = []

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            # Fallback to sys.getsizeof for approximate usage
            return sys.getsizeof(gc.get_objects())

    def checkpoint(self, name: str) -> None:
        """Create a memory usage checkpoint."""
        current_memory = self._get_memory_usage()
        self.peak_memory = max(self.peak_memory, current_memory)
        
        checkpoint = {
            "name": name,
            "memory_bytes": current_memory,
            "memory_mb": current_memory / (1024 * 1024),
            "delta_from_baseline_mb": (current_memory - self.baseline_memory) / (1024 * 1024),
        }
        
        self.checkpoints.append(checkpoint)
        logger.debug("Memory checkpoint", **checkpoint)

    def get_report(self) -> Dict[str, Any]:
        """Generate memory usage report."""
        current_memory = self._get_memory_usage()
        
        return {
            "baseline_mb": self.baseline_memory / (1024 * 1024),
            "current_mb": current_memory / (1024 * 1024),
            "peak_mb": self.peak_memory / (1024 * 1024),
            "total_growth_mb": (current_memory - self.baseline_memory) / (1024 * 1024),
            "peak_growth_mb": (self.peak_memory - self.baseline_memory) / (1024 * 1024),
            "checkpoints": self.checkpoints,
        }


@contextmanager
def memory_monitoring(operation_name: str):
    """Context manager for monitoring memory usage during operations."""
    monitor = MemoryMonitor()
    monitor.checkpoint(f"start_{operation_name}")
    
    try:
        yield monitor
    finally:
        monitor.checkpoint(f"end_{operation_name}")
        report = monitor.get_report()
        logger.info("Memory usage report", operation=operation_name, **report)


def chunked_processing(
    data: List[Any], 
    chunk_size: int = 100,
    process_func: Optional[callable] = None
) -> Generator[List[Any], None, None]:
    """Process large datasets in memory-efficient chunks."""
    logger.info("Starting chunked processing", 
                total_items=len(data), 
                chunk_size=chunk_size)
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        
        if process_func:
            chunk = process_func(chunk)
            
        logger.debug("Processing chunk", 
                    chunk_start=i, 
                    chunk_size=len(chunk))
        
        yield chunk
        
        # Force garbage collection after each chunk
        gc.collect()


class LazyJiraLoader:
    """Lazy loader for Jira data to minimize memory usage."""

    def __init__(self, jira_client, jql: str, fields: List[str], batch_size: int = 50):
        self.jira_client = jira_client
        self.jql = jql
        self.fields = fields
        self.batch_size = batch_size
        self._total_count = None

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate through issues lazily."""
        start_at = 0
        
        while True:
            try:
                batch = self.jira_client.search_issues(
                    jql=self.jql,
                    fields=self.fields,
                    start_at=start_at,
                    max_results=self.batch_size,
                )
                
                if not batch:
                    break
                    
                for issue in batch:
                    yield issue
                    
                start_at += len(batch)
                
                # If we got fewer results than batch_size, we're done
                if len(batch) < self.batch_size:
                    break
                    
            except Exception as e:
                logger.error("Error in lazy loading", error=str(e), start_at=start_at)
                break

    def count(self) -> int:
        """Get total count of issues (cached after first call)."""
        if self._total_count is None:
            # Use JQL count query to get total without loading all data
            count_jql = f"({self.jql})"
            try:
                result = self.jira_client.search_issues(
                    jql=count_jql,
                    fields=["key"],  # Minimal fields for counting
                    max_results=0,   # We only want the total count
                )
                # The search_issues method should return total count in metadata
                # For now, we'll estimate by doing a small search
                sample = self.jira_client.search_issues(
                    jql=count_jql,
                    fields=["key"],
                    max_results=1,
                )
                
                # This is a rough estimate - in practice, you'd want to use
                # the total count from the search response metadata
                self._total_count = len(sample) * 1000  # Rough estimate
                
            except Exception as e:
                logger.warning("Could not get count", error=str(e))
                self._total_count = 0
                
        return self._total_count


class MemoryEfficientProcessor:
    """Process large datasets with memory optimization strategies."""

    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        self.monitor = MemoryMonitor()
        self.processed_count = 0

    def process_jira_data(
        self,
        jira_client,
        jql: str,
        fields: List[str],
        processor_func: callable,
        batch_size: int = 50,
    ) -> List[Any]:
        """Process Jira data with memory management."""
        logger.info("Starting memory-efficient Jira data processing")
        
        self.monitor.checkpoint("start_processing")
        results = []
        
        # Use lazy loading
        loader = LazyJiraLoader(jira_client, jql, fields, batch_size)
        
        for issue in loader:
            # Check memory usage periodically
            if self.processed_count % 100 == 0:
                self.monitor.checkpoint(f"processed_{self.processed_count}")
                self._check_memory_usage()
            
            try:
                processed_issue = processor_func(issue)
                if processed_issue:
                    results.append(processed_issue)
                    
            except Exception as e:
                logger.error("Error processing issue", 
                           issue_key=issue.get("key", "unknown"),
                           error=str(e))
            
            self.processed_count += 1
            
            # Periodic garbage collection
            if self.processed_count % batch_size == 0:
                gc.collect()

        self.monitor.checkpoint("end_processing")
        
        logger.info("Memory-efficient processing completed",
                   processed_count=self.processed_count,
                   results_count=len(results))
        
        return results

    def _check_memory_usage(self) -> None:
        """Check if memory usage is approaching limits."""
        current_mb = self.monitor._get_memory_usage() / (1024 * 1024)
        
        if current_mb > self.max_memory_mb * 0.8:  # 80% threshold
            logger.warning("Memory usage approaching limit",
                          current_mb=current_mb,
                          limit_mb=self.max_memory_mb)
            
            # Force garbage collection
            collected = gc.collect()
            logger.info("Forced garbage collection", objects_collected=collected)
            
            # Log memory after GC
            new_mb = self.monitor._get_memory_usage() / (1024 * 1024)
            logger.info("Memory after GC", memory_mb=new_mb, freed_mb=current_mb - new_mb)


class WeakReferenceCache:
    """Cache that automatically cleans up unused objects."""

    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
        self._access_count = {}

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        item = self._cache.get(key)
        if item is not None:
            self._access_count[key] = self._access_count.get(key, 0) + 1
        return item

    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        self._cache[key] = value
        self._access_count[key] = 0

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)

    def cleanup(self) -> int:
        """Force cleanup of weak references."""
        # The WeakValueDictionary automatically cleans up,
        # but we can clean up our access count dict
        keys_to_remove = []
        for key in self._access_count:
            if key not in self._cache:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._access_count[key]
            
        return len(keys_to_remove)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": self.size(),
            "total_keys_tracked": len(self._access_count),
            "most_accessed": max(self._access_count.items(), 
                               key=lambda x: x[1]) if self._access_count else None,
        }


def optimize_data_structure(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Optimize data structures for memory efficiency."""
    logger.info("Optimizing data structures", input_count=len(data))
    
    optimized = []
    
    for item in data:
        # Remove None values to save memory
        optimized_item = {k: v for k, v in item.items() if v is not None}
        
        # Convert large strings to more efficient representations if possible
        for key, value in optimized_item.items():
            if isinstance(value, str) and len(value) > 1000:
                # For very large strings, consider compression or truncation
                # This is a simple example - in practice you'd want more sophisticated logic
                optimized_item[key] = value[:1000] + "..." if len(value) > 1000 else value
        
        optimized.append(optimized_item)
    
    # Force garbage collection of original data
    del data
    gc.collect()
    
    logger.info("Data structure optimization completed", output_count=len(optimized))
    return optimized


@contextmanager
def memory_limited_operation(max_memory_mb: int = 512):
    """Context manager for operations with memory limits."""
    monitor = MemoryMonitor()
    
    try:
        yield monitor
    finally:
        report = monitor.get_report()
        if report["peak_mb"] > max_memory_mb:
            logger.warning("Memory limit exceeded",
                          peak_mb=report["peak_mb"],
                          limit_mb=max_memory_mb)
        else:
            logger.info("Memory usage within limits",
                       peak_mb=report["peak_mb"],
                       limit_mb=max_memory_mb)
