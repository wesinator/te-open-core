#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse header fields from an email."""

import datetime
import json
import re

from django.utils.dateparse import parse_datetime

from utility import utility

"""Contact Objects:
    {
        'name': 'John Doe',
        'email': 'johndoe@gmail.com'
    }
"""

# Need to polish receive parser

# def receive_parser(self, string):

#     event = dict()
#     date = string.split(';')[-1].strip('\n').strip()[0:-6]
#     event['date'] = self.get_date_time_string(date)

#     from_data = re.search('from \[?(.*?)\]? \((.*?)\[(.*?)\]\)', string)
#     if from_data:
#         event['sender_server'] = from_data.group(1).strip('?')
#         event['sender_domain'] = from_data.group(2)
#         event['sender_address'] = from_data.group(3)

#     by_data = re.search('by (.*?) (?:with) (.*?) id (.*?)(?:;|\s)', string)
#     if by_data:
#         event['receiver_server'] = by_data.group(1)
#         event['protocol'] = by_data.group(2)
#         event['emailid'] = by_data.group(3)

#     for_field = re.match('for <(.*?)>', string)
#     if for_field:
#         event['targets'] = for_field.group(1).split(',')
#     return event


def _contact_parser(string):
    if string == '':
        return None

    string = string.replace('"', '').strip()
    contact_format1 = re.match('(.*?)\s*?<(.*?)>', string)
    contact_format2 = re.match('(.*?)\s*?\((.*?)\)', string)
    if contact_format1:
        name = contact_format1.group(1).strip("'")
        # TODO: perhaps use regex instead of strip (3)
        email = contact_format1.group(2).strip('<').strip('>')
    elif contact_format2:
        name = contact_format2.group(2).strip("'")
        email = contact_format2.group(1)
    else:
        name = None
        email = string.strip('<').strip('>')
    return {'name': name, 'email': email}


def _multi_contact_parser(string):
    return [_contact_parser(r) for r in string.split(',')]


def _date_parser(string):
    dt = str()
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %z (%Z)',
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S',
        '%d %b %Y %H:%M:%S %z',
        '%a %b %d %H:%M:%S %Y',
    ]
    date_formatted = False

    for date_format in date_formats:
        try:
            dt = datetime.datetime.strptime(string, date_format)
        except ValueError:
            pass
        else:
            date_formatted = True
            break

    if not date_formatted:
        # try Django's function
        parsed_date = parse_datetime(dt)

        if parsed_date is not None:
            dt = parsed_date
        else:
            dt = string
            print('Could not parse date: {}'.format(string))

    return str(dt)


def _dkim_parser(string):
    dkim_obj = dict()
    cleaned = ''.join(string.split())
    key_value_pairs = cleaned.split(';')
    for item in key_value_pairs:
        pairs = item.split('=')
        if len(pairs) > 2:
            key = pairs[0]
            value = ''.join(pairs[1:])
        else:
            key, value = pairs
        dkim_obj[key] = value
    return dkim_obj


def _id_parser(string):
    # TODO: the regex below should probably be pulled from somewhere else (the indicator parser?) (3)
    ip_address_regex = (
        '(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))'
    )
    stripped = string.strip('<').strip('>')

    try:
        email_id, host = stripped.split('@')
    except ValueError:
        return stripped

    ip = re.match(ip_address_regex, host)
    if ip:
        host = ip.group(0)
    return {'id': email_id, 'host': host}


def _address_parser(string):
    stripped = string.strip('<').strip('>')
    return stripped


def _return_raw(string):
    if (string.startswith('[') or string.startswith('{')) and (string.endswith(']') or string.endswith('}')):
        try:
            string = json.loads(string)
        except json.decoder.JSONDecodeError:
            return string[1:-1]
    return string


# listed out for keeping track of what headers are being processed and how
header_function_mapping = {
    'Accept_Language': _return_raw,
    'Alternate_Recipient': _multi_contact_parser,
    'Bcc': _multi_contact_parser,
    'Cc': _multi_contact_parser,
    'Content_Language': _return_raw,
    'Content_Location': _return_raw,
    'Content_MD5': _return_raw,
    'Content_Translation_Type': _return_raw,
    'Content_Type': _return_raw,
    'Date': _date_parser,
    'Delivered_To': _return_raw,
    'Delivery_Date': _date_parser,
    'DKIM_Signature': _dkim_parser,
    'Encoding': _return_raw,
    'Encrypted': _return_raw,
    'From': _contact_parser,
    'Language': _return_raw,
    'Message_ID': _id_parser,
    'Original_From': _contact_parser,
    'Original_Recipient': _multi_contact_parser,
    'Original_Subject': _return_raw,
    'Originator_Return_Address': _return_raw,
    'Received': _return_raw,  # Implement strong parser
    'Received_SPF': _return_raw,  # Implement strong parser
    'Reply_To': _contact_parser,
    'Return_Path': _address_parser,
    'Sender': _contact_parser,
    'Subject': _return_raw,
    'To': _multi_contact_parser,
    'X-Originating-IP': _return_raw,
    'x_mailer': _return_raw,
}


def parse_header(email_message, log_mising_properties=True):
    """Parser email headers."""
    from db.models import JOIN_STRING

    parsed_header_fields = dict()

    for item in email_message.items():
        header_name = item[0].replace(' ', '_').replace('-', '_')
        if header_function_mapping.get(header_name):
            if parsed_header_fields.get(header_name):
                parsed_header_fields[header_name] = (
                    parsed_header_fields[header_name] + JOIN_STRING + header_function_mapping[header_name](item[1])
                )
            else:
                parsed_header_fields[header_name] = header_function_mapping[header_name](item[1])
        else:
            if log_mising_properties:
                utility.create_alerta_alert('Unmapped header property: {}'.format(header_name), 'info', '')
            if parsed_header_fields.get(header_name):
                parsed_header_fields[header_name] = parsed_header_fields[header_name] + JOIN_STRING + item[1]
            else:
                parsed_header_fields[header_name] = item[1]

    return parsed_header_fields


def get_header_string(email_message):
    """Create a string representation of the header."""
    full_header_text = ""

    for header_field in email_message.items():
        full_header_text += (
            ": ".join(header_field) + "\r\n"
        )  # RFC 2822 header uses CRLF line endings - https://tools.ietf.org/html/rfc2822#section-2.1

    return full_header_text
