#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from .parse_headers import parse_header
from utility import utility


def clean_email(email_text, redaction_values=None):
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

    # find all base64 encoded header values
    base64_encoded_header_pattern = '=\?[a-zA-Z0-9\-]+\?B\?([a-zA-Z0-9+\/=]+)\?='
    for base64_content in re.findall(base64_encoded_header_pattern, email_text):
        # decode the content
        decoded_content = utility.base64_decode(base64_content)
        cleaned_content = decoded_content

        for redaction_value in redaction_value_list:
            if redaction_value.lower() in decoded_content.lower():
                cleaned_content = re.sub(re.escape(redaction_value), 'REDACTED', decoded_content, flags=re.IGNORECASE)

        # encode the content and replace it in the email
        encoded_content = utility.base64_encode(cleaned_content)
        cleaned_email = re.sub(re.escape(base64_content), encoded_content, cleaned_email, flags=re.IGNORECASE)

    # TODO: we also need to make sure that things are properly removed from base64 encoded bodies
    # TODO: we need to make sure we are not changing the content of an attachment in the redaction process
    for redaction_value in redaction_value_list:
        cleaned_email = re.sub(re.escape(redaction_value), 'REDACTED', cleaned_email, flags=re.IGNORECASE)

    # redact the bodies which are base64 encoded
    email_object = utility.email_read(email_text)
    if email_object['Content-Transfer-Encoding'] and email_object['Content-Transfer-Encoding'].lower() == 'base64':
        bodies = utility.email_bodies(email_object)
        for body in bodies:
            # decode the body
            decoded_body = utility.base64_decode(body.get_payload())
            cleaned_body = decoded_body

            # redact
            for redaction_value in redaction_value_list:
                if redaction_value.lower() in decoded_body.lower():
                    cleaned_body = re.sub(re.escape(redaction_value), 'REDACTED', decoded_body, flags=re.IGNORECASE)

            # reencode and replace the body
            encoded_body = utility.base64_encode(cleaned_body)
            cleaned_email = re.sub(re.escape(body.get_payload()), encoded_body, cleaned_email, flags=re.IGNORECASE)

    return cleaned_email
