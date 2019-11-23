# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.apps import apps

class CustomUser(AbstractUser):

    def get_stories(self):
        my_story_ids = list(
            set([i['story'] for i in self.created_sentences.values('story')])
        )
        return apps.get_model('vocastory', 'Story').objects.filter(id__in=my_story_ids)

    def __str__(self):
        return self.username
