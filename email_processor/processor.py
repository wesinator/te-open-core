#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import email

from .cleaner import clean_email
from .formatter import format_email_for_db
from .parse_attachments import parse_attachment
from .parse_headers import parse_header
from db import db_creator
from utility import utility
from totalemail import settings


def _get_email_structure(
    msg, email_body_objects, email_attachment_objects, structure="", level=0, perform_external_analysis=True
):
    """Get the structure of the email (this function is modified from https://github.com/python/cpython/blob/master/Lib/email/iterators.py#L59 - which is described here: https://docs.python.org/3.5/library/email.iterators.html?highlight=_structure#email.iterators._structure)."""
    # TODO: simplify this
    indent_sequence = '|'.join([('&nbsp;' * 8) for i in range(0, level + 1)])
    if msg.is_multipart():
        structure += "\n" + indent_sequence + msg.get_content_type()
        for subpart in msg.get_payload():
            structure, email_body_objects, email_attachment_objects = _get_email_structure(
                subpart,
                email_body_objects,
                email_attachment_objects,
                structure,
                level + 1,
                perform_external_analysis=perform_external_analysis,
            )
        return structure, email_body_objects, email_attachment_objects
    else:
        new_id = None

        # if the email only has one section that is not multipart, be sure to pull out the payload
        if level == 0:
            if msg.get_content_disposition() == "attachment":
                new_attachment_data = parse_attachment(msg.get_payload())
                new_attachment = db_creator.create_attachment(new_attachment_data)
                new_id = new_attachment.id
                email_attachment_objects.append(new_attachment)
                if 'Attachments:' not in structure:
                    structure += '\n<a href="#attachments"><b>Attachments:</b></a>'
            else:
                new_body = db_creator.create_body(
                    msg.get_payload(), msg.get_content_type(), perform_external_analysis=perform_external_analysis
                )
                new_id = new_body.id
                email_body_objects.append(new_body)
        else:
            if msg.get_content_disposition() == "attachment":
                new_attachment_data = parse_attachment(msg)
                new_attachment = db_creator.create_attachment(new_attachment_data)
                new_id = new_attachment.id
                email_attachment_objects.append(new_attachment)
                level -= 1
                # recalculate the indent_sequence (this may have changed if this object is the first attachment)
                indent_sequence = '|'.join([('&nbsp;' * 8) for i in range(0, level + 1)])
                if 'Attachments:' not in structure:
                    structure += '\n<a href="#attachments"><b>Attachments:</b></a>'
            else:
                new_body = db_creator.create_body(
                    msg, msg.get_content_type(), perform_external_analysis=perform_external_analysis
                )
                new_id = new_body.id
                email_body_objects.append(new_body)
        structure += "\n" + indent_sequence + "<a href='#{}'>".format(new_id) + msg.get_content_type() + "</a>"
        return structure, email_body_objects, email_attachment_objects


def process_email(
    email_text, request_details, redact_email_data=False, perform_external_analysis=True, redaction_values=None
):
    """Process the email text into a form that is ready for the database."""
    if email_text == '':
        return None

    email_body_objects = []
    email_attachment_objects = []
    processed_request_data = settings._process_request_data(request_details)

    # format
    email_text = format_email_for_db(email_text)

    # hash
    original_sha256 = utility.sha256(email_text)
    cleaned_sha256 = original_sha256

    # clean
    if redact_email_data or redaction_values:
        email_text = clean_email(email_text, redaction_values)
        cleaned_sha256 = utility.sha256(email_text)

    email_message = email.message_from_string(email_text)

    # parse and create headers
    header_json = parse_header(email_text)
    email_header = db_creator.create_header(header_json, perform_external_analysis=perform_external_analysis)

    # parse and create attachments and bodies (the `_get_email_structure` function will create bodies and attachments)
    email_structure, email_body_objects, email_attachment_objects = _get_email_structure(
        email_message, email_body_objects, email_attachment_objects, perform_external_analysis=perform_external_analysis
    )

    # create email
    new_email = db_creator.create_email(
        email_text,
        original_sha256,
        cleaned_sha256,
        processed_request_data,
        email_structure,
        email_header,
        email_body_objects,
        email_attachment_objects,
        perform_external_analysis,
    )

    return new_email
