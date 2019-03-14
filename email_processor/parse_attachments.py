#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse attachments and attachment metadata from email text."""

import hashlib

from utility import utility


def parse_attachment(attachment):
    """Parse attachments and attachment metadata from email text."""
    attachment_data = dict()

    formatted_payload_content = str(attachment.get_payload()).replace('\n', '').encode('utf-8')

    try:
        decoded_content = utility.decode_base64(formatted_payload_content)
    except Exception as e:
        if str(e) == "Incorrect padding":
            # TODO: Just a reminder for J: I choose not to keep track of whether or not an attachment's hashes came from the decoded attachment or the undecoded version because I plan on later capturing the hashes of both (the decoded and undedoced versions) and we can easily compare the two to determine if an email was correctly decoded or not (2)
            print("[attachment parser]: Unable to read payload for attachment: {}".format(attachment))
            decoded_content = formatted_payload_content
        else:
            raise e

    # find the hashes for the attachment content
    attachment_data['id'] = hashlib.sha256(decoded_content).hexdigest()
    attachment_data['md5'] = hashlib.md5(decoded_content).hexdigest()
    attachment_data['sha1'] = hashlib.sha1(decoded_content).hexdigest()

    # use the built-in functions from the `email` module to find metadata about the attachment
    attachment_data['content_type'] = attachment.get_content_type()
    attachment_data['filename'] = attachment.get_filename()
    attachment_data['full_text'] = str(attachment)

    return attachment_data
