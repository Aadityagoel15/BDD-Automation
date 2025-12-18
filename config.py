"""
Configuration settings for BDD Automation AI Agents
"""
import os
from dotenv import load_dotenv

load_dotenv()


class ProjectType:
    """Supported project types"""
    API = "api"
    WEB = "web"
    MOBILE = "mobile"
    DATA = "data"
    BACKEND = "backend"
    UNKNOWN = "unknown"


class Config:
    """Configuration class for BDD Automation"""

    # ------------------------------------------------------------------
    # Groq API Configuration
    # ------------------------------------------------------------------
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ------------------------------------------------------------------
    # Project-level Configuration (optional overrides)
    # ------------------------------------------------------------------
    PROJECT_TYPE = os.getenv("PROJECT_TYPE", "").lower()  # api | web | data | mobile
    BASE_URL = os.getenv("BASE_URL", "")

    # ------------------------------------------------------------------
    # Project directories
    # ------------------------------------------------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FEATURES_DIR = os.path.join(BASE_DIR, "features")
    STEP_DEFINITIONS_DIR = os.path.join(BASE_DIR, "features","steps")
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    REQUIREMENTS_DIR = os.path.join(BASE_DIR, "requirements")

    # ------------------------------------------------------------------
    # Agent / LLM settings
    # ------------------------------------------------------------------
    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
    MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 4096))

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.FEATURES_DIR,
            cls.STEP_DEFINITIONS_DIR,
            cls.REPORTS_DIR,
            cls.REQUIREMENTS_DIR,
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @classmethod
    def has_explicit_project_type(cls) -> bool:
        """Check if project type is explicitly configured"""
        return cls.PROJECT_TYPE in {
            ProjectType.API,
            ProjectType.WEB,
            ProjectType.MOBILE,
            ProjectType.DATA,
            ProjectType.BACKEND,
        }

    @classmethod
    def get_project_type(cls) -> str:
        """
        Return explicitly configured project type if present,
        otherwise UNKNOWN (auto-detection will handle it).
        """
        if cls.has_explicit_project_type():
            return cls.PROJECT_TYPE
        return ProjectType.UNKNOWN
