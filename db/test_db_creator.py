"""Testing functions for total_email."""

import datetime
import hashlib

from django.test import TestCase

from utility import utility
from test_resources import DefaultTestObject

TestData = DefaultTestObject()


class TestUtility(TestCase):
    """Utility for performing repetitive tests."""

    def association_test(
        self,
        object1,
        object2,
        storage_location1,
        storage_location2,
        many_to_one=False,
        desired_object1_id=1,
        desired_object2_id=1,
    ):
        """Test two-way associations."""
        # test relating the first object with the second
        storage_location1.add(object2)
        self.assertEqual(storage_location1.all()[0].id, desired_object2_id)

        # test relating the second object with the first
        if not many_to_one:
            storage_location2.add(object1)
            self.assertEqual(storage_location2.all()[0].id, desired_object1_id)
        else:
            storage_location2 = object1
            self.assertEqual(storage_location2.id, desired_object1_id)

    def string_test(self, incoming_object, desired_string):
        """Ensure object's string matches up to the desired string."""
        self.assertEqual(str(incoming_object), desired_string)

    def date_test(self, incoming_datestamp, desired_datestamp=None):
        """Ensure the datestamp matches up with the current ones."""
        # if there is no desired datestamp given, assume that the user wants to use today's date information
        if desired_datestamp is None:
            self.assertEqual(incoming_datestamp.year, datetime.datetime.today().year)
            self.assertEqual(incoming_datestamp.month, datetime.datetime.today().month)
            self.assertEqual(incoming_datestamp.day, datetime.datetime.today().day)
        # if there is a desired_datestamp given, compare the incoming_datestamp with the desired_datestamp
        else:
            self.assertEqual(incoming_datestamp.year, desired_datestamp.year)
            self.assertEqual(incoming_datestamp.month, desired_datestamp.month)
            self.assertEqual(incoming_datestamp.day, desired_datestamp.day)


relater = TestUtility()


def test_create_sha256_id():
    """Make sure the utility.sha256 function can handle byte strings and standard strings."""
    byte_string = b'testing'
    assert utility.sha256(byte_string) == hashlib.sha256(byte_string).hexdigest()
    standard_string = 'testing'
    assert utility.sha256(standard_string) == hashlib.sha256(standard_string.encode("utf-8")).hexdigest()


