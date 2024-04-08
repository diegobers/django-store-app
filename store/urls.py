from django.urls import path
from . import views

urlpatterns = [  
  path('', views.StoreIndexView.as_view(), name='index'),

]