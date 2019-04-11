#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the formatter."""

from .formatter import _decode_text, format_email_for_db, _remove_line_endings


def test_decode_text():
    s = 'test'
    text_decoded = _decode_text(s)
    assert text_decoded == 'test'
    assert isinstance(text_decoded, str)

    s = b'test'
    text_decoded = _decode_text(s)
    assert text_decoded == 'test'
    assert isinstance(text_decoded, str)

    s = 'test'.encode('utf-8')
    text_decoded = _decode_text(s)
    assert text_decoded == 'test'
    assert isinstance(text_decoded, str)


def test_format_main_interface():
    formatted_text = format_email_for_db('test')
    assert formatted_text == 'test\r\n'

    formatted_text = format_email_for_db('this is \r\n just a \r\n test')
    assert formatted_text == 'this is \r\n just a \r\n test\r\n'

    formatted_text = format_email_for_db('this is \n just a \n test')
    assert formatted_text == 'this is \r\n just a \r\n test\r\n'


def test_line_endings_formatting():
    s1 = 'this is \r\n just a \r\n test'
    formatted = _remove_line_endings(s1)
    assert formatted == 'this is \r\n just a \r\n test\r\n'

    s2 = 'this is \n just a \n test'
    formatted = _remove_line_endings(s2)
    assert formatted == 'this is \r\n just a \r\n test\r\n'

    s3 = 'this is \n just a \n test\n\n'
    formatted = _remove_line_endings(s3)
    assert formatted == 'this is \r\n just a \r\n test\r\n\r\n'
