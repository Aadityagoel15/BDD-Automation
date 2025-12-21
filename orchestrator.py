"""
Main Orchestrator for BDD Automation AI Agents
Coordinates all agents in the BDD automation pipeline
"""
import os
import sys
import yaml

from agents.requirements_to_feature_agent import RequirementsToFeatureAgent
from agents.feature_to_stepdef_agent import FeatureToStepDefAgent
from agents.execution_agent import ExecutionAgent
from agents.reporting_agent import ReportingAgent
from agents.defect_agent import DefectAgent
from agents.requirements_extraction_agent import RequirementsExtractionAgent

from project_type_detector import detect_project_type
from config import Config, ProjectType
from preflight import run_preflight, PreflightError


# ------------------------------------------------------------------
# CONFIG LOADER
# ------------------------------------------------------------------
def load_bdd_config() -> dict:
    if not os.path.exists("bdd.config.yaml"):
        return {}
    with open("bdd.config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class BDDAutomationOrchestrator:
    """Main orchestrator that coordinates all BDD automation agents"""

    def __init__(self):
        Config.ensure_directories()
        self.extraction_agent = RequirementsExtractionAgent()
        self.requirements_agent = RequirementsToFeatureAgent()
        self.stepdef_agent = FeatureToStepDefAgent()
        self.execution_agent = ExecutionAgent()
        self.reporting_agent = ReportingAgent()
        self.defect_agent = DefectAgent()

    # ------------------------------------------------------------------
    # FULL PIPELINE
    # ------------------------------------------------------------------
    def run_full_pipeline(self, requirements: str, feature_name: str = None) -> dict:

        results = {
            "pipeline_status": "started",
            "stages": {}
        }

        try:
            # -------------------------------------------------------
            # LOAD CONFIG
            # -------------------------------------------------------
            bdd_config = load_bdd_config()
            project_cfg = bdd_config.get("project", {})

            # -------------------------------------------------------
            # PROJECT TYPE RESOLUTION (CORRECT PRIORITY)
            # 1. bdd.config.yaml
            # 2. .env
            # 3. Auto-detection
            # -------------------------------------------------------
            if project_cfg.get("type"):
                project_type = project_cfg["type"]
            elif Config.has_explicit_project_type():
                project_type = Config.get_project_type()
            else:
                project_type = detect_project_type(
                    project_path=None,
                    requirements=requirements
                )

            print(f"[INFO] Project type resolved as: {project_type}")
            results["project_type"] = project_type

            # -------------------------------------------------------
            # PREFLIGHT VALIDATION
            # -------------------------------------------------------
            try:
                run_preflight(project_type, bdd_config)
                print("[OK] Preflight validation passed")
            except PreflightError as e:
                raise RuntimeError(f"Preflight failed:\n{e}")

            # -------------------------------------------------------
            # INJECT BASE_URL INTO BEHAVE (API ONLY)
            # -------------------------------------------------------
            base_url = project_cfg.get("base_url")
            if base_url:
                os.environ["BEHAVE_USERDATA_BASE_URL"] = base_url

            # -------------------------------------------------------
            # STAGE 1: Requirements → Feature
            # -------------------------------------------------------
            print("=" * 80)
            print("STAGE 1: Converting Requirements to Feature File")
            print("=" * 80)

            feature_content = self.requirements_agent.convert_requirements_to_feature(
                requirements,
                feature_name
            )

            feature_file_path = self.requirements_agent.save_feature_file(
                feature_content,
                feature_name or "generated_feature"
            )

            results["stages"]["requirements_to_feature"] = {
                "status": "success",
                "feature_file": feature_file_path
            }

            print(f"[OK] Feature file created: {feature_file_path}")

            # -------------------------------------------------------
            # STAGE 2: Feature → Step Definitions
            # -------------------------------------------------------
            print("\n" + "=" * 80)
            print("STAGE 2: Generating Step Definitions")
            print("=" * 80)

            step_def_content = self.stepdef_agent.generate_step_definitions(
                feature_file_path,
                project_type=project_type
            )

            feature_basename = os.path.basename(feature_file_path).replace(".feature", "")
            step_def_file_path = self.stepdef_agent.save_step_definitions(
                step_def_content,
                feature_basename
            )

            results["stages"]["feature_to_stepdef"] = {
                "status": "success",
                "step_def_file": step_def_file_path
            }

            print(f"[OK] Step definitions created: {step_def_file_path}")

            # -------------------------------------------------------
            # STAGE 3: Execute Tests
            # -------------------------------------------------------
            print("\n" + "=" * 80)
            print("STAGE 3: Executing Tests")
            print("=" * 80)

            execution_results = self.execution_agent.execute_tests(feature_file_path)
            results["stages"]["execution"] = execution_results

            # -------------------------------------------------------
            # STAGE 4: Reporting
            # -------------------------------------------------------
            print("\n" + "=" * 80)
            print("STAGE 4: Generating Reports")
            print("=" * 80)

            test_report = self.reporting_agent.generate_report(execution_results)
            results["stages"]["reporting"] = test_report

            # -------------------------------------------------------
            # STAGE 5: Defect Identification
            # -------------------------------------------------------
            print("\n" + "=" * 80)
            print("STAGE 5: Identifying Defects")
            print("=" * 80)

            defects_result = self.defect_agent.identify_defects(
                execution_results,
                test_report
            )

            results["stages"]["defects"] = defects_result

            results["pipeline_status"] = "completed"
            print("\nPIPELINE COMPLETED SUCCESSFULLY")

        except Exception as e:
            results["pipeline_status"] = "failed"
            results["error"] = str(e)
            import traceback
            traceback.print_exc()

        return results

    # ------------------------------------------------------------------
    # EXTRACT + GENERATE PIPELINE
    # ------------------------------------------------------------------
    def run_extract_and_generate_pipeline(
        self,
        project_path: str,
        feature_name: str = None,
        file_extensions: list = None
    ) -> dict:

        results = {
            "pipeline_status": "started",
            "stages": {}
        }

        try:
            extraction_result = self.extraction_agent.extract_from_project_directory(
                project_path,
                file_extensions
            )

            combined_requirements = extraction_result.get("combined_requirements", "")
            if not combined_requirements:
                raise ValueError("No requirements extracted from project")

            project_type = detect_project_type(
                project_path=project_path,
                requirements=combined_requirements
            )

            feature_content = self.requirements_agent.convert_requirements_to_feature(
                combined_requirements,
                feature_name or os.path.basename(project_path)
            )

            feature_file_path = self.requirements_agent.save_feature_file(
                feature_content,
                feature_name or "project_feature"
            )

            results["stages"]["requirements_to_feature"] = {
                "status": "success",
                "feature_file": feature_file_path
            }

            results["pipeline_status"] = "completed"

        except Exception as e:
            results["pipeline_status"] = "failed"
            results["error"] = str(e)

        return results


# ----------------------------------------------------------------------
# CLI ENTRY POINT
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# CLI ENTRY POINT
# ----------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="BDD Automation AI Agents Orchestrator"
    )

    parser.add_argument("--requirements", type=str)
    parser.add_argument("--feature-name", type=str)
    parser.add_argument("--project-path", type=str)
    parser.add_argument(
        "--stage",
        choices=["full", "extract_and_generate"],
        default="full"
    )

    args = parser.parse_args()
    orchestrator = BDDAutomationOrchestrator()

    if args.stage == "extract_and_generate":
        if not args.project_path:
            sys.exit("Error: --project-path is required")

        results = orchestrator.run_extract_and_generate_pipeline(
            project_path=args.project_path,
            feature_name=args.feature_name
        )

    else:
        if not args.requirements:
            sys.exit("Error: --requirements is required")

        # --------------------------------------------------
        # SMART REQUIREMENTS RESOLUTION
        # --------------------------------------------------
        req_input = args.requirements
        req_path = None

        # Case 1: Full / relative path provided
        if os.path.isfile(req_input):
            req_path = req_input

        # Case 2: File exists inside requirements/ folder
        else:
            candidate = os.path.join(Config.REQUIREMENTS_DIR, req_input)
            if os.path.isfile(candidate):
                req_path = candidate

        # Load requirements
        if req_path:
            print(f"[INFO] Loading requirements from file: {req_path}")
            with open(req_path, "r", encoding="utf-8") as f:
                requirements_text = f.read()
        else:
            print("[INFO] Using inline requirements text")
            requirements_text = req_input

        results = orchestrator.run_full_pipeline(
            requirements=requirements_text,
            feature_name=args.feature_name
        )

    print("\nRESULTS SUMMARY")
    print("=" * 80)
    print(results)
