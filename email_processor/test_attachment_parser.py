#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.test import TestCase

from .parse_attachments import parse_attachment
from test_resources import DefaultTestObject

TestData = DefaultTestObject()


def find_attachments(msg):
    """Find attachments in the given email."""
    if msg.is_multipart():
        for subpart in msg.get_payload():
            if subpart.get_content_disposition() == "attachment":
                return parse_attachment(subpart)

    return None


class AttachmentParserTest(TestCase):
    def test_incorrect_attachment_padding(self):
        attachment = find_attachments(TestData.bad_attachment_email_message)

        assert isinstance(attachment, dict)

        assert attachment['content_type'] == 'application/octet-stream'
        assert attachment['filename'] == 'image001.png'
        assert attachment['full_text'] != ''
        # the hashes below aren't verified from the original file... they are only checking the precision of the algorithm (letting us know if it changes over time) and not the accuracy of the algorithm with respect to the actual true hashes
        assert attachment['id'] == 'f342baa4b4b3501bcb18b0b6b4a9d08dbd85f198e5c4fc921251f3a84d04ed23'
        assert attachment['md5'] == '60be626fbf635fa47608d8ac96be1f39'
        assert attachment['sha1'] == '673a7a70ccdf5cd485b03a471ebb6eadf57ba253'

    def test_no_attachment(self):
        """Test a situation in which an email has the metadata for an attachment, but no content for the attachment."""
        attachment = find_attachments(TestData.no_attachment_email_message)

        assert isinstance(attachment, dict)

        assert attachment['content_type'] == 'application/octet-stream'
        assert attachment['filename'] == '111111111111111111.txt'
        assert attachment['full_text'] != ''
        # the hashes below aren't verified from the original file... they are only checking the precision of the algorithm (letting us know if it changes over time) and not the accuracy of the algorithm with respect to the actual true hashes
        assert attachment['id'] == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        assert attachment['md5'] == 'd41d8cd98f00b204e9800998ecf8427e'
        assert attachment['sha1'] == 'da39a3ee5e6b4b0d3255bfef95601890afd80709'

    def test_hashing_a(self):
        """Make sure the hashing algorithm by checking the hashes against the known hashes for files - this one checks the hash of a text file."""
        attachment = find_attachments(TestData.attachment_hash_tester_a_email_message)
        assert attachment['md5'] == 'df0a9498a65ca6e20dc58022267f339a'
        assert attachment['sha1'] == '7265cdc53d4a78743e5b09d9a842e85d54fe5b44'
        assert attachment['id'] == '986ee148d0906f9335f2fe790154e7b260fdaed34fe1e3916f6d26f93a95a0f1'

    def test_hashing_b(self):
        """Make sure the hashing algorithm by checking the hashes against the known hashes for files - this one checks the hash of a word document."""
        attachment = find_attachments(TestData.attachment_hash_tester_b_email_message)
        assert attachment['md5'] == '7c3a5c2355f0da6475ebd8adb0863eab'
        assert attachment['sha1'] == 'b8f2954d5dd28d43dbf7ed4b5916309d0b45586c'
        assert attachment['id'] == '041638601ea6d06d17c70a563e44c8dd5d852fa8cd857e85b1cedcdda0c5c364'
