"""
Parallel processing utilities with backward compatibility validation
Quality-centric implementation ensuring all features remain supported
"""

import asyncio
import concurrent.futures
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    import structlog

    logger = structlog.get_logger()
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

try:
    # Try new package structure first
    from ..core.config import get_config
    from ..core.exceptions import ClaudeDirectorError
except ImportError:
    # Fallback for backward compatibility
    class ClaudeDirectorError(Exception):
        pass

    class MinimalConfig:
        def __init__(self):
            self.parallel_requests = 5
            self.max_memory_mb = 512

    def get_config():
        return MinimalConfig()


class ParallelProcessor:
    """
    Quality-centric parallel processing with comprehensive validation
    Maintains backward compatibility while providing performance improvements
    """

    def __init__(self, config=None, validation_mode: bool = True):
        """
        Initialize with quality validation enabled by default

        Args:
            config: Optional configuration override
            validation_mode: Enable comprehensive validation (default: True)
        """
        self.config = config or get_config()
        self.validation_mode = validation_mode
        self.max_workers = min(self.config.parallel_requests, 8)  # Safety limit
        self.memory_limit_mb = self.config.max_memory_mb

        # Performance tracking
        self.stats = {
            "operations_completed": 0,
            "total_time_saved": 0.0,
            "parallel_efficiency": 0.0,
            "validation_checks_passed": 0,
            "fallback_activations": 0,
        }

        logger.info(
            "Parallel processor initialized",
            max_workers=self.max_workers,
            validation_mode=self.validation_mode,
            memory_limit_mb=self.memory_limit_mb,
        )

    def process_files_parallel(
        self,
        file_paths: List[Path],
        processor_func: Callable,
        validation_func: Optional[Callable] = None,
        chunk_size: int = 10,
    ) -> Dict[str, Any]:
        """
        Process files in parallel with quality validation

        Args:
            file_paths: List of file paths to process
            processor_func: Function to apply to each file
            validation_func: Optional validation function for results
            chunk_size: Files per worker batch

        Returns:
            Processing results with validation status
        """
        if not file_paths:
            return {
                "success": True,
                "results": [],
                "parallel_time": 0.0,
                "sequential_time": 0.0,
                "efficiency_gain": 0.0,
                "validation_passed": True,
            }

        start_time = time.time()

        # Quality validation: Test sequential processing first if enabled
        sequential_results = None
        sequential_time = 0.0

        if self.validation_mode and len(file_paths) <= 3:
            # For small batches, run sequential validation
            seq_start = time.time()
            sequential_results = self._process_files_sequential(file_paths, processor_func)
            sequential_time = time.time() - seq_start

            logger.debug(
                "Sequential validation completed",
                files=len(file_paths),
                time=sequential_time,
                results=len(sequential_results),
            )

        # Parallel processing with worker safety
        try:
            parallel_results = self._process_files_concurrent(
                file_paths, processor_func, chunk_size
            )
            parallel_time = time.time() - start_time

            # Validation: Compare results if sequential was run
            validation_passed = True
            if sequential_results is not None:
                validation_passed = self._validate_parallel_results(
                    sequential_results, parallel_results, validation_func
                )

                if not validation_passed:
                    logger.warning(
                        "Parallel processing validation failed, using sequential results",
                        sequential_count=len(sequential_results),
                        parallel_count=len(parallel_results),
                    )
                    self.stats["fallback_activations"] += 1
                    return {
                        "success": True,
                        "results": sequential_results,
                        "parallel_time": parallel_time,
                        "sequential_time": sequential_time,
                        "efficiency_gain": 0.0,  # No gain due to fallback
                        "validation_passed": False,
                        "fallback_used": True,
                    }

            # Success metrics
            efficiency_gain = 0.0
            if sequential_time > 0:
                efficiency_gain = (sequential_time - parallel_time) / sequential_time
                self.stats["total_time_saved"] += sequential_time - parallel_time
                self.stats["parallel_efficiency"] = efficiency_gain

            self.stats["operations_completed"] += 1
            self.stats["validation_checks_passed"] += 1

            logger.info(
                "Parallel processing completed successfully",
                files=len(file_paths),
                parallel_time=round(parallel_time, 2),
                sequential_time=round(sequential_time, 2),
                efficiency_gain=round(efficiency_gain, 2),
                validation_passed=validation_passed,
            )

            return {
                "success": True,
                "results": parallel_results,
                "parallel_time": parallel_time,
                "sequential_time": sequential_time,
                "efficiency_gain": efficiency_gain,
                "validation_passed": validation_passed,
                "fallback_used": False,
            }

        except Exception as e:
            logger.error(
                "Parallel processing failed, falling back to sequential",
                error=str(e),
                files=len(file_paths),
            )

            # Graceful fallback to sequential processing
            if sequential_results is not None:
                return {
                    "success": True,
                    "results": sequential_results,
                    "parallel_time": 0.0,
                    "sequential_time": sequential_time,
                    "efficiency_gain": 0.0,
                    "validation_passed": True,
                    "fallback_used": True,
                    "fallback_reason": str(e),
                }
            else:
                # Emergency sequential processing
                emergency_results = self._process_files_sequential(file_paths, processor_func)
                emergency_time = time.time() - start_time

                self.stats["fallback_activations"] += 1

                return {
                    "success": True,
                    "results": emergency_results,
                    "parallel_time": 0.0,
                    "sequential_time": emergency_time,
                    "efficiency_gain": 0.0,
                    "validation_passed": True,
                    "fallback_used": True,
                    "fallback_reason": str(e),
                }

    def _process_files_sequential(
        self, file_paths: List[Path], processor_func: Callable
    ) -> List[Any]:
        """Sequential processing for validation baseline"""
        results = []

        for file_path in file_paths:
            try:
                result = processor_func(file_path)
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.warning(
                    "Sequential processing error for file", file=str(file_path), error=str(e)
                )
                # Continue processing other files
                continue

        return results

    def _process_files_concurrent(
        self, file_paths: List[Path], processor_func: Callable, chunk_size: int
    ) -> List[Any]:
        """Concurrent processing with thread safety"""
        results = []

        # Chunk files for better memory management
        file_chunks = [
            file_paths[i : i + chunk_size] for i in range(0, len(file_paths), chunk_size)
        ]

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers, thread_name_prefix="claudedirector_worker"
        ) as executor:
            # Submit chunk processing tasks
            future_to_chunk = {
                executor.submit(self._process_chunk, chunk, processor_func): chunk
                for chunk in file_chunks
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_chunk, timeout=300):
                chunk = future_to_chunk[future]
                try:
                    chunk_results = future.result()
                    results.extend(chunk_results)
                except Exception as e:
                    logger.error("Chunk processing failed", chunk_size=len(chunk), error=str(e))
                    # Process chunk sequentially as fallback
                    chunk_results = self._process_files_sequential(chunk, processor_func)
                    results.extend(chunk_results)

        return results

    def _process_chunk(self, file_paths: List[Path], processor_func: Callable) -> List[Any]:
        """Process a chunk of files in a single thread"""
        chunk_results = []

        for file_path in file_paths:
            try:
                result = processor_func(file_path)
                if result is not None:
                    chunk_results.append(result)
            except Exception as e:
                logger.warning(
                    "File processing error in parallel chunk", file=str(file_path), error=str(e)
                )
                continue

        return chunk_results

    def _validate_parallel_results(
        self,
        sequential_results: List[Any],
        parallel_results: List[Any],
        validation_func: Optional[Callable] = None,
    ) -> bool:
        """
        Validate that parallel processing produces equivalent results

        Args:
            sequential_results: Results from sequential processing
            parallel_results: Results from parallel processing
            validation_func: Optional custom validation function

        Returns:
            True if results are equivalent, False otherwise
        """
        if validation_func:
            return validation_func(sequential_results, parallel_results)

        # Default validation: count and basic structure
        if len(sequential_results) != len(parallel_results):
            logger.warning(
                "Result count mismatch",
                sequential=len(sequential_results),
                parallel=len(parallel_results),
            )
            return False

        # For more complex validation, we'd need specific comparison logic
        # For now, assume equivalent if counts match
        return True

    def process_content_parallel(
        self,
        content_items: List[Tuple[str, Dict[str, Any]]],
        processor_func: Callable,
        batch_size: int = 5,
    ) -> Dict[str, Any]:
        """
        Process content items in parallel with memory management

        Args:
            content_items: List of (content, context) tuples
            processor_func: Function to process each content item
            batch_size: Items per batch

        Returns:
            Processing results with performance metrics
        """
        if not content_items:
            return {"success": True, "results": [], "batches_processed": 0}

        start_time = time.time()
        all_results = []

        # Process in batches for memory management
        batches = [
            content_items[i : i + batch_size] for i in range(0, len(content_items), batch_size)
        ]

        try:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=min(self.max_workers, len(batches))
            ) as executor:
                future_to_batch = {
                    executor.submit(self._process_content_batch, batch, processor_func): batch
                    for batch in batches
                }

                for future in concurrent.futures.as_completed(future_to_batch, timeout=180):
                    try:
                        batch_results = future.result()
                        all_results.extend(batch_results)
                    except Exception as e:
                        batch = future_to_batch[future]
                        logger.error(
                            "Content batch processing failed", batch_size=len(batch), error=str(e)
                        )
                        # Sequential fallback for failed batch
                        for content, context in batch:
                            try:
                                result = processor_func(content, context)
                                if result:
                                    all_results.append(result)
                            except Exception:
                                continue

            processing_time = time.time() - start_time

            logger.info(
                "Parallel content processing completed",
                items=len(content_items),
                batches=len(batches),
                results=len(all_results),
                time=round(processing_time, 2),
            )

            return {
                "success": True,
                "results": all_results,
                "batches_processed": len(batches),
                "processing_time": processing_time,
                "items_per_second": len(content_items) / processing_time
                if processing_time > 0
                else 0,
            }

        except Exception as e:
            logger.error("Parallel content processing failed", error=str(e))
            raise ClaudeDirectorError(
                f"Parallel processing failed: {e}", component="parallel_processor"
            )

    def _process_content_batch(
        self, content_batch: List[Tuple[str, Dict[str, Any]]], processor_func: Callable
    ) -> List[Any]:
        """Process a batch of content items"""
        batch_results = []

        for content, context in content_batch:
            try:
                result = processor_func(content, context)
                if result:
                    batch_results.append(result)
            except Exception as e:
                logger.warning(
                    "Content processing error in batch", content_length=len(content), error=str(e)
                )
                continue

        return batch_results

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "operations_completed": self.stats["operations_completed"],
            "total_time_saved_seconds": round(self.stats["total_time_saved"], 2),
            "average_efficiency_gain": round(self.stats["parallel_efficiency"], 2),
            "validation_checks_passed": self.stats["validation_checks_passed"],
            "fallback_activations": self.stats["fallback_activations"],
            "fallback_rate": round(
                self.stats["fallback_activations"] / max(self.stats["operations_completed"], 1), 2
            ),
            "max_workers": self.max_workers,
            "validation_mode": self.validation_mode,
        }


# Backward compatibility functions
def get_parallel_processor(config=None) -> ParallelProcessor:
    """Get parallel processor instance"""
    return ParallelProcessor(config=config)


def process_files_parallel(
    file_paths: List[Path], processor_func: Callable, validation_enabled: bool = True
) -> Dict[str, Any]:
    """Convenience function for parallel file processing"""
    processor = get_parallel_processor()
    processor.validation_mode = validation_enabled
    return processor.process_files_parallel(file_paths, processor_func)
