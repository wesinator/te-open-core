#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility to create entities in the database."""

import json

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import Email, Header, Body, Attachment, JOIN_STRING
from email_processor import parse_bodies
from utility import utility
import analyzer

created_network_data = {'ip_addresses': list(), 'hosts': list(), 'email_addresses': list(), 'urls': list()}


# TODO: could all of these functions be moved into the `save` functions in the classes in models.py?


def create_email(
    email_text,
    original_sha256,
    cleaned_sha256,
    submitter_hash,
    email_structure,
    email_header,
    email_body_objects,
    email_attachment_objects,
    perform_external_analysis,
):
    # the try-except business below handles cases where an email is uploaded and then the same email is uploaded, but then redacted - there may be a better way to handle these situations
    try:
        email_in_db = Email.objects.get(pk=original_sha256)
    except ObjectDoesNotExist:
        new_email, created = Email.objects.update_or_create(
            id=original_sha256,
            cleaned_id=cleaned_sha256,
            full_text=email_text,
            submitter=submitter_hash,
            structure=email_structure,
            header=email_header,
        )

        for body in email_body_objects:
            new_email.bodies.add(body)

        for attachment in email_attachment_objects:
            new_email.attachments.add(attachment)

        analyzer.start_analysis(new_email, perform_external_analysis)
        return new_email
    else:
        # update the modified date
        email_in_db.modified = timezone.now()
        email_in_db.save()
        message = 'Duplicate email with id {}'.format(email_in_db.id)
        utility.create_alerta_alert('Duplicate email uploaded', 'info', message)
        return email_in_db


def create_header(header_json, perform_external_analysis=True):
    header_string = json.dumps(header_json)

    with transaction.atomic():
        new_header, created = Header.objects.update_or_create(id=utility.sha256(header_string), data=header_json)

    if perform_external_analysis:
        analyzer.external_analysis.find_network_data(header_string, new_header.id, 'header')

    return new_header


def create_body(body_payload, body_content_type, perform_external_analysis=True):
    """'While we live in these earthly bodies, we groan and sigh, but it’s not that we want to die and get rid of these bodies that clothe us. Rather, we want to put on our new bodies so that these dying bodies will be swallowed up by life.' ~ 2 Corinthians 5:4."""
    body_text = str(body_payload).strip()

    decoded_text = None

    # TODO: revisit this function as some of the operations done in this function can probably be moved to the utility

    if 'content-transfer-encoding: base64' in str(body_text).lower():
        decoded_text = parse_bodies.decode_base64(str(body_text).split('\n\n')[-1])

    new_body, created = Body.objects.update_or_create(
        id=utility.sha256(body_text), defaults={'full_text': body_text, 'content_type': body_content_type, 'decoded_text': decoded_text}
    )

    if perform_external_analysis:
        analyzer.external_analysis.find_network_data(body_text, new_body.id, 'body')

    return new_body


def _filename_exists(existing_filenames, new_filename):
    """Check to see if the new filename already exists."""
    return (
        '{}{}'.format(new_filename, JOIN_STRING) in existing_filenames
        or '{}{}'.format(JOIN_STRING, new_filename) in existing_filenames
    )


def create_attachment(attachment_data):
    new_attachment, created = Attachment.objects.update_or_create(
        id=attachment_data['id'],
        defaults={
            'content_type': attachment_data['content_type'],
            'md5': attachment_data['md5'],
            'sha1': attachment_data['sha1'],
            'full_text': attachment_data['full_text'],
        },
    )
    # handle multiple file names
    if new_attachment.filename:
        # check to see if the new file name already exists... only add new filenames
        if not _filename_exists(new_attachment.filename, attachment_data['filename']):
            new_attachment.filename = new_attachment.filename + JOIN_STRING + attachment_data['filename']
    else:
        new_attachment.filename = attachment_data['filename']
    new_attachment.save()
    return new_attachment
