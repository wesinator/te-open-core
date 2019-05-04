from django.conf.urls import url

from . import views

app_name = 'details'
urlpatterns = [
    url(r'^$', views.redirect_to_homepage),
    url(r'^(?P<pk>[0-9a-f]{64})/?$', views.EmailDetailView.as_view(), name='details'),
    url(r'^(?P<pk>[0-9a-f]{64})/feedback/?$', views.EmailFeedbackView.as_view(), name='feedback'),
    url(r'^(?P<pk>[0-9a-f]{64})/reanalyze/?$', views.reanalyze_email, name='reanalyze'),
]
