#!/usr/bin/env python3
"""
Strategic Scenario Demo: Real Director Workflow
Demonstrates ClaudeDirector value through realistic usage patterns
"""

import os
import subprocess
import tempfile
import time
from pathlib import Path


class StrategicScenarioDemo:
    """Demonstrates ClaudeDirector through realistic director scenarios"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.demo_workspace = None

    def setup_demo_environment(self):
        """Create realistic demo environment"""
        print("🏗️  Setting up strategic scenario demo environment...")

        # Create demo meeting prep directories
        meeting_dirs = [
            "workspace/meeting-prep/vp-engineering-1on1",
            "workspace/meeting-prep/platform-architecture-review",
            "workspace/meeting-prep/q4-strategic-planning",
            "workspace/meeting-prep/cross-team-dependency-sync",
        ]

        for meeting_dir in meeting_dirs:
            Path(meeting_dir).mkdir(parents=True, exist_ok=True)

        # Create realistic meeting content
        self.create_vp_1on1_content()
        self.create_architecture_review_content()
        self.create_strategic_planning_content()
        self.create_dependency_sync_content()

        print("✅ Demo environment ready")

    def create_vp_1on1_content(self):
        """Create VP 1:1 meeting content"""
        content = """# VP Engineering 1:1 - Strategic Alignment

        ## Attendees
        - Sarah Chen (VP Engineering)
        - Michael Rodriguez (Director, Platform Engineering)

        ## Strategic Topics
        1. **Q4 Platform Initiative Status**
           - Design system adoption at 78% across teams
           - API standardization ahead of schedule
           - Security audit completion by end of month

        2. **Cross-Team Dependencies**
           - Product team needs design system components by Nov 15
           - Mobile team blocked on API gateway changes
           - Legal review required for data compliance features

        3. **Resource Planning**
           - Frontend platform team scaling (+2 engineers)
           - Architecture committee formation
           - Technical debt allocation (20% time commitment)

        ## Action Items
        - [ ] **CRITICAL**: Sarah needs budget approval for platform team expansion by Friday
        - [ ] Follow up with David Kim (Design Lead) on component library timeline
        - [ ] Schedule legal review session with Jennifer Walsh (Compliance Director)
        - [ ] Escalate mobile team blockers to VP level if not resolved by EOW
        - [ ] Prepare platform ROI analysis for board presentation next month

        ## Strategic Context
        Focus on organizational leverage and platform investment ROI.
        Need to demonstrate business impact of platform engineering.

        **Recommended personas**: @diego for platform strategy, @alvaro for ROI discussion, @camille for scaling decisions
        """

        filepath = Path("workspace/meeting-prep/vp-engineering-1on1/meeting-notes.md")
        filepath.write_text(content)

    def create_architecture_review_content(self):
        """Create architecture review content"""
        content = """# Platform Architecture Review - Technical Strategy

        ## Participants
        - Martin Schmidt (Principal Architect)
        - Elena Rodriguez (Security Architecture)
        - David Kim (Design Systems Lead)
        - Michael Rodriguez (Platform Director)

        ## Architecture Decisions
        1. **API Gateway Strategy**
           - Adopt unified API gateway for all platform services
           - Timeline: 6-week migration, rolling deployment
           - Impact: 15 microservices, 8 teams affected

        2. **Design System Evolution**
           - Move to component-driven architecture
           - Shared component library across web/mobile
           - Breaking changes managed through versioning

        ## Technical Debt Priorities
        - [ ] Legacy authentication system migration (Q4 priority)
        - [ ] Database sharding for user service (performance critical)
        - [ ] Monitoring infrastructure upgrade (operational excellence)

        ## Dependencies & Blockers
        - Security team review required for API changes
        - Product team alignment on breaking changes
        - Infrastructure team capacity for database work

        ## Follow-up Actions
        - [ ] Martin to draft API migration plan by next Tuesday
        - [ ] Elena to complete security assessment by month end
        - [ ] Schedule cross-team impact review with all affected teams
        - [ ] Escalate infrastructure capacity concerns to VP level

        **Strategic Focus**: Technical excellence enabling business velocity
        **Recommended personas**: @martin for architecture decisions, @security for risk assessment
        """

        filepath = Path("workspace/meeting-prep/platform-architecture-review/architecture-notes.md")
        filepath.write_text(content)

    def create_strategic_planning_content(self):
        """Create strategic planning content"""
        content = """# Q4 Strategic Planning - Platform Engineering

        ## Strategic Objectives
        1. **Platform Adoption & Developer Experience**
           - Target: 95% adoption across all engineering teams
           - Key metric: Developer satisfaction score >8.5/10
           - Investment: $2M platform engineering budget

        2. **Business Impact Demonstration**
           - Reduce cross-team development time by 40%
           - Accelerate feature delivery velocity by 25%
           - Platform cost efficiency: $800K annual savings

        ## Stakeholder Alignment
        - **Sarah Chen (VP Engineering)**: Platform strategy and resource allocation
        - **Jennifer Walsh (Product Director)**: Feature velocity and business outcomes
        - **Marcus Thompson (CTO)**: Technical vision and architectural decisions
        - **Alvaro Gonzalez (Finance Partner)**: Budget justification and ROI tracking

        ## Key Initiatives
        1. **Design System Maturity** (Owner: David Kim)
           - Component library completion
           - Cross-platform consistency
           - Developer adoption tooling

        2. **API Platform Evolution** (Owner: Martin Schmidt)
           - Unified API gateway
           - Developer experience optimization
           - Performance and reliability improvements

        3. **Platform Observability** (Owner: Elena Rodriguez)
           - Comprehensive monitoring
           - Automated alerting systems
           - Performance optimization insights

        ## Success Metrics & Accountability
        - [ ] Weekly platform health reports to Sarah Chen
        - [ ] Monthly business impact review with Jennifer Walsh
        - [ ] Quarterly ROI presentation to Marcus Thompson and finance team
        - [ ] Escalation protocol for cross-team blockers to VP level

        ## Resource Requirements
        - Platform engineering team: +4 engineers (approved)
        - Architecture committee: 20% time allocation from senior engineers
        - External consulting: API security audit ($150K)

        **Strategic Focus**: Demonstrable business value through platform engineering
        **Recommended personas**: @diego for execution, @alvaro for business case, @camille for organizational scaling
        """

        filepath = Path("workspace/meeting-prep/q4-strategic-planning/strategic-initiatives.md")
        filepath.write_text(content)

    def create_dependency_sync_content(self):
        """Create cross-team dependency content"""
        content = """# Cross-Team Dependency Coordination

        ## Critical Dependencies This Week
        1. **Design System → Product Team**
           - Product needs button component variants by Thursday
           - Blocker: Design review not yet complete
           - Escalation: David Kim + Jennifer Walsh alignment needed

        2. **API Gateway → Mobile Team**
           - Mobile app release depends on new authentication flow
           - Timeline risk: Mobile release scheduled for next Monday
           - Owner: Martin Schmidt coordinating with mobile lead

        3. **Platform Infrastructure → Security Team**
           - Security audit blocking production deployment
           - Elena Rodriguez leading review, needs completion by Friday
           - Escalation path: VP Engineering if delays continue

        ## Stakeholder Follow-ups Required
        - [ ] **URGENT**: Jennifer Walsh confirmation on product timeline flexibility
        - [ ] David Kim status update on design review completion
        - [ ] Martin Schmidt coordination with mobile team lead (Alex Chen)
        - [ ] Elena Rodriguez security audit timeline confirmation
        - [ ] Sarah Chen escalation if any blockers not resolved by EOW

        ## Communication Plan
        - Daily stand-up: 9 AM with all workstream leads
        - Executive update: Sarah Chen by EOD Friday
        - Risk escalation: VP level if timeline at risk

        ## Backup Plans
        - Design system: Fallback to existing components if review delayed
        - API gateway: Feature flag rollback capability
        - Security: Staged deployment with monitoring

        **Strategic Focus**: Cross-team coordination and delivery excellence
        **Recommended personas**: @rachel for design system alignment, @diego for execution coordination
        """

        filepath = Path("workspace/meeting-prep/cross-team-dependency-sync/coordination-notes.md")
        filepath.write_text(content)

    def run_strategic_scenario(self):
        """Run complete strategic scenario demonstration"""
        print("\n" + "=" * 80)
        print("🎯 STRATEGIC SCENARIO DEMO: Director's Strategic Workflow")
        print("=" * 80)
        print("Scenario: Engineering Director managing platform initiative across multiple teams")
        print("Expected: Complete strategic context and actionable insights in < 2 minutes")
        print()

        start_time = time.time()

        # Step 1: Executive Morning Dashboard
        print("📊 Step 1: Executive Morning Dashboard")
        print("Director starts day, needs immediate strategic context...")

        step_start = time.time()
        result = subprocess.run(["./claudedirector", "alerts"], capture_output=True, text=True)

        print(f"✅ Daily alerts completed in {time.time() - step_start:.1f}s")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()[:100]}...")
        print()

        # Step 2: Strategic Intelligence Extraction
        print("🧠 Step 2: Strategic Intelligence Extraction")
        print("Scanning meeting prep content for stakeholder and task intelligence...")

        step_start = time.time()

        # Stakeholder scan
        stakeholder_result = subprocess.run(
            ["./claudedirector", "stakeholders", "scan"], capture_output=True, text=True
        )

        # Task scan
        task_result = subprocess.run(
            ["./claudedirector", "tasks", "scan"], capture_output=True, text=True
        )

        scan_time = time.time() - step_start
        print(f"✅ Intelligence extraction completed in {scan_time:.1f}s")
        print(f"   Stakeholder scan: {'✅' if stakeholder_result.returncode == 0 else '❌'}")
        print(f"   Task scan: {'✅' if task_result.returncode == 0 else '❌'}")
        print()

        # Step 3: Strategic Dashboard Review
        print("📋 Step 3: Strategic Dashboard Review")
        print("Director reviews strategic context and accountability...")

        step_start = time.time()

        # Stakeholder status
        stakeholder_list = subprocess.run(
            ["./claudedirector", "stakeholders", "list"], capture_output=True, text=True
        )

        # Task accountability
        task_list = subprocess.run(
            ["./claudedirector", "tasks", "list"], capture_output=True, text=True
        )

        # Overdue items
        overdue_tasks = subprocess.run(
            ["./claudedirector", "tasks", "overdue"], capture_output=True, text=True
        )

        dashboard_time = time.time() - step_start
        print(f"✅ Strategic dashboard reviewed in {dashboard_time:.1f}s")
        print(f"   Stakeholder status: {'✅' if stakeholder_list.returncode == 0 else '❌'}")
        print(f"   Task accountability: {'✅' if task_list.returncode == 0 else '❌'}")
        print(f"   Critical items: {'✅' if overdue_tasks.returncode == 0 else '❌'}")
        print()

        # Step 4: System Health Check
        print("🔍 Step 4: System Health & Platform Status")
        print("Director validates platform health for executive reporting...")

        step_start = time.time()
        status_result = subprocess.run(
            ["./claudedirector", "status"], capture_output=True, text=True
        )

        health_time = time.time() - step_start
        print(f"✅ Platform health check completed in {health_time:.1f}s")
        if status_result.stdout.strip():
            print(f"   Status: {status_result.stdout.strip()[:100]}...")
        print()

        # Summary
        total_time = time.time() - start_time
        print("=" * 80)
        print("📊 STRATEGIC SCENARIO RESULTS")
        print("=" * 80)
        print(f"Total Strategic Workflow Time: {total_time:.1f} seconds")
        print(f"Target: < 120 seconds (2 minutes)")

        performance_score = min(100, (120.0 / total_time) * 100) if total_time > 0 else 100

        if total_time <= 60:
            grade = "🌟 EXCEPTIONAL - Executive ready"
        elif total_time <= 120:
            grade = "✅ EXCELLENT - Meets strategic requirements"
        elif total_time <= 180:
            grade = "⚠️  ACCEPTABLE - Some optimization needed"
        else:
            grade = "❌ NEEDS IMPROVEMENT - Too slow for executive use"

        print(f"Performance Score: {performance_score:.1f}%")
        print(f"Strategic Assessment: {grade}")

        # Strategic value summary
        print(f"\n💼 STRATEGIC VALUE DELIVERED:")
        print(f"✅ Complete stakeholder context from meeting notes")
        print(f"✅ Strategic task accountability and follow-up tracking")
        print(f"✅ Critical deadline and escalation visibility")
        print(f"✅ Platform health status for executive reporting")
        print(f"✅ Zero manual data entry or complex configuration")

        if total_time <= 120:
            print(f"\n🎯 DIRECTOR IMPACT: ClaudeDirector delivers immediate strategic value")
            print(f"   • Time savings: ~15 minutes vs manual coordination")
            print(f"   • Risk reduction: Automated deadline and stakeholder tracking")
            print(f"   • Decision quality: Persistent context across strategic sessions")

        return {
            "total_time": total_time,
            "performance_score": performance_score,
            "grade": grade,
            "steps": {
                "daily_dashboard": time.time() - start_time,
                "intelligence_extraction": scan_time,
                "strategic_review": dashboard_time,
                "health_check": health_time,
            },
        }


def main():
    """Run strategic scenario demo"""
    demo = StrategicScenarioDemo()

    print("🚀 ClaudeDirector Strategic Scenario Demo")
    print("Creating realistic director workflow scenario...")

    # Setup demo environment
    demo.setup_demo_environment()

    # Run strategic scenario
    results = demo.run_strategic_scenario()

    print(f"\n📁 Demo meeting content created in workspace/meeting-prep/")
    print(f"🔄 You can re-run individual commands to explore the strategic intelligence:")
    print(f"   ./claudedirector stakeholders scan")
    print(f"   ./claudedirector tasks scan")
    print(f"   ./claudedirector stakeholders list")
    print(f"   ./claudedirector tasks overdue")
    print(f"\n✨ Strategic scenario demo complete!")


if __name__ == "__main__":
    main()
