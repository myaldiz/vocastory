from django.urls import path

from . import views

urlpatterns = [
    # Review Mode
    path('review_mode/<int:story_id>/', views.review_story, name='detail'),

    # Browse Mode
    path('browse_mode', views.browse_word_sets, name='index'),
    path('browse_mode/<int:wordset_id>/', views.browse_story_list, name='detail'),

    # Readers Mode
    path('readers_mode/', views.browse_word_sets, name='index'),
    path('readers_mode/<int:story_id>/', views.read_story, name='detail'),

    # Writers Mode
    path('writers_mode/', views.browse_word_sets, name='index'),
    path('writers_mode/<int:story_id>/', views.read_story, name='detail'),
]
