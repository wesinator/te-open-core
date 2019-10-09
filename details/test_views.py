#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html

from django.test import TestCase

from test_resources import DefaultTestObject

TestData = DefaultTestObject()


def ensure_payload_displayed(payloads, response):
    """Assert payload contents are shown."""
    for payload in payloads:
        if not payload.is_multipart():
            str_payload = html.escape(payload.get_payload().strip().replace('\n', '\\n'))
            print('str_payload {}'.format(str_payload))
            print('str(response.content) {}'.format(str(response.content)))
            assert str_payload in str(response.content)


class ViewTests(TestCase):
    """View related tests."""

    def test_email_details_view(self):
        created_content = TestData.create_email()
        response = self.client.get("/email/{}/".format(created_content.id))
        response_content = response.content.decode("utf-8")

        assert html.escape(created_content.header.get_value('Subject')) in response_content
        assert html.escape(created_content.header.get_value('To')) in response_content
        assert html.escape(created_content.header.get_value('From')) in response_content
        assert 'First submitted:' in response_content
        assert 'Most recently submitted:' in response_content
        assert 'minutes ago.' in response_content

        assert html.escape(str(created_content.header)) in response.content.decode("utf-8")

        ensure_payload_displayed(TestData.email_message.get_payload(), response)
        # TODO: add more tests to the test_email_details_view function (3)

    def test_generic_domain_display(self):
        created_email = TestData.create_email()

        new_domain = TestData.create_host('gmail.com')
        new_domain.bodies.add(created_email.bodies.all()[0])
        new_domain.save()

        # make sure the generic domain is displayed properly
        response = self.client.get("/email/{}/".format(created_email.id))
        response_content = response.content.decode("utf-8")
        assert 'a generic domain and no overlaps will be shown' in response_content

    def test_generic_ip_address_display(self):
        created_email = TestData.create_email()

        new_ip_address = TestData.create_ip_address('127.0.0.1')
        new_ip_address.bodies.add(created_email.bodies.all()[0])
        new_ip_address.save()

        # make sure the generic ip address is displayed properly
        response = self.client.get("/email/{}/".format(created_email.id))
        response_content = response.content.decode("utf-8")
        assert 'a generic IP address and no overlaps will be shown' in response_content

    def test_email_details_view_with_attachments(self):
        created_content = TestData.create_email(TestData.attachment_email_text)
        response = self.client.get("/email/{}/".format(created_content.id))
        response_content = response.content.decode("utf-8")
        print('response_content {}'.format(response_content))

        # assert header contents are shown
        assert html.escape(created_content.header.get_value('Subject')) in response_content
        assert html.escape(created_content.header.get_value('To')) in response_content
        assert html.escape(created_content.header.get_value('From')) in response_content

        ensure_payload_displayed(TestData.attachment_email_message.get_payload(), response)

    def test_display_of_to_field_without_name(self):
        """Make sure an email where the `To` field does not have a name is displayed correctly."""
        s = """Delivered-To: bob@gmail.com
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

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml">"""
        response = self.client.post('/save/', {'full_text': s, 'redact_data': True})

        response = self.client.get(response.url)
        # ensure email created and system redirects to new email
        empty_redaction = """                    : """
        assert empty_redaction not in str(response.content)

    def test_x_spam_prev_subject_display(self):
        """Make sure emails with the "X-Spam-Prev-Subject" header are displayed properly - namely that the value in the "X-Spam-Prev-Subject" field is shown rather than the subject."""
        s = """Delivered-To: REDACTED
From: MICHAEL WANG <wangmi102@yandex.com>
Subject: [*SPAM*] hi
Date: Sat, 15 Dec 2018 14:14:13 -0800
MIME-Version: 1.0
Content-Type: text/plain; charset="Windows-1251"
Content-Transfer-Encoding: 7bit
X-Priority: 3
X-MSMail-Priority: Normal
X-Mailer: Microsoft Outlook Express 6.00.2600.0000
X-MimeOLE: Produced By Microsoft MimeOLE V6.00.2600.0000
X-Spam-Prev-Subject: hi
Message-Id: <20181215220658.71636A06FE@mail.cbkipa.net>
To: REDACTED

Good morning to you,
"""
        response = self.client.post('/save/', {'full_text': s, 'redact_data': True})
        response = self.client.get(response.url)
        assert '<h2>hi</h2>' in str(response.content)

    def test_redirect_to_lowercase_url(self):
        """Make sure requests with an uppercased email ID are redirected to the lowercased version of the url."""
        created_email = TestData.create_email()

        response = self.client.get("/email/{}/".format(created_email.id))
        assert response.status_code == 200

        response = self.client.get("/email/{}/".format(created_email.id.upper()))
        assert response.status_code == 302
        assert response.url == '/email/{}/'.format(created_email.id)


class StructureTest(TestCase):
    """Make sure email structures are properly displayed."""

    def test_email_html_structure(self):
        created_content = TestData.create_email()
        response = self.client.get("/email/{}/".format(created_content.id))
        assert response.status_code == 200

        response_content = response.content.decode("utf-8")
        print('response_content {}'.format(response_content))
        assert (
            "multipart/alternative<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#ea2bf05889ac5cf478293492da99b6e62c629f78cc1ef6a1248aea5ff6b0e226'>text/plain (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#6ce1e03b3902eee8dae69a56364413bdc9bb46d16743590ac42513217c5f430c'>text/html (body)</a>"
            in response_content
        )

    def test_email_html_structure_with_attachments(self):
        created_content = TestData.create_email(TestData.attachment_email_text)
        response = self.client.get("/email/{}/".format(created_content.id))
        assert response.status_code == 200

        response_content = response.content.decode("utf-8")
        print('response_content {}'.format(response_content))
        assert (
            "multipart/mixed<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;multipart/alternative<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#c6a1427d7119cd3c049d4fe08cc02f1058d15291fba68a994816ea209af73f0e'>text/plain (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#b64473d833f7568f15e1d86c02af3c237e652fb53c62087b74103c612f4e1dc3'>text/html (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#e5d91ce2991b8f8720cbf499deb19c16b04bc61a3aada3a1011b41ecbee6104e'>text/xml (attachment)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#efc6d065a38f0e3d99391e0bb992ba30f4ddf612fbbb492c3bcdf387039e3f1e'>image/png (attachment)</a>"
            in response_content
        )

    def test_outlook_html_structure(self):
        created_content = TestData.create_email(TestData.outlook_email_text)
        response = self.client.get("/email/{}/".format(created_content.id))
        assert response.status_code == 200

        response_content = response.content.decode("utf-8")
        print('response_content {}'.format(response_content))
        assert (
            "multipart/alternative<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#54712d1572ff09d73c3baacf0760a42735a3ce6dbd83144eb2f998155f53b740'>text/plain (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#b6fba92f1803f9f59d42fdd36b259fe8a550a68fee60808800cb11de14feeb8c'>text/html (body)</a>"
            in response_content
        )