class EmailTests(TestCase):
    """Email related tests."""

    def test_importer_simply(self):
        new_email = TestData.create_email()
        assert new_email.id == 'eab5bd1488bd546155249dcb3e8e4c40c23bad2c9601faa04cf75ac431289676'

    def test_create_email(self):
        """Test email creation."""
        new_email = TestData.create_email()
        assert new_email.id == TestData.email_id
        assert new_email.full_text == TestData.email_text.replace('\n', '\r\n')
        relater.date_test(new_email.first_seen)
        relater.date_test(new_email.modified)
        assert len(new_email.submitter) == 16

    def test_create_empty_email(self):
        """Test email creation."""
        new_email = TestData.create_email('')
        assert new_email is None

    def test_header_retrieval(self):
        new_email = TestData.create_email()
        assert new_email.header.get_header_key_values('from')[0] == 'Alice Underwood <alice@gmail.com>'

        # test an email with multiple header entries with the same key
        header_values = new_email.header.get_header_key_values('Received')
        assert isinstance(header_values, list)
        assert len(header_values) == 2

    def test_related_bodies(self):
        """Make sure a header and body are related to a created email."""
        new_email = TestData.create_email()
        assert len(new_email.bodies.all()) == 2
        body_ids = [body.id for body in new_email.bodies.all()]
        assert '6ce1e03b3902eee8dae69a56364413bdc9bb46d16743590ac42513217c5f430c' in body_ids
        assert 'ea2bf05889ac5cf478293492da99b6e62c629f78cc1ef6a1248aea5ff6b0e226' in body_ids

    def test_body_content_type(self):
        """Make sure a header and body are related to a created email."""
        new_email = TestData.create_email()
        assert len(new_email.bodies.all()) == 2
        content_types = [body.content_type for body in new_email.bodies.all()]
        assert 'text/plain' in content_types
        assert 'text/html' in content_types

    def test_related_header_body_and_attachment(self):
        """Make sure a header and body are related to a created email."""
        created_content = TestData.create_email(TestData.attachment_email_text)
        new_email = created_content
        new_header = created_content.header
        new_attachments = created_content.attachments.all()
        new_attachment_ids = [attachment.id for attachment in new_attachments]

        assert new_email.header.id == new_header.id
        assert len(new_email.attachments.all()) == len(new_attachments)

        for attachment in new_attachments:
            assert attachment.id in new_attachment_ids

    def test_creating_almost_duplicate_attachments(self):
        """Make sure TE can handle a situation in which the hash of an attachment already exists, but the name or other details of the attachment have changed."""
        original_file_name = 'Untitled Diagram.xml'
        updated_file_name = 'Bingo.xml'
        new_email = TestData.create_email(TestData.attachment_email_text)
        assert new_email.attachments.all()[0].filename == original_file_name
        new_email = TestData.create_email(TestData.attachment_email_text.replace(original_file_name, updated_file_name))
        assert new_email.attachments.all()[0].filename == 'Untitled Diagram.xml|||Bingo.xml'

    def test_body_parsing(self):
        """Make sure a header and body are related to a created email."""
        created_content = TestData.create_email(TestData.attachment_email_text)
        new_email = created_content
        new_bodies = created_content.bodies.all()

        assert len(new_bodies) == 2
        assert len(new_email.bodies.all()) == len(new_bodies)

    def test_bad_body_parsing(self):
        """Test parsing body from email which is badly parsed."""
        created_content = TestData.create_email(TestData.bad_body_email_text)
        assert 'From: pamela4701@eudoramail.com' not in created_content.bodies.all()[0].full_text

    def test_email_cleaning(self):
        """Make sure both the header content and the full_text are redacted properly."""
        assert 'github.com' in TestData.email_text

        new_email = TestData.create_email(redaction_values='github.com')
        assert 'github.com' not in new_email.full_text
        assert 'github.com' not in str(new_email.header)

    def test_no_header(self):
        """Test importing an email with no header."""
        # There may be an issue if there is an email body uploaded with a url in it (e.g. https://github.com/test/bingo.php)
        email_text = """
        This email has no headers!

        Yours truly,

        Bob"""
        new_email = TestData.create_email(email_text)
        assert new_email == None

    def test_email_str(self):
        """Test email string."""
        new_email = TestData.create_email()
        relater.string_test(new_email, TestData.email_id)

    def test_email_first_seen_modified(self):
        """Test email first seen date."""
        new_email = TestData.create_email()
        # test to make sure that the first_seen date is accurate
        relater.date_test(new_email.first_seen)
        # test to make sure that the modified date is accurate
        relater.date_test(new_email.modified)
        # make sure that the first seen and modified dates are the same
        relater.date_test(new_email.first_seen, new_email.modified)
        # make sure that the hour of the first seen and modified dates are the same
        assert new_email.first_seen.hour == new_email.modified.hour

    def test_creation_of_duplicate_email(self):
        """Test the creation of the same email twice."""
        new_email1 = TestData.create_email()
        new_email2 = TestData.create_email()
        assert new_email1.id == new_email2.id
        assert new_email1.first_seen == new_email2.first_seen
        assert new_email1.modified != new_email2.modified

    def test_line_endings_handling(self):
        """Make sure two emails with different line endings (in this case `\r\n` and `\n`) are treated as the same email."""
        lf_id = TestData.create_email(TestData.lf_ending_email_text).id
        cr_lf_id = TestData.create_email(TestData.cr_lf_ending_email_text).id
        assert lf_id == cr_lf_id

    def test_outlook_email_handling(self):
        """Make sure we can upload emails from outlook."""
        # TODO: make sure the hash created by this function corresponds with the one created by the UI (this hash was previously `c44c6a5c6b536b987ae38d517170f07f5bac14dda7c387bc2cea2a985ed1c629`)
        new_email = TestData.create_email(TestData.outlook_email_text)
        assert new_email.id == 'e971f4c5ef63c73c615e0cf82ac7b9f0bb82a36f886cdeb92d21039e37a0ac7f'
        assert '[1.2.3.4]' in str(new_email.header)

    def test_email_structure_as_html(self):
        new_email = TestData.create_email(TestData.outlook_email_text)
        assert new_email.id == 'e971f4c5ef63c73c615e0cf82ac7b9f0bb82a36f886cdeb92d21039e37a0ac7f'
        print(new_email.structure_as_html)
        assert (
            new_email.structure_as_html
            == """multipart/alternative<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#54712d1572ff09d73c3baacf0760a42735a3ce6dbd83144eb2f998155f53b740'>text/plain (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#b6fba92f1803f9f59d42fdd36b259fe8a550a68fee60808800cb11de14feeb8c'>text/html (body)</a>"""
        )


