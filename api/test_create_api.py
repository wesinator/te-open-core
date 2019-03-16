#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.test import APITestCase

from test_resources import DefaultTestObject
from db.models import Email, Body, Host, IPAddress, EmailAddress, Url
from .api_test_utility import get_user_token

TestData = DefaultTestObject()


class EmailAPITests(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_basic_email_creation(self):
        email_text = TestData.email_text

        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})

        assert response.status_code == 201

        # make sure the API response is correct
        assert response.data['id'] == TestData.email_id

        # make sure the email was created in the db correctly
        emails = Email.objects.all()
        assert len(emails) == 1
        assert emails[0].id == TestData.email_id
        assert 'Alice Underwood' in emails[0].header._from
        assert 'alice@gmail.com' in emails[0].header._from

    def test_email_redaction(self):
        email_text = TestData.email_text

        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        emails = Email.objects.all()
        assert response.status_code == 201
        # make sure the to field is redacted
        assert 'bob@gmail.com' not in emails[0].header.to

    def test_email_without_redaction_1(self):
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1&redact=false', {'full_text': email_text})
        emails = Email.objects.all()
        assert response.status_code == 201
        # make sure the to field is not redacted
        assert 'bob@gmail.com' in emails[0].header.to

    def test_email_without_redaction_2(self):
        """Make sure an uppercase `False` is handled correctly."""
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1&redact=False', {'full_text': email_text})
        emails = Email.objects.all()
        assert response.status_code == 201
        # make sure the to field is not redacted
        assert 'bob@gmail.com' in emails[0].header.to

    def test_email_custom_redaction(self):
        email_text = TestData.email_text

        response = self.client.post(
            '/api/v1/emails/?test=1', {'full_text': email_text, 'redaction_values': ['github.com']}
        )

        assert response.status_code == 201

        # make sure the API response is correct
        assert response.data['id'] == TestData.email_id

        emails = Email.objects.all()
        assert len(emails) == 1
        assert emails[0].id == TestData.email_id
        assert 'github.com' not in emails[0].bodies.all()[0].full_text

    def test_email_creation_rate_limit(self):
        """Make sure it is possible to make multiple authenticated requests."""
        email_text = TestData.email_text

        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201

        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201

    def test_email_analysis_creation(self):
        new_email = TestData.create_email()
        notes = 'note1;note2'
        response = self.client.post(
            '/api/v1/emails/{}/analysis/'.format(new_email.id),
            {'notes': notes, 'score': 0, 'source': 'external', 'email': new_email.id},
        )
        assert response.status_code == 201
        assert new_email.analysis_set.all()[0].notes == notes
        assert new_email.analysis_set.all()[0].score == 0
        assert new_email.analysis_set.all()[0].source == 'external'
        assert new_email.analysis_set.all()[0].notes_strings == ['note1', 'note2']
        assert len(new_email.analysis_set.all()[0].notes_strings) == 2


class BadEmailTests(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_bad_empty_email_creation(self):
        response = self.client.post('/api/v1/emails/', {'full_text': ''})
        assert response.status_code == 400
        emails = Email.objects.all()
        assert len(emails) == 0

    def test_bad_email_creation_a(self):
        response = self.client.post('/api/v1/emails/', {})
        assert response.status_code == 400
        emails = Email.objects.all()
        assert len(emails) == 0

    def test_bad_email_creation_b(self):
        response = self.client.post('/api/v1/emails/', {'text': 'bingo'})
        assert response.status_code == 400
        emails = Email.objects.all()
        assert len(emails) == 0


class UnauthenticatedEmailAPITests(APITestCase):
    """Test the rate limit on the API for unauthenticated requests."""

    def test_email_creation_rate_limit(self):
        email_text = TestData.email_text

        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201

        # make sure there is a rate limit error
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201


class NetworkDataAPITest(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_basic_domain_creation(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post(
            '/api/v1/domains/?test=1', {'host_name': TestData.domain_name, 'bodies': [body_id], 'headers': []}
        )
        assert response.status_code == 201

        # make sure the email was created in the db correctly
        hosts = Host.objects.all()
        assert len(hosts) == 1
        assert hosts[0].host_name == TestData.domain_name
        assert hosts[0].bodies.all()[0].id == body_id
        assert hosts[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

    def test_basic_ip_address_creation(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post(
            '/api/v1/ipAddresses/?test=1', {'ip_address': TestData.ip_address, 'bodies': [body_id], 'headers': []}
        )
        assert response.status_code == 201

        # make sure the email was created in the db correctly
        ip_addresses = IPAddress.objects.all()
        assert len(ip_addresses) == 1
        assert ip_addresses[0].ip_address == TestData.ip_address
        assert ip_addresses[0].bodies.all()[0].id == body_id
        assert ip_addresses[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

    def test_basic_email_address_creation(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post(
            '/api/v1/emailAddresses/?test=1',
            {'email_address': TestData.email_address, 'bodies': [body_id], 'headers': []},
        )
        assert response.status_code == 201

        # make sure the email was created in the db correctly
        email_addresses = EmailAddress.objects.all()
        assert len(email_addresses) == 1
        assert email_addresses[0].email_address == TestData.email_address
        assert email_addresses[0].bodies.all()[0].id == body_id
        assert email_addresses[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

    def test_basic_url_creation(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post('/api/v1/urls/?test=1', {'url': TestData.url, 'bodies': [body_id], 'headers': []})
        assert response.status_code == 201

        # make sure the email was created in the db correctly
        urls = Url.objects.all()
        assert len(urls) == 1
        assert urls[0].url == TestData.url
        assert urls[0].bodies.all()[0].id == body_id
        assert urls[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

    def test_complex_url_with_fragment_creation(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        url = 'https://bit.ly/1234#1234'
        response = self.client.post('/api/v1/urls/?test=1', {'url': url, 'bodies': [body_id], 'headers': []})
        assert response.status_code == 201

        # make sure the email was created in the db correctly
        urls = Url.objects.all()
        assert len(urls) == 1
        assert urls[0].url == url
        assert urls[0].bodies.all()[0].id == body_id
        assert urls[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]
