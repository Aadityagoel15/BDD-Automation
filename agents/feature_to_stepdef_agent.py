"""
Agent 2: Feature to Step Definition Agent
Converts Gherkin .feature files into Python step definitions
(Project-type aware, base-step enforced, AST-safe)
"""
import os
import ast
from groq_client import GroqClient
from config import Config, ProjectType


class FeatureToStepDefAgent:
    """Agent that converts Gherkin feature files into Python step definitions"""

    def __init__(self):
        self.groq_client = GroqClient()

        self.system_prompt = """
You are an expert BDD automation engineer.

Your task is to generate Python step definitions for Behave.

ABSOLUTE RULES (NON-NEGOTIABLE):
- Output MUST be valid Python code
- DO NOT include explanations, notes, or assumptions
- DO NOT include markdown
- Use behave decorators (@given, @when, @then)
- NEVER leave a decorator without a function
- NEVER leave a step body empty
- NEVER use `pass`

BASE STEP DELEGATION (MANDATORY):
- If a base helper exists, YOU MUST CALL IT
- Do NOT reimplement HTTP or assertions

API PROJECT RULES:
- Requests MUST assign context.response
- Assertions MUST read from context.response
- "the action should succeed" → verify_response_status_code(context, 200)
- "the action should fail" → verify_response_status_code(context, 400)

If unsure, generate executable Python that raises RuntimeError.
Creativity is FORBIDDEN. Reuse is REQUIRED.
"""

    # ------------------------------------------------------------------
    def generate_step_definitions(
        self,
        feature_file_path: str,
        project_type: str = ProjectType.UNKNOWN
    ) -> str:

        if not os.path.exists(feature_file_path):
            raise FileNotFoundError(feature_file_path)

        with open(feature_file_path, "r", encoding="utf-8") as f:
            feature_content = f.read()

        project_rules = self._project_type_rules(project_type)

        prompt = f"""
PROJECT TYPE: {project_type.upper()}

AVAILABLE BASE HELPERS:
- features.steps.base.api_steps:
    - send_get_request
    - send_post_request
    - verify_response_status_code

FEATURE FILE:
{feature_content}

PROJECT RULES:
{project_rules}

GENERATION CONTRACT:
- Requests MUST assign context.response
- "the action should succeed" → verify_response_status_code(context, 200)
- "the action should fail" → verify_response_status_code(context, 400)

Return ONLY valid Python code.
"""

        raw = self.groq_client.generate_response(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return self._clean_python_code(raw)

    # ------------------------------------------------------------------
    def save_step_definitions(self, step_def_content: str, feature_name: str) -> str:
        Config.ensure_directories()

        path = os.path.join(
            Config.STEP_DEFINITIONS_DIR,
            f"{feature_name}_steps.py"
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(step_def_content)

        return path

    # ------------------------------------------------------------------
    def _project_type_rules(self, project_type: str) -> str:
        if project_type == ProjectType.API:
            return """
- Use API base helpers ONLY
- Never hardcode endpoints or credentials
- Execution steps MUST assign context.response
"""

        return "Generate minimal reusable steps."

    # ------------------------------------------------------------------
    def _clean_python_code(self, content: str) -> str:
        """
        HARD SANITIZER:
        - Removes markdown and prose
        - Guarantees decorator → function pairing
        - Guarantees non-empty step bodies
        - Enforces valid Python AST
        """

        # --------------------------------------------------
        # Remove markdown fences
        # --------------------------------------------------
        content = "\n".join(
            line for line in content.splitlines()
            if not line.strip().startswith("```")
        )

        # Remove stray 'python'
        if content.strip().lower().startswith("python"):
            content = content.split("\n", 1)[1]

        # --------------------------------------------------
        # Remove natural language junk
        # --------------------------------------------------
        filtered_lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith((
                "Note:",
                "Explanation:",
                "Assumption:",
                "This implementation",
                "You should",
                "It is assumed",
            )):
                continue
            filtered_lines.append(line)

        lines = filtered_lines
        final_lines = []
        i = 0

        while i < len(lines):
            line = lines[i].rstrip()
            stripped = line.strip()

            # --------------------------------------------------
            # DECORATOR SAFETY (CRITICAL)
            # --------------------------------------------------
            if stripped.startswith("@"):
                final_lines.append(line)

                next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if not next_line.startswith("def "):
                    final_lines.append("def step_impl(context):")
                    final_lines.append(
                        "    raise RuntimeError('Step body not implemented')"
                    )

                i += 1
                continue

            final_lines.append(line)

            # --------------------------------------------------
            # ENSURE FUNCTION BODY
            # --------------------------------------------------
            if stripped.startswith("def ") and stripped.endswith(":"):
                if i + 1 >= len(lines) or not lines[i + 1].startswith((" ", "\t")):
                    final_lines.append(
                        "    raise RuntimeError('Step body not implemented')"
                    )

            i += 1

        final_code = "\n".join(final_lines).strip()

        # --------------------------------------------------
        # FINAL AUTHORITY: AST VALIDATION
        # --------------------------------------------------
        try:
            ast.parse(final_code)
        except SyntaxError as e:
            raise RuntimeError(
                "AI generated invalid Python.\n"
                f"Line {e.lineno}: {e.text}"
            )

        return final_code
