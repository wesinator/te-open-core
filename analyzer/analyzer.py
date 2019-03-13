#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Handle incoming requests for analysis."""

from utility import utility

from .external_analysis import analyze_externally


def start_analysis(email_object, perform_external_analysis):
    """Analyze the given email object."""
    if perform_external_analysis and not utility.is_running_locally():
        # the external analyses will be added later via API, hence they are not returned from this function
        analyze_externally(email_object)
