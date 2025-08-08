"""
Memory optimization utilities with streaming and chunked processing
Quality-first implementation ensuring system stability under memory pressure
"""

import gc
import os
import sys
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, Optional, Tuple, Union

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

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
            self.max_memory_mb = 512
    
    def get_config():
        return MinimalConfig()


class MemoryOptimizer:
    """
    Memory-efficient processing with automatic memory monitoring
    Ensures system stability by preventing memory exhaustion
    """
    
    def __init__(self, config=None, safety_mode: bool = True):
        """
        Initialize memory optimizer with safety controls
        
        Args:
            config: Optional configuration override
            safety_mode: Enable aggressive memory protection (default: True)
        """
        self.config = config or get_config()
        self.safety_mode = safety_mode
        self.max_memory_mb = self.config.max_memory_mb
        self.memory_warning_threshold = 0.8  # 80% of max memory
        self.memory_critical_threshold = 0.95  # 95% of max memory
        
        # Monitoring and stats
        self.process = None
        if PSUTIL_AVAILABLE:
            try:
                self.process = psutil.Process()
            except Exception:
                pass
        
        self.stats = {
            'peak_memory_mb': 0,
            'gc_collections': 0,
            'memory_warnings': 0,
            'memory_emergency_stops': 0,
            'chunks_processed': 0,
            'streaming_operations': 0
        }
        
        logger.info(
            "Memory optimizer initialized",
            max_memory_mb=self.max_memory_mb,
            safety_mode=self.safety_mode,
            psutil_available=PSUTIL_AVAILABLE
        )
    
    def get_current_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        memory_info = {'rss_mb': 0, 'vms_mb': 0, 'percent': 0}
        
        if self.process:
            try:
                memory = self.process.memory_info()
                memory_info['rss_mb'] = memory.rss / 1024 / 1024  # RSS in MB
                memory_info['vms_mb'] = memory.vms / 1024 / 1024  # VMS in MB
                memory_info['percent'] = self.process.memory_percent()
            except Exception:
                pass
        
        # Update peak memory tracking
        if memory_info['rss_mb'] > self.stats['peak_memory_mb']:
            self.stats['peak_memory_mb'] = memory_info['rss_mb']
        
        return memory_info
    
    def check_memory_pressure(self) -> Dict[str, Any]:
        """
        Check for memory pressure and return status
        
        Returns:
            Dict with memory status and recommended actions
        """
        memory_info = self.get_current_memory_usage()
        current_memory = memory_info['rss_mb']
        
        pressure_level = 'normal'
        recommended_action = 'continue'
        
        if current_memory > self.max_memory_mb * self.memory_critical_threshold:
            pressure_level = 'critical'
            recommended_action = 'emergency_gc'
            self.stats['memory_emergency_stops'] += 1
            
        elif current_memory > self.max_memory_mb * self.memory_warning_threshold:
            pressure_level = 'warning'
            recommended_action = 'gc_recommended'
            self.stats['memory_warnings'] += 1
        
        return {
            'level': pressure_level,
            'current_mb': current_memory,
            'max_mb': self.max_memory_mb,
            'usage_percent': (current_memory / self.max_memory_mb) * 100,
            'recommended_action': recommended_action,
            'memory_info': memory_info
        }
    
    def process_large_file_streaming(
        self,
        file_path: Path,
        processor_func: callable,
        chunk_size: int = 8192,
        yield_every: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Process large files using streaming to minimize memory usage
        
        Args:
            file_path: Path to file to process
            processor_func: Function to process each chunk
            chunk_size: Size of each read chunk in bytes
            yield_every: Yield results every N chunks
            
        Yields:
            Processing results for each batch of chunks
        """
        if not file_path.exists():
            raise ClaudeDirectorError(f"File not found: {file_path}", component="memory_optimizer")
        
        try:
            file_size = file_path.stat().st_size
            total_chunks = (file_size + chunk_size - 1) // chunk_size
            
            logger.info(
                "Starting streaming file processing",
                file=str(file_path),
                size_mb=round(file_size / 1024 / 1024, 2),
                chunk_size=chunk_size,
                estimated_chunks=total_chunks
            )
            
            results_batch = []
            chunks_processed = 0
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                while True:
                    # Memory pressure check
                    if self.safety_mode:
                        pressure = self.check_memory_pressure()
                        if pressure['level'] == 'critical':
                            logger.warning(
                                "Critical memory pressure during streaming",
                                current_mb=pressure['current_mb'],
                                max_mb=pressure['max_mb']
                            )
                            self._emergency_memory_cleanup()
                            
                            # If still critical, yield current batch and pause
                            if self.check_memory_pressure()['level'] == 'critical':
                                if results_batch:
                                    yield {
                                        'results': results_batch,
                                        'chunks_processed': chunks_processed,
                                        'memory_pressure': pressure,
                                        'emergency_yield': True
                                    }
                                    results_batch = []
                                break
                    
                    # Read chunk
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break  # End of file
                    
                    try:
                        # Process chunk
                        result = processor_func(chunk)
                        if result is not None:
                            results_batch.append(result)
                        
                        chunks_processed += 1
                        self.stats['chunks_processed'] += 1
                        
                        # Yield batch periodically
                        if chunks_processed % yield_every == 0:
                            memory_info = self.get_current_memory_usage()
                            yield {
                                'results': results_batch,
                                'chunks_processed': chunks_processed,
                                'total_chunks': total_chunks,
                                'progress': chunks_processed / total_chunks,
                                'memory_mb': memory_info['rss_mb'],
                                'emergency_yield': False
                            }
                            results_batch = []
                            
                            # Light garbage collection
                            if chunks_processed % (yield_every * 2) == 0:
                                self._light_gc()
                    
                    except Exception as e:
                        logger.warning(
                            "Chunk processing error during streaming",
                            chunk_number=chunks_processed,
                            error=str(e)
                        )
                        continue
            
            # Yield final batch
            if results_batch:
                memory_info = self.get_current_memory_usage()
                yield {
                    'results': results_batch,
                    'chunks_processed': chunks_processed,
                    'total_chunks': total_chunks,
                    'progress': 1.0,
                    'memory_mb': memory_info['rss_mb'],
                    'final_batch': True,
                    'emergency_yield': False
                }
            
            self.stats['streaming_operations'] += 1
            logger.info(
                "Streaming processing completed",
                file=str(file_path),
                chunks_processed=chunks_processed,
                peak_memory_mb=self.stats['peak_memory_mb']
            )
            
        except Exception as e:
            logger.error(
                "Streaming processing failed",
                file=str(file_path),
                error=str(e),
                chunks_processed=chunks_processed
            )
            raise ClaudeDirectorError(f"Streaming processing failed: {e}", component="memory_optimizer")
    
    def process_items_in_chunks(
        self,
        items: List[Any],
        processor_func: callable,
        chunk_size: Optional[int] = None,
        memory_adaptive: bool = True
    ) -> Iterator[Dict[str, Any]]:
        """
        Process list of items in memory-efficient chunks
        
        Args:
            items: List of items to process
            processor_func: Function to process each chunk
            chunk_size: Fixed chunk size (None for adaptive)
            memory_adaptive: Adjust chunk size based on memory pressure
            
        Yields:
            Processing results for each chunk
        """
        if not items:
            return
        
        # Determine initial chunk size
        if chunk_size is None:
            chunk_size = self._calculate_optimal_chunk_size(len(items))
        
        total_items = len(items)
        processed_items = 0
        
        logger.info(
            "Starting chunked processing",
            total_items=total_items,
            initial_chunk_size=chunk_size,
            memory_adaptive=memory_adaptive
        )
        
        try:
            while processed_items < total_items:
                # Memory-adaptive chunk sizing
                if memory_adaptive and self.safety_mode:
                    pressure = self.check_memory_pressure()
                    
                    if pressure['level'] == 'critical':
                        # Emergency: process one item at a time
                        chunk_size = 1
                        self._emergency_memory_cleanup()
                        logger.warning(
                            "Emergency chunk size reduction",
                            new_chunk_size=chunk_size,
                            memory_mb=pressure['current_mb']
                        )
                        
                    elif pressure['level'] == 'warning':
                        # Warning: reduce chunk size
                        chunk_size = max(1, chunk_size // 2)
                        logger.info(
                            "Adaptive chunk size reduction",
                            new_chunk_size=chunk_size,
                            memory_mb=pressure['current_mb']
                        )
                
                # Extract chunk
                end_index = min(processed_items + chunk_size, total_items)
                chunk_items = items[processed_items:end_index]
                
                try:
                    # Process chunk
                    start_memory = self.get_current_memory_usage()['rss_mb']
                    
                    chunk_results = []
                    for item in chunk_items:
                        result = processor_func(item)
                        if result is not None:
                            chunk_results.append(result)
                    
                    end_memory = self.get_current_memory_usage()['rss_mb']
                    memory_delta = end_memory - start_memory
                    
                    yield {
                        'results': chunk_results,
                        'chunk_start': processed_items,
                        'chunk_end': end_index,
                        'chunk_size': len(chunk_items),
                        'progress': end_index / total_items,
                        'memory_mb': end_memory,
                        'memory_delta_mb': memory_delta,
                        'total_processed': end_index
                    }
                    
                    processed_items = end_index
                    self.stats['chunks_processed'] += 1
                    
                    # Light cleanup every few chunks
                    if self.stats['chunks_processed'] % 5 == 0:
                        self._light_gc()
                
                except Exception as e:
                    logger.error(
                        "Chunk processing error",
                        chunk_start=processed_items,
                        chunk_size=len(chunk_items),
                        error=str(e)
                    )
                    # Skip this chunk and continue
                    processed_items = end_index
                    continue
                    
        except Exception as e:
            logger.error(
                "Chunked processing failed",
                total_items=total_items,
                processed=processed_items,
                error=str(e)
            )
            raise ClaudeDirectorError(f"Chunked processing failed: {e}", component="memory_optimizer")
    
    def _calculate_optimal_chunk_size(self, total_items: int) -> int:
        """Calculate optimal chunk size based on available memory and item count"""
        
        # Base chunk size calculation
        if total_items <= 100:
            base_chunk_size = min(10, total_items)
        elif total_items <= 1000:
            base_chunk_size = min(50, total_items // 10)
        elif total_items <= 10000:
            base_chunk_size = min(100, total_items // 50)
        else:
            base_chunk_size = min(200, total_items // 100)
        
        # Adjust based on available memory
        memory_info = self.get_current_memory_usage()
        available_memory_mb = self.max_memory_mb - memory_info['rss_mb']
        
        if available_memory_mb < 50:  # Low memory
            chunk_size = max(1, base_chunk_size // 4)
        elif available_memory_mb < 100:  # Medium memory
            chunk_size = max(1, base_chunk_size // 2)
        else:  # Good memory availability
            chunk_size = base_chunk_size
        
        logger.debug(
            "Calculated optimal chunk size",
            total_items=total_items,
            base_chunk_size=base_chunk_size,
            final_chunk_size=chunk_size,
            available_memory_mb=available_memory_mb
        )
        
        return chunk_size
    
    def _light_gc(self):
        """Perform light garbage collection"""
        collected = gc.collect()
        self.stats['gc_collections'] += 1
        
        if collected > 0:
            logger.debug("Light GC completed", objects_collected=collected)
    
    def _emergency_memory_cleanup(self):
        """Perform aggressive memory cleanup in emergency situations"""
        logger.warning("Performing emergency memory cleanup")
        
        # Force garbage collection
        for generation in range(3):
            collected = gc.collect(generation)
            if collected > 0:
                logger.debug(f"Emergency GC generation {generation}", objects_collected=collected)
        
        self.stats['gc_collections'] += 3
        
        # Additional cleanup if available
        if hasattr(gc, 'set_threshold'):
            # Temporarily make GC more aggressive
            old_thresholds = gc.get_threshold()
            gc.set_threshold(100, 10, 10)
            gc.collect()
            gc.set_threshold(*old_thresholds)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        current_memory = self.get_current_memory_usage()
        pressure = self.check_memory_pressure()
        
        return {
            'current_memory_mb': current_memory['rss_mb'],
            'peak_memory_mb': self.stats['peak_memory_mb'],
            'max_memory_mb': self.max_memory_mb,
            'memory_pressure_level': pressure['level'],
            'usage_percent': pressure['usage_percent'],
            'gc_collections': self.stats['gc_collections'],
            'memory_warnings': self.stats['memory_warnings'],
            'emergency_stops': self.stats['memory_emergency_stops'],
            'chunks_processed': self.stats['chunks_processed'],
            'streaming_operations': self.stats['streaming_operations'],
            'safety_mode': self.safety_mode,
            'psutil_available': PSUTIL_AVAILABLE
        }


# Backward compatibility functions
def get_memory_optimizer(config=None) -> MemoryOptimizer:
    """Get memory optimizer instance"""
    return MemoryOptimizer(config=config)

def process_items_chunked(
    items: List[Any],
    processor_func: callable,
    chunk_size: Optional[int] = None
) -> Iterator[Dict[str, Any]]:
    """Convenience function for chunked processing"""
    optimizer = get_memory_optimizer()
    return optimizer.process_items_in_chunks(items, processor_func, chunk_size)

def stream_large_file(
    file_path: Path,
    processor_func: callable,
    chunk_size: int = 8192
) -> Generator[Dict[str, Any], None, None]:
    """Convenience function for file streaming"""
    optimizer = get_memory_optimizer()
    return optimizer.process_large_file_streaming(file_path, processor_func, chunk_size)
