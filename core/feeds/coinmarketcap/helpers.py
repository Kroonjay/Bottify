from requests import Session


def get_cmc_session(api_key):
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    session = Session()
    session.headers.update(headers)
    return session
