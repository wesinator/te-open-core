from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^save/$', views.save, name='save'),
    url(r'^api/v1/', include('api.urls')),
    url(r'^about/', views.AboutView.as_view(), name='about'),
    url(r'^email/', include('details.urls')),
    url(r'^search', include('search.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', admin.site.urls),
]
urlpatterns += staticfiles_urlpatterns()
handler500 = 'totalemail.views.error_500_handler'
