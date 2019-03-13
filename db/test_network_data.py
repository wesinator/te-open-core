"""Testing functions for total_email."""

from django.test import TestCase

from test_resources import DefaultTestObject
from .db_creator import _clean_header_string_for_network_data_parsing

TestData = DefaultTestObject()


class HostCreationTests(TestCase):
    def test_host_str(self):
        new_host = TestData.create_host()
        assert str(new_host) == TestData.host_name

    def test_host_dates(self):
        new_object_a = TestData.create_host()
        new_object_b = TestData.create_host()
        assert new_object_a.first_seen == new_object_b.first_seen
        assert new_object_a.modified != new_object_b.modified

    def test_host_parsing(self):
        new_email = TestData.create_email()
        host_list = [host.host_name for host in new_email.bodies.all()[0].host_set.all()]
        assert host_list is not None
        assert 'github.com' in host_list

    # TODO: write a test to make sure hosts are being pulled from headers (2)


class IPAddressCreationTests(TestCase):
    def test_ip_address_str(self):
        new_ip_address = TestData.create_ip_address()
        assert str(new_ip_address) == TestData.ip_address

    def test_ip_dates(self):
        new_object_a = TestData.create_ip_address()
        new_object_b = TestData.create_ip_address()
        assert new_object_a.first_seen == new_object_b.first_seen
        assert new_object_a.modified != new_object_b.modified

    def test_ip_parsing(self):
        new_email = TestData.create_email(TestData.network_data_ip_address)
        ip_list = [ip_address.ip_address for ip_address in new_email.bodies.all()[0].ipaddress_set.all()]
        assert ip_list is not None
        assert '192.168.0.1' in ip_list

    # TODO: write a test to make sure ip addresses are being pulled from headers (2)


class EmailAddressCreationTests(TestCase):
    def test_email_address_str(self):
        new_email_address = TestData.create_email_address()
        assert str(new_email_address) == TestData.email_address

    def test_email_address_dates(self):
        new_object_a = TestData.create_email_address()
        new_object_b = TestData.create_email_address()
        assert new_object_a.first_seen == new_object_b.first_seen
        assert new_object_a.modified != new_object_b.modified

    def test_ip_address(self):
        new_email = TestData.create_email(TestData.network_data_email_address_ip_host)
        assert len(new_email.bodies.all()[0].emailaddress_set.all()) == 1
        assert new_email.bodies.all()[0].emailaddress_set.all()[0].email_address == 'bad@[192.168.7.3]'
        assert new_email.bodies.all()[0].emailaddress_set.all()[0].ip_address.ip_address == '192.168.7.3'

    def test_host_a(self):
        new_email = TestData.create_email()

        assert len(new_email.header.emailaddress_set.all()) >= 2
        desired_email_addresses = ['bob@gmail.com', 'alice@gmail.com']
        existing_email_addresses = [
            email_address.email_address for email_address in new_email.header.emailaddress_set.all()
        ]

        for email_address in desired_email_addresses:
            assert email_address in existing_email_addresses

        for email_address in new_email.header.emailaddress_set.all():
            if email_address.email_address == 'bob@gmail.com':
                assert email_address.host.host_name == 'gmail.com'

    def test_host_b(self):
        new_email = TestData.create_email(TestData.network_data_email_address)
        assert len(new_email.bodies.all()[0].emailaddress_set.all()) == 1
        assert new_email.bodies.all()[0].emailaddress_set.all()[0].email_address == 'bad@example.com'
        assert new_email.bodies.all()[0].emailaddress_set.all()[0].host.host_name == 'example.com'

    # TODO: write a test to make sure email addresses are being pulled from headers (2)


