#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""These are functions to test cleaner.py. The only test the functionality of the algorithm and DO NOT test the views related to the cleaner. Those are located in the test file with the other view tests (at the time of writing that is the `test_views.py` file, but that may change)."""

from .cleaner import clean_email
from test_resources import DefaultTestObject

TestData = DefaultTestObject()


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
    assert 'Content-Transfer-Encoding' in TestData.email_text
    assert 'Yours truly' in TestData.email_text
    assert '//github.com' in TestData.email_text
    assert 'Bob' in TestData.email_text
    cleaned_email = clean_email(TestData.email_text, 'Yours truly,Content-Transfer-Encoding,//github.com,Bob')
    assert 'Content-Transfer-Encoding' not in cleaned_email
    assert 'Yours truly' not in cleaned_email
    assert '//github.com' not in cleaned_email
    assert 'Bob' not in cleaned_email


def test_cleaner_input_stripping():
    assert 'Content-Transfer-Encoding' in TestData.email_text
    assert 'Yours truly' in TestData.email_text
    assert '//github.com' in TestData.email_text
    assert 'Bob' in TestData.email_text
    cleaned_email = clean_email(TestData.email_text, 'Yours truly, Content-Transfer-Encoding, //github.com, Bob')
    assert 'Content-Transfer-Encoding' not in cleaned_email
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
