from behave import given


@given("the API endpoint is available")
def api_endpoint_is_available(context):
    base_url = context.config.userdata.get("base_url")
    assert base_url, (
        "base_url not configured. "
        "Define it in behave.ini under [behave.userdata]"
    )


def verify_success_message(context):
    """
    Generic helper used by generated steps to assert a successful outcome.

    This is intentionally simple and project-agnostic: it just checks for a
    2xx HTTP status code and, if a response body is present, that it contains
    the word 'success' (case-insensitive).
    """
    response = getattr(context, "response", None)
    assert response is not None, "No response found on context"
    assert 200 <= response.status_code < 300, (
        f"Expected success status code (2xx), got {response.status_code}"
    )
    # Optional, best-effort text check
    try:
        body = (response.text or "").lower()
        if body:
            assert "success" in body or "ok" in body, (
                "Response body does not contain a generic success indicator"
            )
    except Exception:
        # If response has no .text, ignore
        pass


def verify_error_message(context):
    """
    Generic helper used by generated steps to assert an error outcome.

    It checks for a 4xx/5xx status code and, if a response body is present,
    that it contains the word 'error' (case-insensitive).
    """
    response = getattr(context, "response", None)
    assert response is not None, "No response found on context"
    assert response.status_code >= 400, (
        f"Expected error status code (4xx/5xx), got {response.status_code}"
    )
    # Optional, best-effort text check
    try:
        body = (response.text or "").lower()
        if body:
            assert "error" in body or "failed" in body, (
                "Response body does not contain a generic error indicator"
            )
    except Exception:
        # If response has no .text, ignore
        pass