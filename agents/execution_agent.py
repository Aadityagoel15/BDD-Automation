"""
Agent 3: Execution Agent
Executes BDD tests using behave framework
"""
import os
import subprocess
import json
from datetime import datetime
from config import Config

class ExecutionAgent:
    """Agent that executes BDD tests"""
    
    def __init__(self):
        Config.ensure_directories()
        self.reports_dir = Config.REPORTS_DIR
    
    def execute_tests(self, feature_file: str = None, tags: list = None, format_type: str = "json") -> dict:
        """
        Execute BDD tests using behave
        
        Args:
            feature_file: Specific feature file to run (None for all)
            tags: List of tags to filter scenarios
            format_type: Output format (json, html, allure)
            
        Returns:
            Dictionary with execution results
        """
        # Build behave command
        base_dir = Config.BASE_DIR
        cmd = ["behave", "--no-capture"]
        
        # Add feature file if specified
        if feature_file:
            if not os.path.isabs(feature_file):
                feature_file = os.path.join(Config.FEATURES_DIR, feature_file)
            cmd.append(feature_file)
        else:
            cmd.append(Config.FEATURES_DIR)
        
        # Add tags if specified
        if tags:
            tag_args = " and ".join([f"@{tag}" for tag in tags])
            cmd.extend(["--tags", tag_args])

        # Inject base_url into behave userdata if configured.
        # This allows any API project to define its base URL via environment
        # (BASE_URL or BEHAVE_USERDATA_BASE_URL) and have it available as
        # context.config.userdata['base_url'] in step definitions.
        base_url = os.getenv("BEHAVE_USERDATA_BASE_URL") or os.getenv("BASE_URL", "")
        if base_url:
            cmd.extend(["-D", f"base_url={base_url}"])
        
        # Add JSON formatter for parsing (behave has built-in json formatter)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_report = os.path.join(self.reports_dir, f"execution_report_{timestamp}.json")
        cmd.extend(["-f", "json.pretty", "-o", json_report])
        
        # Note: HTML formatter may require behave-html-formatter plugin
        # Using pretty format as default, which works out of the box
        html_report = os.path.join(self.reports_dir, f"execution_report_{timestamp}.txt")
        
        try:
            # Execute behave
            result = subprocess.run(
                cmd,
                cwd=base_dir,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            # Parse JSON report if it exists
            execution_results = {
                "status_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "json_report_path": json_report if os.path.exists(json_report) else None,
                "html_report_path": html_report if os.path.exists(html_report) else None,
                "console_output": result.stdout,
                "timestamp": timestamp,
                "success": result.returncode == 0
            }
            
            # Try to load JSON report for detailed results
            if os.path.exists(json_report):
                try:
                    with open(json_report, 'r', encoding='utf-8') as f:
                        execution_results["detailed_results"] = json.load(f)
                    
                    # Extract summary statistics
                    if execution_results["detailed_results"]:
                        execution_results["summary"] = self._extract_summary(
                            execution_results["detailed_results"]
                        )
                except json.JSONDecodeError:
                    pass
            
            return execution_results
            
        except subprocess.TimeoutExpired:
            return {
                "status_code": -1,
                "error": "Test execution timed out",
                "success": False,
                "timestamp": timestamp
            }
        except Exception as e:
            return {
                "status_code": -1,
                "error": str(e),
                "success": False,
                "timestamp": timestamp
            }
    
    def _extract_summary(self, json_results: list) -> dict:
        """Extract summary statistics from JSON results"""
        summary = {
            "total_scenarios": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total_steps": 0,
            "passed_steps": 0,
            "failed_steps": 0,
            "skipped_steps": 0
        }
        
        for feature in json_results:
            for element in feature.get("elements", []):
                if element.get("type") == "scenario":
                    summary["total_scenarios"] += 1
                    status = element.get("status", "").lower()
                    if status == "passed":
                        summary["passed"] += 1
                    elif status == "failed":
                        summary["failed"] += 1
                    else:
                        summary["skipped"] += 1
                    
                    for step in element.get("steps", []):
                        summary["total_steps"] += 1
                        step_status = step.get("result", {}).get("status", "").lower()
                        if step_status == "passed":
                            summary["passed_steps"] += 1
                        elif step_status == "failed":
                            summary["failed_steps"] += 1
                        else:
                            summary["skipped_steps"] += 1
        
        return summary

