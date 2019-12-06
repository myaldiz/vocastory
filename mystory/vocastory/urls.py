from django.urls import path

from . import views

urlpatterns = [
    # Browse Mode
    path('browse_mode', views.browse_word_sets, name='browse_word_sets'),
    path('browse_mode/<int:wordset_id>/', views.browse_story_list, name='browse_wordset_stories'),
    path('browse_mode/wordset/<int:wordset_id>/swap_like', views.swap_like_wordset, name='swap_like_wordset'),

    # Review Mode
    path('review_mode/<int:story_id>/', views.review_story, name='review_story'),

    # Readers Mode
    path('readers_mode/<int:story_id>/', views.read_story, name='read_story'),

    # Writers Mode
    path('writers_mode/<int:story_id>/', views.write_story, name='write_story'),
    
    # Leaderboard
    path('leaderboard', views.see_leaderboard, name='see_leaderboard'),

    # Dictionary
    path('show_meaning/<int:word_id>/', views.show_word_meaning, name='show_word_meaning')
]
