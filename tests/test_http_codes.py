import pytest
from devsetgo_toolkit.http_codes import generate_code_dict


def test_generate_code_dict():
    # Test with a few known codes
    result = generate_code_dict([200, 404, 500])
    expected_result = {
        200: {"description": "OK"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    }
    assert result == expected_result

    # Test with a non-existent code
    result = generate_code_dict([999])
    assert result == {}

    # Test with a mix of valid and invalid codes
    result = generate_code_dict([200, 999])
    expected_result = {200: {"description": "OK"}}
    assert result == expected_result
