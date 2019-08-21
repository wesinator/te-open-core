#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""These are functions to test cleaner.py. The only test the functionality of the algorithm and DO NOT test the views related to the cleaner. Those are located in the test file with the other view tests (at the time of writing that is the `test_views.py` file, but that may change)."""

from .cleaner import clean_email
from test_resources import DefaultTestObject
from utility import utility

TestData = DefaultTestObject()

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


def test_cleaner():
    """Make sure the cleaner is working as expected."""
    to_field = [{'name': 'Bob', 'email': 'bob@gmail.com'}]
    assert to_field[0]['name'] in TestData.email_text
    assert to_field[0]['email'] in TestData.email_text
    cleaned_email = clean_email(TestData.email_text)
    assert to_field[0]['name'] not in cleaned_email
    assert to_field[0]['email'] not in cleaned_email


def test_cleaner_delivered_to():
    """Make sure the cleaner is handling delivered-to header properties correctly."""
    cleaned_email = clean_email(TestData.delivered_to_email_text)
    assert 'bob@gmail.com' not in cleaned_email


def test_cleaner_with_email_with_blank_names():
    """There was a problem with emails where the name of the "To" field is an empty string (rather than None). This test makes sure that this is working properly."""
    email_text = """Delivered-To: bob@gmail.com
Received: by 2002:a4a:88e7:0:0:0:0:0 with SMTP id q36csp2004394ooh;
        Thu, 17 Jan 2019 08:04:11 -0800 (PST)
X-Google-Smtp-Source: ALg8bN5dhjjj8dEb/t7GkAAHhAItqM+BzWn0SeVXKsNnsh5Cj6s61ezQdN8LkrpGw4Y2yHTvmuLo
X-Received: by 2002:a6b:e70b:: with SMTP id b11mr8072946ioh.175.1547741051806;
        Thu, 17 Jan 2019 08:04:11 -0800 (PST)
ARC-Seal: i=1; a=rsa-sha256; t=1547741051; cv=none;
        d=google.com; s=arc-20160816;
        b=NIM4AH02fjvL1VJVPNUrUDrxt/fiIKuCMXphLqyKgcvY80ZtJD5t09kD1n5/looK05
         wwP+Rsrr0qi42xfytMWVx/VwGkFX9xXYXqpRf0+bWi0NnsUAOUwOHSJ8jFZSkRvceOI8
         MIp+NAVxNA1pfqcAFOEfwJ/okbc8u5pon5wLbMtWC3p1yTz2Vk2LeHx5ywjf/RcHOrpu
         diRx5TAngOqIkL+WT14wUlZuVMwo5vINmqk/6tf6t+uKGfqxHhi3ONJptoC4a0YOUXaL
         hwQRt2XXrqZ60cXPhxCZQWI/xrOP7bO01rr7ztwQZ4iIIwi/oGixCDfyxHrXeH5hJOgL
         jyiw==
ARC-Message-Signature: i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20160816;
        h=message-id:to:subject:date:from:list-unsubscribe;
        bh=liW3gmO4zhsYuuYdkHIbew1mCcNrtk6ra9jr7XxVnok=;
        b=iayvaqYrPjj4Gk/CTQJ8FgbFS3TNO6gNgqlUg8bJ5Ggrji+lSzfb81CAI1KjgtQkLo
         gEDkj+1u6B+ytZQNx+CN2mu/d63cxfCslWCro9TQQHU52u2tuBinAsR8/ynqflJ6KGPF
         xIfHxIqaA9FJ03WsXS11Jp2HKPGc56HwhX84VOduHToVbfNMEd3CUoFfhu5ObRnQtr7E
         q9DZ1GQRuDKXLUhzylX75e1OXo+mu0A/xiPqXJIgL0+YY+CTwtbgkroSa2YgvJ4y5QZQ
         xwaX2tSeEDhmIqhp+kUh2zd/XaXjBrQ7DULSMnFHzYaZeTiD/PFZ3Wh+sGC9ZJq2izsA
         cSvA==
ARC-Authentication-Results: i=1; mx.google.com;
       spf=neutral (google.com: 3.16.219.39 is neither permitted nor denied by best guess record for domain of return@5ijy2f3-----.3.16.219.39) smtp.mailfrom=return@5ijy2f3-----.3.16.219.39
Return-Path: <return@5ijy2f3-----.3.16.219.39>
Received: from sale.5bike-socks.com (ec2-3-16-219-39.us-east-2.compute.amazonaws.com. [3.16.219.39])
        by mx.google.com with ESMTP id p127si1132653itp.84.2019.01.17.08.04.11
        for <bob@gmail.com>;
        Thu, 17 Jan 2019 08:04:11 -0800 (PST)
Received-SPF: neutral (google.com: 3.16.219.39 is neither permitted nor denied by best guess record for domain of return@5ijy2f3-----.3.16.219.39) client-ip=3.16.219.39;
Authentication-Results: mx.google.com;
       spf=neutral (google.com: 3.16.219.39 is neither permitted nor denied by best guess record for domain of return@5ijy2f3-----.3.16.219.39) smtp.mailfrom=return@5ijy2f3-----.3.16.219.39
Received: from efianalytics.com (efianalytics.com. 216.244.76.116)
List-Unsubscribe: <YIM77KG3573CUQ2OXICUN089I9ET5Q-JER7TSMR3GNFHGY0R4IRK0J9YFKU8V@sale.5bike-socks.com>
from:  CONFIRM bob <OVI4JJMHHYL8DFK0DU321WBZAFH8WO@4VRJUNDP4OSIWBKGVD7NO42WOTTW8P.net>
Date: Thu, 17 Jan 2019 11:04:10 -0500
Subject: Client #980920416 To_STOP_Receiving These Emails From Us Hit reply And Let Us Know..
To: <EPN253807OOHYET6GN44M8@itlgopk.uk>
Message-Id: <LCDTNQWZF276MRPAFAT0L92DLKCB8E8-FIM0ZK9NA88SQR60SI08AEKCHWCEWD@vevida.net>
X-EMMAIL: [First_Part]@sale.5bike-socks.com
Content-Type: text/html; charset=utf-8

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml">
...
"""
    cleaned_email = clean_email(email_text)
    assert cleaned_email.count('REDACTED') == 3


