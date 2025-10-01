import requests

def test_health_endpoint():
    r = requests.get("http://localhost:5200/health")
    assert r.status_code == 200
