from django.urls import path

from . import views

urlpatterns = [
    # This browses list of words
    path('', views.browse_word_sets, name='index'),
    # ex: /writers_mode/5/
    path('<int:wordset_id>/', views.browse_story_list, name='detail'),
]