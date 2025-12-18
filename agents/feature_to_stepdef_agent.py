"""
Agent 2: Feature to Step Definition Agent
Converts Gherkin .feature files into Python step definitions
(Project-type aware, base-step constrained)
"""
import os
from groq_client import GroqClient
from config import Config, ProjectType


class FeatureToStepDefAgent:
    """Agent that converts Gherkin feature files into Python step definitions"""

    def __init__(self):
        self.groq_client = GroqClient()
        self.system_prompt = """
You are an expert BDD automation engineer.

Your task is to generate Python step definitions for Behave
based on the given Gherkin feature file.

CRITICAL RULES (NON-NEGOTIABLE):
- Generate ONLY valid Python code
- Use behave decorators (@given, @when, @then)
- Do NOT include explanations or markdown
- Do NOT hardcode URLs, credentials, tokens, or selectors
- Use the context object for sharing state

BASE STEP REUSE (VERY IMPORTANT):
- Prefer reusing existing step definitions from features/steps/base
- Do NOT recreate steps that already exist in base steps
- Only generate NEW steps if no suitable base step exists
- Keep new steps generic and reusable

Your goal is STABILITY and REUSE, not creativity.
"""

    # ------------------------------------------------------------------
    # MAIN METHOD
    # ------------------------------------------------------------------
    def generate_step_definitions(
        self,
        feature_file_path: str,
        project_type: str = ProjectType.UNKNOWN
    ) -> str:
        """Generate Python step definitions from a Gherkin feature file"""

        if not os.path.exists(feature_file_path):
            raise FileNotFoundError(f"Feature file not found: {feature_file_path}")

        with open(feature_file_path, "r", encoding="utf-8") as f:
            feature_content = f.read()

        project_rules = self._project_type_rules(project_type)

        prompt = f"""
Generate Python step definitions for the following Gherkin feature.

PROJECT TYPE: {project_type.upper()}

AVAILABLE BASE STEP FILES:
- features/steps/base/common_steps.py
- features/steps/base/api_steps.py
- features/steps/base/web_steps.py

PROJECT-SPECIFIC RULES:
{project_rules}

FEATURE FILE:
{feature_content}

OUTPUT REQUIREMENTS:
- Reuse base steps whenever possible
- Import only required libraries
- Keep logic minimal and deterministic
- Use context consistently

Return ONLY valid Python code.
"""

        raw_output = self.groq_client.generate_response(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        cleaned = self._clean_python_code(raw_output)

        # --------------------------------------------------
        # FINAL SAFETY: validate Python syntax
        # --------------------------------------------------
        try:
            compile(cleaned, "<generated_steps>", "exec")
        except SyntaxError as e:
            raise RuntimeError(
                "Generated step definitions contain invalid Python syntax.\n"
                f"Line {e.lineno}: {e.text}"
            )

        return cleaned

    # ------------------------------------------------------------------
    # SAVE FILE
    # ------------------------------------------------------------------
    def save_step_definitions(self, step_def_content: str, feature_name: str) -> str:
        """Save step definitions to a Python file"""

        Config.ensure_directories()

        if not feature_name:
            feature_name = "generated_steps"

        file_path = os.path.join(
            Config.STEP_DEFINITIONS_DIR,
            f"{feature_name}_steps.py"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(step_def_content)

        return file_path

    # ------------------------------------------------------------------
    # PROJECT RULES
    # ------------------------------------------------------------------
    def _project_type_rules(self, project_type: str) -> str:
        if project_type == ProjectType.API:
            return """
- Prefer existing API base steps
- Use requests ONLY if no base step exists
- Store responses in context.response
- Do NOT generate UI or browser logic
"""

        if project_type == ProjectType.WEB:
            return """
- Prefer existing Web base steps
- Use UI placeholder steps only
- Do NOT use API or HTTP logic
- Do NOT assume locators or frameworks
"""

        if project_type == ProjectType.MOBILE:
            return """
- Generate generic mobile placeholders only
- Do NOT assume Android or iOS specifics
"""

        if project_type == ProjectType.DATA:
            return """
- Generate data validation placeholders
- Do NOT use API or UI logic
"""

        return """
- Generate generic, framework-agnostic steps
- Avoid assumptions about system type
"""

    # ------------------------------------------------------------------
    # OUTPUT SANITIZATION (CRITICAL)
    # ------------------------------------------------------------------
    def _clean_python_code(self, content: str) -> str:
        """
        Clean AI output to ensure valid Python code:
        - Remove markdown fences
        - Remove stray 'python'
        - Normalize behave decorators
        - Ensure function bodies exist
        """

        # Remove markdown fences
        if "```" in content:
            content = "\n".join(
                line for line in content.splitlines()
                if not line.strip().startswith("```")
            )

        # Remove stray 'python'
        if content.strip().lower().startswith("python"):
            content = content.split("\n", 1)[1]

        lines = content.splitlines()
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()

            # --------------------------------------------------
            # FIX BEHAVE DECORATORS (CRITICAL)
            # --------------------------------------------------
            if line.strip().startswith("@"):
                start = line.find("(")
                end = line.rfind(")")
                if start != -1 and end != -1:
                    inner = line[start + 1:end].strip()

                    # Remove surrounding quotes
                    if inner.startswith(("'", '"')) and inner.endswith(("'", '"')):
                        inner = inner[1:-1]

                    # Remove quoted placeholders
                    inner = inner.replace("'{", "{").replace("}'", "}")
                    inner = inner.replace('"{', "{").replace('}"', "}")

                    # Always wrap in double quotes
                    line = f'{line[:start+1]}"{inner}"{line[end:]}'

            fixed_lines.append(line)

            # --------------------------------------------------
            # ENSURE FUNCTION BODY EXISTS
            # --------------------------------------------------
            if line.strip().startswith("def ") and line.strip().endswith(":"):
                if i + 1 >= len(lines) or not lines[i + 1].startswith((" ", "\t")):
                    fixed_lines.append("    pass")

            i += 1

        return "\n".join(fixed_lines).strip()
