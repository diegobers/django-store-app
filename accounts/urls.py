from django.urls import path, include

from allauth.account.views import SignupView, LogoutView
from accounts.views import CustomLoginView


app_name = 'accounts'


urlpatterns = [
    path('cadastro/', SignupView.as_view(template_name = 'signup.html'), name='signup'),
    path('', CustomLoginView.as_view(), name='login'),
    path('sair/', LogoutView.as_view(), name='logout'),
]