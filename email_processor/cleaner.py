#!/usr/bin/env python
# -*- coding: utf-8 -*-

import email
import re

from .parse_headers import parse_header
from utility import utility


def clean_email(email_text, redaction_values=None):
    """Clean an email."""
    to_fields = []
    cleaned_email = email_text
    # I am not logging missing properties this time through (because this will be done when importing the email officially)
    header_fields = parse_header(email.message_from_string(cleaned_email), log_mising_properties=False)
    for field in header_fields:
        if field.lower() == 'to':
            to_fields.append(header_fields[field])
        elif field.lower() == 'delivered_to':
            to_fields.append([{'name': None, 'email': header_fields[field]}])

    if to_fields:
        for field in to_fields:
            for recipient in field:
                cleaned_email = re.sub(re.escape(recipient['email']), 'REDACTED', cleaned_email, flags=re.IGNORECASE)
                if recipient['name']:
                    cleaned_email = re.sub(re.escape(recipient['name']), 'REDACTED', cleaned_email, flags=re.IGNORECASE)
    else:
        message = "No 'To' field found in the email text below. It may have been redacted or this may be an error in the cleaning function. {}.".format(
            email_text
        )
        utility.create_alerta_alert('Missing "to" field', 'warning', message)

    if redaction_values:
        for value in redaction_values.split(','):
            cleaned_email = re.sub(re.escape(value), 'REDACTED', cleaned_email, flags=re.IGNORECASE)

    return cleaned_email
