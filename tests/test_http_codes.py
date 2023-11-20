# -*- coding: utf-8 -*-

from devsetgo_toolkit import ALL_HTTP_CODES, generate_code_dict


def test_generate_code_dict():
    # Test with a list of valid codes
    codes = [200, 404]
    expected_result = {
        200: {"description": ALL_HTTP_CODES[200]["description"]},
        404: {"description": ALL_HTTP_CODES[404]["description"]},
    }
    result = generate_code_dict(codes)
    assert result == expected_result

    # Test with a code that does not exist in ALL_HTTP_CODES
    codes = [200, 999]
    expected_result = {200: {"description": ALL_HTTP_CODES[200]["description"]}}
    result = generate_code_dict(codes)
    assert result == expected_result

    # Test with an empty list
    codes = []
    expected_result = {}
    result = generate_code_dict(codes)
    assert result == expected_result
