#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import collections
from email import _header_value_parser as parser
import email
from email.policy import default
import hashlib
import ipaddress
import json
import os
import re
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

import requests

from totalemail import settings

EmailAddress = collections.namedtuple('EmailAddress', ['display_name', 'username', 'domain'])


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


def url_domain_name(url):
    """Get the domain name of the given url."""
    domain_name = urlparse.urlparse(url).netloc
    return domain_name


def is_ip_address(text):
    """Determine if the given text is an IP address or not."""
    try:
        ipaddress.ip_address(text)
    except ValueError:
        return False
    else:
        return True


def email_read(email_text):
    """Return an email object for the given email text."""
    return email.message_from_string(email_text, policy=default)


def email_bodies(email_object):
    """."""
    bodies = []

    if email_object.is_multipart():
        for subpart in email_object.get_payload():
            bodies.extend(email_bodies(subpart))
    else:
        if email_object.get_content_disposition() != "attachment":
            bodies.append(email_object)

    return bodies


def parse_email_address(email_address):
    parsed_email_address = parser.get_address(email_address)[0]

    if parsed_email_address.all_mailboxes:
        mailbox = parsed_email_address.all_mailboxes[0]
        return EmailAddress(display_name=mailbox.display_name, username=mailbox.local_part, domain=mailbox.domain)
    else:
        return EmailAddress(display_name='', username='', domain='')


def base64_encode(text):
    """Base64 encode the given text."""
    import base64

    result = base64.standard_b64encode(text.encode('utf-8'))
    return result.decode('utf-8')


def base64_decode(text):
    """Base64 decode the given text."""
    import base64

    result = base64.standard_b64decode(text.encode('utf-8'))
    return result.decode('utf-8')


SOURCE_WEIGHTINGS = {
    'Orange Assassin': '(x / 3) - 1',
    'Earth Reflections Spam Regexes': '(2 ** x / 194) - 0.01',
    'Hubspot Spam Keywords': '(x / 3) - .1',
    'Ram Samudrala Spam Regexes': 'x',
}


def _calculate(score, source):
    """Calculate the weighted score for the given score."""
    if SOURCE_WEIGHTINGS.get(source):
        score_function = SOURCE_WEIGHTINGS[source]
        score_function = score_function.replace('x', str(score))
        return eval(score_function)
    else:
        return score


def email_score_calculate(email):
    """Calculate the score of the email from the email."""
    # calculate the score for the email
    email_analysis_score_data = {}
    for analysis in email.analysis_set.all().order_by('-first_seen'):
        if not email_analysis_score_data.get(analysis.source):
            email_analysis_score_data[analysis.source] = analysis.score

    values_to_average = []
    for source, score in email_analysis_score_data.items():
        values_to_average.append(
            _calculate(score, source)
        )

    if len(values_to_average) > 0:
        final_score = sum(values_to_average) / len(values_to_average)

        # add a final gut-check to make sure that the final score is with-in the appropriate boundaries
        if final_score > 1:
            final_score = 1.00
        elif final_score < -1:
            final_score = -1.00
    else:
        final_score = 0

    return final_score


def domain_is_common(domain_name):
    """Check to see if the domain name is common (and should not be displayed in the network data section)."""
    whitelisted_domain_regexes = ['(?:.*\.)?google\.com', 'fonts.googleapis.com', 'amazonaws.com', 'gmail.com', 'aol.com']

    for regex in whitelisted_domain_regexes:
        if re.match(regex, domain_name):
            return True

    return False
