from django.conf.urls import patterns, include, url
from django.contrib import admin
import scikitbox

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hellodjango.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'box/',include('scikitbox.urls')),
    url(r'^$',include('scikitbox.urls')),
)
