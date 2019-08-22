#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback

from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from utility import utility
from email_processor.processor import process_email
from .settings import (
    TOTALEMAIL_VERSION_NUMBER,
    TOTALEMAIL_VERSION_NAME,
    TOTALEMAIL_VERSION_BLOG_LINK,
    EMAIL_UPLOAD_LIMIT,
    _get_request_data,
)


class IndexView(generic.TemplateView):
    """Display an import page on the landing page."""

    template_name = 'totalemail/index.html'


class AboutView(generic.TemplateView):
    template_name = 'totalemail/about.html'

    def get_context_data(self, **kwargs):
        """Pass details about the TE version to the about page."""
        context = super(AboutView, self).get_context_data(**kwargs)

        context['te_version_number'] = TOTALEMAIL_VERSION_NUMBER
        context['te_version_name'] = TOTALEMAIL_VERSION_NAME
        context['te_version_link'] = TOTALEMAIL_VERSION_BLOG_LINK

        return context


def save(request):
    """Save an email to the DB."""
    full_email_texts = []

    # handle files uploaded by user
    if request.FILES.get('email_file'):
        for file in request.FILES.getlist('email_file')[:EMAIL_UPLOAD_LIMIT]:
            raw_email = file.read()
            full_email_text = raw_email.decode()
            full_email_texts.append(full_email_text)
    # handles text input into textarea
    elif request.POST.get('full_text'):
        full_email_texts.append(request.POST['full_text'])
    else:
        messages.error(request, 'Please upload an email or paste the text of an email to analyze it')
        return HttpResponseRedirect('/')

    for full_email_text in full_email_texts:
        new_email = process_email(
            full_email_text,
            _get_request_data(request),
            redact_email_data=request.POST.get('redact_recipient_data', False),
            redact_pii=request.POST.get('redact_pii', False),
            redaction_values=request.POST.get('redaction_values', None),
        )

        # new_email will be None if no headers are found in the uploaded content by the process_email function
        if new_email is None:
            messages.error(
                request, 'That text does not look like an email. Please upload an email (with a header and body(ies).'
            )
            return HttpResponseRedirect('/')

    return HttpResponseRedirect(reverse('details:details', args=(new_email.id,)))


def error_404_handler(request):
    return render(request, '404.html', status=404)


def error_500_handler(request):
    error_type, error_value, error_traceback = sys.exc_info()
    error_traceback_string = ''.join(traceback.format_list(traceback.extract_tb(error_traceback)))
    utility.create_alerta_alert(
        '500 error: {}'.format(request.build_absolute_uri()),
        'error',
        'type: {}\nvalue: {}\ntraceback:{}'.format(error_type, error_value, error_traceback_string),
    )
    return render(request, '500.html', status=500)
