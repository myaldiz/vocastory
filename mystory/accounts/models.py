# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, Subquery
from django.apps import apps


class CustomUser(AbstractUser):

    def get_stories(self):
        story_values = self.created_sentences.filter(is_selected=True).values('story').distinct()
        return apps.get_model('vocastory', 'Story').objects.get(story_values)

    # def get_score(self):
    #     sentence_score = self.created_sentences.filter(is_selected=True).count() * 10
    #     stories_scored = apps.get_model('vocastory', 'Story').get_stories_scored()
    #     story_ids = self.created_sentences.filter(is_selected=True).values_list('story', flat=True)
    #
    #     story_score = stories_scored.filter(pk__in=story_ids) \
    #                       .aggregate(story_score=models.Sum('score'))['story_score'] * 0.3
    #
    #     vote_score = self.voted_sentences.filter(is_selected=True).count() * 2
    #
    #     return sentence_score + story_score + vote_score

    @classmethod
    def get_users_scored(cls):
        stories_scored = apps.get_model('vocastory', 'Story').get_stories_scored()
        users_scored = cls.objects.annotate(
            score=models.Count(
                'created_sentences',
                filter=Q(created_sentences__is_selected=True),
                output_field=models.FloatField(),
                distinct=True) * 10
            + models.Count(
                'voted_sentences',
                filter=Q(voted_sentences__is_selected=True),
                output_field=models.FloatField(),
                distinct=True) * 2
            # + models.Avg('created_sentences__review_set__coherence')
            # + models.Avg('created_sentences__review_set__creativity')
            # + models.Avg('created_sentences__review_set__fun')
        )
        return users_scored

    def __str__(self):
        return self.username
