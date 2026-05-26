from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from compressor.views import (
    home,
    compress_video,
    get_progress
)

urlpatterns = [

    path('', home),

    path(
        'compress/',
        compress_video
    ),

    path(
        'progress/<str:task_id>/',
        get_progress
    ),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)