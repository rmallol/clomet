from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('', views.indexView),
    path('post/ajax/procno', views.procno, name = "procno"),
    path('post/ajax/dataimport', views.dataimport, name = "dataimport"),

    path('local', views.indexLocal, name = "indexlocal"),
    path('local/post/ajax/procnolocal', views.procnoLocal, name = "procnolocal"),
    path('local/post/ajax/dataimportlocal', views.dataimportLocal, name = "dataimportlocal"),


    path('docker', views.docker, name="docker"),
    path('about', views.about, name="about"),
    path('tutorials', views.tutorials, name="tutorials"),

    #path('tests', views.tests, name="tests"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
