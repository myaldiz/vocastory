from django.urls import path

from . import views

urlpatterns = [
    path('', views.browse_word_sets, name='index'),
    path('<int:story_id>/', views.read_story, name='detail'),
]
