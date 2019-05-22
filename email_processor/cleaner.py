#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from .parse_headers import parse_header
from utility import utility

# TODO: make this code beautiful (1)


def _clean_pii(text):
    """."""
    ssn_pattern = '(\d{3}-\d{2}-\d{4})'
    cleaned_text = re.sub(ssn_pattern, 'REDACTED', text, flags=re.IGNORECASE)

    phone_number_pattern = '(?:\(?[0-9]{3}\)?)?([ -]?|^)[0-9]{3}[ -][0-9]{4}'
    cleaned_text = re.sub(phone_number_pattern, 'REDACTED', cleaned_text, flags=re.IGNORECASE)

    return cleaned_text


def clean_email(email_text, redaction_values=None, redact_pii=False):
    """Clean an email."""
    FIELDS_TO_REDACT = ['to', 'delivered-to']
    cleaned_email = email_text
    redaction_value_list = []
    if redaction_values:
        redaction_value_list = [value.strip() for value in redaction_values.split(',')]

    # replace certain headers in the email
    email_header_json = parse_header(email_text)
    for header_key, header_value in email_header_json:
        # if the header is one that we are going to redact, redact appropriately
        if header_key.lower() in FIELDS_TO_REDACT:
            if ',' in header_value:
                values = header_value.split(',')
            else:
                values = [header_value]

            for value in values:
                value = value.strip()
                parsed_email_address = utility.parse_email_address(value)

                if parsed_email_address.display_name:
                    cleaned_email = re.sub(
                        re.escape(parsed_email_address.display_name), 'REDACTED', cleaned_email, flags=re.IGNORECASE
                    )
                    redaction_value_list.append(parsed_email_address.display_name)

                if parsed_email_address.username and parsed_email_address.domain:
                    email_address = '{}@{}'.format(parsed_email_address.username, parsed_email_address.domain)
                    cleaned_email = re.sub(re.escape(email_address), 'REDACTED', cleaned_email, flags=re.IGNORECASE)
                    redaction_value_list.append(email_address)

    # redact the headers
    for header in email_header_json:
        original_header_content = ': '.join(header)
        cleaned_header = original_header_content
        for redaction_value in redaction_value_list:
            if redaction_value.lower() in cleaned_header.lower():
                cleaned_header = re.sub(re.escape(redaction_value), 'REDACTED', cleaned_header, flags=re.IGNORECASE)
        if redact_pii:
            cleaned_header = _clean_pii(cleaned_header)
        cleaned_email = re.sub(re.escape(original_header_content), cleaned_header, cleaned_email, flags=re.IGNORECASE)

    # find all base64 encoded header values
    base64_encoded_header_pattern = '=\?[a-zA-Z0-9\-]+\?B\?([a-zA-Z0-9+\/=]+)\?='
    for base64_content in re.findall(base64_encoded_header_pattern, email_text):
        # decode the content
        decoded_content = utility.base64_decode(base64_content)
        cleaned_content = decoded_content

        for redaction_value in redaction_value_list:
            if redaction_value.lower() in decoded_content.lower():
                cleaned_content = re.sub(re.escape(redaction_value), 'REDACTED', decoded_content, flags=re.IGNORECASE)

        if redact_pii:
            cleaned_content = _clean_pii(cleaned_content)

        # encode the content and replace it in the email
        encoded_content = utility.base64_encode(cleaned_content)
        cleaned_email = re.sub(re.escape(base64_content), encoded_content, cleaned_email, flags=re.IGNORECASE)

    # redact the bodies
    email_object = utility.email_read(cleaned_email)
    bodies = utility.email_bodies(email_object)
    for body in bodies:
        body_content = body.get_payload()
        if email_object['Content-Transfer-Encoding'] and email_object['Content-Transfer-Encoding'].lower() == 'base64':
            # decode the body
            decoded_body = utility.base64_decode(body_content)
            cleaned_body = decoded_body

            # redact
            for redaction_value in redaction_value_list:
                if redaction_value.lower() in decoded_body.lower():
                    cleaned_body = re.sub(re.escape(redaction_value), 'REDACTED', decoded_body, flags=re.IGNORECASE)

            if redact_pii:
                cleaned_body = _clean_pii(cleaned_body)

            # reencode and replace the body
            encoded_body = utility.base64_encode(cleaned_body)
            cleaned_email = re.sub(re.escape(body_content), encoded_body, cleaned_email, flags=re.IGNORECASE)
        else:
            cleaned_body = body_content
            for redaction_value in redaction_value_list:
                if redaction_value.lower() in cleaned_body.lower():
                    cleaned_body = re.sub(re.escape(redaction_value), 'REDACTED', cleaned_body, flags=re.IGNORECASE)

            if redact_pii:
                cleaned_body = _clean_pii(cleaned_body)

            cleaned_email = re.sub(re.escape(body_content), cleaned_body, cleaned_email, flags=re.IGNORECASE)

    return cleaned_email
