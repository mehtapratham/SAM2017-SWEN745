from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'SAM2017'

urlpatterns = [
    url(r'^$', views.index, name='index'),
	
    url(r'^papers/$', views.view_papers, name='view-papers'),
    url(r'^upload-paper/$', views.upload_paper, name='upload-paper'),
    #url(r'^papers/paper-upload/uploaded_files/(?P<papername>)/$',views.download_paper, name='download-paper')


] +static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

