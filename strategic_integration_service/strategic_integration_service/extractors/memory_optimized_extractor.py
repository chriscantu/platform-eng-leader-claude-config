"""Memory-optimized extractors for large dataset processing."""

from typing import Any, Dict, Iterator, List, Optional

import structlog

from ..core.config import Settings
from ..models.initiative import CurrentInitiative, L2Initiative
from ..utils.memory_optimization import (
    LazyJiraLoader,
    MemoryEfficientProcessor,
    chunked_processing,
    memory_monitoring,
)
from ..utils.performance_jira_client import PerformanceJiraClient
from .current_initiatives import CurrentInitiativesExtractor
from .l2_initiatives import L2InitiativeExtractor

logger = structlog.get_logger(__name__)


class MemoryOptimizedL2Extractor(L2InitiativeExtractor):
    """Memory-optimized L2 initiative extractor for large datasets."""

    def __init__(self, settings: Settings, max_memory_mb: int = 512):
        super().__init__(settings)
        self.perf_client = PerformanceJiraClient(settings)
        self.processor = MemoryEfficientProcessor(max_memory_mb)

    def extract_streaming(
        self, batch_size: int = 50, max_total: Optional[int] = None
    ) -> Iterator[L2Initiative]:
        """Extract L2 initiatives using streaming processing."""

        with memory_monitoring("l2_streaming_extraction") as monitor:
            logger.info(
                "Starting streaming L2 extraction", batch_size=batch_size, max_total=max_total
            )

            monitor.checkpoint("setup_complete")

            # Create lazy loader
            loader = LazyJiraLoader(
                self.perf_client, self.get_jql_query(), self.get_required_fields(), batch_size
            )

            count = 0
            processed = 0

            for issue_data in loader:
                if max_total and count >= max_total:
                    break

                count += 1

                try:
                    initiative = L2Initiative.from_jira_issue(issue_data)
                    if self._validate_l2_initiative(initiative):
                        processed += 1
                        yield initiative

                        if processed % 100 == 0:
                            monitor.checkpoint(f"processed_{processed}")

                except Exception as e:
                    issue_key = issue_data.get("key", "unknown")
                    logger.error("Failed to parse issue", issue_key=issue_key, error=str(e))

            monitor.checkpoint("extraction_complete")
            logger.info(
                "Streaming extraction completed", total_processed=count, valid_initiatives=processed
            )

    def extract_chunked(
        self, chunk_size: int = 100, max_total: Optional[int] = None
    ) -> List[L2Initiative]:
        """Extract L2 initiatives using chunked processing."""

        with memory_monitoring("l2_chunked_extraction") as monitor:
            logger.info(
                "Starting chunked L2 extraction", chunk_size=chunk_size, max_total=max_total
            )

            # First, get all raw issues
            raw_issues = self.perf_client.batch_search_with_pagination(
                base_jql=self.get_jql_query(),
                batch_size=chunk_size,
                max_total=max_total or self.settings.jira_max_results,
                fields=self.get_required_fields(),
            )

            monitor.checkpoint("raw_data_loaded")

            # Process in chunks to manage memory
            all_initiatives = []

            def process_chunk(chunk: List[Dict[str, Any]]) -> List[L2Initiative]:
                """Process a chunk of raw issues."""
                initiatives = []
                for issue_data in chunk:
                    try:
                        initiative = L2Initiative.from_jira_issue(issue_data)
                        if self._validate_l2_initiative(initiative):
                            initiatives.append(initiative)
                    except Exception as e:
                        issue_key = issue_data.get("key", "unknown")
                        logger.error("Failed to parse issue", issue_key=issue_key, error=str(e))
                return initiatives

            # Process chunks
            for i, chunk in enumerate(chunked_processing(raw_issues, chunk_size, process_chunk)):
                all_initiatives.extend(chunk)
                monitor.checkpoint(f"chunk_{i}_processed")
                logger.debug(
                    "Chunk processed",
                    chunk_number=i,
                    chunk_size=len(chunk),
                    total_so_far=len(all_initiatives),
                )

            monitor.checkpoint("all_chunks_processed")
            logger.info("Chunked extraction completed", total_initiatives=len(all_initiatives))

            return all_initiatives

    def extract_memory_optimized(self, strategy: str = "chunked", **kwargs) -> List[L2Initiative]:
        """Extract using specified memory optimization strategy."""

        if strategy == "streaming":
            return list(self.extract_streaming(**kwargs))
        elif strategy == "chunked":
            return self.extract_chunked(**kwargs)
        elif strategy == "processor":
            return self._extract_with_processor(**kwargs)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _extract_with_processor(self, **kwargs) -> List[L2Initiative]:
        """Extract using MemoryEfficientProcessor."""

        def process_issue(issue_data: Dict[str, Any]) -> Optional[L2Initiative]:
            """Process a single issue."""
            try:
                initiative = L2Initiative.from_jira_issue(issue_data)
                if self._validate_l2_initiative(initiative):
                    return initiative
            except Exception as e:
                issue_key = issue_data.get("key", "unknown")
                logger.error("Failed to parse issue", issue_key=issue_key, error=str(e))
            return None

        return self.processor.process_jira_data(
            self.perf_client,
            self.get_jql_query(),
            self.get_required_fields(),
            process_issue,
            kwargs.get("batch_size", 50),
        )


