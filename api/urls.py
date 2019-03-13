from django.conf.urls import url

from api import views

app_name = 'api'
urlpatterns = [
    url(r'^emails/$', views.EmailBase.as_view()),
    url(r'^emails/(?P<pk>[0-9a-f]{64})/$', views.EmailDetail.as_view(), name='email_details'),
    url(r'^emails/(?P<pk>[0-9a-f]{64})/header/$', views.EmailHeader.as_view()),
    url(r'^emails/(?P<pk>[0-9a-f]{64})/bodies/$', views.EmailBodies.as_view()),
    url(r'^emails/(?P<pk>[0-9a-f]{64})/attachments/$', views.EmailAttachments.as_view()),
    url(r'^emails/(?P<pk>[0-9a-f]{64})/analysis/$', views.EmailAnalysis.as_view()),
    url(r'^headers/(?P<pk>[0-9a-f]{64})/$', views.HeaderDetail.as_view()),
    url(r'^headers/(?P<pk>[0-9a-f]{64})/emails/$', views.HeaderEmails.as_view()),
    url(r'^bodies/(?P<pk>[0-9a-f]{64})/$', views.BodyDetail.as_view()),
    url(r'^bodies/(?P<pk>[0-9a-f]{64})/emails/$', views.BodyEmails.as_view()),
    url(r'^attachments/(?P<pk>[0-9a-f]{64})/$', views.AttachmentDetail.as_view()),
    url(r'^attachments/(?P<pk>[0-9a-f]{64})/emails/$', views.AttachmentEmails.as_view()),
    url(r'^domains/$', views.DomainBase.as_view()),
    url(r'^emailAddresses/$', views.EmailAddressBase.as_view()),
    url(r'^ipAddresses/$', views.IpAddressBase.as_view()),
    url(r'^urls/$', views.UrlBase.as_view()),
]
