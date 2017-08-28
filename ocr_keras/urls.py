from django.conf.urls import include, url
from django.contrib import admin
from scikitbox.views import Login, Logout

urlpatterns = [
    # Examples:
    # url(r'^$', 'hellodjango.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^box/',include('scikitbox.urls')),
    url(r'^$',include('scikitbox.urls')),
    url(r'^login$', Login.as_view(), name='login'),
    url(r'^logout$', Logout.as_view(), name='logout'),
]
