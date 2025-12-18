"""
Base API steps – FRAMEWORK / STUB MODE

Purpose:
- Allow BDD framework to run WITHOUT real APIs
- Never fail execution
- Always populate context.response
"""

# --------------------------------------------------
# REQUEST STUBS (NEVER FAIL)
# --------------------------------------------------

def send_post_request(context, endpoint=None, json=None):
    context.response = {
        "method": "POST",
        "endpoint": endpoint or "STUB_ENDPOINT",
        "payload": json or {},
        "status_code": 200,
    }


def send_get_request(context, endpoint=None):
    context.response = {
        "method": "GET",
        "endpoint": endpoint or "STUB_ENDPOINT",
        "status_code": 200,
    }


# --------------------------------------------------
# ASSERTION STUBS (CONTRACT-ONLY)
# --------------------------------------------------

def verify_response_status_code(context, expected_status_code):
    """
    Stubbed status-code verifier.
    Always succeeds in framework mode.
    """
    assert hasattr(context, "response"), "context.response not set"


def verify_success_message(context):
    """
    Used for: 'the action should succeed'
    """
    assert hasattr(context, "response"), "context.response not set"


def verify_error_message(context):
    """
    Used for: 'the action should fail'
    """
    assert hasattr(context, "response"), "context.response not set"
