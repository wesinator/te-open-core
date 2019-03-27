#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility to create entities in the database."""

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import Email, Header, Body, Attachment, Analysis, JOIN_STRING
from email_processor import parse_bodies
from utility import utility
import analyzer

created_network_data = {'ip_addresses': list(), 'hosts': list(), 'email_addresses': list(), 'urls': list()}


# TODO: could all of these functions be moved into the `save` functions in the classes in models.py?

def create_analysis(notes, source, new_email):
    """Create an analysis for the email."""
    new_analysis = Analysis(notes=";".join(notes), source=source, score=0, email=new_email)
    new_analysis.save()


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

        # TODO: I've commented out the code on the 3 lines below because we are not using on internal analysis any more... the uncommented line below the commented lines below is correct and simply triggers the external analysis
        # analyses = analyzer.start_analysis(new_email, perform_external_analysis)
        # for analysis_source in analyses:
        #     create_analysis(analyses[analysis_source], analysis_source, new_email)
        analyzer.start_analysis(new_email, perform_external_analysis)
        return new_email
    else:
        # update the modified date
        email_in_db.modified = timezone.now()
        email_in_db.save()
        message = 'Duplicate email with id {}'.format(email_in_db.id)
        utility.create_alerta_alert('Duplicate email uploaded', 'info', message)
        return email_in_db


def create_header(header_fields, header_string, perform_external_analysis=True):
    try:
        with transaction.atomic():
            new_header, created = Header.objects.update_or_create(
                accept_language=header_fields.get('Accept_Language'),
                alternate_recipient=header_fields.get('Alternate_Recipient'),
                bcc=header_fields.get('Bcc'),
                cc=header_fields.get('Cc'),
                content_language=header_fields.get('Content_Language'),
                content_location=header_fields.get('Content_Location'),
                content_md5=header_fields.get('Content_MD5'),
                content_type=header_fields.get('Content_Type'),
                content_translation_type=header_fields.get('Content_Translation_Type'),
                date=header_fields.get('Date'),
                delivery_date=header_fields.get('Delivery_Date'),
                dkim=header_fields.get('DKIM_Signature'),
                message_id=header_fields.get('Message_ID'),
                encoding=header_fields.get('Encoding'),
                _from=header_fields.get('From'),
                original_from=header_fields.get('Original_From'),
                original_recipient=header_fields.get('Original_Recipient'),
                original_subject=header_fields.get('Original_Subject'),
                originator_return_address=header_fields.get('Originator_Return_Address'),
                received=header_fields.get('Received'),
                received_spf=header_fields.get('Received_SPF'),
                reply_to=header_fields.get('Reply_To'),
                return_path=header_fields.get('Return_Path'),
                sender=header_fields.get('Sender'),
                subject=header_fields.get('Subject'),
                to=header_fields.get('To'),
                x_originating_ip=header_fields.get('x_originating_ip'),
                # TODO: do we need the "recipient_email" property which is commented out below? (3)
                # recipient_email=header_fields.get('to', [{}])[0].get('email'), # Implement list handling for data type with multple entries
                full_text=header_string,
                id=utility.sha256(header_string),
            )
    except Exception as e:
        try:
            message = "Error trying to save header for the 1st time: {}".format(e)
            utility.create_alerta_alert('Header creation error', 'warning', message)
            # If the first creation failed, try to create a header with less fields
            with transaction.atomic():
                new_header, created = Header.objects.update_or_create(
                    full_text=header_string,
                    id=utility.sha256(header_string),
                    subject=header_fields.get('Subject'),
                    to=header_fields.get('To'),
                    _from=header_fields.get('From'),
                )
        except Exception as e:
            message = "Error trying to save header for the 2nd time: {}".format(e)
            utility.create_alerta_alert('Header creation error', 'warning', message)
            # If the first and second creation attempts failed, just record the bare minimum
            with transaction.atomic():
                new_header, created = Header.objects.update_or_create(
                    full_text=header_string, id=utility.sha256(header_string)
                )

    if perform_external_analysis:
        analyzer.external_analysis.find_network_data(header_string, new_header.id, 'header')

    return new_header


def create_body(body_payload, body_content_type, perform_external_analysis=True):
    """'While we live in these earthly bodies, we groan and sigh, but it’s not that we want to die and get rid of these bodies that clothe us. Rather, we want to put on our new bodies so that these dying bodies will be swallowed up by life.' ~ 2 Corinthians 5:4."""
    body_text = str(body_payload).strip()

    decoded_text = None

    if 'content-transfer-encoding: base64' in str(body_text).lower():
        decoded_text = parse_bodies.decode_base64(str(body_text).split('\n\n')[-1])

    new_body, created = Body.objects.update_or_create(
        id=utility.sha256(body_text), defaults={'full_text': body_text, 'decoded_text': decoded_text}
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
