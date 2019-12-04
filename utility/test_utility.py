#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utility import (
    base64_decode,
    domain_is_common,
    ip_address_is_common,
    email_bodies_as_objects,
    email_read,
    email_attachments,
    _calculate,
    SOURCE_WEIGHTINGS,
)

ATTACHMENT_EMAIL = """MIME-Version: 1.0
Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>
Content-Type: multipart/mixed; boundary="000000000000c4860205873c8e43"

--000000000000c4860205873c8e43
Content-Type: multipart/alternative; boundary="000000000000c485ff05873c8e41"

--000000000000c485ff05873c8e41
Content-Type: text/plain; charset="UTF-8"

This foobar is a test

--000000000000c485ff05873c8e41
Content-Type: text/html; charset="UTF-8"

<div dir="ltr">This foobar is a test</div>

--000000000000c485ff05873c8e41--
--000000000000c4860205873c8e43
Content-Type: text/plain; charset="US-ASCII"; name="test.txt"
Content-Disposition: attachment; filename="test.txt"
Content-Transfer-Encoding: base64
X-Attachment-Id: f_juujbxeu0
Content-ID: <f_juujbxeu0>

Zm9vYmFyCg==
--000000000000c4860205873c8e43--"""


def test_ip_address_is_common_1():
    assert ip_address_is_common('127.0.0.1')
    assert not ip_address_is_common('1.7.2.5')


def test_base64_decode():
    assert (
        base64_decode('Zm9vIGV4YW1wbGVAZ21haWwuY29tIHRlc3RpbmcgY29uZmlybWF0aW9u')
        == 'foo example@gmail.com testing confirmation'
    )


def test_base64_decode_with_invalid_input():
    assert base64_decode('Q29uZm9ybSE==') == 'Conform!'


def test_domain_is_common_1():
    assert domain_is_common('google.com')
    assert domain_is_common('mx.google.com')
    assert not domain_is_common('foo.com')
    assert not domain_is_common('example.com')


def test_email_bodies_as_objects():
    bodies = email_bodies_as_objects(email_read(ATTACHMENT_EMAIL))
    assert len(bodies) == 2

    bodies = email_bodies_as_objects(ATTACHMENT_EMAIL)
    assert len(bodies) == 2


def test_email_attachments():
    attachments = email_attachments(email_read(ATTACHMENT_EMAIL))
    assert len(attachments) == 1

    attachments = email_attachments(ATTACHMENT_EMAIL)
    assert len(attachments) == 1


def test_calculate_1():
    for source_name, function in SOURCE_WEIGHTINGS.items():
        print('\n{}'.format(source_name))
        for i in range(10):
            print('{}: {}'.format(i, _calculate(i, source_name)))

    assert 1 == 2
