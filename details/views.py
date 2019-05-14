#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from db.models import Email
import analyzer
from utility import utility
from totalemail import settings


def redirect_to_homepage(request):
    return HttpResponseRedirect('/')


class EmailDetailView(generic.DetailView):
    model = Email
    template_name = "details/email-details-base.html"

    def get_context_data(self, **kwargs):
        context = super(EmailDetailView, self).get_context_data(**kwargs)
        email_id = self.object.id

        # note: we don't need to handle cases where the given email id is invalid because this is handled by the parent class (generic.DetailView)
        email = Email.objects.get(pk=email_id)

        network_data, network_data_flat_list, network_data_overlaps, network_data_count = email.network_data()

        network_data_header_count = len(network_data['header']['hosts']) + len(network_data['header']['ip_addresses']) + len(network_data['header']['email_addresses'])
        network_data_body_count = len(network_data['bodies']['hosts']) + len(network_data['bodies']['ip_addresses']) + len(network_data['bodies']['email_addresses']) + len(network_data['bodies']['urls'])

        context['network_data'] = network_data
        context['network_data_flat_list'] = network_data_flat_list
        context['network_data_overlaps'] = network_data_overlaps
        context['network_data_count'] = network_data_count
        context['network_data_header_count'] = network_data_header_count
        context['network_data_body_count'] = network_data_body_count
        context['score'] = utility.email_score_calculate(email)

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


def reanalyze_email(request, **kwargs):
    """Resubmit an email for analysis."""
    try:
        email = Email.objects.get(pk=kwargs['pk'])
    except ObjectDoesNotExist:
        messages.error(request, 'No email found with the ID: {}'.format(kwargs['pk']))
        return HttpResponseRedirect('/')
    else:
        analyzer.start_analysis(email, True)
        messages.info(request, 'Email submitted for reanalysis. Updated results should be posted shortly.')
        return HttpResponseRedirect(reverse('details:details', args=(kwargs['pk'],)))


class EmailFeedbackView(generic.DetailView):
    model = Email
    template_name = 'details/email-feedback.html'

    def post(self, request, **kwargs):
        """."""
        feedback = '{}:{}:{}'.format(request.POST.get('feedback'), kwargs['pk'], settings._process_request_data(settings._get_request_data(request)))
        utility.create_alerta_alert('Feedback: {}'.format(feedback[:16]), 'info', feedback)
        messages.info(request, 'Thank you! Your feedback has been recorded.')
        return HttpResponseRedirect('/')


class EmailRedactionView(generic.DetailView):
    model = Email
    template_name = 'details/email-redaction.html'

    def post(self, request, **kwargs):
        """."""
        redaction_request = '{}:{}:{}'.format(request.POST.get('redactionRequest'), kwargs['pk'], settings._process_request_data(settings._get_request_data(request)))
        utility.create_alerta_alert('Redaction request: {}'.format(redaction_request[:16]), 'info', redaction_request)
        messages.info(request, 'Thank you! Your redaction request has been recorded.')
        return HttpResponseRedirect('/')
