#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import email

from .parse_headers import parse_header, _multi_contact_parser
from db.models import JOIN_STRING
from test_resources import DefaultTestObject

TestData = DefaultTestObject()


def test_not_dropping_data():
    """Make sure that all of the headers from each email are being recorded."""
    for email_message in TestData.parser_test_email_messages:
        duplicate_header_properties = 0
        parsed_header_properties = parse_header(email_message, log_mising_properties=False)
        # check to see if any of the properties are duplicated (e.g. two "Received" properties)
        for property_ in parsed_header_properties:
            if JOIN_STRING in parsed_header_properties[property_]:
                duplicate_header_properties += parsed_header_properties[property_].count(JOIN_STRING)

        assert len(parsed_header_properties) + duplicate_header_properties == len(email_message.items())


def test_header_values():
    parsed_header_properties = parse_header(TestData.email_message, log_mising_properties=False)
    assert len(parsed_header_properties) == 20

    assert (
        parsed_header_properties['Received'].replace('\n', '')
        == """by 10.74.51.193 with SMTP id q184csp3395227ooq;        Fri, 22 Sep 2017 09:34:39 -0700 (PDT)|||from mail-sor-f41.google.com (mail-sor-f41.google.com. [209.85.220.41])        by mx.google.com with SMTPS id c92sor105637uac.93.2017.09.22.09.34.39        for <bob@gmail.com>        (Google Transport Security);        Fri, 22 Sep 2017 09:34:39 -0700 (PDT)"""
    )

    for header in parsed_header_properties:
        if header == 'To':
            assert parsed_header_properties[header][0]['email'] == 'bob@gmail.com'
            assert parsed_header_properties[header][0]['name'] == 'bob'
        elif header == 'From':
            assert parsed_header_properties[header]['email'] == 'alice@gmail.com'
            assert parsed_header_properties[header]['name'] == 'Alice Underwood'
        elif header == 'MIME_Version':
            assert parsed_header_properties[header] == '1.0'
        elif header == 'Subject':
            assert parsed_header_properties[header] == 'consider adding to python project template'


def test_no_header():
    """Make sure that all of the headers from each email are being recorded."""
    email_message = email.message_from_string(
        """
https://github.com/StylishThemes/GitHub-Dark/blob/master/tools/authors.sh

Yours truly,

Bob"""
    )
    parsed_header_properties = parse_header(email_message, log_mising_properties=False)
    assert parsed_header_properties == {}


def test_x_mailer():
    email_message = email.message_from_string(
        """From r-help-bounces@stat.math.ethz.ch  Wed Jun 20 12:51:20 2007
To: gavin.simpson@ucl.ac.uk
X-Mailer: Apple Mail (2.752.2)

https://github.com/StylishThemes/GitHub-Dark/blob/master/tools/authors.sh

Yours truly,

Bob"""
    )
    parsed_header_properties = parse_header(email_message, log_mising_properties=False)
    print("parsed_header_properties {}".format(parsed_header_properties))
    assert parsed_header_properties['X_Mailer'] == 'Apple Mail (2.752.2)'


def test_delivered_to():
    email_message = email.message_from_string(
        """Delivered-To: bob@gmail.com
Received: by 2002:a4a:88e7:0:0:0:0:0 with SMTP id q36csp7016057ooh;
        Mon, 3 Dec 2018 06:51:22 -0800 (PST)

https://github.com/StylishThemes/GitHub-Dark/blob/master/tools/authors.sh

Yours truly,

Bob"""
    )
    parsed_header_properties = parse_header(email_message, log_mising_properties=False)
    print("parsed_header_properties {}".format(parsed_header_properties))
    assert parsed_header_properties['Delivered_To'] == 'bob@gmail.com'


def test_contact_parser():
    s = """"bob@example.com" <bob@example.com>,
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
    "bob@example.com" <bob@example.com>"""
    results = _multi_contact_parser(s)
    assert len(results) == 48
    for result in results:
        assert result['name'] is not None
        assert '\n' not in result['email']


def test_contact_parser_with_odd_spacing():
    """Make sure that the contact parser works even if there is no space between the contact and the email address (or if there are multiple spaces)."""
    s = """"bob@example.com"<bob@example.com>,
    "bob@example.com"   <bob@example.com>"""
    results = _multi_contact_parser(s)
    assert len(results) == 2
    for result in results:
        assert result['name'] is not None
        assert '\n' not in result['email']
