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
    url(r'^paper-details/(?P<paperId>[0-9]+)/$', views.paper_details, name='paper-details'),

    url(r'^paper_assignment/$', views.paper_assignment, name='paper_assignment'),
    url(r'^review-rate/(?P<paperId>\d+)', views.reviewRating, name='review-rate'),

    url(r'^paper-selection/$',views.paper_selection,name='paper-selection'),
    url(r'^request_to_review/(?P<paperId>\d+)',views.request_to_review,name='request_to_review'),

	url(r'^notifications/$', views.view_notifications, name='view-notifications'),

    url(r'^deadlines/$', views.view_deadlines, name='view-deadlines'),
    url(r'^update-deadlines/$', views.update_deadlines, name='update-deadlines'),
    url(r'^sam/admin/accounts/$', views.accounts, name='manage-accounts'),
    url(r'^deleteuser/(?P<userId>[0-9]+)/$', views.deleteUser, name='delete-user'),
    url(r'^promoteauthor/(?P<userId>[0-9]+)/$', views.promoteAuthor, name='promote-author'),
    url(r'^demotepcm/(?P<userId>[0-9]+)/$', views.demotePCM, name='promote-author'),
]
