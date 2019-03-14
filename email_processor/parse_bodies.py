#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse attachments and attachment metadata from email text."""

from utility import utility


def decode_base64(data):
    """Decode base64 for an email body"""
    return utility.decode_base64(data.replace('\n', '').encode('utf-8'))
