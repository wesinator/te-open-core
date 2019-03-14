#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hashlib
import json
import os
import requests

from totalemail import settings


def is_running_locally():
    """Return whether or not the system is running locally."""
    if settings.DATABASES['default']['USER'] == 'postgres' and settings.DATABASES['default']['HOST'] == 'db':
        return True
    else:
        return False


def sha256(text):
    """Find the hash of the given text."""
    if isinstance(text, bytes):
        return hashlib.sha256(text).hexdigest()
    else:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()


def create_alerta_alert(event, severity, text):
    """Handle the interface with Alerta."""

    if is_running_locally():
        print('Running locally, so no alert will be sent to alerta. Here are the details about the alert:')
        print('event: {}'.format(event))
        print('severity: {}'.format(severity))
        print('text: {}'.format(text))
    else:
        headers = {'Content-type': 'application/json'}

        if os.environ['ALERTA_KEY'] in [None, ""]:
            print("No Alerta Key provided.")
        else:
            headers['Authorization'] = 'Key {}'.format(os.environ['ALERTA_KEY'])

        if os.environ['ALERTA_BASE_URL'] in [None, ""]:
            print("No Alerta Base URL provided. Skipping Alerta logging for now.")
            return

        try:
            requests.post(
                '{}/alert'.format(os.environ['ALERTA_BASE_URL']),
                headers=headers,
                data=json.dumps(
                    {
                        "environment": "Production",
                        "event": event,
                        "resource": "totalemail",
                        "severity": severity,
                        "service": ["UI"],
                        "text": text,
                    }
                ),
            )
        except requests.exceptions.MissingSchema as e:
            print('Alerta is failing. Check your environment variables? {}'.format(e))
            return


def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        if missing_padding == 1:
            data += b'A=='
        else:
            data += b'=' * (4 - missing_padding)
    return base64.decodestring(data)
