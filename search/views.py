#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib import messages

from db.models import Email
from .search_mappings import header_search_mappings, body_search_mappings, network_data_search_mappings
from totalemail.settings import _validate_search_query, MAX_RESULTS
from utility import utility

# SEARCH_PREFIX_REGEX = '(\S*:(?:(?:".*?")|\S*))'
SEARCH_PREFIX_REGEX = '(\w*\(.*?\))'


def _add_email_results(existing_email_list, new_emails, search_query):
    unique_new_emails = []
    existing_email_ids = [email['email'].id for email in existing_email_list]

    for email in new_emails:
        if email.id not in existing_email_ids:
            unique_new_emails.append({
                'email': email,
                'search_query': search_query,
                'score': utility.email_score_calculate(email)
            })
            existing_email_ids.append(email.id)

    return unique_new_emails


class IndexSearchView(TemplateView):
    """Base search page."""

    def get(self, request):
        """Handle get requests."""
        template_name = "search/search_index.html"
        total_email_count = len(Email.objects.all())
        query_string = request.GET.get("q")
        original_query_string = query_string
        if query_string:
            if len(query_string) < 3:
                messages.info(request, 'Please enter a search term that is 3 characters or longer')
                return render(request, template_name, {'q': query_string})

            emails = list()

            _validate_search_query(query_string)

            # get the custom search queries used in the search
            queries_with_custom_prefixes = re.findall(SEARCH_PREFIX_REGEX, query_string)

            for query in queries_with_custom_prefixes:
                query = query.strip()

                # find the prefix of the custom query
                prefix = query.split('(')[0]
                # find the search value of the custom query (we are joining on '(' in case the query has a colon in it)
                search = '('.join(query.split('(')[1:]).lower().strip(')')
                prefix_found = False

                if prefix in header_search_mappings:
                    prefix_found = True
                    results = [
                        email
                        for email in Email.objects.all()
                        if search in email.header.get_value(header_search_mappings[prefix]).lower()
                    ]
                    emails.extend(_add_email_results(emails, results, query))
                elif prefix in body_search_mappings:
                    prefix_found = True
                    if prefix == 'bod':
                        results = Email.objects.filter(bodies__full_text__icontains=search)
                        emails.extend(_add_email_results(emails, results, query))
                elif prefix in network_data_search_mappings:
                    prefix_found = True
                    # find emails with the domain
                    if prefix == 'dom':
                        results = Email.objects.filter(header__host__host_name__icontains=search)
                        emails.extend(_add_email_results(emails, results, query))
                        results = Email.objects.filter(bodies__host__host_name__icontains=search)
                    # find emails with the domain in the header
                    elif prefix == 'domh':
                        results = Email.objects.filter(header__host__host_name__icontains=search)
                    # find emails with the domain in the body
                    elif prefix == 'domb':
                        results = Email.objects.filter(bodies__host__host_name__icontains=search)
                    emails.extend(_add_email_results(emails, results, query))

                if prefix_found:
                    # remove the query from the full search query
                    query_string = query_string.replace(query, '')

            query_string = query_string.strip()
            if query_string:
                # search for the remaining query (which has the queries with custom prefixes removed)
                results = Email.objects.filter(full_text__icontains=query_string)
                emails.extend(_add_email_results(emails, results, query_string))

            return render(
                request,
                template_name,
                {
                    "max_results": MAX_RESULTS,
                    "total_result_count": len(emails),
                    "results": emails[:MAX_RESULTS],
                    "q": original_query_string,
                    "total_email_count": total_email_count,
                },
            )
        else:
            return render(request, template_name, {"total_email_count": total_email_count})
