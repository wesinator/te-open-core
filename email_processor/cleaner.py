#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from .parse_headers import parse_header
from utility import utility


def clean_email(email_text, redaction_values=None):
    """Clean an email."""
    FIELDS_TO_REDACT = ['to', 'delivered-to']
    values_to_redact = []
    cleaned_email = email_text

    email_header_json = parse_header(email_text)

    for header_key, header_value in email_header_json:
        if header_key.lower() in FIELDS_TO_REDACT:
            values_to_redact.append(header_value)

    for value in values_to_redact:
        if ',' in value:
            values = value.split(',')
        else:
            values = [value]

        for value in values:
            value = value.strip()
            parsed_email_address = utility.parse_email_address(value)

            if parsed_email_address.display_name:
                cleaned_email = re.sub(
                    re.escape(parsed_email_address.display_name), 'REDACTED', cleaned_email, flags=re.IGNORECASE
                )

            if parsed_email_address.username and parsed_email_address.domain:
                email_address = '{}@{}'.format(parsed_email_address.username, parsed_email_address.domain)
                cleaned_email = re.sub(re.escape(email_address), 'REDACTED', cleaned_email, flags=re.IGNORECASE)

    if redaction_values:
        for value in redaction_values.split(','):
            value = value.strip()
            cleaned_email = re.sub(re.escape(value), 'REDACTED', cleaned_email, flags=re.IGNORECASE)

    return cleaned_email
