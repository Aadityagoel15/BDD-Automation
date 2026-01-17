print("=== ORCHESTRATOR MODULE LOADED ===")

"""
Main Orchestrator for BDD Automation AI Agents
(Coordinated, lifecycle-safe, execution-correct)
"""

import os
import sys
import yaml
import traceback

from agents.requirements_to_feature_agent import RequirementsToFeatureAgent
from agents.feature_to_stepdef_agent import FeatureToStepDefAgent
from agents.execution_agent import ExecutionAgent
from agents.reporting_agent import ReportingAgent
from agents.defect_agent import DefectAgent
from agents.requirements_extraction_agent import RequirementsExtractionAgent
from agents.web_discovery_agent import WebDiscoveryAgent
from agents.ui_context_agent import UIContextAgent
from agents.xpath_discovery_agent import XPathPropertiesAgent
from agents.requirements_aware_ui_discovery_agent import RequirementsAwareUIDiscoveryAgent

from project_type_detector import detect_project_type
from config import Config, ProjectType, ExecutionMode
from preflight import run_preflight


# ------------------------------------------------------------------
# CONFIG LOADER
# ------------------------------------------------------------------
def load_bdd_config() -> dict:
    if not os.path.exists("bdd.config.yaml"):
        return {}
    with open("bdd.config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ------------------------------------------------------------------
# ORCHESTRATOR
# ------------------------------------------------------------------
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

        # UI intelligence
        self.web_discovery_agent = WebDiscoveryAgent()
        self.ui_context_agent = UIContextAgent()

        # XPath discovery
        self.xpath_agent = XPathPropertiesAgent()
        
        # Requirements-aware UI discovery (NEW: discovers actual UI elements and maps to requirements)
        self.requirements_aware_discovery = RequirementsAwareUIDiscoveryAgent(headless=True)

    # ------------------------------------------------------------------
    # FULL PIPELINE
    # ------------------------------------------------------------------
    def run_full_pipeline(self, requirements: str, feature_name: str = None) -> dict:

        results = {
            "pipeline_status": "started",
            "stages": {}
        }

        try:
            # =======================================================
            # 🔒 FRAMEWORK MODE (GENERATION ONLY)
            # =======================================================
            Config.set_execution_mode(ExecutionMode.FRAMEWORK)

            # -------------------------------------------------------
            # LOAD CONFIG
            # -------------------------------------------------------
            bdd_config = load_bdd_config()
            project_cfg = bdd_config.get("project", {})

            # -------------------------------------------------------
            # PROJECT TYPE RESOLUTION
            # -------------------------------------------------------
            if project_cfg.get("type"):
                project_type = project_cfg["type"]
            elif Config.get_project_type() != ProjectType.UNKNOWN:
                project_type = Config.get_project_type()
            else:
                project_type = detect_project_type(
                    project_path=None,
                    requirements=requirements
                )

            # 🔥 SINGLE SOURCE OF TRUTH
            Config.set_project_type(project_type)

            # 🔥 CRITICAL FIX: Persist for Behave subprocess
            os.environ["BDD_PROJECT_TYPE"] = project_type

            print(f"[INFO] Project type resolved as: {project_type}")
            results["project_type"] = project_type

            # -------------------------------------------------------
            # PREFLIGHT
            # -------------------------------------------------------
            run_preflight(project_type, bdd_config)
            print("[OK] Preflight validation passed")

            # -------------------------------------------------------
            # BASE_URL
            # -------------------------------------------------------
            base_url = project_cfg.get("base_url") or Config.BASE_URL
            if base_url:
                os.environ["BEHAVE_USERDATA_BASE_URL"] = base_url

            # -------------------------------------------------------
            # WEB-SPECIFIC PREPARATION (FRAMEWORK MODE ONLY)
            # -------------------------------------------------------
            # CRITICAL: Save original requirements BEFORE UI context modification
            # This ensures credential/URL extraction works from original text
            original_requirements = requirements
            
            if project_type == ProjectType.WEB:
                if not base_url:
                    raise RuntimeError("base_url is required for WEB projects")

                # 🔥 NEW: Requirements-aware UI discovery
                # This discovers actual UI elements from the website and maps them to requirements
                print("[INFO] Discovering actual UI elements and mapping to requirements...")
                ui_discovery_result = None  # Initialize to handle exception case
                try:
                    ui_discovery_result = self.requirements_aware_discovery.discover_and_map(
                        requirements=original_requirements,
                        base_url=base_url
                    )
                    enriched_requirements = ui_discovery_result.get('enriched_requirements', original_requirements)
                    
                    print(f"[INFO] UI Discovery Stats:")
                    print(f"  - Buttons found: {ui_discovery_result['discovery_stats']['buttons_found']}")
                    print(f"  - Inputs found: {ui_discovery_result['discovery_stats']['inputs_found']}")
                    print(f"  - Links found: {ui_discovery_result['discovery_stats']['links_found']}")
                    print(f"  - Terms mapped: {ui_discovery_result['discovery_stats']['terms_mapped']}")
                    
                    # Show mapping
                    mapping = ui_discovery_result.get('requirements_mapping', {})
                    if mapping:
                        print(f"[INFO] Requirement -> UI Element Mapping:")
                        for req_term, ui_name in list(mapping.items())[:10]:  # Show first 10
                            if req_term != ui_name:
                                print(f"  '{req_term}' -> '{ui_name}'")
                    
                    # Use enriched requirements (with actual UI element names)
                    requirements = enriched_requirements
                    # Extract UI semantics for feature generation
                    ui_semantics = ui_discovery_result.get('ui_semantics', {})
                    results["stages"]["requirements_aware_ui_discovery"] = {
                        "status": "success",
                        "mapping": mapping,
                        "stats": ui_discovery_result['discovery_stats']
                    }
                except Exception as e:
                    print(f"[WARNING] Requirements-aware UI discovery failed: {e}")
                    print("[INFO] Continuing with original requirements...")
                    # Continue with original requirements if discovery fails
                    requirements = original_requirements
                    ui_discovery_result = None
                    ui_semantics = None

                # XPath discovery (NO REAL EXECUTION)
                xpath_file = self._run_xpath_discovery(base_url)
                results["stages"]["xpath_discovery"] = {
                    "status": "success",
                    "file": xpath_file
                }

                # UI intent generation (NO REAL EXECUTION)
                # Note: This modifies requirements but we keep original for extraction
                modified_requirements = self._build_ui_test_intent(
                    requirements=requirements,  # Use enriched requirements if available
                    base_url=base_url
                )
                # Use modified requirements for feature generation but extract from original
                requirements = modified_requirements

            # -------------------------------------------------------
            # STAGE 1: Requirements → Feature
            # -------------------------------------------------------
            print("=" * 80)
            print("STAGE 1: Converting Requirements to Feature File")
            print("=" * 80)

            # CRITICAL: Extract data from ORIGINAL requirements (before UI context modification)
            # This ensures credentials and URLs are extracted correctly
            feature_content = self.requirements_agent.convert_requirements_to_feature(
                requirements=requirements,  # Modified requirements for context      
                feature_name=feature_name,
                project_type=project_type,
                original_requirements=original_requirements if project_type == ProjectType.WEB else None,
                ui_discovery_result=ui_discovery_result if project_type == ProjectType.WEB else None
            )

            feature_file_path = self.requirements_agent.save_feature_file(
                feature_content,
                feature_name or "generated_feature"
            )

            results["stages"]["requirements_to_feature"] = {
                "status": "success",
                "feature_file": feature_file_path
            }

            # -------------------------------------------------------
            # STAGE 2: Feature → Step Definitions
            # -------------------------------------------------------
            print("=" * 80)
            print("STAGE 2: Generating Step Definitions")
            print("=" * 80)

            # Clean up old step definition files with same prefix to avoid AmbiguousStep errors
            feature_basename_prefix = os.path.basename(feature_file_path).replace(".feature", "").rsplit("_", 2)[0] if "_" in os.path.basename(feature_file_path) else os.path.basename(feature_file_path).replace(".feature", "")
            if feature_basename_prefix:
                step_def_dir = os.path.join(Config.STEP_DEFINITIONS_DIR or "features/steps", "")
                if os.path.exists(step_def_dir):
                    for old_file in os.listdir(step_def_dir):
                        if old_file.startswith(feature_basename_prefix + "_") and old_file.endswith("_steps.py"):
                            old_path = os.path.join(step_def_dir, old_file)
                            try:
                                if old_file != os.path.basename(feature_file_path).replace(".feature", "_steps.py"):
                                    os.remove(old_path)
                                    print(f"[INFO] Removed old step definition file: {old_file}")
                            except Exception as e:
                                print(f"[WARN] Could not remove old step definition file {old_file}: {e}")

            step_def_content = self.stepdef_agent.generate_step_definitions(
                feature_file_path,
                project_type=project_type
            )

            feature_basename = os.path.basename(
                feature_file_path
            ).replace(".feature", "")

            step_def_file_path = self.stepdef_agent.save_step_definitions(
                step_def_content,
                feature_basename
            )

            results["stages"]["feature_to_stepdef"] = {
                "status": "success",
                "step_def_file": step_def_file_path
            }

            # =======================================================
            # 🚀 PROJECT MODE (REAL EXECUTION)
            # =======================================================
            Config.set_execution_mode(ExecutionMode.PROJECT)

            # -------------------------------------------------------
            # STAGE 3: Execution
            # -------------------------------------------------------
            execution_results = self.execution_agent.execute_tests(
                feature_file=feature_file_path,
                project_type=project_type
            )

            results["stages"]["execution"] = execution_results

            # -------------------------------------------------------
            # STAGE 4: Reporting
            # -------------------------------------------------------
            test_report = self.reporting_agent.generate_report(
                execution_results
            )

            results["stages"]["reporting"] = test_report

            # -------------------------------------------------------
            # STAGE 5: Defects
            # -------------------------------------------------------
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
            traceback.print_exc()

        return results

    # ------------------------------------------------------------------
    # INTERNAL HELPERS (FRAMEWORK SAFE)
    # ------------------------------------------------------------------
    def _build_ui_test_intent(self, requirements: str, base_url: str) -> str:
        print("[INFO] Discovering UI structure (FRAMEWORK MODE)")
        page_model = self.web_discovery_agent.discover(base_url)
        return self.ui_context_agent.build_context(
            requirements=requirements,
            page_model=page_model
        )

    def _run_xpath_discovery(self, base_url: str) -> str:
        output_file = os.path.join(
            Config.REPORTS_DIR,
            "ui_locators.properties"
        )
        print("[INFO] Running XPath discovery (FRAMEWORK MODE)")
        self.xpath_agent.generate(url=base_url, output_file=output_file)
        return output_file


# ------------------------------------------------------------------
# CLI ENTRY POINT
# ------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="BDD Automation AI Agents Orchestrator"
    )

    parser.add_argument("--requirements", type=str, required=True)
    parser.add_argument("--feature-name", type=str)

    args = parser.parse_args()
    orchestrator = BDDAutomationOrchestrator()

    req_input = args.requirements

    if os.path.isfile(req_input):
        with open(req_input, "r", encoding="utf-8") as f:
            requirements_text = f.read()
    else:
        requirements_text = req_input

    results = orchestrator.run_full_pipeline(
        requirements=requirements_text,
        feature_name=args.feature_name
    )

    print("\nRESULTS SUMMARY")
    print("=" * 80)
    print(results)


if __name__ == "__main__":
    main()
