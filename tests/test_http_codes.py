# -*- coding: utf-8 -*-
import pytest

from devsetgo_toolkit.http_codes import generate_code_dict
from devsetgo_toolkit.http_codes import http_codes


def test_generate_code_dict():
    # Test with description_only set to False (default)
    codes = [200, 404]
    expected_result = {200: http_codes[200], 404: http_codes[404]}
    result = generate_code_dict(codes)
    assert result == expected_result

    # Test with description_only set to True
    expected_result = {
        200: http_codes[200]["description"],
        404: http_codes[404]["description"],
    }
    result = generate_code_dict(codes, description_only=True)
    assert result == expected_result

    # Test with a code that does not exist in http_codes
    codes = [200, 999]
    expected_result = {200: http_codes[200]}
    result = generate_code_dict(codes)
    assert result == expected_result

    # Test with an empty list
    codes = []
    expected_result = {}
    result = generate_code_dict(codes)
    assert result == expected_result
