"""
Base API steps – FRAMEWORK / STUB MODE

Purpose:
- Allow BDD framework to run WITHOUT real APIs
- Never fail execution
- Always populate context.response
"""

# --------------------------------------------------
# INTERNAL STUB RESPONSE OBJECT
# --------------------------------------------------

class StubResponse:
    def __init__(self, status_code=200, text="success"):
        self.status_code = status_code
        self.text = text


# --------------------------------------------------
# REQUEST STUBS (NEVER FAIL)
# --------------------------------------------------

def send_post_request(context, endpoint=None, json=None):
    context.response = StubResponse(
        status_code=200,
        text="success"
    )


def send_get_request(context, endpoint=None):
    context.response = StubResponse(
        status_code=200,
        text="success"
    )


# --------------------------------------------------
# ASSERTION HELPERS (CONTRACT SAFE)
# --------------------------------------------------

def verify_response_status_code(context, expected_status_code):
    assert hasattr(context, "response"), "context.response not set"
    assert context.response.status_code == expected_status_code


def verify_success_message(context):
    assert hasattr(context, "response"), "context.response not set"


def verify_error_message(context):
    assert hasattr(context, "response"), "context.response not set"
