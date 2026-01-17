"""
Constants for BDD Automation Framework
"""


class Timeouts:
    """Timeout constants in milliseconds"""
    DEFAULT = 30000  # 30 seconds
    SHORT = 10000    # 10 seconds
    LONG = 60000     # 60 seconds
    ELEMENT_WAIT = 5000  # 5 seconds
    ELEMENT_VISIBLE = 5000  # 5 seconds - for element visibility checks
    PAGE_LOAD = 30000    # 30 seconds


class ErrorMessages:
    """Standard error messages"""
    BROWSER_NOT_INITIALIZED = "Browser is not initialized. Please navigate to a page first."
    ELEMENT_NOT_FOUND = "Element not found"
    ELEMENT_NOT_VISIBLE = "Element is not visible"
    TIMEOUT = "Operation timed out"
    NAVIGATION_FAILED = "Navigation failed"
    INVALID_URL = "Invalid URL provided"


class CommonValues:
    """Common values used across the framework"""
    DEFAULT_WAIT_TIME = 5
    MAX_RETRIES = 3
    DEFAULT_PAGE_TIMEOUT = 30
    LOGIN_FIELDS = ["username", "user", "email", "password", "pass", "passwd", "pwd"]

