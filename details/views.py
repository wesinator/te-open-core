#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json

# from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.views import generic

from db.models import Email


def _get_related_headers_and_bodies(network_data_object, email, get_related_headers=True):
    """."""
    links = []

    if get_related_headers:
        # TODO: the links for each host will need to be deduplicated (between the header and body links) - I may want to move this code to the models.py
        for header in network_data_object.headers.all()[:5]:
            if header.id != email.header.id:
                links.append({'link': '/{}'.format(header.link), 'text': header.subject})
    for body in network_data_object.bodies.all()[:5]:
        # TODO: does this check work?
        if body.id not in email.bodies.all():
            for link in body.links:
                links.append({'link': '/{}'.format(link), 'text': body.emails.all()[0].header.subject})
    return links


def redirect_to_homepage(request):
    """Save an email to the DB."""
    return HttpResponseRedirect('/')


class EmailDetailView(generic.DetailView):
    model = Email
    template_name = "details/email-details-base.html"

    def get_context_data(self, **kwargs):
        context = super(EmailDetailView, self).get_context_data(**kwargs)
        email_id = self.object.id

        try:
            email = Email.objects.get(pk=email_id)
        except ObjectDoesNotExist:
            # TODO: it would be nice to print a message to the user if they visit the page that doesn't exist (as I attempted below) (3)
            # messages.error(request, 'No email found with the ID: {}'.format(email_id))
            return HttpResponseRedirect('/')

        # prepare the network data
        network_data = {
            'header': {'hosts': {}, 'ip_addresses': {}, 'email_addresses': {}},
            'bodies': {'hosts': {}, 'ip_addresses': {}, 'email_addresses': {}, 'urls': {}},
        }
        network_data_overlaps = 0

        # get network data from headers
        if email.header.host_set.exists:
            for host in email.header.host_set.all():
                data = _get_related_headers_and_bodies(host, email)
                network_data_overlaps += len(data)
                network_data['header']['hosts'][host.host_name] = data
        if email.header.ipaddress_set.exists:
            for address in email.header.ipaddress_set.all():
                data = _get_related_headers_and_bodies(address, email)
                network_data_overlaps += len(data)
                network_data['header']['ip_addresses'][address.ip_address] = data
        if email.header.emailaddress_set.exists:
            for address in email.header.emailaddress_set.all():
                data = _get_related_headers_and_bodies(address, email)
                network_data_overlaps += len(data)
                network_data['header']['email_addresses'][address.email_address] = data

        # get network data from bodies
        for body in email.bodies.all():
            if body.host_set.exists:
                for host in body.host_set.all():
                    data = _get_related_headers_and_bodies(host, email)
                    network_data_overlaps += len(data)
                    network_data['bodies']['hosts'][host.host_name] = data
            if body.ipaddress_set.exists:
                for address in body.ipaddress_set.all():
                    data = _get_related_headers_and_bodies(address, email)
                    network_data_overlaps += len(data)
                    network_data['bodies']['ip_addresses'][address.ip_address] = data
            if body.emailaddress_set.exists:
                for address in body.emailaddress_set.all():
                    data = _get_related_headers_and_bodies(address, email)
                    network_data_overlaps += len(data)
                    network_data['bodies']['email_addresses'][address.email_address] = data
            if body.url_set.exists:
                for url in body.url_set.all():
                    data = _get_related_headers_and_bodies(url, email, get_related_headers=False)
                    network_data_overlaps += len(data)
                    network_data['bodies']['urls'][url.url] = data

        context['network_data'] = network_data
        context['network_data_overlaps'] = network_data_overlaps

        try:
            # check to see if email was recently uploaded (if so, how a jgrowl letting them know they can refresh the page to view the external analyses)
            today = datetime.datetime.today()
            delta = datetime.timedelta(seconds=20)
            if (today - delta) < email.modified:
                context['new'] = True
            else:
                context['new'] = False
        except AttributeError:
            pass

        return context
