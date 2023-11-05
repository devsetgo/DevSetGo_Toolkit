# -*- coding: utf-8 -*-
import pytest

from devsetgo_toolkit import ALL_HTTP_CODES
from devsetgo_toolkit import generate_code_dict


def test_generate_code_dict():
    # Test with description_only set to False (default)
    codes = [200, 404]
    expected_result = {200: ALL_HTTP_CODES[200], 404: ALL_HTTP_CODES[404]}
    result = generate_code_dict(codes)
    assert result == expected_result

    # Test with description_only set to True
    expected_result = {
        200: ALL_HTTP_CODES[200]["description"],
        404: ALL_HTTP_CODES[404]["description"],
    }
    result = generate_code_dict(codes, description_only=True)
    assert result == expected_result

    # Test with a code that does not exist in http_codes
    codes = [200, 999]
    expected_result = {200: ALL_HTTP_CODES[200]}
    result = generate_code_dict(codes)
    assert result == expected_result

    # Test with an empty list
    codes = []
    expected_result = {}
    result = generate_code_dict(codes)
    assert result == expected_result
