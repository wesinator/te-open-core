#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mappings from search prefixes to db objects."""


def get_search_to_db_mappings():
    """Return the mappings from the search prefix to the db object."""
    search_mappings = {
        "sub": "header__subject__icontains",
        "to": "header__to__icontains",
        "from": "header___from__icontains",
    }

    return search_mappings
