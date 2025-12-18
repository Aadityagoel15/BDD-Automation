import os
from config import ProjectType

API_KEYWORDS = ["api", "endpoint", "status code", "http", "rest", "graphql"]
WEB_KEYWORDS = ["browser", "click", "page", "ui", "button", "form"]
DATA_KEYWORDS = ["pipeline", "etl", "batch", "database", "table"]
MOBILE_KEYWORDS = ["android", "ios", "apk", "ipa", "mobile"]

def detect_project_type(project_path: str = None, requirements: str = "") -> str:
    """
    Detect project type using:
    1. File inspection
    2. Requirement keywords
    """

    # ---------- 1. File-based detection ----------
    if project_path and os.path.exists(project_path):
        for root, _, files in os.walk(project_path):
            for f in files:
                name = f.lower()

                if name in ("openapi.yaml", "swagger.yaml"):
                    return ProjectType.API
                if name.endswith((".html", ".jsx", ".tsx")):
                    return ProjectType.WEB
                if name == "androidmanifest.xml":
                    return ProjectType.MOBILE
                if name.endswith(".sql"):
                    return ProjectType.DATA

    # ---------- 2. Requirement-based detection ----------
    text = requirements.lower()

    if any(k in text for k in API_KEYWORDS):
        return ProjectType.API
    if any(k in text for k in WEB_KEYWORDS):
        return ProjectType.WEB
    if any(k in text for k in MOBILE_KEYWORDS):
        return ProjectType.MOBILE
    if any(k in text for k in DATA_KEYWORDS):
        return ProjectType.DATA

    return ProjectType.UNKNOWN