def test_cleaner_casing():
    assert 'Date' in TestData.email_text
    assert 'Yours truly' in TestData.email_text
    assert '//github.com' in TestData.email_text
    assert 'Bob' in TestData.email_text
    cleaned_email = clean_email(TestData.email_text, 'Yours truly,Date,//github.com,Bob')
    print('cleaned_email {}'.format(cleaned_email))
    assert 'Date' not in cleaned_email
    assert 'Yours truly' not in cleaned_email
    assert '//github.com' not in cleaned_email
    assert 'Bob' not in cleaned_email


def test_cleaner_input_stripping():
    assert 'X-Google-Smtp-Source' in TestData.email_text
    assert 'Yours truly' in TestData.email_text
    assert '//github.com' in TestData.email_text
    assert 'Bob' in TestData.email_text
    cleaned_email = clean_email(TestData.email_text, 'Yours truly, X-Google-Smtp-Source, //github.com, Bob')
    print('cleaned_email {}'.format(cleaned_email))
    assert 'X-Google-Smtp-Source' not in cleaned_email
    assert 'Yours truly' not in cleaned_email
    assert '//github.com' not in cleaned_email
    assert 'Bob' not in cleaned_email


def test_multi_instance_name_parsing():
    s = """Subject: Buy bitcoin now!
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>

Hi Alice Asimov!"""

    cleaned_email = clean_email(s)
    print('cleaned_email {}'.format(cleaned_email))
    assert 'Alice Asimov' not in cleaned_email
    assert 'alice@gmail.com' not in cleaned_email


def test_cleaner_simple_to_field():
    s = """Subject: Buy bitcoin now!
From: Bob Bradbury <bob@gmail.com>
To: alice@gmail.com

Hi Alice Asimov!"""

    cleaned_email = clean_email(s)
    print('cleaned_email {}'.format(cleaned_email))
    assert 'alice@gmail.com' not in cleaned_email


