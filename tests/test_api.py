import requests

def test_api_get_deals():
    r = requests.get("http://localhost:5200/deals")
    assert r.status_code == 200
