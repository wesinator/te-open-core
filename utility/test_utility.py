#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utility import base64_decode


def test_base64_decode():
    assert base64_decode('Zm9vIGV4YW1wbGVAZ21haWwuY29tIHRlc3RpbmcgY29uZmlybWF0aW9u') == 'foo example@gmail.com testing confirmation'


def test_base64_decode_with_invalid_input():
    assert base64_decode('Q29uZm9ybSE==') == 'Conform!'
