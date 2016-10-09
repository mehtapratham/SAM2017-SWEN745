from django.conf.urls import url
from . import views

app_name = 'SAM2017'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^papers/$', views.view_papers, name='papers'),
    url(r'^upload-paper/$', views.upload_paper, name='upload-paper'),

]

