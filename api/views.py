#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404

from api.serializers import (
    EmailSerializer,
    EmailCreateSerializer,
    AnalysisSerializer,
    HeaderSerializer,
    HeaderVotesSerializer,
    BodySerializer,
    AttachmentSerializer,
    DomainSerializer,
    IpAddressSerializer,
    EmailAddressSerializer,
    UrlSerializer,
)
from db.models import Email, Header, Body, Attachment, Host, IPAddress, EmailAddress, Url, Analysis
from totalemail import settings


class EmailBase(generics.ListCreateAPIView):
    serializer_class = EmailSerializer
    queryset = Email.objects.all()[: settings.MAX_RESULTS]

    # TODO: eventually, this function should also return analysis details about the email that was just submitted (or we will have to tell the user to wait and check until the analysis results are available)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        request_details = settings._get_request_data(request)

        redaction_values = ','.join(request.data.get('redaction_values', []))

        # use a special serializer for email creation
        serializer = EmailCreateSerializer(data=request.data)
        if serializer.is_valid():
            redact = True
            if request.query_params.get('redact'):
                if request.query_params['redact'].lower() == 'false':
                    redact = False

            if request.query_params.get('test'):
                new_email = serializer.save(
                    request_details=request_details,
                    is_test=True,
                    redact_recipient_info=redact,
                    redaction_values=redaction_values,
                )
            else:
                new_email = serializer.save(
                    request_details=request_details, redact_recipient_info=redact, redaction_values=redaction_values
                )
            return Response(EmailSerializer(new_email).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailDetail(APIView):
    def get_object(self, pk):
        try:
            return Email.objects.get(pk=pk)
        except Email.DoesNotExist:
            # TODO: handle this differently...
            raise Http404

    def get(self, request, pk, format=None):
        email = self.get_object(pk)
        serializer = EmailSerializer(email)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        email = self.get_object(pk)
        serializer = EmailSerializer(email, data=request.data)
        if serializer.is_valid():
            new_email = serializer.save()
            new_email.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailAnalysis(generics.ListCreateAPIView):
    serializer_class = AnalysisSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        email = Email.objects.get(id=self.kwargs['pk'])
        return Analysis.objects.filter(email=email.id)


class EmailHeader(generics.ListAPIView):
    serializer_class = HeaderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        email = Email.objects.get(id=self.kwargs['pk'])
        return Header.objects.filter(id=email.header.id)


class EmailBodies(generics.ListAPIView):
    serializer_class = BodySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        email = Email.objects.get(id=self.kwargs['pk'])
        if email:
            return email.bodies.all()
        else:
            return []


class EmailAttachments(generics.ListAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        email = Email.objects.get(id=self.kwargs['pk'])
        if email:
            return email.attachments.all()
        else:
            return []


class HeaderDetail(generics.RetrieveAPIView):
    queryset = Header.objects.all()
    serializer_class = HeaderSerializer
    permission_classes = (permissions.IsAuthenticated,)


class HeaderEmails(generics.ListAPIView):
    serializer_class = EmailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        header = Header.objects.get(id=self.kwargs['pk'])
        return Email.objects.filter(header=header)


class HeaderVotes(generics.RetrieveUpdateAPIView):
    queryset = Header.objects.all()
    serializer_class = HeaderVotesSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        header = Header.objects.get(id=self.kwargs['pk'])
        return header

    def put(self, request, pk):
        header = Header.objects.get(id=pk)

        # todo: pull the values out of the request and save them (as an automic operation)

        # todo: not sure what to return here...
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    # todo: test these functions and see what happens when we post to this endpoint


class BodyDetail(generics.RetrieveAPIView):
    queryset = Body.objects.all()
    serializer_class = BodySerializer
    permission_classes = (permissions.IsAuthenticated,)


class BodyEmails(generics.ListAPIView):
    serializer_class = EmailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        body = Body.objects.get(id=self.kwargs['pk'])
        return Email.objects.filter(bodies=body)


class AttachmentDetail(generics.RetrieveAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated,)


class AttachmentEmails(generics.ListAPIView):
    serializer_class = EmailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        attachment = Attachment.objects.get(id=self.kwargs['pk'])
        return Email.objects.filter(attachments=attachment)


class DomainBase(generics.ListCreateAPIView):
    serializer_class = DomainSerializer
    queryset = Host.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        host, created = Host.objects.update_or_create(host_name=request.data['host_name'])

        if request.data.get('bodies'):
            for body in request.data['bodies']:
                host.bodies.add(body)

        if request.data.get('headers'):
            for header in request.data['headers']:
                host.headers.add(header)

        if created:
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK

        return Response(self.serializer_class(host).data, status=status_code)


class EmailAddressBase(generics.ListCreateAPIView):
    serializer_class = EmailAddressSerializer
    queryset = EmailAddress.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        email_address, created = EmailAddress.objects.update_or_create(email_address=request.data['email_address'])

        if request.data.get('bodies'):
            for body in request.data['bodies']:
                email_address.bodies.add(body)

        if request.data.get('headers'):
            for header in request.data['headers']:
                email_address.headers.add(header)

        if created:
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK

        return Response(self.serializer_class(email_address).data, status=status_code)


class IpAddressBase(generics.ListCreateAPIView):
    serializer_class = IpAddressSerializer
    queryset = IPAddress.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        ip_address, created = IPAddress.objects.update_or_create(ip_address=request.data['ip_address'])

        if request.data.get('bodies'):
            for body in request.data['bodies']:
                ip_address.bodies.add(body)

        if request.data.get('headers'):
            for header in request.data['headers']:
                ip_address.headers.add(header)

        if created:
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK

        return Response(self.serializer_class(ip_address).data, status=status_code)


class UrlBase(generics.ListCreateAPIView):
    serializer_class = UrlSerializer
    queryset = Url.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        url, created = Url.objects.update_or_create(url=request.data['url'])

        if request.data.get('bodies'):
            for body in request.data['bodies']:
                url.bodies.add(body)

        if created:
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK

        return Response(self.serializer_class(url).data, status=status_code)
