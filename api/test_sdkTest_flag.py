#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Make sure requests with the ?sdkTest query string are handled properly."""

from rest_framework.test import APITestCase

from test_resources import DefaultTestObject
from db.models import Email
from .api_test_utility import get_user_token

TestData = DefaultTestObject()


class EmailSDKTestFlagTests(APITestCase):
    def setUp(self):
        self.token = get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_basic_email_creation(self):
        email_text = TestData.email_text

        response = self.client.post('/api/v1/emails/?sdkTest=1', {'full_text': email_text})

        assert response.status_code == 201
        assert response.data['result'] == 'Email passed serializer validation.'

        # make sure no email was created
        emails = Email.objects.all()
        assert len(emails) == 0
