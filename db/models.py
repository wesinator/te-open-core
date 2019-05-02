#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
import re

from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.postgres.fields import JSONField

from utility import utility

JOIN_STRING = '|||'


class Email(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    cleaned_id = models.CharField(max_length=64)
    full_text = models.TextField()
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    submitter = models.CharField(max_length=16)
    structure = models.TextField()
    # todo: Assumption (jan 2018): a many to one field between emails and a header is correct
    header = models.ForeignKey('Header')
    bodies = models.ManyToManyField('Body')
    attachments = models.ManyToManyField('Attachment', blank=True)
    tlsh_hash = models.CharField(max_length=70, null=True, blank=True)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        self.modified = timezone.now()
        return super(Email, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Header(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    data = JSONField()
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        self.modified = timezone.now()
        return super(Header, self).save(*args, **kwargs)

    @property
    def link(self):
        """Return a link to the first email with the header."""
        email_set = self.email_set.all()

        if any(email_set):
            return 'email/{}{}'.format(email_set[0].id, '#header')

    @property
    def subject(self):
        return self.get_value('subject')

    def get_value(self, desired_header_key):
        for header_key, header_value in self.data:
            if header_key.lower() == desired_header_key.lower():
                return header_value
        return 'N/A'

    def __str__(self):
        string = ''
        tab_pattern = '( {3,})'

        for header_key, header_value in self.data:
            # find all large spaces in the header_value and replace them with a newline and tab for display
            header_value_string = re.sub(tab_pattern, r'\n\1', header_value)
            string += '{}: {}\n'.format(header_key, header_value_string)

        return string


class Body(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    first_seen = models.DateTimeField(editable=False)
    full_text = models.TextField()
    decoded_text = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        return super(Body, self).save(*args, **kwargs)

    @property
    def links(self):
        links = []
        for email in self.email_set.all():
            'email/{}{}'.format(email.id, '#bodies')
        return links

    def __str__(self):
        return str(self.id)


class Attachment(models.Model):
    # attachment_base64 = models.TextField()
    id = models.CharField(max_length=64, primary_key=True)
    content_type = models.CharField(max_length=100)
    filename = models.CharField(max_length=500)
    # todo: assumption (dec 2017): I've commented out the field below which assumes that we won't need to capture the content_transfer_encoding (there are more details on this field here: https://www.w3.org/Protocols/rfc1341/5_Content-Transfer-Encoding.html)
    # content_transfer_encoding = models.CharField(max_length=100)
    md5 = models.CharField(max_length=32)
    sha1 = models.CharField(max_length=40)
    full_text = models.TextField()
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        self.modified = timezone.now()
        return super(Attachment, self).save(*args, **kwargs)

    @property
    def sha256(self):
        return str(self.id)

    @property
    def filenames(self):
        return self.filename.split(JOIN_STRING)

    def __str__(self):
        return str(self.id)


class Analysis(models.Model):
    notes = models.TextField()
    source = models.CharField(max_length=50)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0000'))
    # one to many relationship between an email and analysis, respectively
    email = models.ForeignKey('Email')
    first_seen = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        return super(Analysis, self).save(*args, **kwargs)

    # These functions below are still used for handling the introspection analysis results
    @property
    def notes_strings(self):
        """Print the notes as a string."""
        return self._split_string(self.notes)

    def _split_string(self, string):
        """Standardize the way we split the internal and external notes."""
        return [string_section for string_section in string.split(";") if string_section != '']

    def __str__(self):
        return '{}: {}'.format(self.email.id, self.first_seen)


class Host(models.Model):
    # TODO: is this the proper length of a hostname (255 characters)? (3)
    host_name = models.CharField(max_length=255, primary_key=True)
    headers = models.ManyToManyField(Header)
    bodies = models.ManyToManyField(Body)
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        self.modified = timezone.now()
        return super(Host, self).save(*args, **kwargs)

    def __str__(self):
        return self.host_name


class IPAddress(models.Model):
    # TODO: is this a good length for ip addresses? (remember that we need to include ipv6) (3)
    ip_address = models.CharField(max_length=15, primary_key=True)
    headers = models.ManyToManyField(Header)
    bodies = models.ManyToManyField(Body)
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        self.modified = timezone.now()
        return super(IPAddress, self).save(*args, **kwargs)

    def __str__(self):
        return self.ip_address


class EmailAddress(models.Model):
    # the length of an email address is discussed here: https://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690
    email_address = models.CharField(max_length=254, primary_key=True)
    headers = models.ManyToManyField(Header)
    bodies = models.ManyToManyField(Body)
    host = models.ForeignKey(Host, blank=True, null=True)
    ip_address = models.ForeignKey(IPAddress, blank=True, null=True)
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
            # NOTE: I'm stripping off '[' and ']' in case the hostname is an ip address
            host_name = self.email_address.split('@')[-1].strip('[').strip(']')
            # NOTE: no need to make a connection between the host and the email body as this will be made when the host is created (it will be parsed out of the body too)
            if utility.is_ip_address(host_name):
                ip_address, created = IPAddress.objects.update_or_create(ip_address=host_name)
                self.ip_address = ip_address
            else:
                host, created = Host.objects.update_or_create(host_name=host_name)
                self.host = host
        self.modified = timezone.now()
        return super(EmailAddress, self).save(*args, **kwargs)

    def __str__(self):
        return self.email_address


class Url(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    # todo: assumption (dec 2017): 2000 characters is enough for the length of the urls (see https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers)
    url = models.CharField(max_length=2000)
    bodies = models.ManyToManyField(Body)
    host = models.ForeignKey(Host, blank=True, null=True)
    ip_address = models.ForeignKey(IPAddress, blank=True, null=True)
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
            self.id = utility.sha256(self.url)
            host_name = utility.url_domain_name(self.url)
            # NOTE: no need to make a connection between the host and the email body as this will be made when the host is created (it will be parsed out of the body too)
            if utility.is_ip_address(host_name):
                ip_address, created = IPAddress.objects.update_or_create(ip_address=host_name)
                self.ip_address = ip_address
            else:
                host, created = Host.objects.update_or_create(host_name=host_name)
                self.host = host
        self.modified = timezone.now()
        return super(Url, self).save(*args, **kwargs)

    def __str__(self):
        return self.url
