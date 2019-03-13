from rest_framework import serializers

from db.models import Email, Header, Body, Attachment, Analysis, Host, IPAddress, EmailAddress, Url

from email_processor import processor


class EmailSerializer(serializers.ModelSerializer):
    """Handle all email operations except for email creation."""

    class Meta:
        model = Email
        fields = ('full_text', 'id', 'tlsh_hash')
        read_only_fields = ('full_text', 'id')

    tlsh_hash = serializers.CharField(max_length=70, required=False)


class EmailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ('full_text',)

    def save(self, request_details=None, is_test=False, redact_recipient_info=True, redaction_values=[]):
        perform_external_analysis = not is_test
        new_email = processor.process_email(
            self.data['full_text'],
            request_details,
            perform_external_analysis=perform_external_analysis,
            log_mising_properties=perform_external_analysis,
            redact_email_data=redact_recipient_info,
            redaction_values=redaction_values,
        )
        return new_email


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = ('notes', 'source', 'score', 'email')


class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = ('full_text', 'id')


class BodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Body
        fields = ('full_text', 'id')


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('full_text', 'id', 'content_type', 'filename', 'md5', 'sha1', 'sha256')


class DomainSerializer(serializers.ModelSerializer):
    headers = serializers.PrimaryKeyRelatedField(queryset=Header.objects.all(), many=True, allow_null=True)
    bodies = serializers.PrimaryKeyRelatedField(queryset=Body.objects.all(), many=True, allow_null=True)

    class Meta:
        model = Host
        fields = ('host_name', 'headers', 'bodies')


class EmailAddressSerializer(serializers.ModelSerializer):
    headers = serializers.PrimaryKeyRelatedField(queryset=Header.objects.all(), many=True, allow_null=True)
    bodies = serializers.PrimaryKeyRelatedField(queryset=Body.objects.all(), many=True, allow_null=True)

    class Meta:
        model = EmailAddress
        fields = ('email_address', 'headers', 'bodies')


class IpAddressSerializer(serializers.ModelSerializer):
    headers = serializers.PrimaryKeyRelatedField(queryset=Header.objects.all(), many=True, allow_null=True)
    bodies = serializers.PrimaryKeyRelatedField(queryset=Body.objects.all(), many=True, allow_null=True)

    class Meta:
        model = IPAddress
        fields = ('ip_address', 'headers', 'bodies')


class UrlSerializer(serializers.ModelSerializer):
    bodies = serializers.PrimaryKeyRelatedField(queryset=Body.objects.all(), many=True, allow_null=True)

    class Meta:
        model = Url
        fields = ('url', 'bodies')
