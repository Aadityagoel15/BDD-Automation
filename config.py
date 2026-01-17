"""
Configuration settings for BDD Automation AI Agents
(SINGLE SOURCE OF TRUTH – RUNTIME + SUBPROCESS SAFE)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------
# Project Type
# ------------------------------------------------------------------
class ProjectType:
    API = "api"
    WEB = "web"
    MOBILE = "mobile"
    DATA = "data"
    BACKEND = "backend"
    UNKNOWN = "unknown"


# ------------------------------------------------------------------
# Execution Mode
# ------------------------------------------------------------------
class ExecutionMode:
    """
    FRAMEWORK → generation, analysis, discovery (NO REAL EXECUTION)
    PROJECT   → real execution (browser / API)
    """
    FRAMEWORK = "framework"
    PROJECT = "project"


class Config:
    """Runtime-safe + subprocess-safe configuration"""

    # ------------------------------------------------------------------
    # LLM / Groq
    # ------------------------------------------------------------------
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
    MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 4096))

    # ------------------------------------------------------------------
    # 🔒 RUNTIME STATE (IN-MEMORY CACHE)
    # ------------------------------------------------------------------
    _PROJECT_TYPE = ProjectType.UNKNOWN
    _EXECUTION_MODE = ExecutionMode.PROJECT

    BASE_URL = os.getenv("BASE_URL", "")

    # ------------------------------------------------------------------
    # Directories
    # ------------------------------------------------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FEATURES_DIR = os.path.join(BASE_DIR, "features")
    STEP_DEFINITIONS_DIR = os.path.join(BASE_DIR, "features", "steps")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    REQUIREMENTS_DIR = os.path.join(BASE_DIR, "requirements")

    # ------------------------------------------------------------------
    # Directory bootstrap
    # ------------------------------------------------------------------
    @classmethod
    def ensure_directories(cls):
        for directory in (
            cls.FEATURES_DIR,
            cls.STEP_DEFINITIONS_DIR,
            cls.REPORTS_DIR,
            cls.REQUIREMENTS_DIR,
        ):
            os.makedirs(directory, exist_ok=True)

    # ------------------------------------------------------------------
    # ✅ PROJECT TYPE (RUNTIME + SUBPROCESS SAFE)
    # ------------------------------------------------------------------
    @classmethod
    def set_project_type(cls, project_type: str):
        project_type = (project_type or "").lower()

        resolved = (
            project_type
            if project_type in {
                ProjectType.API,
                ProjectType.WEB,
                ProjectType.MOBILE,
                ProjectType.DATA,
                ProjectType.BACKEND,
            }
            else ProjectType.UNKNOWN
        )

        cls._PROJECT_TYPE = resolved

        # 🔥 Persist for Behave subprocess
        os.environ["BDD_PROJECT_TYPE"] = resolved

    @classmethod
    def get_project_type(cls) -> str:
        """
        Priority:
        1. In-memory runtime state
        2. Environment variable (subprocess-safe)
        3. UNKNOWN fallback
        """

        if cls._PROJECT_TYPE != ProjectType.UNKNOWN:
            return cls._PROJECT_TYPE

        env_type = os.getenv("BDD_PROJECT_TYPE", "").lower()
        if env_type in {
            ProjectType.API,
            ProjectType.WEB,
            ProjectType.MOBILE,
            ProjectType.DATA,
            ProjectType.BACKEND,
        }:
            cls._PROJECT_TYPE = env_type
            return env_type

        return ProjectType.UNKNOWN

    # ------------------------------------------------------------------
    # ✅ EXECUTION MODE (RUNTIME + SUBPROCESS SAFE)
    # ------------------------------------------------------------------
    @classmethod
    def set_execution_mode(cls, mode: str):
        resolved = (
            mode
            if mode in (ExecutionMode.FRAMEWORK, ExecutionMode.PROJECT)
            else ExecutionMode.FRAMEWORK
        )

        cls._EXECUTION_MODE = resolved

        # Optional persistence (useful for debugging / CI)
        os.environ["BDD_EXECUTION_MODE"] = resolved

    @classmethod
    def get_execution_mode(cls) -> str:
        if cls._EXECUTION_MODE:
            return cls._EXECUTION_MODE

        return os.getenv(
            "BDD_EXECUTION_MODE", ExecutionMode.FRAMEWORK
        )

    @classmethod
    def is_framework_mode(cls) -> bool:
        return cls.get_execution_mode() == ExecutionMode.FRAMEWORK

    @classmethod
    def is_project_mode(cls) -> bool:
        return cls.get_execution_mode() == ExecutionMode.PROJECT

    # ------------------------------------------------------------------
    # Import utility constants for backward compatibility
    # ------------------------------------------------------------------
    @staticmethod
    def get_timeouts():
        """Get timeout constants - delegates to utils.constants"""
        from utils.constants import Timeouts
        return Timeouts