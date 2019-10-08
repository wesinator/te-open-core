#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .cleaner import clean_email
from .formatter import format_email_for_db
from .parse_attachments import parse_attachment
from .parse_headers import parse_header
from db import db_creator
from utility import utility
from totalemail import settings


def process_email(
    email_text,
    request_details,
    redact_email_data=False,
    perform_external_analysis=True,
    redaction_values=None,
    redact_pii=False,
):
    """Process the email text into a form that is ready for the database."""
    if email_text == '':
        return None

    processed_request_data = settings._process_request_data(request_details)

    # format
    email_text = format_email_for_db(email_text)

    # hash
    original_sha256 = utility.sha256(email_text)
    cleaned_sha256 = original_sha256

    # clean
    if redact_email_data or redaction_values:
        email_text = clean_email(email_text, redaction_values, redact_pii=redact_pii)
        cleaned_sha256 = utility.sha256(email_text)

    # parse and create headers
    header_json = parse_header(email_text)

    # if there are no headers in the email, abort the import and return None
    if header_json == []:
        return None

    email_header = db_creator.create_header(
        header_json, original_sha256, perform_external_analysis=perform_external_analysis
    )

    email_structure = utility.email_structure(email_text)

    bodies = utility.email_bodies_as_objects(email_text)
    body_objects = []
    for body in bodies:
        # determine whether or not this body is base64 encoded
        decode_body_as_base64 = body.get('Content-Transfer-Encoding', '').lower() == 'base64'

        new_body = db_creator.create_body(
            body.get_payload(),
            body.get_content_type(),
            original_sha256,
            perform_external_analysis=perform_external_analysis,
            decode_body_as_base64=decode_body_as_base64,
        )
        body_objects.append(new_body)

    attachments = utility.email_attachments(email_text)
    attachment_objects = []
    for attachment in attachments:
        new_attachment_data = parse_attachment(attachment)
        new_attachment = db_creator.create_attachment(new_attachment_data)
        attachment_objects.append(new_attachment)

    # create email
    new_email = db_creator.create_email(
        email_text,
        original_sha256,
        cleaned_sha256,
        processed_request_data,
        email_structure,
        email_header,
        body_objects,
        attachment_objects,
        perform_external_analysis,
    )

    return new_email
