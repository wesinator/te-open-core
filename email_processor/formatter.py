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
    # find all newlines NOT preceded by a carriage return
    pattern = '(?<!\r)\n'
    # add a carriage return before all newlines NOT preceded by a carriage return
    text = re.sub(pattern, '\r\n', text)

    # if the text does not end in a newline, add one (this is according to spec)
    if not text.endswith('\r\n'):
        text = text + '\r\n'

    return text


def format_email_for_db(email_text):
    """Format the given request for being stored in the DB."""
    formatted_email_text = _decode_text(email_text)
    formatted_email_text = _remove_line_endings(formatted_email_text)

    return formatted_email_text
