"""
Agent 4: Reporting Agent
Generates comprehensive test execution reports
"""
import os
import json
from datetime import datetime
from groq_client import GroqClient
from config import Config
from config import Config

class ReportingAgent:
    """Agent that generates comprehensive test reports"""
    
    def __init__(self):
        self.groq_client = GroqClient()
        Config.ensure_directories()
        self.system_prompt = """You are an expert in test automation reporting.
Your task is to analyze test execution results and generate comprehensive, insightful reports.

Guidelines:
1. Provide clear executive summary
2. Highlight key metrics (pass rate, failure rate, execution time)
3. Identify patterns in failures
4. Provide actionable insights
5. Categorize issues by severity
6. Suggest improvements
7. Make reports readable for both technical and non-technical stakeholders
"""
    
    def generate_report(self, execution_results: dict) -> dict:
        """
        Generate comprehensive test execution report
        
        Args:
            execution_results: Results from ExecutionAgent
            
        Returns:
            Dictionary containing generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extract data for report generation
        summary = execution_results.get("summary", {})
        detailed_results = execution_results.get("detailed_results", [])
        
        # Generate AI-powered insights
        insights = self._generate_insights(execution_results)
        
        # Build report structure
        report = {
            "timestamp": timestamp,
            "execution_summary": summary,
            "insights": insights,
            "detailed_results_path": execution_results.get("json_report_path"),
            "html_report_path": execution_results.get("html_report_path"),
            "overall_status": "PASSED" if execution_results.get("success") else "FAILED"
        }
        
        # Calculate metrics
        report["metrics"] = self._calculate_metrics(summary)
        
        # Save report
        report_path = os.path.join(Config.REPORTS_DIR, f"test_report_{timestamp}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        report["report_path"] = report_path
        
        # Generate human-readable summary
        human_readable = self._generate_human_readable_report(report)
        summary_path = os.path.join(Config.REPORTS_DIR, f"test_report_summary_{timestamp}.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(human_readable)
        
        report["summary_path"] = summary_path
        
        return report
    
    def _generate_insights(self, execution_results: dict) -> dict:
        """Generate AI-powered insights from test results"""
        summary = execution_results.get("summary", {})
        detailed_results = execution_results.get("detailed_results", [])
        
        # Prepare prompt for AI analysis
        prompt = f"""Analyze the following test execution results and provide insights:

SUMMARY:
- Total Scenarios: {summary.get('total_scenarios', 0)}
- Passed: {summary.get('passed', 0)}
- Failed: {summary.get('failed', 0)}
- Skipped: {summary.get('skipped', 0)}
- Pass Rate: {(summary.get('passed', 0) / max(summary.get('total_scenarios', 1), 1) * 100):.2f}%

Provide:
1. Overall assessment
2. Key patterns or trends
3. Areas of concern
4. Recommendations for improvement

Keep it concise and actionable."""
        
        try:
            insights_text = self.groq_client.generate_response(prompt, self.system_prompt)
            
            # Extract failures for detailed analysis
            failures = []
            if detailed_results:
                for feature in detailed_results:
                    for element in feature.get("elements", []):
                        if element.get("status", "").lower() == "failed":
                            failures.append({
                                "feature": feature.get("name"),
                                "scenario": element.get("name"),
                                "error": element.get("steps", [{}])[-1].get("result", {}).get("error_message", "Unknown error")
                            })
            
            return {
                "analysis": insights_text,
                "failure_count": len(failures),
                "failures": failures[:10]  # Top 10 failures
            }
        except Exception as e:
            return {
                "analysis": f"Error generating insights: {str(e)}",
                "failure_count": summary.get("failed", 0)
            }
    
    def _calculate_metrics(self, summary: dict) -> dict:
        """Calculate key metrics from summary"""
        total_scenarios = summary.get("total_scenarios", 0)
        total_steps = summary.get("total_steps", 0)
        
        if total_scenarios == 0:
            return {}
        
        return {
            "scenario_pass_rate": (summary.get("passed", 0) / total_scenarios * 100),
            "scenario_fail_rate": (summary.get("failed", 0) / total_scenarios * 100),
            "step_pass_rate": (summary.get("passed_steps", 0) / max(total_steps, 1) * 100),
            "step_fail_rate": (summary.get("failed_steps", 0) / max(total_steps, 1) * 100),
            "total_execution_time": summary.get("duration", 0)
        }
    
    def _generate_human_readable_report(self, report: dict) -> str:
        """Generate human-readable text report"""
        lines = [
            "=" * 80,
            "BDD TEST EXECUTION REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Overall Status: {report['overall_status']}",
            "",
            "EXECUTION SUMMARY",
            "-" * 80,
        ]
        
        summary = report.get("execution_summary", {})
        if summary:
            lines.extend([
                f"Total Scenarios: {summary.get('total_scenarios', 0)}",
                f"  - Passed: {summary.get('passed', 0)}",
                f"  - Failed: {summary.get('failed', 0)}",
                f"  - Skipped: {summary.get('skipped', 0)}",
                "",
                f"Total Steps: {summary.get('total_steps', 0)}",
                f"  - Passed: {summary.get('passed_steps', 0)}",
                f"  - Failed: {summary.get('failed_steps', 0)}",
                f"  - Skipped: {summary.get('skipped_steps', 0)}",
                "",
            ])
        
        metrics = report.get("metrics", {})
        if metrics:
            lines.extend([
                "METRICS",
                "-" * 80,
                f"Scenario Pass Rate: {metrics.get('scenario_pass_rate', 0):.2f}%",
                f"Scenario Fail Rate: {metrics.get('scenario_fail_rate', 0):.2f}%",
                f"Step Pass Rate: {metrics.get('step_pass_rate', 0):.2f}%",
                "",
            ])
        
        insights = report.get("insights", {})
        if insights.get("analysis"):
            lines.extend([
                "AI INSIGHTS",
                "-" * 80,
                insights["analysis"],
                "",
            ])
        
        if insights.get("failures"):
            lines.extend([
                "FAILED SCENARIOS",
                "-" * 80,
            ])
            for failure in insights["failures"][:5]:
                lines.extend([
                    f"Feature: {failure.get('feature', 'N/A')}",
                    f"Scenario: {failure.get('scenario', 'N/A')}",
                    f"Error: {failure.get('error', 'N/A')[:200]}",
                    "",
                ])
        
        lines.extend([
            "=" * 80,
            f"Detailed JSON Report: {report.get('report_path', 'N/A')}",
            f"HTML Report: {report.get('html_report_path', 'N/A')}",
        ])
        
        return "\n".join(lines)