def test_multi_recipient():
    s = """Subject: Buy bitcoin now!
From: Bob Bradbury <bob@gmail.com>
To: alice@gmail.com, foo@bar.com, Charlee <charlee@gmail.com>

Hi Alice Asimov (and Charlee)!"""

    cleaned_email = clean_email(s)
    print('cleaned_email {}'.format(cleaned_email))
    assert 'alice@gmail.com' not in cleaned_email
    assert 'Charlee' not in cleaned_email
    assert 'charlee@gmail.com' not in cleaned_email

    s = """Subject: Buy bitcoin now!
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>, foo@bar.com, Charlee <charlee@gmail.com>

Hi Alice Asimov (and Charlee)!"""

    cleaned_email = clean_email(s)
    print('cleaned_email {}'.format(cleaned_email))
    assert 'Alice Asimov' not in cleaned_email
    assert 'alice@gmail.com' not in cleaned_email


def test_utf_header_cleaning():
    s = """Subject: =?UTF-8?B?Q29uZmlybWF0aW9uIE5lZWRlZDogZXhhbXBsZUBnbWFpbC5jb20=?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>

Foo"""
    cleaned_email = clean_email(s, redaction_values='example@gmail.com')
    print('cleaned_email {}'.format(cleaned_email))
    assert 'Q29uZmlybWF0aW9uIE5lZWRlZDogZXhhbXBsZUBnbWFpbC5jb20=' not in cleaned_email
    assert 'Q29uZmlybWF0aW9uIE5lZWRlZDogUkVEQUNURUQ=' in cleaned_email

    s = 'Subject: =?UTF-8?B?Zm9vIGV4YW1wbGVAZ21haWwuY29tIHRlc3RpbmcgY29uZmlybWF0aW9u?='
    cleaned_email = clean_email(s, redaction_values='example@gmail.com')
    print('cleaned_email {}'.format(cleaned_email))
    assert 'GV4YW1wbGVAZ21haWwuY29t' not in cleaned_email
    assert 'Zm9vIFJFREFDVEVEIHRlc3RpbmcgY29uZmlybWF0aW9u' in cleaned_email


def test_utf_invalid_header():
    s = """Subject: =?UTF-8?B?Q29uZm9ybSE==?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>

Foo"""
    cleaned_email = clean_email(s, redaction_values='Conform')
    assert 'Q29uZm9ybSE==' not in cleaned_email
    assert 'Subject: =?UTF-8?B?UkVEQUNURUQh?=' in cleaned_email


def test_redaction_of_email_address_name_from_utf_encoded_subject():
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>

Foo"""
    cleaned_email = clean_email(s)
    print('cleaned_email {}'.format(cleaned_email))
    assert 'aGkgYWxpY2UgYXNpbW92' not in cleaned_email
    assert 'Subject: =?UTF-8?B?aGkgUkVEQUNURUQ=?=' in cleaned_email


def test_base64_encoded_body_redaction():
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>
Content-Type: text/html;
    charset="utf-8"
Content-Transfer-Encoding: base64

SSdtIHNvcnJ5IERhdmUsIEknbSBhZnJhaWQgSSBjYW4ndCBkbyB0aGF0

"""
    cleaned_email = clean_email(s, redaction_values='dave')
    assert 'SSdtIHNvcnJ5IERhdmUsIEknbSBhZnJhaWQgSSBjYW4ndCBkbyB0aGF0' not in cleaned_email
    assert 'SSdtIHNvcnJ5IFJFREFDVEVELCBJJ20gYWZyYWlkIEkgY2FuJ3QgZG8gdGhhdA==' in cleaned_email


