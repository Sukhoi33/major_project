from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import SecureTwoFactorLoginView


urlpatterns = [
    path("login/", SecureTwoFactorLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('register/', views.register, name='register'),
    path('top-up/', views.top_up, name='top_up'),
]