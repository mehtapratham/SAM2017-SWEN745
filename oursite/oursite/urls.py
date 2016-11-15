"""oursite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views
from django.core.urlresolvers import reverse
from SAM2017 import views
from SAM2017.forms import *
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    # index page, i.e. Homepage after log-in
    url(r'^$', views.index, name='index'),

    # Log-in page
    url(r'^login/$', views.login, {'template_name': 'user/login.html', 'authentication_form': LoginForm}, name="login"),
    # url(r'^logout/$', views.logout, {'next_page': '/login'}),

    url(r'^admin/', admin.site.urls),
    url(r'^SAM2017/', include('SAM2017.urls', namespace='SAM2017')),

    # registration page
    url(r'^register/$', views.register, name='register'),
    url(r'^register/success$', views.register_complete, name='register_complete'),

	url(r'^papers/$', views.view_papers, name='view-papers'),
    url(r'^upload-paper/$', views.upload_paper, name='upload-paper'),

    url(r'^review-rate/$', views.reviewRating, name='review-rate'),
	url(r'^notifications/$', views.view_notifications, name='view-notifications')
]
