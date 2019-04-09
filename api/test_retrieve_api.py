#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework.test import APITestCase

from test_resources import DefaultTestObject
from .api_test_utility import get_user_token

TestData = DefaultTestObject()


class EmailAPITests(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_emails_list_a(self):
        new_email = TestData.create_email()
        response = self.client.get('/api/v1/emails/')
        print(response.data)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == new_email.id
        assert "full_text" in response.data[0].keys()
        assert response.data[0]['id'] == new_email.id

    def test_emails_list_b(self):
        new_objects = TestData.create_emails_with_same_header(count=6)
        response = self.client.get('/api/v1/emails/')
        assert response.status_code == 200
        assert len(response.data) == 6
        email_ids = [email['id'] for email in response.data]

        for new_object in new_objects:
            assert new_object.id in email_ids

    def test_specific_email(self):
        new_email = TestData.create_email()
        response = self.client.get('/api/v1/emails/{}/'.format(new_email.id))
        assert response.status_code == 200
        assert len(response.data) == 3
        assert "full_text" in response.data.keys()
        assert "id" in response.data.keys()
        assert "tlsh_hash" in response.data.keys()

    def test_related_header(self):
        new_email = TestData.create_email()
        response = self.client.get('/api/v1/emails/{}/header/'.format(new_email.id))
        print("response {}".format(response.data))
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == new_email.header.id

    def test_related_bodies(self):
        new_email = TestData.create_email()
        response = self.client.get('/api/v1/emails/{}/bodies/'.format(new_email.id))
        print("response {}".format(response.data))
        assert response.status_code == 200
        assert len(response.data) == len(new_email.bodies.all())

        id_list = [body.id for body in new_email.bodies.all()]
        full_text_list = [body.full_text for body in new_email.bodies.all()]

        for count, body in enumerate(response.data):
            assert body.get('id') in id_list
            assert body.get('full_text') in full_text_list

    def test_related_attachments(self):
        new_email = TestData.create_email()
        response = self.client.get('/api/v1/emails/{}/attachments/'.format(new_email.id))
        assert response.status_code == 200
        assert len(response.data) == len(new_email.attachments.all())

        id_list = [attachment.id for attachment in new_email.attachments.all()]
        full_text_list = [attachment.full_text for attachment in new_email.attachments.all()]

        for count, attachment in enumerate(response.data):
            assert attachment.get('id') in id_list
            assert attachment.get('full_text') in full_text_list
            assert attachment['content_type']
            assert attachment['filename']
            assert attachment['md5']
            assert attachment['sha1']


class EmailInvalidCalls(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_invalid_email_details(self):
        """Make a call to the email details branch with an email id that does not exist."""
        response = self.client.get('/api/v1/emails/{}/'.format('a' * 64))
        assert response.status_code == 404
        assert len(response.data) == 1
        assert response.data['detail'] == 'Not found.'


class UnauthenticatedRequests(APITestCase):
    """Make sure unauthenticated requests are handled properly."""

    def test_unauthenticated_request(self):
        TestData.create_email()
        response = self.client.get('/api/v1/emails/')
        assert response.status_code == 401


class HeaderAPITests(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    # NOT IMPLEMENTED YET - Jan 2019
    # def test_headers_list(self):
    #     new_email = TestData.create_email()
    #     response = self.client.get('/api/v1/headers/')
    #     assert response.status_code == 200
    #     assert len(response.data) == 10

    #     for count, header_field in enumerate(response.data):
    #         assert header_field.get('id') == new_email.header.id
    #         assert header_field.get('full_text') == new_email.header.full_text

    def test_specific_header(self):
        new_header = TestData.create_email().header
        response = self.client.get('/api/v1/headers/{}/'.format(new_header.id))
        assert response.status_code == 200
        assert len(response.data) == 2
        print("response {}".format(response.data))
        assert response.data['id'] == new_header.id

    def test_related_email(self):
        new_email = TestData.create_email()
        response = self.client.get('/api/v1/headers/{}/emails/'.format(new_email.header.id))
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['id'] == new_email.id

    # def test_related_indicators(self):
    #     new_header = TestData.create_email().header
    #     response = self.client.get('/api/v1/headers/{}/indicators'.format(new_header.id))
    #     assert response.status_code == 200


class BodyAPITests(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    # NOT IMPLEMENTED YET - Jan 2019
    # def test_bodies_list(self):
    #     TestData.create_email()
    #     response = self.client.get('/api/v1/bodies/')
    #     assert response.status_code == 200
    #     assert len(response.data) == 10

    def test_specific_body(self):
        new_body = TestData.create_email().bodies.all()[0]
        response = self.client.get('/api/v1/bodies/{}/'.format(new_body.id))
        assert response.status_code == 200
        assert len(response.data) == 2
        print("response {}".format(response.data))
        assert response.data['id'] == new_body.id
        assert response.data['full_text'] == new_body.full_text

    def test_related_email(self):
        new_email = TestData.create_email()
        response = self.client.get('/api/v1/bodies/{}/emails/'.format(new_email.bodies.all()[0].id))
        assert response.status_code == 200
        assert len(response.data) == 1

        for count, email_field in enumerate(response.data):
            assert email_field.get('id') == new_email.id
            assert email_field.get('full_text') == new_email.full_text


class AttachmentAPITest(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    # NOT IMPLEMENTED YET - Jan 2019
    # def test_attachments_list(self):
    #     TestData.create_email()
    #     response = self.client.get('/api/v1/attachments/')
    #     assert response.status_code == 200
    #     assert len(response.data) == 10

    def test_specific_attachment(self):
        new_attachment = TestData.create_email(TestData.attachment_email_text).attachments.all()[0]
        response = self.client.get('/api/v1/attachments/{}/'.format(new_attachment.id))
        assert response.status_code == 200
        assert len(response.data) == 7
        print("response {}".format(response.data))
        assert response.data['id'] == new_attachment.id
        assert response.data['full_text'] == new_attachment.full_text
        assert response.data['content_type'] == new_attachment.content_type
        assert response.data['filename'] == new_attachment.filename
        assert response.data['sha256'] == new_attachment.sha256
        assert response.data['sha1'] == new_attachment.sha1
        assert response.data['md5'] == new_attachment.md5

    def test_related_email(self):
        new_email = TestData.create_email(TestData.attachment_email_text)
        response = self.client.get('/api/v1/attachments/{}/emails/'.format(new_email.attachments.all()[0].id))
        assert response.status_code == 200
        assert len(response.data) == 1

        for count, email_field in enumerate(response.data):
            assert email_field.get('id') == new_email.id
            assert email_field.get('full_text') == new_email.full_text
