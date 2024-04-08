from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('entrar/', include("accounts.urls")),
    path('accounts/', include('allauth.urls')),
]