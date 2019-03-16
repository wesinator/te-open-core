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

    def test_email_hash_update(self):
        new_email = TestData.create_email()
        assert new_email.tlsh_hash == None
        response = self.client.put(
            '/api/v1/emails/{}/'.format(new_email.id),
            {'tlsh_hash': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'},
        )
        assert response.status_code == 200
        new_email = Email.objects.get(pk=new_email.id)
        assert new_email.tlsh_hash == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

    def test_email_hash_multi_update(self):
        new_email = TestData.create_email()
        assert new_email.tlsh_hash == None
        response = self.client.put(
            '/api/v1/emails/{}/'.format(new_email.id),
            {'tlsh_hash': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'},
        )
        assert response.status_code == 200
        new_email = Email.objects.get(pk=new_email.id)
        assert new_email.tlsh_hash == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

        new_email = TestData.create_email()
        response = self.client.put(
            '/api/v1/emails/{}/'.format(new_email.id),
            {'tlsh_hash': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'},
        )
        assert response.status_code == 200
        new_email = Email.objects.get(pk=new_email.id)
        assert new_email.tlsh_hash == 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'

    def test_update_domain(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post(
            '/api/v1/domains/?test=1', {'host_name': TestData.domain_name, 'bodies': [], 'headers': []}
        )
        assert response.status_code == 201

        # try to update the data
        response = self.client.post(
            '/api/v1/domains/?test=1', {'host_name': TestData.domain_name, 'bodies': [body_id], 'headers': []}
        )
        assert response.status_code == 200

        # make sure the email was created in the db correctly
        hosts = Host.objects.all()
        assert len(hosts) == 1
        assert hosts[0].host_name == TestData.domain_name
        assert hosts[0].bodies.all()[0].id == body_id
        assert hosts[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

    def test_multi_update_domain(self):
        # create an email
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': TestData.email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post(
            '/api/v1/domains/?test=1', {'host_name': TestData.domain_name, 'bodies': [], 'headers': []}
        )
        assert response.status_code == 201

        # try to update the data
        response = self.client.post(
            '/api/v1/domains/?test=1', {'host_name': TestData.domain_name, 'bodies': [body_id], 'headers': []}
        )
        assert response.status_code == 200

        # make sure the email was created in the db correctly
        hosts = Host.objects.all()
        assert len(hosts) == 1
        assert hosts[0].host_name == TestData.domain_name
        assert hosts[0].bodies.all()[0].id == body_id
        assert hosts[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

        # create another email
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': TestData.attachment_email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[1].bodies.all()[0].id

        response = self.client.post(
            '/api/v1/domains/?test=1', {'host_name': TestData.domain_name, 'bodies': [body_id], 'headers': []}
        )
        assert response.status_code == 200

        # make sure the email was created in the db correctly
        hosts = Host.objects.all()
        assert len(hosts) == 1
        assert hosts[0].host_name == TestData.domain_name
        assert len(hosts[0].bodies.all()) == 2

    def test_update_email_address(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post(
            '/api/v1/emailAddresses/?test=1', {'email_address': TestData.email_address, 'bodies': [], 'headers': []}
        )
        assert response.status_code == 201

        # try to update the data
        response = self.client.post(
            '/api/v1/emailAddresses/?test=1',
            {'email_address': TestData.email_address, 'bodies': [body_id], 'headers': []},
        )
        assert response.status_code == 200

        # make sure the email was created in the db correctly
        email_addresses = EmailAddress.objects.all()
        assert len(email_addresses) == 1
        assert email_addresses[0].email_address == TestData.email_address
        assert email_addresses[0].bodies.all()[0].id == body_id
        assert email_addresses[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

    def test_update_ip_address(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post(
            '/api/v1/ipAddresses/?test=1', {'ip_address': TestData.ip_address, 'bodies': [], 'headers': []}
        )
        assert response.status_code == 201

        # try to update the data
        response = self.client.post(
            '/api/v1/ipAddresses/?test=1', {'ip_address': TestData.ip_address, 'bodies': [body_id], 'headers': []}
        )
        assert response.status_code == 200

        # make sure the email was created in the db correctly
        ip_addresses = IPAddress.objects.all()
        assert len(ip_addresses) == 1
        assert ip_addresses[0].ip_address == TestData.ip_address
        assert ip_addresses[0].bodies.all()[0].id == body_id
        assert ip_addresses[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

    def test_update_url(self):
        # create an email
        email_text = TestData.email_text
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post('/api/v1/urls/?test=1', {'url': TestData.url, 'bodies': [], 'headers': []})
        assert response.status_code == 201

        # try to update the data
        response = self.client.post('/api/v1/urls/?test=1', {'url': TestData.url, 'bodies': [body_id], 'headers': []})
        assert response.status_code == 200

        # make sure the email was created in the db correctly
        urls = Url.objects.all()
        assert len(urls) == 1
        assert urls[0].url == TestData.url
        assert urls[0].bodies.all()[0].id == body_id
        assert urls[0].bodies.all()[0].id in [body.id for body in Body.objects.all()]

    def test_multi_update_url(self):
        # create an email
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': TestData.email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[0].bodies.all()[0].id

        response = self.client.post('/api/v1/urls/?test=1', {'url': TestData.url, 'bodies': [], 'headers': []})
        assert response.status_code == 201

        # try to update the data
        response = self.client.post('/api/v1/urls/?test=1', {'url': TestData.url, 'bodies': [body_id], 'headers': []})
        assert response.status_code == 200

        # create another email
        response = self.client.post('/api/v1/emails/?test=1', {'full_text': TestData.attachment_email_text})
        assert response.status_code == 201
        # get the id of the body of the email we just created
        body_id = Email.objects.all()[1].bodies.all()[0].id

        response = self.client.post('/api/v1/urls/?test=1', {'url': TestData.url, 'bodies': [body_id], 'headers': []})
        assert response.status_code == 200

        # make sure the email was created in the db correctly
        urls = Url.objects.all()
        assert len(urls) == 1
        assert urls[0].url == TestData.url
        assert len(urls[0].bodies.all()) == 2
