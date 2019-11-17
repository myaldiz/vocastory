from django.urls import path

from . import views

urlpatterns = [
    path('<int:story_id>/', views.review_story, name='detail'),
]
