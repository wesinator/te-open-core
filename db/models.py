#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from decimal import Decimal
import re

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from utility import utility

JOIN_STRING = '|||'


def _get_related_headers_and_bodies(network_data_object, email, get_related_headers=True):
    """."""
    links = []
    related_headers = None
    related_bodies = network_data_object.bodies.all()
    MAX_RESULTS_LIMIT = 4

    if get_related_headers:
        related_headers = network_data_object.headers.all()
        for header in related_headers[:MAX_RESULTS_LIMIT]:
            if header.id != email.header.id:
                link_text = '(header) {}'.format(header.subject)
                if link_text not in [l['text'] for l in links]:
                    links.append({'link': '/{}'.format(header.link), 'text': link_text})
    for body in related_bodies[:MAX_RESULTS_LIMIT]:
        if body.id not in [b.id for b in email.bodies.all()]:
            for link in body.links:
                link_text = '(body) {}'.format(body.email_set.all()[0].header.subject)
                if link_text not in [l['text'] for l in links]:
                    links.append({'link': '/{}'.format(link), 'text': link_text})

    if related_bodies and len(related_bodies) > MAX_RESULTS_LIMIT:
        links.append({'link': '/search?q={}'.format(network_data_object), 'text': ''})
    if related_headers and len(related_headers) > MAX_RESULTS_LIMIT:
        links.append({'link': '/search?q={}'.format(network_data_object), 'text': ''})

    return links


