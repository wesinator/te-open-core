#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse header fields from an email."""

from utility import utility


def parse_header(email_text):
    """Parser email headers."""
    email_object = utility.email_read(email_text)
    return email_object.items()
