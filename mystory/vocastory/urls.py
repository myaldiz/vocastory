from django.urls import path

from . import views

urlpatterns = [
    # Home is handled at base url.py
    path('my_page', views.mypage_view, name='my_view'),

    path('starred_page', views.starred_page_view, name='starred_view'),

    # Browse Mode
    path('browse_mode', views.browse_word_sets, name='browse_word_set'),
    path('browse_mode/<int:wordset_id>/', views.browse_story_list, name='browse_story'),

    # Review Mode
    path('review_mode/<int:story_id>/', views.review_story, name='review_story'),

    # Readers Mode
    path('readers_mode/', views.browse_word_sets, name='index1'),
    path('readers_mode/<int:story_id>/', views.read_story, name='detail1'),

    # Writers Mode
    path('writers_mode/', views.browse_word_sets, name='index2'),
    path('writers_mode/<int:story_id>/', views.read_story, name='detail2'),
]
