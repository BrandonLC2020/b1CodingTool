import pytest
import re

def extract_list_id(input_str: str) -> str | None:
    # Pattern to match 11-13 digits after "li/" or as a standalone string
    match = re.search(r"li/(\d{11,13})(?:\?|$)", input_str)
    if match:
        return match.group(1)
    match = re.search(r"^(\d{11,13})$", input_str)
    return match.group(1) if match else None

def test_extract_list_id_raw():
    assert extract_list_id("901414778471") == "901414778471"

def test_extract_list_id_url():
    url = "https://app.clickup.com/90141049639/v/li/901414778471"
    assert extract_list_id(url) == "901414778471"

def test_extract_list_id_invalid():
    assert extract_list_id("invalid") is None
