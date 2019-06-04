#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html
import os

from django.test import TestCase

from db.models import Email
from test_resources import DefaultTestObject
from utility import utility

TestData = DefaultTestObject()


def ensure_payload_displayed(payloads, response):
    """Assert payload contents are shown."""
    for payload in payloads:
        if not payload.is_multipart():
            str_payload = html.escape(str(payload).replace("\n", "\\n"))
            assert str_payload in str(response.content)


class ViewTests(TestCase):
    """View related tests."""

    def test_index_view(self):
        """Test the index view."""
        response = self.client.get('/email/')
        assert response.status_code == 302
        self.assertEqual(response.url, "/")

    def test_import_view(self):
        response = self.client.get('/')
        assert (
            '<input class="hollow large button success" id="submitButton" type="submit" value="Analyze email" onclick="disable()">'
            in str(response.content)
        )

    def test_save_view(self):
        response = self.client.post('/save/', {'full_text': TestData.email_text})
        # ensure email created and system redirects to new email
        self.assertEqual(response.url, "/email/{}".format(TestData.email_id))

    def test_save_view_with_data_redaction(self):
        original_sha256 = utility.sha256(TestData.email_text.replace('\n', '\r\n'))
        response = self.client.post('/save/', {'full_text': TestData.email_text, 'redact_recipient_data': True})
        # ensure email created and system redirects to new email
        self.assertEqual(response.url, "/email/{}".format(TestData.email_id))
        # make sure the original_sha256 is correct
        email_object = Email.objects.get(id=TestData.email_id)
        # assert email_object.cleaned_id == original_sha256
        assert email_object.id != email_object.cleaned_id
        assert original_sha256 == email_object.id

    def test_save_with_multiple_custom_redaction_values(self):
        original_sha256 = utility.sha256(TestData.email_text.replace('\n', '\r\n'))
        response = self.client.post('/save/', {'full_text': TestData.email_text, 'redact_recipient_data': True, 'redaction_values': 'github.com,master'})
        # ensure email created and system redirects to new email
        self.assertEqual(response.url, "/email/{}".format(TestData.email_id))
        # make sure the original_sha256 is correct
        email_object = Email.objects.get(id=TestData.email_id)
        # assert email_object.cleaned_id == original_sha256
        assert email_object.id != email_object.cleaned_id
        assert original_sha256 == email_object.id
        assert 'github.com' not in email_object.full_text
        assert 'master' not in email_object.full_text

    def test_save_with_single_custom_redaction_value(self):
        original_sha256 = utility.sha256(TestData.email_text.replace('\n', '\r\n'))
        response = self.client.post('/save/', {'full_text': TestData.email_text, 'redact_recipient_data': True, 'redaction_values': 'master'})
        # ensure email created and system redirects to new email
        self.assertEqual(response.url, "/email/{}".format(TestData.email_id))
        # make sure the original_sha256 is correct
        email_object = Email.objects.get(id=TestData.email_id)
        # assert email_object.cleaned_id == original_sha256
        assert email_object.id != email_object.cleaned_id
        assert original_sha256 == email_object.id
        assert 'master' not in email_object.full_text

    def test_save_view_with_pii_redaction(self):
        s = """Subject: =?UTF-8?B?aGkgYWxpY2UgYXNpbW92?=
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>

123-45-6789

"""
        response = self.client.post('/save/', {'full_text': s, 'redact_recipient_data': True, 'redact_pii': True})
        assert response.status_code == 302
        assert '123-45-6789' not in Email.objects.all()[0].full_text
        assert Email.objects.all()[0].full_text == """Subject: =?UTF-8?B?aGkgUkVEQUNURUQ=?=
From: Bob Bradbury <bob@gmail.com>
To: REDACTED <REDACTED>

REDACTED

""".replace('\n', '\r\n')

    def test_save_view_with_duplicate_uploads(self):
        """Try saving an email without redaction and then saving it with redaction."""
        self.client.post('/save/', {'full_text': TestData.email_text})
        self.client.post('/save/', {'full_text': TestData.email_text, 'redact_recipient_data': True})
        # if the two requests ^^ above don't cause this test to fail, that is good enough

    def test_save_view_with_multiple_file_upload(self):
        """Try to save multiple emails at once."""
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_resources/emails/test.eml'))) as f1:
            with open(
                os.path.abspath(
                    os.path.join(os.path.dirname(__file__), '../test_resources/emails/single_attachment_test.eml')
                )
            ) as f2:
                response = self.client.post('/save/', {'email_file': [f1, f2], 'redact_recipient_data': True})

        # ensure email created and system redirects to new email
        self.assertEqual(
            response.url,
            "/email/{}".format(utility.sha256(TestData.single_attachment_email_text.replace('\n', '\r\n'))),
        )

        assert len(Email.objects.all()) == 2

        # make sure both emails were created
        assert Email.objects.get(id=utility.sha256(TestData.email_text.replace('\n', '\r\n')))
        assert Email.objects.get(id=utility.sha256(TestData.single_attachment_email_text.replace('\n', '\r\n')))

    def test_empty_save_without_following_redirect(self):
        response = self.client.post('/save/', {})
        assert response.status_code == 302
        self.assertEqual(response.url, "/")

    def test_empty_save_following_redirect(self):
        response = self.client.post('/save/', {}, follow=True)
        assert 'Please upload an email or paste the text of an email to analyze it' in response.content.decode("utf-8")
