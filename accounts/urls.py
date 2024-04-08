from django.urls import path, include

from allauth.account.views import SignupView, LoginView, LogoutView


urlpatterns = [
    path('cadastro/', SignupView.as_view(template_name = 'signup.html'), name='signup'),
    path('', LoginView.as_view(template_name ='signin.html'), name='login'),
    path('sair/', LogoutView.as_view(), name='logout'),
]