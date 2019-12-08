from django.urls import path

from . import views

urlpatterns = [
    # Browse Mode
    path('see_sentences.png', views.see_sentences, name='see_sentences'),
    path('see_users.png', views.see_users, name='see_users')
]
