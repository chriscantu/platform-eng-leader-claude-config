#!/usr/bin/env python3
"""
Immediate Strategic Usage Pattern Validation
Quick validation of ClaudeDirector's core strategic workflows
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Tuple


class QuickStrategicValidator:
    """Quick validation of strategic usage patterns"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.claudedirector = self.project_root / "claudedirector"
        self.results = {}

    def test_executive_startup(self) -> Tuple[bool, float, str]:
        """Test: Director starts their day - get immediate strategic value"""
        print("🏃‍♂️ Testing executive startup workflow...")

        start_time = time.time()
        try:
            # Test 1: Setup verification (foundation check)
            result = subprocess.run(
                [str(self.claudedirector), "setup", "--verify"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return False, time.time() - start_time, "Setup verification failed"

            # Test 2: System status (health check)
            result = subprocess.run(
                [str(self.claudedirector), "status"], capture_output=True, text=True, timeout=15
            )

            elapsed = time.time() - start_time

            # Executive success criteria: < 30 seconds, no errors
            success = elapsed < 30.0 and result.returncode == 0
            message = f"Completed in {elapsed:.1f}s (target: <30s)"

            return success, elapsed, message

        except subprocess.TimeoutExpired:
            return False, 30.0, "Timeout - too slow for executive use"
        except Exception as e:
            return False, time.time() - start_time, f"Error: {e}"

    def test_stakeholder_intelligence(self) -> Tuple[bool, float, str]:
        """Test: Stakeholder management workflow"""
        print("👥 Testing stakeholder intelligence workflow...")

        start_time = time.time()
        try:
            # Test stakeholder CLI responsiveness
            result = subprocess.run(
                [str(self.claudedirector), "stakeholders", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return False, time.time() - start_time, "Stakeholder CLI not available"

            # Test stakeholder list command
            result = subprocess.run(
                [str(self.claudedirector), "stakeholders", "list"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            elapsed = time.time() - start_time

            # Success: CLI works, responds quickly
            success = elapsed < 15.0 and result.returncode == 0
            message = f"Stakeholder system responsive in {elapsed:.1f}s"

            return success, elapsed, message

        except subprocess.TimeoutExpired:
            return False, 15.0, "Stakeholder operations too slow"
        except Exception as e:
            return False, time.time() - start_time, f"Error: {e}"

    def test_task_accountability(self) -> Tuple[bool, float, str]:
        """Test: Strategic task management workflow"""
        print("📋 Testing task accountability workflow...")

        start_time = time.time()
        try:
            # Test task CLI responsiveness
            result = subprocess.run(
                [str(self.claudedirector), "tasks", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return False, time.time() - start_time, "Task CLI not available"

            # Test task list command
            result = subprocess.run(
                [str(self.claudedirector), "tasks", "list"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            elapsed = time.time() - start_time

            # Success: CLI works, responds quickly
            success = elapsed < 15.0 and result.returncode == 0
            message = f"Task system responsive in {elapsed:.1f}s"

            return success, elapsed, message

        except subprocess.TimeoutExpired:
            return False, 15.0, "Task operations too slow"
        except Exception as e:
            return False, time.time() - start_time, f"Error: {e}"

    def test_meeting_intelligence(self) -> Tuple[bool, float, str]:
        """Test: Meeting intelligence workflow"""
        print("🧠 Testing meeting intelligence workflow...")

        start_time = time.time()
        try:
            # Test meeting CLI responsiveness
            result = subprocess.run(
                [str(self.claudedirector), "meetings", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return False, time.time() - start_time, "Meeting CLI not available"

            # Test meeting scan capability
            result = subprocess.run(
                [str(self.claudedirector), "meetings", "scan"],
                capture_output=True,
                text=True,
                timeout=20,
            )

            elapsed = time.time() - start_time

            # Success: CLI works, scans without crashing
            success = elapsed < 20.0 and result.returncode == 0
            message = f"Meeting intelligence active in {elapsed:.1f}s"

            return success, elapsed, message

        except subprocess.TimeoutExpired:
            return False, 20.0, "Meeting operations too slow"
        except Exception as e:
            return False, time.time() - start_time, f"Error: {e}"

    def test_git_optimization(self) -> Tuple[bool, float, str]:
        """Test: Intelligent git workflow"""
        print("⚡ Testing git optimization workflow...")

        start_time = time.time()
        try:
            # Test git CLI availability
            result = subprocess.run(
                [str(self.claudedirector), "git", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            elapsed = time.time() - start_time

            # Success: Git commands available and responsive
            success = elapsed < 10.0 and result.returncode == 0
            message = f"Git optimization available in {elapsed:.1f}s"

            return success, elapsed, message

        except subprocess.TimeoutExpired:
            return False, 10.0, "Git commands too slow"
        except Exception as e:
            return False, time.time() - start_time, f"Error: {e}"

    def run_validation(self) -> Dict:
        """Run comprehensive strategic usage validation"""
        print("🎯 ClaudeDirector Strategic Usage Pattern Validation")
        print("=" * 60)
        print("Testing real-world director workflows...\n")

        # Core strategic workflows
        workflows = [
            ("Executive Startup", self.test_executive_startup),
            ("Stakeholder Intelligence", self.test_stakeholder_intelligence),
            ("Task Accountability", self.test_task_accountability),
            ("Meeting Intelligence", self.test_meeting_intelligence),
            ("Git Optimization", self.test_git_optimization),
        ]

        results = {}
        total_time = 0
        successful_workflows = 0

        for workflow_name, test_func in workflows:
            success, elapsed, message = test_func()

            status = "✅" if success else "❌"
            print(f"{status} {workflow_name}: {message}")

            results[workflow_name] = {"success": success, "time": elapsed, "message": message}

            total_time += elapsed
            if success:
                successful_workflows += 1

        # Calculate summary metrics
        success_rate = (successful_workflows / len(workflows)) * 100
        avg_performance = (successful_workflows / len(workflows)) * 100

        print(f"\n📊 VALIDATION SUMMARY")
        print(
            f"Success Rate: {success_rate:.1f}% ({successful_workflows}/{len(workflows)} workflows)"
        )
        print(f"Total Time: {total_time:.1f}s")
        print(f"Average Performance: {avg_performance:.1f}%")

        # Strategic assessment
        if success_rate >= 80:
            grade = "🌟 EXECUTIVE READY"
            assessment = "ClaudeDirector meets strategic director requirements"
        elif success_rate >= 60:
            grade = "⚠️  NEEDS OPTIMIZATION"
            assessment = "Core functionality works but needs performance tuning"
        else:
            grade = "❌ CRITICAL ISSUES"
            assessment = "Major issues blocking strategic usage"

        print(f"\n🎯 STRATEGIC ASSESSMENT: {grade}")
        print(f"Assessment: {assessment}")

        # Generate recommendations
        recommendations = []
        for workflow_name, result in results.items():
            if not result["success"]:
                if "timeout" in result["message"].lower() or "slow" in result["message"]:
                    recommendations.append(f"Optimize {workflow_name} performance")
                elif "not available" in result["message"]:
                    recommendations.append(f"Fix {workflow_name} availability issues")
                else:
                    recommendations.append(f"Debug {workflow_name} errors")

        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")

        return {
            "summary": {
                "success_rate": success_rate,
                "total_time": total_time,
                "grade": grade,
                "assessment": assessment,
                "recommendations": recommendations,
            },
            "workflows": results,
        }


def main():
    """Main validation execution"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Strategic Usage Pattern Validator")
        print("\nTests ClaudeDirector against real director workflows:")
        print("• Executive startup (daily dashboard)")
        print("• Stakeholder management")
        print("• Task accountability")
        print("• Meeting intelligence")
        print("• Git optimization")
        print("\nUsage: python validate-strategic-patterns.py")
        return

    validator = QuickStrategicValidator()
    results = validator.run_validation()

    # Return appropriate exit code
    success_rate = results["summary"]["success_rate"]
    if success_rate >= 80:
        sys.exit(0)  # Success
    elif success_rate >= 60:
        sys.exit(1)  # Warning
    else:
        sys.exit(2)  # Critical issues


if __name__ == "__main__":
    main()
