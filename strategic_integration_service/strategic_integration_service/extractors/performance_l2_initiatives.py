"""Performance-optimized L2 Strategic Initiative Extractor.

Enhanced version of L2InitiativeExtractor with:
- Multi-tier caching (memory, file, Redis)
- Parallel API requests
- Batch processing
- Performance monitoring
"""

from typing import Dict, List, Optional, Tuple

import structlog

from ..core.config import Settings
from ..models.initiative import L2Initiative
from ..utils.performance_jira_client import PerformanceExtractorMixin, PerformanceJiraClient
from .l2_initiatives import L2InitiativeExtractor

logger = structlog.get_logger(__name__)


class PerformanceL2InitiativeExtractor(PerformanceExtractorMixin, L2InitiativeExtractor):
    """Performance-optimized L2 strategic initiative extractor."""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.perf_client = PerformanceJiraClient(settings)

    def extract_with_parallelization(
        self,
        include_context: bool = True,
        warm_cache: bool = False,
    ) -> Tuple[List[L2Initiative], Optional[List[Dict]], Dict[str, any]]:
        """Extract L2 initiatives using parallel processing and caching.

        Returns:
            Tuple of (L2 initiatives, L1 context if requested, performance metrics)
        """
        logger.info("Starting performance-optimized L2 extraction")

        # Define parallel queries
        queries = [
            (
                "l2_initiatives",
                self.get_jql_query(),
                self.get_required_fields(),
                self.settings.jira_max_results,
            )
        ]

        if include_context:
            queries.append(
                (
                    "l1_context",
                    self._get_l1_context_query(),
                    self.get_required_fields(),
                    100,  # Smaller limit for context
                )
            )

        # Execute parallel queries
        results = self.extract_with_performance(queries, warm_cache=warm_cache)

        # Process L2 initiatives
        l2_initiatives = []
        raw_l2_issues = results.get("l2_initiatives", [])

        for issue_data in raw_l2_issues:
            try:
                initiative = L2Initiative.from_jira_issue(issue_data)
                if self._validate_l2_initiative(initiative):
                    l2_initiatives.append(initiative)
                else:
                    logger.warning(
                        "Issue failed L2 validation",
                        issue_key=initiative.key,
                        division=initiative.division,
                        initiative_type=initiative.initiative_type,
                    )
            except Exception as e:
                issue_key = issue_data.get("key", "unknown")
                logger.error("Failed to parse issue", issue_key=issue_key, error=str(e))

        # Process L1 context if requested
        l1_context = None
        if include_context:
            l1_context = results.get("l1_context", [])

        # Get performance metrics
        metrics = self.get_extraction_metrics()

        logger.info(
            "Performance-optimized extraction completed",
            l2_count=len(l2_initiatives),
            l1_context_count=len(l1_context) if l1_context else 0,
            **metrics,
        )

        return l2_initiatives, l1_context, metrics

    def extract_batch_optimized(
        self,
        batch_size: Optional[int] = None,
        max_total: Optional[int] = None,
    ) -> List[L2Initiative]:
        """Extract L2 initiatives using optimized batch processing."""
        batch_size = batch_size or self.settings.batch_size
        max_total = max_total or self.settings.jira_max_results

        logger.info(
            "Starting batch-optimized L2 extraction",
            batch_size=batch_size,
            max_total=max_total,
        )

        # Use performance client for batch processing
        raw_issues = self.perf_client.batch_search_with_pagination(
            base_jql=self.get_jql_query(),
            batch_size=batch_size,
            max_total=max_total,
            fields=self.get_required_fields(),
        )

        # Process issues into L2Initiative objects
        l2_initiatives = []
        for issue_data in raw_issues:
            try:
                initiative = L2Initiative.from_jira_issue(issue_data)
                if self._validate_l2_initiative(initiative):
                    l2_initiatives.append(initiative)
            except Exception as e:
                issue_key = issue_data.get("key", "unknown")
                logger.error("Failed to parse issue", issue_key=issue_key, error=str(e))

        logger.info(
            "Batch-optimized extraction completed",
            total_processed=len(raw_issues),
            valid_l2_initiatives=len(l2_initiatives),
        )

        return l2_initiatives

    def warm_extraction_cache(self) -> None:
        """Pre-warm cache with commonly used L2 extraction queries."""
        logger.info("Warming L2 extraction cache")

        common_queries = [
            (
                "l2_all",
                self.get_jql_query(),
                self.get_required_fields(),
                self.settings.jira_max_results,
            ),
            (
                "l1_context",
                self._get_l1_context_query(),
                self.get_required_fields(),
                100,
            ),
        ]

        self.perf_client.warm_cache(common_queries)
        logger.info("L2 extraction cache warmed")

    def _get_l1_context_query(self) -> str:
        """Get JQL query for L1 context initiatives."""
        excluded_statuses = ["Done", "Closed", "Completed", "Canceled", "Released"]
        status_filter = ", ".join(f'"{status}"' for status in excluded_statuses)

        return (
            f"project = PI "
            f'AND division in ("{self.division_filter}") '
            f"AND type = L1 "
            f"AND status not in ({status_filter}) "
            f"ORDER BY priority DESC, updated DESC"
        )

    def get_performance_report(self) -> Dict[str, any]:
        """Generate detailed performance report."""
        metrics = self.get_extraction_metrics()

        cache_efficiency = (
            "Excellent"
            if metrics.get("cache_hit_rate", 0) > 0.8
            else "Good"
            if metrics.get("cache_hit_rate", 0) > 0.5
            else "Needs Improvement"
        )

        api_efficiency = (
            "Excellent"
            if metrics.get("average_api_time", 1) < 0.5
            else "Good"
            if metrics.get("average_api_time", 1) < 1.0
            else "Needs Improvement"
        )

        return {
            "extraction_metrics": metrics,
            "cache_efficiency": cache_efficiency,
            "api_efficiency": api_efficiency,
            "recommendations": self._get_performance_recommendations(metrics),
        }

    def _get_performance_recommendations(self, metrics: Dict[str, any]) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        cache_hit_rate = metrics.get("cache_hit_rate", 0)
        if cache_hit_rate < 0.5:
            recommendations.append(
                "Cache hit rate is low. Consider increasing cache TTL or pre-warming cache."
            )

        avg_api_time = metrics.get("average_api_time", 0)
        if avg_api_time > 1.0:
            recommendations.append(
                "API response times are slow. Consider optimizing JQL queries or increasing parallel requests."
            )

        api_calls = metrics.get("api_calls", 0)
        parallel_requests = metrics.get("parallel_requests", 0)
        if api_calls > 10 and parallel_requests == 0:
            recommendations.append(
                "Many sequential API calls detected. Consider using parallel processing."
            )

        if not recommendations:
            recommendations.append("Performance is optimal. No recommendations at this time.")

        return recommendations

    def close(self) -> None:
        """Close extractor and log performance summary."""
        if hasattr(self, "perf_client"):
            report = self.get_performance_report()
            logger.info("L2 Extractor Performance Summary", **report)
            self.perf_client.close()
        super().close()


def create_optimized_extractor(settings: Settings) -> PerformanceL2InitiativeExtractor:
    """Factory function to create optimized L2 extractor."""
    return PerformanceL2InitiativeExtractor(settings)
