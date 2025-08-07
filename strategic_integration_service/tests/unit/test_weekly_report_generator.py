"""Unit tests for WeeklyReportGenerator."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from strategic_integration_service.core.config import Settings
from strategic_integration_service.generators.weekly_report import WeeklyReportGenerator
from strategic_integration_service.models.initiative import CurrentInitiative, JiraProject
from strategic_integration_service.models.report import InitiativeHealthStatus, ReportType, WeeklyReportData


class TestWeeklyReportGenerator:
    """Test cases for WeeklyReportGenerator."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        return Settings(
            jira_base_url="https://test.atlassian.net",
            jira_api_token="test-token",
            jira_email="test@example.com",
            output_base_dir="/tmp/test-output"
        )

    @pytest.fixture
    def generator(self, settings):
        """Create WeeklyReportGenerator instance."""
        return WeeklyReportGenerator(settings)

    @pytest.fixture
    def sample_initiative(self):
        """Create a sample CurrentInitiative for testing."""
        return CurrentInitiative(
            key="UIS-123",
            summary="Test Initiative",
            description="Test description",
            status="In Progress",
            priority="High",
            created=datetime.now() - timedelta(days=5),
            updated=datetime.now() - timedelta(days=1),
            assignee=None,
            reporter=None,
            project=JiraProject(key="UIS", name="Web Platform"),
            labels=["platform-foundation"],
            components=["core"],
            fix_versions=["2025.1"],
            raw_data={}
        )

    def test_get_report_type(self, generator):
        """Test that generator returns correct report type."""
        assert generator.get_report_type() == ReportType.WEEKLY_SLT

    def test_determine_initiative_health_high_priority_recent_update(self, generator, sample_initiative):
        """Test health determination for high priority with recent update."""
        sample_initiative.priority = "Highest"
        sample_initiative.updated = datetime.now() - timedelta(days=2)

        health = generator.determine_initiative_health(sample_initiative)
        assert health == InitiativeHealthStatus.GREEN

    def test_determine_initiative_health_high_priority_stale_update(self, generator, sample_initiative):
        """Test health determination for high priority with stale update."""
        sample_initiative.priority = "Highest"
        sample_initiative.updated = datetime.now() - timedelta(days=10)

        health = generator.determine_initiative_health(sample_initiative)
        assert health == InitiativeHealthStatus.YELLOW

    def test_determine_initiative_health_at_risk(self, generator, sample_initiative):
        """Test health determination for at-risk initiative."""
        sample_initiative.labels = ["at-risk"]

        health = generator.determine_initiative_health(sample_initiative)
        assert health == InitiativeHealthStatus.RED

    def test_calculate_team_health_all_green(self, generator, sample_initiative):
        """Test team health calculation with all green initiatives."""
        initiatives = [sample_initiative] * 3

        with patch.object(generator, 'determine_initiative_health', return_value=InitiativeHealthStatus.GREEN):
            health = generator.calculate_team_health(initiatives)
            assert health == InitiativeHealthStatus.GREEN

    def test_calculate_team_health_high_red_percentage(self, generator, sample_initiative):
        """Test team health calculation with high red percentage."""
        initiatives = [sample_initiative] * 5

        def mock_health(init):
            return InitiativeHealthStatus.RED

        with patch.object(generator, 'determine_initiative_health', side_effect=mock_health):
            health = generator.calculate_team_health(initiatives)
            assert health == InitiativeHealthStatus.RED

    def test_group_initiatives_by_team(self, generator):
        """Test grouping initiatives by team."""
        now = datetime.now()
        init1 = CurrentInitiative(
            key="UIS-1", summary="Test 1", project=JiraProject(key="UIS", name="Web Platform"),
            status="In Progress", priority="Medium", created=now, updated=now, raw_data={}
        )
        init2 = CurrentInitiative(
            key="WES-1", summary="Test 2", project=JiraProject(key="WES", name="Experience Services"),
            status="In Progress", priority="Medium", created=now, updated=now, raw_data={}
        )
        init3 = CurrentInitiative(
            key="UIS-2", summary="Test 3", project=JiraProject(key="UIS", name="Web Platform"),
            status="In Progress", priority="Medium", created=now, updated=now, raw_data={}
        )

        initiatives = [init1, init2, init3]
        grouped = generator.group_initiatives_by_team(initiatives)

        assert len(grouped) == 2
        assert "Web Platform" in grouped
        assert "Experience Services" in grouped
        assert len(grouped["Web Platform"]) == 2
        assert len(grouped["Experience Services"]) == 1

    def test_filter_by_date_range(self, generator):
        """Test filtering initiatives by date range."""
        now = datetime.now()
        init1 = CurrentInitiative(
            key="UIS-1", summary="Test 1", project=JiraProject(key="UIS", name="Web Platform"),
            status="In Progress", priority="Medium", created=now, updated=now - timedelta(days=2),
            raw_data={}
        )
        init2 = CurrentInitiative(
            key="UIS-2", summary="Test 2", project=JiraProject(key="UIS", name="Web Platform"),
            status="In Progress", priority="Medium", created=now, updated=now - timedelta(days=10),
            raw_data={}
        )

        initiatives = [init1, init2]
        start_date = now - timedelta(days=5)
        end_date = now

        filtered = generator.filter_by_date_range(initiatives, start_date, end_date, 'updated')

        assert len(filtered) == 1
        assert filtered[0].key == "UIS-1"

    @pytest.mark.asyncio
    async def test_collect_data(self, generator):
        """Test data collection."""
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()

        mock_active = [MagicMock()]
        mock_epics = [MagicMock()]
        mock_completed = [MagicMock()]

        with patch('asyncio.run') as mock_run:
            mock_run.return_value = (mock_active, mock_epics, mock_completed)

            data = generator.collect_data(period_start, period_end)

            assert 'active_initiatives' in data
            assert 'strategic_epics' in data
            assert 'recent_completed' in data
            assert 'data_sources' in data
            assert data['active_initiatives'] == mock_active
            assert data['strategic_epics'] == mock_epics
            assert data['recent_completed'] == mock_completed

    def test_analyze_data(self, generator, sample_initiative):
        """Test data analysis."""
        period_start = datetime.now() - timedelta(days=7)
        period_end = datetime.now()

        # Create test initiatives
        now = datetime.now()
        completed_initiative = CurrentInitiative(
            key="UIS-DONE", summary="Completed", project=JiraProject(key="UIS", name="Web Platform"),
            status="Done", priority="High", created=now, updated=now,
            resolution_date=now - timedelta(days=2),
            raw_data={}
        )

        raw_data = {
            'active_initiatives': [sample_initiative],
            'strategic_epics': [],
            'recent_completed': [completed_initiative],
            'period_start': period_start,
            'period_end': period_end,
            'data_sources': ['Test Source']
        }

        with patch.object(generator, 'filter_by_date_range', return_value=[completed_initiative]):
            with patch.object(generator, '_generate_team_highlights', return_value=['Test highlight']):
                with patch.object(generator, '_identify_major_completions', return_value=[]):
                    with patch.object(generator, '_identify_escalations', return_value=[]):
                        with patch.object(generator, '_generate_upcoming_milestones', return_value=[]):
                            with patch.object(generator, '_calculate_platform_health', return_value={}):
                                analyzed = generator.analyze_data(raw_data)

        assert 'total_active_initiatives' in analyzed
        assert 'completed_this_week' in analyzed
        assert 'team_summaries' in analyzed
        assert analyzed['total_active_initiatives'] == 1

    def test_generate_report_data(self, generator):
        """Test report data generation."""
        analyzed_data = {
            'total_active_initiatives': 5,
            'completed_this_week': 2,
            'at_risk_count': 1,
            'high_priority_count': 3,
            'team_summaries': {'Test Team': {'health': InitiativeHealthStatus.GREEN}},
            'major_completions': [],
            'escalations': [],
            'upcoming_milestones': [],
            'platform_health': {}
        }

        report_data = generator.generate_report_data(analyzed_data)

        assert isinstance(report_data, WeeklyReportData)
        assert report_data.total_active_initiatives == 5
        assert report_data.completed_this_week == 2
        assert report_data.at_risk_count == 1
        assert report_data.high_priority_count == 3

    def test_generate_team_highlights(self, generator):
        """Test team highlights generation."""
        now = datetime.now()
        completed_high_priority = CurrentInitiative(
            key="UIS-1", summary="High Priority Completed", project=JiraProject(key="UIS", name="Web Platform"),
            status="Done", priority="Highest", created=now, updated=now,
            raw_data={}
        )

        active_at_risk = CurrentInitiative(
            key="UIS-2", summary="At Risk Initiative", project=JiraProject(key="UIS", name="Web Platform"),
            status="In Progress", priority="Medium", created=now, updated=now,
            labels=["at-risk"], raw_data={}
        )

        team_initiatives = [active_at_risk]
        team_completed = [completed_high_priority]

        highlights = generator._generate_team_highlights(team_initiatives, team_completed)

        assert len(highlights) > 0
        assert any("Completed:" in highlight for highlight in highlights)
        assert any("at risk" in highlight for highlight in highlights)

    def test_identify_major_completions(self, generator):
        """Test major completions identification."""
        now = datetime.now()
        high_priority_completed = CurrentInitiative(
            key="UIS-1", summary="Major Feature", project=JiraProject(key="UIS", name="Web Platform"),
            status="Done", priority="Highest", created=now, updated=now,
            raw_data={}
        )

        regular_completed = CurrentInitiative(
            key="UIS-2", summary="Regular Task", project=JiraProject(key="UIS", name="Web Platform"),
            status="Done", priority="Medium", created=now, updated=now,
            raw_data={}
        )

        completed = [high_priority_completed, regular_completed]

        with patch.object(generator, '_truncate_description', return_value="Test description"):
            with patch.object(generator, '_assess_completion_impact', return_value="High impact"):
                major = generator._identify_major_completions(completed)

        assert len(major) == 1
        assert major[0]['key'] == "UIS-1"
        assert major[0]['priority'] == "Highest"

    def test_identify_escalations(self, generator):
        """Test escalations identification."""
        now = datetime.now()
        blocked_high_priority = CurrentInitiative(
            key="UIS-1", summary="Blocked Task", project=JiraProject(key="UIS", name="Web Platform"),
            status="In Progress", priority="Highest", created=now, updated=now,
            labels=["blocked"], raw_data={}
        )

        stale_epic = CurrentInitiative(
            key="PI-1", summary="Stale Epic", project=JiraProject(key="PI", name="Platform Initiatives"),
            status="In Progress", priority="High", created=now,
            updated=now - timedelta(days=20), raw_data={}
        )

        active = [blocked_high_priority]
        epics = [stale_epic]

        with patch.object(generator, '_identify_escalation_issue', return_value="Test issue"):
            with patch.object(generator, '_generate_escalation_recommendation', return_value="Test recommendation"):
                escalations = generator._identify_escalations(active, epics)

        assert len(escalations) == 2
        assert any(esc['key'] == "UIS-1" for esc in escalations)
        assert any(esc['key'] == "PI-1" for esc in escalations)

    def test_calculate_platform_health(self, generator):
        """Test platform health calculation."""
        now = datetime.now()
        platform_initiative = CurrentInitiative(
            key="UIS-1", summary="Platform Work", project=JiraProject(key="UIS", name="Web Platform"),
            status="In Progress", priority="High", created=now, updated=now,
            labels=["platform-foundation"], raw_data={}
        )

        design_initiative = CurrentInitiative(
            key="UXI-1", summary="Design System", project=JiraProject(key="UXI", name="Design Systems"),
            status="In Progress", priority="Medium", created=now, updated=now,
            labels=["design-system"], raw_data={}
        )

        initiatives = [platform_initiative, design_initiative]

        with patch.object(generator, 'calculate_team_health') as mock_team_health:
            mock_team_health.return_value = InitiativeHealthStatus.GREEN

            health = generator._calculate_platform_health(initiatives, [])

        assert 'Foundation & Architecture' in health
        assert 'Design Systems' in health
        assert 'Overall' in health

    def test_generate_executive_summary(self, generator):
        """Test executive summary generation."""
        report_data = {
            'total_active_initiatives': 10,
            'completed_this_week': 3,
            'at_risk_count': 2,
            'team_summaries': {'Team A': {}, 'Team B': {}},
            'platform_health': {
                'Overall': InitiativeHealthStatus.GREEN,
                'Design Systems': InitiativeHealthStatus.RED
            }
        }

        summary = generator.generate_executive_summary(report_data)

        assert "10 active initiatives" in summary
        assert "3 initiatives this week" in summary
        assert "2 initiatives require immediate attention" in summary
        assert "Design Systems" in summary

    def test_generate_recommendations(self, generator):
        """Test recommendations generation."""
        analyzed_data = {
            'escalations': [{'title': 'Test Escalation'}],
            'completed_this_week': 1,
            'total_active_initiatives': 20,
            'at_risk_count': 3,
            'team_summaries': {}
        }

        recommendations = generator.generate_recommendations(analyzed_data)

        assert len(recommendations) > 0
        assert any("escalated initiatives" in rec for rec in recommendations)
        assert any("completion velocity" in rec for rec in recommendations)