def test_base64_encoded_body_redaction_in_multipart_email():
    s = """From: "Bar, Foo" <Foo>
To: "REDACTED" <REDACTED>
Subject:
 =?utf-8?B?0KLQvtC70YzQutC+INC00LvRjyDQvdCw0YjQuNGFINC00YDRg9C30LXQuQ==?=
Content-Type: multipart/alternative;
    boundary="_000_886b229e3de3c9c12d289e32df4b615ba1cca7easdpaorg_"
MIME-Version: 1.0

--_000_886b229e3de3c9c12d289e32df4b615ba1cca7easdpaorg_
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: base64

SSdtIHNvcnJ5IERhdmUsIEknbSBhZnJhaWQgSSBjYW4ndCBkbyB0aGF0

--_000_886b229e3de3c9c12d289e32df4b615ba1cca7easdpaorg_
Content-Type: text/html; charset="utf-8"
Content-ID: <3AE5B20EAE07E240A62C41F25E44173E@namprd02.prod.outlook.com>
Content-Transfer-Encoding: base64

PGh0bWw+DQo8aGVhZD4NCjxtZXRhIGh0dHAtZXF1aXY9IkNvbnRlbnQtVHlwZSIgY29udGVudD0i
dGV4dC9odG1sOyBjaGFyc2V0PXV0Zi04Ij4NCjwvaGVhZD4NCjxib2R5IGJnY29sb3I9IiNmZmZm
ZmYiPg0KPGRpdiBhbGlnbj0ibGVmdCI+PGZvbnQgc2l6ZT0iMiIgZmFjZT0iVmVyZGFuYSI+0J3Q
sNGIINC/0LDRgNGC0L3QtdGAINGD0YHRgtGA0LDQuNCy0LDQtdGCINGB0YDQtdC00Lgg0L/QvtC7
0YzQt9C+0LLQsNGC0LXQu9C10Lkg0L3QsNGI0LXQs9C+INGB0LXRgNCy0LjRgdCwINC60L7QvdC6
0YPRgNGBINC4INCy0LDRiCBlbWFpbA0KPGEgaHJlZj0ibWFpbHRvOnhvbWEuYW5kcmVAZ21haWwu
Y29tIj54b21hLmFuZHJlQGdtYWlsLmNvbTwvYT4mbmJzcDvRg9GH0LDRgdGC0LLRg9C10YI8L2Zv
bnQ+PC9kaXY+DQo8ZGl2IGFsaWduPSJsZWZ0Ij48Zm9udCBzaXplPSIyIiBmYWNlPSJWZXJkYW5h
Ij7Qn9C10YDQtdGF0L7QtNC4LCDRg9C30L3QsNCy0LDQuSDQuCDQt9Cw0LHQuNGA0LDQuSDRgdCy
0L7QuSDQv9C+0LTQsNGA0L7QuiAtDQo8L2ZvbnQ+PGZvbnQgc2l6ZT0iMiIgZmFjZT0iVmVyZGFu
YSI+PGEgaHJlZj0iaHR0cHM6Ly9nb29nbGUucnUvI2J0bkkmYW1wO3E9YVBWZFBSZGdoZ2prNzM4
OTMiPmh0dHBzOi8vZ29vZ2xlLnJ1LyNidG5JJmFtcDtxPWFQVmRQUmRnaGdqazczODkzPC9hPjwv
Zm9udD48L2Rpdj4NCjxkaXYgYWxpZ249ImxlZnQiPjxmb250IHNpemU9IjIiIGZhY2U9IkFyaWFs
Ij48L2ZvbnQ+PC9kaXY+DQpDT05GSURFTlRJQUwgTUFURVJJQUw6IFRoaXMgbWVzc2FnZSBpcyBp
bnRlbmRlZCBvbmx5IGZvciB0aGUgdXNlIG9mIHRoZSBpbmRpdmlkdWFsIG9yIGVudGl0eSB0byB3
aGljaCBpdCBpcyBhZGRyZXNzZWQgYW5kIG1heSBjb250YWluIGluZm9ybWF0aW9uIHRoYXQgaXMg
cHJpdmlsZWdlZCwgY29uZmlkZW50aWFsLCBhbmQgZXhlbXB0IGZyb20gZGlzY2xvc3VyZSB1bmRl
ciBhcHBsaWNhYmxlIGxhdy4gSWYgcmVjZWl2ZWQgaW4gZXJyb3IsIHBsZWFzZQ0KIG5vdGlmeSBz
ZW5kZXIgYnkgcmV0dXJuIGUtbWFpbCBhbmQgZGVzdHJveSBhbGwgY29waWVzIG9mIHRoZSBvcmln
aW5hbCB0cmFuc21pc3Npb24gYW5kIGFueSBhdHRhY2htZW50cy4gVGhhbmsgeW91LiBJZiB5b3Ug
d2lzaCB0byB2aWV3IGluZm9ybWF0aW9uIGFib3V0IEVwaHJhdGEgQXJlYSBTY2hvb2wgRGlzdHJp
Y3QsIHBsZWFzZSB2aXNpdCBvdXIgd2Vic2l0ZSBhdCB3d3cuZWFzZHBhLm9yZy4NCjwvYm9keT4N
CjwvaHRtbD4NCg==

--_000_886b229e3de3c9c12d289e32df4b615ba1cca7easdpaorg_--

"""
    cleaned_email = clean_email(s, redaction_values='dave')
    assert 'SSdtIHNvcnJ5IERhdmUsIEknbSBhZnJhaWQgSSBjYW4ndCBkbyB0aGF0' not in cleaned_email
    assert 'SSdtIHNvcnJ5IFJFREFDVEVELCBJJ20gYWZyYWlkIEkgY2FuJ3QgZG8gdGhhdA==' in cleaned_email


