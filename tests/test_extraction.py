from services.data_source import extract_deals

def test_extract_deals():
    deals = extract_deals("test_token")
    assert deals is not None
