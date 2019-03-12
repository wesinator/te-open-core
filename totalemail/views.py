#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.views import generic

from .settings import TOTALEMAIL_VERSION_NUMBER, TOTALEMAIL_VERSION_NAME, TOTALEMAIL_VERSION_BLOG_LINK


class IndexView(generic.TemplateView):
    """Display an import page on the landing page."""

    template_name = 'importer/index-import.html'


class AboutView(generic.TemplateView):
    template_name = 'totalemail/about.html'

    def get_context_data(self, **kwargs):
        """Pass details about the TE version to the about page."""
        context = super(AboutView, self).get_context_data(**kwargs)

        context['te_version_number'] = TOTALEMAIL_VERSION_NUMBER
        context['te_version_name'] = TOTALEMAIL_VERSION_NAME
        context['te_version_link'] = TOTALEMAIL_VERSION_BLOG_LINK

        return context
