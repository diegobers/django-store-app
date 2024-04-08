from django.urls import path, include

from allauth.account.views import SignupView, LoginView, LogoutView


urlpatterns = [
    path('cadastro/', SignupView.as_view(), name='signup'),
    path('', LoginView.as_view(), name='login'),
    path('sair/', LogoutView.as_view(), name='logout'),
]