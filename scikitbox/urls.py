from django.conf.urls import url

from scikitbox import views

urlpatterns = [
    
    url(r'^$', views.index, name='index'),

    url(r'^uploadSingle',views.uploadSingle, name='upload_single'),
    url(r'^clear(?P<folder_target>\w+)',views.clear, name='clear'),
    url(r'^setupTraining',views.setupTraining, name='setup'),
    url(r'^view(?P<classifier_type>\w+)', views.viewTraining, name='view'),
    url(r'^normalizeTraining',views.normalizeTraining, name='normalize'),
    url(r'^invert', views.invert, name='invert'),
    url(r'^match', views.match, name='match'),
    url(r'^saveimage', views.save_image, name='save_image'),
    
]