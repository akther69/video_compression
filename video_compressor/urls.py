from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from compressor.views import upload_video


urlpatterns = [

    path('admin/', admin.site.urls),

    path('', upload_video, name='upload_video'),

]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)