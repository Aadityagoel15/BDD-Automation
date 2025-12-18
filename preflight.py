import os
import importlib.util
from config import Config, ProjectType


class PreflightError(Exception):
    pass


def _check_package(pkg_name: str):
    if importlib.util.find_spec(pkg_name) is None:
        raise PreflightError(f"Required package not installed: {pkg_name}")


def run_preflight(project_type: str, bdd_config: dict):
    errors = []

    # --------------------------------------------------
    # ENV CHECKS
    # --------------------------------------------------
    if not Config.GROQ_API_KEY:
        errors.append("GROQ_API_KEY is missing in .env")

    # --------------------------------------------------
    # STRUCTURE CHECKS
    # --------------------------------------------------
    if not os.path.isdir("features"):
        errors.append("Missing 'features/' directory")

    if not os.path.isdir(os.path.join("features", "steps")):
        errors.append("Missing 'features/steps/' directory")

    # --------------------------------------------------
    # DEPENDENCY CHECKS
    # --------------------------------------------------
    try:
        _check_package("behave")
    except PreflightError as e:
        errors.append(str(e))

    if project_type == ProjectType.API:
        try:
            _check_package("requests")
        except PreflightError as e:
            errors.append(str(e))

    # --------------------------------------------------
    # CONFIG CHECKS
    # --------------------------------------------------
    project_cfg = bdd_config.get("project", {})
    base_url = project_cfg.get("base_url")

    if project_type == ProjectType.API and not base_url:
        errors.append(
            "base_url is required for API projects "
            "(define it in bdd.config.yaml)"
        )

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------
    if errors:
        raise PreflightError("\n".join(errors))
