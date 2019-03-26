"""Testing functions for total_email."""

from django.test import TestCase

from test_resources import DefaultTestObject

TestData = DefaultTestObject()


class HostCreationTests(TestCase):
    def test_host_str(self):
        new_host = TestData.create_host()
        assert str(new_host) == TestData.domain_name

    def test_host_dates(self):
        new_object_a = TestData.create_host()
        new_object_b = TestData.create_host()
        assert new_object_a.first_seen == new_object_b.first_seen
        assert new_object_a.modified != new_object_b.modified


class IPAddressCreationTests(TestCase):
    def test_ip_address_str(self):
        new_ip_address = TestData.create_ip_address()
        assert str(new_ip_address) == TestData.ip_address

    def test_ip_dates(self):
        new_object_a = TestData.create_ip_address()
        new_object_b = TestData.create_ip_address()
        assert new_object_a.first_seen == new_object_b.first_seen
        assert new_object_a.modified != new_object_b.modified


class EmailAddressCreationTests(TestCase):
    def test_email_address_str(self):
        new_email_address = TestData.create_email_address()
        assert str(new_email_address) == TestData.email_address

    def test_email_address_dates(self):
        new_object_a = TestData.create_email_address()
        new_object_b = TestData.create_email_address()
        assert new_object_a.first_seen == new_object_b.first_seen
        assert new_object_a.modified != new_object_b.modified

    def test_email_address_hostname(self):
        new_email_address = TestData.create_email_address()
        assert new_email_address.host.host_name == 'gmail.com'

    def test_email_address_hostname_with_ip_address(self):
        new_email_address = TestData.create_email_address(TestData.email_address_ip_hostname)
        assert new_email_address.ip_address.ip_address == '192.168.0.1'


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

    def test_url_id(self):
        new_url = TestData.create_url()
        assert len(new_url.id) == 64

    def test_url_hostname(self):
        new_url = TestData.create_url()
        assert new_url.host.host_name == 'example.com'

    def test_url_hostname_with_ip_address(self):
        new_url = TestData.create_url(TestData.url_ip_hostname)
        assert new_url.ip_address.ip_address == '192.168.0.1'
