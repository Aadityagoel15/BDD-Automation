"""
Agent 5: Defect Identification Agent
Analyzes test failures and identifies/creates defects
"""
import os
import json
from datetime import datetime
from groq_client import GroqClient
from config import Config

class DefectAgent:
    """Agent that identifies and creates defect reports from test failures"""
    
    def __init__(self):
        self.groq_client = GroqClient()
        Config.ensure_directories()
        self.system_prompt = """You are an expert QA analyst specializing in defect identification and reporting.
Your task is to analyze test failures and create comprehensive defect reports.

Guidelines:
1. Identify root causes of failures
2. Categorize defects by severity (Critical, High, Medium, Low)
3. Provide clear reproduction steps
4. Include expected vs actual behavior
5. Suggest potential fixes
6. Identify patterns across multiple failures
7. Determine if failures indicate bugs or test issues
8. Create actionable defect descriptions
"""
    
    def identify_defects(self, execution_results: dict, test_report: dict = None) -> dict:
        """
        Identify defects from test execution results
        
        Args:
            execution_results: Results from ExecutionAgent
            test_report: Optional report from ReportingAgent
            
        Returns:
            Dictionary containing identified defects
        """
        detailed_results = execution_results.get("detailed_results", [])
        failures = self._extract_failures(detailed_results)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not failures:
            result = {
                "defects_found": 0,
                "defects": [],
                "timestamp": timestamp,
                "message": "No failures found - no defects identified",
                "severity_distribution": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
            }
            
            # Save defects file even when no defects found
            defects_path = os.path.join(Config.REPORTS_DIR, f"defects_{timestamp}.json")
            with open(defects_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            result["defects_file_path"] = defects_path
            
            # Generate defect report document
            report_text = self._generate_defect_report(result)
            report_path = os.path.join(Config.REPORTS_DIR, f"defect_report_{timestamp}.txt")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            result["defect_report_path"] = report_path
            
            return result
        
        # Analyze each failure
        defects = []
        for failure in failures:
            defect = self._analyze_failure(failure)
            if defect:
                defects.append(defect)
        
        # Group and deduplicate defects
        unique_defects = self._deduplicate_defects(defects)
        
        # Generate summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = {
            "defects_found": len(unique_defects),
            "defects": unique_defects,
            "timestamp": timestamp,
            "severity_distribution": self._calculate_severity_distribution(unique_defects)
        }
        
        # Save defects to file
        defects_path = os.path.join(Config.REPORTS_DIR, f"defects_{result['timestamp']}.json")
        with open(defects_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        result["defects_file_path"] = defects_path
        
        # Generate defect report document
        report_text = self._generate_defect_report(result)
        report_path = os.path.join(Config.REPORTS_DIR, f"defect_report_{result['timestamp']}.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        result["defect_report_path"] = report_path
        
        return result
    
    def _extract_failures(self, detailed_results: list) -> list:
        """Extract all failures from detailed results"""
        failures = []
        
        for feature in detailed_results:
            feature_name = feature.get("name", "Unknown")
            for element in feature.get("elements", []):
                if element.get("type") == "scenario" and element.get("status", "").lower() == "failed":
                    failed_steps = [step for step in element.get("steps", []) 
                                   if step.get("result", {}).get("status", "").lower() == "failed"]
                    
                    if failed_steps:
                        failure = {
                            "feature": feature_name,
                            "scenario": element.get("name", "Unknown"),
                            "tags": element.get("tags", []),
                            "failed_step": failed_steps[-1].get("name", ""),
                            "error_message": failed_steps[-1].get("result", {}).get("error_message", ""),
                            "duration": element.get("duration", 0),
                            "all_steps": element.get("steps", [])
                        }
                        failures.append(failure)
        
        return failures
    
    def _analyze_failure(self, failure: dict) -> dict:
        """Analyze a single failure and create defect information"""
        prompt = f"""Analyze the following test failure and create a defect report:

Feature: {failure.get('feature', 'N/A')}
Scenario: {failure.get('scenario', 'N/A')}
Failed Step: {failure.get('failed_step', 'N/A')}
Error Message: {failure.get('error_message', 'N/A')}

Provide a JSON response with:
{{
    "title": "Brief defect title",
    "severity": "Critical|High|Medium|Low",
    "category": "Functional|UI|Performance|Integration|Test Issue",
    "description": "Detailed description of the defect",
    "reproduction_steps": ["step1", "step2", ...],
    "expected_behavior": "What should happen",
    "actual_behavior": "What actually happened",
    "root_cause_analysis": "Analysis of why this might be failing",
    "suggested_fix": "Suggestions for fixing the issue",
    "affected_scenario": "{failure.get('scenario', 'N/A')}",
    "error_type": "Type of error (AssertionError, TimeoutError, etc.)"
}}"""
        
        try:
            response = self.groq_client.generate_structured_response(prompt, self.system_prompt)
            
            # Ensure we have a valid defect structure
            if isinstance(response, dict) and "title" in response:
                defect = {
                    "id": f"DEF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(response)}",
                    "title": response.get("title", "Untitled Defect"),
                    "severity": response.get("severity", "Medium"),
                    "category": response.get("category", "Functional"),
                    "description": response.get("description", ""),
                    "reproduction_steps": response.get("reproduction_steps", []),
                    "expected_behavior": response.get("expected_behavior", ""),
                    "actual_behavior": response.get("actual_behavior", ""),
                    "root_cause_analysis": response.get("root_cause_analysis", ""),
                    "suggested_fix": response.get("suggested_fix", ""),
                    "affected_scenario": response.get("affected_scenario", failure.get("scenario", "")),
                    "error_message": failure.get("error_message", ""),
                    "feature": failure.get("feature", ""),
                    "timestamp": datetime.now().isoformat()
                }
                return defect
        except Exception as e:
            # Fallback defect creation
            return {
                "id": f"DEF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "title": f"Test Failure in {failure.get('scenario', 'Unknown Scenario')}",
                "severity": "Medium",
                "category": "Functional",
                "description": f"Test scenario failed with error: {failure.get('error_message', 'Unknown error')}",
                "reproduction_steps": [failure.get("failed_step", "")],
                "expected_behavior": "Test should pass",
                "actual_behavior": f"Test failed: {failure.get('error_message', 'Unknown error')}",
                "affected_scenario": failure.get("scenario", ""),
                "error_message": failure.get("error_message", ""),
                "feature": failure.get("feature", ""),
                "timestamp": datetime.now().isoformat(),
                "analysis_error": str(e)
            }
        
        return None
    
    def _deduplicate_defects(self, defects: list) -> list:
        """Group similar defects together"""
        unique_defects = []
        seen_titles = set()
        
        for defect in defects:
            # Simple deduplication by title similarity
            title = defect.get("title", "").lower()
            if title not in seen_titles:
                seen_titles.add(title)
                unique_defects.append(defect)
            else:
                # Update existing defect with additional info
                for existing in unique_defects:
                    if existing.get("title", "").lower() == title:
                        if defect.get("affected_scenario") not in existing.get("affected_scenarios", []):
                            if "affected_scenarios" not in existing:
                                existing["affected_scenarios"] = [existing.get("affected_scenario")]
                            existing["affected_scenarios"].append(defect.get("affected_scenario"))
                        break
        
        return unique_defects
    
    def _calculate_severity_distribution(self, defects: list) -> dict:
        """Calculate distribution of defects by severity"""
        distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        
        for defect in defects:
            severity = defect.get("severity", "Medium")
            if severity in distribution:
                distribution[severity] += 1
        
        return distribution
    
    def _generate_defect_report(self, defects_result: dict) -> str:
        """Generate human-readable defect report"""
        lines = [
            "=" * 80,
            "DEFECT REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Defects Found: {defects_result['defects_found']}",
            "",
            "SEVERITY DISTRIBUTION",
            "-" * 80,
        ]
        
        for severity, count in defects_result.get("severity_distribution", {}).items():
            lines.append(f"{severity}: {count}")
        
        lines.append("")
        lines.append("DEFECT DETAILS")
        lines.append("-" * 80)
        
        for defect in defects_result.get("defects", []):
            lines.extend([
                "",
                f"Defect ID: {defect.get('id', 'N/A')}",
                f"Title: {defect.get('title', 'N/A')}",
                f"Severity: {defect.get('severity', 'N/A')}",
                f"Category: {defect.get('category', 'N/A')}",
                f"Feature: {defect.get('feature', 'N/A')}",
                f"Scenario: {defect.get('affected_scenario', 'N/A')}",
                "",
                "Description:",
                defect.get("description", "N/A"),
                "",
                "Reproduction Steps:",
                "\n".join([f"  {i+1}. {step}" for i, step in enumerate(defect.get("reproduction_steps", []))]),
                "",
                f"Expected Behavior: {defect.get('expected_behavior', 'N/A')}",
                f"Actual Behavior: {defect.get('actual_behavior', 'N/A')}",
                "",
                "Root Cause Analysis:",
                defect.get("root_cause_analysis", "N/A"),
                "",
                "Suggested Fix:",
                defect.get("suggested_fix", "N/A"),
                "",
                "Error Message:",
                defect.get("error_message", "N/A"),
                "",
                "-" * 80,
            ])
        
        return "\n".join(lines)

