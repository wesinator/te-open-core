from db import models


def find_headers_without_emails():
    """Find all headers that are not related to an email."""
    headers = models.Header.objects.all()
    for header in headers:
        if len(header.email_set.all()) == 0:
            print(header.id)


def find_bodies_without_emails():
    """Find all bodies that are not related to an email."""
    bodies = models.Body.objects.all()
    for body in bodies:
        if len(body.email_set.all()) == 0:
            print(body.id)
