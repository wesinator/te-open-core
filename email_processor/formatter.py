#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provide standardized formatting an email should undergo before being created in the DB."""

import re


def _decode_text(text):
    """Decode the given text appropriately."""
    if isinstance(text, bytes):
        try:
            decoded_text = text.decode('utf-8')
        except UnicodeDecodeError:
            decoded_text = str(text)
    else:
        decoded_text = text

    # replace any null characters (and anything after a null character)
    decoded_text = re.sub('\x00.*?\n', '\n', decoded_text)

    return decoded_text


def _remove_line_endings(text):
    pattern = '(?<!\r)\n'
    # add a carriage return before all newlines NOT preceded by a carriage return
    text = re.sub(pattern, '\r\n', text)
    # I can add this newline (which matches the spec) because I stripped the email earlier
    return text + '\r\n'


def format_email_for_db(email_text):
    """Format the given request for being stored in the DB."""
    # I am removing the newline at the end of the email here because I add it in the _remove_line_endings function
    formatted_email_text = email_text.strip()
    formatted_email_text = _decode_text(formatted_email_text)
    formatted_email_text = _remove_line_endings(formatted_email_text)

    return formatted_email_text
