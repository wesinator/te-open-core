from django.conf.urls import url

from . import views

app_name = 'details'
urlpatterns = [url(r'^(?P<pk>[0-9a-f]{64})', views.EmailDetailView.as_view(), name='details')]
