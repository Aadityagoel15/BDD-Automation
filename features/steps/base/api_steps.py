from behave import when, then
import os
import requests
from config import Config


def _build_url(base_url: str, endpoint: str) -> str:
    """Helper to safely join base_url and endpoint paths."""
    return base_url.rstrip("/") + "/" + endpoint.lstrip("/")


def _resolve_base_url(context=None) -> str:
    """
    Resolve base_url for API calls in a project-agnostic way.

    Priority:
    1. Behave userdata (if context provided)
    2. Env vars: BEHAVE_USERDATA_BASE_URL, then BASE_URL
    3. Config.BASE_URL
    """
    if context is not None:
        base_url = context.config.userdata.get("base_url")
        if base_url:
            return base_url

    base_url = (
        os.getenv("BEHAVE_USERDATA_BASE_URL")
        or os.getenv("BASE_URL")
        or Config.BASE_URL
    )
    return base_url


def send_get_request(endpoint: str, context=None):
    """
    Generic helper used by generated steps to send GET requests.

    Intended usage from generated step files:
        from features.steps.base.api_steps import send_get_request
        response = send_get_request("/path")
    """
    base_url = _resolve_base_url(context)
    assert base_url, (
        "base_url not configured. "
        "Set it in behave.ini, bdd.config.yaml, or via BASE_URL env var"
    )

    url = _build_url(base_url, endpoint)
    return requests.get(url)


def send_post_request(endpoint: str, json=None, context=None):
    """
    Generic helper used by generated steps to send POST requests.

    Intended usage from generated step files:
        from features.steps.base.api_steps import send_post_request
        response = send_post_request("/path", json=payload)
    """
    base_url = _resolve_base_url(context)
    assert base_url, (
        "base_url not configured. "
        "Set it in behave.ini, bdd.config.yaml, or via BASE_URL env var"
    )

    url = _build_url(base_url, endpoint)
    return requests.post(url, json=json or {})


@when("I send a {method} request to the {endpoint} endpoint")
def send_request(context, method, endpoint):
    base_url = context.config.userdata.get("base_url")
    assert base_url, (
        "base_url not configured. "
        "Define it in behave.ini or bdd.config.yaml"
    )

    url = _build_url(base_url, endpoint)
    method = method.upper()

    response = requests.request(method, url)
    context.response = response


@when("I send a GET request to an empty endpoint")
def send_request_empty_endpoint(context):
    base_url = context.config.userdata.get("base_url")
    assert base_url, "base_url not configured"

    context.response = requests.get(base_url)


@then("the response status code should be {status_code:d}")
def verify_status_code(context, status_code):
    assert context.response is not None, "No response found"
    assert context.response.status_code == status_code