class Email(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    cleaned_id = models.CharField(max_length=64)
    full_text = models.TextField()
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    submitter = models.CharField(max_length=16)
    structure = JSONField()
    # todo: Assumption (jan 2018): a many to one field between emails and a header is correct
    header = models.ForeignKey('Header', on_delete=models.CASCADE)
    bodies = models.ManyToManyField('Body')
    attachments = models.ManyToManyField('Attachment', blank=True)
    tlsh_hash = models.CharField(max_length=70, null=True, blank=True)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        self.modified = timezone.now()
        return super(Email, self).save(*args, **kwargs)

    def _structure_as_html_iterator(self, current_structure, bodies_by_content_type, attachments_by_content_type, html_structure='', indent_sequence=''):
        TAB = '&nbsp;' * 8
        # TODO: there may be a way/ways to improve the efficiency of this function... it would be worth investigating in the future (3)

        # handle multipart entries
        if 'multipart' in current_structure['type']:
            html_structure += '<br>{}{}'.format(indent_sequence, current_structure['type'])
        # handle attachments
        elif current_structure['content_disposition'] == 'attachment':
            if attachments_by_content_type.get(current_structure['type']):
                current_attachment_id = attachments_by_content_type[current_structure['type']].pop()
                html_structure += "<br>{}<a href='#{}'>".format(indent_sequence, current_attachment_id) + current_structure['type'] + " (attachment)</a>"
            else:
                # TODO: log an error message??? - this occurs if the structure dictates the presence of an attachment that is not really there
                pass

        # handle bodies
        else:
            if bodies_by_content_type.get(current_structure['type']):
                current_body_id = bodies_by_content_type[current_structure['type']].pop()
                html_structure += "<br>{}<a href='#{}'>".format(indent_sequence, current_body_id) + current_structure['type'] + " (body)</a>"
            else:
                # TODO: log an error message??? - this occurs if the structure dictates the presence of an email body that is not really there
                pass

        # TODO: test with multiple attachments/bodies of the same type

        if current_structure['children']:
            indent_sequence += TAB
            for child in current_structure['children']:
                html_structure += self._structure_as_html_iterator(child, bodies_by_content_type, attachments_by_content_type, indent_sequence=indent_sequence)

        return html_structure

    @property
    def structure_as_html(self):
        """Convert the email's structure to html."""
        bodies = self.bodies.all()
        bodies_by_content_type = {}

        for body in bodies:
            if not bodies_by_content_type.get(body.content_type):
                bodies_by_content_type[body.content_type] = []
            bodies_by_content_type[body.content_type].append(body.id)

        attachments = self.attachments.all()
        attachments_by_content_type = {}

        for attachment in attachments:
            if not attachments_by_content_type.get(attachment.content_type):
                attachments_by_content_type[attachment.content_type] = []
            attachments_by_content_type[attachment.content_type].append(attachment.id)

        structure = self._structure_as_html_iterator(self.structure, bodies_by_content_type, attachments_by_content_type)
        if structure.startswith('<br>'):
            structure = structure[4:]
        return structure

    def network_data(self):
        """Get the network data for the given email."""
        # prepare the network data
        network_data = {
            'header': {'hosts': {}, 'ip_addresses': {}, 'email_addresses': {}},
            'bodies': {'hosts': {}, 'ip_addresses': {}, 'email_addresses': {}, 'urls': {}},
        }
        # this is simply a list of all of the network data so that the user can copy it
        network_data_flat_list = []
        network_data_overlaps = 0
        # right now (may, 2019), this value is primarily used to determine whether we need to display the analysis data in the template
        network_data_count = 0

        # get network data from headers
        if self.header.host_set.exists:
            for host in self.header.host_set.all():
                network_data_count += 1
                if utility.domain_is_common(host.host_name):
                    data = [{
                        'link': '/search?q={}'.format(host.host_name),
                        'text': 'view more (this is a generic domain and no overlaps will be shown)...'
                    }]
                else:
                    data = _get_related_headers_and_bodies(host, self)
                    network_data_overlaps += len(data)
                network_data['header']['hosts'][host.host_name] = data
                network_data_flat_list.append(host.host_name)
        if self.header.ipaddress_set.exists:
            for address in self.header.ipaddress_set.all():
                network_data_count += 1
                data = _get_related_headers_and_bodies(address, self)
                network_data_overlaps += len(data)
                network_data['header']['ip_addresses'][address.ip_address] = data
                network_data_flat_list.append(address.ip_address)
        if self.header.emailaddress_set.exists:
            for address in self.header.emailaddress_set.all():
                network_data_count += 1
                data = _get_related_headers_and_bodies(address, self)
                network_data_overlaps += len(data)
                network_data['header']['email_addresses'][address.email_address] = data
                network_data_flat_list.append(address.email_address)

        # get network data from bodies
        for body in self.bodies.all():
            if body.host_set.exists:
                for host in body.host_set.all():
                    network_data_count += 1
                    if utility.domain_is_common(host.host_name):
                        data = [{
                            'link': '/search?q={}'.format(host.host_name),
                            'text': 'view more (this is a generic domain and no overlaps will be shown)...'
                        }]
                    else:
                        data = _get_related_headers_and_bodies(host, self)
                        network_data_overlaps += len(data)
                    network_data['bodies']['hosts'][host.host_name] = data
                    network_data_flat_list.append(host.host_name)
            if body.ipaddress_set.exists:
                for address in body.ipaddress_set.all():
                    network_data_count += 1
                    data = _get_related_headers_and_bodies(address, self)
                    network_data_overlaps += len(data)
                    network_data['bodies']['ip_addresses'][address.ip_address] = data
                    network_data_flat_list.append(address.ip_address)
            if body.emailaddress_set.exists:
                for address in body.emailaddress_set.all():
                    network_data_count += 1
                    data = _get_related_headers_and_bodies(address, self)
                    network_data_overlaps += len(data)
                    network_data['bodies']['email_addresses'][address.email_address] = data
                    network_data_flat_list.append(address.email_address)
            if body.url_set.exists:
                for url in body.url_set.all():
                    network_data_count += 1
                    data = _get_related_headers_and_bodies(url, self, get_related_headers=False)
                    network_data_overlaps += len(data)
                    network_data['bodies']['urls'][url.url] = data
                    network_data_flat_list.append(url.url)

        return network_data, network_data_flat_list, network_data_overlaps, network_data_count

    def __str__(self):
        return str(self.id)


class Header(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    data = JSONField()
    first_seen = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    subject_suspicious_votes = models.IntegerField(default=0)
    subject_not_suspicious_votes = models.IntegerField(default=0)

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
        # if the email has been run through SpamAssassin, the subject will be changed and the original subject is stored in the "X-Spam-Prev-Subject" field
        if self.get_value('x-spam-prev-subject'):
            return self.get_value('x-spam-prev-subject')
        else:
            subject_value = self.get_value('subject')
            # if there is a subject for this email, return the subject... otherwise return 'N/A' (I'm returning a string rather than None because this function is often used to display the subject line in the UI)
            if subject_value:
                return subject_value
            else:
                return 'N/A'

    def get_value(self, desired_header_key):
        for header_key, header_value in self.data:
            if header_key.lower() == desired_header_key.lower():
                return header_value
        return None

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
    content_type = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.first_seen:
            self.first_seen = timezone.now()
        return super(Body, self).save(*args, **kwargs)

    @property
    def links(self):
        links = []
        for email in self.email_set.all():
            links.append('email/{}{}'.format(email.id, '#bodies'))
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
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    # one to many relationship between an email and analysis, respectively
    email = models.ForeignKey('Email', on_delete=models.CASCADE)
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
