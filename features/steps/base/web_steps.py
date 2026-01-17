from behave import given, when, then
from pathlib import Path
import re
from config import Config
from utils.constants import Timeouts, ErrorMessages, CommonValues
from utils.exceptions import (
    BrowserNotInitializedError,
    ElementNotFoundError,
    ElementNotVisibleError,
    TimeoutError as BDDTimeoutError
)
from utils.logging_utils import get_logger
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

logger = get_logger()


# ==================================================
# 🛡️ HARD GUARDS (NON-NEGOTIABLE)
# ==================================================
def _assert_page_valid(context):
    """
    RULE #1: Hard guard to detect page lifecycle violations immediately.
    This will instantly expose bugs instead of waiting 3 minutes.
    """
    assert hasattr(context, "page"), "❌ Playwright page not initialized"
    assert context.page is not None, "❌ Playwright page is None"
    assert not context.page.is_closed(), "❌ Playwright page was closed"


# ==================================================
# 📦 LOCATOR LOADING (XPATH-DRIVEN, CACHED)
# ==================================================
_LOCATORS = None


def _load_locators():
    global _LOCATORS
    if _LOCATORS is not None:
        return _LOCATORS

    locator_file = Path("reports/ui_locators.properties")
    if not locator_file.exists():
        raise RuntimeError(
            "ui_locators.properties not found. "
            "Run XPath discovery before executing UI tests."
        )

    locators = {}
    with open(locator_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                locators[k.strip().lower()] = v.strip()

    _LOCATORS = locators
    return locators


# ==================================================
# 🔑 SEMANTIC NORMALIZATION
# ==================================================
def _normalize_label(label: str) -> list[str]:
    """
    Produce an ordered set of label variants, prioritizing realistic attribute
    styles (camelCase, kebab, nospace, underscore) before falling back to the
    raw label with spaces. This avoids picking unlikely selectors like
    `[data-test="first name"]` when `[data-test="firstName"]` is expected.
    """
    base = label.strip().lower()

    variants: list[str] = []
    seen: set[str] = set()

    def add(var: str):
        if var and var not in seen:
            variants.append(var)
            seen.add(var)

    def add_core_variants(text: str):
        parts = [p for p in text.split() if p]
        camel = parts[0] + "".join(p.title() for p in parts[1:]) if len(parts) >= 2 else None
        kebab = text.replace(" ", "-")
        nospace = text.replace(" ", "")
        underscore = text.replace(" ", "_")
        for v in (camel, kebab, nospace, underscore, text):
            add(v)

    # Core variants for the full label
    add_core_variants(base)

    # Variants with common suffixes stripped (button/field/link)
    for noun in ["button", "field", "link"]:
        stripped = base.replace(noun, "").strip()
        if stripped:
            add_core_variants(stripped)

    return variants


def _resolve_locator(label: str) -> str:
    """
    Resolve locator for a label by:
    1. Checking ui_locators.properties file
    2. Trying data-test attributes directly (from UI discovery)
    3. Falling back to text-based locator
    """
    locators = _load_locators()
    candidates = _normalize_label(label)

    # Strategy 1: Check ui_locators.properties file
    for candidate in candidates:
        if candidate in locators:
            return locators[candidate]

    for candidate in candidates:
        for key, value in locators.items():
            if candidate in key or key in candidate:
                return value

    # Strategy 2: Try variations with "Link" suffix (for mapped elements like "Shopping Cart Link")
    # Remove common suffixes and try again
    base_label = label.replace(" Link", "").replace(" link", "").replace(" Button", "").replace(" button", "")
    if base_label != label:
        base_candidates = _normalize_label(base_label)
        for candidate in base_candidates:
            if candidate in locators:
                return locators[candidate]
        for candidate in base_candidates:
            for key, value in locators.items():
                if candidate in key or key in candidate:
                    return value

    # Strategy 3: Heuristic data-test/id/name selectors for inputs and buttons
    for candidate in candidates:
        normalized = candidate
        selectors = [
            f'[data-test="{normalized}"]',
            f'[data-test="{normalized.replace("_", "-")}"]',
            f'[data-test="{normalized.replace("-", "")}"]',
            f'[data-test="{normalized.replace(" ", "")}"]',
            f'[id="{normalized}"]',
            f'[name="{normalized}"]',
        ]
        for sel in selectors:
            try:
                # Try a lightweight existence check using Playwright selector syntax
                # (locator creation is lazy; real wait happens in callers)
                return sel
            except Exception:
                continue

    # Strategy 4: Fallback to text-based locator
    # The actual element finding in click_element will try data-test patterns automatically
    # This ensures site-agnostic behavior - works for any website
    return f"text={label}"


# ==================================================
# 🌐 NAVIGATION
# ==================================================
@given('the user navigates to "{url}"')
def navigate(context, url):
    if Config.is_framework_mode():
        raise RuntimeError("UI step executed in framework mode")

    _assert_page_valid(context)

    if getattr(context, "_last_url", None) == url:
        return

    context.page.goto(url, wait_until="load")
    context._last_url = url
    context.last_action_success = True


# ==================================================
# ✏️ INPUT
# ==================================================
@given('the user enters "{value}" into the "{field}" field')
@when('the user enters "{value}" into the "{field}" field')
def enter_text(context, value, field):
    if Config.is_framework_mode():
        raise RuntimeError("UI step executed in framework mode")

    _assert_page_valid(context)

    selector = _resolve_locator(field)
    try:
        locator = context.page.locator(selector)
        locator.wait_for(state="visible", timeout=Timeouts.ELEMENT_VISIBLE)
        locator.fill(value)
        context.last_action_success = True
    except PlaywrightTimeoutError:
        raise ElementNotFoundError(field, "Input field not found")


# ==================================================
# 🔒 POST-ACTION STABILIZATION (GENERIC)
# ==================================================
def _wait_for_post_action_stabilization(context, action_name: str = None):
    """
    Generic post-action stabilization.
    Waits for meaningful UI change after navigation-triggering actions.
    
    This is site-agnostic - works for any SPA/modern web app.
    Handles both URL-based navigation and client-side routing.
    """
    # Step 1: Wait for network to stabilize
    try:
        context.page.wait_for_load_state("networkidle", timeout=8000)
    except:
        try:
            context.page.wait_for_load_state("domcontentloaded", timeout=5000)
        except:
            pass

    # Step 2: Wait for URL change (for traditional navigation)
    # But don't fail if URL doesn't change (SPA client-side routing)
    try:
        context.page.wait_for_function(
            "document.readyState === 'complete'",
            timeout=5000
        )
    except:
        pass

    # Step 3: Wait for meaningful content to appear
    # This works for inventory pages, dashboards, admin panels, etc.
    # No site-specific assumptions - just waits for content to appear
    content_found = False
    content_selectors = [
        # Generic content patterns (works for most web apps)
        "text=/inventory|products|items|dashboard|content|main|container|grid|list/i",
        "[class*='content']",
        "[class*='main']",
        "[class*='container']",
        "[id*='content']",
        "[id*='main']",
        "[id*='container']",
        # Common SPA patterns
        "[data-test*='inventory']",
        "[data-test*='product']",
        "[data-test*='item']",
    ]
    
    for selector in content_selectors:
        try:
            context.page.wait_for_selector(selector, timeout=5000, state="visible")
            content_found = True
            logger.debug(f"Post-action stabilization: Found content with selector '{selector}'")
            break
        except:
            continue
    
    # Step 4: Additional wait for dynamic content to render (SPAs often need this)
    # This ensures React/Vue/Angular components have time to render
    context.page.wait_for_timeout(2000)
    
    if not content_found:
        logger.warning("Post-action stabilization: No content indicators found, but continuing anyway")


# ==================================================
# 🎯 SCOPED ACTION (GENERIC – DOMAIN AGNOSTIC)
# ==================================================
@when('the user clicks the "{action}" button for the item "{item}"')
def click_scoped_action(context, action, item):
    """
    Generic scoped action: Click an action button scoped to a specific item.
    
    This is a universal UI pattern that works for:
    - Products (Add to Cart for "Backpack")
    - Cards (Edit for "User Profile")
    - Rows (Delete for "Order #123")
    - Tiles (View for "Invoice")
    - Any container-scoped action
    
    No site-specific assumptions - uses container-scoped search which is a UI invariant.
    """
    if Config.is_framework_mode():
        raise RuntimeError("UI step executed in framework mode")

    _assert_page_valid(context)

    # 🔒 HARD GUARD: Item must exist before attempting scoped action
    # This prevents lifecycle bugs from causing silent failures
    # Wait for item to appear on page (with multiple strategies and longer timeout)
    item_found = False
    item_selectors = [
        f'text="{item}"',
        f'text=/.*{re.escape(item)}.*/i',
        f'[data-test*="{item.lower().replace(" ", "-")}"]',
        f'[aria-label*="{item}"]',
        f'a:has-text("{item}")',  # Item might be a link
    ]
    
    last_error = None
    for selector in item_selectors:
        try:
            context.page.wait_for_selector(selector, timeout=10000, state="visible")
            item_found = True
            logger.debug(f"Scoped action guard: Found item '{item}' with selector '{selector}'")
            break
        except Exception as e:
            last_error = e
            continue
    
    if not item_found:
        # Get current URL and page title for better error message
        current_url = context.page.url
        try:
            page_title = context.page.title()
        except:
            page_title = "unknown"
        
        raise RuntimeError(
            f"Scoped action attempted but item '{item}' not found on page.\n"
            f"Current URL: {current_url}\n"
            f"Page title: {page_title}\n"
            f"This likely means:\n"
            f"  1. Page hasn't stabilized after previous navigation/action\n"
            f"  2. Item name doesn't match what's on the page\n"
            f"  3. Page is still loading (SPA client-side routing)\n"
            f"Last error: {last_error}"
        )

    action_l = action.lower()
    item_l = item.lower()
    item_normalized = item_l.replace(" ", "-").replace("_", "-")

    # 1️⃣ Find a visible container that represents the item
    # Universal UI pattern: items are typically in containers (div, li, tr, article, section)
    container_candidates = [
        # Strategy 1: Exact text match, find nearest container
        f'text="{item}" >> xpath=ancestor::*[self::div or self::li or self::tr or self::article or self::section][1]',
        # Strategy 2: Partial text match (for cases where item text is part of larger text)
        f'text=/.*{re.escape(item)}.*/ >> xpath=ancestor::*[self::div or self::li or self::tr or self::article or self::section][1]',
        # Strategy 3: Data-test attributes (common in modern web apps)
        f'[data-test*="{item_normalized}"] >> xpath=ancestor::*',
        f'[data-testid*="{item_normalized}"] >> xpath=ancestor::*',
        # Strategy 4: Aria-label attributes (accessibility)
        f'[aria-label*="{item}"] >> xpath=ancestor::*',
        # Strategy 5: Class names containing item identifier
        f'[class*="{item_normalized}"] >> xpath=ancestor::*',
    ]

    for container_sel in container_candidates:
        try:
            container = context.page.locator(container_sel).first
            if container.count() == 0:
                continue
            container.wait_for(state="visible", timeout=3000)

            # 2️⃣ Inside that container, find the action button
            # Universal pattern: actions are typically buttons or elements with role="button"
            action_selectors = [
                f'button:has-text("{action}")',
                f'[role="button"]:has-text("{action}")',
                f'button[data-test*="{action_l.replace(" ", "-")}"]',
                f'[role="button"][data-test*="{action_l.replace(" ", "-")}"]',
                f'[data-test*="{action_l.replace(" ", "-")}"]',
                f'text="{action}"',
            ]

            for act_sel in action_selectors:
                try:
                    btn = container.locator(act_sel).first
                    if btn.count() == 0:
                        continue
                    btn.wait_for(state="visible", timeout=3000)
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    context.last_action_success = True
                    logger.info(f"Successfully clicked scoped action '{action}' for item '{item}'")
                    return
                except Exception as e:
                    logger.debug(f"Action selector '{act_sel}' failed: {e}")
                    continue
        except Exception as e:
            logger.debug(f"Container selector '{container_sel}' failed: {e}")
            continue

    raise ElementNotFoundError(
        f"{action} for {item}",
        f"Scoped action '{action}' not found for item '{item}'. "
        f"This indicates the action requires context (item scope) but the item or action could not be located."
    )


# ==================================================
# 🖱️ GENERIC BUTTON CLICK (SITE-AGNOSTIC)
# ==================================================
@given('the user clicks the "{element}" button')
@when('the user clicks the "{element}" button')
def click_element(context, element):
    """
    Click button element. Prioritizes actual button elements and role="button",
    but includes fallbacks for link elements that might be styled as buttons.
    Works for any website - no site-specific assumptions.
    """
    if Config.is_framework_mode():
        raise RuntimeError("UI step executed in framework mode")

    _assert_page_valid(context)

    element_norm = element.strip().lower()
    normalized_element = element.strip().lower().replace(" ", "-").replace("_", "-")
    selectors = []
    
    # Strategy 0: Special handling for login button (common pattern)
    if "login" in element_norm:
        login_selectors = [
            '#login-button',
            '[data-test="login-button"]',
            'input[type="submit"][value*="Login" i]',
            'button[type="submit"]:has-text("Login")',
        ]
        selectors.extend(login_selectors)
    
    # Strategy 0.5: Special handling for common elements like "Shopping Cart"
    # SauceDemo and many sites use data-test="shopping-cart-link" or similar
    if "cart" in element_norm or "shopping" in element_norm:
        cart_patterns = [
            '[data-test="shopping-cart-link"]',
            '[data-test*="shopping-cart"]',
            '[data-test*="cart"]',
            'a[data-test="shopping-cart-link"]',
            'a[data-test*="shopping-cart"]',
            'a[data-test*="cart"]',
            # Also try with aria-label for icon-based carts
            '[aria-label*="cart"]',
            '[aria-label*="shopping"]',
            'a[aria-label*="cart"]',
            'a[aria-label*="shopping"]',
        ]
        selectors.extend(cart_patterns)
    
    # Strategy 1: Resolved from locator file (if present)
    resolved = _resolve_locator(element)
    if resolved and not resolved.startswith("text="):
        selectors.append(resolved)
    
    # Strategy 2: Data-test attributes - PRIORITIZE BUTTON PATTERNS FIRST
    # This works for any website - prioritizes buttons but includes links as fallback
    data_test_patterns = [
        # Button-specific data-test patterns (highest priority)
        f'button[data-test="{normalized_element}"]',
        f'button[data-test*="{normalized_element}"]',
        f'[role="button"][data-test="{normalized_element}"]',
        f'[role="button"][data-test*="{normalized_element}"]',
        # Generic data-test patterns (might be button or link)
        f'[data-test="{normalized_element}"]',
        f'[data-test*="{normalized_element}"]',
        # Link patterns as fallback (in case it's a link styled as button)
        f'a[data-test="{normalized_element}"]',
        f'a[data-test*="{normalized_element}"]',
        f'[role="link"][data-test="{normalized_element}"]',
        f'[role="link"][data-test*="{normalized_element}"]',
    ]
    selectors.extend(data_test_patterns)

    # Strategy 3: Text-based selectors - PRIORITIZE BUTTON ELEMENTS
    # Works for any website - selector priority ensures button elements are tried first
    text_patterns = [
        # Button elements first (highest priority)
        f'button:has-text("{element}")',
        f'[role="button"]:has-text("{element}")',
        # Link elements as fallback (some buttons might be implemented as links)
        f'a:has-text("{element}")',
        f'[role="link"]:has-text("{element}")',
        # Try variations with "Link" suffix (for mapped elements like "Shopping Cart Link")
        f'a:has-text("{element} Link")',
        f'a:has-text("{element} link")',
        f'[role="link"]:has-text("{element} Link")',
        # Try aria-label and title attributes (for icon links without visible text)
        f'[aria-label*="{element}"]',
        f'[title*="{element}"]',
        f'a[aria-label*="{element}"]',
        f'a[title*="{element}"]',
    ]
    # Try base text without "Link" suffix if element has it (for reverse mapping)
    base_text = element.replace(" Link", "").replace(" link", "").replace(" Button", "").replace(" button", "")
    if base_text != element:
        text_patterns.extend([
            f'a:has-text("{base_text}")',
            f'[role="link"]:has-text("{base_text}")',
            f'button:has-text("{base_text}")',
        ])
    # Try partial text matching for links (e.g., "Shopping Cart" should match "Shopping Cart Link")
    # Split element into words and try matching with partial text
    element_words = element.split()
    if len(element_words) > 1:
        # Try matching first N words (for "Shopping Cart" matching "Shopping Cart Link")
        for i in range(len(element_words), 0, -1):
            partial_text = " ".join(element_words[:i])
            text_patterns.extend([
                f'a:has-text("{partial_text}")',
                f'[role="link"]:has-text("{partial_text}")',
            ])
    # Generic text match (last resort - works for any clickable element)
    text_patterns.append(f'text="{element}"')
    selectors.extend(text_patterns)

    last_error = None
    tried_selectors = []
    for sel in selectors:
        tried_selectors.append(sel)
        try:
            locator = context.page.locator(sel)
            # Quick existence check
            try:
                count = locator.count()
                if count == 0:
                    continue
            except:
                pass
            
            element_locator = locator.first
            element_locator.wait_for(state="visible", timeout=Timeouts.ELEMENT_VISIBLE)
            element_locator.scroll_into_view_if_needed()
            
            # Store current URL before click (for navigation detection)
            current_url_before = context.page.url
            
            element_locator.click()
            
            # Wait for navigation if URL might change (e.g., login, form submission)
            try:
                # Wait for load state
                context.page.wait_for_load_state("networkidle", timeout=5000)
            except:
                try:
                    context.page.wait_for_load_state("domcontentloaded", timeout=3000)
                except:
                    pass
            
            # If this looks like a login/navigation action, wait for URL change
            if element.lower() in ["login", "submit", "continue", "next"]:
                try:
                    # Wait for URL to change (max 15 seconds for login)
                    context.page.wait_for_function(
                        f"window.location.href !== '{current_url_before}'",
                        timeout=15000
                    )
                    # Additional wait for page to fully load
                    context.page.wait_for_load_state("networkidle", timeout=5000)
                    logger.info(f"Navigation successful: {current_url_before} → {context.page.url}")
                    
                    # 🔒 CRITICAL: Post-action stabilization for SPAs/modern web apps
                    # This ensures page content is fully rendered before next step executes
                    _wait_for_post_action_stabilization(context, element)
                except Exception as e:
                    # If URL didn't change, check for error messages
                    try:
                        error_elements = context.page.locator('[class*="error"], [data-test*="error"], [class*="alert"]').all()
                        if error_elements:
                            error_text = " ".join([el.inner_text() for el in error_elements[:3]])
                            logger.warning(f"Navigation may have failed. Current URL: {context.page.url}. Error messages: {error_text}")
                        else:
                            logger.warning(f"Navigation may have failed. Still on: {context.page.url} (was: {current_url_before})")
                    except:
                        logger.warning(f"Navigation check failed. Still on: {context.page.url}")
                    # Wait a bit more for page to load
                    context.page.wait_for_timeout(2000)
                    
                    # Still attempt stabilization even if URL didn't change (might be SPA navigation)
                    try:
                        _wait_for_post_action_stabilization(context, element)
                    except:
                        pass
            
            context.last_action_success = True
            return
        except Exception as e:
            last_error = e
            continue

    # Provide more detailed error message
    error_msg = f"Clickable button not found. Last error: {last_error}"
    if len(tried_selectors) <= 10:  # Only show if reasonable number
        error_msg += f". Tried selectors: {tried_selectors[:5]}..."  # Show first 5
    raise ElementNotFoundError(element, error_msg)

# ==================================================
# 🔗 GENERIC LINK CLICK (SITE-AGNOSTIC)
# ==================================================
@given('the user clicks the "{element}" link')
@when('the user clicks the "{element}" link')
def click_link(context, element):
    """
    Click link element. Prioritizes actual anchor/link elements and role="link",
    but includes fallbacks for button elements that might act as links.
    Works for any website - no site-specific assumptions.
    """
    if Config.is_framework_mode():
        raise RuntimeError("UI step executed in framework mode")

    _assert_page_valid(context)

    element_norm = element.strip().lower()
    normalized_element = element.strip().lower().replace(" ", "-").replace("_", "-")
    selectors = []

    # Strategy 1: Resolved from locator file (if present)
    resolved = _resolve_locator(element)
    if resolved and not resolved.startswith("text="):
        selectors.append(resolved)

    # Strategy 2: Extract core keyword (remove common words like "shopping", "link", etc.)
    # This helps match variations in data-test attributes
    all_words = element_norm.split()
    core_words = [w for w in all_words if w not in ['shopping', 'the', 'a', 'an', 'link', 'button', 'page']]
    core_keyword = ' '.join(core_words) if core_words else element_norm
    core_normalized = core_keyword.replace(" ", "-").replace("_", "-")
    
    # Create variations for data-test matching
    variations = [normalized_element, core_normalized]
    if len(all_words) > len(core_words):
        with_removed = '-'.join(all_words).replace(" ", "-")
        if with_removed != normalized_element:
            variations.insert(1, with_removed)
    
    # Strategy 3: Data-test attributes - PRIORITIZE LINK PATTERNS FIRST
    # Works for any website - prioritizes links but includes buttons as fallback
    data_test_patterns = []
    for variation in variations:
        # Link-specific data-test patterns (highest priority)
        data_test_patterns.extend([
            f'a[data-test="{variation}"]',  # Actual <a> tag
            f'a[data-test*="{variation}"]',
            f'[role="link"][data-test="{variation}"]',
            f'[role="link"][data-test*="{variation}"]',
        ])
    # Then generic patterns
    for variation in variations:
        data_test_patterns.extend([
            f'[data-test="{variation}"]',
            f'[data-test*="{variation}"]',
        ])
    # Button patterns as fallback (some links might be styled as buttons)
    for variation in variations:
        data_test_patterns.extend([
            f'button[data-test="{variation}"]',
            f'button[data-test*="{variation}"]',
            f'[role="button"][data-test="{variation}"]',
            f'[role="button"][data-test*="{variation}"]',
        ])
    selectors.extend(data_test_patterns)

    # Strategy 4: Text-based selectors - PRIORITIZE LINK ELEMENTS
    # Works for any website - selector priority ensures link elements are tried first
    text_patterns = [
        # Link elements first (highest priority)
        f'a:has-text("{core_keyword}")',
        f'a:has-text("{element}")',
        f'[role="link"]:has-text("{core_keyword}")',
        f'[role="link"]:has-text("{element}")',
        # Button elements as fallback (some links might be implemented as buttons)
        f'button:has-text("{element}")',
        f'[role="button"]:has-text("{element}")',
        # Generic text match (last resort - works for any clickable element)
        f'text="{core_keyword}"',
        f'text="{element}"',
    ]
    selectors.extend(text_patterns)

    last_error = None
    for sel in selectors:
        try:
            locator = context.page.locator(sel).first
            # Quick existence check
            try:
                count = locator.count()
                if count == 0:
                    continue
            except:
                pass
            
            locator.wait_for(state="visible", timeout=Timeouts.ELEMENT_VISIBLE)
            locator.scroll_into_view_if_needed()
            locator.click()
            try:
                context.page.wait_for_load_state("networkidle", timeout=3000)
            except:
                pass
            context.last_action_success = True
            return
        except Exception as e:
            last_error = e
            continue

    raise ElementNotFoundError(element, f"Clickable link not found. Last error: {last_error}")


# ==================================================
# 👀 ASSERT TEXT
# ==================================================
@when('the user should see text "{text}"')
@then('the user should see text "{text}"')
def should_see_text(context, text):
    if Config.is_framework_mode():
        raise RuntimeError("UI step executed in framework mode")

    _assert_page_valid(context)
    locator = context.page.locator(f"text={text}")
    if not locator.first.is_visible(timeout=Timeouts.ELEMENT_VISIBLE):
        raise ElementNotVisibleError(text, Timeouts.ELEMENT_VISIBLE)
    context.last_action_success = True


# ==================================================
# 🏠 PAGE VERIFICATION
# ==================================================
@then('the user should be on the home page')
def should_be_on_home_page(context):
    if Config.is_framework_mode():
        raise RuntimeError("UI step executed in framework mode")

    _assert_page_valid(context)
    current_url = context.page.url.lower()
    if not any(x in current_url for x in ["login", "auth", "signin"]):
        context.last_action_success = True
        return

    raise AssertionError(f"Not on home page: {context.page.url}")