def test_redaction_not_touching_attachments():
    # try to redact a value that is in the base64 decoded attachment
    cleaned_email = clean_email(ATTACHMENT_EMAIL, redaction_values='foo')
    # make sure the encoded attachment is not changed
    assert 'Zm9vYmFyCg==' in cleaned_email
    assert 'This REDACTEDbar is a test' in cleaned_email

    # try to redact a value that is in the base64 encoded attachment
    cleaned_email = clean_email(ATTACHMENT_EMAIL, redaction_values='9vY')
    # make sure the encoded attachment is not changed
    assert 'Zm9vYmFyCg==' in cleaned_email


def test_ssn_redaction():
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>

123-45-6789

"""
    cleaned_email = clean_email(s, redaction_values='', redact_pii=True)
    assert '123-45-6789' not in cleaned_email


def test_base64_encoded_ssn_redaction():
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>
Content-Type: text/html;
    charset="utf-8"
Content-Transfer-Encoding: base64

MTIzLTQ1LTY3ODk=

"""
    cleaned_email = clean_email(s, redaction_values='', redact_pii=True)
    assert 'MTIzLTQ1LTY3ODk' not in cleaned_email
    assert 'UkVEQUNURUQ=' in cleaned_email

    # test an ssn in the middle of a string
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>
Content-Type: text/html;
    charset="utf-8"
Content-Transfer-Encoding: base64

dGhpcyBpcyBhIHRlc3QgMTIzLTQ1LTY3ODkgZm9vCg==

"""
    cleaned_email = clean_email(s, redaction_values='', redact_pii=True)
    assert 'dGhpcyBpcyBhIHRlc3QgMTIzLTQ1LTY3ODkgZm9vCg' not in cleaned_email
    assert 'UkVEQUNURUQ' in cleaned_email


def test_phone_number_redaction():
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>

1 (800) 123-4567 ext. 17

"""
    cleaned_email = clean_email(s, redaction_values='', redact_pii=True)
    assert '1 (800) 123-4567' not in cleaned_email


def test_base64_encoded_phone_number_redaction():
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>
Content-Type: text/html;
    charset="utf-8"
Content-Transfer-Encoding: base64

MSAoODAwKSAxMjMtNDU2Nw==

"""
    cleaned_email = clean_email(s, redaction_values='', redact_pii=True)
    assert 'MSAoODAwKSAxMjMtNDU2Nw==' not in cleaned_email
    assert 'UkVEQUNURUQ=' in cleaned_email

    # test a phone number in the middle of a string
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>
Content-Type: text/html;
    charset="utf-8"
Content-Transfer-Encoding: base64

dGhpcyBpcyBhIDEgKDgwMCkgMTIzLTQ1NjcgcGhvbmUgbnVtYmVyIHRlc3Q=

"""
    cleaned_email = clean_email(s, redaction_values='', redact_pii=True)
    assert 'dGhpcyBpcyBhIDEoODAwKTEyMy00NTY3IHBob25lIG51bWJlciB0ZXN0Cg' not in cleaned_email
    assert 'UkVEQUNURUQ' in cleaned_email


def test_phone_regex():
    """Make sure the phone number regex is not too broad. This was previously a problem."""
    s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>
Date: Wed, 08 May 2019 03:44:37 -0400
Content-Type: text/html;
    charset="utf-8"
Content-Transfer-Encoding: text/plain

foo

"""
    cleaned_email = clean_email(s, redaction_values='', redact_pii=True)
    assert 'Wed, 08 May 2019 03:44:37 -0400' in cleaned_email