class HeaderTests(TestCase):
    # TODO: expand the tests in this section (3)

    def test_email_header(self):
        new_header = TestData.create_email().header
        assert new_header is not None

    def test_bad_content_type(self):
        new_header = TestData.create_email(TestData.bad_content_type_email_text).header
        assert new_header is not None
        assert new_header.get_header_key_values('subject')[0] == '[ILUG] STOP THE MLM INSANITY'

    def test_creation_of_duplicate_headers(self):
        new_headers = TestData.create_emails_with_same_header()
        assert new_headers[0].header.id == new_headers[1].header.id
        assert new_headers[0].header.first_seen == new_headers[1].header.first_seen
        assert new_headers[0].header.modified != new_headers[1].header.modified

    def test_header_with_subject_line_changed_by_SpamAssassin(self):
        email_text = '''Subject: SPAMISH SPAM
From: Bob Bradbury <bob@gmail.com>
To: Alice Asimov <alice@gmail.com>
X-Spam-Prev-Subject: Did You Authorize Her?

Hello!
'''

        new_email = TestData.create_email(email_text=email_text)
        assert new_email.header.subject == 'Did You Authorize Her?'


class BodyTests(TestCase):
    # TODO: expand the tests in this section (3)

    def test_email_body(self):
        new_bodies = TestData.create_email().bodies.all()
        assert new_bodies is not None
        assert len(new_bodies) == 2

    def test_email_body_2(self):
        new_bodies = TestData.create_email().bodies.all()
        assert 'text/plain' in [body.content_type for body in new_bodies]
        assert 'text/html' in [body.content_type for body in new_bodies]
        assert 'Subject:' in TestData.email_text

        for body in new_bodies:
            assert 'Subject:' not in body.full_text


class AttachmentTests(TestCase):
    """Attachment related tests."""

    def test_attachment_creation(self):
        attachments = TestData.create_email(TestData.attachment_email_text).attachments.all()
        assert len(attachments) == 2

        for attachment in attachments:
            assert attachment.email_set.all() is not None

    def test_attachment_attribute_creation(self):
        attachments = TestData.create_email(TestData.single_attachment_email_text).attachments.all()
        assert len(attachments) == 1

        for attachment in attachments:
            assert attachment.email_set.all() is not None
            assert attachment.content_type == 'text/xml'
            assert attachment.filename == 'Untitled Diagram.xml'