class UrlCreationTests(TestCase):
    def test_url_str(self):
        new_url = TestData.create_url()
        assert str(new_url) == TestData.url
        assert new_url.url == 'http://example.com/training/bingo.php'

    def test_url_dates(self):
        new_object_a = TestData.create_url()
        new_object_b = TestData.create_url()
        assert new_object_a.first_seen == new_object_b.first_seen
        assert new_object_a.modified != new_object_b.modified

    def test_ip_address(self):
        new_email = TestData.create_email(TestData.network_data_ip_address_url)
        assert len(new_email.bodies.all()[0].url_set.all()) == 1
        assert new_email.bodies.all()[0].url_set.all()[0].url == 'http://192.168.0.1/test/bad.html'
        assert new_email.bodies.all()[0].url_set.all()[0].ip_address.ip_address == '192.168.0.1'

    def test_url_parsing(self):
        new_email = TestData.create_email()
        assert len(new_email.bodies.all()[0].url_set.all()) == 1
        assert (
            new_email.bodies.all()[0].url_set.all()[0].url == 'https://github.com/StylishThemes/GitHub-Dark/blob/master/tools/authors.sh'
        )
        assert new_email.bodies.all()[0].url_set.all()[0].host.host_name == 'github.com'


def test_header_cleaning():
    """Make sure the "Message-ID" header field is removed before network data is parsed from the email."""
    test_header = """Authentication-Results: mx.google.com;
       spf=pass (google.com: domain of john.@song.ocn.ne.jp designates 153.149.231.29 as permitted sender) smtp.mailfrom=john.@song.ocn.ne.jp
Received: from mf-smf-unw002c2 (mf-smf-unw002c2.ocn.ad.jp [153.138.219.70]) by mogw1023.ocn.ad.jp (Postfix) with ESMTP id 6C8AB2002B1; Mon,
  3 Dec 2018 23:51:09 +0900 (JST)
Received: from ocn-vc-mts-203c1.ocn.ad.jp ([153.138.219.218]) by mf-smf-unw002c2 with ESMTP id TpTagQxUrYtNbTpYzgKEI4; Mon, 03 Dec 2018 23:51:09 +0900
Received: from vcwebmail.ocn.ad.jp ([153.149.227.165]) by ocn-vc-mts-203c1.ocn.ad.jp with ESMTP id TpYyglAztlSxJTpYyge5qz; Mon, 03 Dec 2018 23:51:09 +0900
Received: from mzcstore301.ocn.ad.jp (mz-fcb301p.ocn.ad.jp [180.37.202.232]) by vcwebmail.ocn.ad.jp (Postfix) with ESMTP; Mon,
  3 Dec 2018 23:51:08 +0900 (JST)
Date: Mon, 3 Dec 2018 23:51:08 +0900 (JST)
From: "Mr. John Feeney " <john.@song.ocn.ne.jp>
Reply-To: "Mr. John Feeney " <johnfeeney1awelle@gmail.com>
Message-ID: <166398783.650247489.1543848668060.JavaMail.root@song.ocn.ne.jp>"""
    assert (
        _clean_header_string_for_network_data_parsing(test_header).strip()
        == """Authentication-Results: mx.google.com;
       spf=pass (google.com: domain of john.@song.ocn.ne.jp designates 153.149.231.29 as permitted sender) john.@song.ocn.ne.jp
Received: from mf-smf-unw002c2 (mf-smf-unw002c2.ocn.ad.jp [153.138.219.70]) by mogw1023.ocn.ad.jp (Postfix) with ESMTP id 6C8AB2002B1; Mon,
  3 Dec 2018 23:51:09 +0900 (JST)
Received: from ocn-vc-mts-203c1.ocn.ad.jp ([153.138.219.218]) by mf-smf-unw002c2 with ESMTP id TpTagQxUrYtNbTpYzgKEI4; Mon, 03 Dec 2018 23:51:09 +0900
Received: from vcwebmail.ocn.ad.jp ([153.149.227.165]) by ocn-vc-mts-203c1.ocn.ad.jp with ESMTP id TpYyglAztlSxJTpYyge5qz; Mon, 03 Dec 2018 23:51:09 +0900
Received: from mzcstore301.ocn.ad.jp (mz-fcb301p.ocn.ad.jp [180.37.202.232]) by vcwebmail.ocn.ad.jp (Postfix) with ESMTP; Mon,
  3 Dec 2018 23:51:08 +0900 (JST)
Date: Mon, 3 Dec 2018 23:51:08 +0900 (JST)
From: "Mr. John Feeney " <john.@song.ocn.ne.jp>
Reply-To: "Mr. John Feeney " <johnfeeney1awelle@gmail.com>"""
    )
