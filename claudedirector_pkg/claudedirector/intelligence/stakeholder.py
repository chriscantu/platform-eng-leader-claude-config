"""
Stakeholder Intelligence Module
Unified interface for stakeholder detection, profiling, and management
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Backward compatibility imports
try:
    # Try new package structure first
    from ..core.config import get_config
    from ..core.database import get_database_manager
    from ..core.exceptions import AIDetectionError, DatabaseError
    from ..utils.parallel import ParallelProcessor
    from ..utils.cache import CacheManager
    from ..utils.memory import MemoryOptimizer
except ImportError:
    # Fallback to legacy structure
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "memory"))
    sys.path.insert(0, str(project_root / "bin"))
    
    # Create minimal config for backward compatibility
    class MinimalConfig:
        def __init__(self):
            self.database_path = str(project_root / "memory" / "strategic_memory.db")
    
    def get_config():
        return MinimalConfig()
    
    class AIDetectionError(Exception):
        pass
    
    class DatabaseError(Exception):
        pass

# Import legacy modules for functionality
try:
    from local_stakeholder_ai import LocalStakeholderAI
    from intelligent_stakeholder_detector import IntelligentStakeholderDetector
    from stakeholder_engagement_engine import StakeholderEngagementEngine
except ImportError:
    # If legacy imports fail, create minimal stubs
    class LocalStakeholderAI:
        def __init__(self, *args, **kwargs):
            pass
    
    class IntelligentStakeholderDetector:
        def __init__(self, *args, **kwargs):
            pass
    
    class StakeholderEngagementEngine:
        def __init__(self, *args, **kwargs):
            pass


class StakeholderIntelligence:
    """
    Unified stakeholder intelligence interface
    Provides modern API while maintaining backward compatibility
    """
    
    def __init__(self, config=None, db_path: Optional[str] = None, enable_performance: bool = True):
        """Initialize stakeholder intelligence with optional config override"""
        self.config = config or get_config()
        self.db_path = db_path or self.config.database_path
        self.enable_performance = enable_performance
        
        # Initialize performance components
        if self.enable_performance:
            try:
                self.parallel_processor = ParallelProcessor(self.config)
                self.cache_manager = CacheManager(self.config)
                self.memory_optimizer = MemoryOptimizer(self.config)
            except Exception as e:
                logger.warning("Performance components unavailable, using standard processing", error=str(e))
                self.enable_performance = False
        
        # Initialize legacy components for functionality
        try:
            self.ai_engine = LocalStakeholderAI(self.db_path)
            self.detector = IntelligentStakeholderDetector(self.db_path)
            self.engagement_engine = StakeholderEngagementEngine(self.db_path)
        except Exception as e:
            raise AIDetectionError(f"Failed to initialize stakeholder intelligence: {e}")
    
    def detect_stakeholders_in_content(self, content: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect stakeholders in content using AI
        
        Args:
            content: Text content to analyze
            context: Context information (file_path, meeting_type, etc.)
            
        Returns:
            List of detected stakeholder candidates with confidence scores
        """
        try:
            return self.ai_engine.detect_stakeholders_in_content(content, context)
        except Exception as e:
            raise AIDetectionError(f"Stakeholder detection failed: {e}", detection_type="stakeholder")
    
    def process_content_for_stakeholders(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content and automatically handle stakeholder detection and creation
        
        Args:
            content: Text content to analyze
            context: Context information
            
        Returns:
            Processing results with counts and actions taken
        """
        if self.enable_performance:
            # Check cache first
            cache_key = f"stakeholder_detection:{hash(content)}:{hash(str(sorted(context.items())))}"
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug("Using cached stakeholder detection result")
                return cached_result
        
        try:
            # Try new method first, fallback to available methods
            if hasattr(self.detector, 'process_content_for_stakeholders'):
                result = self.detector.process_content_for_stakeholders(content, context)
            else:
                # Fallback: simulate the method with available functionality
                detected = self.ai_engine.detect_stakeholders_in_content(content, context)
                result = {
                    'candidates_detected': len(detected) if detected else 0,
                    'auto_created': 0,  # Would need actual creation logic
                    'profiling_needed': 0,  # Would need actual profiling logic
                    'updates_suggested': 0
                }
            
            # Cache successful results
            if self.enable_performance and result.get('candidates_detected', 0) > 0:
                self.cache_manager.set(cache_key, result, ttl_override=7200)  # 2 hour cache
            
            return result
        except Exception as e:
            raise AIDetectionError(f"Stakeholder processing failed: {e}", detection_type="stakeholder")
    
    def get_pending_profiling_tasks(self) -> List[Dict[str, Any]]:
        """Get stakeholders that need manual profiling"""
        try:
            return self.detector.get_pending_profiling_tasks()
        except Exception as e:
            raise DatabaseError(f"Failed to get profiling tasks: {e}")
    
    def get_pending_update_suggestions(self) -> List[Dict[str, Any]]:
        """Get pending stakeholder update suggestions"""
        try:
            return self.detector.get_pending_update_suggestions()
        except Exception as e:
            raise DatabaseError(f"Failed to get update suggestions: {e}")
    
    def list_stakeholders(self, filter_by: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all stakeholders with optional filtering
        
        Args:
            filter_by: Optional filters (importance, role, etc.)
            
        Returns:
            List of stakeholder profiles
        """
        try:
            return self.engagement_engine.list_stakeholders(filter_by or {})
        except Exception as e:
            raise DatabaseError(f"Failed to list stakeholders: {e}")
    
    def add_stakeholder(self, stakeholder_key: str, display_name: str, **kwargs) -> bool:
        """
        Add a new stakeholder manually
        
        Args:
            stakeholder_key: Unique identifier
            display_name: Human-readable name
            **kwargs: Additional stakeholder attributes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.engagement_engine.add_stakeholder(
                stakeholder_key=stakeholder_key,
                display_name=display_name,
                **kwargs
            )
        except Exception as e:
            raise DatabaseError(f"Failed to add stakeholder: {e}")
    
    def get_stakeholder(self, stakeholder_key: str) -> Optional[Dict[str, Any]]:
        """Get specific stakeholder by key"""
        try:
            return self.engagement_engine.get_stakeholder(stakeholder_key)
        except Exception as e:
            raise DatabaseError(f"Failed to get stakeholder: {e}")
    
    def update_stakeholder(self, stakeholder_key: str, **updates) -> bool:
        """Update stakeholder information"""
        try:
            return self.engagement_engine.update_stakeholder(stakeholder_key, **updates)
        except Exception as e:
            raise DatabaseError(f"Failed to update stakeholder: {e}")
    
    def generate_engagement_recommendations(self) -> List[Dict[str, Any]]:
        """Generate engagement recommendations for stakeholders"""
        try:
            return self.engagement_engine.generate_engagement_recommendations()
        except Exception as e:
            raise AIDetectionError(f"Failed to generate recommendations: {e}", detection_type="engagement")
    
    def process_workspace_for_stakeholders(self, workspace_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process entire workspace for stakeholder detection with performance optimization
        
        Args:
            workspace_path: Optional workspace path override
            
        Returns:
            Processing results with performance metrics
        """
        try:
            workspace_dir = Path(workspace_path) if workspace_path else self.config.workspace_path_obj
            
            # Find all relevant files
            file_patterns = ["*.md", "*.txt"]
            all_files = []
            
            for pattern in file_patterns:
                all_files.extend(workspace_dir.rglob(pattern))
            
            # Filter out small files
            relevant_files = [
                f for f in all_files 
                if f.stat().st_size > 10 and f.stat().st_size < 50 * 1024 * 1024  # 10 bytes to 50MB
            ]
            
            if not relevant_files:
                return {
                    'files_processed': 0,
                    'stakeholders_detected': 0,
                    'auto_created': 0,
                    'needs_profiling': 0,
                    'processing_time': 0.0
                }
            
            if self.enable_performance and len(relevant_files) > 3:
                # Use parallel processing for larger sets
                return self._process_files_parallel(relevant_files, workspace_dir)
            else:
                # Use sequential processing for small sets
                return self._process_files_sequential(relevant_files, workspace_dir)
                
        except Exception as e:
            raise AIDetectionError(f"Workspace processing failed: {e}", detection_type="stakeholder")
    
    def _process_files_parallel(self, files: List[Path], workspace_dir: Path) -> Dict[str, Any]:
        """Process files using parallel processing"""
        def process_single_file(file_path: Path) -> Optional[Dict[str, Any]]:
            try:
                if file_path.stat().st_size < 20:  # Skip very small files
                    return None
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content.strip()) < 20:
                    return None
                
                # Build context
                context = self._build_file_context(file_path, workspace_dir)
                
                # Process content
                result = self.process_content_for_stakeholders(content, context)
                return {
                    'file_path': str(file_path),
                    'result': result
                }
                
            except Exception as e:
                logger.warning("File processing error", file=str(file_path), error=str(e))
                return None
        
        # Use parallel processor
        parallel_result = self.parallel_processor.process_files_parallel(
            files, process_single_file, chunk_size=5
        )
        
        # Aggregate results
        total_stakeholders = 0
        total_auto_created = 0
        total_needs_profiling = 0
        
        for file_result in parallel_result['results']:
            if file_result and 'result' in file_result:
                result = file_result['result']
                total_stakeholders += result.get('candidates_detected', 0)
                total_auto_created += result.get('auto_created', 0)
                total_needs_profiling += result.get('profiling_needed', 0)
        
        return {
            'files_processed': len(parallel_result['results']),
            'stakeholders_detected': total_stakeholders,
            'auto_created': total_auto_created,
            'needs_profiling': total_needs_profiling,
            'processing_time': parallel_result['parallel_time'],
            'efficiency_gain': parallel_result['efficiency_gain'],
            'parallel_processing_used': True
        }
    
    def _process_files_sequential(self, files: List[Path], workspace_dir: Path) -> Dict[str, Any]:
        """Process files sequentially with memory optimization"""
        import time
        start_time = time.time()
        
        total_stakeholders = 0
        total_auto_created = 0
        total_needs_profiling = 0
        files_processed = 0
        
        if self.enable_performance:
            # Use memory-optimized chunked processing
            chunk_processor = lambda file_path: self._process_single_file_for_stakeholders(file_path, workspace_dir)
            
            for chunk_result in self.memory_optimizer.process_items_in_chunks(files, chunk_processor, chunk_size=10):
                for result in chunk_result['results']:
                    if result:
                        total_stakeholders += result.get('candidates_detected', 0)
                        total_auto_created += result.get('auto_created', 0) 
                        total_needs_profiling += result.get('profiling_needed', 0)
                        files_processed += 1
        else:
            # Standard sequential processing
            for file_path in files:
                result = self._process_single_file_for_stakeholders(file_path, workspace_dir)
                if result:
                    total_stakeholders += result.get('candidates_detected', 0)
                    total_auto_created += result.get('auto_created', 0)
                    total_needs_profiling += result.get('profiling_needed', 0)
                    files_processed += 1
        
        processing_time = time.time() - start_time
        
        return {
            'files_processed': files_processed,
            'stakeholders_detected': total_stakeholders,
            'auto_created': total_auto_created,
            'needs_profiling': total_needs_profiling,
            'processing_time': processing_time,
            'parallel_processing_used': False
        }
    
    def _process_single_file_for_stakeholders(self, file_path: Path, workspace_dir: Path) -> Optional[Dict[str, Any]]:
        """Process a single file for stakeholder detection"""
        try:
            if file_path.stat().st_size < 20:
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) < 20:
                return None
            
            context = self._build_file_context(file_path, workspace_dir)
            return self.process_content_for_stakeholders(content, context)
            
        except Exception as e:
            logger.warning("File processing error", file=str(file_path), error=str(e))
            return None
    
    def _build_file_context(self, file_path: Path, workspace_dir: Path) -> Dict[str, Any]:
        """Build context for file analysis"""
        relative_path = file_path.relative_to(workspace_dir)
        
        context = {
            'file_path': str(file_path),
            'relative_path': str(relative_path),
            'category': 'general'
        }
        
        # Determine category from path
        path_parts = relative_path.parts
        
        if 'meeting-prep' in path_parts:
            context['category'] = 'meeting_prep'
        elif 'initiatives' in path_parts or 'projects' in path_parts:
            context['category'] = 'current_initiatives'
        elif 'strategic' in path_parts:
            context['category'] = 'strategic_docs'
        
        return context
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get stakeholder system statistics with performance metrics"""
        stats = {}
        
        try:
            # Basic stakeholder stats
            try:
                db_manager = get_database_manager(self.db_path)
                stats.update(db_manager.get_table_info("stakeholder_profiles_enhanced"))
            except:
                stats["total_stakeholders"] = len(self.list_stakeholders())
            
            # Performance stats if available
            if self.enable_performance:
                stats["performance"] = {
                    "parallel_processor": self.parallel_processor.get_performance_stats(),
                    "cache_manager": self.cache_manager.get_cache_stats(),
                    "memory_optimizer": self.memory_optimizer.get_memory_stats()
                }
            
        except Exception as e:
            stats["error"] = str(e)
        
        return stats


# Backward compatibility functions
def get_stakeholder_intelligence(db_path: Optional[str] = None) -> StakeholderIntelligence:
    """Get stakeholder intelligence instance"""
    return StakeholderIntelligence(db_path=db_path)

def detect_stakeholders(content: str, context: Dict[str, Any], db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Convenience function for stakeholder detection"""
    intelligence = get_stakeholder_intelligence(db_path)
    return intelligence.detect_stakeholders_in_content(content, context)