class MemoryOptimizedCurrentExtractor(CurrentInitiativesExtractor):
    """Memory-optimized current initiatives extractor."""

    def __init__(self, settings: Settings, max_memory_mb: int = 512):
        super().__init__(settings)
        self.perf_client = PerformanceJiraClient(settings)
        self.processor = MemoryEfficientProcessor(max_memory_mb)

    def extract_all_optimized(
        self, strategy: str = "chunked", batch_size: int = 50
    ) -> Dict[str, List[Any]]:
        """Extract all current initiatives using memory optimization."""

        with memory_monitoring("current_initiatives_extraction") as monitor:
            logger.info("Starting memory-optimized current initiatives extraction")

            # Define extraction queries
            queries = [
                ("active", self.get_active_initiatives_jql()),
                ("epics", self.get_strategic_epics_jql()),
                ("completed", self.get_recent_completed_jql()),
            ]

            results = {}

            for query_name, jql in queries:
                monitor.checkpoint(f"start_{query_name}")

                if strategy == "chunked":
                    raw_issues = self.perf_client.batch_search_with_pagination(
                        base_jql=jql,
                        batch_size=batch_size,
                        max_total=200,  # Reasonable limit for current initiatives
                        fields=self.get_required_fields(),
                    )

                    # Process in chunks
                    initiatives = []
                    for chunk in chunked_processing(raw_issues, batch_size):
                        for issue_data in chunk:
                            try:
                                initiative = CurrentInitiative.from_jira_issue(issue_data)
                                initiatives.append(initiative)
                            except Exception as e:
                                issue_key = issue_data.get("key", "unknown")
                                logger.error(
                                    "Failed to parse issue", issue_key=issue_key, error=str(e)
                                )

                    results[query_name] = initiatives

                else:
                    # Use processor strategy
                    def process_issue(issue_data: Dict[str, Any]) -> Optional[CurrentInitiative]:
                        try:
                            return CurrentInitiative.from_jira_issue(issue_data)
                        except Exception as e:
                            issue_key = issue_data.get("key", "unknown")
                            logger.error("Failed to parse issue", issue_key=issue_key, error=str(e))
                            return None

                    results[query_name] = self.processor.process_jira_data(
                        self.perf_client,
                        jql,
                        self.get_required_fields(),
                        process_issue,
                        batch_size,
                    )

                monitor.checkpoint(f"end_{query_name}")
                logger.info(f"Completed {query_name} extraction", count=len(results[query_name]))

            logger.info(
                "Memory-optimized extraction completed",
                results_summary={k: len(v) for k, v in results.items()},
            )

            return results


def compare_memory_strategies(settings: Settings, max_results: int = 500) -> Dict[str, Any]:
    """Compare different memory optimization strategies."""

    logger.info("Starting memory strategy comparison")

    extractor = MemoryOptimizedL2Extractor(settings)
    results = {}

    strategies = ["chunked", "streaming", "processor"]

    for strategy in strategies:
        logger.info(f"Testing strategy: {strategy}")

        with memory_monitoring(f"strategy_{strategy}") as monitor:
            try:
                if strategy == "streaming":
                    # Convert iterator to list for comparison
                    initiatives = list(
                        extractor.extract_streaming(batch_size=50, max_total=max_results)
                    )
                else:
                    initiatives = extractor.extract_memory_optimized(
                        strategy=strategy, chunk_size=50, batch_size=50, max_total=max_results
                    )

                results[strategy] = {
                    "success": True,
                    "initiative_count": len(initiatives),
                    "memory_report": monitor.get_report(),
                }

            except Exception as e:
                logger.error(f"Strategy {strategy} failed", error=str(e))
                results[strategy] = {
                    "success": False,
                    "error": str(e),
                    "memory_report": monitor.get_report(),
                }

    # Analyze results
    successful_strategies = {k: v for k, v in results.items() if v["success"]}

    if successful_strategies:
        # Find most memory efficient
        memory_efficient = min(
            successful_strategies.items(), key=lambda x: x[1]["memory_report"]["peak_mb"]
        )

        # Find fastest (assuming lower peak memory correlates with speed)
        fastest = min(
            successful_strategies.items(), key=lambda x: len(x[1]["memory_report"]["checkpoints"])
        )

        comparison_summary = {
            "most_memory_efficient": {
                "strategy": memory_efficient[0],
                "peak_memory_mb": memory_efficient[1]["memory_report"]["peak_mb"],
            },
            "fastest": {
                "strategy": fastest[0],
                "checkpoints": len(fastest[1]["memory_report"]["checkpoints"]),
            },
        }
    else:
        comparison_summary = {"error": "No strategies succeeded"}

    logger.info("Memory strategy comparison completed", summary=comparison_summary)

    return {
        "strategy_results": results,
        "comparison_summary": comparison_summary,
    }
