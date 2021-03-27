from django.conf import settings
from django.conf.urls import handler404, handler500, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

handler404 = 'posts.views.page_not_found'  # noqa
handler500 = 'posts.views.server_error'  # noqa

urlpatterns = [
    path('yatube_admin/', admin.site.urls),
    path('', include('posts.urls', namespace='posts')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    url('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
