"""
Behave environment setup for Playwright integration
Properly integrated with AI framework and configuration
"""

from playwright.sync_api import sync_playwright
from config import Config, ProjectType, ExecutionMode
import os


def before_all(context):
    """Initialize Playwright only for WEB projects in PROJECT mode"""
    context.config.setup_logging()
    
    # Only initialize browser for WEB projects in PROJECT mode
    project_type = Config.get_project_type()
    execution_mode = Config.get_execution_mode()
    
    # DEBUG: Print execution mode and project type
    print(f"[DEBUG] Execution mode: {execution_mode}")
    print(f"[DEBUG] Project type: {project_type}")
    print(f"[DEBUG] Environment BDD_EXECUTION_MODE: {os.getenv('BDD_EXECUTION_MODE', 'NOT SET')}")
    
    if project_type == ProjectType.WEB and execution_mode == ExecutionMode.PROJECT:
        # Check if UI testing is enabled
        ui_enabled = context.config.userdata.get("ui", "false").lower() == "true"
        
        if ui_enabled:
            context.playwright = sync_playwright().start()
            # Use headless mode by default, can be overridden
            headless = context.config.userdata.get("headless", "true").lower() == "true"
            context.browser = context.playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            context.page = context.browser.new_page()
            
            # Set viewport for consistent testing
            context.page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Set base URL from config
            base_url = (
                context.config.userdata.get("base_url") or
                Config.BASE_URL or
                ""
            )
            if base_url:
                context.base_url = base_url.rstrip('/')
            else:
                context.base_url = None


def before_scenario(context, scenario):
    """
    Setup before each scenario.
    RULE #1: Exactly ONE Playwright page per scenario. No exceptions.
    """
    # For framework mode, raise error if UI steps are executed
    if Config.is_framework_mode():
        return
    
    # CRITICAL: Guarantee ONE page per scenario
    # Check if page exists and is valid
    page_exists = hasattr(context, "page") and context.page is not None
    page_valid = False
    if page_exists:
        try:
            # Check if page is closed
            page_valid = not context.page.is_closed()
        except Exception:
            page_valid = False
    
    # Only create page if it doesn't exist OR is closed
    if Config.get_project_type() == ProjectType.WEB:
        ui_enabled = context.config.userdata.get("ui", "false").lower() == "true"
        
        if ui_enabled:
            # Ensure browser exists
            if not hasattr(context, "browser") or context.browser is None:
                if not hasattr(context, "playwright") or context.playwright is None:
                    context.playwright = sync_playwright().start()
                headless = context.config.userdata.get("headless", "true").lower() == "true"
                context.browser = context.playwright.chromium.launch(
                    headless=headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
            
            # Create page ONLY if it doesn't exist or is closed
            if not page_exists or not page_valid:
                context.page = context.browser.new_page()
                context.page.set_viewport_size({"width": 1920, "height": 1080})
                
                base_url = (
                    context.config.userdata.get("base_url") or
                    Config.BASE_URL or
                    ""
                )
                if base_url:
                    context.base_url = base_url.rstrip('/')
                else:
                    context.base_url = None


def after_scenario(context, scenario):
    """
    Cleanup after each scenario.
    RULE #1: Close page after each scenario to ensure clean state.
    """
    # Only cleanup in PROJECT mode
    if Config.is_framework_mode():
        return
    
    if hasattr(context, "page") and context.page:
        try:
            # Take screenshot on failure (optional)
            if scenario.status == "failed" and hasattr(context, "browser"):
                screenshot_dir = os.path.join(Config.REPORTS_DIR, "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(
                    screenshot_dir,
                    f"{scenario.name.replace(' ', '_')}_{scenario.line_number}.png"
                )
                context.page.screenshot(path=screenshot_path)
        except Exception:
            pass  # Don't fail on screenshot errors
        
        # CRITICAL: Close page after scenario to ensure clean state
        try:
            if not context.page.is_closed():
                context.page.close()
        except Exception:
            pass  # Don't fail on close errors


def after_all(context):
    """Cleanup after all scenarios"""
    # Only cleanup in PROJECT mode
    if Config.is_framework_mode():
        return
    
    if hasattr(context, "browser") and context.browser:
        try:
            context.browser.close()
        except Exception:
            pass
    
    if hasattr(context, "playwright") and context.playwright:
        try:
            context.playwright.stop()
        except Exception:
            pass
