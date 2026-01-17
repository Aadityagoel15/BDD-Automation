"""
Common canonical BDD steps – SHARED (API + WEB)

Purpose:
- Centralize canonical steps
- Prevent duplication & ambiguity
- Support API & WEB execution
- AI-safe, Unicode-safe, project-safe
"""

from behave import given, when, then
from config import Config, ProjectType
from features.steps.base.api_steps import (
    send_post_request,
    verify_success_message,
    verify_error_message,
)

# ==================================================
# 🔒 UNICODE SAFETY (CRITICAL FOR WINDOWS + LLMs)
# ==================================================
def sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        return text

    return (
        text
        .replace("→", "->")
        .replace("←", "<-")
        .replace("✓", "[OK]")
        .replace("✗", "[FAIL]")
    )

# ==================================================
# 🌐 ENV / PRECONDITION STEPS
# ==================================================

@given("the API endpoint is available")
def api_endpoint_is_available(context):
    base_url = context.config.userdata.get("base_url")
    assert base_url, sanitize_text(
        "base_url not configured. "
        "Define it via BASE_URL env var or behave -D base_url=<url>"
    )

# ==================================================
# 🚀 EXECUTION STEPS (API – GENERIC)
# ==================================================

@when("the request is executed")
def execute_request(context):
    """
    Canonical API execution step.
    Endpoint & payload MUST be set earlier.
    """

    endpoint = getattr(context, "endpoint", None)
    payload = getattr(context, "payload", {})

    assert endpoint, sanitize_text(
        "context.endpoint not set before executing request"
    )

    send_post_request(
        context=context,
        endpoint=endpoint,
        json=payload
    )

# ==================================================
# ✅ ASSERTION STEPS (SINGLE SOURCE OF TRUTH)
# ==================================================

@given("the action should succeed")
@when("the action should succeed")
@then("the action should succeed")
def action_should_succeed(context):
    """
    Canonical success assertion (API + WEB)
    """

    project_type = Config.get_project_type()

    if project_type == ProjectType.API:
        verify_success_message(context)

    elif project_type == ProjectType.WEB:
        assert hasattr(context, "page"), sanitize_text(
            "WEB context.page not initialized"
        )
        assert hasattr(context, "last_action_success"), sanitize_text(
            "WEB step did not set context.last_action_success"
        )
        assert context.last_action_success is True, sanitize_text(
            "WEB action failed"
        )

    else:
        raise AssertionError(
            sanitize_text(f"Unknown project type: {project_type}")
        )


@given("the action should fail")
@when("the action should fail")
@then("the action should fail")
def action_should_fail(context):
    """
    Canonical failure assertion (API + WEB)
    """

    project_type = Config.get_project_type()

    if project_type == ProjectType.API:
        verify_error_message(context)

    elif project_type == ProjectType.WEB:
        assert hasattr(context, "page"), sanitize_text(
            "WEB context.page not initialized"
        )
        assert hasattr(context, "last_action_success"), sanitize_text(
            "WEB step did not set context.last_action_success"
        )
        assert context.last_action_success is False, sanitize_text(
            "WEB action unexpectedly succeeded"
        )

    else:
        raise AssertionError(
            sanitize_text(f"Unknown project type: {project_type}")
        )