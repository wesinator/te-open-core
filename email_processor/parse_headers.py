#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse header fields from an email."""

from utility import utility


def parse_header(email_text):
    """Parser email headers."""
    try:
        email_object = utility.email_read(email_text)
        return email_object.items()
    # an index error sometimes occurs when python's default email policy (https://docs.python.org/3/library/email.policy.html#email.policy.default) does not read the email properly
    except IndexError:
        email_object = utility.email_read(email_text, policy='')
        return email_object.items()
