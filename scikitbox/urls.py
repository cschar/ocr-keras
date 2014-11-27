from django.conf.urls import patterns, url

from scikitbox import views

urlpatterns = patterns('',
    
    url(r'^$', views.index, name='index'),
    url(r'^uploadSingle',views.uploadSingle),
    url(r'^clear(?P<folder_target>\w+)$',views.clear),
    url(r'^setupTraining',views.setupTraining),
    url(r'^view(?P<classifier_type>\w+)$', views.viewTraining),
    url(r'^normalizeTraining',views.normalizeTraining),
    url(r'^matchTestGallery', views.matchTestGallery)
    
)