from datetime import datetime

"""
Agent 1: Requirements to .feature file Agent
Converts requirements/user stories into Gherkin .feature files
(Project-type aware, automation-safe)
"""
import os
from groq_client import GroqClient
from config import Config, ProjectType


class RequirementsToFeatureAgent:
    """Agent that converts requirements into Gherkin feature files"""

    def __init__(self):
        self.groq_client = GroqClient()

        self.system_prompt = """
You are an expert BDD (Behavior-Driven Development) specialist.

Your task is to convert requirements or user stories into
well-structured Gherkin .feature files that are EXECUTABLE by automation.

CRITICAL RULES (NON-NEGOTIABLE):
- Generated steps MUST be automation-friendly
- Do NOT generate undefined, empty, or ambiguous steps
- NEVER leave placeholders empty in Scenario Outlines
- Use deterministic, reusable language

PROJECT TYPE RULES:
- For API projects:
  - DO NOT use UI words such as:
    page, form, button, click, screen, navigation, submit
  - Use generic behavior language only

ALLOWED GENERIC ACTIONS (API-SAFE):
- prepare a request / input
- execute the request / action
- verify the outcome

ASSERTIONS MUST USE:
- "the action should succeed"
- "the action should fail"
"""

    # ------------------------------------------------------------------
    def convert_requirements_to_feature(
        self,
        requirements: str,
        feature_name: str = None,
        project_type: str = ProjectType.API
    ) -> str:

        prompt = f"""
PROJECT TYPE: {project_type.upper()}

Convert the following requirements into a Gherkin .feature file
that is COMPATIBLE with the project type.

RULES:
- Do NOT use UI terms for API projects
- Keep scenarios atomic and testable
- Prefer Background only if truly common
- Use Examples tables when appropriate
- NEVER leave example values empty

REQUIREMENTS:
{requirements}

Return ONLY the feature file content.
"""

        feature_content = self.groq_client.generate_response(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        feature_content = self._clean_feature_content(feature_content)

        if project_type == ProjectType.API:
            self._validate_api_feature(feature_content)

        return feature_content

    # ------------------------------------------------------------------
    def save_feature_file(self, feature_content: str, feature_name: str) -> str:
        Config.ensure_directories()

        feature_name = feature_name or "generated_feature"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{feature_name}_{timestamp}.feature"

        path = os.path.join(Config.FEATURES_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(feature_content)

        return path

    # ------------------------------------------------------------------
    # CLEAN & NORMALIZE (SAFE, FINAL)
    # ------------------------------------------------------------------
    def _clean_feature_content(self, content: str) -> str:
        """
        Safely normalize Gherkin:
        - Remove markdown fences (if present)
        - Ensure Feature header
        - Replace empty example values with semantic tokens
        - NEVER rewrite step structure
        """

        # -----------------------------
        # SAFE MARKDOWN REMOVAL
        # -----------------------------
        if "```gherkin" in content:
            parts = content.split("```gherkin", 1)
            if len(parts) > 1:
                content = parts[1].split("```", 1)[0].strip()

        elif "```" in content:
            parts = content.split("```", 1)
            if len(parts) > 1:
                content = parts[1].split("```", 1)[0].strip()

        # -----------------------------
        # ENSURE FEATURE HEADER
        # -----------------------------
        content = content.strip()
        if not content.startswith("Feature:"):
            if "Feature:" in content:
                content = content[content.find("Feature:"):]
            else:
                content = "Feature: Generated Feature\n\n" + content

        # -----------------------------
        # NORMALIZE EMPTY VALUES
        # -----------------------------
        fixed_lines = []
        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith(("Given", "When", "Then", "And")):
                # Replace empty quoted values
                line = line.replace('""', '"missing"')
                line = line.replace("  ", " ")

                # Replace textual empties
                line = line.replace(" of  ", " of missing ")
                line = line.replace(" and  ", " and missing ")

            fixed_lines.append(line)

        result = "\n".join(fixed_lines).strip()

        if not result:
            raise ValueError("Generated feature content is empty after cleanup")

        return result

    # ------------------------------------------------------------------
    def _validate_api_feature(self, content: str):
        forbidden_words = [
            "page", "form", "button", "click",
            "screen", "navigate", "navigation", "submit"
        ]

        lowered = content.lower()
        for word in forbidden_words:
            if word in lowered:
                raise ValueError(
                    f"Invalid API feature detected.\n"
                    f"UI word '{word}' is not allowed.\n\n{content}"
                )