class StructureTest(TestCase):
    """Test the function which walks through the email and pull out all of the parts."""

    def test_email_structure(self):
        created_content = TestData.create_email()
        desired_structure = {
            'type': 'multipart/alternative',
            'content_disposition': None,
            'children': [
                {'type': 'text/plain', 'content_disposition': None, 'children': []},
                {'type': 'text/html', 'content_disposition': None, 'children': []},
            ],
        }
        print(created_content.structure)
        assert created_content.structure == desired_structure

    def test_email_structure_with_attachments(self):
        created_content = TestData.create_email(TestData.attachment_email_text)
        desired_structure = {
            'type': 'multipart/mixed',
            'content_disposition': None,
            'children': [
                {
                    'type': 'multipart/alternative',
                    'content_disposition': None,
                    'children': [
                        {'type': 'text/plain', 'content_disposition': None, 'children': []},
                        {'type': 'text/html', 'content_disposition': None, 'children': []},
                    ],
                },
                {'type': 'text/xml', 'content_disposition': 'attachment', 'children': []},
                {'type': 'image/png', 'content_disposition': 'attachment', 'children': []},
            ],
        }
        print(created_content.structure)
        assert created_content.structure == desired_structure

    def test_outlook_structure(self):
        created_content = TestData.create_email(TestData.outlook_email_text)
        desired_structure = {
            'type': 'multipart/alternative',
            'content_disposition': None,
            'children': [
                {'type': 'text/plain', 'content_disposition': None, 'children': []},
                {'type': 'text/html', 'content_disposition': None, 'children': []},
            ],
        }
        print(created_content.structure)
        assert created_content.structure == desired_structure

    def test_structure_with_duplicate_attachment_types(self):
        created_content = TestData.create_email(TestData.duplicate_attachment_types)
        desired_structure = {
            'type': 'multipart/mixed',
            'content_disposition': None,
            'children': [
                {
                    'type': 'multipart/alternative',
                    'content_disposition': None,
                    'children': [
                        {'type': 'text/plain', 'content_disposition': None, 'children': []},
                        {'type': 'text/html', 'content_disposition': None, 'children': []},
                    ],
                },
                {'type': 'text/xml', 'content_disposition': 'attachment', 'children': []},
                {'type': 'text/xml', 'content_disposition': 'attachment', 'children': []},
            ],
        }
        print(created_content.structure)
        assert created_content.structure == desired_structure

    def test_email_html_structure(self):
        created_content = TestData.create_email()
        desired_structure = """multipart/alternative<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#ea2bf05889ac5cf478293492da99b6e62c629f78cc1ef6a1248aea5ff6b0e226'>text/plain (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#6ce1e03b3902eee8dae69a56364413bdc9bb46d16743590ac42513217c5f430c'>text/html (body)</a>"""
        print(created_content.structure_as_html)
        assert created_content.structure_as_html == desired_structure

    def test_email_html_structure_with_attachments(self):
        created_content = TestData.create_email(TestData.attachment_email_text)
        desired_structure = """multipart/mixed<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;multipart/alternative<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#c6a1427d7119cd3c049d4fe08cc02f1058d15291fba68a994816ea209af73f0e'>text/plain (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#b64473d833f7568f15e1d86c02af3c237e652fb53c62087b74103c612f4e1dc3'>text/html (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#e5d91ce2991b8f8720cbf499deb19c16b04bc61a3aada3a1011b41ecbee6104e'>text/xml (attachment)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#efc6d065a38f0e3d99391e0bb992ba30f4ddf612fbbb492c3bcdf387039e3f1e'>image/png (attachment)</a>"""
        print(created_content.structure_as_html)
        assert created_content.structure_as_html == desired_structure

    def test_outlook_html_structure(self):
        created_content = TestData.create_email(TestData.outlook_email_text)
        desired_structure = """multipart/alternative<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#54712d1572ff09d73c3baacf0760a42735a3ce6dbd83144eb2f998155f53b740'>text/plain (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#b6fba92f1803f9f59d42fdd36b259fe8a550a68fee60808800cb11de14feeb8c'>text/html (body)</a>"""
        print(created_content.structure_as_html)
        assert created_content.structure_as_html == desired_structure

    # TODO: write a test for a body with duplicate content types

    def test_html_structure_with_duplicate_attachment_types(self):
        created_content = TestData.create_email(TestData.duplicate_attachment_types)
        desired_structure = """multipart/mixed<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;multipart/alternative<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#c6a1427d7119cd3c049d4fe08cc02f1058d15291fba68a994816ea209af73f0e'>text/plain (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#b64473d833f7568f15e1d86c02af3c237e652fb53c62087b74103c612f4e1dc3'>text/html (body)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#e5d91ce2991b8f8720cbf499deb19c16b04bc61a3aada3a1011b41ecbee6104e'>text/xml (attachment)</a><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#8f04d84fb9a70c42b9b5f0a7e7a55223c5431ad2de5d13270f4fe73729132d54'>text/xml (attachment)</a>"""
        print(created_content.structure_as_html)
        assert created_content.structure_as_html == desired_structure


class AnalysisTests(TestCase):
    def test_analysis(self):
        new_email = TestData.create_email()
        new_analysis = TestData.create_analysis(new_email)
        assert new_analysis.notes == "test1;test2"
        assert new_analysis.notes_strings == ["test1", "test2"]
        assert new_analysis.score == 1
        assert new_analysis.source == 'internal'

    def test_analysis_string(self):
        new_email = TestData.create_email()
        new_analysis = TestData.create_analysis(new_email)
        assert str(new_analysis) == '{}: {}'.format(new_email.id, new_analysis.first_seen)
