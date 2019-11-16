from django.urls import path
from django.contrib import auth

from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
]