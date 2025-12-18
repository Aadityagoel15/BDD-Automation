from behave import given


@given("the API endpoint is available")
def api_endpoint_is_available(context):
    base_url = context.config.userdata.get("base_url")
    assert base_url, (
        "base_url not configured. "
        "Define it in behave.ini under [behave.userdata]"
    )
