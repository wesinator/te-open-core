#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .parse_headers import parse_header
from test_resources import DefaultTestObject

TestData = DefaultTestObject()


def test_header_values():
    parsed_header = parse_header(TestData.email_text)
    assert len(parsed_header) == 22

    for header_key, header_value in parsed_header:
        if header_key == 'To':
            assert header_value == 'bob <bob@gmail.com>'
        elif header_key == 'From':
            assert header_value == 'Alice Underwood <alice@gmail.com>'
        elif header_key == 'MIME_Version':
            assert header_value == '1.0'
        elif header_key == 'Subject':
            assert header_value == 'consider adding to python project template'


def test_no_header():
    """Make sure that all of the headers from each email are being recorded."""
    s = """
https://github.com/StylishThemes/GitHub-Dark/blob/master/tools/authors.sh

Yours truly,

Bob"""
    parsed_header = parse_header(s)
    assert parsed_header == []


def test_contact_parser():
    s = """Subject: Buy bitcoin now!
From: bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com"
    <bob@example.com>, "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>,
    "bob@example.com" <bob@example.com>
To: alice@gmail.com

Hi Alice Asimov!"""
    cleaned_email = parse_header(s)
    print('cleaned_email {}'.format(cleaned_email))
    assert 'bob' not in cleaned_email


def test_contact_parser_with_odd_spacing():
    """Make sure that the contact parser works even if there is no space between the contact and the email address (or if there are multiple spaces)."""
    s = """Subject: Buy bitcoin now!
From: bob@example.com"<bob@example.com>,
    "bob@example.com"   <bob@example.com>
To: alice@gmail.com

Hi Alice Asimov!"""
    cleaned_email = parse_header(s)
    print('cleaned_email {}'.format(cleaned_email))
    assert 'bob' not in cleaned_email
