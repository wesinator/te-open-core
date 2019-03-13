#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from rest_framework.authtoken.models import Token

from accounts.models import User


@pytest.mark.django_db
def get_user_token():
    user = User(username='bob', email='bob@example.com', password='abc123')
    user.save()
    # user.add_group('free')
    token = Token.objects.get(user=user)
    return token.key
