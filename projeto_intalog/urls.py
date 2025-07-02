from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importe
from django.conf.urls.static import static # Importe

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('APP.urls')),
]

# Adicione esta linha para servir arquivos de mídia em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)