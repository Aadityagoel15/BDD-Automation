"""
Custom exceptions for BDD Automation Framework
"""


class FeatureGenerationError(Exception):
    """Raised when feature file generation fails"""
    pass


class BrowserNotInitializedError(Exception):
    """Raised when browser is not initialized"""
    pass


class ElementNotFoundError(Exception):
    """Raised when an element is not found on the page"""
    pass


class ElementNotVisibleError(Exception):
    """Raised when an element is not visible"""
    pass


class TimeoutError(Exception):
    """Raised when an operation times out"""
    pass








