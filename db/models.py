#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from django.db import models
from django.utils import timezone
from django.urls import reverse

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
    attachments = models.ManyToManyField('Attachment')
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
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    full_text = models.TextField()

    accept_language = models.CharField(max_length=50, null=True, blank=True)
    alternate_recipient = models.CharField(
        max_length=1000, null=True, blank=True
    )  # models.ManyToManyField(EmailAddress)
    bcc = models.CharField(max_length=1000, null=True, blank=True)  # models.ManyToManyField(EmailAddress)
    cc = models.CharField(max_length=3000, null=True, blank=True)  # models.ManyToManyField(EmailAddress)
    content_language = models.CharField(max_length=20, null=True, blank=True)
    content_location = models.CharField(max_length=20, null=True, blank=True)
    content_md5 = models.CharField(max_length=32, null=True, blank=True)
    content_type = models.CharField(max_length=100, null=True, blank=True)
    content_translation_type = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    dkim = models.CharField(max_length=1000, null=True, blank=True)  # TODO: Implement class for dkim
    message_id = models.CharField(max_length=500, null=True, blank=True)
    encoding = models.CharField(max_length=50, null=True, blank=True)
    _from = models.CharField(max_length=1000, null=True, blank=True)  # models.ManyToManyField(EmailAddress)
    original_from = models.CharField(max_length=1000, null=True, blank=True)  # models.ManyToManyField(EmailAddress)
    original_recipient = models.CharField(
        max_length=1000, null=True, blank=True
    )  # models.ManyToManyField(EmailAddress)
    original_subject = models.CharField(max_length=500, null=True, blank=True)
    originator_return_address = models.CharField(
        max_length=1000, null=True, blank=True
    )  # models.ManyToManyField(EmailAddress)
    received = models.CharField(max_length=1000, null=True, blank=True)  # TODO: Implement class for received
    received_spf = models.CharField(
        max_length=1000, null=True, blank=True
    )  # TODO: Definitely implement class for received spf
    reply_to = models.CharField(max_length=1000, null=True, blank=True)  # models.ManyToManyField(EmailAddress)
    return_path = models.CharField(
        max_length=1000, null=True, blank=True
    )  # models.ManyToManyField(EmailAddress)  # This header contains more data than just an email address, should get its own class
    sender = models.CharField(
        max_length=1000, null=True, blank=True
    )  # models.ManyToManyField(EmailAddress)  # Same deal as return path
    subject = models.CharField(max_length=1000, null=True, blank=True)
    to = models.CharField(max_length=3000, null=True, blank=True)  # models.ManyToManyField(EmailAddress)
    x_originating_ip = models.GenericIPAddressField(null=True, blank=True)
    # good description of this field here: https://www.techwalla.com/articles/what-is-a-x-mailer-header
    x_mailer = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        self.modified = timezone.now()
        return super(Header, self).save(*args, **kwargs)

    @property
    def link(self):
        """Return a link to the first email with the header."""
        return 'email/{}{}'.format(self.email_set.all()[0].id, '#header')

    # TODO: not sure if we need this, but I made it and figured I'd keep it in here for now
    @property
    def full_from_field(self):
        try:
            from_json = json.loads(self._from)
        except json.JSONDecodeError:
            return self._from
        else:
            return '{} <{}>'.format(from_json['name'], from_json['email'])

    def __str__(self):
        return str(self.id)


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
    source = models.CharField(max_length=25)
    score = models.IntegerField()
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
